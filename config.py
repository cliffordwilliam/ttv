PAUSE_BEFORE_S = 0.6
PAUSE_AFTER_S = 0.6
RESOLUTION = (1920, 1080)
FPS = 60

# --- Syntax ---
DIRECTIVE = "@"
START_DIRECTIVE = f"{DIRECTIVE}slide="
END_DIRECTIVE = f"{DIRECTIVE}end"

# --- Loading bar ---
LOADING_BAR_TOTAL_WIDTH_CHAR_UNIT = 30
FILLED_BAR_CHARACTER = "█"
EMPTY_BAR_CHARACTER = "░"

# --- Slide canvas ---
BACKGROUND_COLOR = (18, 18, 18)

# --- Fonts ---
FONT_REGULAR = "/usr/share/fonts/noto/NotoSans-Regular.ttf"
FONT_SEMIBOLD = "/usr/share/fonts/noto/NotoSans-SemiBold.ttf"
FONT_BOLD = "/usr/share/fonts/noto/NotoSans-Bold.ttf"
FONT_EXTRABOLD = "/usr/share/fonts/noto/NotoSans-ExtraBold.ttf"
FONT_MONO = "/usr/share/fonts/noto/NotoSansMono-Regular.ttf"

# --- Prose slide font sizes (Tailwind prose ratios: 2.25 / 1.5 / 1.25 / 1) ---
PROSE_SIZE_BODY = 40
PROSE_SIZE_H3 = int(PROSE_SIZE_BODY * 1.25)  # 50px  weight 600
PROSE_SIZE_H2 = int(PROSE_SIZE_BODY * 1.5)  # 60px  weight 700
PROSE_SIZE_H1 = int(PROSE_SIZE_BODY * 2.25)  # 90px  weight 800

# --- Prose slide line heights (Tailwind prose ratios) ---
PROSE_LINE_HEIGHT_BODY = 1.75
PROSE_LINE_HEIGHT_H1 = 1.11
PROSE_LINE_HEIGHT_H2 = 1.33
PROSE_LINE_HEIGHT_H3 = 1.60

# --- Prose slide colors (dark canvas, adapted from Tailwind slate palette) ---
PROSE_COLOR_H1 = (255, 255, 255)  # slate-50
PROSE_COLOR_H2 = (241, 245, 249)  # slate-100
PROSE_COLOR_H3 = (226, 232, 240)  # slate-200
PROSE_COLOR_BODY = (148, 163, 184)  # slate-400
PROSE_COLOR_BULLET = (120, 180, 255)

# --- Prose slide layout (notebook/NoteView.svelte spec) ---
PROSE_PAD_X = 120
PROSE_PAD_Y = 100
PROSE_BULLET_INDENT = int(PROSE_SIZE_BODY * 1.625)  # 1.625em

# paragraph
PROSE_PARA_GAP = int(PROSE_SIZE_BODY * 1.25)  # 1.25em top+bottom

# h1: margin-bottom 0.8888em, no margin-top (first element)
PROSE_H1_MARGIN_BOTTOM = int(PROSE_SIZE_H1 * 0.8888)

# h2: margin-top 2em, margin-bottom 1em
PROSE_H2_MARGIN_TOP = int(PROSE_SIZE_H2 * 2.0)
PROSE_H2_MARGIN_BOTTOM = int(PROSE_SIZE_H2 * 1.0)

# h3: margin-top 1.6em, margin-bottom 0.6666em
PROSE_H3_MARGIN_TOP = int(PROSE_SIZE_H3 * 1.6)
PROSE_H3_MARGIN_BOTTOM = int(PROSE_SIZE_H3 * 0.6666)

# lists: 1.25em block margin, 0.5em between items
PROSE_LIST_ITEM_GAP = int(PROSE_SIZE_BODY * 0.5)
PROSE_LIST_MARGIN = int(PROSE_SIZE_BODY * 1.25)

# --- Code slide ---
CODE_SIZE_BODY = 32
CODE_PAD_X = 120  # canvas padding outside the block
CODE_PAD_Y = 80
CODE_BLOCK_PADDING = 48  # inner padding inside the editor block
CODE_LINE_GAP = 10
CODE_CORNER_RADIUS = 16
CODE_GUTTER_PAD_RIGHT = int(CODE_SIZE_BODY * 0.8)  # 0.8em pad between separator and text
