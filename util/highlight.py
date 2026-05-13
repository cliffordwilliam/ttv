import importlib.resources

import tree_sitter_markdown as tsmarkdown
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

_COLORS: dict[str, tuple[int, int, int]] = {
    "keyword": (203, 166, 247),  # mauve
    "constant.builtin": (203, 166, 247),  # mauve   — None / True / False
    "function": (137, 180, 250),  # blue
    "function.method": (116, 199, 236),  # sapphire
    "function.builtin": (249, 226, 175),  # yellow  — builtins as callables
    "property": (116, 199, 236),  # sapphire
    "type": (249, 226, 175),  # yellow
    "constructor": (249, 226, 175),  # yellow  — PascalCase convention
    "constant": (250, 179, 135),  # peach   — ALL_CAPS
    "builtin": (249, 226, 175),  # yellow  — post-pass non-call builtins
    "module": (180, 190, 254),  # lavender
    "parameter": (235, 160, 172),  # maroon
    "string": (166, 227, 161),  # green
    "escape": (148, 226, 213),  # teal
    "comment": (127, 132, 156),  # overlay1
    "number": (250, 179, 135),  # peach
    "operator": (205, 214, 244),  # text
    "variable": (205, 214, 244),  # text
    # markdown-specific
    "text.title": (180, 190, 254),       # lavender — heading content
    "text.strong": (249, 226, 175),      # yellow   — bold
    "text.emphasis": (245, 194, 231),    # pink     — italic
    "text.literal": (166, 227, 161),     # green    — inline code / code blocks
    "text.uri": (137, 180, 250),         # blue     — links
    "text.reference": (116, 199, 236),   # sapphire — link labels
    "punctuation.special": (203, 166, 247),  # mauve — #/- markers
    "punctuation.delimiter": (127, 132, 156),  # overlay1 — brackets / backticks
    "string.escape": (148, 226, 213),    # teal     — backslash escapes
    "default": (205, 214, 244),  # text
}

# Ordered least → most specific; later passes overwrite earlier ones
_PRIORITY: list[str] = [
    "variable",
    "number",
    "string",
    "escape",
    "comment",
    "operator",
    "property",
    "parameter",
    "constant.builtin",
    "function",
    "constructor",  # PascalCase overwrites @function for class-like names
    "module",  # lavender for imports beats yellow PascalCase heuristic
    "constant",  # peach ALL_CAPS beats yellow PascalCase heuristic
    "function.method",
    "type",
    "function.builtin",
    "keyword",
    # markdown-specific
    "text.title",
    "text.strong",
    "text.emphasis",
    "text.literal",
    "text.uri",
    "text.reference",
    "punctuation.special",
    "punctuation.delimiter",
    "string.escape",
]

_BUILTINS: frozenset[str] = frozenset(
    {
        "abs",
        "aiter",
        "all",
        "anext",
        "any",
        "ascii",
        "bin",
        "bool",
        "breakpoint",
        "bytearray",
        "bytes",
        "callable",
        "chr",
        "classmethod",
        "compile",
        "complex",
        "delattr",
        "dict",
        "dir",
        "divmod",
        "enumerate",
        "eval",
        "exec",
        "filter",
        "float",
        "format",
        "frozenset",
        "getattr",
        "globals",
        "hasattr",
        "hash",
        "help",
        "hex",
        "id",
        "input",
        "int",
        "isinstance",
        "issubclass",
        "iter",
        "len",
        "list",
        "locals",
        "map",
        "max",
        "memoryview",
        "min",
        "next",
        "object",
        "oct",
        "open",
        "ord",
        "pow",
        "print",
        "property",
        "range",
        "repr",
        "reversed",
        "round",
        "set",
        "setattr",
        "slice",
        "sorted",
        "staticmethod",
        "str",
        "sum",
        "super",
        "tuple",
        "type",
        "vars",
        "zip",
        "ArithmeticError",
        "AssertionError",
        "AttributeError",
        "BaseException",
        "BaseExceptionGroup",
        "BlockingIOError",
        "BrokenPipeError",
        "BufferError",
        "BytesWarning",
        "ChildProcessError",
        "ConnectionAbortedError",
        "ConnectionError",
        "ConnectionRefusedError",
        "ConnectionResetError",
        "DeprecationWarning",
        "EOFError",
        "EnvironmentError",
        "Exception",
        "ExceptionGroup",
        "FileExistsError",
        "FileNotFoundError",
        "FloatingPointError",
        "FutureWarning",
        "GeneratorExit",
        "IOError",
        "ImportError",
        "ImportWarning",
        "IndentationError",
        "IndexError",
        "InterruptedError",
        "IsADirectoryError",
        "KeyError",
        "KeyboardInterrupt",
        "LookupError",
        "MemoryError",
        "ModuleNotFoundError",
        "NameError",
        "NotADirectoryError",
        "NotImplemented",
        "NotImplementedError",
        "OSError",
        "OverflowError",
        "PendingDeprecationWarning",
        "PermissionError",
        "ProcessLookupError",
        "RecursionError",
        "ReferenceError",
        "ResourceWarning",
        "RuntimeError",
        "RuntimeWarning",
        "StopAsyncIteration",
        "StopIteration",
        "SyntaxError",
        "SyntaxWarning",
        "SystemError",
        "SystemExit",
        "TabError",
        "TimeoutError",
        "TypeError",
        "UnboundLocalError",
        "UnicodeDecodeError",
        "UnicodeEncodeError",
        "UnicodeError",
        "UnicodeTranslateError",
        "UnicodeWarning",
        "UserWarning",
        "ValueError",
        "Warning",
        "ZeroDivisionError",
    }
)

# Maps canonical lang name → installed tree-sitter-* package name.
# To add a language: uv add tree-sitter-<lang>, import it above, then add
# entries here and in _LANGUAGES / _PARSERS / _QUERY_SUBPATHS below.
_LANG_PACKAGES: dict[str, str] = {
    "python": "tree_sitter_python",
    "markdown": "tree_sitter_markdown",
}

# Override when the highlights.scm is not at the default queries/highlights.scm path.
_QUERY_SUBPATHS: dict[str, str] = {
    "markdown": "queries/markdown/highlights.scm",
}

# Extra patterns appended on top of each language's bundled highlights.scm.
# Only needed when the bundled query is missing something important.
_CUSTOM_PATTERNS: dict[str, str] = {
    "python": """
(import_from_statement (dotted_name (identifier) @module))
(import_statement (dotted_name (identifier) @module))

(parameters (identifier) @parameter)
(parameters (typed_parameter (identifier) @parameter))
(parameters (default_parameter name: (identifier) @parameter))
(parameters (typed_default_parameter name: (identifier) @parameter))
(keyword_argument name: (identifier) @parameter)
""",
}

_LANG_ALIASES: dict[str, str] = {
    "py": "python",
    "python3": "python",
    "md": "markdown",
}

_PY_LANGUAGE = Language(tspython.language())
_MD_LANGUAGE = Language(tsmarkdown.language())
_LANGUAGES: dict[str, Language] = {"python": _PY_LANGUAGE, "markdown": _MD_LANGUAGE}
_PARSERS: dict[str, Parser] = {"python": Parser(_PY_LANGUAGE), "markdown": Parser(_MD_LANGUAGE)}

_compiled_queries: dict[str, Query] = {}


def _normalize(lang: str) -> str:
    return _LANG_ALIASES.get(lang, lang)


def _load_query(lang: str) -> Query:
    pkg = _LANG_PACKAGES[lang]
    subpath = _QUERY_SUBPATHS.get(lang, "queries/highlights.scm")
    base = (
        importlib.resources.files(pkg)
        .joinpath(subpath)
        .read_text(encoding="utf-8")
    )
    return Query(_LANGUAGES[lang], base + _CUSTOM_PATTERNS.get(lang, ""))


def _get_query(lang: str) -> Query:
    if lang not in _compiled_queries:
        _compiled_queries[lang] = _load_query(lang)
    return _compiled_queries[lang]


def token_color(capture_name: str) -> tuple[int, int, int]:
    return _COLORS.get(capture_name, _COLORS["default"])


def tokenize(code: str, lang: str) -> list[tuple[str, str]]:
    lang = _normalize(lang)
    if lang not in _LANGUAGES:
        return [("default", code)]

    source = code.encode("utf-8")
    if not source:
        return []

    tree = _PARSERS[lang].parse(source)
    raw_captures: dict[str, list] = QueryCursor(_get_query(lang)).captures(
        tree.root_node
    )

    # Paint each byte with a capture name; more specific passes overwrite less specific
    byte_labels: list[str | None] = [None] * len(source)
    for capture_name in _PRIORITY:
        for node in raw_captures.get(capture_name, []):
            s, e = node.start_byte, min(node.end_byte, len(source))
            byte_labels[s:e] = [capture_name] * (e - s)

    # Collapse consecutive same-label runs into (label, text) pairs
    tokens: list[tuple[str, str]] = []
    i = 0
    while i < len(source):
        label = byte_labels[i] or "default"
        j = i + 1
        while j < len(source) and (byte_labels[j] or "default") == label:
            j += 1
        tokens.append((label, source[i:j].decode("utf-8", errors="replace")))
        i = j

    # Upgrade generic variable tokens that are known builtins
    return [
        ("builtin", v) if label == "variable" and v in _BUILTINS else (label, v)
        for label, v in tokens
    ]
