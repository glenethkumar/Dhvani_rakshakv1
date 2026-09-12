import numpy as np
import io
import wave
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_URL = "http://localhost:8000/api/v1/analyze"

def encode_wav_bytes(audio: np.ndarray, sample_rate: int = 16000) -> bytes:
    pcm16 = np.clip(audio * 32767.0, -32768, 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm16.tobytes())
    return buf.getvalue()

def create_live_speech_clip(sr=16000, duration=4.0):
    t = np.linspace(0, duration, int(sr * duration))
    # Human pitch modulation with natural speech prosody & pauses
    f0 = 160.0 + 35.0 * np.sin(2 * np.pi * 1.8 * t) + 12.0 * np.cos(2 * np.pi * 4.2 * t)
    phase = 2 * np.pi * np.cumsum(f0) / sr
    voiced = np.sin(phase) + 0.3 * np.sin(2 * phase) + 0.2 * np.sin(3 * phase)
    # Phonemic modulation with pauses
    syllables = (np.sin(2 * np.pi * 2.0 * t) > -0.3).astype(float)
    # Consonant unvoiced bursts for realistic ZCR
    noise = np.random.randn(len(t))
    consonants = noise * (np.sin(2 * np.pi * 2.0 * t + np.pi/2) > 0.65).astype(float) * 0.2
    audio = voiced * syllables + consonants
    return (audio / np.max(np.abs(audio)) * 0.8).astype(np.float32)

def create_song_clip(sr=16000, duration=4.0):
    t = np.linspace(0, duration, int(sr * duration))
    # Musical continuous harmony with chords, no speech pauses or unvoiced consonant bursts
    c_note = np.sin(2 * np.pi * 261.63 * t)
    e_note = np.sin(2 * np.pi * 329.63 * t)
    g_note = np.sin(2 * np.pi * 392.00 * t)
    audio = 0.4 * c_note + 0.3 * e_note + 0.3 * g_note
    return (audio / np.max(np.abs(audio)) * 0.8).astype(np.float32)

def create_ai_clip(sr=16000, duration=4.0):
    t = np.linspace(0, duration, int(sr * duration))
    # AI synthetic flat pitch (fixed 150Hz tone + 7kHz vocoder artifact)
    f0 = 150.0
    phase = 2 * np.pi * f0 * t
    voiced = 0.5 * np.sin(phase) + 0.25 * np.sin(2 * phase)
    # Robotic constant buzz without natural pauses
    audio = voiced + 0.15 * np.sin(2 * np.pi * 7000 * t)
    return (audio / np.max(np.abs(audio)) * 0.8).astype(np.float32)

if __name__ == "__main__":
    clips = [
        ("1. Live Human Speech", create_live_speech_clip()),
        ("2. Song / Music Clip", create_song_clip()),
        ("3. AI Synthetic Clip", create_ai_clip())
    ]
    
    print("\n--- SENDING 3 TEST CLIPS TO BACKEND ---\n")
    for label, audio in clips:
        wav_data = encode_wav_bytes(audio)
        files = {"file": (f"{label.lower().replace(' ', '_')}.wav", wav_data, "audio/wav")}
        data = {"language": "en-IN"}
        res = requests.post(API_URL, files=files, data=data)
        print(f"Submitted {label} | Response Code: {res.status_code}")
        body = res.json()
        ra = body.get("risk_assessment", {})
        print(f"   -> RiskScore: {ra.get('risk_score')} | AlertLevel: {ra.get('alert_level')} | VoiceLabel: '{ra.get('voice_label')}' | UserMessage: '{ra.get('user_message')}'\n")
