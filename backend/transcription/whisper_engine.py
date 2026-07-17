import os
import torch
from faster_whisper import WhisperModel
import numpy as np
from utils.logger import setup_logger

# Disable huggingface symlink warning on Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

logger = setup_logger("WhisperEngine")

class WhisperEngine:
    def __init__(self, model_size: str = "distil-large-v3", language: str = "en"):
        self.model_size = model_size
        self.language = language
        
        # Determine device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        
        # Save models to the local project directory on D: drive instead of C: drive
        self.models_dir = os.path.join(os.getcwd(), "models")
        os.makedirs(self.models_dir, exist_ok=True)
        
        logger.info(f"Loading Faster Whisper model '{self.model_size}' on {self.device.upper()} with {self.compute_type}...")
        try:
            self.model = WhisperModel(
                self.model_size, 
                device=self.device, 
                compute_type=self.compute_type,
                download_root=self.models_dir
            )
            logger.info("Whisper model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
            
    def transcribe(self, audio_data: np.ndarray) -> str:
        """
        Transcribes a NumPy array of audio data.
        """
        try:
            # We bypass writing to disk by passing the numpy array directly to transcribe()
            # faster-whisper accepts audio data directly as a 1D numpy array
            segments, info = self.model.transcribe(
                audio_data, 
                language=self.language,
                beam_size=5,
                vad_filter=False # We already did VAD externally
            )
            
            transcript = " ".join([segment.text for segment in segments])
            return transcript.strip()
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
