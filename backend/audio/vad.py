import torch
import numpy as np
from utils.logger import setup_logger

logger = setup_logger("VAD")

class SileroVAD:
    def __init__(self, threshold: float = 0.5, sample_rate: int = 16000):
        self.threshold = threshold
        self.sample_rate = sample_rate
        
        logger.info("Loading Silero VAD model...")
        try:
            # We use torch.hub to load the pre-trained Silero VAD model
            self.model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False,
                trust_repo=True
            )
            self.get_speech_timestamps = utils[0]
            logger.info("Silero VAD model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Silero VAD model: {e}")
            raise
            
    def is_speech(self, audio_chunk: np.ndarray) -> bool:
        """
        Detects if there is speech in the given audio chunk.
        Audio chunk must be a 1D numpy array of float32, normalized between -1 and 1.
        """
        # Convert numpy array to torch tensor
        tensor_audio = torch.from_numpy(audio_chunk)
        
        # VAD requires [batch, time] shape
        tensor_audio = tensor_audio.unsqueeze(0)
        
        try:
            # Get speech probability for the whole chunk
            with torch.no_grad():
                speech_prob = self.model(tensor_audio, self.sample_rate).item()
                
            return speech_prob >= self.threshold
        except Exception as e:
            logger.error(f"VAD error during inference: {e}")
            return False
