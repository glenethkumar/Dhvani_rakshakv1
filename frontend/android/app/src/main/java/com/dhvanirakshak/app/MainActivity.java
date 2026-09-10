package com.dhvanirakshak.app;

import android.os.Build;
import android.os.Bundle;
import android.view.Window;
import android.view.WindowManager;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        // Register Native Call Detector Plugin for Background Phone Call Interception
        registerPlugin(CallDetectorPlugin.class);

        super.onCreate(savedInstanceState);

        // Enhance native mobile system bar appearance
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            Window window = getWindow();
            window.addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
            window.setStatusBarColor(0xFF0F172A); // Dark slate theme status bar (#0F172A)
            window.setNavigationBarColor(0xFF0F172A); // Dark slate navigation bar (#0F172A)
        }
    }
}
