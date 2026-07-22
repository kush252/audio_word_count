# Real-Time Keyword Detection Project

This project is a real-time speech-to-text keyword detection application. It has been built using a **zero-backend architecture**, running entirely in the user's web browser using the native Web Speech API. 

## Features
- **Zero Backend**: No heavy models (like Whisper) or servers required. It runs purely on client-side HTML, CSS, and JavaScript.
- **Continuous Listening**: Uses `webkitSpeechRecognition` to continuously transcribe microphone input.
- **Real-Time Keyword Detection**: Matches spoken words against a predefined list of keywords instantly.
- **Modern UI**: Features a beautiful glassmorphism design with responsive counters and a live transcript feed.

## How It Works

1. **Audio Capture & Transcription**: When you click "Start Listening", the browser asks for microphone access and uses its built-in Speech-to-Text engine (via the Web Speech API).
2. **Keyword Detection**: The transcribed text is sent to the JavaScript logic (`app.js`), which splits the text into words and checks them against the `KEYWORDS` array.
3. **UI Updates**: The live transcript is displayed on the screen, and any detected keywords trigger an immediate update to the counter dashboard.

## Getting Started

Because this is a static web application with no backend dependencies, running it is incredibly simple.

### Prerequisites
- A modern web browser (Google Chrome is highly recommended as it has the best support for the Web Speech API).
- A working microphone.

### Running Locally

1. Open the project folder in your file explorer.
2. Double-click the `index.html` file to open it in your browser.
3. (Optional) Alternatively, you can run a simple local web server:
   ```bash
   # using python
   python -m http.server 8000
   ```
   Then navigate to `http://localhost:8000`.

### Configuring Keywords

To change the words the app listens for, open `app.js` in a text editor and modify the `KEYWORDS` array at the top of the file:

```javascript
const KEYWORDS = ['hello', 'world', 'test', 'keyword', 'speech', 'browser', 'amazing'];
```

## Deployment

Since there is no backend, this app can be deployed anywhere that hosts static files for free:
- **GitHub Pages**: Push this code to a GitHub repository and enable Pages.
- **Vercel / Netlify / Render**: Drag and drop the folder, or link your Git repository to deploy it instantly.
