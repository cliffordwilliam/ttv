from pathlib import Path


SUPPORTED_TYPES = {"prose", "image", "code"}


def parse(path: str | Path) -> list[dict]:
    text = Path(path).read_text(encoding="utf-8")
    return _parse_text(text)


def _parse_text(text: str) -> list[dict]:
    slides = []
    current = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        if line.startswith("@slide="):
            slide_type = line[len("@slide="):]
            if slide_type not in SUPPORTED_TYPES:
                raise ValueError(f"Unknown slide type: {slide_type!r}")
            if current is not None:
                raise ValueError("Found @slide without a preceding @end")
            current = {"type": slide_type, "content": []}

        elif line == "@end":
            if current is None:
                raise ValueError("Found @end without a matching @slide")
            slides.append(current)
            current = None

        elif current is not None:
            if line.startswith("@"):
                key, _, value = line[1:].partition("=")
                current[key] = value
            else:
                current["content"].append(raw_line)

    if current is not None:
        raise ValueError("Reached end of file without a closing @end")

    return slides


if __name__ == "__main__":
    import sys
    import pprint

    target = sys.argv[1] if len(sys.argv) > 1 else "examples/sample.txt"
    slides = parse(target)
    pprint.pprint(slides, sort_dicts=False)
    print(f"\n{len(slides)} slide(s) parsed.")
