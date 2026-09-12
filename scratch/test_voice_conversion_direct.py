import numpy as np
import io
import wave
import sys
import requests
import scipy.signal as signal

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

def generate_voice_converted_ai_clip(sample_rate=16000, duration=3.5):
    """
    Voice-Converted AI Clip (RVC / Voice-to-Voice):
    Preserves human speaker's natural rhythm and pitch modulation (std_f0 = 24.5Hz),
    but alters vocal timbre using neural vocoder synthesis (smooth phase < 1.2, metallic formant resonance, boundary micro-glitches).
    """
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Human pitch modulation from source speaker
    f0 = 145.0 + 35.0 * np.sin(2 * np.pi * 1.5 * t) + 12.0 * np.cos(2 * np.pi * 3.5 * t)
    phase = 2 * np.pi * np.cumsum(f0) / sample_rate
    
    # Neural vocoder timbre conversion (smooth STFT phase alignment & metallic harmonic overtones)
    voiced = np.sin(phase) + 0.45 * np.sin(2 * phase) + 0.25 * np.sin(3 * phase) + 0.15 * np.sin(4 * phase)
    
    syllables = (np.sin(2 * np.pi * 2.5 * t) > -0.2).astype(float)
    voiced_speech = voiced * syllables
    
    # Speech consonants with vocoder frame boundary micro-glitches
    noise = np.random.randn(len(t))
    consonants = noise * (np.sin(2 * np.pi * 2.5 * t + np.pi/2) > 0.60).astype(float) * 0.25
    
    vc_audio = voiced_speech + consonants
    
    # Add subtle neural vocoder boundary micro-glitches
    glitch_mask = (np.sin(2 * np.pi * 5.0 * t) > 0.95).astype(float) * 0.15 * np.random.randn(len(t))
    vc_audio += glitch_mask
    
    return (vc_audio / np.max(np.abs(vc_audio)) * 0.90).astype(np.float32)

if __name__ == "__main__":
    print("\n==================================================================")
    print("  TEST 1: DIRECT FILE UPLOAD TEST FOR VOICE-CONVERTED AI CLIP    ")
    print("==================================================================\n")
    
    audio_vc = generate_voice_converted_ai_clip()
    wav_bytes = encode_wav_bytes(audio_vc)
    files = {"file": ("vc_test_clip.wav", wav_bytes, "audio/wav")}
    data = {"language": "en-IN"}
    
    res = requests.post(API_URL, files=files, data=data)
    print(f"HTTP Status: {res.status_code}")
    body = res.json()
    ra = body.get("risk_assessment", {})
    
    print(f"Alert Level:        {ra.get('alert_level')}")
    print(f"Risk Score:         {ra.get('risk_score')}")
    print(f"Authenticity Score: {ra.get('authenticity_score', ra.get('human_authenticity'))}%")
    print(f"Voice Label:        {ra.get('voice_label')}")
    print(f"User Message:       {ra.get('user_message')}")
    print(f"Primary Reasons:    {body.get('explainability', {}).get('primary_decision_reasons')}")
    print("\n==================================================================\n")
