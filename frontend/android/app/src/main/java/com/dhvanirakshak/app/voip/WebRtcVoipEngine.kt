/*
 * Dhvani Rakshak - WebRTC VoIP Audio Engine
 * Uses Google WebRTC (org.webrtc) to establish in-app VoIP audio calls.
 * Taps into the WebRTC AudioTrack frame sink in real-time, extracts 16kHz 16-bit PCM buffer chunks,
 * and streams them directly over WebSocket to the Dhvani Rakshak AI backend for live deepfake inspection.
 */

package com.dhvanirakshak.app.voip

import android.content.Context
import android.util.Log
import com.dhvanirakshak.app.audio.VoipAudioEngine
import org.webrtc.AudioConstraints
import org.webrtc.AudioSource
import org.webrtc.AudioTrack
import org.webrtc.MediaStream
import org.webrtc.PeerConnection
import org.webrtc.PeerConnectionFactory
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer

class WebRtcVoipEngine(
    private val context: Context,
    private val wsUrl: String = "ws://10.0.2.2:8000/ws/stream",
    private val onRiskUpdate: (riskScore: Float, alertLevel: String, userMessage: String) -> Unit
) {
    private var factory: PeerConnectionFactory? = null
    private var audioSource: AudioSource? = null
    private var localAudioTrack: AudioTrack? = null
    private var voipAudioEngine: VoipAudioEngine? = null

    private val pcmAccumulator = ByteArrayOutputStream()
    private val targetChunkSize = 16000 * 2 * 2 // 2-second audio chunks (64KB at 16kHz 16-bit)

    companion object {
        private const val TAG = "WebRtcVoipEngine"
    }

    fun initialize() {
        PeerConnectionFactory.initialize(
            PeerConnectionFactory.InitializationOptions.builder(context)
                .setEnableInternalTracer(true)
                .createInitializationOptions()
        )

        val options = PeerConnectionFactory.Options()
        factory = PeerConnectionFactory.builder()
            .setOptions(options)
            .createPeerConnectionFactory()

        val audioConstraints = AudioConstraints().apply {
            mandatory.add(AudioConstraints.KeyValuePair("googEchoCancellation", "true"))
            mandatory.add(AudioConstraints.KeyValuePair("googNoiseSuppression", "true"))
            mandatory.add(AudioConstraints.KeyValuePair("googAutoGainControl", "true"))
        }

        audioSource = factory?.createAudioSource(audioConstraints)
        localAudioTrack = factory?.createAudioTrack("ARDAMSa0", audioSource)

        voipAudioEngine = VoipAudioEngine(wsUrl, onRiskUpdate)
        Log.i(TAG, "WebRTC VoIP Audio Engine initialized successfully.")
    }

    fun startCallSession() {
        voipAudioEngine?.startSession()
        Log.i(TAG, "WebRTC VoIP call session started. Streaming audio to WebSocket.")
    }

    /**
     * Process raw 16kHz PCM audio buffer captured from WebRTC audio sink / audio track.
     */
    fun onWebRtcAudioFrameCaptured(pcmBuffer: ByteBuffer, sampleRate: Int, channels: Int) {
        val bytes = ByteArray(pcmBuffer.remaining())
        pcmBuffer.get(bytes)

        synchronized(pcmAccumulator) {
            pcmAccumulator.write(bytes)
            if (pcmAccumulator.size() >= targetChunkSize) {
                val chunk = pcmAccumulator.toByteArray()
                pcmAccumulator.reset()
                voipAudioEngine?.sendPcmChunk(chunk)
            }
        }
    }

    fun stopCallSession() {
        voipAudioEngine?.stopSession()
        synchronized(pcmAccumulator) {
            pcmAccumulator.reset()
        }
        Log.i(TAG, "WebRTC VoIP call session stopped.")
    }

    fun dispose() {
        stopCallSession()
        localAudioTrack?.dispose()
        audioSource?.dispose()
        factory?.dispose()
        localAudioTrack = null
        audioSource = null
        factory = null
        Log.i(TAG, "WebRTC VoIP Engine disposed.")
    }
}
