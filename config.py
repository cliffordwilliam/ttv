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
FONT_MONO = "/home/clif/.local/share/fonts/JetBrainsMono/JetBrainsMono-Regular.ttf"

# --- Code slide ---
CODE_SIZE_BODY = 32
CODE_PAD_X = 120  # canvas padding outside the block
CODE_PAD_Y = 80
CODE_BLOCK_PADDING = 48  # inner padding inside the editor block
CODE_LINE_GAP = 13
CODE_CORNER_RADIUS = 16
CODE_GUTTER_PAD_RIGHT = int(
    CODE_SIZE_BODY * 0.8
)  # 0.8em pad between separator and text
