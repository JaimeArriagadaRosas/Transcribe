import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.providers.instagram import InstagramProvider
from app.providers.social import normalize_social_url, prepare_social_access
from app.providers.tiktok import TikTokProvider


class SocialProviderTests(unittest.TestCase):
    def test_tiktok_urls(self):
        provider = TikTokProvider()
        for url in (
            "https://www.tiktok.com/@account/video/1234567890123456789",
            "https://www.tiktok.com/@torres.torresociel/video/7641375408507735316",
            "https://vm.tiktok.com/ZXexample/",
            "https://vt.tiktok.com/ZXexample/",
            "https://www.tiktok.com/t/ZXexample/",
        ):
            provider.validate_url(url)

    def test_rejects_tiktok_homepage_and_untrusted_host(self):
        provider = TikTokProvider()
        for url in ("https://www.tiktok.com/", "https://tiktok.com.evil.test/@a/video/123"):
            with self.assertRaises(ValueError):
                provider.validate_url(url)

    def test_instagram_urls(self):
        provider = InstagramProvider()
        for url in (
            "https://www.instagram.com/reel/C0example/",
            "https://www.instagram.com/p/C0example/?igsh=abc",
            "https://www.instagram.com/p/DeYZ4M-xrZR/",
            "https://www.instagram.com/tv/C0example/",
            "https://www.instagram.com/stories/account/1234567/",
        ):
            provider.validate_url(url)

    def test_instagram_rejects_profile_and_other_host(self):
        provider = InstagramProvider()
        for url in ("https://www.instagram.com/account/", "https://www.instagram.com.evil.test/p/a"):
            with self.assertRaises(ValueError):
                provider.validate_url(url)

    def test_tracking_parameters_are_removed(self):
        url = "https://www.instagram.com/reel/example/?igsh=abc"
        self.assertEqual(normalize_social_url(url), "https://www.instagram.com/reel/example/")

    @patch("app.providers.social._probe", return_value=(True, "OK"))
    @patch("app.providers.social.prepare_browser_session")
    def test_public_social_does_not_access_browser(self, browser, probe):
        with tempfile.TemporaryDirectory() as tmp:
            session = prepare_social_access(Path(tmp), "https://vm.tiktok.com/a/", "tiktok", {}, unittest.mock.Mock())
        self.assertEqual(session.source, "public")
        browser.assert_not_called()

    @patch("app.providers.social._probe", return_value=(False, "ERROR: HTTP Error 429"))
    @patch("app.providers.social.prepare_browser_session")
    def test_rate_limit_does_not_access_browser(self, browser, probe):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaisesRegex(RuntimeError, "429"):
            prepare_social_access(Path(tmp), "https://vm.tiktok.com/a/", "tiktok", {}, unittest.mock.Mock())
        browser.assert_not_called()


if __name__ == "__main__":
    unittest.main()
