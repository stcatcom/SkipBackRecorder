"""
SkipBackRecorder - スキップバック機能付き録音アプリケーション

録音モジュール - スキップバック録音に対応した録音機能を提供

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
    """循環バッファで常時音声を保持するクラス"""

    def __init__(self, duration_seconds, sample_rate, channels):
        self.sample_rate = sample_rate
        self.channels = channels
        self.buffer_size = int(duration_seconds * sample_rate)
        self.buffer = deque(maxlen=self.buffer_size)
        self._mutex = QMutex()

    def add_samples(self, samples):
        """サンプルをバッファに追加"""
        with QMutexLocker(self._mutex):
            for sample in samples:
                self.buffer.append(sample)

    def get_buffer_contents(self):
        """バッファの内容を取得してクリア"""
        with QMutexLocker(self._mutex):
            contents = np.array(list(self.buffer), dtype=np.int16)
            return contents

    def clear(self):
        """バッファをクリア"""
        with QMutexLocker(self._mutex):
            self.buffer.clear()


class AudioRecorder(QObject):
    """録音を管理するクラス"""

    # シグナル定義
    recording_started = Signal(str)  # 録音開始 (ファイルパス)
    recording_stopped = Signal(str)  # 録音停止 (ファイルパス)
    error_occurred = Signal(str)  # エラー発生

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
        self._current_level = 0.0  # 現在の音声レベル

        # 出力ディレクトリを作成
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def _audio_callback(self, indata, frames, time_info, status):
        """音声入力コールバック"""
        if status:
            print(f"Audio callback status: {status}")

        # int16に変換（ステレオ/モノラル両対応）
        audio_data = (indata * 32767).astype(np.int16)

        # 音声レベルを計算（シグナルは発行せず変数に保存）
        self._current_level = np.abs(audio_data).mean() / 32767.0

        # インターリーブ形式に変換（WAV保存用）
        if CHANNELS == 2:
            # ステレオ: [L, R, L, R, ...] の形式に
            audio_flat = audio_data.flatten('C')
        else:
            # モノラル: そのまま
            audio_flat = audio_data.flatten()

        # 循環バッファに追加（常時）
        self._circular_buffer.add_samples(audio_flat)

        # 録音中なら録音バッファにも追加
        with QMutexLocker(self._mutex):
            if self._is_recording:
                self._recording_buffer.append(audio_flat.copy())

    def start_stream(self):
        """音声ストリームを開始（常時バッファリング）"""
        try:
            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                blocksize=CHUNK_SIZE,
                callback=self._audio_callback
            )
            self._stream.start()
        except Exception as e:
            self.error_occurred.emit(f"ストリーム開始エラー: {e}")

    def stop_stream(self):
        """音声ストリームを停止"""
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def start_recording(self):
        """録音を開始（スキップバック込み）"""
        with QMutexLocker(self._mutex):
            if self._is_recording:
                return

            # ファイル名を生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._current_file = os.path.join(
                OUTPUT_DIR, f"recording_{timestamp}.{OUTPUT_FORMAT}"
            )

            # 先に録音開始（コールバックが新しいサンプルを追加開始）
            self._is_recording = True
            self._recording_buffer = []

        # スキップバックバッファの内容を取得（mutexの外で）
        skip_back_data = self._circular_buffer.get_buffer_contents()

        # スキップバックデータを先頭に挿入
        with QMutexLocker(self._mutex):
            if len(skip_back_data) > 0:
                self._recording_buffer.insert(0, skip_back_data)

        self.recording_started.emit(self._current_file)

    def stop_recording(self):
        """録音を停止してファイルに保存"""
        with QMutexLocker(self._mutex):
            if not self._is_recording:
                return None

            self._is_recording = False

            # 録音データを結合
            if self._recording_buffer:
                audio_data = np.concatenate(self._recording_buffer)
            else:
                audio_data = np.array([], dtype=np.int16)

            file_path = self._current_file
            self._recording_buffer = []

        # ファイルに保存
        if len(audio_data) > 0:
            self._save_wav(file_path, audio_data)
            self.recording_stopped.emit(file_path)
            return file_path
        else:
            self.recording_stopped.emit("")
            return None

    def _save_wav(self, file_path, audio_data):
        """WAVファイルとして保存"""
        try:
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)  # 16bit = 2bytes
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio_data.tobytes())
        except Exception as e:
            self.error_occurred.emit(f"ファイル保存エラー: {e}")

    @property
    def is_recording(self):
        """録音中かどうか"""
        return self._is_recording

    @property
    def current_level(self):
        """現在の音声レベルを取得"""
        return self._current_level


class AudioRecorderThread(QThread):
    """録音用のスレッド"""

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
        """スレッド実行"""
        self._recorder = AudioRecorder()

        # シグナルを転送
        self._recorder.recording_started.connect(self.recording_started.emit)
        self._recorder.recording_stopped.connect(self.recording_stopped.emit)
        self._recorder.error_occurred.connect(self.error_occurred.emit)

        # ストリーム開始
        self._recorder.start_stream()

        # スレッドが停止されるまで待機
        while not self.isInterruptionRequested():
            with QMutexLocker(self._mutex):
                if self._start_requested:
                    self._recorder.start_recording()
                    self._start_requested = False
                if self._stop_requested:
                    self._recorder.stop_recording()
                    self._stop_requested = False

            # 音声レベルを取得してシグナル発行（このスレッドから）
            level = self._recorder.current_level
            self.level_changed.emit(level)

            self.msleep(30)  # 約33fps でレベル更新

        # 録音中なら停止
        if self._recorder.is_recording:
            self._recorder.stop_recording()

        self._recorder.stop_stream()

    def request_start_recording(self):
        """録音開始をリクエスト"""
        with QMutexLocker(self._mutex):
            self._start_requested = True

    def request_stop_recording(self):
        """録音停止をリクエスト"""
        with QMutexLocker(self._mutex):
            self._stop_requested = True

    def stop(self):
        """スレッドを停止"""
        self.requestInterruption()
        self.wait()
