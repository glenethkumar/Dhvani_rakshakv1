"""
Dhvani Rakshak - Step 3 Direct Backend Regression Verification Suite
Tests clean_analyzer.analyze_voice directly against the exact 6 test clips:
  1. Live human speech
  2. Replayed human speech
  3. Song / music clip
  4. Silence / no audio
  5. TTS-generated AI voice clip
  6. Voice-converted AI clip

Prints regression summary table: Clip | Expected result | Actual result | Pass/Fail
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.clean_voice_analyzer import CleanVoiceAnalyzer

def run_step3_regression_suite():
    analyzer = CleanVoiceAnalyzer()
    audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "regression_audio")

    test_cases = [
        {
            "id": 1,
            "filename": "1_live_human_speech.wav",
            "name": "Live human speech",
            "expected_status": "OK",
            "expected_risk": "Low",
            "min_auth": 70
        },
        {
            "id": 2,
            "filename": "2_replayed_human_speech.wav",
            "name": "Replayed human speech",
            "expected_status": "OK",
            "expected_risk": "Low",
            "min_auth": 70
        },
        {
            "id": 3,
            "filename": "3_song_music_clip.wav",
            "name": "Song / music clip",
            "expected_status": "NO_SPEECH",
            "expected_risk": "Neutral",
            "min_auth": 0
        },
        {
            "id": 4,
            "filename": "4_silence_no_audio.wav",
            "name": "Silence / no audio",
            "expected_status": "NO_SPEECH",
            "expected_risk": "Neutral",
            "min_auth": 0
        },
        {
            "id": 5,
            "filename": "5_tts_ai_voice.wav",
            "name": "TTS-generated AI voice",
            "expected_status": "OK",
            "expected_risk": "High",
            "max_auth": 30
        },
        {
            "id": 6,
            "filename": "6_voice_converted_ai_clip.wav",
            "name": "Voice-converted AI clip",
            "expected_status": "OK",
            "expected_risk": "High",
            "max_auth": 30
        }
    ]

    print("\n" + "=" * 85)
    print(" [STEP 3] DHVANI RAKSHAK - DIRECT BACKEND REGRESSION VERIFICATION SUITE")
    print("=" * 85)

    results_table = []
    all_passed = True

    for test in test_cases:
        filepath = os.path.join(audio_dir, test["filename"])
        with open(filepath, "rb") as f:
            audio_bytes = f.read()

        req_id = f"REG_{test['id']:02d}"
        res = analyzer.analyze_voice(audio_bytes, filename=test["filename"], session_id=req_id)

        status = res.get("status")
        risk_level = res.get("risk_level", "Neutral")
        auth_score = res.get("authenticity_score", 0)

        # Check Pass / Fail criteria
        passed = False
        if test["expected_status"] == "NO_SPEECH":
            passed = (status == "NO_SPEECH")
            exp_str = "NO_SPEECH"
            act_str = f"status={status}"
        else: # expected_status == "OK"
            if "min_auth" in test:
                passed = (status == "OK" and risk_level == test["expected_risk"] and auth_score >= test["min_auth"])
                exp_str = f"OK, {test['expected_risk']} (auth >= {test['min_auth']})"
            else:
                passed = (status == "OK" and risk_level == test["expected_risk"] and auth_score <= test["max_auth"])
                exp_str = f"OK, {test['expected_risk']} (auth <= {test['max_auth']})"
            act_str = f"status={status}, risk={risk_level}, auth={auth_score}%"

        if not passed:
            all_passed = False

        pf_str = "PASS" if passed else "FAIL"

        results_table.append({
            "id": test["id"],
            "name": test["name"],
            "expected": exp_str,
            "actual": act_str,
            "result": pf_str
        })

    print("\n" + "-" * 85)
    print(f"{'Clip #':<8} | {'Clip Description':<30} | {'Expected Result':<25} | {'Actual Result':<28} | {'Result':<6}")
    print("-" * 85)
    for r in results_table:
        print(f"{r['id']:<8} | {r['name']:<30} | {r['expected']:<25} | {r['actual']:<28} | {r['result']:<6}")
    print("-" * 85)

    if all_passed:
        print("\n[SUCCESS] All 6 regression test cases PASSED cleanly in a single run!\n")
    else:
        print("\n[FAIL] One or more test cases failed. Re-run required.\n")

    return all_passed, results_table

if __name__ == "__main__":
    run_step3_regression_suite()
