# ttv — Text to Video Compiler

Takes a structured `.txt` file and compiles it into an `.mp4`. Text in, video out.

## External dependencies

These must be installed and available on your PATH before running ttv:

- **FFmpeg** — video encoding and concatenation. Install via your package manager (e.g. `sudo pacman -S ffmpeg`).

## Voice support

Voice is optional. ttv has no built-in TTS — it talks to a [Kokoro FastAPI](https://github.com/remsky/Kokoro-FastAPI) instance over HTTP.

**Without voice** — each slide must declare its screen time explicitly otherwise it defaults to 0 seconds:

```
@duration=5
```

**With voice** — point ttv at a running Kokoro container via the `KOKORO_URL` env var:

```bash
KOKORO_URL=http://localhost:8880 uv run python ttv.py my_video.txt
```

When Kokoro is active, slide duration is derived from the synthesized audio and `@duration` is ignored. When it is not, `@duration` is used as-is.

## Syntax highlighting

Code slides use [tree-sitter](https://tree-sitter.github.io/) for structural syntax highlighting. See [docs/highlight.md](docs/highlight.md) for architecture, adding languages, and tuning colors.

## Python dependencies

Managed via `uv`. Run `uv sync` to install.

## Usage

```bash
uv run python ttv.py my_video.txt
```

```bash
KOKORO_URL=http://localhost:8880 uv run python ttv.py my_video.txt
```

## Provisioning Kokoro

You can provision yourself with Kokoro:

```bash
docker run \
    --name kokoro \
    --restart=always \
    -v kokoro-data:/var/lib/kokoro \
    -p 8880:8880 \
    -d hwdsl2/kokoro-server
```

Do not forget to make sure you have this in your .env:

```text
KOKORO_URL=http://localhost:8880
```
