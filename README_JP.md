# SkipBackRecorder

スキップバック機能付き録音アプリケーション

## 概要

SkipBackRecorderは、録音開始ボタンを押す**前**の音声も録音できる「スキップバック録音」機能を備えたWindows向け録音アプリケーションです。

「あ、今の録音しておけばよかった！」という場面でも、設定した秒数分だけ遡って録音を開始できます。

## 主な機能

- **スキップバック録音** - 録音開始時に、指定秒数前からの音声を含めて録音
- **リアルタイム音声レベル表示** - 入力音声のレベルをリアルタイムで確認
- **シンプルなUI** - ワンクリック（またはインジケータークリック）で録音開始/停止
- **録音履歴表示** - 録音したファイルの履歴を表示

## スクリーンショット

![SkipBackRecorder](screenshot.png)

## 動作環境

- Windows 10/11
- Python 3.10以上

## ファイル構成

```
SkipBackRecorder/
├── main.py           # メインアプリケーション
├── audio_recorder.py # 録音モジュール
├── ui_main.py        # UIモジュール
├── config.py         # 設定ファイル
├── requirements.txt  # 依存パッケージ
├── LICENSE.txt       # MITライセンス
├── README.md         # 英語版ドキュメント
├── README_JP.md      # 日本語版ドキュメント（このファイル）
├── SETUP.md          # セットアップガイド
├── screenshot.png    # スクリーンショット
└── rec/              # 録音ファイル保存先（自動作成）
```

## 設定項目

`config.py` で以下の設定を変更できます：

| 項目 | デフォルト値 | 説明 |
|------|-------------|------|
| `SAMPLE_RATE` | 44100 | サンプリングレート (Hz) |
| `CHANNELS` | 2 | チャンネル数 (1=モノラル, 2=ステレオ) |
| `SKIP_BACK_SECONDS` | 2 | スキップバック秒数 |
| `OUTPUT_DIR` | ./rec | 録音ファイル保存先 |

### メモリ消費量の目安

スキップバック秒数によるメモリ消費量（安全見積もり）：

| 秒数 | メモリ消費量 |
|------|-------------|
| 2秒 | 約 700 KB |
| 5秒 | 約 1.7 MB |
| 10秒 | 約 3.4 MB |
| 30秒 | 約 10 MB |

## クイックスタート

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# 起動
python main.py

# コンソールウィンドウなしで起動（GUI利用時に推奨）
pythonw main.py
```

詳細なセットアップ手順は [SETUP.md](SETUP.md) を参照してください。

## 使い方

1. アプリケーションを起動
2. 音声レベルメーターで入力を確認
3. 「Start Recording」ボタンまたは録音インジケータをクリックして録音開始
4. 再度クリックして録音停止
5. 録音ファイルは `rec/` フォルダに保存されます

## ライセンス

MIT License

Copyright (c) 2026 Masaya Miyazaki / Office Stray Cat

詳細は [LICENSE.txt](LICENSE.txt) を参照してください。

## 作者

- **Author:** Masaya Miyazaki
- **Organization:** Office Stray Cat
- **Website:** https://stcat.com/
- **Email:** info@stcat.com
- **GitHub:** https://github.com/stcatcom/SkipBackRecorder

## サポート

このプロジェクトが役に立った場合は、開発の支援をご検討ください：

[![PayPal](https://img.shields.io/badge/PayPal-Donate-blue.svg)](https://paypal.me/stcatcom?locale.x=ja_JP&country.x=JP)
