#!/usr/bin/env python3
"""
SkipBackRecorder - スキップバック機能付き録音アプリケーション

メインアプリケーション

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

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Slot

from ui_main import MainWindow
from audio_recorder import AudioRecorderThread


class RecordingServer:
    """録音サーバアプリケーション"""

    def __init__(self):
        self._app = QApplication(sys.argv)
        self._window = MainWindow()

        # 録音スレッド
        self._audio_thread = AudioRecorderThread()

        # シグナル接続
        self._connect_signals()

    def _connect_signals(self):
        """シグナルを接続"""
        # 録音 -> UI
        self._audio_thread.recording_started.connect(
            self._window.on_recording_started
        )
        self._audio_thread.recording_stopped.connect(
            self._window.on_recording_stopped
        )
        self._audio_thread.level_changed.connect(
            self._window.on_level_changed
        )
        self._audio_thread.error_occurred.connect(
            self._window.on_error_occurred
        )

        # 録音ボタン
        record_btn = self._window.get_record_button()
        record_btn.toggled.connect(self._on_record_toggled)

    @Slot(bool)
    def _on_record_toggled(self, checked):
        """録音ボタンのトグル処理"""
        if checked:
            self._audio_thread.request_start_recording()
        else:
            self._audio_thread.request_stop_recording()

    def run(self):
        """アプリケーションを実行"""
        # 録音スレッド開始
        self._audio_thread.start()

        # ウィンドウ表示
        self._window.show()

        # イベントループ実行
        result = self._app.exec()

        # クリーンアップ
        self._cleanup()

        return result

    def _cleanup(self):
        """リソースを解放"""
        self._audio_thread.stop()


def main():
    """エントリーポイント"""
    server = RecordingServer()
    sys.exit(server.run())


if __name__ == "__main__":
    main()
