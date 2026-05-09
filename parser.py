from enum import Enum, auto
from dataclasses import fields as dc_fields
from pathlib import Path
from schemas import SlideData, REGISTRY

DIRECTIVE = "@"
START_DIRECTIVE = f"{DIRECTIVE}slide="
END_DIRECTIVE = f"{DIRECTIVE}end"

class _State(Enum):
    OUTSIDE = auto()
    INSIDE = auto()


def parse(path: Path) -> list[SlideData]:
    text = path.read_text(encoding="utf-8")
    slides: list[SlideData] = []
    state = _State.OUTSIDE
    slide_type: str = ""
    slide_kwargs: dict[str, str] = {}
    slide_content: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        if state is _State.OUTSIDE:
            if line.startswith(START_DIRECTIVE):
                given_slide_type = line[len(START_DIRECTIVE):]
                _validate_slide_type(given_slide_type)
                # Transition to INSIDE state.
                slide_type = given_slide_type
                state = _State.INSIDE
            elif line == END_DIRECTIVE:
                raise ValueError(f"Found {END_DIRECTIVE} without a matching {START_DIRECTIVE}")

        elif state is _State.INSIDE:
            # Handle found end.
            if line == END_DIRECTIVE:
                cls = REGISTRY[slide_type]
                slides.append(cls(content=slide_content, **slide_kwargs))
                # Transition to OUTSIDE state.
                slide_type = ""
                slide_kwargs = {}
                slide_content = []
                state = _State.OUTSIDE
            elif line.startswith(START_DIRECTIVE):
                raise ValueError(f"Found {START_DIRECTIVE} without a preceding {END_DIRECTIVE}")
            # Handle inside body.
            elif line.startswith(DIRECTIVE):
                key, _, value = line[1:].partition("=")
                _validate_slide_key(key, slide_type)
                slide_kwargs[key] = value
            else:
                slide_content.append(raw_line)

    if state is _State.INSIDE:
        raise ValueError(f"Reached end of file without a closing {END_DIRECTIVE}")

    return slides

def _validate_slide_type(given_slide_type: str):
    if given_slide_type not in REGISTRY:
        raise ValueError(f"Unknown slide type {given_slide_type!r}")

def _validate_slide_key(given_slide_key: str, given_slide_type: str):
    cls = REGISTRY[given_slide_type]
    valid = {f.name for f in dc_fields(cls)} - {"content"}
    if given_slide_key not in valid:
        raise ValueError(f"Unknown field {given_slide_key!r} for {given_slide_type!r} slide")
