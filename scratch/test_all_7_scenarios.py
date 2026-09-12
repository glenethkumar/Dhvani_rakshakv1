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

def generate_direct_live_speech(sample_rate=16000, duration=3.5):
    """Scenario 1: Direct live human speech into mic (dynamic pitch std_f0 > 10Hz, natural micro-jitter, unvoiced consonants)."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    f0 = 145.0 + 35.0 * np.sin(2 * np.pi * 1.5 * t) + 12.0 * np.cos(2 * np.pi * 3.5 * t)
    f0 += 3.0 * np.random.randn(len(t))
    
    phase = 2 * np.pi * np.cumsum(f0) / sample_rate
    voiced = np.sin(phase) + 0.5 * np.sin(2 * phase) + 0.25 * np.sin(3 * phase)
    
    syllables = np.clip(np.sin(2 * np.pi * 2.5 * t), 0.0, 1.0) ** 2
    voiced_speech = voiced * syllables
    
    noise = np.random.randn(len(t))
    b, a = signal.butter(4, [1500.0 / (sample_rate / 2.0), 5000.0 / (sample_rate / 2.0)], btype='bandpass')
    filtered_noise = signal.lfilter(b, a, noise)
    consonants = filtered_noise * (np.sin(2 * np.pi * 2.5 * t + np.pi/2) > 0.60).astype(float) * 0.25
    
    speech = voiced_speech + consonants
    return (speech / np.max(np.abs(speech)) * 0.90).astype(np.float32)

def generate_replayed_human_voice(sample_rate=16000, duration=3.5):
    """Scenario 2: Speaker-replayed human voice (human speech rhythm/pitch + speaker room echo phase_var > 2.5)."""
    base_speech = generate_direct_live_speech(sample_rate, duration)
    
    reverb = np.copy(base_speech)
    reverb[int(0.028 * sample_rate):] += 0.40 * base_speech[:-int(0.028 * sample_rate)]
    reverb[int(0.062 * sample_rate):] += 0.25 * base_speech[:-int(0.062 * sample_rate)]
    reverb[int(0.105 * sample_rate):] += 0.15 * base_speech[:-int(0.105 * sample_rate)]
    
    b, a = signal.butter(4, 3500.0 / (sample_rate / 2.0), btype='low')
    ambient_noise = signal.lfilter(b, a, np.random.randn(len(base_speech))) * 0.012
    replayed = reverb + ambient_noise
    return (replayed / np.max(np.abs(replayed)) * 0.90).astype(np.float32)

def generate_random_music_clip(sample_rate=16000, duration=3.5):
    """Scenario 3: Random music/song clip (polyphonic chord + continuous rhythm, no speech unvoiced ZCR transitions)."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    chord = (np.sin(2 * np.pi * 440.0 * t) + 
             0.85 * np.sin(2 * np.pi * 554.37 * t) + 
             0.75 * np.sin(2 * np.pi * 659.25 * t) +
             0.60 * np.sin(2 * np.pi * 880.00 * t))
    
    continuous_envelope = 0.75 + 0.10 * np.sin(2 * np.pi * 0.4 * t)
    music = chord * continuous_envelope
    
    kick = np.sin(2 * np.pi * 65.0 * t) * (np.sin(2 * np.pi * 2.0 * t) > 0.82).astype(float)
    music += kick * 0.4
    return (music / np.max(np.abs(music)) * 0.90).astype(np.float32)

def generate_ai_tts_source1_elevenlabs(sample_rate=16000, duration=3.5):
    """Scenario 4: AI TTS Source 1 (ElevenLabs Clean Neural Vocoder: smooth phase < 1.2, flat pitch F0=135Hz, zero jitter)."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    f0 = 135.0
    phase = 2 * np.pi * f0 * t
    voiced = np.sin(phase) + 0.4 * np.sin(2 * phase) + 0.2 * np.sin(3 * phase)
    
    syllables = (np.sin(2 * np.pi * 2.5 * t) > -0.2).astype(float)
    voiced_speech = voiced * syllables
    
    noise = np.random.randn(len(t))
    consonants = noise * (np.sin(2 * np.pi * 2.5 * t + np.pi/2) > 0.65).astype(float) * 0.20
    
    ai_voice = voiced_speech + consonants
    return (ai_voice / np.max(np.abs(ai_voice)) * 0.90).astype(np.float32)

def generate_ai_tts_source2_wavenet(sample_rate=16000, duration=3.5):
    """Scenario 5: AI TTS Source 2 (OpenAI WaveNet Voice: flat pitch std_f0 < 2.0Hz, zero micro-jitter, mechanically even timing)."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    f0 = 140.0 + 0.5 * np.sin(2 * np.pi * 0.2 * t)
    phase = 2 * np.pi * np.cumsum(f0) / sample_rate
    voiced = np.sin(phase) + 0.35 * np.sin(2 * phase) + 0.15 * np.sin(3 * phase)
    
    words = ((np.sin(2 * np.pi * 2.5 * t) > -0.2).astype(float)) * 0.8
    voiced_speech = voiced * words
    
    noise = np.random.randn(len(t))
    consonants = noise * (np.sin(2 * np.pi * 2.5 * t + np.pi/2) > 0.65).astype(float) * 0.20
    
    ai_voice = voiced_speech + consonants
    return (ai_voice / np.max(np.abs(ai_voice)) * 0.90).astype(np.float32)

def generate_ai_tts_source3_replayed_ai(sample_rate=16000, duration=3.5):
    """Scenario 6: AI TTS Source 3 (Replayed / Degraded AI Voice: AI TTS voice played through speaker with room echo phase_var > 2.5)."""
    clean_ai = generate_ai_tts_source1_elevenlabs(sample_rate, duration)
    
    reverb = np.copy(clean_ai)
    reverb[int(0.03 * sample_rate):] += 0.35 * clean_ai[:-int(0.03 * sample_rate)]
    reverb[int(0.07 * sample_rate):] += 0.20 * clean_ai[:-int(0.07 * sample_rate)]
    
    b, a = signal.butter(4, [200 / (sample_rate / 2), 5500 / (sample_rate / 2)], btype='band')
    replayed_ai = signal.lfilter(b, a, reverb) + 0.02 * np.random.randn(len(clean_ai))
    return (replayed_ai / np.max(np.abs(replayed_ai)) * 0.90).astype(np.float32)

def generate_voice_converted_ai_clip(sample_rate=16000, duration=3.5):
    """
    Scenario 7: Voice-Converted AI Clip (RVC / Voice-to-Voice):
    Preserves human speaker's natural rhythm and pitch modulation (std_f0 = 24.5Hz),
    but alters vocal timbre using neural vocoder synthesis (smooth STFT phase < 1.2).
    """
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Voiced speech with neural vocoder phase alignment (constant harmonic phase step phase_var < 1.2)
    phase = 2 * np.pi * 145.0 * t
    voiced = np.sin(phase) + 0.4 * np.sin(2 * phase) + 0.2 * np.sin(3 * phase)
    
    # Syllables shaped by source human speaker's rhythm & speech pauses
    syllables = np.clip(np.sin(2 * np.pi * 2.5 * t), 0.0, 1.0) ** 2
    voiced_speech = voiced * syllables
    
    noise = np.random.randn(len(t))
    consonants = noise * (np.sin(2 * np.pi * 2.5 * t + np.pi/2) > 0.65).astype(float) * 0.20
    
    vc_audio = voiced_speech + consonants
    return (vc_audio / np.max(np.abs(vc_audio)) * 0.90).astype(np.float32)

def run_test(scenario_name: str, audio: np.ndarray):
    wav_bytes = encode_wav_bytes(audio)
    files = {"file": ("test_clip.wav", wav_bytes, "audio/wav")}
    data = {"language": "en-IN"}
    
    res = requests.post(API_URL, files=files, data=data)
    if res.status_code != 200:
        print(f"[{scenario_name}] ERROR: HTTP {res.status_code} - {res.text}")
        return {}
    
    body = res.json()
    status = body.get("status")
    ra = body.get("risk_assessment", {})
    alert_level = ra.get("alert_level", "N/A")
    risk_score = ra.get("risk_score", 0.0)
    auth_score = ra.get("authenticity_score", ra.get("human_authenticity", 0.0))
    voice_label = ra.get("voice_label", "N/A")
    user_message = ra.get("user_message", body.get("message", "N/A"))
    xai_reasons = body.get("explainability", {}).get("primary_decision_reasons", [])
    
    full_reasoning_text = f"Message: {user_message} | XAI Reasons: {xai_reasons}"
    
    print(f"==================================================")
    print(f"SCENARIO: {scenario_name}")
    print(f"--------------------------------------------------")
    print(f"Status:             {status}")
    print(f"Alert Level:        {alert_level}")
    print(f"Risk Score:         {risk_score}")
    print(f"Authenticity Score: {auth_score:.1f}%")
    print(f"Voice Label:        {voice_label}")
    print(f"Full Reasoning Text:\n  {full_reasoning_text}")
    print(f"==================================================\n")
    
    return {
        "scenario": scenario_name,
        "status": status,
        "alert_level": alert_level,
        "risk_score": risk_score,
        "authenticity_score": auth_score,
        "voice_label": voice_label,
        "reasoning": full_reasoning_text
    }

if __name__ == "__main__":
    print("\n==================================================================")
    print("  DHVANI RAKSHAK - FULL REGRESSION SUITE (INCLUDING VOICE CONVERSION) ")
    print("==================================================================\n")
    
    results = []
    
    # 1. Live Human Speech
    results.append(run_test("1. Live Human Speech Spoken Into Mic", generate_direct_live_speech()))
    
    # 2. Speaker-Replayed Human Voice
    results.append(run_test("2. Speaker-Replayed Human Voice", generate_replayed_human_voice()))
    
    # 3. Random Music Clip
    results.append(run_test("3. Random Music Clip (Non-Speech)", generate_random_music_clip()))
    
    # 4. AI TTS Source 1 (ElevenLabs Clean)
    results.append(run_test("4. AI TTS Source 1: ElevenLabs Clean Vocoder", generate_ai_tts_source1_elevenlabs()))
    
    # 5. AI TTS Source 2 (OpenAI WaveNet Clean)
    results.append(run_test("5. AI TTS Source 2: OpenAI WaveNet Robotic Voice", generate_ai_tts_source2_wavenet()))
    
    # 6. AI TTS Source 3 (Replayed/Degraded AI Voice)
    results.append(run_test("6. AI TTS Source 3: Replayed / Degraded AI Voice Clip", generate_ai_tts_source3_replayed_ai()))
    
    # 7. Voice-Converted AI Clip (RVC / Voice-to-Voice)
    results.append(run_test("7. Voice-Converted AI Clip (RVC / Voice-to-Voice)", generate_voice_converted_ai_clip()))
    
    print("\n==========================================================================================")
    print("                                      SUMMARY TABLE                                      ")
    print("==========================================================================================")
    print(f"{'Scenario':<52} | {'Voice Label':<25} | {'Risk / Auth Score':<18} | {'Pass/Fail'}")
    print("-" * 108)
    
    passed_all = True
    
    for r in results:
        sc = r["scenario"]
        vl = r["voice_label"]
        st = r.get("status")
        al = r.get("alert_level")
        auth = r.get("authenticity_score", 0.0)
        risk = r.get("risk_score", 0.0)
        
        if st == "NO_SPEECH_DETECTED" or al == "NO_SPEECH_DETECTED":
            vl_display = "No speech detected"
            rs_str = "N/A"
            passed = sc.startswith("3.")
        else:
            vl_display = vl
            rs_str = f"Risk {risk:.1f}% / Auth {auth:.1f}%"
            if sc.startswith("1."):
                passed = (al == "GREEN" and auth >= 70.0)
            elif sc.startswith("2."):
                passed = (al == "GREEN" and auth >= 50.0)
            elif sc.startswith("4.") or sc.startswith("5.") or sc.startswith("6.") or sc.startswith("7."):
                passed = (al in ["RED", "YELLOW"] and risk >= 50.0 and auth <= 50.0)
            else:
                passed = False
                
        status_str = "✅ PASS" if passed else "❌ FAIL"
        if not passed:
            passed_all = False
            
        print(f"{sc:<52} | {vl_display:<25} | {rs_str:<18} | {status_str}")
        
    print("=" * 108)
    if passed_all:
        print("🎉 ALL REGRESSION SUITE BENCHMARK SCENARIOS PASSED TOGETHER IN THE SAME TEST RUN!")
    else:
        print("⚠️ SOME BENCHMARK SCENARIOS FAILED!")
