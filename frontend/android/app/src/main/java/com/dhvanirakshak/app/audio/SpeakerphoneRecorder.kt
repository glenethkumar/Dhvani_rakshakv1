/*
 * Dhvani Rakshak - Speakerphone Mic Audio Acquisition Module
 * Captures external cellular call audio via microphone using MediaRecorder.AudioSource.VOICE_RECOGNITION.
 * Complies 100% with Android OS privacy sandboxing and cellular audio access policies.
 */

package com.dhvanirakshak.app.audio

import android.annotation.SuppressLint
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import java.io.ByteArrayOutputStream

class SpeakerphoneRecorder(
    private val sampleRate: Int = 16000,
    private val onAudioChunkCaptured: (ByteArray) -> Unit
) {
    private var audioRecord: AudioRecord? = null
    private var isRecording = false
    private var recordingJob: Job? = null
    private val scope = CoroutineScope(Dispatchers.IO)

    companion object {
        private const val TAG = "SpeakerphoneRecorder"
    }

    @SuppressLint("MissingPermission")
    fun startRecording() {
        if (isRecording) return

        val channelConfig = AudioFormat.CHANNEL_IN_MONO
        val audioFormat = AudioFormat.ENCODING_PCM_16BIT
        val minBufferSize = AudioRecord.getMinBufferSize(sampleRate, channelConfig, audioFormat)
        val bufferSize = Math.max(minBufferSize, 4096)

        try {
            audioRecord = AudioRecord(
                MediaRecorder.AudioSource.VOICE_RECOGNITION,
                sampleRate,
                channelConfig,
                audioFormat,
                bufferSize
            )

            if (audioRecord?.state != AudioRecord.STATE_INITIALIZED) {
                Log.e(TAG, "AudioRecord initialization failed!")
                return
            }

            audioRecord?.startRecording()
            isRecording = true

            recordingJob = scope.launch {
                val buffer = ByteArray(2048)
                val chunkStream = ByteArrayOutputStream()
                val targetChunkBytes = sampleRate * 2 * 2 // 2-second audio chunks (16kHz * 2 bytes/sample * 2s = 64KB)

                while (isActive && isRecording) {
                    val bytesRead = audioRecord?.read(buffer, 0, buffer.size) ?: 0
                    if (bytesRead > 0) {
                        chunkStream.write(buffer, 0, bytesRead)
                        if (chunkStream.size() >= targetChunkBytes) {
                            val chunkData = chunkStream.toByteArray()
                            chunkStream.reset()
                            onAudioChunkCaptured(chunkData)
                        }
                    }
                }
            }
            Log.i(TAG, "Speakerphone mic recording started (MediaRecorder.AudioSource.VOICE_RECOGNITION)")
        } catch (e: Exception) {
            Log.e(TAG, "Error starting speakerphone recording", e)
            isRecording = false
        }
    }

    fun stopRecording() {
        isRecording = false
        recordingJob?.cancel()
        try {
            audioRecord?.stop()
            audioRecord?.release()
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping AudioRecord", e)
        } finally {
            audioRecord = null
        }
        Log.i(TAG, "Speakerphone mic recording stopped.")
    }
}
