"""
SkipBackRecorder - スキップバック機能付き録音アプリケーション

PySide6 メインUI - 状態表示と操作インターフェース

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
    """状態インジケータウィジェット（クリック可能）"""

    clicked = Signal()  # クリック時のシグナル

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
        """インジケータの色を設定"""
        self._indicator.setStyleSheet(f"color: {color};")

    def set_recording(self, recording):
        """録音状態を設定"""
        if recording:
            self._set_color("red")
        else:
            self._set_color("gray")

    def mousePressEvent(self, event):
        """クリック時の処理"""
        if self._clickable and event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    """メインウィンドウ"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("スキップバックレコーダー")
        self.setMinimumSize(500, 400)

        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # ステータスグループ
        status_group = QGroupBox("ステータス")
        status_layout = QHBoxLayout(status_group)

        # 録音インジケータ（クリックで録音開始/停止）
        self._rec_indicator = StatusIndicator("録音", clickable=True)
        self._rec_indicator.clicked.connect(self._on_indicator_clicked)
        status_layout.addWidget(self._rec_indicator)

        # ステータステキスト
        status_text_layout = QVBoxLayout()
        self._status_label = QLabel("待機中")
        self._status_label.setFont(QFont("Arial", 14))
        self._skip_back_label = QLabel(f"スキップバック: {SKIP_BACK_SECONDS}秒")
        status_text_layout.addWidget(self._status_label)
        status_text_layout.addWidget(self._skip_back_label)
        status_layout.addLayout(status_text_layout)
        status_layout.addStretch()

        main_layout.addWidget(status_group)

        # 音声レベルグループ
        level_group = QGroupBox("音声レベル")
        level_layout = QVBoxLayout(level_group)

        self._level_bar = QProgressBar()
        self._level_bar.setRange(0, 100)
        self._level_bar.setValue(0)
        self._level_bar.setTextVisible(False)
        self._level_bar.setFixedHeight(25)
        level_layout.addWidget(self._level_bar)

        main_layout.addWidget(level_group)

        # 録音履歴グループ
        history_group = QGroupBox("録音履歴")
        history_layout = QVBoxLayout(history_group)

        self._history_list = QListWidget()
        history_layout.addWidget(self._history_list)

        self._output_dir_label = QLabel(f"保存先: {OUTPUT_DIR}")
        self._output_dir_label.setStyleSheet("color: gray;")
        history_layout.addWidget(self._output_dir_label)

        main_layout.addWidget(history_group)

        # 操作ボタン
        button_layout = QHBoxLayout()

        self._record_btn = QPushButton("録音開始")
        self._record_btn.setCheckable(True)
        self._record_btn.setMinimumHeight(40)
        self._record_btn.toggled.connect(self._on_record_toggled)
        button_layout.addWidget(self._record_btn)

        self._clear_history_btn = QPushButton("履歴クリア")
        self._clear_history_btn.clicked.connect(self._clear_history)
        button_layout.addWidget(self._clear_history_btn)

        button_layout.addStretch()

        main_layout.addLayout(button_layout)

    def _on_record_toggled(self, checked):
        """録音ボタンのトグル時にボタンテキストを更新"""
        if checked:
            self._record_btn.setText("録音停止")
        else:
            self._record_btn.setText("録音開始")

    def _on_indicator_clicked(self):
        """インジケータクリック時の処理（録音ボタンをトグル）"""
        self._record_btn.toggle()

    @Slot(str)
    def on_recording_started(self, file_path):
        """録音開始時の処理"""
        self._rec_indicator.set_recording(True)
        self._status_label.setText("録音中...")
        self._status_label.setStyleSheet("color: red;")
        self._record_btn.setChecked(True)

    @Slot(str)
    def on_recording_stopped(self, file_path):
        """録音停止時の処理"""
        self._rec_indicator.set_recording(False)
        self._status_label.setText("待機中")
        self._status_label.setStyleSheet("color: black;")
        self._record_btn.setChecked(False)

        if file_path:
            # ファイル名のみを表示
            import os
            filename = os.path.basename(file_path)
            self._history_list.insertItem(0, filename)

    @Slot(float)
    def on_level_changed(self, level):
        """音声レベル変化時の処理"""
        # 0.0-1.0 を 0-100 に変換
        self._level_bar.setValue(int(level * 100))

    @Slot(str)
    def on_error_occurred(self, error_msg):
        """エラー発生時の処理"""
        self._status_label.setText(f"エラー: {error_msg}")
        self._status_label.setStyleSheet("color: orange;")

    def _clear_history(self):
        """履歴をクリア"""
        self._history_list.clear()

    def get_record_button(self):
        """録音ボタンを取得"""
        return self._record_btn
