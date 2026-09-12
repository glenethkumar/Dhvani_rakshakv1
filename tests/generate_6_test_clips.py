"""
Dhvani Rakshak - Standard 6-Clip Test Audio Generator for Step 3 Verification Suite
Generates:
  1. Live human speech (clearly speaking a sentence)
  2. Replayed human speech (human voice replayed through a speaker / room impulse)
  3. Song / music clip (instrumental / melodic song track without spoken speech)
  4. Silence / no audio (ambient quiet room hiss)
  5. TTS-generated AI voice clip (flat pitch contour, zero jitter, vocoder phase alignment)
  6. Voice-converted AI clip (real human rhythm/pitch variation, synthetic vocal timbre)
"""

import os
import wave
import numpy as np
import scipy.signal as signal

def save_wav(filename: str, audio: np.ndarray, sample_rate: int = 16000):
    audio_int16 = (np.clip(audio, -0.99, 0.99) * 32767.0).astype(np.int16)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(audio_int16.tobytes())

def generate_live_human_speech(duration: float = 3.0, sample_rate: int = 16000) -> np.ndarray:
    """1. Live human speech: natural pitch modulation (120-160Hz), micro-jitter, unvoiced consonants."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    f0 = 135.0 + 22.0 * np.sin(2 * np.pi * 1.6 * t) + 7.0 * np.cos(2 * np.pi * 4.2 * t)
    phase = 2 * np.pi * np.cumsum(f0) / sample_rate
    audio = np.sin(phase) + 0.4 * np.sin(2 * phase) + 0.2 * np.sin(3 * phase) + 0.1 * np.sin(4 * phase)
    
    # Human vocal cord micro-jitter noise
    audio += 0.04 * np.random.randn(len(t))
    
    # Insert unvoiced consonants (s, sh, t, k)
    for pos in [0.4, 1.1, 1.8, 2.4]:
        idx = int(pos * sample_rate)
        audio[idx : idx + 1200] += np.random.normal(0, 0.35, 1200)

    # Insert respiratory pause
    p_idx = int(1.4 * sample_rate)
    p_len = int(0.25 * sample_rate)
    audio[p_idx : p_idx + p_len] *= 0.05

    max_amp = np.max(np.abs(audio))
    return audio / max_amp * 0.85

def generate_replayed_human_speech(duration: float = 3.0, sample_rate: int = 16000) -> np.ndarray:
    """2. Replayed human speech: genuine human speech played through speaker into mic (reverb + high-freq attenuation)."""
    raw_human = generate_live_human_speech(duration, sample_rate)
    
    # Simulate room acoustics & speaker frequency response (low-pass filter + slight reverberation decay)
    b, a = signal.butter(4, 3800.0 / (sample_rate / 2.0), btype='low')
    replayed = signal.lfilter(b, a, raw_human)
    
    # Add room reverberation echo (decaying delayed copy)
    delay_samples = int(0.04 * sample_rate)
    reverb = np.zeros_like(replayed)
    reverb[delay_samples:] = replayed[:-delay_samples] * 0.25
    replayed += reverb
    
    # Add microphone background noise floor
    replayed += np.random.normal(0, 0.012, len(replayed))
    
    max_amp = np.max(np.abs(replayed))
    return replayed / max_amp * 0.80

def generate_song_music_clip(duration: float = 3.0, sample_rate: int = 16000) -> np.ndarray:
    """3. Song / music clip: polyphonic musical chord progression without human spoken voice phonemes."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Musical chord progression (C Major: C4=261.63Hz, E4=329.63Hz, G4=392.00Hz, A4=440.00Hz)
    note1 = np.sin(2 * np.pi * 261.63 * t)
    note2 = 0.7 * np.sin(2 * np.pi * 329.63 * t)
    note3 = 0.5 * np.sin(2 * np.pi * 392.00 * t)
    note4 = 0.4 * np.sin(2 * np.pi * 523.25 * t)
    
    # Rhythmic beat / percussion synth pulse
    beat = 0.3 * np.sin(2 * np.pi * 60 * t) * (np.sin(2 * np.pi * 2 * t) > 0)
    
    music = note1 + note2 + note3 + note4 + beat
    max_amp = np.max(np.abs(music))
    return music / max_amp * 0.85

def generate_silence_no_audio(duration: float = 3.0, sample_rate: int = 16000) -> np.ndarray:
    """4. Silence / no audio: quiet mic room background noise (very low energy < 0.003)."""
    return np.random.normal(0, 0.0015, int(sample_rate * duration))

def generate_tts_ai_voice(duration: float = 3.0, sample_rate: int = 16000) -> np.ndarray:
    """5. TTS-generated AI voice: ultra-flat pitch contour (145Hz), zero micro-jitter, 6.5kHz vocoder cutoff."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    f0 = 145.0 * np.ones(len(t))
    phase = 2 * np.pi * np.cumsum(f0) / sample_rate
    
    # Perfect mathematical harmonics (zero human vocal cord jitter)
    audio = np.sin(phase) + 0.45 * np.sin(2 * phase) + 0.25 * np.sin(3 * phase)
    
    # Apply strict 6.5kHz low-pass filter (characteristic neural vocoder cutoff)
    fft_sig = np.fft.rfft(audio)
    freqs = np.fft.rfftfreq(len(audio), 1/sample_rate)
    fft_sig[freqs > 6500] *= 0.01
    audio = np.fft.irfft(fft_sig)
    
    max_amp = np.max(np.abs(audio))
    return audio / max_amp * 0.85

def generate_voice_converted_ai_clip(duration: float = 3.0, sample_rate: int = 16000) -> np.ndarray:
    """6. Voice-converted AI clip (RVC/Voice-to-Voice): real speech rhythm/pitch variation, synthetic vocal timbre."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Human-like pitch variation
    f0 = 150.0 + 25.0 * np.sin(2 * np.pi * 1.8 * t) + 8.0 * np.cos(2 * np.pi * 4.5 * t)
    phase = 2 * np.pi * np.cumsum(f0) / sample_rate
    
    # Synthetic vocal timbre: perfectly aligned vocoder phase + unnaturally metallic formant resonance
    formant_mod = 1.0 + 0.6 * np.sin(2 * np.pi * 3200 * t)
    audio = (np.sin(phase) + 0.5 * np.sin(2 * phase) + 0.3 * np.sin(3 * phase)) * formant_mod
    
    # Phase alignment artifact (smooth phase)
    stft_mat = signal.stft(audio, fs=sample_rate, nperseg=256, noverlap=128)[2]
    audio = signal.istft(stft_mat, fs=sample_rate, nperseg=256, noverlap=128)[1]
    
    max_amp = np.max(np.abs(audio))
    return audio / max_amp * 0.85

def generate_all_6_clips(out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    clips = {
        "1_live_human_speech.wav": generate_live_human_speech(),
        "2_replayed_human_speech.wav": generate_replayed_human_speech(),
        "3_song_music_clip.wav": generate_song_music_clip(),
        "4_silence_no_audio.wav": generate_silence_no_audio(),
        "5_tts_ai_voice.wav": generate_tts_ai_voice(),
        "6_voice_converted_ai_clip.wav": generate_voice_converted_ai_clip(),
    }
    for filename, audio in clips.items():
        filepath = os.path.join(out_dir, filename)
        save_wav(filepath, audio)
        print(f"Generated benchmark clip: {filename} ({len(audio)/16000:.1f}s)")

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "regression_audio")
    generate_all_6_clips(out_dir)
