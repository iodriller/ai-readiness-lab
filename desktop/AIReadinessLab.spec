# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — builds the native AI Readiness Lab app.

Run from the repo root (after building the frontend):
    pyinstaller desktop/AIReadinessLab.spec --noconfirm

Produces a self-contained app under dist/ that bundles the Python runtime, the
FastAPI backend, and the built single-page UI. No Python install on the target.
"""

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = Path(SPECPATH).resolve().parent
sys.path.insert(0, str(ROOT / "backend"))

hiddenimports = []
for pkg in ("uvicorn", "anthropic", "keyring", "keyring.backends", "app"):
    hiddenimports += collect_submodules(pkg)

# Bundle the built UI plus the backend package's data files (e.g. the
# opportunity library.json), preserving their package-relative paths.
datas = [(str(ROOT / "frontend" / "dist"), "frontend_dist")]
datas += collect_data_files("app")

a = Analysis(
    [str(ROOT / "desktop" / "launcher.py")],
    pathex=[str(ROOT / "backend")],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AI Readiness Lab",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # no terminal window — this is a consumer desktop app
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="AI Readiness Lab",
)

# macOS: wrap the collected app into a proper .app bundle.
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="AI Readiness Lab.app",
        bundle_identifier="ai.readiness.lab",
        info_plist={"NSHighResolutionCapable": True},
    )
