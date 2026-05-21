# Guía de Contribución — MindKiller

---

## Regla #1 — No romper lo que ya funciona

Antes de cualquier cambio, corre `/check` para verificar el estado actual.
Cada versión debe incluir **todo** lo de la versión anterior más las mejoras nuevas.

---

## Flujo de trabajo

```
1. Lee CLAUDE.md completamente
2. Lee la sección relevante de process_killer_gui.py
3. Implementa el cambio en la clase correcta:
     ConfigManager  → solo config.json
     ProcessManager → solo psutil / OS
     MindKillerApp  → solo GUI
4. Agrega la traducción (EN + ES) si hay texto nuevo
5. Agrega la clave a config.json si hay nueva preferencia
6. Corre: python -c "import process_killer_gui"
7. Lanza la app y prueba manualmente el cambio
8. Corre /check
9. Corre /release patch|minor|major
```

---

## Convenciones de código

- Sin comentarios obvios — solo cuando el "por qué" no es evidente
- Sin `messagebox` para flujo normal — usar `_status()` y `_log_add()`
- Sin operaciones OS en el main thread — usar `threading.Thread(daemon=True)`
- Claves de traducción en `snake_case`
- Colores siempre desde los dicts `DARK` / `LIGHT`, nunca hardcodeados

---

## Commit messages

```
feat: vX.Y.Z — descripción breve de la feature
fix:  vX.Y.Z — descripción del bug corregido
docs: actualizar SDD con ADR-007
```

---

## Versionado

| Cambio            | Bump   | Ejemplo        |
|-------------------|--------|----------------|
| Bug fix           | patch  | 0.0.1 → 0.0.2  |
| Nueva feature     | minor  | 0.0.2 → 0.1.0  |
| Cambio rompedor   | major  | 0.1.0 → 1.0.0  |

Usar el skill `/release` para automatizar el proceso completo.
