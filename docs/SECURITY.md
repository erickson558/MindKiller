# MindKiller — Security Policy

> Versión 1.0 | Fecha: 2026-05-21

---

## 1. Modelo de Amenazas

MindKiller es una aplicación de escritorio local. Las amenazas principales son:

| Amenaza | Vector | Mitigación |
|---------|--------|------------|
| Terminación accidental de proceso crítico | Usuario ingresa "svchost" o "explorer" | Lista PROTECTED_PROCESSES inmutable |
| Escalada de privilegios no autorizada | Click en "Run as Admin" | UAC nativo de Windows (ShellExecuteW + runas) |
| Datos sensibles en logs | Errores que incluyan env vars / rutas | Solo se loguean nombre, PID y tipo de error |
| Inyección de comandos | Campo de búsqueda | El término se usa como substring, jamás como comando |
| EXE malicioso | Distribución del binario comprometido | Releases solo desde GitHub Actions en repositorio oficial |

---

## 2. Procesos Protegidos

Los siguientes procesos **nunca pueden ser terminados** por MindKiller,
independientemente del nivel de privilegio del usuario:

```
explorer.exe      — Shell de Windows (escritorio, barra de tareas)
winlogon.exe      — Proceso de inicio de sesión
csrss.exe         — Client/Server Runtime Subsystem
services.exe      — Service Control Manager
lsass.exe         — Local Security Authority (credenciales)
system            — Kernel de Windows
smss.exe          — Session Manager
wininit.exe       — Inicialización de Windows
svchost.exe       — Host de servicios del sistema
dwm.exe           — Desktop Window Manager
fontdrvhost.exe   — Driver de fuentes
memory compression — Compresión de memoria del kernel
registry          — Hive del registro del sistema
ntoskrnl.exe      — Kernel de NT
taskmgr.exe       — Administrador de tareas
```

**Esta lista no puede ser reducida.** Solo puede crecer en versiones futuras.

---

## 3. Manejo de Privilegios

### 3.1 Detección
```python
ctypes.windll.shell32.IsUserAnAdmin()
```
El resultado se muestra en el badge del header (⚡ ADMIN / ⚠ USER).

### 3.2 Elevación
```python
ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, None, 1)
```
- Usa el verbo `runas` — mecanismo oficial de UAC
- La instancia sin privilegios se cierra inmediatamente
- No se bypassea UAC bajo ninguna circunstancia

### 3.3 Manejo de AccessDenied
Cuando `psutil` lanza `AccessDenied`, la app:
1. Registra el error en `log.txt` con nivel ERROR
2. Muestra mensaje en la barra de estado
3. Sugiere elevar privilegios
4. **No reintenta** silenciosamente

---

## 4. Validación de Entrada

| Campo | Validación |
|-------|-----------|
| Término de búsqueda | String simple, usado como `in name.lower()` — no es regex, no es comando |
| Segundos de autocierre | Spinbox con rango 5–3600, tipo int |
| Configuración cargada | Merge con DEFAULTS — claves inesperadas se ignoran |

No hay `eval()`, `exec()`, ni `subprocess` con `shell=True` en ninguna parte del código.

---

## 5. Privacidad de Datos

- `config.json` contiene solo preferencias de UI — sin datos personales
- `log.txt` contiene nombres de procesos y PIDs — no hay contraseñas, tokens ni rutas sensibles en logs
- Ningún dato se envía a servidores externos (excepto el botón Beer → PayPal, que abre el browser del usuario)

---

## 6. Reporte de Vulnerabilidades

Reportar issues de seguridad en:
**https://github.com/erickson558/MindKiller/issues**

Etiquetar el issue como `security` y describir el vector de ataque y reproducción.
