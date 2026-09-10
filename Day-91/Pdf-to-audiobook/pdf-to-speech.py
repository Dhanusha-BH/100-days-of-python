#!/usr/bin/env python3
"""
pdf_to_speech.py — Convert a PDF file's text into a spoken audio file.

Two engines are supported:

  pyttsx3 (default)
    - Fully offline, no API key, no internet connection needed.
    - Uses your OS's built-in voices (SAPI5 on Windows, NSSpeechSynthesizer
      on macOS, espeak/espeak-ng on Linux).
    - Output is .wav (or .aiff on some Mac configurations).

  gtts (Google Text-to-Speech)
    - Needs an internet connection.
    - Produces more natural-sounding voices, output is .mp3.
    - Long documents are automatically split into chunks and stitched
      together, since the Google endpoint has a practical length limit
      per request.

Install what you need:
    pip install pypdf pyttsx3        # offline engine (default)
    pip install pypdf gTTS           # online engine

Usage:
    python pdf_to_speech.py book.pdf
    python pdf_to_speech.py book.pdf -o book.wav --rate 160
    python pdf_to_speech.py book.pdf --engine gtts -o book.mp3 --lang en
    python pdf_to_speech.py book.pdf --pages 1-5,8
    python pdf_to_speech.py book.pdf --speak          # play instead of saving
    python pdf_to_speech.py --list-voices             # see available pyttsx3 voices
"""

import argparse
import re
import sys
import tempfile
from pathlib import Path


# ----------------------------------------------------------------------
# PDF text extraction
# ----------------------------------------------------------------------

def parse_page_spec(spec, total_pages):
    """Turn a spec like '1-5,8,10-12' into a sorted list of 0-based page
    indices. Page numbers in the spec are 1-based, as a person would say them."""
    if not spec:
        return list(range(total_pages))

    indices = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_str, end_str = part.split("-", 1)
            start, end = int(start_str), int(end_str)
        else:
            start = end = int(part)

        if start < 1 or end > total_pages or start > end:
            raise ValueError(
                f"Page range '{part}' is out of bounds for a {total_pages}-page PDF."
            )
        indices.update(range(start - 1, end))  # convert to 0-based

    return sorted(indices)


def extract_text(pdf_path, page_spec=None):
    try:
        from pypdf import PdfReader
    except ImportError:
        sys.exit("Missing dependency. Install it with:  pip install pypdf")

    reader = PdfReader(str(pdf_path))
    total_pages = len(reader.pages)
    if total_pages == 0:
        sys.exit("This PDF has no pages.")

    page_indices = parse_page_spec(page_spec, total_pages)

    chunks = []
    for i in page_indices:
        page_text = reader.pages[i].extract_text() or ""
        if page_text.strip():
            chunks.append(page_text)

    if not chunks:
        sys.exit(
            "No extractable text was found on the requested pages. "
            "This PDF may be scanned/image-only, which needs OCR first."
        )

    return "\n\n".join(chunks)


def clean_text(text):
    """Collapse odd whitespace and reconnect words split across a line break
    with a hyphen (a common PDF text-extraction artifact)."""
    text = re.sub(r"-\n(?=[a-z])", "", text)      # de-hyphenate line-wrapped words
    text = re.sub(r"[ \t]+", " ", text)             # collapse runs of spaces/tabs
    text = re.sub(r"\n{3,}", "\n\n", text)          # collapse excess blank lines
    return text.strip()


# ----------------------------------------------------------------------
# Offline engine: pyttsx3
# ----------------------------------------------------------------------

def list_pyttsx3_voices():
    try:
        import pyttsx3
    except ImportError:
        sys.exit("Missing dependency. Install it with:  pip install pyttsx3")

    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    if not voices:
        print("No voices found on this system.")
        return
    for v in voices:
        langs = getattr(v, "languages", None)
        print(f"- {v.name}   (id: {v.id})" + (f"   langs: {langs}" if langs else ""))


def synthesize_pyttsx3(text, output_path, rate, voice_substr, speak_only):
    try:
        import pyttsx3
    except ImportError:
        sys.exit("Missing dependency. Install it with:  pip install pyttsx3")

    engine = pyttsx3.init()
    engine.setProperty("rate", rate)

    if voice_substr:
        chosen = None
        for v in engine.getProperty("voices"):
            if voice_substr.lower() in v.name.lower():
                chosen = v.id
                break
        if chosen is None:
            sys.exit(
                f"No installed voice matched '{voice_substr}'. "
                f"Run --list-voices to see what's available."
            )
        engine.setProperty("voice", chosen)

    if speak_only:
        engine.say(text)
        engine.runAndWait()
        return

    engine.save_to_file(text, str(output_path))
    engine.runAndWait()


# ----------------------------------------------------------------------
# Online engine: gTTS
# ----------------------------------------------------------------------

def chunk_text(text, max_chars=3000):
    """Split text into chunks under max_chars, breaking on sentence
    boundaries where possible so playback doesn't cut off mid-sentence."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks, current = [], ""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_chars:
            current = f"{current} {sentence}".strip()
        else:
            if current:
                chunks.append(current)
            # A single sentence longer than max_chars: hard-split it.
            if len(sentence) > max_chars:
                for i in range(0, len(sentence), max_chars):
                    chunks.append(sentence[i:i + max_chars])
                current = ""
            else:
                current = sentence

    if current:
        chunks.append(current)
    return chunks


def synthesize_gtts(text, output_path, lang, speak_only):
    try:
        from gtts import gTTS
    except ImportError:
        sys.exit("Missing dependency. Install it with:  pip install gTTS")

    chunks = chunk_text(text)
    print(f"Synthesizing {len(chunks)} chunk(s) with gTTS (needs internet)...")

    with tempfile.TemporaryDirectory() as tmpdir:
        part_paths = []
        for i, chunk in enumerate(chunks):
            part_path = Path(tmpdir) / f"part_{i:04d}.mp3"
            gTTS(text=chunk, lang=lang).save(str(part_path))
            part_paths.append(part_path)
            print(f"  chunk {i + 1}/{len(chunks)} done")

        # MP3 files can be concatenated as raw bytes and most players will
        # handle it fine, since gTTS outputs constant-bitrate streams.
        with open(output_path, "wb") as out_file:
            for part_path in part_paths:
                out_file.write(part_path.read_bytes())

    if speak_only:
        try:
            from playsound import playsound
            playsound(str(output_path))
        except ImportError:
            print(
                f"Saved to {output_path}. Install 'playsound' "
                f"(pip install playsound) to auto-play gTTS output."
            )


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        description="Convert a PDF's text into a spoken audio file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("pdf", nargs="?", help="Path to the input PDF file")
    parser.add_argument("-o", "--output", help="Output audio file path")
    parser.add_argument(
        "--engine", choices=["pyttsx3", "gtts"], default="pyttsx3",
        help="Speech engine to use (default: pyttsx3, fully offline)"
    )
    parser.add_argument(
        "--pages", default=None,
        help="Page range, e.g. '1-5,8,10-12'. Default: all pages"
    )
    parser.add_argument(
        "--rate", type=int, default=175,
        help="Speaking rate in words/minute, pyttsx3 only (default: 175)"
    )
    parser.add_argument(
        "--voice", default=None,
        help="Substring to match an installed voice name, pyttsx3 only"
    )
    parser.add_argument(
        "--lang", default="en",
        help="Language code for gTTS, e.g. 'en', 'hi', 'es' (default: en)"
    )
    parser.add_argument(
        "--speak", action="store_true",
        help="Speak immediately instead of saving to a file"
    )
    parser.add_argument(
        "--list-voices", action="store_true",
        help="List installed pyttsx3 voices and exit"
    )
    return parser


def main():
    args = build_parser().parse_args()

    if args.list_voices:
        list_pyttsx3_voices()
        return

    if not args.pdf:
        build_parser().error("the PDF path is required unless using --list-voices")

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        sys.exit(f"File not found: {pdf_path}")

    default_ext = ".mp3" if args.engine == "gtts" else ".wav"
    output_path = Path(args.output) if args.output else pdf_path.with_suffix(default_ext)

    print(f"Reading {pdf_path.name}...")
    raw_text = extract_text(pdf_path, args.pages)
    text = clean_text(raw_text)
    word_count = len(text.split())
    print(f"Extracted {word_count} words.")

    if args.engine == "pyttsx3":
        synthesize_pyttsx3(text, output_path, args.rate, args.voice, args.speak)
    else:
        synthesize_gtts(text, output_path, args.lang, args.speak)

    if not args.speak:
        print(f"Saved audio to {output_path}")


if __name__ == "__main__":
    main()