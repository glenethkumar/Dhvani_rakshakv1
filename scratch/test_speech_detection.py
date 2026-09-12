import numpy as np
import scipy.signal as signal
import scipy.fft as fft

def generate_speech_sample(sample_rate=16000, duration=3.0, replayed=False):
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Speech pitch variation (F0 around 150 Hz with dynamic intonation)
    f0 = 150.0 + 35.0 * np.sin(2 * np.pi * 1.8 * t) + 15.0 * np.cos(2 * np.pi * 3.5 * t)
    phase = 2 * np.pi * np.cumsum(f0) / sample_rate
    voiced = np.sin(phase) + 0.5 * np.sin(2 * phase) + 0.25 * np.sin(3 * phase)
    
    # Syllable amplitude modulation with micro-pauses
    syllable_mod = np.clip(np.sin(2 * np.pi * 3.0 * t), 0.0, 1.0) ** 2
    voiced_speech = voiced * syllable_mod
    
    # Unvoiced consonant bursts (high ZCR 's', 't', 'f' phonemes)
    noise = np.random.randn(len(t))
    consonant_mask = (np.sin(2 * np.pi * 3.0 * t + np.pi/2) > 0.6).astype(float)
    unvoiced_speech = noise * consonant_mask * 0.4
    
    speech = voiced_speech + unvoiced_speech
    
    if replayed:
        # Replay simulation: room reverberation (echoes at 25ms, 55ms) + speaker frequency filter
        reverb = np.zeros_like(speech)
        reverb += speech
        reverb[int(0.025 * sample_rate):] += 0.35 * speech[:-int(0.025 * sample_rate)]
        reverb[int(0.055 * sample_rate):] += 0.20 * speech[:-int(0.055 * sample_rate)]
        
        # Bandpass filter (200Hz - 5500Hz) & mild speaker noise
        b, a = signal.butter(4, [200 / (sample_rate / 2), 5500 / (sample_rate / 2)], btype='band')
        replayed_speech = signal.lfilter(b, a, reverb) + 0.02 * np.random.randn(len(t))
        return replayed_speech.astype(np.float32)
    
    return speech.astype(np.float32)

def generate_music_sample(sample_rate=16000, duration=3.0):
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Polyphonic synth song chord (A4 440Hz, C#5 554.37Hz, E5 659.25Hz) + background drum beat
    chord = (np.sin(2 * np.pi * 440.0 * t) + 
             0.8 * np.sin(2 * np.pi * 554.37 * t) + 
             0.7 * np.sin(2 * np.pi * 659.25 * t))
    
    # Continuous sustained musical volume (no speech pauses)
    music_envelope = 0.7 + 0.15 * np.sin(2 * np.pi * 0.5 * t)
    music = chord * music_envelope
    
    # Percussive beat (sub-bass kick)
    kick = np.sin(2 * np.pi * 60.0 * t) * (np.sin(2 * np.pi * 2.0 * t) > 0.8).astype(float)
    music += kick * 0.5
    return music.astype(np.float32)

def is_spoken_human_speech(audio: np.ndarray, sample_rate: int = 16000) -> tuple:
    if len(audio) == 0:
        return False, "EMPTY_AUDIO"
    
    max_amp = float(np.max(np.abs(audio)))
    rms_energy = float(np.sqrt(np.mean(audio ** 2)))
    if max_amp < 0.015 or rms_energy < 0.002:
        return False, "SILENCE_OR_LOW_ENERGY"
    
    # Frame-based feature extraction (25ms frames, 10ms hop)
    frame_len = int(sample_rate * 0.025)
    hop_len = int(sample_rate * 0.010)
    num_frames = (len(audio) - frame_len) // hop_len + 1
    
    if num_frames < 10:
        return False, "AUDIO_TOO_SHORT"
        
    frames = np.array([audio[i*hop_len : i*hop_len + frame_len] for i in range(num_frames)])
    
    # 1. Zero Crossing Rate (ZCR) per frame
    zcr = np.mean(np.abs(np.diff(np.sign(frames), axis=1)) > 0, axis=1)
    std_zcr = float(np.std(zcr))
    high_zcr_ratio = float(np.mean(zcr > 0.12)) # Ratio of unvoiced consonant frames
    
    # 2. Frame energy distribution & Pause Ratio
    frame_energies = np.mean(frames ** 2, axis=1)
    max_frame_energy = np.max(frame_energies) + 1e-10
    pause_ratio = float(np.mean(frame_energies < (0.12 * max_frame_energy)))
    
    # 3. Spectral Flux (frame-to-frame STFT magnitude difference)
    stft_mag = np.abs(fft.rfft(frames, axis=1))
    stft_norm = stft_mag / (np.sum(stft_mag, axis=1, keepdims=True) + 1e-10)
    flux = np.mean(np.abs(np.diff(stft_norm, axis=0)))
    
    print(f"Metrics -> std_zcr: {std_zcr:.4f}, high_zcr_ratio: {high_zcr_ratio:.4f}, pause_ratio: {pause_ratio:.4f}, flux: {flux:.4f}")
    
    # Spoken language criteria:
    # - Spoken human language has unvoiced phoneme bursts (high_zcr_ratio >= 0.025 or std_zcr >= 0.035)
    # - Spoken speech has inter-word / syllable pauses (pause_ratio >= 0.06)
    # Music lacks unvoiced consonant ZCR bursts (high_zcr_ratio < 0.025 and std_zcr < 0.035) OR has continuous sound (pause_ratio < 0.04)
    
    if high_zcr_ratio < 0.025 and std_zcr < 0.035:
        return False, "MUSIC_OR_TONAL_AUDIO (No speech unvoiced phoneme transitions)"
        
    if pause_ratio < 0.04 and high_zcr_ratio < 0.05:
        return False, "MUSIC_OR_CONTINUOUS_SONG (Continuous musical audio without speech pauses)"
        
    return True, "SPOKEN_HUMAN_SPEECH_PRESENT"

if __name__ == "__main__":
    s_live = generate_speech_sample(replayed=False)
    s_replay = generate_speech_sample(replayed=True)
    s_music = generate_music_sample()
    
    print("--- 1. LIVE SPEECH ---")
    res1, msg1 = is_spoken_human_speech(s_live)
    print(f"Result: {res1} ({msg1})\n")
    
    print("--- 2. REPLAYED SPEECH ---")
    res2, msg2 = is_spoken_human_speech(s_replay)
    print(f"Result: {res2} ({msg2})\n")
    
    print("--- 3. MUSIC SAMPLE ---")
    res3, msg3 = is_spoken_human_speech(s_music)
    print(f"Result: {res3} ({msg3})\n")
