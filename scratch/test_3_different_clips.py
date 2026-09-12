import numpy as np
import io
import wave
import sys
import requests
import scipy.signal as signal
import json

sys.stdout.reconfigure(encoding='utf-8')

API_URL = "http://localhost:8000/analyze"

def encode_wav_bytes(audio: np.ndarray, sample_rate: int = 16000) -> bytes:
    pcm16 = np.clip(audio * 32767.0, -32768, 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm16.tobytes())
    return buf.getvalue()

def generate_music():
    sr = 16000
    t = np.linspace(0, 3.5, int(sr * 3.5))
    chord = np.sin(2 * np.pi * 440.0 * t) + 0.8 * np.sin(2 * np.pi * 554.37 * t) + 0.6 * np.sin(2 * np.pi * 659.25 * t)
    return (chord / np.max(np.abs(chord)) * 0.85).astype(np.float32)

def generate_real_human():
    sr = 16000
    t = np.linspace(0, 3.5, int(sr * 3.5))
    f0 = 145.0 + 35.0 * np.sin(2 * np.pi * 1.5 * t) + 12.0 * np.cos(2 * np.pi * 3.5 * t) + 3.0 * np.random.randn(len(t))
    phase = 2 * np.pi * np.cumsum(f0) / sr
    voiced = (np.sin(phase) + 0.5 * np.sin(2 * phase) + 0.25 * np.sin(3 * phase)) * (np.clip(np.sin(2 * np.pi * 2.5 * t), 0, 1) ** 2)
    noise = np.random.randn(len(t))
    b, a = signal.butter(4, [1500.0 / 8000.0, 5000.0 / 8000.0], btype='bandpass')
    consonants = signal.lfilter(b, a, noise) * (np.sin(2 * np.pi * 2.5 * t + np.pi/2) > 0.60).astype(float) * 0.25
    speech = voiced + consonants
    return (speech / np.max(np.abs(speech)) * 0.85).astype(np.float32)

def generate_ai_clip():
    sr = 16000
    t = np.linspace(0, 3.5, int(sr * 3.5))
    f0 = 135.0
    phase = 2 * np.pi * f0 * t
    voiced = (np.sin(phase) + 0.4 * np.sin(2 * phase) + 0.2 * np.sin(3 * phase)) * ((np.sin(2 * np.pi * 2.5 * t) > -0.2).astype(float))
    return (voiced / np.max(np.abs(voiced)) * 0.85).astype(np.float32)

clips = [
    ("1. Random Music (Non-Speech)", generate_music()),
    ("2. Real Human Speech", generate_real_human()),
    ("3. AI Voice Clip (Flat Pitch Vocoder)", generate_ai_clip())
]

print("\n" + "="*80)
print("  STEP 1: PER-REQUEST AI MODEL EVALUATION LOGS SIDE-BY-SIDE")
print("="*80 + "\n")

for label, audio in clips:
    wav_bytes = encode_wav_bytes(audio)
    files = {"file": ("test.wav", wav_bytes, "audio/wav")}
    
    import hashlib
    h = hashlib.md5(wav_bytes).hexdigest()
    print(f"--- PRE-CALL LOG ---")
    print(f"Clip: {label}")
    print(f"File Size: {len(wav_bytes)} bytes | MD5 Hash: {h}")
    
    resp = requests.post(API_URL, files=files)
    data = resp.json()
    ra = data.get("risk_assessment", {})
    
    print(f"--- POST-CALL RESPONSE LOG ---")
    print(f"HTTP Status: {resp.status_code}")
    print(f"Alert Level: {ra.get('alert_level')}")
    print(f"Risk Score: {ra.get('risk_score')}")
    print(f"Authenticity Score: {ra.get('authenticity_score')}%")
    print(f"Voice Label: {ra.get('voice_label')}")
    print(f"User Message: {ra.get('user_message')}")
    print("="*80 + "\n")
