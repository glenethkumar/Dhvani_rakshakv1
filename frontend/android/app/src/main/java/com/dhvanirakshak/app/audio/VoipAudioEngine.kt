/*
 * Dhvani Rakshak - In-App VoIP Call Audio Engine
 * Taps into in-app WebRTC / VoIP call audio buffers and streams PCM frame chunks
 * directly to Dhvani Rakshak backend over WebSocket for real-time deepfake analysis.
 */

package com.dhvanirakshak.app.audio

import android.util.Log
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import okio.ByteString.Companion.toByteString
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class VoipAudioEngine(
    private val backendWsUrl: String = "ws://10.0.2.2:8000/ws/stream",
    private val onRiskUpdate: (riskScore: Float, alertLevel: String, userMessage: String) -> Unit
) {
    private var client: OkHttpClient? = null
    private var webSocket: WebSocket? = null
    private var isConnected = false

    companion object {
        private const val TAG = "VoipAudioEngine"
    }

    fun startSession() {
        client = OkHttpClient.Builder()
            .readTimeout(10, TimeUnit.SECONDS)
            .writeTimeout(10, TimeUnit.SECONDS)
            .build()

        val request = Request.Builder()
            .url(backendWsUrl)
            .build()

        webSocket = client?.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: okhttp3.Response) {
                Log.i(TAG, "VoIP WebSocket connection opened to $backendWsUrl")
                isConnected = true
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                try {
                    val json = JSONObject(text)
                    val riskScore = json.optDouble("risk_score", 0.0).toFloat()
                    val alertLevel = json.optString("alert_level", "GREEN")
                    val userMessage = json.optString("user_message", "Authentic voice call.")

                    onRiskUpdate(riskScore, alertLevel, userMessage)
                } catch (e: Exception) {
                    Log.e(TAG, "Error parsing WebSocket risk payload", e)
                }
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: okhttp3.Response?) {
                Log.e(TAG, "VoIP WebSocket failure: ${t.message}")
                isConnected = false
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                Log.i(TAG, "VoIP WebSocket closed: $reason")
                isConnected = false
            }
        })
    }

    fun sendPcmChunk(pcmData: ByteArray) {
        if (isConnected && webSocket != null) {
            webSocket?.send(pcmData.toByteString())
        }
    }

    fun stopSession() {
        try {
            webSocket?.close(1000, "VoIP Call Ended")
            client?.dispatcher?.executorService?.shutdown()
        } catch (e: Exception) {
            Log.e(TAG, "Error closing VoIP session", e)
        } finally {
            isConnected = false
            webSocket = null
        }
        Log.i(TAG, "VoIP Audio Engine session stopped.")
    }
}
