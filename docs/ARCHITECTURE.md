# MindKiller — Architecture Decision Records (ADR)

> Registro vivo de decisiones arquitectónicas. Agregar una entrada por cada
> decisión significativa que afecte el diseño del sistema.

---

## Formato de cada ADR

```
### ADR-NNN: Título corto
**Estado:** Propuesto | Aceptado | Obsoleto | Reemplazado por ADR-NNN
**Fecha:** YYYY-MM-DD
**Contexto:** Por qué surgió esta decisión
**Decisión:** Qué se decidió
**Consecuencias:** Qué cambia, qué se gana, qué se pierde
```

---

## ADR-001: Arquitectura de un solo archivo

**Estado:** Aceptado | **Fecha:** 2026-05-21

**Contexto:** El usuario requirió explícitamente un solo archivo `.py` para simplificar distribución y mantenimiento.

**Decisión:** Todo el código fuente reside en `process_killer_gui.py`. La separación de responsabilidades se mantiene mediante clases (`ConfigManager`, `ProcessManager`, `MindKillerApp`), no mediante módulos.

**Consecuencias:**
- ✅ Distribución trivial — copiar un archivo es suficiente
- ✅ Sin imports relativos ni problemas de empaquetado
- ⚠️ El archivo crece con el tiempo — mitigado con secciones bien delimitadas por comentarios `# ═══`

---

## ADR-002: tkinter puro (sin CustomTkinter, PyQt, wxPython)

**Estado:** Aceptado | **Fecha:** 2026-05-21

**Contexto:** Necesidad de GUI moderna sin dependencias externas pesadas.

**Decisión:** Usar solo `tkinter` + `ttk` de la stdlib. El look moderno se logra con paleta de colores custom en los dicts `DARK`/`LIGHT` y estilos ttk via `ttk.Style`.

**Consecuencias:**
- ✅ Cero dependencias de GUI — EXE más liviano
- ✅ Sin riesgo de incompatibilidad entre versiones de la librería UI
- ⚠️ Limitaciones de render (sin antialiasing, sin bordes redondeados nativos)

---

## ADR-003: Threading con root.after() para UI thread-safety

**Estado:** Aceptado | **Fecha:** 2026-05-21

**Contexto:** Las operaciones psutil (especialmente en sistemas con muchos procesos) pueden tomar >100ms, bloqueando el event loop de tkinter.

**Decisión:** Todo código que llame a psutil corre en `threading.Thread(daemon=True)`. Los resultados se envían al main thread vía `root.after(0, callback)`.

**Consecuencias:**
- ✅ GUI siempre responsiva
- ✅ Sin race conditions (tkinter no es thread-safe — solo el main thread toca widgets)
- ⚠️ Callbacks asíncronos requieren lambdas con valores capturados correctamente

---

## ADR-004: PROTECTED_PROCESSES como conjunto inmutable de módulo

**Estado:** Aceptado | **Fecha:** 2026-05-21

**Contexto:** Riesgo crítico de que el usuario mate procesos del sistema como `lsass.exe` o `csrss.exe`, lo que causaría BSOD o corrupción.

**Decisión:** `PROTECTED_PROCESSES` es un `set` de constantes a nivel de módulo. `is_protected()` se llama siempre antes de cualquier `kill()`. No hay forma desde la UI de modificar esta lista.

**Consecuencias:**
- ✅ Protección garantizada en tiempo de ejecución
- ✅ La lista es visible y auditable sin ejecutar el programa
- ⚠️ Usuarios avanzados deben editar el código fuente para agregar excepciones (intencional)

---

## ADR-005: config.json con merge de DEFAULTS en carga

**Estado:** Aceptado | **Fecha:** 2026-05-21

**Contexto:** Al actualizar la app a una nueva versión, el `config.json` del usuario puede no tener claves nuevas agregadas en esa versión.

**Decisión:** `ConfigManager._load()` siempre hace `merged = dict(DEFAULTS); merged.update(saved)`. Así, claves nuevas tienen valores por defecto y claves existentes del usuario se respetan.

**Consecuencias:**
- ✅ Compatibilidad hacia adelante — actualizar la app nunca rompe la config
- ✅ Sin migrations manuales de config
- ⚠️ Claves eliminadas de DEFAULTS persisten en el JSON del usuario (inofensivo)

---

## ADR-006: Elevación UAC via ShellExecuteW

**Estado:** Aceptado | **Fecha:** 2026-05-21

**Contexto:** Algunos procesos requieren privilegios de administrador para ser terminados.

**Decisión:** Usar `ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, None, 1)`. El proceso original se destruye inmediatamente tras lanzar el elevado.

**Consecuencias:**
- ✅ Mecanismo oficial de Windows — no bypasea UAC
- ✅ No requiere subprocess ni shell=True
- ⚠️ La nueva instancia abre una ventana nueva (comportamiento esperado de UAC)

---

## Plantilla para nuevas ADRs

```markdown
## ADR-NNN: Título

**Estado:** Propuesto | **Fecha:** YYYY-MM-DD

**Contexto:**
_Por qué surgió esta decisión. Qué problema existe._

**Decisión:**
_Qué se decidió hacer._

**Consecuencias:**
- ✅ Beneficio 1
- ✅ Beneficio 2
- ⚠️ Trade-off o limitación
```
