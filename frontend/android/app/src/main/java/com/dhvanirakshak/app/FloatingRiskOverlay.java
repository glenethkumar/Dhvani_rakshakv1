package com.dhvanirakshak.app;

import android.content.Context;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.util.Log;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

public class FloatingRiskOverlay {
    private static final String TAG = "FloatingRiskOverlay";
    private final Context context;
    private final WindowManager windowManager;
    private View overlayView;
    private TextView tvStatus;
    private TextView tvRiskScore;
    private TextView tvMessage;

    public FloatingRiskOverlay(Context context) {
        this.context = context;
        this.windowManager = (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);
    }

    public void showOverlay(String callerNumber, double riskScore, String alertLevel, String message) {
        new Handler(Looper.getMainLooper()).post(() -> {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && !Settings.canDrawOverlays(context)) {
                Log.w(TAG, "SYSTEM_ALERT_WINDOW permission not granted yet by user.");
                return;
            }

            if (overlayView != null) {
                updateRisk(riskScore, alertLevel, message);
                return;
            }

            int layoutType;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                layoutType = WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY;
            } else {
                layoutType = WindowManager.LayoutParams.TYPE_PHONE;
            }

            WindowManager.LayoutParams params = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.WRAP_CONTENT,
                layoutType,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON,
                PixelFormat.TRANSLUCENT
            );
            params.gravity = Gravity.TOP | Gravity.CENTER_HORIZONTAL;
            params.y = 120; // Top offset below status bar

            LinearLayout container = new LinearLayout(context);
            container.setOrientation(LinearLayout.VERTICAL);
            container.setPadding(40, 30, 40, 30);

            GradientDrawable background = new GradientDrawable();
            background.setColor(Color.parseColor("#0F172A"));
            background.setCornerRadius(30);
            background.setStroke(4, getAlertColor(alertLevel));
            container.setBackground(background);

            // Title Header
            TextView tvTitle = new TextView(context);
            tvTitle.setText("🛡️ DHVANI RAKSHAK - LIVE CALL RISK INTERCEPTOR");
            tvTitle.setTextColor(Color.parseColor("#06B6D4"));
            tvTitle.setTextSize(TypedValue.COMPLEX_UNIT_SP, 12);
            tvTitle.setTypeface(null, android.graphics.Typeface.BOLD);
            container.addView(tvTitle);

            // Caller info
            tvStatus = new TextView(context);
            tvStatus.setText("Call: " + callerNumber);
            tvStatus.setTextColor(Color.WHITE);
            tvStatus.setTextSize(TypedValue.COMPLEX_UNIT_SP, 14);
            tvStatus.setPadding(0, 8, 0, 8);
            container.addView(tvStatus);

            // Risk Score Badge
            tvRiskScore = new TextView(context);
            if ("WAITING".equalsIgnoreCase(alertLevel) || "SILENCE".equalsIgnoreCase(alertLevel)) {
                tvRiskScore.setText("AI CLONE RISK SCORE: 0.0% (WAITING FOR SPEECH)");
            } else {
                tvRiskScore.setText(String.format(java.util.Locale.US, "AI CLONE RISK SCORE: %.1f%% (%s)", riskScore, alertLevel));
            }
            tvRiskScore.setTextColor(getAlertColor(alertLevel));
            tvRiskScore.setTextSize(TypedValue.COMPLEX_UNIT_SP, 15);
            tvRiskScore.setTypeface(null, android.graphics.Typeface.BOLD);
            container.addView(tvRiskScore);

            // Detailed User Message
            tvMessage = new TextView(context);
            tvMessage.setText(message);
            tvMessage.setTextColor(Color.parseColor("#94A3B8"));
            tvMessage.setTextSize(TypedValue.COMPLEX_UNIT_SP, 12);
            tvMessage.setPadding(0, 6, 0, 14);
            container.addView(tvMessage);

            // Dismiss Button
            Button btnClose = new Button(context);
            btnClose.setText("Dismiss Badge");
            btnClose.setTextColor(Color.WHITE);
            btnClose.setBackgroundColor(Color.parseColor("#334155"));
            btnClose.setOnClickListener(v -> removeOverlay());
            container.addView(btnClose);

            overlayView = container;
            try {
                windowManager.addView(overlayView, params);
            } catch (Exception e) {
                Log.e(TAG, "Error adding overlay window", e);
                overlayView = null;
            }
        });
    }

    public void updateRisk(double riskScore, String alertLevel, String message) {
        new Handler(Looper.getMainLooper()).post(() -> {
            if (overlayView == null) return;
            if (tvRiskScore != null) {
                if ("WAITING".equalsIgnoreCase(alertLevel) || "SILENCE".equalsIgnoreCase(alertLevel)) {
                    tvRiskScore.setText("AI CLONE RISK SCORE: 0.0% (WAITING FOR SPEECH)");
                } else {
                    tvRiskScore.setText(String.format(java.util.Locale.US, "AI CLONE RISK SCORE: %.1f%% (%s)", riskScore, alertLevel));
                }
                tvRiskScore.setTextColor(getAlertColor(alertLevel));
            }
            if (tvMessage != null) {
                tvMessage.setText(message);
            }
        });
    }

    public void removeOverlay() {
        new Handler(Looper.getMainLooper()).post(() -> {
            if (overlayView != null && windowManager != null) {
                try {
                    windowManager.removeView(overlayView);
                } catch (Exception e) {
                    Log.e(TAG, "Error removing overlay view", e);
                }
                overlayView = null;
            }
        });
    }

    private int getAlertColor(String alertLevel) {
        if ("RED".equalsIgnoreCase(alertLevel)) {
            return Color.parseColor("#EF4444");
        } else if ("YELLOW".equalsIgnoreCase(alertLevel)) {
            return Color.parseColor("#F59E0B");
        } else if ("GREEN".equalsIgnoreCase(alertLevel)) {
            return Color.parseColor("#10B981");
        }
        // Neutral blue for WAITING / SILENCE state
        return Color.parseColor("#38BDF8");
    }
}
