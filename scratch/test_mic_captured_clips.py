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

def generate_live_direct_human():
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

def generate_song_through_speaker():
    sr = 16000
    t = np.linspace(0, 3.5, int(sr * 3.5))
    chord = np.sin(2 * np.pi * 440.0 * t) + 0.8 * np.sin(2 * np.pi * 554.37 * t) + 0.6 * np.sin(2 * np.pi * 659.25 * t)
    envelope = 0.75 + 0.10 * np.sin(2 * np.pi * 0.4 * t)
    music = chord * envelope
    return (music / np.max(np.abs(music)) * 0.85).astype(np.float32)

def generate_voice_converted_through_speaker():
    sr = 16000
    t = np.linspace(0, 3.5, int(sr * 3.5))
    f0 = 150.0 + 30.0 * np.sin(2 * np.pi * 1.5 * t) + 10.0 * np.cos(2 * np.pi * 3.5 * t)
    phase = 2 * np.pi * np.cumsum(f0) / sr
    vocoder_synth = (np.sin(phase) + 0.4 * np.sin(2 * phase) + 0.2 * np.sin(3 * phase)) * (np.clip(np.sin(2 * np.pi * 2.5 * t), 0, 1) ** 2)
    noise = np.random.randn(len(t))
    b, a = signal.butter(4, [1500.0 / 8000.0, 5000.0 / 8000.0], btype='bandpass')
    consonants = signal.lfilter(b, a, noise) * (np.sin(2 * np.pi * 2.5 * t + np.pi/2) > 0.60).astype(float) * 0.25
    vc_speech = vocoder_synth + consonants
    reverb = np.copy(vc_speech)
    reverb[int(0.028 * sr):] += 0.35 * vc_speech[:-int(0.028 * sr)]
    return (reverb / np.max(np.abs(reverb)) * 0.85).astype(np.float32)

def generate_tts_through_speaker():
    sr = 16000
    t = np.linspace(0, 3.5, int(sr * 3.5))
    f0 = 135.0
    phase = 2 * np.pi * f0 * t
    voiced = (np.sin(phase) + 0.4 * np.sin(2 * phase) + 0.2 * np.sin(3 * phase)) * ((np.sin(2 * np.pi * 2.5 * t) > -0.2).astype(float))
    noise = np.random.randn(len(t))
    b, a = signal.butter(4, [1500.0 / 8000.0, 5000.0 / 8000.0], btype='bandpass')
    consonants = signal.lfilter(b, a, noise) * (np.sin(2 * np.pi * 2.5 * t + np.pi/2) > 0.65).astype(float) * 0.20
    tts_speech = voiced + consonants
    reverb = np.copy(tts_speech)
    reverb[int(0.028 * sr):] += 0.35 * tts_speech[:-int(0.028 * sr)]
    return (reverb / np.max(np.abs(reverb)) * 0.85).astype(np.float32)

def generate_replayed_own_human_voice():
    base_speech = generate_live_direct_human()
    sr = 16000
    reverb = np.copy(base_speech)
    reverb[int(0.028 * sr):] += 0.35 * base_speech[:-int(0.028 * sr)]
    b, a = signal.butter(4, 3500.0 / 8000.0, btype='low')
    ambient_noise = signal.lfilter(b, a, np.random.randn(len(base_speech))) * 0.010
    replayed = reverb + ambient_noise
    return (replayed / np.max(np.abs(replayed)) * 0.85).astype(np.float32)

scenarios = [
    ("1. Live Direct Human Speech", generate_live_direct_human()),
    ("2. Song Played Through Speaker Into Mic", generate_song_through_speaker()),
    ("3. Voice-Converted AI Voice Played Through Speaker", generate_voice_converted_through_speaker()),
    ("4. Genuine TTS-Generated AI Clip Played Through Speaker", generate_tts_through_speaker()),
    ("5. Own Real Voice Played Through Speaker (Replay)", generate_replayed_own_human_voice())
]

print("\n" + "="*95)
print("  STEP 4: FULL REPLAY & VOICE CONVERSION MIC TEST RUN LOGS")
print("="*95 + "\n")

results = []
for name, audio in scenarios:
    wav_bytes = encode_wav_bytes(audio)
    files = {"file": ("live_mic_capture.wav", wav_bytes, "audio/wav")}
    
    import hashlib
    h = hashlib.md5(wav_bytes).hexdigest()
    
    print(f"--- TEST CASE: {name} ---")
    print(f"File Size: {len(wav_bytes)} bytes | MD5: {h}")
    
    resp = requests.post(API_URL, files=files)
    data = resp.json()
    ra = data.get("risk_assessment", {})
    
    status = data.get("status")
    alert_level = ra.get("alert_level")
    risk_score = ra.get("risk_score", 0.0)
    auth_score = ra.get("authenticity_score", 0.0)
    voice_label = ra.get("voice_label", "N/A")
    user_msg = ra.get("user_message", "N/A")
    
    print(f"HTTP Status: {resp.status_code}")
    print(f"Alert Level: {alert_level}")
    print(f"Risk Score: {risk_score:.1f}")
    print(f"Authenticity Score: {auth_score:.1f}%")
    print(f"Voice Label: {voice_label}")
    print(f"User Message: {user_msg}")
    print("-" * 95 + "\n")
    
    results.append({
        "name": name,
        "alert_level": alert_level,
        "risk_score": risk_score,
        "auth_score": auth_score,
        "voice_label": voice_label,
        "user_msg": user_msg
    })

print("="*105)
print("                                      SUMMARY TABLE                                      ")
print("="*105)
print(f"{'Scenario':<55} | {'Voice Label':<22} | {'Risk / Auth Score':<18} | {'State'}")
print("-" * 105)

for r in results:
    nm = r["name"]
    al = r["alert_level"]
    vl = r["voice_label"]
    rs = r["risk_score"]
    aut = r["auth_score"]
    
    if al == "NO_SPEECH_DETECTED":
        score_str = "N/A"
        vl_str = "No Spoken Voice"
        pass_state = "✅ NO SPEECH STATE"
    else:
        score_str = f"Risk {rs:.1f}% / Auth {aut:.1f}%"
        vl_str = vl
        if nm.startswith("1."):
            pass_state = "✅ PASS (Low Risk Organic)" if al == "GREEN" and aut >= 70.0 else "❌ FAIL"
        elif nm.startswith("3.") or nm.startswith("4."):
            pass_state = "✅ PASS (High Risk Synthetic)" if al in ["RED", "YELLOW"] and rs >= 50.0 else "❌ FAIL"
        elif nm.startswith("5."):
            pass_state = "✅ PASS (Organic Replay Verified)" if al == "GREEN" and aut >= 50.0 else "❌ FAIL"
        else:
            pass_state = "UNKNOWN"
            
    print(f"{nm:<55} | {vl_str:<22} | {score_str:<18} | {pass_state}")

print("="*105 + "\n")
