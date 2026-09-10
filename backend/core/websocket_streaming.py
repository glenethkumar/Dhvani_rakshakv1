"""
Dhvani Rakshak - WebSocket Real-Time Audio Streaming Gateway
Provides sub-second live streaming audio inspection over WebSockets for VoIP and Speakerphone channels.
"""

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
from core.keyword_scanner import KeywordScanner
from core.scoring_fusion import ScoringFusionEngine
from core.content_intent_analyzer import ContentIntentAnalyzer
from core.privacy_compliance import PrivacyComplianceManager
from core.explainability_engine import ExplainabilityEngine

class WebSocketStreamHandler:
    """
    High-throughput, low-latency WebSocket gateway for real-time audio chunk inspection.
    """

    def __init__(self):
        self.ingestion = AudioIngestionPipeline(target_sample_rate=16000)
        self.acoustic = AcousticAnalyzer(sample_rate=16000)
        self.prosody = ProsodyAnalyzer(sample_rate=16000)
        self.speaker = SpeakerVerifier(embedding_dim=192)
        self.multilingual = MultilingualEngine(default_lang="en-IN")
        self.risk_engine = RiskScoringEngine()
        self.keyword_scanner = KeywordScanner()
        self.fusion_engine = ScoringFusionEngine(wavlm_weight=0.60, gemini_weight=0.25, keyword_weight=0.15)
        self.intent_analyzer = ContentIntentAnalyzer()
        self.privacy = PrivacyComplianceManager()
        self.xai = ExplainabilityEngine()

    async def handle_stream(self, websocket: WebSocket, language: str = "en-IN", target_speaker_id: str = None):
        """
        Main async loop for WebSocket stream connection.
        Receives binary PCM/WAV chunks, runs full inference pipeline, and pushes live JSON risk updates.
        """
        await websocket.accept()
        session_id = f"WS_{uuid.uuid4().hex[:8].upper()}"

        try:
            while True:
                data = await websocket.receive_bytes()
                if not data or len(data) == 0:
                    continue

                start_time = time.time()
                
                # 1. Ingest & preprocess audio frame
                audio, sr = self.ingestion.load_wav_bytes(data)
                
                # 2. VAD Silence Check
                if not self.ingestion.is_speech_active(audio):
                    latency_ms = round((time.time() - start_time) * 1000.0, 2)
                    response_payload = {
                        "session_id": session_id,
                        "latency_ms": latency_ms,
                        "risk_score": 0.0,
                        "alert_level": "WAITING",
                        "recommendation": "WAIT_FOR_SPEECH",
                        "user_message": "🎧 Listening for caller voice... (Waiting for speech)",
                        "is_speech_detected": False,
                        "reasons": ["Caller is currently silent. Waiting for vocal input."]
                    }
                    await websocket.send_json(response_payload)
                    continue

                audio = self.ingestion.preprocess(audio, sr)

                # 3. Acoustic Analysis (WavLM / AASIST)
                ac_res = self.acoustic.detect_tts_artifacts(audio)

                # 4. Prosody Analysis & Dialect Adaptation
                pr_res = self.prosody.analyze_prosody(audio)
                pr_res = self.multilingual.adapt_prosodic_scores(pr_res, language)

                # 5. Speaker Verification
                sp_res = self.speaker.verify_speaker(audio, target_speaker_id)

                # 6. Intent & Keyword Scan
                transcript_sample = ""
                intent_res = self.intent_analyzer.analyze_content_intent(transcript_sample, len(audio)/16000.0)
                keyword_res = self.keyword_scanner.scan_transcript(transcript_sample)

                # 7. Weighted Score Fusion
                wavlm_score = float(ac_res.get("neural_deepfake_probability", 0.10) * 100.0)
                gemini_score = float(intent_res.get("risk_multiplier", 1.0) * 50.0)
                fusion_res = self.fusion_engine.evaluate_call(wavlm_score, gemini_score, keyword_res)

                # 8. Explainability Reasons
                risk_res = {
                    "session_id": session_id,
                    "risk_score": fusion_res["risk_score"],
                    "alert_level": fusion_res["alert_level"],
                    "recommendation": fusion_res["recommendation"],
                    "user_message": fusion_res["user_message"]
                }
                xai_res = self.xai.generate_explanation(ac_res, pr_res, sp_res, risk_res)

                latency_ms = round((time.time() - start_time) * 1000.0, 2)
                self.privacy.enforce_zero_raw_audio_policy(audio)

                payload = {
                    "session_id": session_id,
                    "latency_ms": latency_ms,
                    "risk_score": fusion_res["risk_score"],
                    "alert_level": fusion_res["alert_level"],
                    "recommendation": fusion_res["recommendation"],
                    "user_message": fusion_res["user_message"],
                    "is_speech_detected": True,
                    "reasons": xai_res.get("primary_decision_reasons", []),
                    "tts_signatures": ac_res.get("tts_signatures", {}),
                    "acoustic_anomaly": ac_res.get("acoustic_anomaly_score", 0.0),
                    "prosody_anomaly": pr_res.get("calibrated_prosody_score", 0.0)
                }

                await websocket.send_json(payload)

        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"WebSocket Streaming Exception: {e}")
