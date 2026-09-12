import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
import numpy as np
import scipy.signal as signal
import scipy.fft as fft
from main import acoustic, prosody, ingestion, speaker

def generate_ai_tts_voice_clip(sample_rate=16000, duration=3.5):
    t = np.linspace(0, duration, int(sample_rate * duration))
    f0 = 135.0
    phase = 2 * np.pi * f0 * t
    voiced = np.sin(phase) + 0.4 * np.sin(2 * phase) + 0.2 * np.sin(3 * phase)
    
    syllables = np.clip(np.sin(2 * np.pi * 2.0 * t), 0.0, 1.0) ** 2
    voiced_speech = voiced * syllables
    
    consonant_mask = np.clip(np.sin(2 * np.pi * 2.0 * t + np.pi/2), 0.0, 1.0) ** 4
    consonants = 0.08 * np.sin(2 * np.pi * 2400.0 * t) * consonant_mask
    
    ai_voice = (voiced_speech + consonants).astype(np.float32)
    return ai_voice / np.max(np.abs(ai_voice)) * 0.95

audio = generate_ai_tts_voice_clip()
is_speech, reason = ingestion.is_spoken_human_speech(audio, 16000)
ac = acoustic.detect_tts_artifacts(audio)
pr = prosody.analyze_prosody(audio)

print("Speech Check:", is_speech, f"({reason})")
print("Acoustic Anomaly / Neural Prob:", ac["acoustic_anomaly_score"], ac["neural_deepfake_probability"])
print("Spectral Features:", ac["spectral_features"])
print("Prosody:", "std_f0:", pr.get("std_f0_hz"), "jitter:", pr.get("jitter_percent"))
