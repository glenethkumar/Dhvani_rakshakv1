import sys
import os
import numpy as np

sys.path.append(os.path.abspath("."))
from backend.core.audio_ingestion import AudioIngestionPipeline
from backend.core.acoustic_analyzer import AcousticAnalyzer
from backend.core.prosody_analyzer import ProsodyAnalyzer
from backend.core.speaker_verifier import SpeakerVerifier
from backend.core.scoring_fusion import ScoringFusionEngine
from backend.core.risk_scorer import RiskScoringEngine
from tests.generate_test_audio import generate_genuine_human_audio, generate_elevenlabs_ai_clone, generate_spliced_audio_attack

def test_all():
    ingestion = AudioIngestionPipeline(target_sample_rate=16000)
    acoustic = AcousticAnalyzer(sample_rate=16000)
    prosody = ProsodyAnalyzer(sample_rate=16000)
    speaker = SpeakerVerifier(embedding_dim=192)
    fusion = ScoringFusionEngine()
    risk_engine = RiskScoringEngine()

    samples = {
        "Human Audio": generate_genuine_human_audio(3.0),
        "ElevenLabs AI Clone": generate_elevenlabs_ai_clone(3.0),
        "Spliced Attack": generate_spliced_audio_attack(3.0),
        "Sine Wave 440Hz": np.sin(2 * np.pi * 440 * np.linspace(0, 3.0, 48000)),
        "White Noise": np.random.normal(0, 0.1, 48000),
    }

    for name, audio in samples.items():
        print(f"\n================ {name} ================")
        is_speech, speech_reason = ingestion.is_spoken_human_speech(audio, 16000)
        print(f"Speech Check: is_speech={is_speech}, reason={speech_reason}")
        if not is_speech:
            continue
        
        ac_res = acoustic.detect_tts_artifacts(audio)
        pr_res = prosody.analyze_prosody(audio)
        sp_res = speaker.verify_speaker(audio)
        
        # main.py logic
        std_f0 = pr_res.get("std_f0_hz", 0.0)
        f0_range = pr_res.get("f0_range_hz", 0.0)
        jitter = pr_res.get("jitter_percent", 0.0)
        phase_var = ac_res.get("spectral_features", {}).get("phase_smoothness_variance", 3.0)
        deepfake_prob = ac_res.get("neural_deepfake_probability", 0.0)

        is_human_speech_production = (std_f0 >= 4.0 or f0_range >= 10.0) and (0.12 <= jitter <= 20.0)
        is_tts_artifact = (std_f0 < 3.5 or f0_range < 9.0 or jitter < 0.12)
        is_voice_conversion_artifact = (phase_var < 1.4 or deepfake_prob >= 0.35 or ac_res.get("acoustic_anomaly_score", 0.0) >= 0.25)
        is_synthetic_voice = is_tts_artifact or is_voice_conversion_artifact

        wavlm_score = float(ac_res.get("neural_deepfake_probability", 0.10) * 100.0)
        if is_human_speech_production and not is_synthetic_voice:
            wavlm_score = min(wavlm_score, 18.5)

        fusion_res = fusion.evaluate_call(wavlm_score)
        risk_res = risk_engine.calculate_risk(ac_res, pr_res, sp_res)

        print(f"ac_res: deepfake_prob={deepfake_prob}, acoustic_anomaly={ac_res.get('acoustic_anomaly_score')}")
        print(f"pr_res: std_f0={std_f0}, f0_range={f0_range}, jitter={jitter}")
        print(f"phase_var={phase_var}")
        print(f"is_human_speech_production={is_human_speech_production}")
        print(f"is_tts_artifact={is_tts_artifact}, is_vc_artifact={is_voice_conversion_artifact}, is_synthetic_voice={is_synthetic_voice}")
        print(f"WavLM Score (Post-override): {wavlm_score}")
        print(f"Fusion Result Risk Score: {fusion_res['risk_score']}, Label: {fusion_res['voice_label']}")
        print(f"Risk Scorer Result: {risk_res['risk_score']}, Alert: {risk_res['alert_level']}")

if __name__ == "__main__":
    test_all()
