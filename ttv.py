import os
import sys
from pathlib import Path

from parser import parse
from pipeline import Pipeline
from schemas import SlideData
from thread_task_logics.voice_actor_task_logic import KokoroProvider

if __name__ == "__main__":
    # Ensure that it takes exactly 1 input.
    if not len(sys.argv) == 2:
        print("usage: ttv.py <input.txt>", file=sys.stderr)
        sys.exit(1)

    # Ensure given input path exists.
    given_text_input_path = Path(sys.argv[1])
    if not given_text_input_path.exists():
        print(f"error: file not found: {given_text_input_path}", file=sys.stderr)
        sys.exit(1)

    # Use absolute paths.
    absolute_text_input_path = given_text_input_path.resolve()
    absolute_video_output_path = absolute_text_input_path.with_suffix(".mp4")

    # DTO validation on the given text file.
    slides: list[SlideData] = parse(absolute_text_input_path)

    # Resolve kokoro provider. It may be present or absent.
    kokoro_url = os.environ.get("KOKORO_URL")
    kokoro_provider = KokoroProvider(kokoro_url) if kokoro_url else None
    if kokoro_provider:
        print(f"Kokoro provider found at {kokoro_url}")
    else:
        print("No Kokoro provider found")

    # Global error boundary to catch if anything goes wrong in pipeline.
    try:
        pipeline = Pipeline(
            slides,
            absolute_video_output_path,
            kokoro_provider,
        )
        pipeline.run_threads()
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
