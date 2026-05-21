# /build — Compile MindKiller to a Windows EXE

Build `process_killer_gui.exe` in the project root using PyInstaller.

## Steps

1. Verify `psutil` and `pyinstaller` are installed: `pip install -r requirements.txt --quiet`
2. Find the `.ico` file in the project root (glob `*.ico`, pick first match).
3. Run PyInstaller:
   ```
   pyinstaller --onefile --windowed --name process_killer_gui --icon=<ICO> process_killer_gui.py
   ```
4. Move `dist/process_killer_gui.exe` to the project root.
5. Delete `build/`, `dist/`, and `process_killer_gui.spec`.
6. Report the file size of the resulting `.exe`.

## Notes
- Never commit the `.exe` to git (it is in `.gitignore`).
- If PyInstaller is not found, install it first then retry.
- The EXE must be windowless (`--windowed`) — no console popup.
