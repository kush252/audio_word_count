import time
import queue
import threading
import numpy as np

from config.config import load_config
from audio.mic_stream import MicStream
from audio.vad import SileroVAD
from transcription.whisper_engine import WhisperEngine
from nlp.keyword_detector import KeywordDetector
from utils.counter_display import CounterDisplay
from utils.logger import setup_logger

logger = setup_logger("Main")

def vad_worker(mic_stream: MicStream, vad: SileroVAD, speech_queue: queue.Queue):
    """
    Consumes raw audio chunks from mic, runs VAD, and aggregates speech chunks.
    """
    buffer = []
    is_speaking = False
    silence_counter = 0
    MAX_SILENCE_CHUNKS = 2 # e.g. 1 second of silence before cutting segment

    while mic_stream.running:
        try:
            chunk = mic_stream.audio_queue.get(timeout=0.1)
        except queue.Empty:
            continue
            
        # Run VAD
        speech_detected = vad.is_speech(chunk)
        
        if speech_detected:
            is_speaking = True
            silence_counter = 0
            buffer.append(chunk)
        else:
            if is_speaking:
                silence_counter += 1
                buffer.append(chunk) # Include some trailing silence
                
                if silence_counter >= MAX_SILENCE_CHUNKS:
                    # Segment ended
                    is_speaking = False
                    segment = np.concatenate(buffer)
                    try:
                        speech_queue.put_nowait(segment)
                    except queue.Full:
                        logger.warning("Speech queue full! Dropping segment.")
                    buffer = []
                    
def transcription_worker(speech_queue: queue.Queue, whisper: WhisperEngine, text_queue: queue.Queue, running_flag: list):
    """
    Consumes speech segments, transcribes them, and outputs text.
    """
    while running_flag[0]:
        try:
            segment = speech_queue.get(timeout=0.1)
        except queue.Empty:
            continue
            
        # Transcribe
        t_start = time.time()
        transcript = whisper.transcribe(segment)
        t_end = time.time()
        
        if transcript:
            logger.info(f"Transcript ({t_end - t_start:.2f}s): {transcript}")
            try:
                text_queue.put_nowait(transcript)
            except queue.Full:
                logger.warning("Text queue full! Dropping transcript.")
                
        # Memory management: ensure segment is released
        del segment

def nlp_worker(text_queue: queue.Queue, nlp: KeywordDetector, counter: CounterDisplay, running_flag: list):
    """
    Consumes transcripts, detects keywords, and updates counts.
    """
    while running_flag[0]:
        try:
            text = text_queue.get(timeout=0.1)
        except queue.Empty:
            continue
            
        detected = nlp.detect(text)
        if detected:
            for keyword in detected:
                counter.update_count(keyword)
            counter.save()
            # The display update runs on a separate timer or can be triggered here.
            # We'll let the main thread handle display to avoid console clashing.

def main():
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return

    if not config.keywords and not config.phrases:
        logger.error("No keywords or phrases defined in config.yaml. Exiting.")
        return

    logger.info("Initializing components...")
    
    # 1. Initialize Components
    mic_stream = MicStream(
        sample_rate=config.audio.sample_rate, 
        chunk_duration=config.audio.chunk_duration,
        device_index=config.audio.device_index
    )
    vad = SileroVAD(
        threshold=config.vad.threshold, 
        sample_rate=config.audio.sample_rate
    )
    whisper = WhisperEngine(
        model_size=config.transcription.model,
        language=config.transcription.language
    )
    nlp = KeywordDetector(
        keywords=config.keywords,
        phrases=config.phrases
    )
    counter = CounterDisplay(save_path=config.output.save_path)
    
    # 2. Setup Queues
    speech_queue = queue.Queue(maxsize=50)
    text_queue = queue.Queue(maxsize=100)
    
    running_flag = [True]
    
    # 3. Start Workers
    threads = []
    
    t_vad = threading.Thread(target=vad_worker, args=(mic_stream, vad, speech_queue), daemon=True)
    t_trans = threading.Thread(target=transcription_worker, args=(speech_queue, whisper, text_queue, running_flag), daemon=True)
    t_nlp = threading.Thread(target=nlp_worker, args=(text_queue, nlp, counter, running_flag), daemon=True)
    
    threads.extend([t_vad, t_trans, t_nlp])
    
    for t in threads:
        t.start()
        
    # 4. Start Mic
    mic_stream.start()
    
    # 5. Main Loop (Display Refresh)
    try:
        while True:
            counter.display()
            time.sleep(config.output.refresh_rate)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
    finally:
        running_flag[0] = False
        mic_stream.stop()
        logger.info("Shutdown complete.")

if __name__ == "__main__":
    main()
