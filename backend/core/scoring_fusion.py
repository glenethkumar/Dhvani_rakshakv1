"""
Dhvani Rakshak - Weighted Score Fusion Engine & Decision Tree
Fuses WavLM acoustic spoof probability, Gemini NLU behavioral risk, and STT keyword scan scores.
"""

from typing import Dict, Any, List

class ScoringFusionEngine:
    """
    Weighted score fusion & rule-based decision engine for non-disruptive fraud alerting.
    
    Formula:
    Final Risk Score = (0.60 * WavLM Score) + (0.25 * Gemini Score) + (0.15 * Keyword Score)
    """

    def __init__(self, wavlm_weight: float = 0.60, gemini_weight: float = 0.25, keyword_weight: float = 0.15):
        self.wavlm_w = wavlm_weight
        self.gemini_w = gemini_weight
        self.keyword_w = keyword_weight

    def evaluate_call(
        self,
        wavlm_score: float,
        gemini_score: float,
        keyword_res: Dict[str, Any],
        transaction_amount: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates fused risk score and determines color-coded alert level and non-disruptive recommendation.
        """
        keyword_score = keyword_res.get("keyword_score", 0.0)
        has_keywords = keyword_res.get("has_fraud_keywords", False)
        matches = keyword_res.get("matches", [])
        categories = keyword_res.get("categories", {})

        # Calculate weighted sum
        raw_fusion = (self.wavlm_w * wavlm_score) + (self.gemini_w * gemini_score) + (self.keyword_w * keyword_score)
        
        # High value transaction risk booster
        if transaction_amount >= 1000000.0:  # > ₹10 Lakhs
            raw_fusion = min(100.0, raw_fusion * 1.15)

        final_risk = round(raw_fusion, 1)

        # Rule-Based Decision Logic
        is_ai_voice = (wavlm_score >= 60.0)
        reasons: List[str] = []

        if is_ai_voice:
            reasons.append(f"AI-generated synthetic voice signature detected (Acoustic Confidence: {wavlm_score:.1f}%)")

        if categories.get("has_urgency"):
            reasons.append("Coercive urgency phrasing detected ('urgent', 'immediately')")
        if categories.get("has_secrecy"):
            reasons.append("Secrecy constraint phrasing detected ('don't tell anyone')")
        if categories.get("has_financial"):
            reasons.append(f"Financial transaction keywords detected ({', '.join(matches)})")

        # Determine Alert Level & Recommendation
        if is_ai_voice and has_keywords:
            alert_level = "RED"
            recommendation = "HANG_UP_AND_VERIFY_CALLBACK"
            user_message = "🚨 HIGH RISK: AI voice + fraud keywords detected. Recommended: hang up and verify via callback."
        elif is_ai_voice and not has_keywords:
            alert_level = "YELLOW"
            recommendation = "PROCEED_WITH_CAUTION"
            user_message = "⚠️ WARNING: AI voice detected, but content appears benign."
        elif not is_ai_voice and has_keywords:
            alert_level = "YELLOW"
            recommendation = "REQUIRE_SECONDARY_OTP"
            user_message = "⚠️ WARNING: Possible social engineering attempt by human caller."
        else:
            alert_level = "GREEN"
            recommendation = "ALLOW"
            user_message = "✅ AUTHENTIC REAL HUMAN VOICE: Voice identity and speech content verified."

        # Cap score for RED alert
        if alert_level == "RED":
            final_risk = max(85.0, final_risk)

        return {
            "risk_score": final_risk,
            "alert_level": alert_level,
            "recommendation": recommendation,
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
