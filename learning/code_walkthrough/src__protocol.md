# protocol.py — ソース全文と逐次解説

- **実装ファイル**：`src/protocol.py`
- **本書の目的**：このファイルを単独で読んでも、各行・関数の入力、出力、状態変化、設計意図が分かるようにする。
- **注意**：以下の全文は作成時点の実ファイルから自動取得しています。動作例のFaker結果は毎回変わります。

## 第1部：ソースコード全文（省略なし）

```python
"""共有する通信規約。課題通り AF_UNIX / SOCK_DGRAM を使う。"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

MAX_BYTES = 4096
DEFAULT_SERVER_PATH = str(Path(tempfile.gettempdir()) / "local_chat_messenger_3_server.sock")


def encode_message(message: str) -> bytes:
    """文字列をUTF-8に変換し、1データグラムの上限をチェックする。"""
    payload = message.encode("utf-8")
    if len(payload) > MAX_BYTES:
        raise ValueError(f"メッセージが長すぎます（最大 {MAX_BYTES} バイト）。")
    return payload


def decode_message(payload: bytes) -> str:
    return payload.decode("utf-8")


def unlink_socket(path: str) -> None:
    """UNIXソケットファイルだけを削除。一般ファイルは絶対に削除しない。"""
    import stat
    try:
        mode = os.lstat(path).st_mode
    except FileNotFoundError:
        return
    if not stat.S_ISSOCK(mode):
        raise RuntimeError(f"ソケット以外のファイルが存在します: {path}")
    os.unlink(path)
```

## 第2部：コード順の詳細解説

### L1–L9：共通定数とモジュール

```text
  1 | """共有する通信規約。課題通り AF_UNIX / SOCK_DGRAM を使う。"""
  2 | from __future__ import annotations
  3 | 
  4 | import os
  5 | import tempfile
  6 | from pathlib import Path
  7 | 
  8 | MAX_BYTES = 4096
  9 | DEFAULT_SERVER_PATH = str(Path(tempfile.gettempdir()) / "local_chat_messenger_3_server.sock")
```

通信規約を1か所に集約。`MAX_BYTES=4096` は送受信するメッセージのアプリ上限。`DEFAULT_SERVER_PATH` は一時ディレクトリ内のUNIXソケットアドレス。`Path(...) / "filename"` はパスの結合で、実体のファイルを作る操作ではありません。

### L12–L17：文字列をバイト列へ

```text
 12 | def encode_message(message: str) -> bytes:
 13 |     """文字列をUTF-8に変換し、1データグラムの上限をチェックする。"""
 14 |     payload = message.encode("utf-8")
 15 |     if len(payload) > MAX_BYTES:
 16 |         raise ValueError(f"メッセージが長すぎます（最大 {MAX_BYTES} バイト）。")
 17 |     return payload
```

`message: str` と `-> bytes` は型ヒント。`encode("utf-8")` で送信用bytesを作り、`len(payload)` で**文字数ではなくバイト数**を検査。超過なら `ValueError`、正常ならbytesを返します。日本語は通常1文字3バイトになります。

### L20–L21：バイト列から文字列へ

```text
 20 | def decode_message(payload: bytes) -> str:
 21 |     return payload.decode("utf-8")
```

`decode_message(payload: bytes) -> str` は `payload.decode("utf-8")` を返す。受信側の逆変換。不正なUTF-8なら `UnicodeDecodeError` が発生するため、呼び出し元で処理する必要があります。

### L24–L33：ソケットだけ安全に削除

```text
 24 | def unlink_socket(path: str) -> None:
 25 |     """UNIXソケットファイルだけを削除。一般ファイルは絶対に削除しない。"""
 26 |     import stat
 27 |     try:
 28 |         mode = os.lstat(path).st_mode
 29 |     except FileNotFoundError:
 30 |         return
 31 |     if not stat.S_ISSOCK(mode):
 32 |         raise RuntimeError(f"ソケット以外のファイルが存在します: {path}")
 33 |     os.unlink(path)
```

`unlink_socket(path)` はパスを削除するが**通常ファイルは守る**関数。`os.lstat(path)` でファイル種類を調べ、なければ何もせず戻る。`stat.S_ISSOCK(mode)` が偽なら`RuntimeError`、UNIXソケットなら`os.unlink(path)`。シンボリックリンクも通常ファイルとして拒否する設計。

## 第3部：このファイルを理解したか確認

1. このファイルは**何を受け取り、何を外部に返す／作用する**か説明できるか。
2. 呼び出す他ファイルの関数と、呼び出される関数を指せるか。
3. エラー時に起こる処理を追跡できるか。
4. 重要な変数の型（`str` / `bytes` / `socket` / `int` など）を区別できるか。
5. コードの一部を変更した際、テストや別ファイルに与える影響を予測できるか。

元ファイルと解説がずれていないかは、実装を修正した後に改めて確認してください。
