// Configuration: Define your keywords here
const KEYWORDS = ['hello', 'did you all understand'];

// State
let isListening = false;
let recognition = null;
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

// Setup Speech Recognition
function setupRecognition() {
    // Check for browser support
    window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!window.SpeechRecognition) {
        alert("Your browser does not support the Web Speech API. Please use Google Chrome.");
        return false;
    }

    recognition = new window.SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    let finalTranscript = '';

    recognition.onstart = () => {
        isListening = true;
        startBtn.disabled = true;
        stopBtn.disabled = false;
        statusDot.parentElement.classList.add('listening');
        statusText.textContent = "Listening...";
    };

    recognition.onresult = (event) => {
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcriptSegment = event.results[i][0].transcript;

            if (event.results[i].isFinal) {
                finalTranscript += transcriptSegment + ' ';

                // Memory Safety: Prevent browser crash over hours of use by limiting visual text
                if (finalTranscript.length > 800) {
                    finalTranscript = '... ' + finalTranscript.slice(-800);
                }

                // Detect Keywords and Phrases in the final segment
                const lowerTranscript = transcriptSegment.toLowerCase();

                KEYWORDS.forEach(kw => {
                    const cleanKw = kw.toLowerCase();
                    // Use regex with word boundaries (\b) to match whole words/phrases only
                    // This prevents 'art' from triggering when you say 'smart'
                    const regex = new RegExp('\\b' + cleanKw + '\\b', 'g');
                    const matches = lowerTranscript.match(regex);

                    if (matches) {
                        // If spoken multiple times in one segment, count each one
                        for (let j = 0; j < matches.length; j++) {
                            updateKeywordCount(cleanKw);
                        }
                    }
                });

            } else {
                interimTranscript += transcriptSegment;
            }
        }

        // Update UI
        transcriptText.classList.remove('placeholder');
        transcriptText.innerHTML = `
            <span style="color: var(--text-color);">${finalTranscript}</span>
            <span style="color: #94a3b8; font-style: italic;">${interimTranscript}</span>
        `;

        // Auto-scroll to bottom
        const container = document.getElementById('transcript-container');
        container.scrollTop = container.scrollHeight;
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        if (event.error === 'not-allowed') {
            alert("Microphone access was denied.");
            stopListening();
        }
    };

    recognition.onend = () => {
        // If it ended unexpectedly (not by user), restart it to simulate continuous listening
        if (isListening) {
            try {
                recognition.start();
            } catch (e) {
                console.error("Error restarting recognition:", e);
                stopListening();
            }
        }
    };

    return true;
}

function startListening() {
    if (!recognition && !setupRecognition()) return;

    try {
        recognition.start();
    } catch (e) {
        console.error("Error starting recognition:", e);
    }
}

function stopListening() {
    isListening = false;
    if (recognition) {
        recognition.stop();
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
