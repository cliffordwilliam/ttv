import sys
import os
from pathlib import Path
from pipeline import run
from voice import KokoroProvider

if __name__ == "__main__":
    if not len(sys.argv) == 2:
        print("usage: ttv.py <input.txt>", file=sys.stderr)
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    kokoro_url = os.environ.get("KOKORO_URL")
    voice = KokoroProvider(kokoro_url) if kokoro_url else None
    if voice:
        print(f"Voice provider: Kokoro at {kokoro_url}")

    try:
        _ = run(input_path, voice=voice)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
