from __future__ import annotations

import logging
from pathlib import Path

from app.core.browser import (
    AuthenticationError,
    BrowserSession,
    _probe,
    prepare_browser_session,
)


_AUTH_MARKERS = (
    "sign in",
    "login required",
    "authentication",
    "age-restricted",
    "confirm your age",
    "private video",
    "members-only",
    "http error 401",
    "http error 403",
)


def prepare_youtube_access(root: Path, url: str, config: dict, logger: logging.Logger) -> BrowserSession:
    """Attempt public YouTube access first, using browser cookies only for auth failures."""
    ok, detail = _probe(url, [], __import__("subprocess").run)
    if ok:
        logger.info("YouTube: public access succeeded")
        return BrowserSession("anonymous", "public")

    logger.warning("YouTube: public probe failed: %s", detail[-2500:])
    lowered = detail.lower()
    if not any(marker in lowered for marker in _AUTH_MARKERS):
        raise RuntimeError(
            "Falló la comprobación pública de YouTube por un problema del extractor o del entorno. "
            "No se intentaron cookies porque no hay evidencia de que sean necesarias. "
            f"Detalle: {detail[-1400:] or 'yt-dlp terminó sin diagnóstico'}"
        )

    logger.info("YouTube: authentication appears required; trying authorized browser session")
    try:
        return prepare_browser_session(root, url, "youtube", config, logger)
    except AuthenticationError as exc:
        raise AuthenticationError(
            "YouTube requiere acceso autorizado, pero no se encontró una sesión válida. "
            f"{exc}"
        ) from exc
