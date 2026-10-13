from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class DownloadedMedia:
    title: str
    video_path: Path
    duration: float | None = None
    source_id: str | None = None


@dataclass
class DownloadedMediaBatch:
    title: str
    items: list[DownloadedMedia]


class Provider(Protocol):
    name: str

    def validate_url(self, url: str) -> None: ...

    def download(self, root: Path, job_dir: Path, url: str, config: dict, logger) -> DownloadedMedia | DownloadedMediaBatch: ...
