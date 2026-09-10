"""
Dhvani Rakshak - Contextual Enrichment Engine
Evaluates caller metadata, transaction value, IP geolocation, off-hours timing,
and historical fraud graphs to compute context risk multipliers.
"""

class ContextEnricher:
    def __init__(self):
        self.known_vip_directory = {
            "CXO_001": {"name": "Rajesh Sharma (CEO)", "role": "Executive", "trusted_ip": "203.0.113.45"},
            "CXO_002": {"name": "Priya Nair (CFO)", "role": "Executive", "trusted_ip": "198.51.100.12"}
        }

    def enrich_context(self, caller_metadata: dict = None, transaction_context: dict = None) -> tuple[float, list[str]]:
        """
        Calculates contextual multiplier and returns flagged risk factors.
        """
        multiplier = 1.0
        risk_flags = []

        if not caller_metadata:
            caller_metadata = {}
        if not transaction_context:
            transaction_context = {}

        # 1. High-value transaction check
        amount = transaction_context.get("amount_inr", 0)
        if amount >= 1000000:  # >= 10 Lakhs
            multiplier += 0.20
            risk_flags.append("HIGH_VALUE_TRANSACTION (> ₹10L)")
        elif amount >= 200000:  # >= 2 Lakhs
            multiplier += 0.10
            risk_flags.append("ELEVATED_VALUE_TRANSACTION (> ₹2L)")

        # 2. New payee / beneficiary addition
        if transaction_context.get("is_new_payee", False):
            multiplier += 0.10
            risk_flags.append("NEW_UNVERIFIED_BENEFICIARY")

        # 3. Off-hours executive call check
        is_off_hours = caller_metadata.get("is_off_hours", False)
        caller_role = caller_metadata.get("caller_role", "Standard")
        if is_off_hours and caller_role == "Executive":
            multiplier += 0.15
            risk_flags.append("OFF_HOURS_EXECUTIVE_CALL")

        # 4. Geolocation / IP Anomaly
        ip = caller_metadata.get("ip_address", "")
        caller_id = caller_metadata.get("caller_id", "")
        if caller_id in self.known_vip_directory:
            trusted = self.known_vip_directory[caller_id]["trusted_ip"]
            if ip and ip != trusted:
                multiplier += 0.15
                risk_flags.append("GEOLOCATION_IP_MISMATCH")

        # 5. VoIP / Virtual number indicator
        if caller_metadata.get("is_voip_proxy", False):
            multiplier += 0.10
            risk_flags.append("VOIP_ANONYMOUS_PROXY_LINE")

        return round(min(1.5, multiplier), 2), risk_flags
