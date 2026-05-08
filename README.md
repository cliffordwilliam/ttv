# ttv — Text to Video Compiler

Takes a structured `.txt` file and compiles it into an `.mp4`. Text in, video out.

## External dependencies

These must be installed and available on your PATH before running ttv:

- **Piper TTS** — voice synthesis. Install with `uv tool install piper-tts`.
- **FFmpeg** — video encoding and concatenation. Install via your package manager (e.g. `sudo pacman -S ffmpeg`).

Voice model files are expected in `~/.local/share/piper-voices/`. The model in use is configured via `VOICE_MODEL` in `config.py`.

## Python dependencies

Managed via `uv`. Run `uv sync` to install.

## Usage

```bash
uv run python ttv.py my_video.txt
```
