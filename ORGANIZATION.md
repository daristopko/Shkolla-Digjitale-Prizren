# Folder Organization

This workspace is organized as course material plus standalone projects.

- `Kursi Python/` contains Python lesson folders, homework, and Python projects.
- `Kursi HTML, CSS & JS/` contains web lesson folders, homework, and web projects.
- `Expense-Tracker/` is a standalone web project.
- `_archive/` contains old generated or duplicate material that was moved out of the active workspace instead of deleted.

Cleanup decisions made:

- Kept `.venv/` as the likely active Python environment.
- Moved old `.venv-1/` into `_archive/old-virtualenvs/`.
- Moved loose Python root runtime files into `_archive/loose-runtime-files/`.
- Moved lesson zip packages into `_archive/packaged-zips/`.
- Moved the older duplicate Dita11 AI-agent project into `_archive/duplicate-projects/`.
- Removed active `__pycache__/` folders because they are generated.

Do not put new random files at the workspace root. Put lesson files inside the matching `Dita` folder, homework inside `Detyra`, and complete projects inside `Projekte` or their own standalone project folder.
