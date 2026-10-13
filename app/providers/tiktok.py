from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from app.providers.base import DownloadedMedia
from app.providers.social import prepare_social_access
from app.providers.ytdlp import download_video


class TikTokProvider:
    name = "tiktok"

    def validate_url(self, url: str) -> None:
        parsed = urlparse(url.strip())
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in {"http", "https"} or host not in {
            "tiktok.com", "www.tiktok.com", "m.tiktok.com",
            "vm.tiktok.com", "vt.tiktok.com",
        }:
            raise ValueError("La URL no pertenece a TikTok")
        path = parsed.path
        short = host in {"vm.tiktok.com", "vt.tiktok.com"} and path.strip("/")
        other_short = host == "www.tiktok.com" and path.startswith("/t/") and path.strip("/") != "t"
        direct = ("/video/" in path and path.startswith("/@") and path.split("/video/", 1)[1].strip("/").isdigit())
        if not (short or other_short or direct):
            raise ValueError("Utiliza la URL de un video de TikTok o un enlace corto vm/vt/t.")

    def download(self, root: Path, job_dir: Path, url: str, config: dict, logger) -> DownloadedMedia:
        self.validate_url(url)
        print("[1/5] Comprobando acceso a TikTok...")
        session = prepare_social_access(root, url, self.name, config, logger, extractor_args=("--impersonate", "chrome"))
        print(f"      Acceso: {session.source}")
        print("[2/5] Descargando video de TikTok...")
        return download_video(
            job_dir, url, [*session.yt_dlp_args, "--impersonate", "chrome"],
            int(config.get("max_video_height", 720)), logger,
        )
