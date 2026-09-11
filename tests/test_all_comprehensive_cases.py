"""
Dhvani Rakshak - Comprehensive End-to-End Test Suite
Tests all core biometric modules, AI vs Human classification, TRAI DLT verifier,
DPDP Act 2023 zero audio policy, G.711 codecs, mid-call defense, and all REST endpoints.
"""

import time
import pytest
import numpy as np
from fastapi.testclient import TestClient

from backend.main import app, fusion_engine
from backend.core.audio_ingestion import AudioIngestionPipeline
from backend.core.acoustic_analyzer import AcousticAnalyzer
from backend.core.prosody_analyzer import ProsodyAnalyzer
from backend.core.speaker_verifier import SpeakerVerifier
from backend.core.multilingual_engine import MultilingualEngine
from backend.core.privacy_compliance import PrivacyComplianceManager
from backend.telecom.codecs import encode_pcm_to_mulaw, decode_mulaw_to_pcm, resample_telephony_to_16k
from backend.telecom.stir_shaken import StirShakenVerifier
from backend.telecom.telecom_gateway import TelecomGateway
from tests.generate_test_audio import generate_genuine_human_audio, generate_elevenlabs_ai_clone

client = TestClient(app)

# ---------------------------------------------------------------------------
# 1. AI Voice Clone vs Real Human Voice Binary Classification Tests
# ---------------------------------------------------------------------------

def test_binary_ai_vs_human_classification():
    """Verify that ScoringFusionEngine accurately classifies AI Voice Clone vs Real Human Voice."""
    # Test High AI Probability (85%)
    res_ai = fusion_engine.evaluate_call(wavlm_score=85.0)
    assert res_ai["voice_type"] == "AI_VOICE_CLONE", "High acoustic score must be classified as AI_VOICE_CLONE"
    assert res_ai["is_ai_voice_detected"] is True
    assert res_ai["alert_level"] == "RED"
    assert "FAKE AI VOICE CLONE DETECTED" in res_ai["user_message"]

    # Test Low AI Probability (15% - Genuine Human)
    res_human = fusion_engine.evaluate_call(wavlm_score=15.0)
    assert res_human["voice_type"] == "REAL_HUMAN_VOICE", "Low acoustic score must be classified as REAL_HUMAN_VOICE"
    assert res_human["is_ai_voice_detected"] is False
    assert res_human["alert_level"] == "GREEN"
    assert "REAL HUMAN VOICE DETECTED" in res_human["user_message"]


# ---------------------------------------------------------------------------
# 2. Latency Sub-2s Benchmark
# ---------------------------------------------------------------------------

def test_analysis_latency_benchmark():
    """Verify analysis pipeline latency stays strictly below 2.0s target."""
    acoustic = AcousticAnalyzer(sample_rate=16000)
    prosody = ProsodyAnalyzer(sample_rate=16000)
    speaker = SpeakerVerifier(embedding_dim=192)

    audio = generate_genuine_human_audio(3.0)
    start = time.time()
    ac_res = acoustic.detect_tts_artifacts(audio)
    pr_res = prosody.analyze_prosody(audio)
    sp_res = speaker.verify_speaker(audio)
    res = fusion_engine.evaluate_call(ac_res["neural_deepfake_probability"] * 100.0)
    elapsed = time.time() - start

    assert elapsed < 2.0, f"Analysis latency ({elapsed:.2f}s) exceeded 2.0s target!"


# ---------------------------------------------------------------------------
# 3. Privacy Compliance & Zero Raw Audio Retention (DPDP Act 2023)
# ---------------------------------------------------------------------------

def test_zero_raw_audio_retention_and_anonymization():
    """Verify raw audio arrays are zeroed in RAM memory and caller PII is masked."""
    privacy = PrivacyComplianceManager()
    audio = generate_genuine_human_audio(1.0)
    
    # 1. Enforce zero raw audio retention
    privacy.enforce_zero_raw_audio_policy(audio)
    assert np.all(audio == 0), "Volatile audio buffer must be completely zeroed out in RAM"

    # 2. Verify audit record masking and SHA-256 hash
    audit = privacy.create_audit_record("SESS_TEST", {"caller_id": "+91 98200 12345"}, {"risk_score": 15.0, "alert_level": "GREEN"})
    assert audit["masked_caller_id"] == "+91****345", "Caller phone number must be anonymized"
    assert len(audit["integrity_hash"]) == 64, "Audit record must contain a valid 64-character SHA-256 hash"
    assert audit["raw_audio_retained"] is False


# ---------------------------------------------------------------------------
# 4. Telephony G.711 Codecs & TRAI DLT Verification
# ---------------------------------------------------------------------------

def test_g711_codecs_and_trai_dlt_attestation():
    """Verify G.711 telephony audio encoding/decoding and TRAI DLT header attestation."""
    # G.711 encode & decode
    pcm_in = np.sin(np.linspace(0, 100, 8000, dtype=np.float32))
    mulaw = encode_pcm_to_mulaw(pcm_in)
    pcm_out = decode_mulaw_to_pcm(mulaw)
    assert len(mulaw) == 8000
    assert len(pcm_out) == 8000

    # Resampling 8k -> 16k
    resampled = resample_telephony_to_16k(pcm_out, 8000, 16000)
    assert len(resampled) == 16000

    # TRAI DLT Attestation Test
    verifier = StirShakenVerifier()
    res_trusted = verifier.verify_caller_identity("+91 98200 12345", "10.200.1.5", "Airtel")
    assert res_trusted["attestation_level"] == "A"
    assert res_trusted["is_cli_spoofed"] is False

    res_spoofed = verifier.verify_caller_identity("+91 00000 00000", "185.220.101.5", "Generic_VoIP")
    assert res_spoofed["attestation_level"] == "C"
    assert res_spoofed["is_cli_spoofed"] is True


# ---------------------------------------------------------------------------
# 5. Mid-Call Automated Defense & Telecom Operator Actions
# ---------------------------------------------------------------------------

def test_telecom_gateway_mid_call_defense():
    """Verify mid-call defense execution for AI clone attacks and operator actions."""
    gateway = TelecomGateway()
    call = gateway.initiate_call(caller_number="+91 98200 12345", dialed_number="+91 22 6600 0000")

    # Operator actions
    transfer_res = gateway.execute_call_action(call.call_sid, "transfer")
    assert transfer_res["status"] == "SUCCESS"
    assert transfer_res["action_executed"] == "SIP_REFER_TRANSFER"

    term_res = gateway.execute_call_action(call.call_sid, "terminate")
    assert term_res["status"] == "SUCCESS"
    assert term_res["action_executed"] == "SIP_BYE_DISCONNECT"


# ---------------------------------------------------------------------------
# 6. All FastAPI REST API Endpoints Test Suite
# ---------------------------------------------------------------------------

def test_all_fastapi_rest_endpoints():
    """Verify 100% of REST API endpoints respond cleanly with 200 OK status."""
    # GET /
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ONLINE"

    # GET /api/v1/health
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "HEALTHY"

    # GET /api/v1/analytics
    r = client.get("/api/v1/analytics")
    assert r.status_code == 200

    # GET /api/v1/real-calls
    r = client.get("/api/v1/real-calls")
    assert r.status_code == 200

    # GET /api/v1/ml-models
    r = client.get("/api/v1/ml-models")
    assert r.status_code == 200
    assert r.json()["status"] == "OPERATIONAL"

    # GET /api/v1/audit-logs
    r = client.get("/api/v1/audit-logs")
    assert r.status_code == 200

    # GET /api/v1/darkweb-threats
    r = client.get("/api/v1/darkweb-threats")
    assert r.status_code == 200

    # GET /api/v1/telecom/trunk-status
    r = client.get("/api/v1/telecom/trunk-status")
    assert r.status_code == 200

    # GET /api/v1/telecom/active-calls
    r = client.get("/api/v1/telecom/active-calls")
    assert r.status_code == 200

    # POST /api/v1/telecom/simulate-call
    r = client.post("/api/v1/telecom/simulate-call", json={"scenario": "elevenlabs_clone", "carrier": "Generic_VoIP"})
    assert r.status_code == 200
    assert r.json()["status"] == "PROCESSED"

    # POST /api/v1/config
    r = client.post("/api/v1/config", json={"default_language": "en-IN"})
    assert r.status_code == 200

    # POST /api/v1/explain
    r = client.post("/api/v1/explain", data={"case_type": "elevenlabs"})
    assert r.status_code == 200

    # POST /api/v1/gov-protect
    r = client.post("/api/v1/gov-protect", data={"caller_id": "+91 98200 12345", "risk_score": "75.0"})
    assert r.status_code == 200

    # POST /api/v1/blockchain-issue
    r = client.post("/api/v1/blockchain-issue", data={"speaker_id": "SPK_001", "speaker_name": "Rajesh Sharma"})
    assert r.status_code == 200

    # POST /api/v1/behavioral-analyze
    r = client.post("/api/v1/behavioral-analyze", data={"typing_cps": "4.2", "mouse_jitter": "0.15", "emotional_state": "HIGH_STRESS"})
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# 7. Indic Languages Support Test
# ---------------------------------------------------------------------------

def test_indic_languages_support():
    """Verify Multilingual Engine supports all 8 Indic languages + Indian English."""
    engine = MultilingualEngine()
    supported = engine.SUPPORTED_LANGUAGES
    assert len(supported) >= 9
    for code in ["hi", "ta", "te", "kn", "ml", "mr", "bn", "gu", "en-IN"]:
        assert code in supported
        adapted = engine.adapt_prosodic_scores({"std_f0_hz": 12.0}, code)
        assert "detected_language" in adapted
