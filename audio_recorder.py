"""
SkipBackRecorder - Recording application with skip-back feature

Audio recording module - Provides recording functionality with skip-back support

Copyright (c) 2026 Masaya Miyazaki / Office Stray Cat
All rights reserved.

Licensed under the MIT License
See LICENSE file for more details.

NOTICE: This copyright notice must be retained in all copies or
substantial portions of the software, including derivative works.

Author: Masaya Miyazaki
Organization: Office Stray Cat
Website: https://stcat.com/
Email: info@stcat.com
GitHub: https://github.com/stcatcom/SkipBackRecorder
Version: 1.0.0
"""

import numpy as np
import sounddevice as sd
import wave
import os
from datetime import datetime
from collections import deque
from PySide6.QtCore import QObject, Signal, QThread, QMutex, QMutexLocker
from config import (
    SAMPLE_RATE, CHANNELS, CHUNK_SIZE,
    SKIP_BACK_SECONDS, OUTPUT_DIR, OUTPUT_FORMAT
)


class CircularAudioBuffer:
    """Circular buffer that continuously holds audio samples"""

    def __init__(self, duration_seconds, sample_rate, channels):
        self.sample_rate = sample_rate
        self.channels = channels
        self.buffer_size = int(duration_seconds * sample_rate)
        self.buffer = deque(maxlen=self.buffer_size)
        self._mutex = QMutex()

    def add_samples(self, samples):
        """Add samples to the buffer"""
        with QMutexLocker(self._mutex):
            for sample in samples:
                self.buffer.append(sample)

    def get_buffer_contents(self):
        """Get buffer contents"""
        with QMutexLocker(self._mutex):
            contents = np.array(list(self.buffer), dtype=np.int16)
            return contents

    def clear(self):
        """Clear the buffer"""
        with QMutexLocker(self._mutex):
            self.buffer.clear()


class AudioRecorder(QObject):
    """Manages audio recording"""

    recording_started = Signal(str)  # Recording started (file path)
    recording_stopped = Signal(str)  # Recording stopped (file path)
    error_occurred = Signal(str)  # Error occurred

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_recording = False
        self._circular_buffer = CircularAudioBuffer(
            SKIP_BACK_SECONDS, SAMPLE_RATE, CHANNELS
        )
        self._recording_buffer = []
        self._current_file = None
        self._stream = None
        self._mutex = QMutex()
        self._current_level = 0.0

        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def _audio_callback(self, indata, frames, time_info, status):
        """Audio input callback"""
        if status:
            print(f"Audio callback status: {status}")

        # Convert to int16 (supports both stereo and mono)
        audio_data = (indata * 32767).astype(np.int16)

        # Calculate audio level (store in variable, no signal emission)
        self._current_level = np.abs(audio_data).mean() / 32767.0

        # Convert to interleaved format (for WAV output)
        if CHANNELS == 2:
            # Stereo: [L, R, L, R, ...] format
            audio_flat = audio_data.flatten('C')
        else:
            # Mono: as-is
            audio_flat = audio_data.flatten()

        # Always add to circular buffer
        self._circular_buffer.add_samples(audio_flat)

        # Also add to recording buffer if recording
        with QMutexLocker(self._mutex):
            if self._is_recording:
                self._recording_buffer.append(audio_flat.copy())

    def start_stream(self):
        """Start audio stream (continuous buffering)"""
        try:
            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                blocksize=CHUNK_SIZE,
                callback=self._audio_callback
            )
            self._stream.start()
        except Exception as e:
            self.error_occurred.emit(f"Stream start error: {e}")

    def stop_stream(self):
        """Stop audio stream"""
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def start_recording(self):
        """Start recording (with skip-back)"""
        with QMutexLocker(self._mutex):
            if self._is_recording:
                return

            # Generate file name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._current_file = os.path.join(
                OUTPUT_DIR, f"recording_{timestamp}.{OUTPUT_FORMAT}"
            )

            # Start recording first (callback begins adding new samples)
            self._is_recording = True
            self._recording_buffer = []

        # Get skip-back buffer contents (outside mutex)
        skip_back_data = self._circular_buffer.get_buffer_contents()

        # Insert skip-back data at the beginning
        with QMutexLocker(self._mutex):
            if len(skip_back_data) > 0:
                self._recording_buffer.insert(0, skip_back_data)

        self.recording_started.emit(self._current_file)

    def stop_recording(self):
        """Stop recording and save to file"""
        with QMutexLocker(self._mutex):
            if not self._is_recording:
                return None

            self._is_recording = False

            # Concatenate recording data
            if self._recording_buffer:
                audio_data = np.concatenate(self._recording_buffer)
            else:
                audio_data = np.array([], dtype=np.int16)

            file_path = self._current_file
            self._recording_buffer = []

        # Save to file
        if len(audio_data) > 0:
            self._save_wav(file_path, audio_data)
            self.recording_stopped.emit(file_path)
            return file_path
        else:
            self.recording_stopped.emit("")
            return None

    def _save_wav(self, file_path, audio_data):
        """Save as WAV file"""
        try:
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)  # 16bit = 2bytes
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio_data.tobytes())
        except Exception as e:
            self.error_occurred.emit(f"File save error: {e}")

    @property
    def is_recording(self):
        """Whether recording is in progress"""
        return self._is_recording

    @property
    def current_level(self):
        """Get current audio level"""
        return self._current_level


class AudioRecorderThread(QThread):
    """Recording thread"""

    recording_started = Signal(str)
    recording_stopped = Signal(str)
    level_changed = Signal(float)
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._recorder = None
        self._start_requested = False
        self._stop_requested = False
        self._mutex = QMutex()

    def run(self):
        """Thread execution"""
        self._recorder = AudioRecorder()

        # Forward signals
        self._recorder.recording_started.connect(self.recording_started.emit)
        self._recorder.recording_stopped.connect(self.recording_stopped.emit)
        self._recorder.error_occurred.connect(self.error_occurred.emit)

        # Start stream
        self._recorder.start_stream()

        # Wait until thread is interrupted
        while not self.isInterruptionRequested():
            with QMutexLocker(self._mutex):
                if self._start_requested:
                    self._recorder.start_recording()
                    self._start_requested = False
                if self._stop_requested:
                    self._recorder.stop_recording()
                    self._stop_requested = False

            # Get audio level and emit signal (from this thread)
            level = self._recorder.current_level
            self.level_changed.emit(level)

            self.msleep(30)  # 約33fps でレベル更新

        # Stop recording if in progress
        if self._recorder.is_recording:
            self._recorder.stop_recording()

        self._recorder.stop_stream()

    def request_start_recording(self):
        """Request to start recording"""
        with QMutexLocker(self._mutex):
            self._start_requested = True

    def request_stop_recording(self):
        """Request to stop recording"""
        with QMutexLocker(self._mutex):
            self._stop_requested = True

    def stop(self):
        """Stop the thread"""
        self.requestInterruption()
        self.wait()
