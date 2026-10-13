from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

from app.providers.base import DownloadedMedia, DownloadedMediaBatch
from app.providers.social import prepare_social_access

_MEDIA_EXTENSIONS = {".mp4", ".mkv", ".webm", ".mov", ".m4v"}


class InstagramProvider:
    name = "instagram"

    def validate_url(self, url: str) -> None:
        parsed = urlparse(url.strip())
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in {"http", "https"} or host not in {
            "instagram.com", "www.instagram.com", "m.instagram.com"
        }:
            raise ValueError("La URL no pertenece a Instagram")
        parts = [part for part in parsed.path.split("/") if part]
        post = len(parts) == 2 and parts[0] in {"reel", "p", "tv"} and bool(parts[1])
        story = len(parts) == 3 and parts[0] == "stories" and bool(parts[1]) and bool(parts[2])
        if not (post or story):
            raise ValueError("Utiliza una URL de Reel, publicación /p/ o historia /stories/ de Instagram.")

    def download(self, root: Path, job_dir: Path, url: str, config: dict, logger) -> DownloadedMediaBatch:
        self.validate_url(url)
        print("[1/5] Comprobando acceso a Instagram...")
        session = prepare_social_access(root, url, self.name, config, logger)
        print(f"      Acceso: {session.source}")
        print("[2/5] Descargando contenido de Instagram...")
        job_dir.mkdir(parents=True, exist_ok=True)
        # A post may contain several videos. Stable names allow interrupted downloads to resume.
        template = job_dir / "source_%(playlist_index|1)03d_%(id)s.%(ext)s"
        selector = f"bestvideo[height<={int(config.get('max_video_height', 720))}]+bestaudio/best[height<={int(config.get('max_video_height', 720))}]/best"
        command = [
            sys.executable, "-m", "yt_dlp", "--ignore-config",
            "--continue", "--no-overwrites", "--yes-playlist", "--ignore-errors",
            "--windows-filenames", "--no-progress",
            "--write-info-json", "--merge-output-format", "mp4",
            "-f", selector, "-o", str(template),
            "--print", "after_move:filepath",
            *session.yt_dlp_args, url,
        ]
        logger.info("Instagram: descargando publicación (puede incluir varios videos)")
        completed = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "yt-dlp falló").replace(url, "<URL>")
            raise RuntimeError(f"Instagram: falló la descarga: {detail[-2500:]}")

        files = []
        for line in (completed.stdout or "").splitlines():
            candidate = Path(line.strip().strip('"'))
            if candidate.is_file() and candidate.suffix.lower() in _MEDIA_EXTENSIONS and candidate.parent.resolve() == job_dir.resolve():
                files.append(candidate)
        # Some extractors do not print after_move for previously downloaded items.
        files.extend(p for p in job_dir.glob("source_*") if p.is_file() and p.suffix.lower() in _MEDIA_EXTENSIONS)
        unique = sorted(set(files), key=lambda path: path.name)
        if not unique:
            raise RuntimeError(
                "Instagram no entregó ningún video descargable. "
                "Si la publicación solo contiene fotos, no hay video para transcribir."
            )

        items = []
        for path in unique:
            info_path = path.with_suffix(".info.json")
            info = {}
            if info_path.is_file():
                try:
                    info = json.loads(info_path.read_text(encoding="utf-8-sig"))
                except (OSError, json.JSONDecodeError):
                    pass
            items.append(DownloadedMedia(
                title=str(info.get("title") or path.stem),
                video_path=path,
                duration=float(info["duration"]) if info.get("duration") else None,
                source_id=str(info.get("id") or "") or None,
            ))
        return DownloadedMediaBatch(title=items[0].title, items=items)
