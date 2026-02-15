"""
SkipBackRecorder - Recording application with skip-back feature

PySide6 Main UI - Status display and control interface

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

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QListWidget,
    QGroupBox, QFrame
)
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QFont, QPalette, QColor, QCursor
from config import SKIP_BACK_SECONDS, OUTPUT_DIR


class StatusIndicator(QFrame):
    """Status indicator widget (clickable)"""

    clicked = Signal()

    def __init__(self, label_text, clickable=False, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 80)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(2)
        self._clickable = clickable

        if clickable:
            self.setCursor(QCursor(Qt.PointingHandCursor))

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self._indicator = QLabel("●")
        self._indicator.setAlignment(Qt.AlignCenter)
        self._indicator.setFont(QFont("Arial", 24))
        self._set_color("gray")

        self._label = QLabel(label_text)
        self._label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self._indicator)
        layout.addWidget(self._label)

    def _set_color(self, color):
        """Set indicator color"""
        self._indicator.setStyleSheet(f"color: {color};")

    def set_recording(self, recording):
        """Set recording state"""
        if recording:
            self._set_color("red")
        else:
            self._set_color("gray")

    def mousePressEvent(self, event):
        """Handle mouse press event"""
        if self._clickable and event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    """Main window"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SkipBack Recorder")
        self.setMinimumSize(500, 400)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Status group
        status_group = QGroupBox("Status")
        status_layout = QHBoxLayout(status_group)

        # Recording indicator (click to start/stop recording)
        self._rec_indicator = StatusIndicator("REC", clickable=True)
        self._rec_indicator.clicked.connect(self._on_indicator_clicked)
        status_layout.addWidget(self._rec_indicator)

        # Status text
        status_text_layout = QVBoxLayout()
        self._status_label = QLabel("Standby")
        self._status_label.setFont(QFont("Arial", 14))
        self._skip_back_label = QLabel(f"Skip Back: {SKIP_BACK_SECONDS}s")
        status_text_layout.addWidget(self._status_label)
        status_text_layout.addWidget(self._skip_back_label)
        status_layout.addLayout(status_text_layout)
        status_layout.addStretch()

        main_layout.addWidget(status_group)

        # Audio level group
        level_group = QGroupBox("Audio Level")
        level_layout = QVBoxLayout(level_group)

        self._level_bar = QProgressBar()
        self._level_bar.setRange(0, 100)
        self._level_bar.setValue(0)
        self._level_bar.setTextVisible(False)
        self._level_bar.setFixedHeight(25)
        level_layout.addWidget(self._level_bar)

        main_layout.addWidget(level_group)

        # Recording history group
        history_group = QGroupBox("Recording History")
        history_layout = QVBoxLayout(history_group)

        self._history_list = QListWidget()
        history_layout.addWidget(self._history_list)

        self._output_dir_label = QLabel(f"Output: {OUTPUT_DIR}")
        self._output_dir_label.setStyleSheet("color: gray;")
        history_layout.addWidget(self._output_dir_label)

        main_layout.addWidget(history_group)

        # Control buttons
        button_layout = QHBoxLayout()

        self._record_btn = QPushButton("Start Recording")
        self._record_btn.setCheckable(True)
        self._record_btn.setMinimumHeight(40)
        self._record_btn.toggled.connect(self._on_record_toggled)
        button_layout.addWidget(self._record_btn)

        self._clear_history_btn = QPushButton("Clear History")
        self._clear_history_btn.clicked.connect(self._clear_history)
        button_layout.addWidget(self._clear_history_btn)

        button_layout.addStretch()

        main_layout.addLayout(button_layout)

    def _on_record_toggled(self, checked):
        """Update button text on toggle"""
        if checked:
            self._record_btn.setText("Stop Recording")
        else:
            self._record_btn.setText("Start Recording")

    def _on_indicator_clicked(self):
        """Handle indicator click (toggle record button)"""
        self._record_btn.toggle()

    @Slot(str)
    def on_recording_started(self, file_path):
        """Handle recording started"""
        self._rec_indicator.set_recording(True)
        self._status_label.setText("Recording...")
        self._status_label.setStyleSheet("color: red;")
        self._record_btn.setChecked(True)

    @Slot(str)
    def on_recording_stopped(self, file_path):
        """Handle recording stopped"""
        self._rec_indicator.set_recording(False)
        self._status_label.setText("Standby")
        self._status_label.setStyleSheet("color: black;")
        self._record_btn.setChecked(False)

        if file_path:
            import os
            filename = os.path.basename(file_path)
            self._history_list.insertItem(0, filename)

    @Slot(float)
    def on_level_changed(self, level):
        """Handle audio level change"""
        self._level_bar.setValue(int(level * 100))

    @Slot(str)
    def on_error_occurred(self, error_msg):
        """Handle error"""
        self._status_label.setText(f"Error: {error_msg}")
        self._status_label.setStyleSheet("color: orange;")

    def _clear_history(self):
        """Clear recording history"""
        self._history_list.clear()

    def get_record_button(self):
        """Get the record button widget"""
        return self._record_btn
