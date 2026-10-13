from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse, urlunparse

from app.core.browser import (
    AuthenticationError,
    BrowserSession,
    _probe,
    prepare_browser_session,
)

_AUTH_MARKERS = (
    "login required", "login to", "log in", "sign in", "authentication",
    "requires authentication", "login_required", "private",
    "age-restricted", "confirm your age", "cookies are needed",
    "fresh cookies", "http error 401", "http error 403",
)

def normalize_social_url(url: str) -> str:
    """Strip tracking parameters without attempting network redirects.

    Short TikTok links remain short until their destination is resolved by yt-dlp.
    """
    parsed = urlparse(url.strip())
    path = parsed.path.rstrip("/") + "/"
    return urlunparse(("https", (parsed.hostname or "").lower(), path, "", "", ""))


def prepare_social_access(
    root: Path, url: str, provider: str, config: dict, logger,
    extractor_args: tuple[str, ...] = (),
) -> BrowserSession:
    """Try public extraction first; use an authorized browser only for access errors."""
    ok, detail = _probe(url, list(extractor_args), __import__("subprocess").run)
    if ok:
        logger.info("%s: acceso público disponible", provider)
        return BrowserSession("anonymous", "public")

    logger.warning("%s: comprobación pública fallida: %s", provider, detail[-1200:])
    lowered = detail.lower()
    if "http error 429" in lowered or "too many requests" in lowered or "rate limit" in lowered:
        raise RuntimeError(
            f"{provider}: la plataforma está limitando las solicitudes (429). "
            "Prueba más tarde; las cookies no solucionan necesariamente este problema."
        )
    if not any(marker in lowered for marker in _AUTH_MARKERS):
        raise RuntimeError(
            f"{provider}: no se pudo acceder al contenido. Comprueba que el enlace "
            "funcione en el navegador y que yt-dlp esté actualizado. "
            f"Detalle: {detail[-1200:] or 'extractor sin diagnóstico'}"
        )

    try:
        return prepare_browser_session(
            root, url, provider, config, logger, extractor_args=extractor_args
        )
    except AuthenticationError as exc:
        raise AuthenticationError(
            f"{provider}: se necesita una sesión con acceso autorizado. {exc}"
        ) from exc
