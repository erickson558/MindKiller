# /release — Bump version and publish a new release

Bump the version in `process_killer_gui.py`, update `README.md` changelog,
commit, tag, and push to trigger the GitHub Actions auto-release.

## Steps

1. Read `process_killer_gui.py` and find the current `APP_VERSION` string.
2. Ask the user which part to bump (patch / minor / major) if not provided as argument.
3. Compute the new version following semver.
4. Edit `APP_VERSION` in `process_killer_gui.py`.
5. Add a changelog entry in `README.md` under `## Changelog` with today's date and a bullet list of changes (ask the user for the change summary if not provided).
6. Stage both files: `git add process_killer_gui.py README.md`
7. Commit: `git commit -m "feat: v<NEW_VERSION> — <summary>"`
8. Tag: `git tag v<NEW_VERSION>`
9. Push branch and tag: `git push && git push origin v<NEW_VERSION>`
10. Confirm the tag was pushed and remind the user that GitHub Actions will build the EXE and create the release automatically.

## Rules (from CLAUDE.md)
- Never remove existing features or protected-process list entries.
- Verify `APP_VERSION` constant is the single source of truth — do not duplicate it.
- Commit message format: `feat: vX.Y.Z — <what changed>`
