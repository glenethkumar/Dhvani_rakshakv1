/*
 * Dhvani Rakshak - Background Call Audio Foreground Service
 * Runs active audio processing in background using Android ForegroundService (foregroundServiceType="microphone").
 * Manages both VoIP and Speakerphone microphone channels.
 */

package com.dhvanirakshak.app.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import com.dhvanirakshak.app.audio.SpeakerphoneRecorder
import com.dhvanirakshak.app.audio.VoipAudioEngine

class CallAudioService : Service() {

    private var speakerphoneRecorder: SpeakerphoneRecorder? = null
    private var voipAudioEngine: VoipAudioEngine? = null

    companion object {
        private const val TAG = "CallAudioService"
        private const val CHANNEL_ID = "dhvani_rakshak_audio_channel"
        private const val NOTIFICATION_ID = 1001

        const val ACTION_START_SPEAKERPHONE = "ACTION_START_SPEAKERPHONE"
        const val ACTION_START_VOIP = "ACTION_START_VOIP"
        const val ACTION_STOP_SERVICE = "ACTION_STOP_SERVICE"
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val action = intent?.action

        when (action) {
            ACTION_START_SPEAKERPHONE -> {
                startForeground(NOTIFICATION_ID, buildNotification("Scanning Speakerphone Mic Audio..."))
                startSpeakerphoneCapture()
            }
            ACTION_START_VOIP -> {
                startForeground(NOTIFICATION_ID, buildNotification("Scanning In-App VoIP Call Audio..."))
                startVoipCapture()
            }
            ACTION_STOP_SERVICE -> {
                stopAudioProcessing()
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
        }
        return START_NOT_STICKY
    }

    private fun startSpeakerphoneCapture() {
        voipAudioEngine = VoipAudioEngine { riskScore, alertLevel, userMessage ->
            Log.i(TAG, "Risk Update -> Score: $riskScore | Alert: $alertLevel | Msg: $userMessage")
        }.apply { startSession() }

        speakerphoneRecorder = SpeakerphoneRecorder { pcmBytes ->
            voipAudioEngine?.sendPcmChunk(pcmBytes)
        }.apply { startRecording() }
    }

    private fun startVoipCapture() {
        voipAudioEngine = VoipAudioEngine { riskScore, alertLevel, userMessage ->
            Log.i(TAG, "VoIP Risk Update -> Score: $riskScore | Alert: $alertLevel")
        }.apply { startSession() }
    }

    private fun stopAudioProcessing() {
        speakerphoneRecorder?.stopRecording()
        voipAudioEngine?.stopSession()
        speakerphoneRecorder = null
        voipAudioEngine = null
    }

    private fun buildNotification(text: String): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Dhvani Rakshak Voice Defense Active")
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_menu_call)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Dhvani Rakshak Audio Scanner",
                NotificationManager.IMPORTANCE_LOW
            )
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        stopAudioProcessing()
        super.onDestroy()
    }
}
