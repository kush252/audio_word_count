import os
import json
import asyncio
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

app = FastAPI()

# Allow frontend to connect from any origin (useful for local development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Proxy server is running"}

@app.websocket("/listen")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    if not DEEPGRAM_API_KEY:
        await websocket.send_json({"type": "error", "message": "DEEPGRAM_API_KEY is not set on the server."})
        await websocket.close()
        return

    # Deepgram WebSocket URL for real-time streaming
    # We expect 16kHz linear16 (raw PCM) from the browser by default, but web browser usually sends WebM/Opus.
    # We will tell Deepgram we are sending WebM/Opus if we let the browser use MediaRecorder.
    # To be safe, we omit encoding/sample_rate so Deepgram auto-detects the WebM/Opus container.
    deepgram_url = "wss://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&keepalive=true&interim_results=true"
    
    extra_headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}"
    }

    try:
        # Open connection to Deepgram
        async with websockets.connect(deepgram_url, extra_headers=extra_headers) as dg_socket:
            print("Connected to Deepgram")
            
            # Forward audio from Browser -> Deepgram
            async def sender():
                try:
                    while True:
                        data = await websocket.receive_bytes()
                        await dg_socket.send(data)
                except WebSocketDisconnect:
                    print("Browser disconnected")
                    # Tell Deepgram the stream is closing
                    await dg_socket.send(json.dumps({"type": "CloseStream"}))
                except Exception as e:
                    print(f"Error forwarding to Deepgram: {e}")

            # Forward text from Deepgram -> Browser
            async def receiver():
                try:
                    while True:
                        msg = await dg_socket.recv()
                        # Pass the raw JSON string back to the browser to parse
                        await websocket.send_text(msg)
                except websockets.exceptions.ConnectionClosed:
                    print("Deepgram connection closed")
                except Exception as e:
                    print(f"Error receiving from Deepgram: {e}")

            # Run both tasks concurrently
            await asyncio.gather(sender(), receiver())
            
    except Exception as e:
        print(f"Failed to connect to Deepgram: {e}")
        try:
            await websocket.close()
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    # Run the server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
