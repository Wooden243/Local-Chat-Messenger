import os
import socket
import tempfile
import threading
import time
import unittest
from pathlib import Path
from src.client import send_message
from src.server import run_server


@unittest.skipUnless(hasattr(socket, "AF_UNIX") and os.name == "posix", "UNIX sockets required")
class IntegrationTests(unittest.TestCase):
    def test_server_client_roundtrip_and_cleanup(self):
        with tempfile.TemporaryDirectory() as d:
            path = str(Path(d) / "server.sock")
            thread = threading.Thread(target=run_server, args=(path, 2), daemon=True)
            thread.start()
            for _ in range(100):
                if Path(path).exists():
                    break
                time.sleep(0.01)
            self.assertTrue(Path(path).exists())
            for message in ["hello", "日本語で送信"]:
                reply = send_message(message, path)
                self.assertTrue(reply)
            thread.join(timeout=3)
            self.assertFalse(thread.is_alive())
            self.assertFalse(Path(path).exists())


if __name__ == "__main__":
    unittest.main()
