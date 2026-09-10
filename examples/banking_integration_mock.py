"""
Dhvani Rakshak - Enterprise Banking Integration Example (NPCI / Razorpay / Core Banking Gateway)
Simulates real-time voice verification before authorizing a high-value ₹15,00,000 wire transfer.
"""

import sys
import os
import json

# Ensure UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sdks.python.dhvani_sdk import DhvaniRakshakClient

def process_banking_wire_transfer():
    print("=" * 70)
    print("  ENTERPRISE CORE BANKING INTERCEPTOR - POWERED BY DHVANI RAKSHAK  ")
    print("=" * 70)

    client = DhvaniRakshakClient(api_url="http://localhost:8000")

    # Transaction Details
    transaction = {
        "transaction_id": "TXN_994827104",
        "amount_inr": 1500000,  # ₹15 Lakhs
        "sender_account": "ACC_884920194",
        "payee_name": "Offshore Global Logistics Ltd",
        "is_new_payee": True
    }

    caller_info = {
        "caller_id": "+91 98765 43210",
        "caller_role": "Executive",
        "ip_address": "198.51.100.99",
        "is_off_hours": True
    }

    print(f"\n[BANKING GATEWAY] Wire Transfer Initiated:")
    print(f"  - Amount: ₹{transaction['amount_inr']:,}")
    print(f"  - Beneficiary: {transaction['payee_name']} (NEW PAYEE)")
    print(f"  - Caller ID: {caller_info['caller_id']} (Off-hours Executive Call)")

    sample_audio_path = os.path.join(os.path.dirname(__file__), "..", "backend", "audio_samples", "elevenlabs_ai_clone.wav")

    if not os.path.exists(sample_audio_path):
        print("\nError: Run `python tests/generate_test_audio.py` first to generate sample audio.")
        return

    print("\n[DHVANI RAKSHAK] Intercepting call audio stream & extracting multi-layer features...")

    # Analyze audio via SDK
    try:
        res = client.analyze_audio(
            audio_filepath=sample_audio_path,
            language="en-IN",
            target_speaker_id="CXO_001",
            caller_metadata=caller_info,
            transaction_context=transaction
        )

        risk = res["risk_assessment"]
        print(f"\n[ANALYSIS COMPLETE] Sub-second Latency: {res['latency_ms']} ms")
        print(f"  - Impersonation Risk Score: {risk['risk_score']} / 100")
        print(f"  - Threat Alert Level: [{risk['alert_level']}]")
        print(f"  - System Action: {risk['recommendation']}")
        print(f"  - User Notification: {risk['user_message']}")
        print(f"  - Flagged Threat Multipliers: {risk.get('flagged_context_risk_factors', [])}")

        if risk["alert_level"] in ["RED", "YELLOW"]:
            print("\n[SECURITY BLOCK] Transaction intercept triggered!")
            print(f"  - Audit Trail Integrity Hash: {res['audit_integrity_hash']}")
            if res.get("mitigation_workflow"):
                opt = res["mitigation_workflow"]["options"]
                print(f"  - Secondary Verification Activated:")
                print(f"    * Callback Target: {opt['callback']['target_number']}")
                print(f"    * Step-Up OTP Generated: {opt['otp']['generated_otp']}")
                print(f"    * Voice Liveness Passphrase: '{opt['voice_liveness']['challenge_phrase']}'")
        else:
            print("\n[APPROVED] Call audio verified. Processing transaction.")

    except Exception as e:
        print(f"\nAPI Error (Ensure backend server `uvicorn backend.main:app` is running): {e}")

if __name__ == "__main__":
    process_banking_wire_transfer()
