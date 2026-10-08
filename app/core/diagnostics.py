from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path


def check_environment(root: Path) -> list[str]:
    """Report missing tools without importing the Whisper model."""
    warnings: list[str] = []
    expected = root / ".venv" / "Scripts" / "python.exe"
    if expected.is_file() and Path(sys.prefix).resolve() != (root / ".venv").resolve():
        warnings.append("Se está usando Python fuera de .venv; ejecuta transcribe.cmd.")
    for module in ("yt_dlp", "faster_whisper"):
        if importlib.util.find_spec(module) is None:
            warnings.append(
                f"Falta {module} en este Python ({sys.executable}). "
                "Instala las dependencias con .venv\\Scripts\\python.exe -m pip install -r requirements.txt"
            )
    for binary in ("ffmpeg", "ffprobe"):
        if shutil.which(binary) is None:
            warnings.append(f"No se encontró {binary} en PATH.")
    if not (shutil.which("deno") or shutil.which("node")):
        warnings.append("YouTube: no se encontró Deno ni Node.js en PATH.")
    return warnings
