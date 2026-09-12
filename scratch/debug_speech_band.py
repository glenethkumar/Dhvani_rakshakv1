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

def analyze_speech_band_flatness(audio, sample_rate=16000):
    stft_mat = signal.stft(audio, fs=sample_rate, nperseg=256, noverlap=128)[2]
    # Speech band STFT bins (200 Hz to 4000 Hz)
    bin_low = int(200.0 / (sample_rate / 256.0))
    bin_high = int(4000.0 / (sample_rate / 256.0))
    stft_speech_band = stft_mat[bin_low:bin_high, :]
    
    frame_energies = np.mean(np.abs(stft_speech_band)**2, axis=0)
    voiced_mask = frame_energies > (0.05 * (np.max(frame_energies) + 1e-8))
    
    if np.sum(voiced_mask) > 5:
        speech_mags = np.abs(stft_speech_band[:, voiced_mask])
        geom = np.exp(np.mean(np.log(speech_mags + 1e-10), axis=0))
        arith = np.mean(speech_mags, axis=0) + 1e-10
        flatness_speech_band = float(np.mean(geom / arith))
        
        phases = np.unwrap(np.angle(stft_mat[:, voiced_mask]), axis=1)
        phase_diff = np.diff(phases, axis=1)
        phase_var = float(np.mean(np.var(phase_diff, axis=1)))
    else:
        flatness_speech_band = 0.10
        phase_var = 3.0
        
    return flatness_speech_band, phase_var

print("\n--- SPEECH BAND (200Hz - 4000Hz) FEATURE ANALYSIS ---\n")
for name, audio in scenarios:
    flat_sb, phase_v = analyze_speech_band_flatness(audio)
    print(f"{name:<35} | Speech Band Flatness: {flat_sb:.4f} | Phase Var: {phase_v:.4f}")
print()
