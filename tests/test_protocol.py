import tempfile
import unittest
from pathlib import Path
from faker import Faker
from src.protocol import encode_message, decode_message, unlink_socket, MAX_BYTES
from src.server import make_reply


class ProtocolTests(unittest.TestCase):
    def test_unicode_roundtrip(self):
        self.assertEqual(decode_message(encode_message("こんにちは")), "こんにちは")

    def test_size_limit(self):
        with self.assertRaises(ValueError):
            encode_message("あ" * (MAX_BYTES // 3 + 1))

    def test_does_not_unlink_regular_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "protected.txt"
            p.write_text("keep")
            with self.assertRaises(RuntimeError):
                unlink_socket(str(p))
            self.assertTrue(p.exists())

    def test_faker_produces_reply(self):
        self.assertTrue(make_reply("hello", Faker("ja_JP")))


if __name__ == "__main__":
    unittest.main()
