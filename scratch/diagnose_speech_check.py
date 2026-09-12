import sys
import os
import numpy as np

sys.path.append(os.path.abspath("."))
from backend.core.audio_ingestion import AudioIngestionPipeline
from tests.generate_test_audio import generate_genuine_human_audio, generate_elevenlabs_ai_clone

ingestion = AudioIngestionPipeline()

for name, audio in [("Human", generate_genuine_human_audio()), ("AI Clone", generate_elevenlabs_ai_clone())]:
    max_amp = float(np.max(np.abs(audio)))
    rms_energy = float(np.sqrt(np.mean(audio ** 2)))
    
    sample_rate = 16000
    frame_len = int(sample_rate * 0.025)
    hop_len = int(sample_rate * 0.010)
    num_frames = (len(audio) - frame_len) // hop_len + 1
    frames = np.array([audio[i * hop_len : i * hop_len + frame_len] for i in range(num_frames)])

    zcr = np.mean(np.abs(np.diff(np.sign(frames), axis=1)) > 0, axis=1)
    std_zcr = float(np.std(zcr))
    high_zcr_ratio = float(np.mean(zcr > 0.12))

    frame_energies = np.mean(frames ** 2, axis=1)
    max_frame_energy = np.max(frame_energies) + 1e-10
    pause_ratio = float(np.mean(frame_energies < (0.12 * max_frame_energy)))

    print(f"=== {name} ===")
    print(f"max_amp={max_amp:.4f}, rms_energy={rms_energy:.4f}")
    print(f"high_zcr_ratio={high_zcr_ratio:.4f}, std_zcr={std_zcr:.4f}, pause_ratio={pause_ratio:.4f}")
    res, msg = ingestion.is_spoken_human_speech(audio, 16000)
    print(f"is_spoken_human_speech -> {res}, {msg}\n")
