import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
import numpy as np
from main import acoustic, prosody, ingestion, speaker

def generate_ai_tts_voice_clip(sample_rate=16000, duration=3.5):
    t = np.linspace(0, duration, int(sample_rate * duration))
    f0 = 135.0
    phase = 2 * np.pi * f0 * t
    voiced = np.sin(phase) + 0.4 * np.sin(2 * phase) + 0.2 * np.sin(3 * phase)
    
    # Smooth hanning syllable envelope
    syllables = np.clip(np.sin(2 * np.pi * 2.5 * t), 0.0, 1.0) ** 2
    voiced_speech = voiced * syllables
    
    # High-frequency vocoder buzzing artifact (> 0.08) characteristic of neural vocoders
    buzz = 0.12 * np.sin(2 * np.pi * 7500.0 * t) * syllables
    
    noise = np.random.randn(len(t))
    consonant_mask = np.clip(np.sin(2 * np.pi * 2.0 * t + np.pi/2), 0.0, 1.0) ** 4
    consonants = 0.08 * np.sin(2 * np.pi * 2400.0 * t) * consonant_mask
    
    ai_voice = voiced_speech + buzz + consonants
    return ai_voice.astype(np.float32)

audio = generate_ai_tts_voice_clip()
ac = acoustic.detect_tts_artifacts(audio)
pr = prosody.analyze_prosody(audio)

print("Acoustic:", ac)
print("Prosody:", pr)
