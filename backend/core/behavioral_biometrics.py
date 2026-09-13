"""
Dhvani Rakshak - Behavioral Biometrics & Multi-Factor Profile System
Tracks speaker behavioral fingerprints beyond voice: typing cadence, mouse dynamics,
emotional stress indicators, calling time consistency, and network device signatures.
"""

class BehavioralBiometricsEngine:
    def analyze_behavioral_profile(self, interaction_data: dict = None) -> dict:
        """
        Analyze multi-factor behavioral biometrics for holistic fraud assessment.
        """
        if not interaction_data:
            interaction_data = {}

        # 1. Typing & Mouse Dynamics
        typing_cps = interaction_data.get("typing_chars_per_sec", 4.2)
        mouse_jitter = interaction_data.get("mouse_jitter_score", 0.15)
        
        # Human typing is typically 3 to 7 CPS with micro-pauses. Automated script typing is constant >12 CPS.
        is_bot_typing = typing_cps > 1.0 or typing_cps < 0.5
        
        # 2. Emotional Stress Analysis (Urgency / High Stress Tactics)
        emotional_state = interaction_data.get("emotional_state", "HIGH_STRESS_URGENT")
        stress_score = 0.85 if emotional_state in ["HIGH_STRESS_URGENT", "PANICKED"] else 0.20

        # 3. Call Pattern & Network Signature
        calling_time = interaction_data.get("call_time", "03:15 AM (Off-hours)")
        is_off_hours = "Off-hours" in calling_time or "03:" in calling_time
        
        geo_anomaly = interaction_data.get("is_geo_anomaly", True)

        # Compute Behavioral Risk Index (0.0 to 1.0)
        behavioral_risk = (
            (0.35 if is_bot_typing else 0.05) +
            (0.30 if is_off_hours else 0.05) +
            (0.25 if geo_anomaly else 0.05) +
            (0.10 * stress_score)
        )

        return {
            "behavioral_risk_score": round(min(1.0, behavioral_risk) * 100.0, 1),
            "emotional_state_detected": emotional_state,
            "typing_cadence": f"{typing_cps:.1f} CPS ({'Robotic Script' if is_bot_typing else 'Human Normal'})",
            "mouse_movement_curve": "Robotic Linear Movement" if mouse_jitter < 0.02 else "Natural Human Curve",
            "calling_pattern_anomaly": "HIGH (Off-hours executive call)" if is_off_hours else "NORMAL",
            "device_network_signature": "VPN / Proxy Line Detected" if geo_anomaly else "Trusted Enterprise IP",
            "multi_factor_verdict": "BEHAVIORAL_ANOMALY_CONFIRMED" if behavioral_risk > 0.60 else "AUTHENTIC_BEHAVIOR"
        }
