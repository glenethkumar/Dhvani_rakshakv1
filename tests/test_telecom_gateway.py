"""
Dhvani Rakshak - Telecom Gateway & PBX/SIP Integration Test Suite
Verifies G.711 telephony audio codecs, STIR/SHAKEN caller verification,
bidirectional audio stream processing, and automated mid-call fraud defense.
"""

import pytest
import numpy as np
from scipy import signal

from backend.telecom.codecs import (
    decode_mulaw_to_pcm,
    decode_alaw_to_pcm,
    encode_pcm_to_mulaw,
    resample_telephony_to_16k,
    apply_telephony_channel_degradation
)
from backend.telecom.stir_shaken import StirShakenVerifier
from backend.telecom.telecom_gateway import TelecomGateway
from backend.main import simulate_inbound_telecom_call, TelecomSimulationRequest
from tests.generate_test_audio import generate_genuine_human_audio, generate_elevenlabs_ai_clone


def test_g711_codecs_and_resampling():
    """Verify G.711 mu-law and A-law encode/decode and 8k->16k resampling accuracy."""
    # 1 second of 440Hz test sine wave at 8000 Hz
    t = np.linspace(0, 1.0, 8000, endpoint=False)
    orig_pcm = (0.8 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)

    # Test mu-law
    mu_bytes = encode_pcm_to_mulaw(orig_pcm)
    assert len(mu_bytes) == 8000, "mu-law output must be exactly 8000 bytes for 1 second"
    dec_pcm = decode_mulaw_to_pcm(mu_bytes)
    assert len(dec_pcm) == 8000, "Decoded PCM must match sample length"
    # G.711 quantization error should be minimal (RMSE < 0.05)
    rmse = np.sqrt(np.mean((orig_pcm - dec_pcm) ** 2))
    assert rmse < 0.05, f"G.711 mu-law quantization error too high: {rmse}"

    # Test A-law decoding
    a_dec = decode_alaw_to_pcm(mu_bytes)
    assert len(a_dec) == 8000

    # Test 8k -> 16k resampling
    resampled_16k = resample_telephony_to_16k(dec_pcm, source_rate=8000, target_rate=16000)
    assert len(resampled_16k) == 16000, "Resampled audio must be 16000 samples for 1 second"


def test_stir_shaken_caller_verification():
    """Verify STIR/SHAKEN attestation level classification and CLI spoofing detection."""
    verifier = StirShakenVerifier()

    # 1. Verified Indian number via legitimate carrier and trusted trunk IP
    res_a = verifier.verify_caller_identity(
        caller_number="+91 98200 12345",
        ingress_trunk_ip="10.200.1.5",
        carrier_declared="Airtel"
    )
    assert res_a["attestation_level"] == "A", "Legitimate direct MNO trunk must receive Attestation A"
    assert not res_a["is_cli_spoofed"], "Legitimate caller should not be flagged as spoofed"
    assert res_a["telecom_risk_modifier"] <= 0.0

    # 2. Suspicious repetitive number via anonymous VoIP gateway
    res_c = verifier.verify_caller_identity(
        caller_number="+91 00000 00000",
        ingress_trunk_ip="185.220.101.5",
        carrier_declared="Generic_VoIP"
    )
    assert res_c["attestation_level"] == "C", "Untrusted international trunk must receive Attestation C"
    assert res_c["is_cli_spoofed"], "Repetitive number on VoIP trunk must be flagged as spoofed CLI"
    assert res_c["telecom_risk_modifier"] > 0.0


def test_automated_mid_call_fraud_deflection():
    """Verify that incoming telephone calls trigger automated mitigation based on risk thresholds."""
    gateway = TelecomGateway()
    
    # 1. Inbound genuine call
    call = gateway.initiate_call(
        caller_number="+91 98200 12345",
        dialed_number="+91 22 6600 0000",
        carrier="Airtel",
        target_speaker_id="VIP_CEO"
    )
    assert call.status == "IN_PROGRESS"

    # Process audio chunk
    gen_audio = generate_genuine_human_audio(3.0)
    deg_gen = apply_telephony_channel_degradation(gen_audio)
    mu_gen = encode_pcm_to_mulaw(signal.resample(deg_gen, 24000))
    res_gen = gateway.process_telecom_audio_chunk(call.call_sid, mu_gen)

    assert res_gen["risk_score"] < 60.0, f"Genuine caller risk score should be low: {res_gen['risk_score']}"
    assert res_gen["mitigation_action"] == "CONTINUE"

    # 2. Inbound AI clone attack with spoofed carrier
    clone_call = gateway.initiate_call(
        caller_number="+91 00000 00000",
        dialed_number="+91 22 6600 0000",
        carrier="Generic_VoIP",
        target_speaker_id="VIP_CEO"
    )
    clone_audio = generate_elevenlabs_ai_clone(3.0)
    deg_clo = apply_telephony_channel_degradation(clone_audio)
    mu_clo = encode_pcm_to_mulaw(signal.resample(deg_clo, 24000))
    res_clo = gateway.process_telecom_audio_chunk(clone_call.call_sid, mu_clo)

    assert res_clo["risk_score"] >= 85.0, f"Spoofed AI clone attack should exceed RED threshold: {res_clo['risk_score']}"
    assert res_clo["mitigation_action"] == "TERMINATED_BY_SIP_BYE"
    assert res_clo["sip_command"]["action"] == "SEND_SIP_BYE"
    assert res_clo["sip_command"]["sip_code"] == 603


def test_telecom_operator_actions():
    """Verify manual operator in-call actions (terminate, transfer, challenge)."""
    gateway = TelecomGateway()
    call = gateway.initiate_call(caller_number="+91 98200 12345", dialed_number="+91 22 6600 0000")

    # Test transfer
    trans_res = gateway.execute_call_action(call.call_sid, "transfer", "Suspicious voice request")
    assert trans_res["status"] == "SUCCESS"
    assert trans_res["action_executed"] == "SIP_REFER_TRANSFER"

    # Test challenge
    chall_res = gateway.execute_call_action(call.call_sid, "challenge")
    assert chall_res["status"] == "SUCCESS"
    assert "challenge_phrase" in chall_res

    # Test terminate
    term_res = gateway.execute_call_action(call.call_sid, "terminate")
    assert term_res["status"] == "SUCCESS"
    assert term_res["action_executed"] == "SIP_BYE_DISCONNECT"
    assert call.status == "TERMINATED_BY_SIP_BYE"


def test_telecom_simulation_endpoint():
    """Verify the /api/v1/telecom/simulate-call endpoint end-to-end."""
    req_gen = TelecomSimulationRequest(scenario="genuine_ceo", carrier="Airtel", caller_number="+91 98200 12345")
    res_gen = simulate_inbound_telecom_call(req_gen)
    assert res_gen["status"] == "PROCESSED"
    assert res_gen["chunk_evaluation"]["risk_score"] < 60.0

    req_clo = TelecomSimulationRequest(scenario="elevenlabs_clone", carrier="Generic_VoIP", caller_number="+91 00000 00000")
    res_clo = simulate_inbound_telecom_call(req_clo)
    assert res_clo["status"] == "PROCESSED"
    assert res_clo["chunk_evaluation"]["risk_score"] >= 85.0
    assert res_clo["chunk_evaluation"]["mitigation_action"] == "TERMINATED_BY_SIP_BYE"
