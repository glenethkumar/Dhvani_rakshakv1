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
from backend.models.deep_fake_detector import DeepFakeDetector

def create_human_voice(pitch=140.0, duration=3.0):
    sr = 16000
    t = np.linspace(0, duration, int(sr * duration))
    f0 = pitch + 25.0 * np.sin(2 * np.pi * 1.8 * t) + 8.0 * np.cos(2 * np.pi * 4.5 * t)
    phase = 2 * np.pi * np.cumsum(f0) / sr
    audio = np.sin(phase) + 0.4 * np.sin(2 * phase) + 0.2 * np.sin(3 * phase)
    # Add unvoiced consonant bursts (s, sh, t)
    for pos in [0.5, 1.2, 2.0, 2.6]:
        idx = int(pos * sr)
        audio[idx:idx+800] += np.random.normal(0, 0.3, 800)
    audio += np.random.normal(0, 0.02, len(audio))
    return audio / np.max(np.abs(audio)) * 0.85

def create_ai_clone_flat(pitch=145.0, duration=3.0):
    sr = 16000
    t = np.linspace(0, duration, int(sr * duration))
    f0 = pitch * np.ones(len(t))
    phase = 2 * np.pi * np.cumsum(f0) / sr
    audio = np.sin(phase) + 0.45 * np.sin(2 * phase) + 0.25 * np.sin(3 * phase)
    # Filter high freq low-pass 6.5kHz
    fft_sig = np.fft.rfft(audio)
    freqs = np.fft.rfftfreq(len(audio), 1/sr)
    fft_sig[freqs > 6500] *= 0.01
    audio = np.fft.irfft(fft_sig)
    return audio / np.max(np.abs(audio)) * 0.85

def create_voice_conversion(duration=3.0):
    # Natural human rhythm/pitch but smooth phase / vocoder timbre
    sr = 16000
    t = np.linspace(0, duration, int(sr * duration))
    f0 = 160.0 + 30.0 * np.sin(2 * np.pi * 2.0 * t)
    phase = 2 * np.pi * np.cumsum(f0) / sr
    audio = np.sin(phase) + 0.5 * np.sin(2 * phase)
    # Phase is perfectly smooth, high-freq energy boosted
    return audio / np.max(np.abs(audio)) * 0.85

def test_diverse_inputs():
    acoustic = AcousticAnalyzer()
    prosody = ProsodyAnalyzer()
    speaker = SpeakerVerifier()
    fusion = ScoringFusionEngine()
    risk_engine = RiskScoringEngine()

    test_cases = {
        "Human Male Low Pitch": create_human_voice(110.0),
        "Human Female High Pitch": create_human_voice(220.0),
        "AI Clone Flat Pitch": create_ai_clone_flat(145.0),
        "Voice Conversion (RVC)": create_voice_conversion(),
    }

    for name, audio in test_cases.items():
        print(f"\n================ {name} ================")
        ac_res = acoustic.detect_tts_artifacts(audio)
        pr_res = prosody.analyze_prosody(audio)
        sp_res = speaker.verify_speaker(audio)
        risk_res = risk_engine.calculate_risk(ac_res, pr_res, sp_res)

        deepfake_prob = ac_res.get("neural_deepfake_probability", 0.0)
        std_f0 = pr_res.get("std_f0_hz", 0.0)
        jitter = pr_res.get("jitter_percent", 0.0)
        phase_var = ac_res.get("spectral_features", {}).get("phase_smoothness_variance", 3.0)

        # main.py logic check
        is_human_speech_production = (std_f0 >= 4.0 or pr_res.get("f0_range_hz", 0.0) >= 10.0) and (0.12 <= jitter <= 20.0)
        is_tts_artifact = (std_f0 < 3.5 or pr_res.get("f0_range_hz", 0.0) < 9.0 or jitter < 0.12)
        is_voice_conversion_artifact = (phase_var < 1.4 or deepfake_prob >= 0.35 or ac_res.get("acoustic_anomaly_score", 0.0) >= 0.25)
        is_synthetic_voice = is_tts_artifact or is_voice_conversion_artifact

        wavlm_score = float(deepfake_prob * 100.0)
        if is_human_speech_production and not is_synthetic_voice:
            wavlm_score = min(wavlm_score, 18.5)

        fusion_res = fusion.evaluate_call(wavlm_score)

        print(f"DeepfakeProb: {deepfake_prob:.4f}")
        print(f"std_f0: {std_f0:.1f}, jitter: {jitter:.2f}, phase_var: {phase_var:.2f}")
        print(f"is_human_speech_production: {is_human_speech_production}")
        print(f"is_tts_artifact: {is_tts_artifact}, is_vc_artifact: {is_voice_conversion_artifact}")
        print(f"WavLM Score (Post-override): {wavlm_score:.1f}")
        print(f"Fusion RiskScore: {fusion_res['risk_score']}, Alert: {fusion_res['alert_level']}, Label: {fusion_res['voice_label']}")
        print(f"Risk Engine Score: {risk_res['risk_score']}, Alert: {risk_res['alert_level']}")

if __name__ == "__main__":
    test_diverse_inputs()
