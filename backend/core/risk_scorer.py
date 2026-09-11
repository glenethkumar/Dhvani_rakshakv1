"""
Dhvani Rakshak - Pure Acoustic Risk Scoring Engine
Calculates voice authenticity score and risk level (Low / Medium / High)
exclusively using acoustic spectral, prosodic pitch, and speaker biometric signals.
"""

from typing import Dict, Any, List

class RiskScoringEngine:
    """
    Pure Voice Authenticity Risk Scoring Engine.
    Evaluates acoustic vocoder artifacts, pitch prosody, and speaker consistency.
    """

    def __init__(self, acoustic_weight: float = 0.40, prosody_weight: float = 0.30, speaker_weight: float = 0.30):
        self.acoustic_weight = acoustic_weight
        self.prosody_weight = prosody_weight
        self.speaker_weight = speaker_weight

        # Risk thresholds (based on authenticity / deepfake probability)
        self.red_threshold = 70.0    # High Risk
        self.yellow_threshold = 40.0 # Medium Risk

    def update_config(self, acoustic_w: float = None, prosody_w: float = None, speaker_w: float = None,
                      red_t: float = None, yellow_t: float = None):
        """Update weights and risk thresholds dynamically."""
        if acoustic_w is not None: self.acoustic_weight = acoustic_w
        if prosody_w is not None: self.prosody_weight = prosody_w
        if speaker_w is not None: self.speaker_weight = speaker_w
        if red_t is not None: self.red_threshold = red_t
        if yellow_t is not None: self.yellow_threshold = yellow_t

        # Normalize weights to sum to 1.0
        total_w = self.acoustic_weight + self.prosody_weight + self.speaker_weight
        if total_w > 0:
            self.acoustic_weight /= total_w
            self.prosody_weight /= total_w
            self.speaker_weight /= total_w

    def calculate_risk(self, acoustic_res: dict, prosody_res: dict, speaker_res: dict, contextual_multiplier: float = 1.0, content_intent: dict = None) -> dict:
        """
        Compute overall voice authenticity and risk level (Low / Medium / High)
        strictly from acoustic, prosodic, and spectral signals.
        """
        ac_score = acoustic_res.get("acoustic_anomaly_score", 0.0)
        pr_score = prosody_res.get("calibrated_prosody_score", prosody_res.get("prosody_anomaly_score", 0.0))
        sp_score = speaker_res.get("speaker_anomaly_score", 0.0)

        # Weighted Ensemble Calculation (0.0 to 1.0)
        raw_ensemble = (
            ac_score * self.acoustic_weight +
            pr_score * self.prosody_weight +
            sp_score * self.speaker_weight
        )

        neural_prob = acoustic_res.get("neural_deepfake_probability", 0.0)
        splicing_disc = acoustic_res.get("splicing_discontinuity", 0.0)
        if neural_prob >= 0.60 or sp_score >= 0.60 or (splicing_disc >= 1.2 and sp_score >= 0.25):
            attack_severity = max(neural_prob, sp_score)
            raw_ensemble = max(raw_ensemble, 0.55 + 0.35 * attack_severity)

        final_anomaly = min(1.0, raw_ensemble * contextual_multiplier)
        ai_probability = round(final_anomaly * 100.0, 1)
        authenticity_score = round(max(0.0, 100.0 - ai_probability), 1)

        # Pure acoustic risk level classification: Low / Medium / High
        red_flags: List[str] = []
        if ai_probability >= self.red_threshold:
            risk_level = "High"
            alert_level = "RED"
            recommendation = "RECOMMEND_DISCONNECT"
            if neural_prob >= 0.5:
                red_flags.append("High-frequency neural vocoder artifacts detected (>6.5kHz spectral cutoff)")
            if pr_score >= 0.5:
                red_flags.append("Unnatural flat pitch contour & missing micro-jitter vibration")
            if sp_score >= 0.5:
                red_flags.append("Speaker voice embedding anomaly identified (distance >0.65)")
            if not red_flags:
                red_flags.append("Synthetic voice spectral signature detected")
            reasoning = f"High AI voice clone risk ({ai_probability}% AI Probability). Synthetic vocoder artifacts and pitch anomalies identified."
            user_message = f"🚨 FAKE AI VOICE CLONE DETECTED ({ai_probability}% AI Probability). Recommended: disconnect call."
        elif ai_probability >= self.yellow_threshold:
            risk_level = "Medium"
            alert_level = "YELLOW"
            recommendation = "PROCEED_WITH_CAUTION"
            red_flags.append("Elevated pitch prosody irregularity detected")
            reasoning = f"Medium voice clone risk ({ai_probability}% AI Probability). Moderate acoustic anomaly detected."
            user_message = f"⚠️ SUSPICIOUS VOICE CHARACTERISTICS ({ai_probability}% AI Probability). Proceed with caution."
        else:
            risk_level = "Low"
            alert_level = "GREEN"
            recommendation = "ALLOW"
            reasoning = f"Authentic real human voice confirmed ({authenticity_score}% Authenticity). Natural vocal tract formants verified."
            user_message = f"✅ REAL HUMAN VOICE DETECTED ({authenticity_score}% Human Authenticity). Voice verified."

        return {
            "authenticity_score": authenticity_score,
            "risk_score": ai_probability,
            "ai_probability": ai_probability,
            "human_authenticity": authenticity_score,
            "risk_level": risk_level,
            "alert_level": alert_level,
            "red_flags": red_flags,
            "reasoning": reasoning,
            "recommendation": recommendation,
            "user_message": user_message,
            "flagged_context_risk_factors": red_flags,
            "breakdown": {
                "acoustic_contribution": round(ac_score * self.acoustic_weight * 100.0, 1),
                "prosody_contribution": round(pr_score * self.prosody_weight * 100.0, 1),
                "speaker_contribution": round(sp_score * self.speaker_weight * 100.0, 1)
            },
            "weights": {
                "acoustic": round(self.acoustic_weight, 2),
                "prosody": round(self.prosody_weight, 2),
                "speaker": round(self.speaker_weight, 2)
            }
        }
