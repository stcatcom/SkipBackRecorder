#!/usr/bin/env python3
"""
SkipBackRecorder - Recording application with skip-back feature

Main application

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
    """Recording server application"""

    def __init__(self):
        self._app = QApplication(sys.argv)
        self._window = MainWindow()

        # Recording thread
        self._audio_thread = AudioRecorderThread()

        # Connect signals
        self._connect_signals()

    def _connect_signals(self):
        """Connect signals"""
        # Recording -> UI
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

        # Record button
        record_btn = self._window.get_record_button()
        record_btn.toggled.connect(self._on_record_toggled)

    @Slot(bool)
    def _on_record_toggled(self, checked):
        """Handle record button toggle"""
        if checked:
            self._audio_thread.request_start_recording()
        else:
            self._audio_thread.request_stop_recording()

    def run(self):
        """Run the application"""
        # Start recording thread
        self._audio_thread.start()

        # Show window
        self._window.show()

        # Run event loop
        result = self._app.exec()

        # Cleanup
        self._cleanup()

        return result

    def _cleanup(self):
        """Release resources"""
        self._audio_thread.stop()


def main():
    """Entry point"""
    server = RecordingServer()
    sys.exit(server.run())


if __name__ == "__main__":
    main()
