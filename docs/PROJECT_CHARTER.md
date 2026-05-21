# MindKiller — Project Charter (Constitución del Proyecto)

> Versión 1.0 | Fecha: 2026-05-21 | Autor: Synyster Rick

---

## 1. Propósito del Proyecto

MindKiller nace para resolver un problema real de productividad en Windows:
terminar procesos bloqueados o no deseados de forma rápida, segura y visual,
sin abrir el Administrador de Tareas ni una terminal.

---

## 2. Visión

> "Una herramienta de escritorio que cualquier usuario de Windows pueda usar
> para tomar control de sus procesos en segundos, sin riesgo de dañar el sistema."

---

## 3. Misión

Proveer una aplicación de escritorio moderna, segura y multilingüe que permita:
- Buscar procesos por nombre
- Inspeccionar PID y ruta del ejecutable
- Terminar procesos de forma segura (graceful → force)
- Proteger automáticamente procesos críticos del sistema

---

## 4. Alcance

### Dentro del alcance
- Aplicación de escritorio Windows 10/11
- Interfaz gráfica con tkinter (dark mode, multi-idioma)
- Gestión de procesos con psutil
- Empaquetado como `.exe` sin dependencias externas
- Repositorio GitHub con CI/CD (GitHub Actions)

### Fuera del alcance
- Aplicaciones web o móviles
- Gestión de servicios de Windows (SCM)
- Monitoreo en tiempo real con grafos/métricas
- Soporte para Linux/macOS (futuro, no v1.x)

---

## 5. Stakeholders

| Rol              | Persona          | Responsabilidad                        |
|------------------|------------------|----------------------------------------|
| Project Owner    | Synyster Rick    | Decisiones de producto y diseño        |
| Developer        | Synyster Rick    | Desarrollo, testing, releases          |
| AI Assistant     | Claude Code      | Implementación y mantenimiento del código |

---

## 6. Restricciones

| Restricción              | Detalle                                           |
|--------------------------|---------------------------------------------------|
| Un solo archivo fuente   | Todo en `process_killer_gui.py`                   |
| Sin dependencias GUI ext | Solo tkinter + ttk (stdlib)                       |
| Sin base de datos        | Persistencia solo via `config.json` y `log.txt`  |
| Sin instalador           | El `.exe` debe ser portable (standalone)          |
| Sin consola              | La app GUI nunca muestra una ventana cmd          |

---

## 7. Criterios de Éxito

- [ ] La app lanza sin errores en Python 3.10+ y como `.exe`
- [ ] Los procesos protegidos no pueden ser terminados bajo ninguna circunstancia
- [ ] La GUI no se congela durante búsquedas o kill operations
- [ ] La configuración persiste entre sesiones
- [ ] El build produce un `.exe` standalone < 20 MB

---

## 8. Riesgos

| Riesgo                              | Probabilidad | Impacto | Mitigación                            |
|-------------------------------------|--------------|---------|---------------------------------------|
| AccessDenied al matar procesos      | Alta         | Medio   | Detectar y ofrecer elevación UAC      |
| Usuario mata proceso del sistema    | Media        | Alto    | Lista `PROTECTED_PROCESSES` inmutable |
| GUI se congela en búsquedas largas  | Media        | Medio   | Hilos daemon + `root.after()`         |
| PyInstaller rompe en nueva versión  | Baja         | Alto    | Fijar versión mínima en requirements  |

---

## 9. Principios de Diseño

1. **Seguridad primero** — nunca matar procesos críticos, nunca hardcodear credenciales
2. **No regresión** — cada versión incluye todo lo anterior
3. **GUI no bloqueante** — todo IO/sistema en hilos separados
4. **Configuración persistente** — el usuario no repite preferencias
5. **Sin ventanas emergentes innecesarias** — status bar y log panel son suficientes

---

## 10. Licencia y Derechos

Apache License 2.0 — ver [LICENSE](../LICENSE)
© 2026 Synyster Rick. Todos los derechos reservados.
