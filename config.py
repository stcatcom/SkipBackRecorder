"""
Recording server configuration
Windows compatible
"""

# Recording settings
SAMPLE_RATE = 44100  # Sample rate (Hz)
CHANNELS = 2  # Stereo
CHUNK_SIZE = 2048  # Buffer size
AUDIO_FORMAT = 'int16'  # Audio format
SKIP_BACK_SECONDS = 2  # Skip-back duration (seconds)

# Output settings
OUTPUT_DIR = './rec'  # Recording file output directory
OUTPUT_FORMAT = 'wav'  # Output format
