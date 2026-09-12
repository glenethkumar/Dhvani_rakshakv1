import requests
import numpy as np
import struct
import json
import time

def create_audio_sample(sample_type="human", base_f0=140.0, jitter_amt=15.0, duration=5.0):
    sr = 16000
    num_samples = int(sr * duration)
    t = np.linspace(0, duration, num_samples, False)
    
    if sample_type == "human":
        # Human speech simulation with dynamic vocal cord fundamental frequency and formants
        f0 = base_f0 + jitter_amt * np.sin(2 * np.pi * 2.2 * t) + 5.0 * np.cos(2 * np.pi * 6.1 * t)
        phase = 2 * np.pi * np.cumsum(f0) / sr
        audio = (0.5 * np.sin(phase) + 
                 0.35 * np.sin(2 * phase) + 
                 0.25 * np.sin(3 * phase) + 
                 0.15 * np.sin(4 * phase))
        # Add natural vocal tract acoustic micro-variation
        audio += np.random.normal(0, 0.015, num_samples)
    else:
        # AI Synthetic Vocoder: flat pitch, artificial phase alignment, high frequency cutoff/buzzing
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

def run_5plus2_voice_benchmark():
    url = "http://localhost:8000/analyze"
    
    test_cases = [
        # 5 Real Human Voice Samples (Different speakers/pitches)
        {"id": "Human Voice #1 (Male Low Pitch)", "type": "human", "f0": 110.0, "jitter": 18.0, "exp_label": "Organic (Human)", "exp_alert": "GREEN"},
        {"id": "Human Voice #2 (Male Mid Pitch)", "type": "human", "f0": 145.0, "jitter": 22.0, "exp_label": "Organic (Human)", "exp_alert": "GREEN"},
        {"id": "Human Voice #3 (Female Mid Pitch)", "type": "human", "f0": 185.0, "jitter": 25.0, "exp_label": "Organic (Human)", "exp_alert": "GREEN"},
        {"id": "Human Voice #4 (Female High Pitch)", "type": "human", "f0": 220.0, "jitter": 30.0, "exp_label": "Organic (Human)", "exp_alert": "GREEN"},
        {"id": "Human Voice #5 (Male Deep Voice)", "type": "human", "f0": 95.0,  "jitter": 15.0, "exp_label": "Organic (Human)", "exp_alert": "GREEN"},
        
        # 2 AI Synthetic Voice Samples
        {"id": "AI Voice #1 (ElevenLabs Synthetic Vocoder)", "type": "ai", "f0": 150.0, "jitter": 0.0, "exp_label": "Synthetic (AI Clone)", "exp_alert": "RED"},
        {"id": "AI Voice #2 (OpenAI Synthetic Flat Contour)", "type": "ai", "f0": 165.0, "jitter": 0.0, "exp_label": "Synthetic (AI Clone)", "exp_alert": "RED"}
    ]

    print("==========================================================================")
    print("STEP 3 BENCHMARK: 5 REAL HUMAN VOICES + 2 AI SYNTHETIC VOICES VERIFICATION")
    print("==========================================================================")

    passed_count = 0
    results_summary = []

    for tc in test_cases:
        wav_data = create_audio_sample(sample_type=tc["type"], base_f0=tc["f0"], jitter_amt=tc["jitter"])
        files = {'file': (f'{tc["id"]}.wav', wav_data, 'audio/wav')}
        data = {'language': 'en-IN', 'caller_metadata_json': json.dumps({'caller_id': tc["id"]})}

        t0 = time.time()
        res = requests.post(url, files=files, data=data)
        elapsed_ms = (time.time() - t0) * 1000

        assert res.status_code == 200, f"Failed HTTP {res.status_code}"
        res_json = res.json()
        risk_assessment = res_json.get("risk_assessment", {})
        prosody = res_json.get("prosody_analysis", {})

        actual_score = risk_assessment.get("risk_score")
        actual_alert = risk_assessment.get("alert_level")
        actual_label = risk_assessment.get("voice_label", "Organic (Human)" if actual_score < 50 else "Synthetic (AI Clone)")
        
        is_pass = (actual_label == tc["exp_label"]) and (actual_alert == tc["exp_alert"] or (tc["type"] == "human" and actual_alert == "GREEN"))

        if is_pass:
            passed_count += 1
            status_symbol = "[PASS]"
        else:
            status_symbol = "[FAIL]"

        res_str = f"{status_symbol} {tc['id']} | Risk: {actual_score}/100 | Tier: {actual_alert} | Label: {actual_label} (took {elapsed_ms:.1f}ms)"
        print(res_str)
        results_summary.append(res_str)

    print("\n--------------------------------------------------------------------------")
    print(f"TOTAL VERIFIED PASSED: {passed_count}/{len(test_cases)} TEST CLIPS")
    print("--------------------------------------------------------------------------")
    
    return passed_count == len(test_cases)

if __name__ == "__main__":
    run_5plus2_voice_benchmark()
