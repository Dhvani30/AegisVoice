import soundcard as sc
import numpy as np
from faster_whisper import WhisperModel
import webrtcvad
import time
import collections
import logging
import warnings
import warnings

# ignore warnings (garbage text)
warnings.filterwarnings("ignore", message="data discontinuity in recording")
# ignore warnings (bluetooth issue)
warnings.filterwarnings("ignore", category=UserWarning, module="soundcard")

# Setup professional logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AegisAudioEngine:
    def __init__(self):
        # small model 
        logging.info("Loading Whisper model (small.int8)... This might take a minute to download.")
        self.model = WhisperModel("small", device="cpu", compute_type="int8")
        
        self.vad = webrtcvad.Vad(3)
        # parameters
        self.sample_rate = 16000
        self.frame_duration_ms = 30  # VAD requires 10, 20, or 30ms frames
        self.chunk_duration = 3.0    # We process 3 seconds of audio at a time for Whisper
        
        # sliding context buffer (last 5 transcribed sentences)
        self.context_buffer = collections.deque(maxlen=5)
        
        # get OS loopback
        self._setup_loopback()

    def _setup_loopback(self):
        """Fixes the API call to correctly capture desktop audio on Windows."""
        try:
            speaker = sc.default_speaker()
            # fetch the loopback-capable input matching your active speaker's ID/name
            self.loopback = sc.get_microphone(id=str(speaker.name), include_loopback=True)
            logging.info(f"Successfully hooked into system audio loopback: {speaker.name}")
            
            # add bluetooth warning
            if "Bluetooth" in speaker.name or "Buds" in speaker.name or "Wireless" in speaker.name:
                logging.warning("!!!WARNING: You are using Bluetooth audio. This may cause 'data discontinuity' errors. Please use wired speakers/headphones for stable testing.")
        except Exception as e:
            logging.error(f"XXX Failed to setup loopback: {e}")
            raise

    def _has_speech(self, audio_chunk):
        """Checks if the 3-second audio chunk actually contains human speech."""
        # Convert float32 audio to 16-bit PCM (required by WebRTC VAD)
        pcm_audio = (audio_chunk * 32767).astype(np.int16).tobytes()
        
        # Break into 30ms frames for VAD
        frame_size = int(self.sample_rate * (self.frame_duration_ms / 1000.0))
        speech_frames = 0
        
        for i in range(0, len(pcm_audio), frame_size * 2): # *2 because int16 is 2 bytes
            frame = pcm_audio[i:i + frame_size * 2]
            if len(frame) == frame_size * 2:
                if self.vad.is_speech(frame, self.sample_rate):
                    speech_frames += 1
                    
        # If at least 30% of the frames have speech, process it
        return speech_frames > (len(pcm_audio) / (frame_size * 2)) * 0.3

    def process_audio(self, audio_data):
        """Transcribes audio and updates the sliding context buffer."""
        # PRODUCTION WHISPER SETTINGS:
        # beam_size=5: Better accuracy than 1
        # language="en": Forces English, stops it from guessing French/Thai.
        # condition_on_previous_text=False: Stops hallucination cascades.
        # vad_filter=True: Double-checks voice activity.
        segments, info = self.model.transcribe(
            audio_data, 
            beam_size=5, 
            language="en", 
            condition_on_previous_text=False,
            vad_filter=True
        )
        text = " ".join([segment.text.strip() for segment in segments])
        
        if text:
            self.context_buffer.append(text)
            full_context = " ".join(self.context_buffer)
            logging.info(f"NEW TRANSCRIPT: {text}")
            logging.info(f"CURRENT CONTEXT: {full_context}")
            return full_context
        return " ".join(self.context_buffer)

    def start(self):
        logging.info("-- Aegis Engine Started. Listening to system audio...")
        chunk_size = int(self.sample_rate * self.chunk_duration)
        
        with self.loopback.recorder(samplerate=self.sample_rate, channels=1) as mic:
            while True:
                try:
                    # record auido for 3 secs
                    audio_data = mic.record(numframes=chunk_size)
                    
                    # flatten to 1D array if needed
                    if len(audio_data.shape) > 1:
                        audio_data = np.mean(audio_data, axis=1)

                    # VAD Check: Skip if it's just silence or background hum
                    if not self._has_speech(audio_data):
                        continue 

                    # processing of speech
                    self.process_audio(audio_data)

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logging.error(f"Runtime error in audio loop: {e}")
                    time.sleep(1) # Prevent CPU spinning on error

if __name__ == "__main__":
    engine = AegisAudioEngine()
    engine.start()