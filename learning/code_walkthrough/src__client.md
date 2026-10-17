# client.py — ソース全文と逐次解説

- **実装ファイル**：`src/client.py`
- **本書の目的**：このファイルを単独で読んでも、各行・関数の入力、出力、状態変化、設計意図が分かるようにする。
- **注意**：以下の全文は作成時点の実ファイルから自動取得しています。動作例のFaker結果は毎回変わります。

## 第1部：ソースコード全文（省略なし）

```python
"""コマンドラインからメッセージを送信するクライアント。"""
from __future__ import annotations

import argparse
import os
import socket
import tempfile
import uuid
from pathlib import Path

from .protocol import DEFAULT_SERVER_PATH, MAX_BYTES, decode_message, encode_message, unlink_socket


def send_message(message: str, server_path: str = DEFAULT_SERVER_PATH, timeout: float = 5.0) -> str:
    """自分のソケットをbindして送信し、返信を受信する。"""
    payload = encode_message(message)
    client_path = str(Path(tempfile.gettempdir()) / f"lcm3_{os.getpid()}_{uuid.uuid4().hex[:8]}.sock")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        sock.settimeout(timeout)
        # SOCK_DGRAMではサーバーが返送する宛先を知るため、クライアントもbindする。
        sock.bind(client_path)
        sock.sendto(payload, server_path)
        received, _ = sock.recvfrom(MAX_BYTES + 1)
        if len(received) > MAX_BYTES:
            raise ValueError("返信が長すぎます。")
        return decode_message(received)
    finally:
        sock.close()
        unlink_socket(client_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Chat Messenger (3) クライアント")
    parser.add_argument("--socket", default=DEFAULT_SERVER_PATH, help="サーバー側のUNIXソケットパス")
    parser.add_argument("--message", help="一度だけ送信するメッセージ（省略すると対話モード）")
    parser.add_argument("--timeout", type=float, default=5.0, help="応答待ち秒数")
    args = parser.parse_args()

    if args.message is not None:
        messages = [args.message]
    else:
        print("[client] メッセージを入力（終了: /quit または Ctrl+C）")
        def input_messages():
            while True:
                try:
                    message = input("あなた> ")
                except (EOFError, KeyboardInterrupt):
                    print()
                    return
                if message.strip() == "/quit":
                    return
                if message.strip():
                    yield message
        messages = input_messages()

    for message in messages:
        try:
            answer = send_message(message, args.socket, args.timeout)
            print(f"Faker> {answer}")
        except (OSError, ValueError, UnicodeDecodeError) as exc:
            print(f"[client] 通信エラー: {exc}")
            if args.message is not None:
                raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
```

## 第2部：コード順の詳細解説

### L1–L11：依存関係と型・インポート

```text
  1 | """コマンドラインからメッセージを送信するクライアント。"""
  2 | from __future__ import annotations
  3 | 
  4 | import argparse
  5 | import os
  6 | import socket
  7 | import tempfile
  8 | import uuid
  9 | from pathlib import Path
 10 | 
 11 | from .protocol import DEFAULT_SERVER_PATH, MAX_BYTES, decode_message, encode_message, unlink_socket
```

`from __future__ import annotations` は型ヒント評価を遅らせる宣言。`argparse` はCLI引数、`os.getpid()` はプロセスID、`tempfile` は一時ディレクトリ、`uuid` は衝突回避用のランダム文字列、`Path` はパス操作。`.protocol` は同じ `src` パッケージ内から上限・変換関数・掃除関数を取り込む相対importです。インポート時点では通信は発生しません。

### L14–L18：通信関数の定義・準備

```text
 14 | def send_message(message: str, server_path: str = DEFAULT_SERVER_PATH, timeout: float = 5.0) -> str:
 15 |     """自分のソケットをbindして送信し、返信を受信する。"""
 16 |     payload = encode_message(message)
 17 |     client_path = str(Path(tempfile.gettempdir()) / f"lcm3_{os.getpid()}_{uuid.uuid4().hex[:8]}.sock")
 18 |     sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
```

`send_message(message: str, server_path: str = ..., timeout: float = 5.0) -> str` は文字列を受け取って返信文字列を返す関数。`encode_message` はstr→bytes変換と4096バイト制限の検査。`client_path` は `/tmp/lcm3_<PID>_<random>.sock` のような一時アドレス。`socket.socket(AF_UNIX, SOCK_DGRAM)` はローカルのデータグラム通信口を作成します。

### L19–L23：クライアントの宛先設定と送信

```text
 19 |     try:
 20 |         sock.settimeout(timeout)
 21 |         # SOCK_DGRAMではサーバーが返送する宛先を知るため、クライアントもbindする。
 22 |         sock.bind(client_path)
 23 |         sock.sendto(payload, server_path)
```

`try` でリソース解放を保証。`settimeout(timeout)` は受信等の待機時間を制限。`bind(client_path)` は**自分が返信を受け取るアドレス**を作る操作です。`sendto(payload, server_path)` はUTF-8バイト列をサーバーのソケットパスへ1データグラムとして送ります。これを省くと返信できません。

### L24–L27：返信受信・検査・戻り値

```text
 24 |         received, _ = sock.recvfrom(MAX_BYTES + 1)
 25 |         if len(received) > MAX_BYTES:
 26 |             raise ValueError("返信が長すぎます。")
 27 |         return decode_message(received)
```

`received, _ = recvfrom(MAX_BYTES + 1)` は `(bytes, 送信元アドレス)` のうちbytesだけを利用します。4096超を検出するため4097バイト受信。長すぎれば`ValueError`。`return decode_message(received)` はUTF-8デコードした返信文字列を呼び出し元へ返します。`_` は使わない値の慣用名です。

### L28–L30：後片付け（重要）

```text
 28 |     finally:
 29 |         sock.close()
 30 |         unlink_socket(client_path)
```

`finally` は正常終了・例外のどちらでも実行。`sock.close()` はソケットを閉じ、`unlink_socket(client_path)` は一時ソケットの**パス**を削除。closeだけではファイルシステム上のアドレスが残る場合があります。

### L33–L38：CLI入口

```text
 33 | def main() -> None:
 34 |     parser = argparse.ArgumentParser(description="Local Chat Messenger (3) クライアント")
 35 |     parser.add_argument("--socket", default=DEFAULT_SERVER_PATH, help="サーバー側のUNIXソケットパス")
 36 |     parser.add_argument("--message", help="一度だけ送信するメッセージ（省略すると対話モード）")
 37 |     parser.add_argument("--timeout", type=float, default=5.0, help="応答待ち秒数")
 38 |     args = parser.parse_args()
```

`main() -> None` が `ArgumentParser` を作成。`--socket` は宛先、`--message` があれば一回送信、`--timeout` は秒数。`type=float` でCLIの文字列を浮動小数点数に変換。`parse_args()` が実際のコマンド引数を読みます。

### L40–L55：一回送信と対話モードの分岐

```text
 40 |     if args.message is not None:
 41 |         messages = [args.message]
 42 |     else:
 43 |         print("[client] メッセージを入力（終了: /quit または Ctrl+C）")
 44 |         def input_messages():
 45 |             while True:
 46 |                 try:
 47 |                     message = input("あなた> ")
 48 |                 except (EOFError, KeyboardInterrupt):
 49 |                     print()
 50 |                     return
 51 |                 if message.strip() == "/quit":
 52 |                     return
 53 |                 if message.strip():
 54 |                     yield message
 55 |         messages = input_messages()
```

`args.message is not None` なら一要素配列を作り1回だけ送信。省略時は `input_messages()` というジェネレーターを定義。`input()` は標準入力、`except (EOFError, KeyboardInterrupt)` はCtrl+D/Ctrl+C対応、`strip()` は前後空白の除去。`/quit` なら終了し、空白以外なら `yield message` で**次の一件**を出す。`yield` は処理状態を保存して次の反復時に再開します。

### L57–L64：送信ループ・例外処理

```text
 57 |     for message in messages:
 58 |         try:
 59 |             answer = send_message(message, args.socket, args.timeout)
 60 |             print(f"Faker> {answer}")
 61 |         except (OSError, ValueError, UnicodeDecodeError) as exc:
 62 |             print(f"[client] 通信エラー: {exc}")
 63 |             if args.message is not None:
 64 |                 raise SystemExit(1) from exc
```

`for message in messages` は一件送信にもジェネレーターの複数件にも対応。`send_message()` から得た文字列を`Faker>`付きで表示。通信関連例外をまとめて捕捉しメッセージ表示。一回送信モードなら`SystemExit(1)`で失敗を終了コードに反映し、対話モードなら次入力へ継続します。

### L67–L68：直接起動時だけmainを呼ぶ

```text
 67 | if __name__ == "__main__":
 68 |     main()
```

Pythonファイルの直接実行では `__name__` が `"__main__"` になる。`import src.client` だけではmainが起動しないので、テストが `send_message` を直接取り出せます。

## 第3部：このファイルを理解したか確認

1. このファイルは**何を受け取り、何を外部に返す／作用する**か説明できるか。
2. 呼び出す他ファイルの関数と、呼び出される関数を指せるか。
3. エラー時に起こる処理を追跡できるか。
4. 重要な変数の型（`str` / `bytes` / `socket` / `int` など）を区別できるか。
5. コードの一部を変更した際、テストや別ファイルに与える影響を予測できるか。

元ファイルと解説がずれていないかは、実装を修正した後に改めて確認してください。
