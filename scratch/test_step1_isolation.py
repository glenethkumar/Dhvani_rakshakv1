import requests
import numpy as np
import struct
import json

def create_sine_speech_audio(duration=5.0, pitch_var=True, noise_level=0.01):
    """
    Simulates human voice audio with rich formant harmonics (100Hz - 3500Hz) and natural pitch variation.
    """
    sr = 16000
    num_samples = int(sr * duration)
    t = np.linspace(0, duration, num_samples, False)
    
    if pitch_var:
        # Dynamic natural pitch variation (F0 contour 120Hz - 220Hz with vibrato & micro-jitter)
        f0 = 160.0 + 35.0 * np.sin(2 * np.pi * 1.8 * t) + 8.0 * np.cos(2 * np.pi * 5.2 * t)
        phase = 2 * np.pi * np.cumsum(f0) / sr
        # Vocal tract formants (F1, F2, F3)
        audio = (0.5 * np.sin(phase) + 
                 0.3 * np.sin(2 * phase) + 
                 0.2 * np.sin(3 * phase) + 
                 0.15 * np.sin(4 * phase))
        # Add slight natural breathiness/acoustic variation
        audio += np.random.normal(0, noise_level, num_samples)
    else:
        # Synthetic flat pitch (150Hz fixed tone + 7kHz vocoder artifact)
        f0 = 150.0
        phase = 2 * np.pi * f0 * t
        audio = 0.5 * np.sin(phase) + 0.2 * np.sin(2 * np.pi * 7000 * t)

    # Normalize Float32 to Int16 PCM
    audio = audio / np.max(np.abs(audio)) * 0.8
    pcm_data = (audio * 32767).astype(np.int16).tobytes()
    
    header = bytearray()
    header.extend(b'RIFF')
    header.extend(struct.pack('<I', 36 + len(pcm_data)))
    header.extend(b'WAVEfmt ')
    header.extend(struct.pack('<I', 16))
    header.extend(struct.pack('<H', 1))  # PCM
    header.extend(struct.pack('<H', 1))  # Mono
    header.extend(struct.pack('<I', sr))
    header.extend(struct.pack('<I', sr * 2))
    header.extend(struct.pack('<H', 2))
    header.extend(struct.pack('<H', 16))
    header.extend(b'data')
    header.extend(struct.pack('<I', len(pcm_data)))
    
    return bytes(header + pcm_data)

def run_step1_isolation():
    url = "http://localhost:8000/analyze"
    
    print("==================================================")
    print("STEP 1: ISOLATING THE BUG (DIRECT FILE VS LIVE MIC)")
    print("==================================================")
    
    # 1. Direct File Test with Natural Speech Dynamics
    human_wav = create_sine_speech_audio(duration=5.0, pitch_var=True, noise_level=0.03)
    files_human = {'file': ('human_sample.wav', human_wav, 'audio/wav')}
    data_human = {'language': 'en-IN', 'caller_metadata_json': json.dumps({'caller_id': 'Direct File Test'})}
    
    res_human = requests.post(url, files=files_human, data=data_human)
    print("\n--- 1. DIRECT FILE TEST (Natural Voice Audio) ---")
    print(f"HTTP Status: {res_human.status_code}")
    json_human = res_human.json()
    print("Raw Response:")
    print(json.dumps(json_human, indent=2))
    
    # 2. Synthetic Audio Test
    synth_wav = create_sine_speech_audio(duration=5.0, pitch_var=False, noise_level=0.001)
    files_synth = {'file': ('synthetic_sample.wav', synth_wav, 'audio/wav')}
    data_synth = {'language': 'en-IN', 'caller_metadata_json': json.dumps({'caller_id': 'Synthetic Test'})}
    
    res_synth = requests.post(url, files=files_synth, data=data_synth)
    print("\n--- 2. DIRECT FILE TEST (Synthetic AI Audio) ---")
    print(f"HTTP Status: {res_synth.status_code}")
    json_synth = res_synth.json()
    print("Risk Score:", json_synth.get("risk_assessment", {}).get("risk_score"))
    print("Alert Level:", json_synth.get("risk_assessment", {}).get("alert_level"))
    print("Voice Type:", json_synth.get("risk_assessment", {}).get("voice_type"))

if __name__ == "__main__":
    run_step1_isolation()
