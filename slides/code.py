from PIL import Image, ImageDraw, ImageFilter

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

CODE_BLOCK_COLOR = (30, 30, 46)           # mocha base
CODE_DEFAULT_COLOR = (205, 214, 244)      # mocha text
CODE_HIGHLIGHT_COLOR = (49, 50, 68)       # mocha surface0
CODE_GUTTER_COLOR = (127, 132, 156)       # mocha overlay1
CODE_GUTTER_BORDER = (69, 71, 90)         # mocha surface1
CODE_TITLEBAR_COLOR = (24, 24, 37)        # mocha mantle
CODE_TITLEBAR_DOT_COLOR = (88, 91, 112)   # mocha surface2
CODE_TITLEBAR_BORDER_COLOR = (49, 50, 68) # mocha surface0

CODE_TITLEBAR_HEIGHT = 90       # ref 38px × (32/13.5)
CODE_TITLEBAR_PAD = 28          # ref 12px × (32/13.5) — left/right padding inside titlebar
CODE_TITLEBAR_DOT_RADIUS = 14   # ref 6px  × (32/13.5)
CODE_TITLEBAR_DOT_GAP = 45      # ref 19px × (32/13.5) — center-to-center (diameter + edge gap)
CODE_TITLEBAR_LABEL_RIGHT = 33  # ref 14px × (32/13.5) — right offset for the editor name


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

        lang = self.data.lang
        font = load_font(FONT_MONO, CODE_SIZE_BODY)
        gutter_font = load_font(FONT_MONO, CODE_SIZE_BODY)
        titlebar_font = load_font(FONT_MONO, int(CODE_SIZE_BODY * 11.5 / 13.5))  # ref 11.5/13.5 ratio

        raw_lines = self.data.content
        highlighted = [line.endswith(HIGHLIGHT_MARKER) for line in raw_lines]
        clean_lines = [
            line[: -len(HIGHLIGHT_MARKER)].rstrip() if hl else line
            for line, hl in zip(raw_lines, highlighted)
        ]

        code_text = "\n".join(clean_lines)
        tokens = highlight.tokenize(code_text, lang)
        token_lines = _split_tokens_by_line(tokens)

        # Measure layout before compositing
        _tmp = ImageDraw.Draw(img)
        _, _, _, line_h = _tmp.textbbox((0, 0), "Ag", font=font)
        row_h = line_h + CODE_LINE_GAP
        _, _, char_w, _ = _tmp.textbbox((0, 0), "0", font=gutter_font)
        gutter_digits = len(str(len(token_lines)))
        gutter_width = char_w * gutter_digits + CODE_GUTTER_PAD_RIGHT

        canvas_w, canvas_h = RESOLUTION
        block_x0 = CODE_PAD_X
        block_y0 = CODE_PAD_Y
        block_x1 = canvas_w - CODE_PAD_X
        block_y1 = canvas_h - CODE_PAD_Y
        titlebar_y1 = block_y0 + CODE_TITLEBAR_HEIGHT
        gutter_border_x = block_x0 + CODE_BLOCK_PADDING + gutter_width
        x_text = gutter_border_x + CODE_GUTTER_PAD_RIGHT

        # Drop shadow
        shadow = Image.new("RGBA", RESOLUTION, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle(
            [block_x0, block_y0 + 16, block_x1, block_y1 + 16],
            radius=CODE_CORNER_RADIUS,
            fill=(0, 0, 0, 170),
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=24))
        img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")

        draw = ImageDraw.Draw(img)

        # Card background
        _rounded_rect(draw, (block_x0, block_y0, block_x1, block_y1), CODE_CORNER_RADIUS, CODE_BLOCK_COLOR)

        # Titlebar: extend rounded rect below the separator by corner radius so the
        # bottom "rounded corners" of this rect are hidden inside the code area,
        # then patch that strip back to CODE_BLOCK_COLOR.
        _rounded_rect(draw, (block_x0, block_y0, block_x1, titlebar_y1 + CODE_CORNER_RADIUS), CODE_CORNER_RADIUS, CODE_TITLEBAR_COLOR)
        draw.rectangle([(block_x0, titlebar_y1), (block_x1, titlebar_y1 + CODE_CORNER_RADIUS)], fill=CODE_BLOCK_COLOR)
        draw.line([(block_x0, titlebar_y1), (block_x1, titlebar_y1)], fill=CODE_TITLEBAR_BORDER_COLOR, width=1)

        # Traffic light dots
        dot_cx = block_x0 + CODE_TITLEBAR_PAD + CODE_TITLEBAR_DOT_RADIUS
        dot_cy = block_y0 + CODE_TITLEBAR_HEIGHT // 2
        for _ in range(3):
            r = CODE_TITLEBAR_DOT_RADIUS
            draw.ellipse([dot_cx - r, dot_cy - r, dot_cx + r, dot_cy + r], fill=CODE_TITLEBAR_DOT_COLOR)
            dot_cx += CODE_TITLEBAR_DOT_GAP

        # Editor name label (right-aligned)
        label = "Phantom Editor"
        lx0, ly0, lx1, ly1 = draw.textbbox((0, 0), label, font=titlebar_font)
        label_h = ly1 - ly0
        draw.text(
            (block_x1 - CODE_TITLEBAR_LABEL_RIGHT - lx1, block_y0 + (CODE_TITLEBAR_HEIGHT - label_h) // 2 - ly0),
            label,
            font=titlebar_font,
            fill=CODE_GUTTER_COLOR,
        )

        # Gutter separator
        draw.line(
            [(gutter_border_x, titlebar_y1 + CODE_BLOCK_PADDING), (gutter_border_x, block_y1 - CODE_BLOCK_PADDING)],
            fill=CODE_GUTTER_BORDER,
            width=1,
        )

        # Code rows
        y = titlebar_y1 + CODE_BLOCK_PADDING
        for i, token_row in enumerate(token_lines):
            if i >= len(highlighted):
                break

            if highlighted[i]:
                draw.rectangle([(block_x0, y - 4), (block_x1, y + row_h - 4)], fill=CODE_HIGHLIGHT_COLOR)
                draw.line([(gutter_border_x, y - 4), (gutter_border_x, y + row_h - 4)], fill=CODE_GUTTER_BORDER, width=1)

            lineno = str(i + 1)
            _, _, lw, _ = draw.textbbox((0, 0), lineno, font=gutter_font)
            draw.text((gutter_border_x - CODE_GUTTER_PAD_RIGHT - lw, y), lineno, font=gutter_font, fill=CODE_GUTTER_COLOR)

            x = x_text
            for ttype, value in token_row:
                color = highlight.token_color(ttype)
                draw.text((x, y), value, font=font, fill=color)
                _, _, tw, _ = draw.textbbox((0, 0), value, font=font)
                x += tw

            y += row_h

        return img
