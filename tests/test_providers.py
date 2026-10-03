import unittest
from unittest.mock import patch

from app.providers.ytdlp import _js_runtime_args
from app.providers.youtube import YouTubeProvider
from app.providers.zoom import ZoomProvider


class ProviderValidationTests(unittest.TestCase):
    def test_zoom_accepts_institutional_recordings(self):
        ZoomProvider().validate_url("https://institucion.zoom.us/rec/play/example")

    def test_zoom_rejects_non_recording_urls(self):
        with self.assertRaises(ValueError):
            ZoomProvider().validate_url("https://institucion.zoom.us/j/123")

    def test_youtube_accepts_common_hosts(self):
        provider = YouTubeProvider()
        provider.validate_url("https://www.youtube.com/watch?v=abc")
        provider.validate_url("https://youtu.be/abc")

    def test_youtube_rejects_other_hosts(self):
        with self.assertRaises(ValueError):
            YouTubeProvider().validate_url("https://example.com/watch?v=abc")


class YtDlpRuntimeTests(unittest.TestCase):
    @patch("app.providers.ytdlp.shutil.which")
    def test_prefers_deno_when_available(self, which):
        which.side_effect = lambda name: "C:/deno.exe" if name == "deno" else "C:/node.exe"
        self.assertEqual(_js_runtime_args(), ["--js-runtimes", "deno"])

    @patch("app.providers.ytdlp.shutil.which")
    def test_uses_node_when_deno_is_missing(self, which):
        which.side_effect = lambda name: "C:/node.exe" if name == "node" else None
        self.assertEqual(_js_runtime_args(), ["--js-runtimes", "node"])

    @patch("app.providers.ytdlp.shutil.which", return_value=None)
    def test_reports_clear_error_when_no_runtime_exists(self, _which):
        with self.assertRaisesRegex(RuntimeError, "runtime JavaScript compatible"):
            _js_runtime_args()


if __name__ == "__main__":
    unittest.main()
