#!/usr/bin/env python3
"""Non-interactive CLI for Qwen3-TTS on Apple Silicon."""

import argparse
import os
import re
import shutil
import sys
import time
import warnings
from datetime import datetime

os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

MODEL_MAP = {
    "speak": {
        "pro": "Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit",
        "lite": "Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit",
    },
    "design": {
        "pro": "Qwen3-TTS-12Hz-1.7B-VoiceDesign-8bit",
    },
    "clone": {
        "pro": "Qwen3-TTS-12Hz-1.7B-Base-8bit",
        "lite": "Qwen3-TTS-12Hz-0.6B-Base-8bit",
    },
}


def get_smart_path(folder_name):
    full_path = os.path.join(MODELS_DIR, folder_name)
    if not os.path.exists(full_path):
        return f"mlx-community/{folder_name}"
    snapshots_dir = os.path.join(full_path, "snapshots")
    if os.path.exists(snapshots_dir):
        subfolders = [f for f in os.listdir(snapshots_dir) if not f.startswith(".")]
        if subfolders:
            return os.path.join(snapshots_dir, subfolders[0])
    return full_path


def resolve_text(text_arg):
    if os.path.isfile(text_arg) and text_arg.endswith(".txt"):
        with open(text_arg, "r", encoding="utf-8") as f:
            return f.read().strip()
    return text_arg


def split_into_chunks(text):
    """Split text into sentence-separated chunks joined by newlines.

    generate_audio splits on '\\n' and processes each segment independently,
    then join_audio=True stitches them into one file. This avoids hitting
    the per-segment token limit (~96s of audio at 12.5 Hz) on long texts.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return "\n".join(s.strip() for s in sentences if s.strip())


def make_filename(text):
    timestamp = datetime.now().strftime("%H-%M-%S")
    snippet = re.sub(r"[^\w\s-]", "", text)[:20].strip().replace(" ", "_") or "audio"
    return f"{timestamp}_{snippet}.wav"


def generate(args, mode):
    try:
        from mlx_audio.tts.utils import load_model
        from mlx_audio.tts.generate import generate_audio
    except ImportError:
        print("Error: mlx_audio not found. Activate the venv first.", file=sys.stderr)
        sys.exit(1)

    folder = MODEL_MAP[mode].get(args.model)
    if folder is None:
        print(f"Error: --model {args.model} is not available for '{mode}'.", file=sys.stderr)
        sys.exit(1)

    text = resolve_text(args.text)
    if not text:
        print("Error: empty text input.", file=sys.stderr)
        sys.exit(1)

    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)

    model_path = get_smart_path(folder)
    print(f"Loading model: {folder}")
    model = load_model(model_path)

    text = split_into_chunks(text)

    temp_dir = f"temp_cli_{int(time.time())}"
    print("Generating audio...")

    common = dict(
        model=model,
        text=text,
        output_path=temp_dir,
        join_audio=True,
        max_tokens=4096,
    )

    if mode == "speak":
        generate_audio(
            **common,
            voice=args.voice,
            instruct=args.emotion,
            speed=args.speed,
        )
    elif mode == "design":
        generate_audio(
            **common,
            instruct=args.description,
        )
    elif mode == "clone":
        ref_audio = os.path.abspath(args.ref_audio)
        if not os.path.isfile(ref_audio):
            print(f"Error: reference audio not found: {ref_audio}", file=sys.stderr)
            sys.exit(1)
        generate_audio(
            **common,
            ref_audio=ref_audio,
            ref_text=args.ref_text,
        )

    # join_audio=True produces "audio.wav"; without it, "audio_000.wav"
    source = os.path.join(temp_dir, "audio.wav")
    if not os.path.exists(source):
        source = os.path.join(temp_dir, "audio_000.wav")
    if not os.path.exists(source):
        print("Error: generation produced no output.", file=sys.stderr)
        shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(1)

    filename = args.filename if args.filename else make_filename(text)
    if not filename.endswith(".wav"):
        filename += ".wav"
    dest = os.path.join(output_dir, filename)
    shutil.move(source, dest)
    shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"Saved: {dest}")


def main():
    parser = argparse.ArgumentParser(
        description="Qwen3-TTS CLI — generate speech from text"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # -- speak (custom voice) --
    sp = sub.add_parser("speak", help="Generate with a built-in speaker voice")
    sp.add_argument("text", help="Text to speak, or path to a .txt file")
    sp.add_argument("--voice", default="Ryan", help="Speaker name (default: Ryan)")
    sp.add_argument("--emotion", default="Calm, but speaking in a broadcaster pace", help="Emotion instruction")
    sp.add_argument("--speed", type=float, default=1.3, help="Speed multiplier (default: 1.3)")

    # -- design (voice design) --
    dp = sub.add_parser("design", help="Generate with a described voice")
    dp.add_argument("text", help="Text to speak, or path to a .txt file")
    dp.add_argument("--description", required=True, help="Describe the voice to synthesize")

    # -- clone (voice cloning) --
    cp = sub.add_parser("clone", help="Clone a voice from reference audio")
    cp.add_argument("text", help="Text to speak, or path to a .txt file")
    cp.add_argument("--ref-audio", required=True, help="Path to reference audio file")
    cp.add_argument("--ref-text", default=".", help="Transcript of the reference audio")

    # common options
    for p in (sp, dp, cp):
        p.add_argument("-o", "--output", default="./outputs", help="Output directory (default: ./outputs)")
        p.add_argument("--model", choices=["pro", "lite"], default="pro", help="Model size (default: pro)")
        p.add_argument("--filename", default=None, help="Output filename (default: auto-generated)")

    args = parser.parse_args()
    generate(args, args.command)


if __name__ == "__main__":
    main()
