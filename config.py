"""
録音サーバ設定ファイル
Windows対応版
"""

# 録音設定
SAMPLE_RATE = 44100  # サンプリングレート (Hz)
CHANNELS = 2  # ステレオ
CHUNK_SIZE = 2048  # バッファサイズ
AUDIO_FORMAT = 'int16'  # 音声フォーマット
SKIP_BACK_SECONDS = 2  # スキップバック秒数

# 出力設定
OUTPUT_DIR = './rec'  # 録音ファイル保存先
OUTPUT_FORMAT = 'wav'  # 出力フォーマット
