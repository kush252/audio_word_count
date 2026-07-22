// Configuration: Define your keywords here
const KEYWORDS = ['hello', 'did you all understand'];

// Backend WebSocket URL
const BACKEND_WS_URL = 'wss://audio-word-count.onrender.com/listen';

// State
let isListening = false;
let socket = null;
let mediaRecorder = null;
let counts = {};

// Initialize counts
KEYWORDS.forEach(kw => {
    counts[kw.toLowerCase()] = 0;
});

// DOM Elements
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const transcriptText = document.getElementById('transcript-text');
const keywordsContainer = document.getElementById('keywords-container');

// Initialize Keyword Dashboard
function renderKeywords() {
    keywordsContainer.innerHTML = '';
    KEYWORDS.forEach(kw => {
        const word = kw.toLowerCase();
        const card = document.createElement('div');
        card.className = 'keyword-card';
        card.id = `card-${word}`;

        card.innerHTML = `
            <div class="keyword-word">${word}</div>
            <div class="keyword-count" id="count-${word}">${counts[word]}</div>
        `;
        keywordsContainer.appendChild(card);
    });
}

function updateKeywordCount(word) {
    counts[word]++;
    const countEl = document.getElementById(`count-${word}`);
    if (countEl) {
        countEl.textContent = counts[word];

        // Add animation class
        const card = document.getElementById(`card-${word}`);
        card.classList.add('active');
        setTimeout(() => card.classList.remove('active'), 500);
    }
}

let finalTranscript = '';

async function startListening() {
    if (isListening) return;

    try {
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        // Connect to our lightweight Python backend
        socket = new WebSocket(BACKEND_WS_URL);

        socket.onopen = () => {
            console.log("Connected to backend");
            isListening = true;
            startBtn.disabled = true;
            stopBtn.disabled = false;
            statusDot.parentElement.classList.add('listening');
            statusText.textContent = "Listening via Deepgram...";

            // Configure MediaRecorder to send chunks every 250ms
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0 && socket.readyState === WebSocket.OPEN) {
                    socket.send(event.data);
                }
            };

            mediaRecorder.start(250);
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);

            // Handle Deepgram response format
            if (data.type === 'Results' && data.channel && data.channel.alternatives) {
                const transcriptSegment = data.channel.alternatives[0].transcript;

                if (data.is_final && transcriptSegment.trim().length > 0) {
                    finalTranscript += transcriptSegment + ' ';

                    // Memory Safety: Prevent browser crash over hours of use
                    if (finalTranscript.length > 800) {
                        finalTranscript = '... ' + finalTranscript.slice(-800);
                    }

                    // Detect Keywords and Phrases in the final segment
                    // Strip all punctuation to make matching much more forgiving
                    const lowerTranscript = transcriptSegment.toLowerCase().replace(/[.,!?'"]/g, '');
                    
                    KEYWORDS.forEach(kw => {
                        const cleanKw = kw.toLowerCase();
                        
                        // Use simpler, more forgiving string matching instead of strict Regex word boundaries
                        if (lowerTranscript.includes(cleanKw)) {
                            updateKeywordCount(cleanKw);
                        }
                    });

                    // Update UI with final text
                    transcriptText.classList.remove('placeholder');
                    transcriptText.innerHTML = `<span style="color: var(--text-color);">${finalTranscript}</span>`;
                    
                    // Auto-scroll to bottom
                    const container = document.getElementById('transcript-container');
                    container.scrollTop = container.scrollHeight;
                } else if (!data.is_final) {
                    // Show interim results instantly to fix perceived slowness without chopping audio
                    transcriptText.classList.remove('placeholder');
                    transcriptText.innerHTML = `
                        <span style="color: var(--text-color);">${finalTranscript}</span>
                        <span style="color: #94a3b8; font-style: italic;">${transcriptSegment}</span>
                    `;
                    const container = document.getElementById('transcript-container');
                    container.scrollTop = container.scrollHeight;
                }
            } else if (data.type === 'error') {
                console.error("Backend Error:", data.message);
                alert("Backend Error: " + data.message);
                stopListening();
            }
        };

        socket.onclose = () => {
            console.log("Disconnected from backend");
            stopListening();
        };

        socket.onerror = (error) => {
            console.error("WebSocket Error:", error);
            alert("Could not connect to the backend server. Is it running?");
            stopListening();
        };

    } catch (err) {
        console.error("Error accessing microphone:", err);
        alert("Could not access microphone.");
    }
}

function stopListening() {
    isListening = false;

    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }

    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
    }

    startBtn.disabled = false;
    stopBtn.disabled = true;
    statusDot.parentElement.classList.remove('listening');
    statusText.textContent = "Not listening";
}

// Event Listeners
startBtn.addEventListener('click', startListening);
stopBtn.addEventListener('click', stopListening);

// Initial Render
renderKeywords();
