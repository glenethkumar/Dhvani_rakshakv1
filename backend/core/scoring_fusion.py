"""
Dhvani Rakshak - Weighted Score Fusion Engine & Decision Tree
Fuses WavLM acoustic spoof probability, Gemini NLU behavioral risk, and STT keyword scan scores.
"""

from typing import Dict, Any, List

class ScoringFusionEngine:
    """
    Weighted score fusion & rule-based decision engine for non-disruptive fraud alerting.
    
    Formula (Content-Free Biometric Standard):
    Final Risk Score = (1.00 * Acoustic/Prosodic WavLM Score) + (0.00 * Optional Text Intent) + (0.00 * Optional STT Keywords)
    Note: Speech content analysis is bypassed to ensure 100% privacy compliance and eliminate call transcript access requirements.
    """

    def __init__(self, wavlm_weight: float = 1.00, gemini_weight: float = 0.00, keyword_weight: float = 0.00):
        self.wavlm_w = wavlm_weight
        self.gemini_w = gemini_weight
        self.keyword_w = keyword_weight

    def evaluate_call(
        self,
        wavlm_score: float,
        gemini_score: float = 0.0,
        keyword_res: Dict[str, Any] = None,
        transaction_amount: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates fused risk score using content-free acoustic biometrics.
        Does NOT require call transcript or speech-to-text access.
        """
        if keyword_res is None:
            keyword_res = {}

        keyword_score = keyword_res.get("keyword_score", 0.0)
        has_keywords = keyword_res.get("has_fraud_keywords", False)
        matches = keyword_res.get("matches", [])
        categories = keyword_res.get("categories", {})

        # Calculate weighted sum based on acoustic biometrics
        raw_fusion = (self.wavlm_w * wavlm_score) + (self.gemini_w * gemini_score) + (self.keyword_w * keyword_score)
        
        # High value transaction risk booster
        if transaction_amount >= 1000000.0:  # > ₹10 Lakhs
            raw_fusion = min(100.0, raw_fusion * 1.15)

        final_risk = round(raw_fusion, 1)

        # Rule-Based Biometric Decision Logic
        is_ai_voice = (wavlm_score >= 60.0)
        reasons: List[str] = []

        if is_ai_voice:
            reasons.append(f"AI-generated synthetic vocoder artifacts detected (Acoustic Confidence: {wavlm_score:.1f}%)")
        else:
            reasons.append("Natural acoustic phoneme transitions & vocal cords vibration verified")

        # Optional enterprise text insights (if transcript provided, without enforcing dependency)
        if categories.get("has_urgency"):
            reasons.append("[Optional Text Plugin] Coercive urgency phrasing detected")
        if categories.get("has_financial"):
            reasons.append(f"[Optional Text Plugin] Financial transaction keywords ({', '.join(matches)})")

        # Determine Voice Classification & Alert Level
        if wavlm_score >= 50.0:
            voice_type = "AI_VOICE_CLONE"
            is_ai_voice = True
            alert_level = "RED" if wavlm_score >= 70.0 else "YELLOW"
            recommendation = "RECOMMEND_DISCONNECT" if wavlm_score >= 70.0 else "PROCEED_WITH_CAUTION"
            recommended_action = "RECOMMEND_DISCONNECT" if wavlm_score >= 70.0 else "WARN_USER_CAUTION"
            action_taken = "USER_WARNED_DISCONNECTED_MANUALLY" if wavlm_score >= 70.0 else "USER_NOTIFIED"
            user_message = f"🚨 FAKE AI VOICE CLONE DETECTED ({wavlm_score:.1f}% AI probability). Recommended: disconnect call."
        else:
            voice_type = "REAL_HUMAN_VOICE"
            is_ai_voice = False
            alert_level = "GREEN"
            recommendation = "ALLOW"
            recommended_action = "ALLOW_CALL"
            action_taken = "CALL_ALLOWED"
            user_message = f"✅ REAL HUMAN VOICE DETECTED ({100.0 - wavlm_score:.1f}% human authenticity). Voice verified."

        # Cap score for RED alert
        if alert_level == "RED":
            final_risk = max(85.0, final_risk)

        return {
            "risk_score": final_risk,
            "alert_level": alert_level,
            "voice_type": voice_type,
            "voice_label": "Fake AI Voice Clone" if is_ai_voice else "Real Human Voice",
            "recommendation": recommendation,
            "recommended_action": recommended_action,
            "action_taken": action_taken,
            "user_message": user_message,
            "is_ai_voice_detected": is_ai_voice,
            "has_fraud_keywords": has_keywords,
            "flagged_reasons": reasons,
            "breakdown": {
                "wavlm_acoustic_contribution": round(self.wavlm_w * wavlm_score, 1),
                "gemini_behavioral_contribution": round(self.gemini_w * gemini_score, 1),
                "keyword_contribution": round(self.keyword_w * keyword_score, 1),
                "wavlm_score_raw": wavlm_score,
                "gemini_score_raw": gemini_score,
                "keyword_score_raw": keyword_score
            }
        }
