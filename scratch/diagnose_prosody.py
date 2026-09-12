import requests
import numpy as np
import struct
import json

def create_audio(sample_type="human", base_f0=110.0, jitter_amt=18.0):
    sr = 16000
    duration = 5.0
    num_samples = int(sr * duration)
    t = np.linspace(0, duration, num_samples, False)
    
    if sample_type == "human":
        f0 = base_f0 + jitter_amt * np.sin(2 * np.pi * 2.2 * t) + 5.0 * np.cos(2 * np.pi * 6.1 * t)
        phase = 2 * np.pi * np.cumsum(f0) / sr
        audio = (0.5 * np.sin(phase) + 
                 0.35 * np.sin(2 * phase) + 
                 0.25 * np.sin(3 * phase) + 
                 0.15 * np.sin(4 * phase))
        audio += np.random.normal(0, 0.015, num_samples)
    else:
        f0 = base_f0
        phase = 2 * np.pi * f0 * t
        audio = 0.5 * np.sin(phase) + 0.25 * np.sin(2 * np.pi * 7200 * t) + 0.15 * np.sin(2 * np.pi * 3.5 * t)
        
    audio = audio / np.max(np.abs(audio)) * 0.85
    pcm_data = (audio * 32767).astype(np.int16).tobytes()
    
    header = bytearray()
    header.extend(b'RIFF')
    header.extend(struct.pack('<I', 36 + len(pcm_data)))
    header.extend(b'WAVEfmt ')
    header.extend(struct.pack('<I', 16))
    header.extend(struct.pack('<H', 1))
    header.extend(struct.pack('<H', 1))
    header.extend(struct.pack('<I', sr))
    header.extend(struct.pack('<I', sr * 2))
    header.extend(struct.pack('<H', 2))
    header.extend(struct.pack('<H', 16))
    header.extend(b'data')
    header.extend(struct.pack('<I', len(pcm_data)))
    
    return bytes(header + pcm_data)

def diagnose():
    url = "http://localhost:8000/analyze"
    
    # 1. Male Low Pitch Human
    wav1 = create_audio("human", 110.0, 18.0)
    res1 = requests.post(url, files={'file': ('male_low.wav', wav1, 'audio/wav')})
    print("=== MALE LOW PITCH HUMAN VOICE ===")
    j1 = res1.json()
    print("Prosody Analysis:", json.dumps(j1.get("prosody_analysis"), indent=2))
    print("Acoustic Analysis:", json.dumps(j1.get("acoustic_analysis"), indent=2))
    print("Risk Assessment:", json.dumps(j1.get("risk_assessment"), indent=2))

if __name__ == "__main__":
    diagnose()
