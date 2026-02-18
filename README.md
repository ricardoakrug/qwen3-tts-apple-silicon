# Qwen3-TTS for Apple Silicon

Run **Qwen3-TTS** text-to-speech locally on your Mac with Apple Silicon (M1/M2/M3/M4). No cloud services, no API keys, completely offline.

> **Fork notice:** This is a fork of [kapi2800/qwen3-tts-apple-silicon](https://github.com/kapi2800/qwen3-tts-apple-silicon) with an added non-interactive CLI (`cli.py`) for programmatic/scripted use, long-text support via sentence splitting, and bug fixes to model resolution.

---

## Features

- **Non-interactive CLI** — pass text in, get a WAV file out, no menus
- **Interactive UI** — menu-driven interface for exploration and voice enrollment
- **Voice Cloning** — clone any voice from a short audio sample
- **Voice Design** — create voices by describing them ("deep British narrator")
- **Custom Voices** — 9 built-in speakers with emotion and speed control
- **Long text support** — automatic sentence splitting so output isn't truncated
- **100% Local** — runs entirely on your Mac, no internet after model download
- **Optimized for M-Series** — uses Apple's MLX framework for fast GPU inference

---

## Quick Start

```bash
git clone https://github.com/ricardoakrug/qwen3-tts-apple-silicon.git
cd qwen3-tts-apple-silicon
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
brew install ffmpeg
```

Models download automatically from HuggingFace on first use. To pre-download them or use local copies, see [Models](#models) below.

---

## CLI Usage (`cli.py`)

The CLI is non-interactive — pass text (or a `.txt` file), get a WAV file. No playback, no menus. Designed to be called from scripts, automation, or other tools.

### Speak — Built-in voices with emotion control

```bash
python cli.py speak "Hello, this is a test"
python cli.py speak "Exciting news everyone!" --voice Vivian --emotion "Excited and happy" --speed 1.0
python cli.py speak article.txt -o ./output --filename narration
```

### Design — Describe a voice

```bash
python cli.py design "Welcome to the show" --description "A deep British male narrator"
```

### Clone — Reference audio

```bash
python cli.py clone "Text to speak in the cloned voice" --ref-audio voice.wav --ref-text "transcript of the audio"
```

### Options

All subcommands share these options:

| Option | Default | Description |
|--------|---------|-------------|
| `text` (positional) | — | Text string or path to a `.txt` file (auto-detected) |
| `-o`, `--output` | `./outputs` | Output directory |
| `--model` | `pro` | Model size: `pro` (1.7B) or `lite` (0.6B) |
| `--filename` | auto | Output filename (auto-generated from timestamp + text snippet) |

Subcommand-specific options:

| Subcommand | Option | Default |
|------------|--------|---------|
| `speak` | `--voice` | `Ryan` |
| `speak` | `--emotion` | `Calm, but speaking in a broadcaster pace` |
| `speak` | `--speed` | `1.3` |
| `design` | `--description` | *(required)* |
| `clone` | `--ref-audio` | *(required)* |
| `clone` | `--ref-text` | `.` |

### Global install

To run `tts` from anywhere instead of `python cli.py`:

```bash
# Create a wrapper script (adjust paths to your setup)
cat > ~/.local/bin/tts << 'EOF'
#!/bin/bash
exec /path/to/qwen3-tts-apple-silicon/.venv/bin/python /path/to/qwen3-tts-apple-silicon/cli.py "$@"
EOF
chmod +x ~/.local/bin/tts
```

Then use it from any directory:

```bash
tts speak "Hello world"
tts speak article.txt -o ~/Desktop
tts design "Some text" --description "A calm female narrator"
tts clone "Some text" --ref-audio ~/voices/sample.wav --ref-text "transcript"
```

---

## Interactive UI (`main.py`)

The original menu-driven interface for exploring voices, enrolling clones, and generating audio with playback.

```bash
source .venv/bin/activate
python main.py
```

```
========================================
 Qwen3-TTS Manager
========================================

  Pro Models (1.7B - Best Quality)
  ---------------------------------
  1. Custom Voice
  2. Voice Design
  3. Voice Cloning

  Lite Models (0.6B - Faster)
  ---------------------------
  4. Custom Voice
  5. Voice Cloning

  q. Exit
```

- **Custom Voice** — pick a speaker, set emotion and speed, type or paste text
- **Voice Design** — describe a voice, then generate speech with it
- **Voice Cloning** — enroll voices from audio samples, manage a voice library

---

## Models

Models download automatically from HuggingFace on first run. To use local copies instead, download them and place in the `models/` directory.

### Pro (1.7B) — Best quality

| Model | Use Case | HuggingFace |
|-------|----------|-------------|
| CustomVoice | Built-in voices + emotion | [mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit](https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit) |
| VoiceDesign | Voice from text description | [mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-8bit](https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-8bit) |
| Base | Voice cloning | [mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit](https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit) |

### Lite (0.6B) — Faster, less RAM

| Model | Use Case | HuggingFace |
|-------|----------|-------------|
| CustomVoice | Built-in voices + emotion | [mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit](https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit) |
| Base | Voice cloning | [mlx-community/Qwen3-TTS-12Hz-0.6B-Base-8bit](https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-0.6B-Base-8bit) |

> **Note:** There is no 0.6B VoiceDesign model. Running `cli.py design --model lite` will return an error.

### Local model directory structure

```
models/
├── Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit/
├── Qwen3-TTS-12Hz-1.7B-VoiceDesign-8bit/
├── Qwen3-TTS-12Hz-1.7B-Base-8bit/
├── Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit/
└── Qwen3-TTS-12Hz-0.6B-Base-8bit/
```

---

## Available Speakers

For the `speak` subcommand and Custom Voice mode in the interactive UI:

| Language | Speakers |
|----------|----------|
| English | Ryan, Aiden, Ethan, Chelsie, Serena, Vivian |
| Chinese | Vivian, Serena, Uncle_Fu, Dylan, Eric |
| Japanese | Ono_Anna |
| Korean | Sohee |

---

## Tips

- Pass a `.txt` file path as the text argument for long documents
- Long text is automatically split by sentence so audio won't be truncated
- Voice cloning works best with clean 5-10 second audio clips
- The CLI generates files only (no playback); the interactive UI plays audio via `afplay`

---

## Requirements

- macOS with Apple Silicon (M1/M2/M3/M4)
- Python 3.10+
- ffmpeg (`brew install ffmpeg`) — needed for audio conversion in voice cloning
- RAM: ~3 GB for Lite models, ~6 GB for Pro models

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `mlx_audio not found` | Run `source .venv/bin/activate` first |
| `Model not found` | Models auto-download; check your internet connection |
| Audio truncated at ~90s | Update to latest `cli.py` — long text is now split automatically |
| `--model lite` error on `design` | The 0.6B VoiceDesign model doesn't exist; use `--model pro` |

---

## Changes from Upstream

This fork adds the following on top of [kapi2800/qwen3-tts-apple-silicon](https://github.com/kapi2800/qwen3-tts-apple-silicon):

- **`cli.py`** — non-interactive CLI with `speak`, `design`, and `clone` subcommands
- **Long text support** — sentence-level splitting with joined audio output to avoid the ~90 second token limit
- **Auto-download models** — falls back to HuggingFace repo IDs when local models aren't present
- **Removed non-existent 0.6B VoiceDesign model** from the interactive menu

---

## Related Projects

- [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) — Original Qwen3-TTS by Alibaba
- [MLX Audio](https://github.com/Blaizzy/mlx-audio) — MLX framework for audio models
- [MLX Community](https://huggingface.co/mlx-community) — Pre-converted MLX models
- [kapi2800/qwen3-tts-apple-silicon](https://github.com/kapi2800/qwen3-tts-apple-silicon) — Original upstream project
