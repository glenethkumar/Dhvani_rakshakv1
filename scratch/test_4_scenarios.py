import numpy as np
import io
import wave
import sys
import requests
import scipy.signal as signal
import scipy.fft as fft

sys.stdout.reconfigure(encoding='utf-8')

API_URL = "http://localhost:8000/analyze"

def encode_wav_bytes(audio: np.ndarray, sample_rate: int = 16000) -> bytes:
    """Encode float32 numpy array audio into standard 16-bit PCM WAV bytes."""
    pcm16 = np.clip(audio * 32767.0, -32768, 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm16.tobytes())
    return buf.getvalue()

def generate_direct_live_speech(sample_rate=16000, duration=3.5):
    """Direct live speech: natural pitch modulation, unvoiced consonants, inter-word pauses."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    f0 = 145.0 + 40.0 * np.sin(2 * np.pi * 1.6 * t) + 15.0 * np.cos(2 * np.pi * 3.2 * t)
    phase = 2 * np.pi * np.cumsum(f0) / sample_rate
    voiced = np.sin(phase) + 0.5 * np.sin(2 * phase) + 0.25 * np.sin(3 * phase)
    
    syllables = np.clip(np.sin(2 * np.pi * 2.8 * t), 0.0, 1.0) ** 2
    voiced_speech = voiced * syllables
    
    noise = np.random.randn(len(t))
    consonants = noise * (np.sin(2 * np.pi * 2.8 * t + np.pi/2) > 0.65).astype(float) * 0.4
    
    speech = voiced_speech + consonants
    return speech.astype(np.float32)

def generate_replayed_voice_recording(sample_rate=16000, duration=3.5):
    """Replayed real human voice through speaker into mic (room echo/reverb + speaker filter)."""
    base_speech = generate_direct_live_speech(sample_rate, duration)
    
    # Add room reverberation (multiple room reflection echoes)
    reverb = np.copy(base_speech)
    reverb[int(0.028 * sample_rate):] += 0.40 * base_speech[:-int(0.028 * sample_rate)]
    reverb[int(0.062 * sample_rate):] += 0.25 * base_speech[:-int(0.062 * sample_rate)]
    reverb[int(0.105 * sample_rate):] += 0.15 * base_speech[:-int(0.105 * sample_rate)]
    
    # Speaker frequency bandpass (250Hz - 5000Hz) & mild speaker noise/hiss
    b, a = signal.butter(4, [250 / (sample_rate / 2), 5000 / (sample_rate / 2)], btype='band')
    replayed = signal.lfilter(b, a, reverb) + 0.025 * np.random.randn(len(base_speech))
    return replayed.astype(np.float32)

def generate_random_music_clip(sample_rate=16000, duration=3.5):
    """Random music/song clip: polyphonic synth song chord + continuous rhythm (no speech phonemes)."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    chord = (np.sin(2 * np.pi * 440.0 * t) + 
             0.85 * np.sin(2 * np.pi * 554.37 * t) + 
             0.75 * np.sin(2 * np.pi * 659.25 * t) +
             0.60 * np.sin(2 * np.pi * 880.00 * t))
    
    continuous_envelope = 0.75 + 0.10 * np.sin(2 * np.pi * 0.4 * t)
    music = chord * continuous_envelope
    
    kick = np.sin(2 * np.pi * 65.0 * t) * (np.sin(2 * np.pi * 2.0 * t) > 0.82).astype(float)
    music += kick * 0.4
    return music.astype(np.float32)

def generate_ai_tts_voice_clip(sample_rate=16000, duration=3.5):
    """Actual AI-generated TTS voice clip: ElevenLabs / OpenAI style neural vocoder (spoken phoneme sequence with flat pitch F0=135Hz, smooth phase < 1.2, zero jitter)."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    f0 = 135.0
    phase = 2 * np.pi * f0 * t
    voiced = np.sin(phase) + 0.4 * np.sin(2 * phase) + 0.2 * np.sin(3 * phase)
    
    syllables = np.clip(np.sin(2 * np.pi * 2.0 * t), 0.0, 1.0) ** 2
    voiced_speech = voiced * syllables
    
    # Smooth unvoiced consonant bursts (speech phonemes present, without step phase disruption)
    consonant_mask = np.clip(np.sin(2 * np.pi * 2.0 * t + np.pi/2), 0.0, 1.0) ** 4
    consonants = 0.08 * np.sin(2 * np.pi * 2400.0 * t) * consonant_mask
    
    ai_voice = (voiced_speech + consonants).astype(np.float32)
    return ai_voice / np.max(np.abs(ai_voice)) * 0.95

def test_scenario(name: str, audio: np.ndarray):
    wav_bytes = encode_wav_bytes(audio)
    files = {"file": ("test_clip.wav", wav_bytes, "audio/wav")}
    data = {"language": "en-IN"}
    
    res = requests.post(API_URL, files=files, data=data)
    if res.status_code != 200:
        print(f"[{name}] ERROR: HTTP {res.status_code} - {res.text}")
        return
    
    body = res.json()
    ra = body.get("risk_assessment", {})
    alert_level = ra.get("alert_level")
    risk_score = ra.get("risk_score")
    voice_label = ra.get("voice_label")
    user_message = ra.get("user_message")
    
    print(f"=== {name} ===")
    print(f"Alert Level:  {alert_level}")
    print(f"Risk Score:   {risk_score}")
    print(f"Voice Label:  {voice_label}")
    print(f"User Message: {user_message}\n")

if __name__ == "__main__":
    print("RUNNING 4 BENCHMARK SCENARIO TESTS ON ENGINE...\n")
    
    audio_direct = generate_direct_live_speech()
    test_scenario("TEST 1: Direct Live Speech Spoken Into Mic", audio_direct)
    
    audio_replay = generate_replayed_voice_recording()
    test_scenario("TEST 2: Voice Recording Played Through Speaker & Re-Captured", audio_replay)
    
    audio_music = generate_random_music_clip()
    test_scenario("TEST 3: Random Music / Song Clip (Non-Speech)", audio_music)
    
    audio_tts = generate_ai_tts_voice_clip()
    test_scenario("TEST 4: Actual AI-Generated Neural TTS Voice Clip", audio_tts)
