package com.dhvanirakshak.app.ui;

import android.graphics.Color;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;

import com.dhvanirakshak.app.R;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.card.MaterialCardView;

public class ResultFragment extends Fragment {

    private MaterialCardView cardRiskBadge;
    private TextView tvRiskTitle;
    private TextView tvRiskScore;
    private TextView tvReasoning;
    private MaterialButton btnAction;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_result, container, false);

        cardRiskBadge = view.findViewById(R.id.card_risk_badge);
        tvRiskTitle = view.findViewById(R.id.tv_risk_title);
        tvRiskScore = view.findViewById(R.id.tv_risk_score);
        tvReasoning = view.findViewById(R.id.tv_reasoning);
        btnAction = view.findViewById(R.id.btn_action);

        // Retrieve arguments
        Bundle args = getArguments();
        double riskScore = 0.85;
        String riskLevel = "HIGH";
        String reasoning = "• Voice Naturalness: Unnatural synthetic speech harmonics detected (AI Voice Generator).\n\n• Content Analysis: Urgent demands for money or bank OTP verification.";

        if (args != null) {
            riskScore = args.getDouble("risk_score", 0.85);
            riskLevel = args.getString("risk_level", "HIGH");
            reasoning = args.getString("reasoning", reasoning);
        }

        tvReasoning.setText(reasoning);
        int percentage = (int) Math.round(riskScore * 100);
        tvRiskScore.setText("Risk Confidence: " + percentage + "%");

        // Dual Indicator: Color + Clear Text Label (Colorblind Accessible)
        if ("HIGH".equalsIgnoreCase(riskLevel) || riskScore >= 0.70) {
            cardRiskBadge.setCardBackgroundColor(ContextCompat.getColor(requireContext(), R.color.risk_high_bg));
            tvRiskTitle.setText("HIGH RISK - SCAM DETECTED");
            btnAction.setText("Block Caller & Send Alert");
            btnAction.setBackgroundColor(ContextCompat.getColor(requireContext(), R.color.risk_high_bg));
        } else if ("MEDIUM".equalsIgnoreCase(riskLevel) || (riskScore >= 0.35 && riskScore < 0.70)) {
            cardRiskBadge.setCardBackgroundColor(ContextCompat.getColor(requireContext(), R.color.risk_medium_bg));
            tvRiskTitle.setText("MEDIUM RISK - CAUTION REQUIRED");
            btnAction.setText("Proceed with Safety Verification");
            btnAction.setBackgroundColor(ContextCompat.getColor(requireContext(), R.color.risk_medium_bg));
        } else {
            cardRiskBadge.setCardBackgroundColor(ContextCompat.getColor(requireContext(), R.color.risk_low_bg));
            tvRiskTitle.setText("LOW RISK - SAFE VOICE");
            btnAction.setText("Allow Call & Clear");
            btnAction.setBackgroundColor(ContextCompat.getColor(requireContext(), R.color.risk_low_bg));
        }

        btnAction.setOnClickListener(v -> {
            Toast.makeText(getContext(), "Action Taken: " + btnAction.getText(), Toast.LENGTH_LONG).show();
            // Navigate to Verification Checklist Fragment
            getParentFragmentManager()
                    .beginTransaction()
                    .replace(R.id.fragment_container, new VerificationFragment())
                    .addToBackStack(null)
                    .commit();
        });

        return view;
    }
}
