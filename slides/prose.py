import re

from PIL import Image, ImageDraw, ImageFont

from config import (
    FONT_BOLD,
    FONT_EXTRABOLD,
    FONT_REGULAR,
    FONT_SEMIBOLD,
    PROSE_BULLET_INDENT,
    PROSE_COLOR_BODY,
    PROSE_COLOR_BULLET,
    PROSE_COLOR_H1,
    PROSE_COLOR_H2,
    PROSE_COLOR_H3,
    PROSE_H1_MARGIN_BOTTOM,
    PROSE_H2_MARGIN_BOTTOM,
    PROSE_H2_MARGIN_TOP,
    PROSE_H3_MARGIN_BOTTOM,
    PROSE_H3_MARGIN_TOP,
    PROSE_LINE_HEIGHT_BODY,
    PROSE_LINE_HEIGHT_H1,
    PROSE_LINE_HEIGHT_H2,
    PROSE_LINE_HEIGHT_H3,
    PROSE_LIST_ITEM_GAP,
    PROSE_LIST_MARGIN,
    PROSE_PAD_X,
    PROSE_PAD_Y,
    PROSE_PARA_GAP,
    PROSE_SIZE_BODY,
    PROSE_SIZE_H1,
    PROSE_SIZE_H2,
    PROSE_SIZE_H3,
    RESOLUTION,
)
from schemas import ProseData
from slides.base import BaseSlide
from util.fonts import load_font

MAX_TEXT_WIDTH = RESOLUTION[0] - PROSE_PAD_X * 2


def _wrap(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int
) -> list[str]:
    words = text.split()
    lines, current = [], []
    for word in words:
        current.append(word)
        _, _, w, _ = draw.textbbox((0, 0), " ".join(current), font=font)
        if w > max_width:
            if len(current) > 1:
                lines.append(" ".join(current[:-1]))
                current = [word]
            else:
                lines.append(word)
                current = []
    if current:
        lines.append(" ".join(current))
    return lines or [""]


def _draw_wrapped(draw, text, font, color, x, y, max_width, line_height) -> int:
    for wrapped_line in _wrap(draw, text, font, max_width):
        draw.text((x, y), wrapped_line, font=font, fill=color)
        y += line_height
    return y


class ProseSlide(BaseSlide):
    def __init__(self, data: ProseData):
        super().__init__(data)
        self.data: ProseData = data

    def render(self) -> Image.Image:
        img = self._blank_canvas()
        draw = ImageDraw.Draw(img)

        fonts = {
            "h1": load_font(FONT_EXTRABOLD, PROSE_SIZE_H1),  # weight 800
            "h2": load_font(FONT_BOLD, PROSE_SIZE_H2),  # weight 700
            "h3": load_font(FONT_SEMIBOLD, PROSE_SIZE_H3),  # weight 600
            "body": load_font(FONT_REGULAR, PROSE_SIZE_BODY),  # weight 400
        }

        lh_body = int(PROSE_SIZE_BODY * PROSE_LINE_HEIGHT_BODY)
        lh_h1 = int(PROSE_SIZE_H1 * PROSE_LINE_HEIGHT_H1)
        lh_h2 = int(PROSE_SIZE_H2 * PROSE_LINE_HEIGHT_H2)
        lh_h3 = int(PROSE_SIZE_H3 * PROSE_LINE_HEIGHT_H3)

        x = PROSE_PAD_X
        y = PROSE_PAD_Y
        marker_font = load_font(FONT_BOLD, PROSE_SIZE_BODY)
        bullet_width = MAX_TEXT_WIDTH - PROSE_BULLET_INDENT

        def _is_list_item(s):
            return s.startswith("- ") or bool(re.match(r"^\d+\.\s", s))

        def _is_heading(s):
            return s.startswith("# ") or s.startswith("## ") or s.startswith("### ")

        for i, line in enumerate(self.data.content):
            is_list = _is_list_item(line)
            prev = self.data.content[i - 1] if i > 0 else ""
            prev_is_list = _is_list_item(prev)
            prev_is_heading = _is_heading(prev)

            # list block margin — before first item and after last item
            if is_list and not prev_is_list and i > 0 and not prev_is_heading:
                y += PROSE_LIST_MARGIN
            elif not is_list and prev_is_list and line.strip():
                y += PROSE_LIST_MARGIN

            # inter-item gap
            if is_list and prev_is_list:
                y += PROSE_LIST_ITEM_GAP

            if line.startswith("### "):
                if not prev_is_heading:
                    y += PROSE_H3_MARGIN_TOP
                y = _draw_wrapped(
                    draw,
                    line[4:],
                    fonts["h3"],
                    PROSE_COLOR_H3,
                    x,
                    y,
                    MAX_TEXT_WIDTH,
                    lh_h3,
                )
                y += PROSE_H3_MARGIN_BOTTOM

            elif line.startswith("## "):
                if not prev_is_heading:
                    y += PROSE_H2_MARGIN_TOP
                y = _draw_wrapped(
                    draw,
                    line[3:],
                    fonts["h2"],
                    PROSE_COLOR_H2,
                    x,
                    y,
                    MAX_TEXT_WIDTH,
                    lh_h2,
                )
                y += PROSE_H2_MARGIN_BOTTOM

            elif line.startswith("# "):
                y = _draw_wrapped(
                    draw,
                    line[2:],
                    fonts["h1"],
                    PROSE_COLOR_H1,
                    x,
                    y,
                    MAX_TEXT_WIDTH,
                    lh_h1,
                )
                y += PROSE_H1_MARGIN_BOTTOM

            elif line.startswith("- "):
                draw.text(
                    (x + PROSE_BULLET_INDENT - 28, y + 6),
                    "•",
                    font=marker_font,
                    fill=PROSE_COLOR_BULLET,
                )
                y = _draw_wrapped(
                    draw,
                    line[2:],
                    fonts["body"],
                    PROSE_COLOR_BODY,
                    x + PROSE_BULLET_INDENT,
                    y,
                    bullet_width,
                    lh_body,
                )

            elif m := re.match(r"^(\d+)\.\s", line):
                marker = m.group(1) + "."
                _, _, mw, _ = draw.textbbox((0, 0), marker, font=marker_font)
                draw.text(
                    (x + PROSE_BULLET_INDENT - mw - 8, y),
                    marker,
                    font=marker_font,
                    fill=PROSE_COLOR_BULLET,
                )
                y = _draw_wrapped(
                    draw,
                    line[m.end() :],
                    fonts["body"],
                    PROSE_COLOR_BODY,
                    x + PROSE_BULLET_INDENT,
                    y,
                    bullet_width,
                    lh_body,
                )

            elif not line.strip():
                # blank line = explicit paragraph gap, but suppress after headings
                if not prev_is_heading:
                    y += PROSE_PARA_GAP

            else:
                y = _draw_wrapped(
                    draw,
                    line,
                    fonts["body"],
                    PROSE_COLOR_BODY,
                    x,
                    y,
                    MAX_TEXT_WIDTH,
                    lh_body,
                )

        return img
