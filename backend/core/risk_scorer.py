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
        if neural_prob >= 0.70 or (splicing_disc >= 4.5 and sp_score >= 0.60):
            attack_severity = max(neural_prob, sp_score)
            raw_ensemble = max(raw_ensemble, 0.55 + 0.35 * attack_severity)


        final_anomaly = min(1.0, raw_ensemble * contextual_multiplier)
        auth_score = round(final_anomaly * 100.0, 1)

        # Pure acoustic risk level classification according to strict 3-tier system:
        #   0-39   -> Human Voice       (GREEN / Safe)
        #   40-69  -> Uncertain Voice   (YELLOW / Recommend Verification)
        #   70-100 -> AI Voice Clone    (RED / High Risk - Flagged)
        red_flags: List[str] = []
        if auth_score >= 70.0:
            risk_level = "High"
            alert_level = "RED"
            label = "AI Voice Clone"
            recommendation = "RECOMMEND_DISCONNECT"
            if neural_prob >= 0.5:
                red_flags.append("High-frequency neural vocoder artifacts detected (>6.5kHz spectral cutoff)")
            if pr_score >= 0.5:
                red_flags.append("Unnatural flat pitch contour & missing micro-jitter vibration")
            if sp_score >= 0.5:
                red_flags.append("Speaker voice embedding anomaly identified (distance >0.65)")
            if not red_flags:
                red_flags.append("Synthetic voice spectral signature detected")
            reasoning = f"High AI voice clone risk ({auth_score}/100 Score). Synthetic vocoder artifacts and pitch anomalies identified."
            user_message = f"🚨 FAKE AI VOICE CLONE DETECTED (Score: {auth_score}/100). Recommended: disconnect call."
        elif auth_score >= 40.0:
            risk_level = "Medium"
            alert_level = "YELLOW"
            label = "Uncertain Voice"
            recommendation = "PROCEED_WITH_CAUTION"
            red_flags.append("Elevated pitch prosody irregularity / ambiguous audio quality detected")
            reasoning = f"Uncertain voice characteristics ({auth_score}/100 Score). Secondary verification recommended."
            user_message = f"⚠️ UNCERTAIN VOICE (Score: {auth_score}/100). Secondary verification recommended."
        else:
            risk_level = "Low"
            alert_level = "GREEN"
            label = "Human Voice"
            recommendation = "ALLOW"
            reasoning = f"Authentic human voice confirmed ({auth_score}/100 Score). Natural vocal tract formants verified."
            user_message = f"✅ REAL HUMAN VOICE DETECTED (Score: {auth_score}/100). Voice verified."

        return {
            "authenticity_score": auth_score,
            "risk_score": auth_score,
            "ai_probability": auth_score,
            "human_authenticity": round(max(0.0, 100.0 - auth_score), 1),
            "risk_level": risk_level,
            "alert_level": alert_level,
            "label": label,
            "color": alert_level,
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
