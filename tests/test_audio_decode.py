import tempfile
import unittest
import wave
from pathlib import Path


class AudioDecodeCompatibilityTests(unittest.TestCase):
    def test_faster_whisper_decodes_real_audio(self):
        # Exercise the real PyAV call; mocked models cannot catch API changes.
        from faster_whisper.audio import decode_audio

        with tempfile.TemporaryDirectory() as directory:
            audio = Path(directory) / "sample.wav"
            with wave.open(str(audio), "wb") as stream:
                stream.setnchannels(1)
                stream.setsampwidth(2)
                stream.setframerate(16000)
                stream.writeframes(b"\x00\x00" * 16000)

            samples = decode_audio(str(audio))

        self.assertEqual(samples.shape, (16000,))
        self.assertEqual(str(samples.dtype), "float32")
        self.assertTrue((samples == 0).all())


if __name__ == "__main__":
    unittest.main()
