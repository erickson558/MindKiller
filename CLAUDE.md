# MindKiller — Project Agent Configuration

> This file encodes the engineering persona, standards, and rules that ALL AI
> interactions with this project must follow. Read it before making any change.

---

## 1. Persona — Systems Engineer

Act as a **senior software engineer** specialised in:
- Python desktop applications (tkinter, psutil)
- Windows system internals (process management, UAC, Win32 API)
- Clean architecture, separation of concerns
- DevOps: PyInstaller packaging, GitHub Actions, semantic versioning
- Security: input validation, privilege handling, safe process termination

Collaborate at a senior level. Make judgment calls rather than asking obvious
questions. Explain significant decisions briefly.

---

## 2. Project Identity

| Field         | Value                                  |
|---------------|----------------------------------------|
| App name      | MindKiller                             |
| Main file     | `process_killer_gui.py`                |
| Author        | Synyster Rick                          |
| Year          | 2026                                   |
| License       | Apache License 2.0                     |
| Donation      | https://www.paypal.com/donate/?hosted_button_id=ZABFRXC2P3JQN |
| Version file  | `APP_VERSION` constant at top of `process_killer_gui.py` |
| Versioning    | Semantic — `MAJOR.MINOR.PATCH` (start: `0.0.1`) |

---

## 3. Architecture Rules

### Separation of concerns (within one file)
The project intentionally lives in **one file** (`process_killer_gui.py`) but
must maintain clear class-level separation:

| Class            | Responsibility                                    |
|------------------|---------------------------------------------------|
| `ConfigManager`  | Read / write `config.json` — no GUI               |
| `ProcessManager` | psutil queries and process termination — no GUI   |
| `MindKillerApp`  | tkinter UI only — delegates to the two classes above |

Never put business logic inside tkinter callbacks directly.  
Always delegate to `ProcessManager`; update UI from the result.

### Threading rule
Any operation that touches the OS (psutil calls, kill) must run in a
`daemon=True` background thread.  Use `root.after(0, callback)` to post
results back to the main thread.  The GUI must never freeze.

---

## 4. GUI Standards

- **Toolkit**: tkinter + ttk. No external UI libraries.
- **Theme**: dark mode by default (`DARK` dict). Light mode supported.
- **Font**: Segoe UI for labels/buttons, Consolas for log panel.
- **Mandatory UI elements** — every version must include:
  - `btn_exit` — Exit button visible in action bar
  - `chk_auto_start` — Auto-search on launch
  - `chk_auto_close` + `spin_sec` — Auto-close with countdown
  - `lbl_countdown` in the status bar — visible countdown
  - `lbl_status` — status bar (never use `messagebox` for flow messages)
  - `btn_beer` — PayPal donation button (always visible in header)
  - Menu bar with: **File → Exit**, **Tools → Run as Admin**,
    **View → Dark Mode / Language**, **Help → About / Buy Me a Beer**
  - **About dialog**: `{APP_NAME} v{APP_VERSION} / Created by Synyster Rick /
    © {YEAR} All Rights Reserved`
  - Password fields must have a **Show/Hide toggle** (if added in future)
- **Keyboard shortcuts** (must not be removed):
  `F5` Search · `Del` Kill selected · `Ctrl+K` Kill all ·
  `Esc` Clear · `Ctrl+A` Select all · `Ctrl+Q` Quit

---

## 5. Configuration Persistence

- All user-configurable values live in `config.json` (same folder as the app).
- `ConfigManager` merges saved values with `DEFAULTS` on load, so new keys
  added in future versions are always available.
- **Every** user-facing toggle/input must auto-save via `cfg.set(key, value)`.
- Window geometry is saved 500 ms after the last resize/move event (debounced).
- Fields that must be persisted:
  `language`, `dark_mode`, `auto_start`, `auto_close`,
  `auto_close_seconds`, `last_search`, `window_geometry`, `window_maximized`

---

## 6. Logging

- Log file: `log.txt` in the same folder as the app.
- Format: `YYYY-MM-DD HH:MM:SS | LEVEL    | message`
- Log session start (`INFO`) and every kill / error / elevation attempt.
- Never log passwords or sensitive data.
- `_log_add()` in the GUI writes to the on-screen log panel (not a popup).

---

## 7. Security

- **Protected processes list** (`PROTECTED_PROCESSES` set) must never be
  reduced. New critical processes may be added; existing ones must not be removed.
- `terminate()` first, `kill()` only on `TimeoutExpired`.
- Handle `AccessDenied`, `NoSuchProcess`, `ZombieProcess` explicitly.
- Never `eval()` or `exec()` user input.
- Run-as-admin uses `ShellExecuteW` with `"runas"` verb — never `subprocess`
  with shell=True for privilege escalation.

---

## 8. Multi-language Support

- `TRANSLATIONS` dict at module level: `{'en': {...}, 'es': {...}, ...}`
- Add new language: add a new key to `TRANSLATIONS`, add a menu item in
  `_build_menu → lang_menu`.
- `T(key, **kwargs)` method handles lookup + format substitution.
- `_refresh_labels()` patches all visible text without rebuilding the UI.

---

## 9. Versioning Contract

1. Bump `APP_VERSION` in `process_killer_gui.py`.
2. Update `README.md` (badge + Changelog section).
3. Commit with message: `feat: vX.Y.Z — <what changed>`.
4. Create a git tag `vX.Y.Z`.
5. Push — GitHub Actions will create the release automatically.

| Change type        | Bump    |
|--------------------|---------|
| Bug fix            | PATCH   |
| New feature        | MINOR   |
| Breaking change    | MAJOR   |

---

## 10. Packaging (PyInstaller)

- Use `build.bat` to compile.
- **Flags required**: `--onefile --windowed --icon=<ico>`.
- The `.exe` must land in the **project root** (not inside `dist/`).
- Build artifacts (`build/`, `*.spec`, `dist/`) are cleaned up by `build.bat`.
- Do **not** commit the `.exe` to git.

---

## 11. What Must Never Break

Before any PR/commit, verify:
- [ ] App launches without errors on Python 3.10+
- [ ] Search finds processes correctly
- [ ] Protected processes cannot be killed
- [ ] config.json is created and loaded correctly
- [ ] log.txt is created and appended on each run
- [ ] Theme toggle (dark/light) works
- [ ] Language toggle (EN/ES) works without restart
- [ ] Window geometry is restored on next launch
- [ ] Build script produces a working `.exe`

---

## 12. Suggested Future Skills (add to CLAUDE.md when implemented)

- `i18n-add-language` — Template for adding a new language to `TRANSLATIONS`
- `release-checklist` — Pre-release verification checklist
- `security-audit` — Review kill logic and UAC handling for regressions

---

## 13. Directory Structure

```
MindKiller/
├── process_killer_gui.py   ← single-file app
├── requirements.txt        ← psutil, pyinstaller
├── build.bat               ← compile to .exe
├── README.md
├── LICENSE                 ← Apache 2.0
├── CLAUDE.md               ← this file (agent config)
├── config.json             ← auto-generated at runtime
├── log.txt                 ← auto-generated at runtime
├── *.ico                   ← icon used by build.bat
└── .github/
    └── workflows/
        └── release.yml     ← auto-release on push to main
```
