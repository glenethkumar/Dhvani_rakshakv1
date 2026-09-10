package com.dhvanirakshak.app.ui;

import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class BackendApiClient {

    private static final String TAG = "BackendApiClient";

    // Primary Production Render, Local Wi-Fi IP, and Emulator Fallback URLs
    private static final String[] BASE_URLS = new String[] {
        "https://dhvani-rakshak-backend.onrender.com",
        "http://192.168.31.150:8000",
        "http://10.0.2.2:8000"
    };

    private static final ExecutorService executor = Executors.newSingleThreadExecutor();
    private static final Handler mainHandler = new Handler(Looper.getMainLooper());

    public interface ApiCallback {
        void onSuccess(JSONObject response);
        void onError(String errorMsg);
    }

    public static void postRequest(String endpoint, JSONObject payload, ApiCallback callback) {
        executor.execute(() -> {
            boolean success = false;
            String lastError = "Network connection error";

            for (String baseUrl : BASE_URLS) {
                HttpURLConnection conn = null;
                try {
                    URL url = new URL(baseUrl + endpoint);
                    conn = (HttpURLConnection) url.openConnection();
                    conn.setRequestMethod("POST");
                    conn.setRequestProperty("Content-Type", "application/json");
                    conn.setConnectTimeout(4000);
                    conn.setReadTimeout(4000);
                    conn.setDoOutput(true);

                    if (payload != null) {
                        try (OutputStream os = conn.getOutputStream()) {
                            byte[] input = payload.toString().getBytes("utf-8");
                            os.write(input, 0, input.length);
                        }
                    }

                    int code = conn.getResponseCode();
                    BufferedReader br = new BufferedReader(new InputStreamReader(
                            code >= 400 ? conn.getErrorStream() : conn.getInputStream(), "utf-8"));
                    StringBuilder sb = new StringBuilder();
                    String line;
                    while ((line = br.readLine()) != null) {
                        sb.append(line.trim());
                    }

                    JSONObject responseJson = new JSONObject(sb.toString());
                    mainHandler.post(() -> callback.onSuccess(responseJson));
                    success = true;
                    conn.disconnect();
                    break;

                } catch (Exception e) {
                    lastError = e.getMessage() != null ? e.getMessage() : "Failed to connect to " + baseUrl;
                    Log.w(TAG, "Request failed for " + baseUrl + endpoint + ": " + lastError);
                } finally {
                    if (conn != null) conn.disconnect();
                }
            }

            if (!success) {
                final String finalErr = lastError;
                mainHandler.post(() -> callback.onError(finalErr));
            }
        });
    }

    public static void getRequest(String endpoint, ApiCallback callback) {
        executor.execute(() -> {
            boolean success = false;
            String lastError = "Network connection error";

            for (String baseUrl : BASE_URLS) {
                HttpURLConnection conn = null;
                try {
                    URL url = new URL(baseUrl + endpoint);
                    conn = (HttpURLConnection) url.openConnection();
                    conn.setRequestMethod("GET");
                    conn.setConnectTimeout(4000);
                    conn.setReadTimeout(4000);

                    int code = conn.getResponseCode();
                    BufferedReader br = new BufferedReader(new InputStreamReader(
                            code >= 400 ? conn.getErrorStream() : conn.getInputStream(), "utf-8"));
                    StringBuilder sb = new StringBuilder();
                    String line;
                    while ((line = br.readLine()) != null) {
                        sb.append(line.trim());
                    }

                    JSONObject responseJson = new JSONObject(sb.toString());
                    mainHandler.post(() -> callback.onSuccess(responseJson));
                    success = true;
                    conn.disconnect();
                    break;

                } catch (Exception e) {
                    lastError = e.getMessage() != null ? e.getMessage() : "Failed to connect to " + baseUrl;
                    Log.w(TAG, "Request failed for " + baseUrl + endpoint + ": " + lastError);
                } finally {
                    if (conn != null) conn.disconnect();
                }
            }

            if (!success) {
                final String finalErr = lastError;
                mainHandler.post(() -> callback.onError(finalErr));
            }
        });
    }
}
