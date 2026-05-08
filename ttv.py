import sys
from pathlib import Path
from pipeline import run

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: ttv.py <input.txt>", file=sys.stderr)
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if input_path.suffix != ".txt":
        print(f"error: expected a .txt file, got: {input_path.suffix}", file=sys.stderr)
        sys.exit(1)

    try:
        run(input_path)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
