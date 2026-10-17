# test_protocol.py — ソース全文と逐次解説

- **実装ファイル**：`tests/test_protocol.py`
- **本書の目的**：このファイルを単独で読んでも、各行・関数の入力、出力、状態変化、設計意図が分かるようにする。
- **注意**：以下の全文は作成時点の実ファイルから自動取得しています。動作例のFaker結果は毎回変わります。

## 第1部：ソースコード全文（省略なし）

```python
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
```

## 第2部：コード順の詳細解説

### L1–L7：テスト対象のインポート

```text
  1 | import tempfile
  2 | import unittest
  3 | from pathlib import Path
  4 | from faker import Faker
  5 | from src.protocol import encode_message, decode_message, unlink_socket, MAX_BYTES
  6 | from src.server import make_reply
  7 | 
```

`unittest` はPython標準テストフレームワーク、`tempfile` は安全な一時作業場所、`Faker` は返信生成の確認用。`src.protocol` と `src.server` から実際の関数をimportしています。

### L9–L11：UTF-8の往復テスト

```text
  9 | class ProtocolTests(unittest.TestCase):
 10 |     def test_unicode_roundtrip(self):
 11 |         self.assertEqual(decode_message(encode_message("こんにちは")), "こんにちは")
```

`unittest.TestCase` を継承。`assertEqual` で、`encode_message` して `decode_message` した日本語が元の文字列と一致することを確認しています。

### L13–L15：サイズ上限のテスト

```text
 13 |     def test_size_limit(self):
 14 |         with self.assertRaises(ValueError):
 15 |             encode_message("あ" * (MAX_BYTES // 3 + 1))
```

`assertRaises(ValueError)` はエラーになることが成功条件。`"あ" * (MAX_BYTES // 3 + 1)` は日本語1文字が3バイトという特性を使って4096バイトを超える入力を作っています。

### L17–L23：通常ファイルを守れるか

```text
 17 |     def test_does_not_unlink_regular_file(self):
 18 |         with tempfile.TemporaryDirectory() as d:
 19 |             p = Path(d) / "protected.txt"
 20 |             p.write_text("keep")
 21 |             with self.assertRaises(RuntimeError):
 22 |                 unlink_socket(str(p))
 23 |             self.assertTrue(p.exists())
```

`TemporaryDirectory()` は一時フォルダを作り文脈終了で後片付け。通常の `protected.txt` に対し `unlink_socket` が `RuntimeError` を出すこと、その後ファイルが存在することを二段階で検査します。

### L25–L26：Faker返信の最低限テスト

```text
 25 |     def test_faker_produces_reply(self):
 26 |         self.assertTrue(make_reply("hello", Faker("ja_JP")))
```

`assertTrue(make_reply(...))` は空文字列ではないことを検査。生成内容はランダムなので内容の完全一致は調べていません。

### L29–L30：テスト直接起動

```text
 29 | if __name__ == "__main__":
 30 |     unittest.main()
```

`python tests/test_protocol.py` のように直接起動された場合 `unittest.main()` がテストを走らせます。通常は `python -m unittest discover` でも実行できます。

## 第3部：このファイルを理解したか確認

1. このファイルは**何を受け取り、何を外部に返す／作用する**か説明できるか。
2. 呼び出す他ファイルの関数と、呼び出される関数を指せるか。
3. エラー時に起こる処理を追跡できるか。
4. 重要な変数の型（`str` / `bytes` / `socket` / `int` など）を区別できるか。
5. コードの一部を変更した際、テストや別ファイルに与える影響を予測できるか。

元ファイルと解説がずれていないかは、実装を修正した後に改めて確認してください。
