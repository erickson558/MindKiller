# /add-language <code> — Add a new UI language

Add a new language to MindKiller's multi-language system.

## Argument
`<code>` — ISO 639-1 code, e.g. `pt` for Portuguese, `fr` for French.

## Steps

1. Open `process_killer_gui.py` and locate the `TRANSLATIONS` dict.
2. Copy the entire `'en'` block as a template for the new language.
3. Add the new language block under the copied block with key `'<code>'`.
4. Translate every value string to the target language.
   - Keep format placeholders like `{count}`, `{name}`, `{pid}` unchanged.
   - Keep emoji characters unchanged.
5. In `_build_menu → lang_menu` section, add:
   ```python
   lm.add_command(label=self.T('lang_<code>'), command=lambda: self._set_lang('<code>'))
   ```
6. Add `'lang_<code>'` keys to ALL existing language blocks in `TRANSLATIONS`
   with the language's own name in that language (e.g. for `pt`: `'lang_pt': 'Português'`).
7. Run a quick syntax check: `python -c "import process_killer_gui"`
8. Report which strings were translated and flag any that need human review.

## Rules
- Never remove or rename existing language keys.
- Keep all existing `'en'` and `'es'` entries intact.
