"""
Dhvani Rakshak - Dynamic Real-Time Risk Scoring Engine
Aggregates Acoustic (40%), Prosody (30%), and Speaker Consistency (30%) scores
to calculate Impersonation Confidence Score (0-100) and alert tier.
"""

class RiskScoringEngine:
    def __init__(self, acoustic_weight: float = 0.40, prosody_weight: float = 0.30, speaker_weight: float = 0.30):
        self.acoustic_weight = acoustic_weight
        self.prosody_weight = prosody_weight
        self.speaker_weight = speaker_weight

        # Default thresholds
        self.red_threshold = 85.0
        self.yellow_threshold = 60.0

    def update_config(self, acoustic_w: float = None, prosody_w: float = None, speaker_w: float = None,
                      red_t: float = None, yellow_t: float = None):
        """Update weights and risk alert thresholds dynamically."""
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
        Compute overall impersonation risk score (0 to 100) and threat tier,
        calibrated with Content & Intent Analysis (Helpful AI Allowed vs Harmful Scam AI Blocked).
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

        # Apply contextual risk multiplier
        final_anomaly = min(1.0, raw_ensemble * contextual_multiplier)
        risk_score = round(final_anomaly * 100.0, 1)

        # ----------------------------------------------------
        # Content Intent AI Calibration: Helpful vs Harmful AI
        # ----------------------------------------------------
        intent_type = content_intent.get("intent_type", "NEUTRAL") if content_intent else "NEUTRAL"
        
        if intent_type == "HELPFUL_ASSISTANT":
            # HELPFUL AI (e.g. Appointment reminder, Customer support, Emergency alert) -> ALLOW CALL
            risk_score = min(risk_score, 32.0)
            alert_level = "GREEN"
            recommendation = "ALLOW"
            user_message = "✅ HELPFUL AI ASSISTANT DETECTED: Spoken content is helpful and benign. Call allowed."
        elif intent_type == "HARMFUL_SCAM":
            # HARMFUL SCAM AI (e.g. OTP phishing, Wire transfer, Extortion) -> BLOCK CALL & ALERT
            risk_score = max(risk_score, 94.5)
            alert_level = "RED"
            recommendation = "BLOCK_TRANSACTION_AND_ESCALATE"
            user_message = "🚨 HARMFUL SCAM AI VOICE DETECTED: Phishing/Fraud intent detected! Call blocked and intercepted."
        else:
            # Determine Alert Level standard thresholds
            if risk_score >= self.red_threshold:
                alert_level = "RED"
                recommendation = "BLOCK_TRANSACTION_AND_ESCALATE"
                user_message = "HIGH RISK: AI Voice Clone Detected! Transaction automatically blocked."
            elif risk_score >= self.yellow_threshold:
                alert_level = "YELLOW"
                recommendation = "REQUIRE_SECONDARY_VERIFICATION"
                user_message = "WARNING: Suspicious voice characteristics detected. Secondary verification required."
            else:
                alert_level = "GREEN"
                recommendation = "ALLOW"
                user_message = "AUTHENTIC: Voice identity verified. Proceeding with standard process."

        return {
            "risk_score": risk_score,
            "alert_level": alert_level,
            "recommendation": recommendation,
            "user_message": user_message,
            "content_intent": content_intent,
            "breakdown": {
                "acoustic_contribution": round(ac_score * self.acoustic_weight * 100.0, 1),
                "prosody_contribution": round(pr_score * self.prosody_weight * 100.0, 1),
                "speaker_contribution": round(sp_score * self.speaker_weight * 100.0, 1),
                "contextual_multiplier": contextual_multiplier
            },
            "weights": {
                "acoustic": round(self.acoustic_weight, 2),
                "prosody": round(self.prosody_weight, 2),
                "speaker": round(self.speaker_weight, 2)
            },
            "thresholds": {
                "RED": self.red_threshold,
                "YELLOW": self.yellow_threshold
            }
        }
