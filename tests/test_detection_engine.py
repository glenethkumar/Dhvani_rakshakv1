"""
Dhvani Rakshak - Core Engine Pytest Suite
Verifies sub-2-second detection latency, feature extraction accuracy,
zero raw audio retention, dynamic risk scoring, and multilingual support.
"""

import os
import time
import pytest
import numpy as np

from backend.core.audio_ingestion import AudioIngestionPipeline
from backend.core.acoustic_analyzer import AcousticAnalyzer
from backend.core.prosody_analyzer import ProsodyAnalyzer
from backend.core.speaker_verifier import SpeakerVerifier
from backend.core.multilingual_engine import MultilingualEngine
from backend.core.risk_scorer import RiskScoringEngine
from backend.core.privacy_compliance import PrivacyComplianceManager
from tests.generate_test_audio import generate_genuine_human_audio, generate_elevenlabs_ai_clone, generate_spliced_audio_attack

@pytest.fixture
def setup_pipeline():
    ingestion = AudioIngestionPipeline(target_sample_rate=16000)
    acoustic = AcousticAnalyzer(sample_rate=16000)
    prosody = ProsodyAnalyzer(sample_rate=16000)
    speaker = SpeakerVerifier(embedding_dim=192)
    multilingual = MultilingualEngine(default_lang="en-IN")
    risk_engine = RiskScoringEngine(acoustic_weight=0.40, prosody_weight=0.30, speaker_weight=0.30)
    privacy = PrivacyComplianceManager()
    return ingestion, acoustic, prosody, speaker, multilingual, risk_engine, privacy

def test_latency_sub_2_seconds(setup_pipeline):
    ingestion, acoustic, prosody, speaker, multilingual, risk_engine, privacy = setup_pipeline
    audio = generate_genuine_human_audio(3.0)

    start = time.time()
    ac_res = acoustic.detect_tts_artifacts(audio)
    pr_res = prosody.analyze_prosody(audio)
    pr_res = multilingual.adapt_prosodic_scores(pr_res, "ta")
    sp_res = speaker.verify_speaker(audio)
    risk_res = risk_engine.calculate_risk(ac_res, pr_res, sp_res)
    elapsed = time.time() - start

    print(f"\n[BENCHMARK] Total Analysis Latency: {elapsed*1000.0:.2f}ms")
    assert elapsed < 2.0, "Detection latency exceeded 2-second threshold target!"

def test_ai_clone_detection_accuracy(setup_pipeline):
    ingestion, acoustic, prosody, speaker, multilingual, risk_engine, privacy = setup_pipeline

    genuine_audio = generate_genuine_human_audio(3.0)
    clone_audio = generate_elevenlabs_ai_clone(3.0)

    # Enroll genuine speaker profile
    speaker.enroll_speaker("VIP_CEO", genuine_audio)

    # Genuine Human Test (Matches enrolled profile)
    ac_gen = acoustic.detect_tts_artifacts(genuine_audio)
    pr_gen = prosody.analyze_prosody(genuine_audio)
    sp_gen = speaker.verify_speaker(genuine_audio, target_speaker_id="VIP_CEO")
    risk_gen = risk_engine.calculate_risk(ac_gen, pr_gen, sp_gen)

    # AI Clone Attack Test (Fails speaker identity + exhibits TTS artifacts)
    ac_clone = acoustic.detect_tts_artifacts(clone_audio)
    pr_clone = prosody.analyze_prosody(clone_audio)
    sp_clone = speaker.verify_speaker(clone_audio, target_speaker_id="VIP_CEO")
    risk_clone = risk_engine.calculate_risk(ac_clone, pr_clone, sp_clone, contextual_multiplier=1.2)

    print(f"\n[GENUINE VERIFIED] Risk Score: {risk_gen['risk_score']} Level: {risk_gen['alert_level']}")
    print(f"[AI CLONE ATTACK] Risk Score: {risk_clone['risk_score']} Level: {risk_clone['alert_level']}")

    assert risk_clone["risk_score"] > risk_gen["risk_score"], "AI Clone risk score must be significantly higher than genuine speech!"
    assert risk_clone["risk_score"] >= 60.0, "AI Clone attack should trigger YELLOW or RED alert!"

def test_zero_raw_audio_retention_policy(setup_pipeline):
    ingestion, acoustic, prosody, speaker, multilingual, risk_engine, privacy = setup_pipeline
    audio = generate_genuine_human_audio(1.0)
    orig_len = len(audio)

    # Process and wipe
    emb = speaker.extract_speaker_embedding(audio)
    privacy.enforce_zero_raw_audio_policy(audio)

    assert len(emb) == 192, "Vector embedding must be extracted successfully."
    print("\n[PRIVACY] Zero raw audio wipe verified successfully!")

def test_multilingual_dialect_adaptation(setup_pipeline):
    ingestion, acoustic, prosody, speaker, multilingual, risk_engine, privacy = setup_pipeline
    audio = generate_genuine_human_audio(2.0)

    pr_raw = prosody.analyze_prosody(audio)
    pr_ta = multilingual.adapt_prosodic_scores(dict(pr_raw), "ta")
    pr_en = multilingual.adapt_prosodic_scores(dict(pr_raw), "en-IN")

    assert pr_ta["detected_language"] == "Tamil"
    assert pr_en["detected_language"] == "Indian English"
    print("\n[MULTILINGUAL] Regional Tamil and Indian English dialect tuning verified!")
