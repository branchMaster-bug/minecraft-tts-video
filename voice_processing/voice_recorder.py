import sounddevice as sd
import numpy as np
import noisereduce as nr
import soundfile as sf
from scipy import signal
import os
import time
from tqdm import tqdm
from multiprocessing import Process, Queue
import yaml
from utils.audio_tools import calculate_snr, normalize_audio

class VoiceSampleCreator:
    def __init__(self):
        with open("config/settings.yaml") as f:
            self.config = yaml.safe_load(f)
            
        self.sample_rate = self.config['project']['sample_rate']
        self.samples_dir = self.config['project']['voice_samples_dir']
        self.duration = 45  # Optimal recording duration
        
    def create_samples(self):
        self._setup_environment()
        num_samples = self._get_sample_count()
        
        for i in range(num_samples):
            print(f"\n=== Recording Sample {i+1}/{num_samples} ===")
            audio = self._record_session()
            processed = self._process_audio(audio)
            
            if self._validate_quality(processed):
                self._save_sample(processed, i+1)
            else:
                print("Quality check failed, re-recording...")
                i -= 1
                
        print("\nVoice samples created successfully!")

    def _record_session(self):
        # Noise calibration
        print("Calibrating background noise... (Stay silent for 2 seconds)")
        noise_profile = self._capture_noise()
        
        # Start visual meter
        q = Queue()
        meter = Process(target=self._audio_meter, args=(q,))
        meter.start()
        
        # Main recording
        print("\nSpeak now... (Recording for 45 seconds)")
        audio = sd.rec(int(self.duration * self.sample_rate),
                      samplerate=self.sample_rate,
                      channels=1,
                      dtype='float32')
        
        # Progress bar
        for _ in tqdm(range(self.duration), desc="Recording"):
            time.sleep(1)
            
        sd.wait()
        q.put('stop')
        meter.join()
        
        return self._post_process(audio.flatten(), noise_profile)

    def _process_audio(self, audio):
        # Noise reduction
        reduced = nr.reduce_noise(y=audio, sr=self.sample_rate, stationary=True)
        
        # Normalization
        normalized = normalize_audio(reduced)
        
        # High-pass filter
        sos = signal.butter(4, 80, 'hp', fs=self.sample_rate, output='sos')
        filtered = signal.sosfilt(sos, normalized)
        
        return filtered

    def _validate_quality(self, audio):
        metrics = {
            'snr': calculate_snr(audio),
            'peak': np.max(np.abs(audio)),
            'clipping': np.mean(audio > 0.99)
        }
        
        return (0.3 < metrics['peak'] < 0.9 and
                metrics['snr'] > 25 and
                metrics['clipping'] < 0.005)

    # Helper methods (audio_meter, _capture_noise, etc.) similar to previous version
