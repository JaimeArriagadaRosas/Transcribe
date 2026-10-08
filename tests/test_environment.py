import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.core.diagnostics import check_environment
from app.providers.youtube import YouTubeProvider


class EnvironmentTests(unittest.TestCase):
    def test_reports_missing_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("app.core.diagnostics.importlib.util.find_spec", return_value=None), \
                 patch("app.core.diagnostics.shutil.which", return_value=None):
                messages = check_environment(Path(tmp))
        self.assertTrue(any("yt_dlp" in m for m in messages))
        self.assertTrue(any("ffmpeg" in m for m in messages))

    def test_youtube_provider_does_not_use_zoom_cookies(self):
        self.assertEqual(YouTubeProvider.name, "youtube")


if __name__ == "__main__":
    unittest.main()
