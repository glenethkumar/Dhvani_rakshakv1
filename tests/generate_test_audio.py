"""
Dhvani Rakshak - Synthetic Audio Test Generator
Creates benchmark WAV audio files representing Genuine Human Speech vs. AI Cloned Voices
(ElevenLabs, OpenAI Voice, Spliced Voice Attacks).
"""

import os
import wave
import numpy as np

def generate_wav(filename: str, audio: np.ndarray, sample_rate: int = 16000):
    """Save normalized float numpy array as 16-bit PCM WAV."""
    audio_int16 = (audio * 32767.0).astype(np.int16)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(audio_int16.tobytes())
    print(f"Generated test file: {filename} ({len(audio)/sample_rate:.2f}s)")

def generate_genuine_human_audio(duration: float = 3.0, sample_rate: int = 16000) -> np.ndarray:
    """Simulate authentic human voice with natural pitch modulation, micro-jitter, and breathing dynamics."""
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Dynamic F0 pitch variation (120Hz to 160Hz natural pitch curve)
    f0 = 140.0 + 20.0 * np.sin(2 * np.pi * 1.5 * t) + 5.0 * np.cos(2 * np.pi * 4.0 * t)

    # Fundamental + harmonics with human vocal tract resonance
    phase = 2 * np.pi * np.cumsum(f0) / sample_rate
    harm1 = np.sin(phase)
    harm2 = 0.5 * np.sin(2 * phase)
    harm3 = 0.25 * np.sin(3 * phase)
    harm4 = 0.12 * np.sin(4 * phase)

    # Human micro-jitter & breath noise
    jitter_noise = 0.05 * np.random.randn(len(t))
    breath_pause = np.ones(len(t))
    # Insert natural respiratory pause around 1.5s
    pause_idx = int(1.4 * sample_rate)
    pause_len = int(0.25 * sample_rate)
    breath_pause[pause_idx : pause_idx + pause_len] = 0.05

    signal = (harm1 + harm2 + harm3 + harm4 + jitter_noise) * breath_pause
    max_amp = np.max(np.abs(signal))
    return signal / max_amp * 0.90

def generate_elevenlabs_ai_clone(duration: float = 3.0, sample_rate: int = 16000) -> np.ndarray:
    """Simulate ElevenLabs synthetic voice: ultra-flat F0 pitch, phase alignment, high-frequency cutoff."""
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Static pitch contour (145Hz with zero micro-modulation)
    f0 = 145.0 * np.ones(len(t))
    phase = 2 * np.pi * np.cumsum(f0) / sample_rate

    # Perfect mathematical harmonics without human vocal tract jitter
    signal = np.sin(phase) + 0.4 * np.sin(2 * phase) + 0.2 * np.sin(3 * phase)

    # Apply strict 6.5kHz low-pass filter (characteristic neural vocoder cutoff)
    # Filter high frequencies
    fft_sig = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(len(signal), 1/sample_rate)
    fft_sig[freqs > 6500] *= 0.01  # Artificial roll-off
    signal = np.fft.irfft(fft_sig)

    max_amp = np.max(np.abs(signal))
    return signal / max_amp * 0.90

def generate_spliced_audio_attack(duration: float = 3.0, sample_rate: int = 16000) -> np.ndarray:
    """Simulate spliced voice attack: abrupt spectral jumps mid-call."""
    part1 = generate_genuine_human_audio(1.5, sample_rate)
    part2 = generate_elevenlabs_ai_clone(1.5, sample_rate)
    # Abrupt splice at 1.5s
    spliced = np.concatenate([part1, part2 * 2.5])
    max_amp = np.max(np.abs(spliced))
    return spliced / max_amp * 0.90

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "..", "backend", "audio_samples")
    generate_wav(os.path.join(out_dir, "human_genuine.wav"), generate_genuine_human_audio())
    generate_wav(os.path.join(out_dir, "elevenlabs_ai_clone.wav"), generate_elevenlabs_ai_clone())
    generate_wav(os.path.join(out_dir, "spliced_attack.wav"), generate_spliced_audio_attack())
    print("All test audio samples generated successfully!")
