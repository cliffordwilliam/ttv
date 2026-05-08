# TODO

Things planned from today's design discussion.

## Tooling for the .txt DSL

- [ ] **Syntax highlighter** — TextMate grammar for `@slide`, `@end`, directives, etc. Works in VS Code, Neovim, and anything that consumes TextMate grammars.
- [ ] **Formatter** — round-trip pretty-printer (parse → emit canonical form). Normalizes blank lines between blocks, strips trailing whitespace, enforces directive ordering.
- [ ] **LSP** — language server with diagnostics (missing `@src` on image slides, unclosed blocks, unknown slide types), completions for directive keys and `@slide=` values, and hover docs. Also exposes the formatter as a capability. No separate linter needed — LSP diagnostics cover it.

## Distribution

- [ ] **Docker image** — packages ttv with ffmpeg and fonts so users can run it like a compiler: `docker run --rm -v $(pwd):/work ttv input.txt output.mp4`. Keep image lean; don't bake in voice models.
- [ ] **Kokoro TTS sidecar** — replace the Piper `subprocess` call in `audio.py` with an HTTP call to a Kokoro container. Voice becomes opt-in: "provision Kokoro if you want voice." Make the endpoint configurable via env var so it can point at a remote instance too.
