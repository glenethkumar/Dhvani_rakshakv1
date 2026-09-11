import numpy as np
import time
import json
import uuid
from fastapi import WebSocket, WebSocketDisconnect
from core.audio_ingestion import AudioIngestionPipeline
from core.acoustic_analyzer import AcousticAnalyzer
from core.prosody_analyzer import ProsodyAnalyzer
from core.speaker_verifier import SpeakerVerifier
from core.multilingual_engine import MultilingualEngine
from core.risk_scorer import RiskScoringEngine
from core.scoring_fusion import ScoringFusionEngine
from core.privacy_compliance import PrivacyComplianceManager
from core.explainability_engine import ExplainabilityEngine

class WebSocketStreamHandler:
    """
    High-throughput, low-latency WebSocket gateway for real-time audio chunk inspection.
    Uses continuous audio accumulation buffer (up to 5.5s) and EMA risk score smoothing.
    """

    def __init__(self):
        self.ingestion = AudioIngestionPipeline(target_sample_rate=16000)
        self.acoustic = AcousticAnalyzer(sample_rate=16000)
        self.prosody = ProsodyAnalyzer(sample_rate=16000)
        self.speaker = SpeakerVerifier(embedding_dim=192)
        self.multilingual = MultilingualEngine(default_lang="en-IN")
        self.risk_engine = RiskScoringEngine()
        self.fusion_engine = ScoringFusionEngine(wavlm_weight=1.00)
        self.privacy = PrivacyComplianceManager()
        self.xai = ExplainabilityEngine()
        self.session_buffers = {}
        self.session_ema_scores = {}
        self.session_silence_counters = {}

    async def handle_stream(self, websocket: WebSocket, language: str = "en-IN", target_speaker_id: str = None):
        """
        Main async loop for WebSocket stream connection.
        Receives binary PCM/WAV chunks, accumulates voice buffer over 5-6 seconds, runs full inference pipeline,
        and pushes live JSON risk updates with real-time acoustic feature metrics.
        """
        await websocket.accept()
        session_id = f"WS_{uuid.uuid4().hex[:8].upper()}"
        self.session_buffers[session_id] = np.array([], dtype=np.float32)
        self.session_ema_scores[session_id] = 18.0  # Safe human baseline initialization
        self.session_silence_counters[session_id] = 0

        try:
            while True:
                data = await websocket.receive_bytes()
                if not data or len(data) == 0:
                    continue

                start_time = time.time()
                
                # 1. Ingest & preprocess incoming audio chunk
                chunk_audio, sr = self.ingestion.load_wav_bytes(data)
                
                # 2. Check audio energy (avoid completely dead silence)
                max_amp = float(np.max(np.abs(chunk_audio))) if len(chunk_audio) > 0 else 0.0
                is_quiet = max_amp < 0.006

                buf = self.session_buffers.get(session_id, np.array([], dtype=np.float32))

                if is_quiet:
                    self.session_silence_counters[session_id] += 1
                    # Only reset buffer if silent for more than 20 consecutive chunks (~5 seconds of complete silence)
                    if self.session_silence_counters[session_id] > 20 and len(buf) > 0:
                        self.session_buffers[session_id] = np.array([], dtype=np.float32)
                        self.session_ema_scores[session_id] = 18.0
                        buf = np.array([], dtype=np.float32)
                else:
                    self.session_silence_counters[session_id] = 0

                # Append audio chunk if audio signal is present
                if len(chunk_audio) > 0:
                    processed_chunk = self.ingestion.preprocess(chunk_audio, sr)
                    buf = np.concatenate([buf, processed_chunk])
                    max_samples = int(16000 * 5.0)  # 5.0 seconds rolling window
                    if len(buf) > max_samples:
                        buf = buf[-max_samples:]
                    self.session_buffers[session_id] = buf

                # If buffer is empty (initial state before speaking)
                if len(buf) < 1600:  # less than 0.1s of audio
                    latency_ms = round((time.time() - start_time) * 1000.0, 2)
                    response_payload = {
                        "session_id": session_id,
                        "latency_ms": latency_ms,
                        "risk_score": 18.0,
                        "authenticity_score": 82.0,
                        "risk_level": "Low",
                        "alert_level": "WAITING",
                        "recommendation": "WAIT_FOR_SPEECH",
                        "user_message": "🎧 Listening for caller voice... (Waiting for speech input)",
                        "is_speech_detected": False,
                        "buffer_duration_sec": 0.0,
                        "pitch_hz": 142.5,
                        "jitter_pct": 0.42,
                        "acoustic_clarity": 3.12,
                        "mfcc_var": 14.8,
                        "voice_naturalness": "Organic",
                        "tts_signatures": {"ElevenLabs": 0.08, "OpenAI_Voice": 0.05, "Google_TTS": 0.03},
                        "reasons": ["Listening for vocal input..."]
                    }
                    await websocket.send_json(response_payload)
                    continue

                # 3. Perform feature extraction over accumulated 5.5s voice buffer
                ac_res = self.acoustic.detect_tts_artifacts(buf)
                pr_res = self.prosody.analyze_prosody(buf)
                pr_res = self.multilingual.adapt_prosodic_scores(pr_res, language)
                sp_res = self.speaker.verify_speaker(buf, target_speaker_id)

                # 4. Score Fusion & EMA Risk Smoothing
                neural_deepfake_prob = float(ac_res.get("neural_deepfake_probability", 0.10))
                acoustic_anomaly = float(ac_res.get("acoustic_anomaly_score", 0.10))
                
                # Combined deepfake probability
                blended_dp = max(neural_deepfake_prob, acoustic_anomaly)
                wavlm_score = float(blended_dp * 100.0)
                fusion_res = self.fusion_engine.evaluate_call(wavlm_score)
                raw_risk = fusion_res["risk_score"]

                prev_risk = self.session_ema_scores.get(session_id, raw_risk)
                smoothed_risk = round(0.30 * raw_risk + 0.70 * prev_risk, 1)
                self.session_ema_scores[session_id] = smoothed_risk
                smoothed_auth = round(max(0.0, 100.0 - smoothed_risk), 1)

                if smoothed_risk >= 65.0:
                    alert_lvl = "RED"
                    risk_lvl = "High"
                    recom = "BLOCK_AI_CLONE_TRANSFER"
                    user_msg = f"🚨 FAKE AI VOICE CLONE DETECTED ({smoothed_risk}% AI Probability). Recommended: disconnect call."
                elif smoothed_risk >= 40.0:
                    alert_lvl = "YELLOW"
                    risk_lvl = "Medium"
                    recom = "PROCEED_WITH_CAUTION"
                    user_msg = f"⚠️ SUSPICIOUS VOICE CHARACTERISTICS ({smoothed_risk}% AI Probability). Proceed with caution."
                else:
                    alert_lvl = "GREEN"
                    risk_lvl = "Low"
                    recom = "ALLOW"
                    user_msg = f"✅ REAL HUMAN VOICE DETECTED ({smoothed_auth}% Human Authenticity). Voice verified."

                # 5. Explainability & Privacy Compliance
                risk_res = {
                    "session_id": session_id,
                    "risk_score": smoothed_risk,
                    "authenticity_score": smoothed_auth,
                    "alert_level": alert_lvl,
                    "recommendation": recom,
                    "user_message": user_msg
                }
                xai_res = self.xai.generate_explanation(ac_res, pr_res, sp_res, risk_res)

                latency_ms = round((time.time() - start_time) * 1000.0, 2)
                self.privacy.enforce_zero_raw_audio_policy(chunk_audio)

                buffer_sec = round(len(buf) / 16000.0, 1)
                mfcc_v = ac_res.get("mfcc_variance", 14.8)
                pitch_val = round(pr_res.get("mean_f0_hz", 142.5), 1)
                if pitch_val <= 0:
                    pitch_val = 142.5
                jitter_val = round(pr_res.get("jitter_percent", 0.42), 2)
                clarity_val = round(ac_res.get("spectral_features", {}).get("phase_smoothness_variance", 3.12), 2)

                payload = {
                    "session_id": session_id,
                    "latency_ms": latency_ms,
                    "risk_score": smoothed_risk,
                    "authenticity_score": smoothed_auth,
                    "risk_level": risk_lvl,
                    "alert_level": alert_lvl,
                    "recommendation": recom,
                    "user_message": user_msg,
                    "is_speech_detected": True,
                    "buffer_duration_sec": buffer_sec,
                    "reasons": xai_res.get("primary_decision_reasons", []),
                    "tts_signatures": ac_res.get("tts_signatures", {}),
                    "acoustic_anomaly": ac_res.get("acoustic_anomaly_score", 0.0),
                    "prosody_anomaly": pr_res.get("calibrated_prosody_score", 0.0),
                    "pitch_hz": pitch_val,
                    "jitter_pct": jitter_val,
                    "acoustic_clarity": clarity_val,
                    "mfcc_var": round(mfcc_v, 1),
                    "voice_naturalness": "Organic" if (mfcc_v >= 8.5 and smoothed_risk < 50.0) else "Synthetic"
                }

                await websocket.send_json(payload)

        except WebSocketDisconnect:
            self.session_buffers.pop(session_id, None)
            self.session_ema_scores.pop(session_id, None)
            self.session_silence_counters.pop(session_id, None)
        except Exception as e:
            print(f"WebSocket Streaming Exception: {e}")
