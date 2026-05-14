import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from parser import parse
from pipeline import Pipeline
from schemas import SlideData
from thread_task_logics.voice_actor_task_logic import ElevenLabsProvider, PiperProvider

def main() -> None:
    load_dotenv()

    if not len(sys.argv) == 2:
        print("Usage: ttv <input.txt>", file=sys.stderr)
        sys.exit(1)

    given_text_file_path = Path(sys.argv[1])
    if not given_text_file_path.exists():
        print(f"File not found: {given_text_file_path}", file=sys.stderr)
        sys.exit(1)

    given_text_file_absolute_path = given_text_file_path.resolve()
    video_output_absolute_path = given_text_file_absolute_path.with_suffix(".mp4")

    slides: list[SlideData] = parse(given_text_file_absolute_path)

    piper_model = os.environ.get("PIPER_MODEL")
    eleven_labs_api_key = os.environ.get("ELEVEN_LABS_API_KEY")
    voice_id = os.environ.get("VOICE_ID")

    if piper_model:
        provider = PiperProvider(piper_model)
        print(f"Piper provider loaded ({Path(piper_model).name})")
    elif eleven_labs_api_key and voice_id:
        provider = ElevenLabsProvider(eleven_labs_api_key, voice_id)
        print(f"ElevenLabs provider found (voice: {voice_id})")
    else:
        provider = None
        print("No voice provider found, running silent")

    try:
        pipeline = Pipeline(slides, video_output_absolute_path, provider)
        pipeline.run_threads()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
