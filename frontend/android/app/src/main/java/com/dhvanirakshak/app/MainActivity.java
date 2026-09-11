package com.dhvanirakshak.app;

import android.os.Build;
import android.os.Bundle;
import android.view.Window;
import android.view.WindowManager;

import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebView;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Enhance native mobile system bar appearance
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            Window window = getWindow();
            window.addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
            window.setStatusBarColor(0xFF07090E); // Deep dark theme status bar
            window.setNavigationBarColor(0xFF07090E); // Deep dark navigation bar
        }
    }

    @Override
    public void onStart() {
        super.onStart();
        // Enable WebAudio microphone permission prompts inside Capacitor WebView
        if (this.bridge != null && this.bridge.getWebView() != null) {
            this.bridge.getWebView().setWebChromeClient(new WebChromeClient() {
                @Override
                public void onPermissionRequest(final PermissionRequest request) {
                    runOnUiThread(() -> request.grant(request.getResources()));
                }
            });
        }
    }
}
