import requests
import numpy as np
import struct
import json
import time

def generate_mic_pcm_wav(duration=5.0, is_synthetic=False):
    sample_rate = 16000
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples, False)
    
    if is_synthetic:
        # Flat pitch contour, high frequency harmonic artifacts (AI-like)
        freq = 150.0  # static pitch
        phase = 2 * np.pi * freq * t
        signal = np.sin(phase) * 0.4 + np.sin(2 * np.pi * 7000 * t) * 0.1
    else:
        # Organic pitch variation (Human-like)
        freq = 140.0 + 20.0 * np.sin(2 * np.pi * 1.5 * t)
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        signal = np.sin(phase) * 0.4
    
    pcm_data = (signal * 32767).astype(np.int16).tobytes()
    
    header = bytearray()
    header.extend(b'RIFF')
    header.extend(struct.pack('<I', 36 + len(pcm_data)))
    header.extend(b'WAVEfmt ')
    header.extend(struct.pack('<I', 16))
    header.extend(struct.pack('<H', 1))  # PCM
    header.extend(struct.pack('<H', 1))  # Mono
    header.extend(struct.pack('<I', sample_rate))
    header.extend(struct.pack('<I', sample_rate * 2))
    header.extend(struct.pack('<H', 2))
    header.extend(struct.pack('<H', 16))
    header.extend(b'data')
    header.extend(struct.pack('<I', len(pcm_data)))
    
    return bytes(header + pcm_data)

def test_full_flow(run_idx):
    print(f"\n--- TEST RUN {run_idx}/3 ---")
    url = "http://localhost:8000/analyze"
    wav_bytes = generate_mic_pcm_wav(duration=5.0, is_synthetic=(run_idx == 2))
    
    files = {'file': ('live_mic_5s.wav', wav_bytes, 'audio/wav')}
    data = {
        'language': 'en-IN',
        'caller_metadata_json': json.dumps({'caller_id': 'Live Mic Capture'})
    }
    
    start_time = time.time()
    res = requests.post(url, files=files, data=data)
    elapsed_ms = (time.time() - start_time) * 1000
    
    print(f"HTTP Status: {res.status_code} (took {elapsed_ms:.1f}ms)")
    assert res.status_code == 200, f"Expected HTTP 200, got {res.status_code}"
    
    resp_json = res.json()
    risk_assessment = resp_json.get("risk_assessment", {})
    prosody = resp_json.get("prosody_analysis", {})
    acoustic = resp_json.get("acoustic_analysis", {})
    
    risk_score = risk_assessment.get("risk_score")
    alert_level = risk_assessment.get("alert_level")
    voice_naturalness = "Synthetic (AI Clone)" if (risk_score >= 50 or alert_level in ['RED', 'YELLOW']) else "Organic (Human)"
    pitch_hz = prosody.get("mean_f0_hz")
    jitter_pct = prosody.get("jitter_percent")
    phase_smoothness = acoustic.get("spectral_features", {}).get("phase_smoothness_variance")
    
    print("Parsed Front-End Real Values:")
    print(f"  - Voice Naturalness : {voice_naturalness}")
    print(f"  - Voice Pitch (Hz)  : {pitch_hz} Hz")
    print(f"  - Pitch Variation   : {jitter_pct}%")
    print(f"  - Acoustic Clarity  : {phase_smoothness}")
    print(f"  - Risk Score        : {risk_score}/100 [{alert_level}]")
    
    status_text = "Authenticated"
    if alert_level == 'RED':
        status_text = "High Risk — Flagged for Review"
    elif alert_level == 'YELLOW':
        status_text = "Step-up Verification Recommended"
    
    log_entry = {
        "time": time.strftime("%H:%M:%S"),
        "callerIdentity": "Live Mic Capture",
        "riskScore": risk_score,
        "alertTier": alert_level,
        "decisionLabel": status_text
    }
    print(f"  - Appended Log Entry: {json.dumps(log_entry)}")
    return True

if __name__ == "__main__":
    for i in range(1, 4):
        success = test_full_flow(i)
        if not success:
            print("Test failed on run", i)
            break
    print("\n[SUCCESS] ALL 3 CONSECUTIVE TEST RUNS COMPLETED SUCCESSFULLY!")
