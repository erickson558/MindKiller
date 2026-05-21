# 💀 MindKiller

![Version](https://img.shields.io/badge/version-0.0.1-e94560?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-0f3460?style=flat-square)
![Python](https://img.shields.io/badge/python-3.10%2B-00cec9?style=flat-square)
![License](https://img.shields.io/badge/license-Apache%202.0-fdcb6e?style=flat-square)

**MindKiller** is a modern, dark-themed Windows desktop tool that lets you
search for, inspect, and forcefully terminate any running process — without
touching the terminal.

---

## Features

- 🔍 **Smart process search** — fuzzy name matching, case-insensitive
- 💀 **Kill selected** or **kill all** matching processes
- 🔒 **Protected list** — system-critical processes (explorer, lsass, etc.)
  can never be killed accidentally
- 🌗 **Dark / Light theme** toggle
- 🌐 **Multi-language** — English & Español (easily extensible)
- ⚡ **Run as Administrator** in one click (UAC elevation)
- 📋 **Activity log** panel inside the app — no popup spam
- 💾 **Auto-saves** window position, theme, language, last search
- ⏱ **Auto-close countdown** configurable timer
- 🍺 **Buy Me a Beer** — [support the author](https://www.paypal.com/donate/?hosted_button_id=ZABFRXC2P3JQN)

---

## Requirements

| Dependency  | Version   |
|-------------|-----------|
| Python      | ≥ 3.10    |
| psutil      | ≥ 5.9.0   |
| PyInstaller | ≥ 6.0.0 *(build only)* |

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/erickson558/MindKiller.git
cd MindKiller

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python process_killer_gui.py
```

---

## Build (Windows EXE)

```batch
build.bat
```

This produces `process_killer_gui.exe` in the project root — no installer
needed, no console window.

---

## Keyboard Shortcuts

| Key       | Action                  |
|-----------|-------------------------|
| `F5`      | Search / Refresh        |
| `Del`     | Kill selected processes |
| `Ctrl+K`  | Kill all found          |
| `Esc`     | Clear search            |
| `Ctrl+A`  | Select all in list      |
| `Ctrl+Q`  | Quit                    |

---

## Configuration

Settings are auto-saved to `config.json` next to the app:

```json
{
  "language": "es",
  "dark_mode": true,
  "auto_start": false,
  "auto_close": false,
  "auto_close_seconds": 60,
  "last_search": "",
  "window_geometry": "960x680+120+80"
}
```

---

## Changelog

### v0.0.1 — 2026-05-21
- Initial release
- Search, kill selected, kill all
- Protected process list
- Dark / Light theme
- EN / ES multi-language
- Auto-save config, window position
- Auto-close countdown
- Admin elevation
- Activity log panel
- Buy Me a Beer button
- GitHub Actions auto-release

---

## License

Apache License 2.0 — see [LICENSE](LICENSE)

---

## Author

Created by **Synyster Rick**  
© 2026 All Rights Reserved

[![Buy Me a Beer](https://img.shields.io/badge/🍺%20Buy%20Me%20a%20Beer-PayPal-f6c90e?style=for-the-badge)](https://www.paypal.com/donate/?hosted_button_id=ZABFRXC2P3JQN)
