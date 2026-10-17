# test_integration.py — ソース全文と逐次解説

- **実装ファイル**：`tests/test_integration.py`
- **本書の目的**：このファイルを単独で読んでも、各行・関数の入力、出力、状態変化、設計意図が分かるようにする。
- **注意**：以下の全文は作成時点の実ファイルから自動取得しています。動作例のFaker結果は毎回変わります。

## 第1部：ソースコード全文（省略なし）

```python
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
```

## 第2部：コード順の詳細解説

### L1–L9：結合テストの依存

```text
  1 | import os
  2 | import socket
  3 | import tempfile
  4 | import threading
  5 | import time
  6 | import unittest
  7 | from pathlib import Path
  8 | from src.client import send_message
  9 | from src.server import run_server
```

`threading` は同一テストプロセス内でサーバーを別スレッド起動、`tempfile` は一時ソケットパス、`time.sleep` は起動待ち。実際の `send_message` と `run_server` をimportします。

### L12–L14：UNIX環境だけで実行

```text
 12 | @unittest.skipUnless(hasattr(socket, "AF_UNIX") and os.name == "posix", "UNIX sockets required")
 13 | class IntegrationTests(unittest.TestCase):
 14 |     def test_server_client_roundtrip_and_cleanup(self):
```

`@unittest.skipUnless(...)` はAF_UNIXがあり、POSIX環境の場合にのみテストするデコレーター。未対応のOSでは失敗ではなくスキップ。

### L15–L18：サーバーを別スレッドで起動

```text
 15 |         with tempfile.TemporaryDirectory() as d:
 16 |             path = str(Path(d) / "server.sock")
 17 |             thread = threading.Thread(target=run_server, args=(path, 2), daemon=True)
 18 |             thread.start()
```

一時ディレクトリ内の `server.sock` を使います。`args=(path,2)` は2件返信で停止させる設定。`daemon=True` はテストが終わった後の残存を抑える補助ですが、適切な終了処理の代替ではありません。

### L19–L23：待受開始を待つ

```text
 19 |             for _ in range(100):
 20 |                 if Path(path).exists():
 21 |                     break
 22 |                 time.sleep(0.01)
 23 |             self.assertTrue(Path(path).exists())
```

ループでソケットパスの存在を最大約1秒待ちます。`time.sleep(0.01)` は10ms単位の短い待機。存在しなければ `assertTrue` が失敗し、サーバー起動問題として分かります。

### L24–L26：英語・日本語の往復確認

```text
 24 |             for message in ["hello", "日本語で送信"]:
 25 |                 reply = send_message(message, path)
 26 |                 self.assertTrue(reply)
```

2つの文字列を順番に `send_message` して、返信が空でないことを検証。Fakerはランダム文なので内容一致を要求しません。

### L27–L29：正常終了とソケット掃除

```text
 27 |             thread.join(timeout=3)
 28 |             self.assertFalse(thread.is_alive())
 29 |             self.assertFalse(Path(path).exists())
```

`thread.join(timeout=3)` はサーバー処理の終了を待機。その後 `thread.is_alive()` が偽、`Path(path).exists()` が偽であることを検証。処理件数で正常終了しソケットパスが消えているかを調べます。

### L32–L33：テスト直接起動

```text
 32 | if __name__ == "__main__":
 33 |     unittest.main()
```

`unittest.main()` はテストファイルを直接起動した場合に実行。

## 第3部：このファイルを理解したか確認

1. このファイルは**何を受け取り、何を外部に返す／作用する**か説明できるか。
2. 呼び出す他ファイルの関数と、呼び出される関数を指せるか。
3. エラー時に起こる処理を追跡できるか。
4. 重要な変数の型（`str` / `bytes` / `socket` / `int` など）を区別できるか。
5. コードの一部を変更した際、テストや別ファイルに与える影響を予測できるか。

元ファイルと解説がずれていないかは、実装を修正した後に改めて確認してください。
