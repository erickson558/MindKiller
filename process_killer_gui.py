#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MindKiller v0.0.1
Process Management Tool for Windows
Created by Synyster Rick — 2026 All Rights Reserved
Apache License 2.0
"""

# ── Standard library ──────────────────────────────────────────────────────────
import ctypes
import json
import logging
import os
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ── Third-party ───────────────────────────────────────────────────────────────
import psutil
import tkinter as tk
from tkinter import ttk, messagebox

# ═════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═════════════════════════════════════════════════════════════════════════════
APP_VERSION   = "0.0.1"
APP_NAME      = "MindKiller"
AUTHOR        = "Synyster Rick"
YEAR          = "2026"
PAYPAL_URL    = "https://www.paypal.com/donate/?hosted_button_id=ZABFRXC2P3JQN"
APP_DIR       = (Path(sys.executable).parent
                 if getattr(sys, 'frozen', False)
                 else Path(__file__).parent)

# Windows processes that must never be killed
PROTECTED_PROCESSES = {
    'explorer.exe', 'winlogon.exe', 'csrss.exe', 'services.exe',
    'lsass.exe', 'system', 'smss.exe', 'wininit.exe', 'svchost.exe',
    'dwm.exe', 'fontdrvhost.exe', 'memory compression', 'registry',
    'ntoskrnl.exe', 'taskmgr.exe',
}

# ═════════════════════════════════════════════════════════════════════════════
# TRANSLATIONS
# ═════════════════════════════════════════════════════════════════════════════
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'en': {
        'title':                f'{APP_NAME} - Process Killer',
        'search_label':         'Process Name:',
        'search_placeholder':   'e.g. chrome, zoom, teams...',
        'btn_search':           'Search  [F5]',
        'btn_kill_selected':    'Kill Selected  [Del]',
        'btn_kill_all':         'Kill All  [Ctrl+K]',
        'btn_refresh':          'Refresh  [F5]',
        'btn_clear':            'Clear  [Esc]',
        'btn_run_as_admin':     '⚡ Run as Administrator',
        'btn_beer':             '🍺 Buy Me a Beer',
        'btn_exit':             'Exit',
        'menu_file':            'File',
        'menu_exit':            'Exit  Alt+F4',
        'menu_tools':           'Tools',
        'menu_run_admin':       'Run as Administrator',
        'menu_view':            'View',
        'menu_dark_mode':       'Dark Mode',
        'menu_language':        'Language',
        'menu_help':            'Help',
        'menu_about':           'About',
        'col_name':             'Process Name',
        'col_pid':              'PID',
        'col_path':             'Executable Path',
        'col_status':           'Status',
        'auto_start':           'Auto-search on launch',
        'auto_close':           'Auto-close in',
        'seconds':              'sec',
        'status_ready':         'Ready — enter a process name and press Search or F5.',
        'status_searching':     'Searching for processes…',
        'status_found':         '{count} process(es) found for "{name}"',
        'status_not_found':     'No processes found for "{name}"',
        'status_killed':        '✓ {name} (PID:{pid}) terminated.',
        'status_kill_error':    '✗ Error terminating {name}: {error}',
        'status_protected':     '🔒 {name} is a protected system process — skipped.',
        'confirm_kill_sel':     'Terminate {count} selected process(es)?',
        'confirm_kill_all':     'Terminate ALL {count} process(es) related to "{name}"?\n\nThis cannot be undone.',
        'confirm_title':        'Confirm Action',
        'about_title':          'About MindKiller',
        'autoclosing':          '⏱ Auto-closing in {n}s…',
        'no_selection':         'Select at least one process first.',
        'no_results':           'No processes in the list.',
        'all_protected':        'All found processes are protected — nothing killed.',
        'lang_en':              'English',
        'lang_es':              'Español',
        'log_header':           'Activity Log',
    },
    'es': {
        'title':                f'{APP_NAME} - Matador de Procesos',
        'search_label':         'Nombre del Proceso:',
        'search_placeholder':   'ej. chrome, zoom, teams...',
        'btn_search':           'Buscar  [F5]',
        'btn_kill_selected':    'Matar Seleccionados  [Del]',
        'btn_kill_all':         'Matar Todos  [Ctrl+K]',
        'btn_refresh':          'Refrescar  [F5]',
        'btn_clear':            'Limpiar  [Esc]',
        'btn_run_as_admin':     '⚡ Ejecutar como Administrador',
        'btn_beer':             '🍺 Cómprame una Cerveza',
        'btn_exit':             'Salir',
        'menu_file':            'Archivo',
        'menu_exit':            'Salir  Alt+F4',
        'menu_tools':           'Herramientas',
        'menu_run_admin':       'Ejecutar como Administrador',
        'menu_view':            'Ver',
        'menu_dark_mode':       'Modo Oscuro',
        'menu_language':        'Idioma',
        'menu_help':            'Ayuda',
        'menu_about':           'Acerca de',
        'col_name':             'Nombre del Proceso',
        'col_pid':              'PID',
        'col_path':             'Ruta del Ejecutable',
        'col_status':           'Estado',
        'auto_start':           'Buscar al iniciar',
        'auto_close':           'Cerrar en',
        'seconds':              'seg',
        'status_ready':         'Listo — ingrese un nombre de proceso y presione Buscar o F5.',
        'status_searching':     'Buscando procesos…',
        'status_found':         'Se encontraron {count} proceso(s) para "{name}"',
        'status_not_found':     'No se encontraron procesos para "{name}"',
        'status_killed':        '✓ {name} (PID:{pid}) terminado.',
        'status_kill_error':    '✗ Error al terminar {name}: {error}',
        'status_protected':     '🔒 {name} es un proceso del sistema protegido — omitido.',
        'confirm_kill_sel':     '¿Terminar {count} proceso(s) seleccionado(s)?',
        'confirm_kill_all':     '¿Terminar TODOS los {count} proceso(s) relacionados con "{name}"?\n\nEsta acción no se puede deshacer.',
        'confirm_title':        'Confirmar Acción',
        'about_title':          'Acerca de MindKiller',
        'autoclosing':          '⏱ Cerrando en {n}s…',
        'no_selection':         'Seleccione al menos un proceso.',
        'no_results':           'No hay procesos en la lista.',
        'all_protected':        'Todos los procesos encontrados están protegidos — nada fue terminado.',
        'lang_en':              'English',
        'lang_es':              'Español',
        'log_header':           'Registro de Actividad',
    },
}

# ═════════════════════════════════════════════════════════════════════════════
# THEMES
# ═════════════════════════════════════════════════════════════════════════════
DARK: Dict[str, str] = {
    'bg':           '#12121f',
    'bg2':          '#1a1a2e',
    'bg3':          '#0f3460',
    'accent':       '#e94560',
    'accent_h':     '#c73652',
    'success':      '#00cec9',
    'warning':      '#fdcb6e',
    'danger':       '#e94560',
    'text':         '#eaeaea',
    'text2':        '#8a8ab0',
    'border':       '#2d2d5e',
    'tree_bg':      '#1a1a2e',
    'tree_fg':      '#eaeaea',
    'tree_sel':     '#e94560',
    'entry_bg':     '#1a1a2e',
    'entry_fg':     '#eaeaea',
    'status_bg':    '#0a0a14',
    'log_bg':       '#12121f',
    'log_fg':       '#7f7fa8',
}

LIGHT: Dict[str, str] = {
    'bg':           '#f0f2f5',
    'bg2':          '#ffffff',
    'bg3':          '#dfe6e9',
    'accent':       '#d63031',
    'accent_h':     '#b52929',
    'success':      '#00b894',
    'warning':      '#e17055',
    'danger':       '#d63031',
    'text':         '#2d3436',
    'text2':        '#636e72',
    'border':       '#dfe6e9',
    'tree_bg':      '#ffffff',
    'tree_fg':      '#2d3436',
    'tree_sel':     '#d63031',
    'entry_bg':     '#ffffff',
    'entry_fg':     '#2d3436',
    'status_bg':    '#dfe6e9',
    'log_bg':       '#f5f5f5',
    'log_fg':       '#636e72',
}


# ═════════════════════════════════════════════════════════════════════════════
# CONFIGURATION MANAGER
# ═════════════════════════════════════════════════════════════════════════════
class ConfigManager:
    """Reads and writes persistent config.json next to the app."""

    DEFAULTS: Dict = {
        'language':           'es',
        'dark_mode':          True,
        'auto_start':         False,
        'auto_close':         False,
        'auto_close_seconds': 60,
        'last_search':        '',
        'window_geometry':    '960x680+120+80',
        'window_maximized':   False,
        'version':            APP_VERSION,
    }

    def __init__(self):
        self.path = APP_DIR / 'config.json'
        self.data = self._load()

    def _load(self) -> Dict:
        if self.path.exists():
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                merged = dict(self.DEFAULTS)
                merged.update(saved)
                return merged
            except Exception as exc:
                logging.warning(f'Config load failed ({exc}), using defaults')
        return dict(self.DEFAULTS)

    def save(self):
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as exc:
            logging.error(f'Config save failed: {exc}')

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value):
        self.data[key] = value
        self.save()


# ═════════════════════════════════════════════════════════════════════════════
# LOGGER
# ═════════════════════════════════════════════════════════════════════════════
def setup_logger() -> logging.Logger:
    log_path = APP_DIR / 'log.txt'
    logger   = logging.getLogger(APP_NAME)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        fh = logging.FileHandler(log_path, encoding='utf-8')
        fh.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        ))
        logger.addHandler(fh)

    return logger


# ═════════════════════════════════════════════════════════════════════════════
# PROCESS MANAGER  (pure backend — no GUI calls)
# ═════════════════════════════════════════════════════════════════════════════
class ProcessManager:
    """Discovers and terminates OS processes."""

    def __init__(self, logger: logging.Logger):
        self._log = logger

    @staticmethod
    def is_protected(name: str) -> bool:
        return name.lower() in PROTECTED_PROCESSES

    def find(self, term: str) -> List[Dict]:
        """Return list of process dicts whose name contains *term*."""
        term_l  = term.lower().strip()
        results = []

        for proc in psutil.process_iter(['pid', 'name', 'exe', 'status']):
            try:
                info = proc.info
                name = (info.get('name') or '').strip()
                if term_l in name.lower():
                    results.append({
                        'name':      name,
                        'pid':       info['pid'],
                        'exe':       info.get('exe') or 'N/A',
                        'status':    info.get('status') or 'unknown',
                        'protected': self.is_protected(name),
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        self._log.info(f"Search '{term}': {len(results)} result(s)")
        return results

    def kill(self, pid: int, name: str) -> Tuple[bool, str]:
        """
        Try terminate(); escalate to kill() on timeout.
        Returns (success, reason_key).
        """
        if self.is_protected(name):
            self._log.warning(f"Skipped protected process '{name}' PID:{pid}")
            return False, 'protected'

        try:
            proc = psutil.Process(pid)
            proc.terminate()
            try:
                proc.wait(timeout=3)
                self._log.info(f"Terminated '{name}' PID:{pid} gracefully")
                return True, 'success'
            except psutil.TimeoutExpired:
                proc.kill()
                self._log.info(f"Force-killed '{name}' PID:{pid}")
                return True, 'success'

        except psutil.AccessDenied as exc:
            self._log.error(f"Access denied '{name}' PID:{pid}: {exc}")
            return False, 'access_denied'
        except psutil.NoSuchProcess:
            self._log.info(f"Process already gone: '{name}' PID:{pid}")
            return True, 'already_gone'
        except psutil.ZombieProcess:
            self._log.warning(f"Zombie process: '{name}' PID:{pid}")
            return False, 'zombie'
        except Exception as exc:
            self._log.error(f"Unexpected error '{name}' PID:{pid}: {exc}")
            return False, str(exc)


# ═════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION  (GUI frontend)
# ═════════════════════════════════════════════════════════════════════════════
class MindKillerApp:
    """Main tkinter application window."""

    # ── init ──────────────────────────────────────────────────────────────────
    def __init__(self, root: tk.Tk):
        self.root    = root
        self.logger  = setup_logger()
        self.cfg     = ConfigManager()
        self.backend = ProcessManager(self.logger)

        # State vars
        self.dark_mode      = tk.BooleanVar(value=self.cfg.get('dark_mode', True))
        self.lang           = self.cfg.get('language', 'es')
        self.auto_start_v   = tk.BooleanVar(value=self.cfg.get('auto_start', False))
        self.auto_close_v   = tk.BooleanVar(value=self.cfg.get('auto_close', False))
        self.auto_close_sec = tk.IntVar(value=self.cfg.get('auto_close_seconds', 60))
        self.search_v       = tk.StringVar(value=self.cfg.get('last_search', ''))

        self._countdown_active    = False
        self._countdown_remaining = 0
        self._geo_timer: Optional[str] = None
        self._processes: List[Dict]    = []   # last search results

        self.logger.info('=' * 60)
        self.logger.info(f'{APP_NAME} v{APP_VERSION} starting | admin={self._is_admin()}')

        self._setup_window()
        self._build_ui()
        self._apply_theme()
        self._bind_keys()
        self._restore_geometry()

        # Post-init triggers
        if self.auto_start_v.get() and self.search_v.get():
            self.root.after(600, self._search)
        if self.auto_close_v.get():
            self._start_countdown()

    # ── translation helper ────────────────────────────────────────────────────
    def T(self, key: str, **kw) -> str:
        text = TRANSLATIONS.get(self.lang, TRANSLATIONS['es']).get(key, key)
        return text.format(**kw) if kw else text

    # ── admin helpers ─────────────────────────────────────────────────────────
    def _is_admin(self) -> bool:
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False

    def _run_as_admin(self):
        script = sys.executable if getattr(sys, 'frozen', False) else __file__
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, 'runas', sys.executable, f'"{script}"', None, 1
            )
            self.root.quit()
        except Exception as exc:
            self.logger.error(f'Elevation failed: {exc}')
            self._status(f'Elevation failed: {exc}', 'danger')

    # ── window setup ──────────────────────────────────────────────────────────
    def _setup_window(self):
        self.root.title(f'{APP_NAME}  v{APP_VERSION}')
        self.root.minsize(760, 560)

        # Use the .ico in the project folder
        for ico in ['mindkiller.ico', 'task_update_folder_progress_icon_142270.ico']:
            ico_path = APP_DIR / ico
            if ico_path.exists():
                try:
                    self.root.iconbitmap(str(ico_path))
                except Exception:
                    pass
                break

        self.root.protocol('WM_DELETE_WINDOW', self._on_close)

    def _restore_geometry(self):
        geo = self.cfg.get('window_geometry', '960x680+120+80')
        try:
            self.root.geometry(geo)
            if self.cfg.get('window_maximized', False):
                self.root.state('zoomed')
        except Exception:
            self.root.geometry('960x680+120+80')

        self.root.bind('<Configure>', self._on_configure)

    def _on_configure(self, event):
        if event.widget is not self.root:
            return
        if self._geo_timer:
            self.root.after_cancel(self._geo_timer)
        self._geo_timer = self.root.after(500, self._save_geometry)

    def _save_geometry(self):
        state = self.root.state()
        self.cfg.data['window_maximized'] = (state == 'zoomed')
        if state != 'zoomed':
            self.cfg.data['window_geometry'] = self.root.geometry()
        self.cfg.save()

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_menu()

        self.main = tk.Frame(self.root)
        self.main.pack(fill='both', expand=True)

        self._build_header()
        self._build_search_bar()
        self._build_options_bar()
        self._build_process_list()
        self._build_action_buttons()
        self._build_log_panel()
        self._build_status_bar()

    # ── menu ──────────────────────────────────────────────────────────────────
    def _build_menu(self):
        mb = tk.Menu(self.root)
        self.root.config(menu=mb)
        self._mb = mb

        # File
        fm = tk.Menu(mb, tearoff=0)
        mb.add_cascade(label=self.T('menu_file'), menu=fm)
        fm.add_command(label=self.T('menu_exit'), command=self._on_close)
        self._fm = fm

        # Tools
        tm = tk.Menu(mb, tearoff=0)
        mb.add_cascade(label=self.T('menu_tools'), menu=tm)
        tm.add_command(label=self.T('menu_run_admin'), command=self._run_as_admin)
        self._tm = tm

        # View
        vm = tk.Menu(mb, tearoff=0)
        mb.add_cascade(label=self.T('menu_view'), menu=vm)
        vm.add_checkbutton(label=self.T('menu_dark_mode'), variable=self.dark_mode,
                           command=self._toggle_theme)
        lm = tk.Menu(vm, tearoff=0)
        vm.add_cascade(label=self.T('menu_language'), menu=lm)
        lm.add_command(label=self.T('lang_en'), command=lambda: self._set_lang('en'))
        lm.add_command(label=self.T('lang_es'), command=lambda: self._set_lang('es'))
        self._vm, self._lm = vm, lm

        # Help
        hm = tk.Menu(mb, tearoff=0)
        mb.add_cascade(label=self.T('menu_help'), menu=hm)
        hm.add_command(label=self.T('menu_about'), command=self._show_about)
        hm.add_separator()
        hm.add_command(label=self.T('btn_beer'), command=self._open_beer)
        self._hm = hm

    # ── header ────────────────────────────────────────────────────────────────
    def _build_header(self):
        self.hdr = tk.Frame(self.main)
        self.hdr.pack(fill='x')

        self.lbl_skull = tk.Label(self.hdr, text='💀', font=('Segoe UI', 28))
        self.lbl_skull.pack(side='left', padx=(16, 4), pady=8)

        self.lbl_title = tk.Label(self.hdr, text=APP_NAME,
                                  font=('Segoe UI', 22, 'bold'))
        self.lbl_title.pack(side='left', pady=8)

        ver_frame = tk.Frame(self.hdr)
        ver_frame.pack(side='left', padx=10, pady=6)

        self.lbl_ver = tk.Label(ver_frame, text=f'v{APP_VERSION}',
                                font=('Segoe UI', 9))
        self.lbl_ver.pack()

        admin_txt = '⚡ ADMIN' if self._is_admin() else '⚠ USER'
        self.lbl_admin = tk.Label(ver_frame, text=admin_txt,
                                  font=('Segoe UI', 8, 'bold'))
        self.lbl_admin.pack()

        # Right-side header buttons
        rframe = tk.Frame(self.hdr)
        rframe.pack(side='right', padx=10)

        self.btn_beer = tk.Button(rframe, text=self.T('btn_beer'),
                                  command=self._open_beer,
                                  relief='flat', cursor='hand2',
                                  font=('Segoe UI', 9), padx=10, pady=4)
        self.btn_beer.pack(side='right', padx=4, pady=8)

        if not self._is_admin():
            self.btn_admin_hdr = tk.Button(rframe, text=self.T('btn_run_as_admin'),
                                           command=self._run_as_admin,
                                           relief='flat', cursor='hand2',
                                           font=('Segoe UI', 9, 'bold'),
                                           padx=10, pady=4)
            self.btn_admin_hdr.pack(side='right', padx=4, pady=8)
        else:
            self.btn_admin_hdr = None

        # Accent separator
        self.sep = tk.Frame(self.main, height=3)
        self.sep.pack(fill='x')

    # ── search bar ────────────────────────────────────────────────────────────
    def _build_search_bar(self):
        self.sf = tk.Frame(self.main)
        self.sf.pack(fill='x', padx=16, pady=(12, 4))

        self.lbl_search = tk.Label(self.sf, text=self.T('search_label'),
                                   font=('Segoe UI', 11))
        self.lbl_search.pack(side='left', padx=(0, 8))

        self.entry_search = tk.Entry(self.sf, textvariable=self.search_v,
                                     font=('Segoe UI', 12), relief='flat',
                                     bd=0, width=32)
        self.entry_search.pack(side='left', ipady=7, padx=(0, 10))
        self.entry_search.bind('<Return>', lambda _: self._search())

        self.btn_search = tk.Button(self.sf, text=self.T('btn_search'),
                                    command=self._search,
                                    relief='flat', cursor='hand2',
                                    font=('Segoe UI', 10, 'bold'),
                                    padx=14, pady=5)
        self.btn_search.pack(side='left', padx=3)

        self.btn_clear = tk.Button(self.sf, text=self.T('btn_clear'),
                                   command=self._clear,
                                   relief='flat', cursor='hand2',
                                   font=('Segoe UI', 10),
                                   padx=14, pady=5)
        self.btn_clear.pack(side='left', padx=3)

    # ── options bar ───────────────────────────────────────────────────────────
    def _build_options_bar(self):
        self.of = tk.Frame(self.main)
        self.of.pack(fill='x', padx=16, pady=2)

        self.chk_auto_start = tk.Checkbutton(
            self.of, text=self.T('auto_start'),
            variable=self.auto_start_v,
            command=lambda: self.cfg.set('auto_start', self.auto_start_v.get()),
            font=('Segoe UI', 9))
        self.chk_auto_start.pack(side='left', padx=(0, 18))

        self.chk_auto_close = tk.Checkbutton(
            self.of, text=self.T('auto_close'),
            variable=self.auto_close_v,
            command=self._on_auto_close_toggle,
            font=('Segoe UI', 9))
        self.chk_auto_close.pack(side='left')

        self.spin_sec = tk.Spinbox(
            self.of, from_=5, to=3600,
            textvariable=self.auto_close_sec,
            width=5, font=('Segoe UI', 9), relief='flat',
            command=self._on_auto_close_sec_change)
        self.spin_sec.pack(side='left', padx=4, ipady=2)

        self.lbl_sec = tk.Label(self.of, text=self.T('seconds'),
                                font=('Segoe UI', 9))
        self.lbl_sec.pack(side='left')

    # ── process list ──────────────────────────────────────────────────────────
    def _build_process_list(self):
        cont = tk.Frame(self.main)
        cont.pack(fill='both', expand=True, padx=16, pady=6)

        inner = tk.Frame(cont)
        inner.pack(fill='both', expand=True)

        cols = ('name', 'pid', 'path', 'status')
        self.tree = ttk.Treeview(inner, columns=cols, show='headings',
                                 selectmode='extended')

        self.tree.heading('name',   text=self.T('col_name'),   anchor='w')
        self.tree.heading('pid',    text=self.T('col_pid'),     anchor='center')
        self.tree.heading('path',   text=self.T('col_path'),    anchor='w')
        self.tree.heading('status', text=self.T('col_status'),  anchor='center')

        self.tree.column('name',   width=190, minwidth=130)
        self.tree.column('pid',    width=80,  minwidth=60,  anchor='center')
        self.tree.column('path',   width=440, minwidth=200)
        self.tree.column('status', width=110, minwidth=80,  anchor='center')

        vsb = ttk.Scrollbar(inner, orient='vertical',   command=self.tree.yview)
        hsb = ttk.Scrollbar(inner, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        inner.grid_rowconfigure(0, weight=1)
        inner.grid_columnconfigure(0, weight=1)

        # Tag colors
        self.tree.tag_configure('protected', foreground='#fdcb6e')

    # ── action buttons ────────────────────────────────────────────────────────
    def _build_action_buttons(self):
        self.bf = tk.Frame(self.main)
        self.bf.pack(fill='x', padx=16, pady=4)

        self.btn_kill_sel = tk.Button(self.bf, text=self.T('btn_kill_selected'),
                                      command=self._kill_selected,
                                      relief='flat', cursor='hand2',
                                      font=('Segoe UI', 10, 'bold'),
                                      padx=14, pady=6)
        self.btn_kill_sel.pack(side='left', padx=(0, 6))

        self.btn_kill_all = tk.Button(self.bf, text=self.T('btn_kill_all'),
                                      command=self._kill_all,
                                      relief='flat', cursor='hand2',
                                      font=('Segoe UI', 10, 'bold'),
                                      padx=14, pady=6)
        self.btn_kill_all.pack(side='left', padx=4)

        self.btn_refresh = tk.Button(self.bf, text=self.T('btn_refresh'),
                                     command=self._search,
                                     relief='flat', cursor='hand2',
                                     font=('Segoe UI', 10),
                                     padx=14, pady=6)
        self.btn_refresh.pack(side='left', padx=4)

        self.btn_exit = tk.Button(self.bf, text=self.T('btn_exit'),
                                  command=self._on_close,
                                  relief='flat', cursor='hand2',
                                  font=('Segoe UI', 10),
                                  padx=14, pady=6)
        self.btn_exit.pack(side='right', padx=4)

    # ── log panel ─────────────────────────────────────────────────────────────
    def _build_log_panel(self):
        self.log_frame = tk.LabelFrame(self.main,
                                       text=f'  {self.T("log_header")}  ',
                                       font=('Segoe UI', 9))
        self.log_frame.pack(fill='x', padx=16, pady=(2, 4))

        self.log_txt = tk.Text(self.log_frame, height=5,
                               font=('Consolas', 9), wrap='word',
                               state='disabled', relief='flat', bd=0)
        log_sb = ttk.Scrollbar(self.log_frame, orient='vertical',
                               command=self.log_txt.yview)
        self.log_txt.configure(yscrollcommand=log_sb.set)
        self.log_txt.pack(side='left', fill='both', expand=True, padx=4, pady=4)
        log_sb.pack(side='right', fill='y', pady=4)

    # ── status bar ────────────────────────────────────────────────────────────
    def _build_status_bar(self):
        self.sb = tk.Frame(self.main)
        self.sb.pack(fill='x', side='bottom')

        self.lbl_status = tk.Label(self.sb, text=self.T('status_ready'),
                                   font=('Segoe UI', 9), anchor='w')
        self.lbl_status.pack(side='left', fill='x', expand=True, padx=8, pady=4)

        self.lbl_countdown = tk.Label(self.sb, text='',
                                      font=('Segoe UI', 9, 'bold'), anchor='e')
        self.lbl_countdown.pack(side='right', padx=8, pady=4)

    # ── theme ─────────────────────────────────────────────────────────────────
    def _apply_theme(self):
        th = DARK if self.dark_mode.get() else LIGHT

        self.root.configure(bg=th['bg'])
        for w in (self.main, self.sf, self.of, self.bf, self.sb):
            w.configure(bg=th['bg'])

        # Header
        self.hdr.configure(bg=th['bg3'])
        self.sep.configure(bg=th['accent'])
        self.lbl_skull.configure(bg=th['bg3'], fg=th['accent'])
        self.lbl_title.configure(bg=th['bg3'], fg=th['text'])
        self.lbl_ver.configure(bg=th['bg3'], fg=th['text2'])
        self.lbl_admin.configure(
            bg=th['bg3'],
            fg=th['success'] if self._is_admin() else th['warning'])

        # Labels / checkboxes
        for lbl in (self.lbl_search, self.lbl_sec):
            lbl.configure(bg=th['bg'], fg=th['text'])
        for chk in (self.chk_auto_start, self.chk_auto_close):
            chk.configure(bg=th['bg'], fg=th['text'],
                          activebackground=th['bg'], activeforeground=th['text'],
                          selectcolor=th['bg2'])
        self.spin_sec.configure(bg=th['entry_bg'], fg=th['entry_fg'],
                                buttonbackground=th['bg2'],
                                insertbackground=th['text'])
        self.entry_search.configure(bg=th['entry_bg'], fg=th['entry_fg'],
                                    insertbackground=th['text'])

        # Action buttons
        self.btn_search.configure(bg=th['accent'],   fg='white',
                                  activebackground=th['accent_h'],
                                  activeforeground='white')
        self.btn_clear.configure(bg=th['bg2'],  fg=th['text'],
                                 activebackground=th['bg3'],
                                 activeforeground=th['text'])
        self.btn_kill_sel.configure(bg=th['danger'], fg='white',
                                    activebackground=th['accent_h'],
                                    activeforeground='white')
        self.btn_kill_all.configure(bg=th['danger'], fg='white',
                                    activebackground=th['accent_h'],
                                    activeforeground='white')
        self.btn_refresh.configure(bg=th['success'], fg='white',
                                   activebackground='#00a880',
                                   activeforeground='white')
        self.btn_exit.configure(bg=th['bg2'], fg=th['text'],
                                activebackground=th['bg3'],
                                activeforeground=th['text'])
        self.btn_beer.configure(bg='#f6c90e', fg='#1a1a1a',
                                activebackground='#e5b800',
                                activeforeground='#1a1a1a')
        if self.btn_admin_hdr:
            self.btn_admin_hdr.configure(bg=th['warning'], fg='#1a1a1a',
                                         activebackground='#e5b800',
                                         activeforeground='#1a1a1a')

        # Log panel
        self.log_frame.configure(bg=th['bg'], fg=th['text2'])
        self.log_txt.configure(bg=th['log_bg'], fg=th['log_fg'],
                               insertbackground=th['text'])

        # Status bar
        self.sb.configure(bg=th['status_bg'])
        self.lbl_status.configure(bg=th['status_bg'], fg=th['text2'])
        self.lbl_countdown.configure(bg=th['status_bg'], fg=th['warning'])

        # Treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background=th['tree_bg'],
                        foreground=th['tree_fg'], fieldbackground=th['tree_bg'],
                        borderwidth=0, font=('Segoe UI', 10), rowheight=27)
        style.configure('Treeview.Heading', background=th['bg3'],
                        foreground=th['text'], font=('Segoe UI', 10, 'bold'),
                        borderwidth=0)
        style.map('Treeview',
                  background=[('selected', th['tree_sel'])],
                  foreground=[('selected', 'white')])
        style.map('Treeview.Heading',
                  background=[('active', th['accent'])])
        for sb_style in ('Vertical.TScrollbar', 'Horizontal.TScrollbar'):
            style.configure(sb_style, background=th['bg2'],
                            troughcolor=th['bg'], bordercolor=th['border'],
                            arrowcolor=th['text2'])

    def _toggle_theme(self):
        self.cfg.set('dark_mode', self.dark_mode.get())
        self._apply_theme()
        self._log_add('Dark mode: ON' if self.dark_mode.get() else 'Light mode: ON')

    # ── language ──────────────────────────────────────────────────────────────
    def _set_lang(self, lang: str):
        if lang == self.lang:
            return
        self.lang = lang
        self.cfg.set('language', lang)
        self._refresh_labels()
        self._log_add(f'Language: {lang}')

    def _refresh_labels(self):
        """Patch all visible text strings without rebuilding the whole UI."""
        self.root.title(f'{APP_NAME}  v{APP_VERSION}')
        self.lbl_search.configure(text=self.T('search_label'))
        self.btn_search.configure(text=self.T('btn_search'))
        self.btn_clear.configure(text=self.T('btn_clear'))
        self.btn_kill_sel.configure(text=self.T('btn_kill_selected'))
        self.btn_kill_all.configure(text=self.T('btn_kill_all'))
        self.btn_refresh.configure(text=self.T('btn_refresh'))
        self.btn_exit.configure(text=self.T('btn_exit'))
        self.btn_beer.configure(text=self.T('btn_beer'))
        self.chk_auto_start.configure(text=self.T('auto_start'))
        self.chk_auto_close.configure(text=self.T('auto_close'))
        self.lbl_sec.configure(text=self.T('seconds'))
        self.log_frame.configure(text=f'  {self.T("log_header")}  ')
        self.tree.heading('name',   text=self.T('col_name'))
        self.tree.heading('pid',    text=self.T('col_pid'))
        self.tree.heading('path',   text=self.T('col_path'))
        self.tree.heading('status', text=self.T('col_status'))
        # Menus
        self._mb.entryconfig(0, label=self.T('menu_file'))
        self._mb.entryconfig(1, label=self.T('menu_tools'))
        self._mb.entryconfig(2, label=self.T('menu_view'))
        self._mb.entryconfig(3, label=self.T('menu_help'))
        self._status(self.T('status_ready'))

    # ── keyboard shortcuts ────────────────────────────────────────────────────
    def _bind_keys(self):
        self.root.bind('<F5>',          lambda _: self._search())
        self.root.bind('<Delete>',      lambda _: self._kill_selected())
        self.root.bind('<Control-k>',   lambda _: self._kill_all())
        self.root.bind('<Escape>',      lambda _: self._clear())
        self.root.bind('<Control-q>',   lambda _: self._on_close())
        self.root.bind('<Control-a>',   lambda _: self._select_all())

    def _select_all(self):
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    # ── search & list ─────────────────────────────────────────────────────────
    def _search(self, _event=None):
        term = self.search_v.get().strip()
        if not term:
            self._status(self.T('status_ready'))
            return
        self.cfg.set('last_search', term)
        self._status(self.T('status_searching'))
        self._clear_tree()

        def _worker():
            procs = self.backend.find(term)
            self.root.after(0, lambda: self._fill_tree(procs, term))

        threading.Thread(target=_worker, daemon=True).start()

    def _clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._processes.clear()

    def _fill_tree(self, procs: List[Dict], term: str):
        self._processes = procs
        for p in procs:
            tag = 'protected' if p['protected'] else ''
            self.tree.insert('', 'end', values=(
                p['name'], p['pid'], p['exe'],
                f"{'🔒 ' if p['protected'] else ''}{p['status']}",
            ), tags=(tag,))

        if procs:
            self._status(self.T('status_found', count=len(procs), name=term))
            self._log_add(f"Found {len(procs)} process(es) for '{term}'")
        else:
            self._status(self.T('status_not_found', name=term))
            self._log_add(f"No results for '{term}'")

    def _clear(self):
        self.search_v.set('')
        self._clear_tree()
        self._status(self.T('status_ready'))
        self.entry_search.focus()

    # ── kill actions ──────────────────────────────────────────────────────────
    def _kill_selected(self):
        selected = self.tree.selection()
        if not selected:
            self._status(self.T('no_selection'), 'warning')
            return
        count = len(selected)
        if not messagebox.askyesno(self.T('confirm_title'),
                                   self.T('confirm_kill_sel', count=count),
                                   parent=self.root):
            return

        targets = [(self.tree.item(i, 'values')[0],
                    int(self.tree.item(i, 'values')[1])) for i in selected]

        def _worker():
            for name, pid in targets:
                ok, reason = self.backend.kill(pid, name)
                if reason == 'protected':
                    self.root.after(0, lambda n=name:
                        self._status(self.T('status_protected', name=n), 'warning'))
                elif ok:
                    self.root.after(0, lambda n=name, p=pid: (
                        self._status(self.T('status_killed', name=n, pid=p), 'success'),
                        self._log_add(f'Killed: {n} PID:{p}')))
                else:
                    self.root.after(0, lambda n=name, r=reason: (
                        self._status(self.T('status_kill_error', name=n, error=r), 'danger'),
                        self._log_add(f'Error: {n} — {r}')))
            self.root.after(150, self._search)

        threading.Thread(target=_worker, daemon=True).start()

    def _kill_all(self):
        if not self._processes:
            self._status(self.T('no_results'), 'warning')
            return
        term     = self.search_v.get().strip()
        killable = [p for p in self._processes if not p['protected']]
        if not killable:
            self._status(self.T('all_protected'), 'warning')
            return
        if not messagebox.askyesno(self.T('confirm_title'),
                                   self.T('confirm_kill_all',
                                          count=len(killable), name=term),
                                   parent=self.root):
            return

        def _worker():
            killed = 0
            for p in killable:
                ok, _ = self.backend.kill(p['pid'], p['name'])
                if ok:
                    killed += 1
            self.root.after(0, lambda:
                self._log_add(f"Kill-all: {killed}/{len(killable)} terminated for '{term}'"))
            self.root.after(150, self._search)

        threading.Thread(target=_worker, daemon=True).start()

    # ── status / log helpers ──────────────────────────────────────────────────
    def _status(self, msg: str, level: str = 'info'):
        th = DARK if self.dark_mode.get() else LIGHT
        colors = {'info':    th['text2'],
                  'success': th['success'],
                  'warning': th['warning'],
                  'danger':  th['accent']}
        self.lbl_status.configure(text=msg, fg=colors.get(level, th['text2']))

    def _log_add(self, msg: str):
        ts = datetime.now().strftime('%H:%M:%S')
        self.log_txt.configure(state='normal')
        self.log_txt.insert('end', f'[{ts}] {msg}\n')
        self.log_txt.configure(state='disabled')
        self.log_txt.see('end')

    # ── auto-close countdown ──────────────────────────────────────────────────
    def _start_countdown(self):
        self._countdown_active    = True
        self._countdown_remaining = self.auto_close_sec.get()
        self._tick()

    def _tick(self):
        if not self._countdown_active or not self.auto_close_v.get():
            self.lbl_countdown.configure(text='')
            return
        if self._countdown_remaining <= 0:
            self._on_close()
            return
        self.lbl_countdown.configure(
            text=self.T('autoclosing', n=self._countdown_remaining))
        self._countdown_remaining -= 1
        self.root.after(1000, self._tick)

    def _stop_countdown(self):
        self._countdown_active = False
        self.lbl_countdown.configure(text='')

    def _on_auto_close_toggle(self):
        self.cfg.set('auto_close', self.auto_close_v.get())
        if self.auto_close_v.get():
            self._start_countdown()
        else:
            self._stop_countdown()

    def _on_auto_close_sec_change(self):
        self.cfg.set('auto_close_seconds', self.auto_close_sec.get())
        if self.auto_close_v.get():
            self._stop_countdown()
            self._start_countdown()

    # ── donation & about ──────────────────────────────────────────────────────
    def _open_beer(self):
        webbrowser.open(PAYPAL_URL)
        self.logger.info('Beer donation link opened')

    def _show_about(self):
        th = DARK if self.dark_mode.get() else LIGHT

        win = tk.Toplevel(self.root)
        win.title(self.T('about_title'))
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        win.configure(bg=th['bg'])
        win.geometry('420x340')
        win.update_idletasks()
        ox = self.root.winfo_x() + (self.root.winfo_width()  - 420) // 2
        oy = self.root.winfo_y() + (self.root.winfo_height() - 340) // 2
        win.geometry(f'+{ox}+{oy}')

        tk.Label(win, text='💀',  font=('Segoe UI', 50),
                 bg=th['bg'], fg=th['accent']).pack(pady=(18, 0))
        tk.Label(win, text=APP_NAME, font=('Segoe UI', 22, 'bold'),
                 bg=th['bg'], fg=th['text']).pack()
        tk.Label(win, text=f'v{APP_VERSION}', font=('Segoe UI', 11),
                 bg=th['bg'], fg=th['text2']).pack()
        tk.Label(win, text=f'Created by {AUTHOR}', font=('Segoe UI', 11),
                 bg=th['bg'], fg=th['text']).pack(pady=(16, 0))
        tk.Label(win, text=f'© {YEAR} All Rights Reserved', font=('Segoe UI', 10),
                 bg=th['bg'], fg=th['text2']).pack()
        tk.Label(win, text='Apache License 2.0', font=('Segoe UI', 9),
                 bg=th['bg'], fg=th['text2']).pack(pady=(4, 14))

        tk.Button(win, text=self.T('btn_beer'),
                  command=lambda: (self._open_beer(), win.destroy()),
                  bg='#f6c90e', fg='#1a1a1a', relief='flat',
                  cursor='hand2', font=('Segoe UI', 10),
                  padx=18, pady=5).pack(pady=4)
        tk.Button(win, text='OK', command=win.destroy,
                  bg=th['bg2'], fg=th['text'], relief='flat',
                  cursor='hand2', font=('Segoe UI', 10),
                  padx=28, pady=5).pack(pady=4)

    # ── window close ──────────────────────────────────────────────────────────
    def _on_close(self):
        self.logger.info(f'{APP_NAME} exiting')
        self._save_geometry()
        self.root.destroy()


# ═════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    MindKillerApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
