from PIL import Image, ImageDraw

from config import (
    CODE_BLOCK_PADDING,
    CODE_CORNER_RADIUS,
    CODE_GUTTER_PAD_RIGHT,
    CODE_LINE_GAP,
    CODE_PAD_X,
    CODE_PAD_Y,
    CODE_SIZE_BODY,
    FONT_MONO,
    RESOLUTION,
)
from schemas import CodeData
from slides.base import BaseSlide
from util import highlight
from util.fonts import load_font

HIGHLIGHT_MARKER = "!#"

CODE_BLOCK_COLOR = (30, 30, 46)  # mocha base
CODE_DEFAULT_COLOR = (205, 214, 244)  # mocha text
CODE_HIGHLIGHT_COLOR = (49, 50, 68)  # mocha surface0
CODE_GUTTER_COLOR = (127, 132, 156)  # mocha overlay1
CODE_GUTTER_BORDER = (69, 71, 90)  # mocha surface1


def _split_tokens_by_line(tokens: list[tuple]) -> list[list[tuple]]:
    lines = [[]]
    for ttype, value in tokens:
        parts = value.split("\n")
        for i, part in enumerate(parts):
            if part:
                lines[-1].append((ttype, part))
            if i < len(parts) - 1:
                lines.append([])
    return lines


def _rounded_rect(
    draw: ImageDraw.ImageDraw, box: tuple, radius: int, fill: tuple
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill)


class CodeSlide(BaseSlide):
    def __init__(self, data: CodeData):
        super().__init__(data)
        self.data: CodeData = data

    def render(self) -> Image.Image:
        img = self._blank_canvas()
        draw = ImageDraw.Draw(img)

        lang = self.data.lang
        font = load_font(FONT_MONO, CODE_SIZE_BODY)
        gutter_font = load_font(FONT_MONO, CODE_SIZE_BODY)

        raw_lines = self.data.content
        highlighted = [line.endswith(HIGHLIGHT_MARKER) for line in raw_lines]
        clean_lines = [
            line[: -len(HIGHLIGHT_MARKER)].rstrip() if hl else line
            for line, hl in zip(raw_lines, highlighted)
        ]

        code_text = "\n".join(clean_lines)
        tokens = highlight.tokenize(code_text, lang)
        token_lines = _split_tokens_by_line(tokens)

        _, _, _, line_h = draw.textbbox((0, 0), "Ag", font=font)
        row_h = line_h + CODE_LINE_GAP

        # Derive gutter width from actual char width × digit count (Pygments: fontw * chars + pad)
        _, _, char_w, _ = draw.textbbox((0, 0), "0", font=gutter_font)
        gutter_digits = len(str(len(token_lines)))
        gutter_width = char_w * gutter_digits + CODE_GUTTER_PAD_RIGHT

        canvas_w, canvas_h = RESOLUTION
        block_x0 = CODE_PAD_X
        block_y0 = CODE_PAD_Y
        block_x1 = canvas_w - CODE_PAD_X
        block_y1 = canvas_h - CODE_PAD_Y

        # editor card background
        _rounded_rect(
            draw,
            (block_x0, block_y0, block_x1, block_y1),
            CODE_CORNER_RADIUS,
            CODE_BLOCK_COLOR,
        )

        gutter_border_x = block_x0 + CODE_BLOCK_PADDING + gutter_width
        x_text = gutter_border_x + CODE_GUTTER_PAD_RIGHT
        y = block_y0 + CODE_BLOCK_PADDING

        # 1px vertical separator — Prism spec
        draw.line(
            [
                (gutter_border_x, block_y0 + CODE_BLOCK_PADDING),
                (gutter_border_x, block_y1 - CODE_BLOCK_PADDING),
            ],
            fill=CODE_GUTTER_BORDER,
            width=1,
        )

        for i, token_row in enumerate(token_lines):
            if i >= len(highlighted):
                break

            if highlighted[i]:
                draw.rectangle(
                    [(block_x0, y - 4), (block_x1, y + row_h - 4)],
                    fill=CODE_HIGHLIGHT_COLOR,
                )
                draw.line(
                    [(gutter_border_x, y - 4), (gutter_border_x, y + row_h - 4)],
                    fill=CODE_GUTTER_BORDER,
                    width=1,
                )

            # gutter line number — right-aligned with 0.8em pad from separator
            lineno = str(i + 1)
            _, _, lw, _ = draw.textbbox((0, 0), lineno, font=gutter_font)
            gutter_x = gutter_border_x - CODE_GUTTER_PAD_RIGHT - lw
            draw.text((gutter_x, y), lineno, font=gutter_font, fill=CODE_GUTTER_COLOR)

            # syntax-colored tokens
            x = x_text
            for ttype, value in token_row:
                color = highlight.token_color(ttype)
                draw.text((x, y), value, font=font, fill=color)
                _, _, tw, _ = draw.textbbox((0, 0), value, font=font)
                x += tw

            y += row_h

        return img
