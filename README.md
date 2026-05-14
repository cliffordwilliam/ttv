# ttv — Text to Video Compiler

Takes a structured `.txt` file and compiles it into an `.mp4`. Text in, video out.

## Installation

```bash
uv tool install git+https://github.com/cliffordwilliam/ttv
```

This installs `ttv` as a global command. To update:

```bash
uv tool upgrade ttv
```

## External dependencies

These must be installed and available on your PATH before running ttv:

- **FFmpeg** — video encoding and concatenation. Install via your package manager (e.g. `sudo pacman -S ffmpeg`).
- **Piper** — required only for local dev voice. Installed automatically as a Python dependency via `uv sync`.

## Voice support

Voice is optional. ttv supports two providers:

| Provider | Use case | Requires |
|---|---|---|
| **Piper** | Local dev — free, no network, no credits | `PIPER_MODEL` env var |
| **ElevenLabs** | Final render — Yuki's voice | `ELEVEN_LABS_API_KEY` + `VOICE_ID` env vars |

If neither is configured, each slide must declare its screen time explicitly:

```
@duration=5
```

When a voice provider is active, slide duration is derived from the synthesized audio and `@duration` is ignored.

Provider priority: **Piper → ElevenLabs → silent**.

### Piper (local dev)

Download a voice model once and point `PIPER_MODEL` at the `.onnx` file:

```bash
# example — downloads en_US-lessac-high into voices/
curl -L https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/high/en_US-lessac-high.onnx -o voices/en_US-lessac-high.onnx
curl -L https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/high/en_US-lessac-high.onnx.json -o voices/en_US-lessac-high.onnx.json
```

```bash
PIPER_MODEL=voices/en_US-lessac-high.onnx ttv my_video.txt
```

### ElevenLabs (final render)

Add your credentials to `.env` (see `.env.example`):

```text
ELEVEN_LABS_API_KEY=your_key_here
VOICE_ID=your_voice_id_here
```

```bash
ttv my_video.txt
```

## Python dependencies

Managed via `uv`. Run `uv sync` to install.

## Usage

```bash
# silent
ttv my_video.txt

# local dev voice
PIPER_MODEL=voices/en_US-lessac-high.onnx ttv my_video.txt

# final render (ttv auto-loads .env from current directory)
ttv my_video.txt
```
