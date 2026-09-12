import numpy as np
import scipy.signal as signal

def compute_phase_var(audio, sr=16000):
    stft_mat = signal.stft(audio, fs=sr, nperseg=256, noverlap=128)[2]
    # Phase difference across time per frequency bin
    phase_diff = np.diff(np.unwrap(np.angle(stft_mat), axis=1), axis=1)
    phase_var = float(np.mean(np.var(phase_diff, axis=1)))
    return phase_var

# Synthetic vocoder speech
t = np.linspace(0, 3.5, int(3.5 * 16000))
syllables = np.clip(np.sin(2 * np.pi * 2.0 * t), 0.0, 1.0) ** 2
synth = (np.sin(2 * np.pi * 135.0 * t) + 0.5 * np.sin(2 * np.pi * 270.0 * t)) * syllables

# Room reverberation (speaker playback)
reverb = np.copy(synth)
reverb[int(0.03 * 16000):] += 0.4 * synth[:-int(0.03 * 16000)]
reverb += 0.03 * np.random.randn(len(t))

print("Synthetic Vocoder Phase Var:", compute_phase_var(synth))
print("Replayed Speaker Echo Phase Var:", compute_phase_var(reverb))
