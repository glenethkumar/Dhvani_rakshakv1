"""
Dhvani Rakshak - Step 4 Final Three-Tier Regression Verification Suite
Verifies all 6 test cases against the exact three-tier risk system contract:
  - authenticity_score 0-39   -> label: "Human Voice"     -> color: GREEN  -> "Safe"
  - authenticity_score 40-69  -> label: "Uncertain Voice" -> color: YELLOW -> "Recommend Verification"
  - authenticity_score 70-100 -> label: "AI Voice Clone"  -> color: RED    -> "High Risk - Flagged"
  - Silence / No Speech       -> state: "No speech detected" (no numeric score)
"""

import sys
import os
import wave
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from core.clean_voice_analyzer import CleanVoiceAnalyzer

def run_regression_suite():
    analyzer = CleanVoiceAnalyzer()
    audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "regression_audio")

    test_cases = [
        {
            "num": 1,
            "filename": "1_live_human_speech.wav",
            "desc": "Live human speech (clear, direct)",
            "expected_color": "GREEN",
            "expected_label": "Human Voice",
            "expected_score_range": (0, 39)
        },
        {
            "num": 2,
            "filename": "2_second_live_human_speech.wav",
            "desc": "Second live human speaker (female/different pitch)",
            "expected_color": "GREEN",
            "expected_label": "Human Voice",
            "expected_score_range": (0, 39)
        },
        {
            "num": 3,
            "filename": "3_tts_ai_voice.wav",
            "desc": "TTS-generated AI voice clip",
            "expected_color": "RED",
            "expected_label": "AI Voice Clone",
            "expected_score_range": (70, 100)
        },
        {
            "num": 4,
            "filename": "4_voice_converted_ai_clip.wav",
            "desc": "Voice-converted AI clip (RVC/Voice-to-Voice)",
            "expected_color": "RED",
            "expected_label": "AI Voice Clone",
            "expected_score_range": (70, 100)
        },
        {
            "num": 5,
            "filename": "5_unclear_mumbling_ambiguous.wav",
            "desc": "Background noise / unclear mumbling",
            "expected_color": "YELLOW",
            "expected_label": "Uncertain Voice",
            "expected_score_range": (40, 69)
        },
        {
            "num": 6,
            "filename": "6_silence_no_speech.wav",
            "desc": "Silence / no speech",
            "expected_color": "NEUTRAL",
            "expected_label": "No Speech Detected",
            "expected_score_range": None
        }
    ]

    print("\n" + "="*110)
    print("DHVANI RAKSHAK — STEP 4 THREE-TIER RISK REGRESSION VERIFICATION SUITE")
    print("="*110 + "\n")

    results_table = []
    all_passed = True

    for test in test_cases:
        filepath = os.path.join(audio_dir, test["filename"])
        if not os.path.exists(filepath):
            print(f"[ERROR] Test audio file missing: {filepath}")
            all_passed = False
            continue

        with open(filepath, "rb") as f:
            audio_bytes = f.read()

        raw_result = analyzer.analyze_voice(audio_bytes, filename=test["filename"], session_id=f"REG_{test['num']:02d}")
        
        status = raw_result.get("status")
        raw_score = raw_result.get("authenticity_score")
        label = raw_result.get("label", raw_result.get("voice_label"))
        color = raw_result.get("color", raw_result.get("alert_level"))

        # Evaluation criteria check
        if test["expected_color"] == "NEUTRAL":
            # Expecting NO_SPEECH state without numeric score
            is_pass = (status == "NO_SPEECH") and (raw_result.get("message") == "No spoken voice detected in this clip")
            display_score = "N/A (No score)"
            actual_label = "No Speech Detected"
            actual_color = "NEUTRAL"
        else:
            is_pass = False
            display_score = str(raw_score)
            actual_label = str(label)
            actual_color = str(color)

            if status == "OK" and raw_score is not None:
                min_s, max_s = test["expected_score_range"]
                if min_s <= raw_score <= max_s and actual_color == test["expected_color"]:
                    is_pass = True

        if not is_pass:
            all_passed = False

        results_table.append({
            "num": test["num"],
            "desc": test["desc"],
            "raw_score": display_score,
            "label": actual_label,
            "color": actual_color,
            "status": "PASS" if is_pass else "FAIL"
        })

    # Print Formatted Verification Table
    print("\n" + "-"*110)
    print(f"{'Clip #':<7} | {'Clip Description':<40} | {'Raw Score':<12} | {'Label':<18} | {'Color':<8} | {'Result'}")
    print("-"*110)

    for row in results_table:
        print(f"{row['num']:<7} | {row['desc']:<40} | {row['raw_score']:<12} | {row['label']:<18} | {row['color']:<8} | {row['status']}")

    print("-"*110 + "\n")

    if all_passed:
        print("[SUCCESS] All 6 three-tier regression test cases PASSED cleanly in a single run!\n")
    else:
        print("[FAILURE] One or more test cases failed. Please inspect logs.\n")

    return all_passed

if __name__ == "__main__":
    success = run_regression_suite()
    sys.exit(0 if success else 1)
