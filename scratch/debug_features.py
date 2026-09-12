import numpy as np
import sys

sys.path.append("backend")
from core.acoustic_analyzer import AcousticAnalyzer
from core.prosody_analyzer import ProsodyAnalyzer
from core.audio_ingestion import AudioIngestionPipeline
from models.deep_fake_detector import DeepFakeDetector

from test_all_6_scenarios import (
    generate_direct_live_speech,
    generate_replayed_human_voice,
    generate_random_music_clip,
    generate_ai_tts_source1_elevenlabs,
    generate_ai_tts_source2_wavenet,
    generate_ai_tts_source3_replayed_ai
)

ac = AcousticAnalyzer()
pr = ProsodyAnalyzer()
ingest = AudioIngestionPipeline()
detector = DeepFakeDetector()

scenarios = [
    ("1. Live Human Speech", generate_direct_live_speech()),
    ("2. Replayed Human Speech", generate_replayed_human_voice()),
    ("3. Random Music", generate_random_music_clip()),
    ("4. ElevenLabs Clean AI", generate_ai_tts_source1_elevenlabs()),
    ("5. WaveNet Clean AI", generate_ai_tts_source2_wavenet()),
    ("6. Replayed AI Voice", generate_ai_tts_source3_replayed_ai()),
]

print("\n--- DETAILED DIAGNOSTIC FEATURE ANALYSIS ---\n")

for name, audio in scenarios:
    speech_ok, speech_msg = ingest.is_spoken_human_speech(audio)
    
    ac_res = ac.detect_tts_artifacts(audio)
    pr_res = pr.analyze_prosody(audio)
    detector_res = detector.detect_deepfake(audio)
    
    spec_feats = ac_res.get("spectral_features", {})
    phase_var = spec_feats.get("phase_smoothness_variance", 3.0)
    high_freq = spec_feats.get("high_freq_energy_ratio", 0.0)
    
    std_f0 = pr_res.get("std_f0_hz", 0.0)
    f0_rng = pr_res.get("f0_range_hz", 0.0)
    jitter = pr_res.get("jitter_percent", 0.0)
    
    mfcc_std = ac_res.get("mfcc_variance", 0.0)
    neural_prob = ac_res.get("neural_deepfake_probability", 0.0)
    
    print(f"[{name}]")
    print(f"  Speech Check:    Speech={speech_ok}, Msg='{speech_msg}'")
    print(f"  Phase Var:       {phase_var:.4f}")
    print(f"  High Freq Energy:{high_freq:.4f}")
    print(f"  MFCC Std:        {mfcc_std:.4f}")
    print(f"  Pitch std_f0:    {std_f0:.2f} Hz | f0_range: {f0_rng:.2f} Hz")
    print(f"  Jitter:          {jitter:.4f}%")
    print(f"  Neural Deepfake: {neural_prob:.4f}")
    print()
