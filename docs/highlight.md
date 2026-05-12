# Syntax highlighting

Code slides use [tree-sitter](https://tree-sitter.github.io/) for syntax highlighting. It builds a real parse tree so it can distinguish things a regex lexer cannot: function definitions vs. calls, type annotations, method calls, PascalCase constructors, ALL\_CAPS constants, import names, and function parameters.

All highlighting logic lives in `util/highlight.py`.

## How it works

Highlighting runs in two passes:

**Pass 1 — AST query.** tree-sitter parses the snippet and a `highlights.scm` query (loaded from the installed language package, with custom patterns appended) labels every byte with a capture name: `@keyword`, `@function`, `@constructor`, `@type`, etc. Labels are painted in priority order from least to most specific, so later patterns overwrite earlier ones. For example, a PascalCase identifier first gets `@variable`, then `@constructor` overwrites it.

**Pass 2 — builtin upgrade.** Any token still labeled `variable` whose text matches a name in `_BUILTINS` is upgraded to `builtin`. This catches lowercase builtins like `list`, `str`, `dict` in type annotation positions (`-> list[Foo]`) where the query cannot reach them because they sit outside a call expression.

Colors are looked up by capture name from `_COLORS`. Any capture name not in `_COLORS` silently falls back to default text color — nothing breaks if a new name appears.

## Adding a language

1. Install the grammar package:
   ```bash
   uv add tree-sitter-<language>
   ```

2. Import it at the top of `util/highlight.py`:
   ```python
   import tree_sitter_javascript as tsjavascript
   ```

3. Add entries to the three language registries in `util/highlight.py`:
   ```python
   _LANG_PACKAGES["javascript"] = "tree_sitter_javascript"

   _JS_LANGUAGE = Language(tsjavascript.language())
   _LANGUAGES["javascript"] = _JS_LANGUAGE
   _PARSERS["javascript"]   = Parser(_JS_LANGUAGE)
   ```

4. Add any aliases if needed:
   ```python
   _LANG_ALIASES["js"] = "javascript"
   ```

The bundled `highlights.scm` from the grammar package covers most tokens automatically using the same standard capture names (`@keyword`, `@function`, `@string`, etc.). If something important is missing, add patterns to `_CUSTOM_PATTERNS["javascript"]` — see the Python entry there for the pattern syntax.

## Adjusting colors

All colors are catppuccin-mocha RGB tuples in `_COLORS` at the top of `util/highlight.py`. The capture name is the key; the value is `(r, g, b)`.

If a token renders in the wrong color, find its capture name first by adding a temporary debug print inside `tokenize()` just before the final return:

```python
for label, value in tokens:
    if value.strip():
        print(f"{label:<20} {value!r}")
```

Then either add the capture name to `_COLORS` or adjust where it sits in `_PRIORITY`.

## The priority system

`_PRIORITY` is a list of capture names ordered from least to most specific. The byte-painting loop processes them in order, with each pass overwriting the previous. Moving a name later in the list makes it win over everything before it.

A token can match multiple patterns — for example `Path` matches both `@variable` (generic identifier) and `@constructor` (PascalCase heuristic). Priority resolves the conflict: `constructor` sits after `variable` in `_PRIORITY`, so `constructor` wins.

If a token is rendering with the wrong color, the fix is almost always moving its capture name relative to another in `_PRIORITY`.

## Custom patterns

The bundled `highlights.scm` does not cover everything. `_CUSTOM_PATTERNS` in `util/highlight.py` holds extra `.scm` patterns appended per language. For Python these add:

- `@module` — identifiers inside import statements (lavender)
- `@parameter` — function definition parameters and call-site keyword argument names (maroon)

These use the same [tree-sitter query syntax](https://tree-sitter.github.io/tree-sitter/using-parsers/queries/1-syntax.html) as `highlights.scm`.
