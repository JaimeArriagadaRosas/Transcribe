import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.core.diagnostics import check_environment
from app.core.youtube_access import prepare_youtube_access
from app.core.browser import BrowserSession
import logging


class EnvironmentTests(unittest.TestCase):
    def test_reports_missing_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("app.core.diagnostics.importlib.util.find_spec", return_value=None), \
                 patch("app.core.diagnostics.shutil.which", return_value=None):
                messages = check_environment(Path(tmp))
        self.assertTrue(any("yt_dlp" in m for m in messages))
        self.assertTrue(any("ffmpeg" in m for m in messages))

    @patch("app.core.youtube_access.prepare_browser_session")
    @patch("app.core.youtube_access._probe", return_value=(True, "video"))
    def test_public_youtube_skips_browser(self, probe, browser):
        result = prepare_youtube_access(Path("."), "https://youtu.be/abc", {}, logging.getLogger("test"))
        self.assertEqual(result.source, "public")
        browser.assert_not_called()

    @patch("app.core.youtube_access.prepare_browser_session")
    @patch("app.core.youtube_access._probe", return_value=(False, "ERROR: No module named yt_dlp"))
    def test_technical_failure_does_not_use_cookies(self, probe, browser):
        with self.assertRaisesRegex(RuntimeError, "extractor o del entorno"):
            prepare_youtube_access(Path("."), "https://youtu.be/abc", {}, logging.getLogger("test"))
        browser.assert_not_called()

    @patch("app.core.youtube_access.prepare_browser_session", return_value=BrowserSession("anonymous", "test"))
    @patch("app.core.youtube_access._probe", return_value=(False, "ERROR: Sign in required"))
    def test_auth_failure_uses_youtube_cookies_only(self, probe, browser):
        prepare_youtube_access(Path("."), "https://youtu.be/abc", {}, logging.getLogger("test"))
        self.assertEqual(browser.call_args.args[2], "youtube")


if __name__ == "__main__":
    unittest.main()
