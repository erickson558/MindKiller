# MindKiller — Software Design Document (SDD)

> Versión 1.0 | Fecha: 2026-05-21
> Basado en IEEE 1016-2009 Software Design Description

---

## 1. Introducción

### 1.1 Propósito
Este documento describe el diseño completo del software MindKiller v0.0.1:
arquitectura, componentes, interfaces, flujos de datos, seguridad y decisiones
de diseño tomadas durante el desarrollo.

### 1.2 Alcance
Aplica a `process_killer_gui.py` y todos los archivos de soporte del proyecto.

### 1.3 Audiencia
- Desarrolladores que mantengan o extiendan el proyecto
- Agentes de IA (Claude Code) que trabajen sobre el codebase
- Revisores de código / auditores de seguridad

### 1.4 Definiciones

| Término          | Definición                                              |
|------------------|---------------------------------------------------------|
| GUI              | Graphical User Interface — interfaz tkinter             |
| PID              | Process Identifier — ID único de un proceso OS          |
| psutil           | Librería Python para información de procesos del sistema|
| UAC              | User Account Control — mecanismo de elevación Windows   |
| SDD              | Software Design Document                                |
| PROTECTED         | Proceso del sistema que nunca debe ser terminado        |

---

## 2. Arquitectura General

### 2.1 Estilo Arquitectónico
**Layered Architecture** de 2 capas dentro de un único archivo fuente:

```
┌─────────────────────────────────────────────┐
│               PRESENTATION LAYER             │
│            MindKillerApp (tkinter)           │
│  UI, eventos, theming, i18n, auto-save       │
└──────────────┬──────────────────────────────┘
               │ delega
┌──────────────▼──────────────────────────────┐
│               DOMAIN LAYER                   │
│  ProcessManager          ConfigManager       │
│  (psutil, kill logic)    (config.json r/w)   │
└─────────────────────────────────────────────┘
```

### 2.2 Principio de Threading

```
Main Thread (Tk event loop)
    │
    ├─ Usuario presiona "Buscar" → _search()
    │       └─ threading.Thread(daemon=True) → backend.find()
    │               └─ root.after(0, _fill_tree)   ← vuelve al main thread
    │
    └─ Usuario presiona "Matar" → _kill_selected()
            └─ threading.Thread(daemon=True) → backend.kill()
                    └─ root.after(0, _status / _log_add)
```

**Regla:** Ninguna operación de OS/psutil ocurre en el main thread.

---

## 3. Descripción de Componentes

### 3.1 `ConfigManager`

**Responsabilidad:** Leer y escribir `config.json`. Sin lógica de negocio, sin GUI.

**Atributos:**
| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `path`   | Path | Ruta a config.json en APP_DIR |
| `data`   | Dict | Estado actual de la configuración |
| `DEFAULTS` | Dict | Valores por defecto del sistema |

**Métodos:**
| Método | Firma | Descripción |
|--------|-------|-------------|
| `_load` | `() → Dict` | Carga config.json; merge con DEFAULTS si faltan claves |
| `save`  | `() → None` | Escribe data a disco en JSON indentado |
| `get`   | `(key, default) → Any` | Acceso seguro a un valor |
| `set`   | `(key, value) → None` | Asigna y guarda inmediatamente |

**Invariantes:**
- Siempre contiene todas las claves de `DEFAULTS` (merge on load)
- `save()` es idempotente
- No lanza excepciones al usuario — registra en log y continúa

---

### 3.2 `ProcessManager`

**Responsabilidad:** Descubrir y terminar procesos del OS. Sin GUI.

**Métodos:**
| Método | Firma | Descripción |
|--------|-------|-------------|
| `is_protected` | `(name: str) → bool` | True si el nombre está en PROTECTED_PROCESSES |
| `find` | `(term: str) → List[Dict]` | Devuelve procesos cuyo nombre contiene `term` |
| `kill` | `(pid, name) → Tuple[bool, str]` | Termina proceso; devuelve (éxito, razón) |

**Algoritmo de kill:**
```
1. is_protected(name) → True  ⇒ return (False, 'protected')
2. proc.terminate()
3. proc.wait(timeout=3s)
   OK  → return (True, 'success')
   TimeoutExpired → proc.kill() → return (True, 'success')
4. AccessDenied  → return (False, 'access_denied')
5. NoSuchProcess → return (True, 'already_gone')
6. ZombieProcess → return (False, 'zombie')
7. Exception     → return (False, str(e))
```

**Procesos protegidos (inmutables):**
```
explorer.exe  winlogon.exe  csrss.exe   services.exe
lsass.exe     system        smss.exe    wininit.exe
svchost.exe   dwm.exe       fontdrvhost.exe
memory compression  registry  ntoskrnl.exe  taskmgr.exe
```

---

### 3.3 `MindKillerApp`

**Responsabilidad:** Todo lo visual. Construye la UI, aplica temas, gestiona
eventos, delega lógica a `ProcessManager` y `ConfigManager`.

**Sub-componentes UI:**

| Método builder | Widget principal | Descripción |
|----------------|-----------------|-------------|
| `_build_menu`  | `tk.Menu`       | Barra de menús (File/Tools/View/Help) |
| `_build_header`| `tk.Frame`      | Título, versión, badge admin, botones beer/admin |
| `_build_search_bar` | `tk.Entry` | Campo de búsqueda + botones Buscar/Limpiar |
| `_build_options_bar`| `tk.Checkbutton` | Auto-start, auto-close, spinbox segundos |
| `_build_process_list` | `ttk.Treeview` | Lista de procesos con scrollbars |
| `_build_action_buttons` | `tk.Button` | Kill selected, Kill all, Refresh, Exit |
| `_build_log_panel` | `tk.Text`   | Log visual dentro de la app |
| `_build_status_bar`| `tk.Label`  | Barra de estado + countdown |

---

## 4. Diseño de Datos

### 4.1 config.json

```json
{
  "language":           "es",       // "en" | "es" | futuros ISO 639-1
  "dark_mode":          true,       // bool
  "auto_start":         false,      // bool — buscar al abrir
  "auto_close":         false,      // bool — cerrar automáticamente
  "auto_close_seconds": 60,         // int 5–3600
  "last_search":        "chrome",   // string — último término buscado
  "window_geometry":    "960x680+120+80",  // formato WxH+X+Y de tkinter
  "window_maximized":   false,      // bool
  "version":            "0.0.1"     // versión cuando se guardó
}
```

### 4.2 log.txt

```
2026-05-21 15:30:00 | INFO     | MindKiller v0.0.1 starting | admin=True
2026-05-21 15:30:05 | INFO     | Search 'chrome': 3 result(s)
2026-05-21 15:30:10 | INFO     | Terminated 'chrome.exe' PID:1234 gracefully
2026-05-21 15:30:10 | ERROR    | Access denied 'chrome.exe' PID:5678
```

### 4.3 Estructura de un proceso en memoria

```python
{
    'name':      str,   # Nombre del ejecutable, e.g. "chrome.exe"
    'pid':       int,   # Process ID
    'exe':       str,   # Ruta completa o "N/A"
    'status':    str,   # "running" | "sleeping" | etc.
    'protected': bool,  # True si está en PROTECTED_PROCESSES
}
```

---

## 5. Diseño de Interfaz

### 5.1 Layout

```
┌────────────────────────────────────────────────────────────┐
│ 💀 MindKiller    v0.0.1 ⚡ADMIN    [⚡ Admin] [🍺 Beer]  │  ← Header (bg3)
├────────────────────────────────────────────────────────────┤  ← accent separator
│ Proceso: [________________]  [Buscar F5]  [Limpiar Esc]   │  ← Search bar
│ ☐ Buscar al iniciar   ☐ Cerrar en [60] seg               │  ← Options bar
├────────────────────────────────────────────────────────────┤
│ Nombre Proceso  │ PID  │ Ruta del Ejecutable  │ Estado    │  ← Treeview
│ chrome.exe      │ 1234 │ C:\Program Files\... │ running   │
│ chrome.exe      │ 5678 │ C:\Program Files\... │ sleeping  │
├────────────────────────────────────────────────────────────┤
│ [Matar Sel Del] [Matar Todos Ctrl+K] [Refrescar F5] [Salir]│  ← Action buttons
├────────────────────────────────────────────────────────────┤
│  Activity Log                                              │  ← Log panel
│  [15:30:10] Found 2 process(es) for 'chrome'              │
├────────────────────────────────────────────────────────────┤
│ ✓ 2 procesos encontrados para "chrome"    ⏱ Cerrando 58s │  ← Status bar
└────────────────────────────────────────────────────────────┘
```

### 5.2 Paleta de colores — Dark Mode

| Token    | Hex       | Uso                          |
|----------|-----------|------------------------------|
| bg       | `#12121f` | Fondo principal              |
| bg2      | `#1a1a2e` | Fondos secundarios, treeview |
| bg3      | `#0f3460` | Header, headings             |
| accent   | `#e94560` | Botones primarios, separador |
| success  | `#00cec9` | Mensajes de éxito            |
| warning  | `#fdcb6e` | Advertencias, procesos prot. |
| text     | `#eaeaea` | Texto principal              |
| text2    | `#8a8ab0` | Texto secundario, status bar |

### 5.3 Atajos de teclado

| Tecla        | Acción               |
|--------------|----------------------|
| `F5`         | Buscar / Refrescar   |
| `Delete`     | Matar seleccionados  |
| `Ctrl+K`     | Matar todos          |
| `Escape`     | Limpiar búsqueda     |
| `Ctrl+A`     | Seleccionar todos    |
| `Ctrl+Q`     | Salir                |

---

## 6. Diseño de Seguridad

### 6.1 Protección de procesos críticos
- `PROTECTED_PROCESSES` es un `frozenset` inmutable en tiempo de ejecución
- `is_protected()` se llama **antes** de cualquier operación de kill
- La UI muestra `🔒` en la columna Status para procesos protegidos

### 6.2 Elevación de privilegios
- Implementada con `ShellExecuteW(verb="runas")` — mecanismo oficial UAC
- Nunca se usa `subprocess` con `shell=True` para elevación
- El proceso original se cierra (`root.quit()`) tras lanzar el elevado

### 6.3 Manejo de errores
- `AccessDenied`, `NoSuchProcess`, `ZombieProcess` capturados explícitamente
- Ningún error expone stack traces al usuario — solo mensajes legibles
- Los errores se registran en `log.txt` con nivel ERROR

### 6.4 Entrada de usuario
- El campo de búsqueda es solo texto — se usa como substring, no como comando
- No hay `eval()` ni `exec()` de input del usuario en ninguna parte

---

## 7. Internacionalización (i18n)

### 7.1 Estructura
```python
TRANSLATIONS = {
    'en': { 'key': 'English text', ... },
    'es': { 'key': 'Texto en español', ... },
    # Agregar nuevos idiomas aquí
}
```

### 7.2 Acceso
```python
self.T('key')           # lookup simple
self.T('key', n=5)      # con formato: T devuelve text.format(n=5)
```

### 7.3 Agregar un idioma
Ver skill `/add-language` en `.claude/commands/add-language.md`

---

## 8. Empaquetado y Distribución

### 8.1 Comando de build
```bash
pyinstaller --onefile --windowed --name process_killer_gui \
            --icon=<archivo.ico> process_killer_gui.py
```

### 8.2 Flags requeridos
| Flag | Motivo |
|------|--------|
| `--onefile` | EXE portable sin carpeta dist |
| `--windowed` | Sin ventana de consola cmd |
| `--icon` | Icono de la aplicación |

### 8.3 Output esperado
- Archivo: `process_killer_gui.exe` en la raíz del proyecto
- Tamaño aproximado: 10–15 MB
- Dependencias: ninguna (todo embebido)

---

## 9. CI/CD — GitHub Actions

### 9.1 Trigger
Push a rama `main` o tag `v*.*.*`

### 9.2 Pipeline

```
push to main
    │
    ├─ Setup Python 3.11
    ├─ pip install -r requirements.txt
    ├─ Extraer APP_VERSION de process_killer_gui.py (regex)
    ├─ pyinstaller --onefile --windowed ...
    └─ softprops/action-gh-release
           ├─ tag_name: v{VERSION}
           ├─ name: MindKiller v{VERSION}
           ├─ prerelease: true si version empieza con "0."
           └─ files: dist/process_killer_gui.exe
```

---

## 10. Versionado

Formato: `MAJOR.MINOR.PATCH` — Semantic Versioning 2.0.0

| Tipo de cambio     | Qué incrementar |
|--------------------|-----------------|
| Bug fix            | PATCH (0.0.x)   |
| Nueva feature      | MINOR (0.x.0)   |
| Cambio incompatible| MAJOR (x.0.0)   |

`0.x.x` = pre-release / alpha (flag `prerelease: true` en GitHub)

**Fuente única de verdad:** `APP_VERSION` en `process_killer_gui.py`

---

## 11. Decisiones de Diseño (ADR)

### ADR-001: Un solo archivo fuente
**Decisión:** Todo el código en `process_killer_gui.py`
**Razón:** El usuario especificó esta restricción explícitamente. Facilita distribución y modificaciones rápidas.
**Consecuencia:** Se usa separación por clases dentro del archivo para mantener legibilidad.

### ADR-002: tkinter sin librerías externas de UI
**Decisión:** Solo `tkinter` + `ttk` de la stdlib
**Razón:** Cero dependencias extra → menor tamaño del EXE, sin incompatibilidades.
**Consecuencia:** El look moderno se logra con temas ttk personalizados y paleta de colores custom.

### ADR-003: Hilos daemon para operaciones OS
**Decisión:** Toda llamada a psutil corre en `threading.Thread(daemon=True)`
**Razón:** La GUI nunca debe bloquearse — requisito explícito.
**Consecuencia:** Los resultados se postean al main thread via `root.after(0, cb)`.

### ADR-004: Lista de procesos protegidos como set inmutable
**Decisión:** `PROTECTED_PROCESSES` es un `set` de literales en el módulo
**Razón:** Seguridad crítica — ningún path de código puede bypasear esta lista.
**Consecuencia:** El usuario no puede "desproteger" procesos desde la UI (intencional).
