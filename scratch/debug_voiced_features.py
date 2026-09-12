import sys
import numpy as np
import scipy.fft as fft
import scipy.signal as signal

sys.path.append("backend")
from test_all_7_scenarios import (
    generate_direct_live_speech,
    generate_replayed_human_voice,
    generate_random_music_clip,
    generate_ai_tts_source1_elevenlabs,
    generate_ai_tts_source2_wavenet,
    generate_ai_tts_source3_replayed_ai,
    generate_voice_converted_ai_clip
)

scenarios = [
    ("1. Live Human Speech", generate_direct_live_speech()),
    ("2. Replayed Human Speech", generate_replayed_human_voice()),
    ("3. Random Music", generate_random_music_clip()),
    ("4. ElevenLabs Clean AI", generate_ai_tts_source1_elevenlabs()),
    ("5. WaveNet Clean AI", generate_ai_tts_source2_wavenet()),
    ("6. Replayed AI Voice", generate_ai_tts_source3_replayed_ai()),
    ("7. Voice-Converted AI Clip", generate_voice_converted_ai_clip())
]

def analyze_voiced_flatness(audio, sample_rate=16000):
    stft_mat = signal.stft(audio, fs=sample_rate, nperseg=256, noverlap=128)[2]
    frame_energies = np.mean(np.abs(stft_mat)**2, axis=0)
    voiced_mask = frame_energies > (0.05 * (np.max(frame_energies) + 1e-8))
    
    if np.sum(voiced_mask) > 5:
        phases = np.unwrap(np.angle(stft_mat[:, voiced_mask]), axis=1)
        voiced_mags = np.abs(stft_mat[:, voiced_mask])
        geom = np.exp(np.mean(np.log(voiced_mags + 1e-10), axis=0))
        arith = np.mean(voiced_mags, axis=0) + 1e-10
        flatness_voiced = float(np.mean(geom / arith))
    else:
        phases = np.unwrap(np.angle(stft_mat), axis=1)
        flatness_voiced = 0.10
        
    phase_diff = np.diff(phases, axis=1)
    phase_var = float(np.mean(np.var(phase_diff, axis=1)))
    return flatness_voiced, phase_var

print("\n--- VOICED FRAME FEATURE ANALYSIS ---\n")
for name, audio in scenarios:
    flat_v, phase_v = analyze_voiced_flatness(audio)
    print(f"{name:<35} | Voiced Flatness: {flat_v:.4f} | Phase Var: {phase_v:.4f}")
print()
