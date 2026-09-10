"""
Dhvani Rakshak - Keyword Fraud Scanner
Scans transcribed text from speech-to-text (Whisper/STT) for high-risk social engineering,
OTP phishing, urgency coercion, and financial extortion keywords.
"""

import re
from typing import List, Dict, Any

class KeywordScanner:
    """
    High-speed regex and token matching engine for fraud and coercion keyword detection.
    """
    
    DEFAULT_FRAUD_KEYWORDS = [
        "transfer", "otp", "urgent", "immediately", "don't tell", "dont tell",
        "ceo", "money", "account number", "wire", "upi", "verify", "bank",
        "pin", "password", "police", "digital arrest", "court fine", "extortion",
        "card details", "cvv", "credit card", "debit card", "pay now", "gpay", "phonepe"
    ]

    SECRECY_KEYWORDS = ["don't tell", "dont tell", "keep secret", "do not share", "hush", "strictly confidential"]
    URGENCY_KEYWORDS = ["urgent", "immediately", "right now", "within 5 minutes", "emergency", "account block"]
    FINANCIAL_KEYWORDS = ["transfer", "money", "account number", "wire", "upi", "pay now", "gpay", "phonepe", "bank"]

    def __init__(self, target_keywords: List[str] = None):
        self.keywords = target_keywords or self.DEFAULT_FRAUD_KEYWORDS
        # Compile regex pattern for high performance
        escaped_words = [re.escape(word) for word in self.keywords]
        self.pattern = re.compile(r'\b(' + '|'.join(escaped_words) + r')\b', re.IGNORECASE)

    def scan_transcript(self, text: str) -> Dict[str, Any]:
        """
        Scan spoken transcript for fraud keywords and categorize threat indicators.
        Returns match count, detected keywords list, keyword_score (0.0 to 100.0), and categories.
        """
        if not text or not text.strip():
            return {
                "has_fraud_keywords": False,
                "matches": [],
                "keyword_count": 0,
                "keyword_score": 0.0,
                "categories": {
                    "has_urgency": False,
                    "has_secrecy": False,
                    "has_financial": False
                }
            }

        matches = list(set(self.pattern.findall(text)))
        match_count = len(matches)
        
        # Calculate normalized keyword score (1 match = 40.0, 2 matches = 75.0, 3+ = 100.0)
        if match_count == 0:
            score = 0.0
        elif match_count == 1:
            score = 45.0
        elif match_count == 2:
            score = 75.0
        else:
            score = 100.0

        lower_text = text.lower()
        has_urgency = any(w in lower_text for w in self.URGENCY_KEYWORDS)
        has_secrecy = any(w in lower_text for w in self.SECRECY_KEYWORDS)
        has_financial = any(w in lower_text for w in self.FINANCIAL_KEYWORDS)

        return {
            "has_fraud_keywords": match_count > 0,
            "matches": matches,
            "keyword_count": match_count,
            "keyword_score": score,
            "categories": {
                "has_urgency": has_urgency,
                "has_secrecy": has_secrecy,
                "has_financial": has_financial
            }
        }
