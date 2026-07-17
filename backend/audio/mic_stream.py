import queue
import numpy as np
import sounddevice as sd
from utils.logger import setup_logger

logger = setup_logger("MicStream")

class MicStream:
    def __init__(self, sample_rate: int = 16000, chunk_duration: float = 0.5, device_index=None):
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.device_index = device_index
        
        self.chunk_samples = int(self.sample_rate * self.chunk_duration)
        # Queue to hold raw audio chunks
        self.audio_queue = queue.Queue(maxsize=100) # prevent memory leaks
        self.stream = None
        self.running = False

    def _audio_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            logger.warning(f"Audio callback status: {status}")
            
        # We need mono audio (1 channel)
        # Extract channel 0 and copy to avoid keeping the original array in memory
        audio_data = indata[:, 0].copy()
        
        # Audio normalization: ensure it's not too quiet
        # Calculate max amplitude
        max_amp = np.max(np.abs(audio_data))
        if max_amp > 0 and max_amp < 0.5:
             # simple gain boost if it's very quiet, capped at 1.0
             gain = min(0.5 / max_amp, 5.0) 
             audio_data = np.clip(audio_data * gain, -1.0, 1.0)
        
        try:
            self.audio_queue.put_nowait(audio_data)
        except queue.Full:
            logger.warning("Audio queue full! Dropping chunk.")

    def start(self):
        """Starts the microphone stream."""
        if self.running:
            return
            
        logger.info(f"Starting microphone stream (SR: {self.sample_rate}, Chunk: {self.chunk_duration}s)")
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                blocksize=self.chunk_samples,
                device=self.device_index,
                channels=1,
                dtype='float32',
                callback=self._audio_callback
            )
            self.stream.start()
            self.running = True
            logger.info("Microphone stream started.")
        except Exception as e:
            logger.error(f"Failed to start microphone: {e}")
            raise

    def stop(self):
        """Stops the microphone stream."""
        self.running = False
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            logger.info("Microphone stream stopped.")
