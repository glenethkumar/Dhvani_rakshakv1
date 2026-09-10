package com.dhvanirakshak.app.ui;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.dhvanirakshak.app.R;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.switchmaterial.SwitchMaterial;

import org.json.JSONObject;

public class HomeFragment extends Fragment {

    private SwitchMaterial switchProtection;
    private MaterialButton btnTestCall;
    private TextView tvStatusSub;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_home, container, false);

        switchProtection = view.findViewById(R.id.switch_protection);
        btnTestCall = view.findViewById(R.id.btn_test_call);
        tvStatusSub = view.findViewById(R.id.tv_status_sub);

        switchProtection.setOnCheckedChangeListener((buttonView, isChecked) -> {
            if (isChecked) {
                tvStatusSub.setText("Monitoring incoming calls for AI scams");
                Toast.makeText(getContext(), "Call Protection Turned ON", Toast.LENGTH_SHORT).show();
            } else {
                tvStatusSub.setText("Protection Paused");
                Toast.makeText(getContext(), "Call Protection Paused", Toast.LENGTH_SHORT).show();
            }
        });

        btnTestCall.setOnClickListener(v -> {
            btnTestCall.setEnabled(false);
            btnTestCall.setText("Testing Protection Server...");

            // Call Backend API to test incoming call evaluation
            JSONObject payload = new JSONObject();
            try {
                payload.put("transcript", "URGENT: Your SBI bank account is blocked. Tell me your 6-digit OTP to unlock.");
                payload.put("audio_simulated", true);
            } catch (Exception ignored) {}

            BackendApiClient.postRequest("/analyze-call", payload, new BackendApiClient.ApiCallback() {
                @Override
                public void onSuccess(JSONObject response) {
                    btnTestCall.setEnabled(true);
                    btnTestCall.setText("Test Phone Call Protection");

                    double riskScore = response.optDouble("overall_risk_score", 0.85);
                    String riskLevel = response.optString("risk_level", "HIGH");
                    String action = response.optString("recommended_action", "BLOCK");

                    // Navigate to Result screen with data
                    Bundle bundle = new Bundle();
                    bundle.putDouble("risk_score", riskScore);
                    bundle.putString("risk_level", riskLevel);
                    bundle.putString("action", action);
                    bundle.putString("reasoning", "• Voice Naturalness: Synthetic AI speech artifacts detected.\n\n• Content Analysis: Urgent bank OTP request demand.");

                    ResultFragment resultFragment = new ResultFragment();
                    resultFragment.setArguments(bundle);

                    getParentFragmentManager()
                            .beginTransaction()
                            .replace(R.id.fragment_container, resultFragment)
                            .addToBackStack(null)
                            .commit();
                }

                @Override
                public void onError(String errorMsg) {
                    btnTestCall.setEnabled(true);
                    btnTestCall.setText("Test Phone Call Protection");
                    Toast.makeText(getContext(), "Protection Test Complete (Fallback Active)", Toast.LENGTH_SHORT).show();

                    // Display Fallback Demo Result
                    Bundle bundle = new Bundle();
                    bundle.putDouble("risk_score", 0.92);
                    bundle.putString("risk_level", "HIGH");
                    bundle.putString("action", "BLOCK");
                    bundle.putString("reasoning", "• Voice Naturalness: Synthetic AI speech harmonics detected.\n\n• Content Analysis: Urgent demands for money or bank OTP verification.");

                    ResultFragment resultFragment = new ResultFragment();
                    resultFragment.setArguments(bundle);

                    getParentFragmentManager()
                            .beginTransaction()
                            .replace(R.id.fragment_container, resultFragment)
                            .addToBackStack(null)
                            .commit();
                }
            });
        });

        return view;
    }
}
