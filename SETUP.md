# SkipBackRecorder セットアップガイド

## 動作要件

- **OS:** Windows 10/11
- **Python:** 3.10以上
- **オーディオデバイス:** マイクまたはライン入力

## セットアップ手順

### 1. Pythonのインストール

Pythonがインストールされていない場合は、公式サイトからダウンロードしてインストールしてください。

https://www.python.org/downloads/

インストール時に「Add Python to PATH」にチェックを入れてください。

インストール確認：
```bash
python --version
```

### 2. プロジェクトのダウンロード

**方法A: Gitでクローン**
```bash
git clone https://github.com/stcatcom/SkipBackRecorder.git
```

**方法B: ZIPダウンロード**

GitHubページからZIPファイルをダウンロードして展開してください。

### 3. 依存パッケージのインストール

プロジェクトフォルダに移動し、必要なパッケージをインストールします：

```bash
cd SkipBackRecorder
pip install -r requirements.txt
```

インストールされるパッケージ：
- **PySide6** - GUIフレームワーク
- **sounddevice** - オーディオ入出力
- **numpy** - 数値計算

### 4. 設定の確認・変更

`config.py` を編集して設定を変更できます：

```python
# 録音設定
SAMPLE_RATE = 44100      # サンプリングレート (Hz)
CHANNELS = 2             # ステレオ
SKIP_BACK_SECONDS = 2    # スキップバック秒数

# 出力設定
OUTPUT_DIR = './rec'     # 録音ファイル保存先
```

### 5. 起動

```bash
python main.py
```

## トラブルシューティング

### 音声が入力されない

1. **オーディオデバイスの確認**
   - Windowsのサウンド設定で録音デバイスが正しく選択されているか確認
   - デバイスのレベルがミュートになっていないか確認

2. **デフォルトデバイスの確認**
   ```bash
   python -c "import sounddevice; print(sounddevice.query_devices())"
   ```

### PySide6のインストールエラー

Visual C++ 再頒布可能パッケージが必要な場合があります：
https://aka.ms/vs/17/release/vc_redist.x64.exe

### sounddeviceのインストールエラー

PortAudioが必要です。通常はsounddeviceと一緒にインストールされますが、
問題がある場合は以下を試してください：

```bash
pip install --upgrade sounddevice
```

## アンインストール

プロジェクトフォルダを削除してください。

インストールしたパッケージも削除する場合：
```bash
pip uninstall PySide6 sounddevice numpy
```

## アップデート

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## お問い合わせ

- **GitHub Issues:** https://github.com/stcatcom/SkipBackRecorder/issues
- **Email:** info@stcat.com
