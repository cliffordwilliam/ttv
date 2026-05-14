import json
import subprocess
import urllib.request
import wave
from pathlib import Path

from config import VOICE_SIMILARITY_BOOST, VOICE_SPEED, VOICE_STABILITY, VOICE_STYLE
from schemas import SlideData


class ElevenLabsProvider:
    audio_suffix = ".mp3"

    def __init__(self, api_key: str, voice_id: str):
        self.api_key = api_key
        self.voice_id = voice_id

    def synthesize(
        self,
        slide_data: SlideData,
        audio_path: Path,
        previous_text: str | None = None,
        next_text: str | None = None,
    ) -> float:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}?output_format=mp3_44100_128"
        body: dict = {
            "text": slide_data.voice_line,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": VOICE_STABILITY,
                "similarity_boost": VOICE_SIMILARITY_BOOST,
                "style": VOICE_STYLE,
                "speed": VOICE_SPEED,
            },
        }
        if previous_text:
            body["previous_text"] = previous_text
        if next_text:
            body["next_text"] = next_text
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers={
                "Content-Type": "application/json",
                "xi-api-key": self.api_key,
            },
        )
        with urllib.request.urlopen(req) as resp:
            audio_path.write_bytes(resp.read())
        return _audio_duration(audio_path)


class PiperProvider:
    audio_suffix = ".wav"

    def __init__(self, model_path: str):
        self.model_path = model_path

    def synthesize(
        self,
        slide_data: SlideData,
        audio_path: Path,
        previous_text: str | None = None,
        next_text: str | None = None,
    ) -> float:
        result = subprocess.run(
            ["piper", "--model", self.model_path, "--output_file", str(audio_path)],
            input=slide_data.voice_line,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Piper failed: {result.stderr.strip()}")
        with wave.open(str(audio_path), "rb") as wav_file:
            return wav_file.getnframes() / wav_file.getframerate()


def voice_actor_task_logic(
    slide_data: SlideData,
    audio_path: Path,
    provider: ElevenLabsProvider | PiperProvider,
    previous_text: str | None = None,
    next_text: str | None = None,
) -> float:
    return provider.synthesize(slide_data, audio_path, previous_text, next_text)


def _audio_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr.strip()}")
    return float(result.stdout.strip())
