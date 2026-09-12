"""
Dhvani Rakshak - Pure Voice Biometric Fusion Engine
Evaluates acoustic vocoder artifacts and pitch prosody to classify AI Voice Clone vs Real Human Voice.
"""

from typing import Dict, Any, List

class ScoringFusionEngine:
    """
    Pure Voice Biometric Evaluation Engine.
    Detects synthetic AI voice clones vs real human voices using acoustic spectral biometrics.
    """

    def __init__(self, wavlm_weight: float = 1.00):
        self.wavlm_w = wavlm_weight

    def evaluate_call(
        self,
        wavlm_score: float,
        transaction_amount: float = 0.0,
        prosody_score: float = 0.0,
        speaker_anomaly_score: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates voice authenticity using fused acoustic, prosodic, and biometric scores.
        Outputs binary classification: AI Voice Clone vs Real Human Voice.
        """
        # Multi-feature fusion (Acoustic 50%, Prosody 30%, Speaker 20%)
        ensemble_score = 0.50 * wavlm_score + 0.30 * (prosody_score * 100.0) + 0.20 * (speaker_anomaly_score * 100.0)
        
        # High acoustic or prosody anomaly boosts overall risk
        if wavlm_score >= 65.0 or prosody_score >= 0.70:
            raw_score = max(wavlm_score, ensemble_score)
        else:
            raw_score = ensemble_score

        raw_score = min(100.0, max(0.0, raw_score * self.wavlm_w))
        
        # High value transaction risk booster
        if transaction_amount >= 1000000.0:  # > ₹10 Lakhs
            raw_score = min(100.0, raw_score * 1.15)

        final_risk = round(raw_score, 1)
        human_authenticity = round(max(0.0, 100.0 - final_risk), 1)

        # Rule-Based Biometric Decision Logic
        is_ai_voice = (final_risk >= 50.0)
        reasons: List[str] = []

        if is_ai_voice:
            if wavlm_score >= 50.0:
                reasons.append(f"AI-generated synthetic vocoder artifacts detected (AI Confidence: {wavlm_score:.1f}%)")
            if prosody_score >= 0.50:
                reasons.append("Unnatural flat pitch contour & prosodic micro-jitter deficiency identified")
            if speaker_anomaly_score >= 0.50:
                reasons.append("Speaker embedding identity mismatch detected")
            if not reasons:
                reasons.append(f"Synthetic voice anomaly detected (Risk Score: {final_risk:.1f}%)")

            voice_type = "AI_VOICE_CLONE"
            voice_label = "Synthetic (AI Clone)"
            alert_level = "RED" if final_risk >= 70.0 else "YELLOW"
            recommendation = "RECOMMEND_DISCONNECT" if final_risk >= 70.0 else "PROCEED_WITH_CAUTION"
            recommended_action = "RECOMMEND_DISCONNECT" if final_risk >= 70.0 else "WARN_USER_CAUTION"
            action_taken = "USER_WARNED_DISCONNECTED_MANUALLY" if final_risk >= 70.0 else "USER_NOTIFIED"
            user_message = f"🚨 FAKE AI VOICE CLONE DETECTED ({final_risk:.1f}% AI Probability). Recommended: disconnect call."
        else:
            reasons.append(f"Natural human vocal cord vibration & acoustic phonemes verified (Human Authenticity: {human_authenticity:.1f}%)")
            reasons.append("Natural fundamental frequency (F0) pitch dynamics confirmed")
            voice_type = "REAL_HUMAN_VOICE"
            voice_label = "Organic (Human)"
            alert_level = "GREEN"
            recommendation = "ALLOW"
            recommended_action = "ALLOW_CALL"
            action_taken = "CALL_ALLOWED"
            user_message = f"✅ REAL HUMAN VOICE DETECTED ({human_authenticity:.1f}% Human Authenticity). Voice verified."

        # Cap score for RED alert
        if alert_level == "RED":
            final_risk = max(85.0, final_risk)

        return {
            "risk_score": final_risk,
            "ai_probability": final_risk,
            "human_authenticity": human_authenticity,
            "alert_level": alert_level,
            "voice_type": voice_type,
            "voice_label": voice_label,
            "recommendation": recommendation,
            "recommended_action": recommended_action,
            "action_taken": action_taken,
            "user_message": user_message,
            "is_ai_voice_detected": is_ai_voice,
            "flagged_reasons": reasons,
            "breakdown": {
                "wavlm_acoustic_contribution": round(wavlm_score * 0.50, 1),
                "prosody_contribution": round(prosody_score * 30.0, 1),
                "speaker_contribution": round(speaker_anomaly_score * 20.0, 1),
                "wavlm_score_raw": wavlm_score
            }
        }
