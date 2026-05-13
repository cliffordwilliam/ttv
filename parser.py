from dataclasses import fields as dc_fields
from enum import Enum, auto
from pathlib import Path

from config import DIRECTIVE, END_DIRECTIVE, START_DIRECTIVE
from schemas import REGISTRY, SlideData


class _State(Enum):
    OUTSIDE = auto()
    INSIDE = auto()


def parse(text_file_path: Path) -> list[SlideData]:
    # Decode text using utf-8 and store it here.
    text = text_file_path.read_text(encoding="utf-8")

    # Setup state machine states
    slides: list[SlideData] = []
    state = _State.OUTSIDE
    slide_type: str = ""
    slide_kwargs: dict[str, str] = {}
    slide_content: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        if state is _State.OUTSIDE:
            # Hunt for START!
            # Setup and transition to INSIDE state.
            if line.startswith(START_DIRECTIVE):
                given_slide_type = line[len(START_DIRECTIVE) :]
                _validate_slide_type(given_slide_type)
                slide_type = given_slide_type
                state = _State.INSIDE
            # Handle illegal find.
            elif line == END_DIRECTIVE:
                raise ValueError(
                    f"Invalid format: Found {END_DIRECTIVE} without a matching {START_DIRECTIVE}"
                )

        elif state is _State.INSIDE:
            # Hunt for END!
            # Setup and transition to OUTSIDE state.
            if line == END_DIRECTIVE:
                slide_class = REGISTRY[slide_type]
                slides.append(slide_class(content=slide_content, **slide_kwargs))
                slide_type = ""
                slide_kwargs = {}
                slide_content = []
                state = _State.OUTSIDE
            # Handle illegal find.
            elif line.startswith(START_DIRECTIVE):
                raise ValueError(
                    f"Invalid format: Found {START_DIRECTIVE} without a preceding {END_DIRECTIVE}"
                )
            # Handle inside body.
            elif line.startswith(DIRECTIVE):
                # Handle this slide key value pairs!
                key, _, value = line[1:].partition("=")
                _validate_slide_key(key, slide_type)
                _validate_image_path_exists(key, value)
                slide_kwargs[key] = value
            else:
                # Handle this slide content!
                slide_content.append(raw_line)

    if state is _State.INSIDE:
        raise ValueError(
            f"Invalid format: Reached end of file without a closing {END_DIRECTIVE}"
        )

    return slides


def _validate_image_path_exists(given_slide_key: str, given_slide_value: str):
    if given_slide_key == "src":
        image_path_string = given_slide_value
        if not Path(image_path_string).exists():
            raise ValueError(f"Image not found: {image_path_string}")


def _validate_slide_type(given_slide_type: str):
    if given_slide_type not in REGISTRY:
        raise ValueError(f"Unknown slide type: {given_slide_type!r}")


def _validate_slide_key(given_slide_key: str, given_slide_type: str):
    slide_class = REGISTRY[given_slide_type]
    # Valid keys are the ones in DTO (minus its content key)
    valid_keys = {f.name for f in dc_fields(slide_class)} - {"content"}
    if given_slide_key not in valid_keys:
        raise ValueError(
            f"Unknown field: {given_slide_key!r} for {given_slide_type!r} slide"
        )
