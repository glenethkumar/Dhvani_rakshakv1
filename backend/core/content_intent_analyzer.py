"""
Dhvani Rakshak - Content & Intent-Aware AI Voice Classifier
Analyzes speech transcripts and intent patterns to differentiate between:
1. HELPFUL BENIGN AI VOICES (Customer Service Assistants, Appointment Reminders, Public Alerts) -> ALLOW CALL
2. HARMFUL MISLEADING SCAM AI VOICES (OTP Phishing, CEO Wire Transfer Demand, Digital Arrest Extortion) -> BLOCK CALL & ALERT
"""

import re
from typing import Dict, List, Any

class ContentIntentAnalyzer:
    def __init__(self):
        # Harmful / Misleading Scam Patterns
        self.harmful_patterns = {
            "OTP_PHISHING": [
                r"share.*otp", r"tell.*me.*otp", r"verification.*code", r"6-digit", r"bank.*password",
                r"cvv", r"pin.*number", r"account.*blocked", r"verify.*debit.*card"
            ],
            "URGENT_WIRE_TRANSFER": [
                r"transfer.*money", r"urgent.*wire", r"send.*lakhs", r"new.*bank.*account",
                r"pay.*immediately", r"ceo.*demand", r"rtgs", r"neft", r"emergency.*funds"
            ],
            "DIGITAL_ARREST_EXTORTION": [
                r"cbi.*officer", r"police.*warrant", r"digital.*arrest", r"customs.*illegal.*parcel",
                r"drugs.*found", r"court.*summons", r"money.*laundering", r"pay.*fine.*now"
            ],
            "ACCOUNT_COMPROMISE_SCAM": [
                r"kyc.*expired", r"update.*pan", r"link.*aadhaar", r"sim.*deactivated",
                r"electricity.*bill.*unpaid", r"power.*cut"
            ]
        }

        # Helpful / Benign AI Assistant Patterns
        self.helpful_patterns = {
            "CUSTOMER_SERVICE_ASSISTANT": [
                r"customer.*support", r"service.*desk", r"flight.*status", r"appointment.*reminder",
                r"table.*reservation", r"delivery.*status", r"feedback.*survey", r"automated.*assistant"
            ],
            "EMERGENCY_PUBLIC_ALERT": [
                r"weather.*advisory", r"disaster.*management", r"government.*alert", r"public.*warning",
                r"evacuation.*notice", r"traffic.*update"
            ],
            "ACCESSIBILITY_VOICE_ASSISTANT": [
                r"screen.*reader", r"reading.*message", r"voice.*assistant", r"smart.*speaker"
            ]
        }

    def analyze_content_intent(self, text_transcript: str = "", audio_duration: float = 3.0) -> Dict[str, Any]:
        """
        Classifies spoken content into HARMFUL_SCAM, HELPFUL_ASSISTANT, or NEUTRAL_SPEECH.
        """
        if not text_transcript or len(text_transcript.strip()) == 0:
            # Standard generic transcript simulation if raw STT model is offline
            text_transcript = "Standard voice call stream evaluation."

        transcript_lower = text_transcript.lower()

        flagged_harmful_category = None
        harmful_matches = []

        # 1. Check for Harmful / Misleading Scam Intent
        for category, regex_list in self.harmful_patterns.items():
            for pattern in regex_list:
                if re.search(pattern, transcript_lower):
                    flagged_harmful_category = category
                    harmful_matches.append(pattern)

        # 2. Check for Helpful / Benign AI Assistant Intent
        flagged_helpful_category = None
        helpful_matches = []
        for category, regex_list in self.helpful_patterns.items():
            for pattern in regex_list:
                if re.search(pattern, transcript_lower):
                    flagged_helpful_category = category
                    helpful_matches.append(pattern)

        # 3. Determine Overall Purpose Intent Decision
        if flagged_harmful_category:
            intent_type = "HARMFUL_SCAM"
            decision = "BLOCK_AND_ALERT"
            user_explanation = f"🚨 HARMFUL SCAM DETECTED: Spoken content matches fraud pattern ({flagged_harmful_category}). Call blocked immediately!"
            risk_multiplier = 1.6
        elif flagged_helpful_category:
            intent_type = "HELPFUL_ASSISTANT"
            decision = "ALLOW_CALL"
            user_explanation = f"✅ HELPFUL AI ASSISTANT: Spoken content verified as benign service assistant ({flagged_helpful_category}). Call allowed."
            risk_multiplier = 0.3
        else:
            intent_type = "NEUTRAL"
            decision = "EVALUATE_VOICE_ONLY"
            user_explanation = "Neutral speech content. Evaluating bio-physical voice authenticity."
            risk_multiplier = 1.0

        return {
            "intent_type": intent_type,
            "decision": decision,
            "user_explanation": user_explanation,
            "flagged_harmful_category": flagged_harmful_category,
            "flagged_helpful_category": flagged_helpful_category,
            "transcript_analyzed": text_transcript,
            "risk_multiplier": risk_multiplier
        }
