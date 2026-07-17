# Real-Time Keyword Detection

This is a robust, production-quality Python application that continuously listens to microphone input in real-time, transcribes speech, detects user-defined keywords/phrases, and maintains accurate occurrence counts.

## Features
- **Continuous Listening**: Non-blocking microphone input using `sounddevice`.
- **Voice Activity Detection**: Ignores silence and background noise using Silero VAD.
- **Accurate Transcription**: Uses `faster-whisper` for highly accurate, offline transcription.
- **Advanced NLP**: Uses `spaCy`'s PhraseMatcher to handle multi-word phrases, case insensitivity, and lemmatization (e.g., "running" counts as "run").
- **Memory Safe**: Utilizes decoupled worker threads with bounded queues to ensure memory stability over hours of continuous use. No audio is written to disk.
- **Live Updating**: Real-time console table output and JSON saving.

## Installation

### Prerequisites
- Python 3.9+
- For best performance, a GPU with CUDA installed is highly recommended.

### 1. Install Dependencies
Run the following command to install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Download spaCy Language Model
You must download the spaCy english model before running the application:

```bash
python -m spacy download en_core_web_sm
```

## Configuration

Edit the `config/config.yaml` file to define your own keywords and phrases. 
You can also adjust the microphone index, Whisper model size (`tiny`, `base`, `small`, `medium`, `large-v3`, `distil-large-v3`), and VAD sensitivity.

## Usage

Run the main application script:

```bash
python main.py
```

The application will download the Whisper and Silero VAD models on the very first run. Subsequent runs will use the cached offline models.
