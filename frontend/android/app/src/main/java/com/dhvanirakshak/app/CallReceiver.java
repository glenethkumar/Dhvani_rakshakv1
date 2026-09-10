package com.dhvanirakshak.app;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.telephony.TelephonyManager;
import android.util.Log;

public class CallReceiver extends BroadcastReceiver {
    private static final String TAG = "DhvaniCallReceiver";
    private static String lastState = TelephonyManager.EXTRA_STATE_IDLE;
    private static String currentCallerNumber = "";

    @Override
    @SuppressWarnings("deprecation")
    public void onReceive(Context context, Intent intent) {
        if (intent == null || intent.getAction() == null) return;

        if (intent.getAction().equals(TelephonyManager.ACTION_PHONE_STATE_CHANGED)) {
            String stateStr = intent.getStringExtra(TelephonyManager.EXTRA_STATE);
            String number = intent.getStringExtra(TelephonyManager.EXTRA_INCOMING_NUMBER);

            if (number != null && !number.isEmpty()) {
                currentCallerNumber = number;
            }

            if (stateStr == null) return;

            if (stateStr.equals(TelephonyManager.EXTRA_STATE_RINGING)) {
                Log.d(TAG, "Incoming Phone Call Ringing from: " + currentCallerNumber);
            } else if (stateStr.equals(TelephonyManager.EXTRA_STATE_OFFHOOK)) {
                Log.d(TAG, "Phone Call Answered / Offhook: " + currentCallerNumber);
                // Start Native Call Detection & Floating Risk Score Overlay Service
                Intent serviceIntent = new Intent(context, CallDetectionService.class);
                serviceIntent.putExtra("ACTION", "START_DETECTION");
                serviceIntent.putExtra("CALLER_NUMBER", currentCallerNumber != null ? currentCallerNumber : "Incoming Call");
                if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                    context.startForegroundService(serviceIntent);
                } else {
                    context.startService(serviceIntent);
                }
            } else if (stateStr.equals(TelephonyManager.EXTRA_STATE_IDLE)) {
                Log.d(TAG, "Phone Call Ended / Idle");
                // Stop Call Detection Service & Dismiss Overlay
                Intent serviceIntent = new Intent(context, CallDetectionService.class);
                serviceIntent.putExtra("ACTION", "STOP_DETECTION");
                context.stopService(serviceIntent);
            }

            lastState = stateStr;
        }
    }
}
