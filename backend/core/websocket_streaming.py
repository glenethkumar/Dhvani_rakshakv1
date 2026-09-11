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
    Uses temporal rolling audio buffer (up to 2.0s) and EMA risk score smoothing.
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

    async def handle_stream(self, websocket: WebSocket, language: str = "en-IN", target_speaker_id: str = None):
        """
        Main async loop for WebSocket stream connection.
        Receives binary PCM/WAV chunks, runs full inference pipeline on rolling buffer, and pushes live JSON risk updates.
        """
        await websocket.accept()
        session_id = f"WS_{uuid.uuid4().hex[:8].upper()}"
        self.session_buffers[session_id] = np.array([], dtype=np.float32)
        self.session_ema_scores[session_id] = 20.0  # Safe human baseline initialization

        try:
            while True:
                data = await websocket.receive_bytes()
                if not data or len(data) == 0:
                    continue

                start_time = time.time()
                
                # 1. Ingest & preprocess incoming chunk
                chunk_audio, sr = self.ingestion.load_wav_bytes(data)
                
                # 2. VAD Silence Check on current chunk
                if not self.ingestion.is_speech_active(chunk_audio):
                    latency_ms = round((time.time() - start_time) * 1000.0, 2)
                    self.session_ema_scores[session_id] = 0.0
                    self.session_buffers[session_id] = np.array([], dtype=np.float32)
                    response_payload = {
                        "session_id": session_id,
                        "latency_ms": latency_ms,
                        "risk_score": 0.0,
                        "authenticity_score": 100.0,
                        "risk_level": "Low",
                        "alert_level": "WAITING",
                        "recommendation": "WAIT_FOR_SPEECH",
                        "user_message": "🎧 Listening for caller voice... (Waiting for speech)",
                        "is_speech_detected": False,
                        "reasons": ["Caller is currently silent. Waiting for vocal input."]
                    }
                    await websocket.send_json(response_payload)
                    continue

                chunk_audio = self.ingestion.preprocess(chunk_audio, sr)

                # 3. Rolling audio accumulation (keep up to 2.0s = 32,000 samples at 16kHz)
                buf = self.session_buffers.get(session_id, np.array([], dtype=np.float32))
                buf = np.concatenate([buf, chunk_audio])
                max_samples = int(16000 * 2.0)
                if len(buf) > max_samples:
                    buf = buf[-max_samples:]
                self.session_buffers[session_id] = buf

                # 4. Feature extraction over rolling buffer
                ac_res = self.acoustic.detect_tts_artifacts(buf)
                pr_res = self.prosody.analyze_prosody(buf)
                pr_res = self.multilingual.adapt_prosodic_scores(pr_res, language)
                sp_res = self.speaker.verify_speaker(buf, target_speaker_id)

                # 5. Score Fusion & EMA Risk Smoothing
                wavlm_score = float(ac_res.get("neural_deepfake_probability", 0.10) * 100.0)
                fusion_res = self.fusion_engine.evaluate_call(wavlm_score)
                raw_risk = fusion_res["risk_score"]

                prev_risk = self.session_ema_scores.get(session_id, raw_risk)
                smoothed_risk = round(0.35 * raw_risk + 0.65 * prev_risk, 1)
                self.session_ema_scores[session_id] = smoothed_risk
                smoothed_auth = round(max(0.0, 100.0 - smoothed_risk), 1)

                if smoothed_risk >= 70.0:
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

                # 6. Explainability & Privacy Compliance
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
                    "reasons": xai_res.get("primary_decision_reasons", []),
                    "tts_signatures": ac_res.get("tts_signatures", {}),
                    "acoustic_anomaly": ac_res.get("acoustic_anomaly_score", 0.0),
                    "prosody_anomaly": pr_res.get("calibrated_prosody_score", 0.0)
                }

                await websocket.send_json(payload)

        except WebSocketDisconnect:
            self.session_buffers.pop(session_id, None)
            self.session_ema_scores.pop(session_id, None)
        except Exception as e:
            print(f"WebSocket Streaming Exception: {e}")
