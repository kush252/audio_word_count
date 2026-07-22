# Real-Time Keyword Detection Project (Deepgram Edition)

This project is a real-time speech-to-text keyword detection application. It uses a **lightweight frontend-backend architecture** to stream audio from the browser directly to **Deepgram's** real-time Cloud API for maximum accuracy and speed.

## Architecture

- **Frontend (`index.html`, `app.js`, `style.css`)**: A static web app that captures raw audio using the `MediaRecorder` API and streams it via WebSockets. It also handles the keyword matching logic (using Regex) and updates the modern UI.
- **Backend (`backend/server.py`)**: A tiny, single-file Python proxy server built with FastAPI. Its sole purpose is to securely hold your `DEEPGRAM_API_KEY` and forward the WebSocket audio stream from the browser to Deepgram's servers.

## Getting Started

### Prerequisites

- Python 3.9+
- A free API key from [Deepgram](https://deepgram.com/).

### Installation

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Install the lightweight Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the `.env.example` file to `.env` and insert your API key:
   ```bash
   cp .env.example .env
   # Edit .env and set DEEPGRAM_API_KEY=your_key
   ```

### Running the Application

1. **Start the backend server:**
   ```bash
   cd backend
   python server.py
   ```
   *The proxy server will start on `ws://localhost:8000/listen`.*

2. **Open the frontend:**
   In your file explorer, go to the root project directory and double-click `index.html` to open it in Google Chrome.

3. Click **Start Listening**!

## Configuring Keywords

To change the words and phrases the app listens for, open `app.js` in a text editor and modify the `KEYWORDS` array at the top of the file:

```javascript
const KEYWORDS = ['hello', 'did you all understand', 'video understand'];
```

## Deployment

This architecture is incredibly easy to deploy:
- **Backend**: Deploy the `backend/` folder to a service like **Render** as a Web Service. Ensure you set the `DEEPGRAM_API_KEY` environment variable in their dashboard.
- **Frontend**: Update `BACKEND_WS_URL` in `app.js` to point to your new deployed backend URL (e.g., `wss://your-backend.onrender.com/listen`), and host the HTML files anywhere for free (GitHub Pages, Vercel, Netlify).
