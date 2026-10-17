# server.py — ソース全文と逐次解説

- **実装ファイル**：`src/server.py`
- **本書の目的**：このファイルを単独で読んでも、各行・関数の入力、出力、状態変化、設計意図が分かるようにする。
- **注意**：以下の全文は作成時点の実ファイルから自動取得しています。動作例のFaker結果は毎回変わります。

## 第1部：ソースコード全文（省略なし）

```python
"""Fakerを使ってランダムな文字列を返信するUNIXデータグラムサーバー。"""
from __future__ import annotations

import argparse
import socket

from faker import Faker

from .protocol import DEFAULT_SERVER_PATH, MAX_BYTES, decode_message, encode_message, unlink_socket


def make_reply(message: str, fake: Faker) -> str:
    """ユーザー入力の内容に関わらず、Fakerで返信テキストを生成する。"""
    # Fakerが実際に生成した情報を返信。入力メッセージはログに残す。
    return fake.sentence(nb_words=8)


def run_server(path: str = DEFAULT_SERVER_PATH, max_messages: int | None = None) -> None:
    if max_messages is not None and max_messages < 1:
        raise ValueError("max_messages は1以上を指定してください")

    # 既存のサーバーソケットを誤って消さないようにする。
    # 残骸がある場合は --clean-socket で明示的に削除する。
    import os
    if os.path.lexists(path):
        raise RuntimeError(f"パスが使用中です: {path}（起動していなければ --clean-socket を使用）")

    fake = Faker("ja_JP")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        sock.bind(path)
        print(f"[server] 待受中: {path}", flush=True)
        served = 0
        while max_messages is None or served < max_messages:
            # 受信は1データグラム単位。送信元のクライアントパスも取得する。
            payload, address = sock.recvfrom(MAX_BYTES + 1)
            if not address:
                print("[server] 返信先アドレスがありません。スキップします。", flush=True)
                continue
            try:
                message = decode_message(payload)
                if len(payload) > MAX_BYTES:
                    answer = "メッセージが長すぎます。"
                else:
                    print(f"[server] 受信: {message}", flush=True)
                    answer = make_reply(message, fake)
                sock.sendto(encode_message(answer), address)
                print(f"[server] 返信: {answer}", flush=True)
            except UnicodeDecodeError:
                sock.sendto(encode_message("UTF-8の文字列を送信してください。"), address)
            served += 1
    except KeyboardInterrupt:
        print("\n[server] 停止します。", flush=True)
    finally:
        sock.close()
        unlink_socket(path)
        print("[server] ソケットを片付けました。", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Chat Messenger (3) サーバー")
    parser.add_argument("--socket", default=DEFAULT_SERVER_PATH, help="サーバー側のUNIXソケットパス")
    parser.add_argument("--max-messages", type=int, default=None, help="指定件数返信したら終了（テスト用）")
    parser.add_argument("--clean-socket", action="store_true", help="残存するソケットファイルを明示的に除去")
    args = parser.parse_args()
    if args.clean_socket:
        unlink_socket(args.socket)
    run_server(args.socket, args.max_messages)


if __name__ == "__main__":
    main()
```

## 第2部：コード順の詳細解説

### L1–L9：モジュールと依存

```text
  1 | """Fakerを使ってランダムな文字列を返信するUNIXデータグラムサーバー。"""
  2 | from __future__ import annotations
  3 | 
  4 | import argparse
  5 | import socket
  6 | 
  7 | from faker import Faker
  8 | 
  9 | from .protocol import DEFAULT_SERVER_PATH, MAX_BYTES, decode_message, encode_message, unlink_socket
```

`socket` は通信、`argparse` はCLI解析、`Faker` はテスト用ランダム文章生成。`protocol` から共通のパス/サイズ/エンコード・デコード・後片付けをimport。クライアントと同じ規約を使うため重複設定を避けています。

### L12–L15：Faker返信関数

```text
 12 | def make_reply(message: str, fake: Faker) -> str:
 13 |     """ユーザー入力の内容に関わらず、Fakerで返信テキストを生成する。"""
 14 |     # Fakerが実際に生成した情報を返信。入力メッセージはログに残す。
 15 |     return fake.sentence(nb_words=8)
```

`make_reply(message: str, fake: Faker) -> str` は実際には入力`message`を参照しません。`fake.sentence(nb_words=8)` がランダムな日本語文を生成します。`nb_words` はFakerの文章生成の目安で、必ず8語になる保証ではありません。会話AIとの違いに注意。

### L18–L20：サーバー関数と件数チェック

```text
 18 | def run_server(path: str = DEFAULT_SERVER_PATH, max_messages: int | None = None) -> None:
 19 |     if max_messages is not None and max_messages < 1:
 20 |         raise ValueError("max_messages は1以上を指定してください")
```

`run_server(path, max_messages)` はデフォルトで無期限待受。`max_messages` が整数ならその件数だけ返信して終了するテスト用機能。1未満は不正として `ValueError`。`int | None` は整数または未指定を表します。

### L22–L26：既存ソケットの安全性

```text
 22 |     # 既存のサーバーソケットを誤って消さないようにする。
 23 |     # 残骸がある場合は --clean-socket で明示的に削除する。
 24 |     import os
 25 |     if os.path.lexists(path):
 26 |         raise RuntimeError(f"パスが使用中です: {path}（起動していなければ --clean-socket を使用）")
```

既にソケットパスがある場合は、無条件に削除せず `RuntimeError` として停止。`os.path.lexists` は壊れたシンボリックリンクも検出する。ほかの稼働中サーバーのアドレスを奪う事故を避ける意図です。

### L28–L33：Faker初期化・bind・初期状態

```text
 28 |     fake = Faker("ja_JP")
 29 |     sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
 30 |     try:
 31 |         sock.bind(path)
 32 |         print(f"[server] 待受中: {path}", flush=True)
 33 |         served = 0
```

`Faker("ja_JP")` は日本語向けロケール。`socket.socket` はデータグラムソケットを作成。`sock.bind(path)` は待受アドレスを設定。`served=0` は返信したデータグラムの件数。`flush=True` はログをすぐ標準出力へ書き出します。

### L34–L39：受信ループ・送信元確認

```text
 34 |         while max_messages is None or served < max_messages:
 35 |             # 受信は1データグラム単位。送信元のクライアントパスも取得する。
 36 |             payload, address = sock.recvfrom(MAX_BYTES + 1)
 37 |             if not address:
 38 |                 print("[server] 返信先アドレスがありません。スキップします。", flush=True)
 39 |                 continue
```

`while max_messages is None or served < max_messages` は制限なし、または上限未満の間繰り返します。`payload, address = recvfrom(MAX_BYTES+1)` はバイト列と送信元アドレスを返す（待受でブロック）。`if not address` は宛先が分からない要求を処理せず次ループへ。

### L40–L48：デコード・Faker・返信

```text
 40 |             try:
 41 |                 message = decode_message(payload)
 42 |                 if len(payload) > MAX_BYTES:
 43 |                     answer = "メッセージが長すぎます。"
 44 |                 else:
 45 |                     print(f"[server] 受信: {message}", flush=True)
 46 |                     answer = make_reply(message, fake)
 47 |                 sock.sendto(encode_message(answer), address)
 48 |                 print(f"[server] 返信: {answer}", flush=True)
```

`decode_message(payload)` でstr化。次の長さチェックで4096バイト超ならエラー文、そうでなければ受信内容をログ表示し`make_reply`で文章生成。`sock.sendto(encode_message(answer), address)` は、**直前に受け取った送信元アドレス**に返信。実装上はデコードをサイズ検査より先に行っている点に注意。

### L49–L51：文字化け対処・件数更新

```text
 49 |             except UnicodeDecodeError:
 50 |                 sock.sendto(encode_message("UTF-8の文字列を送信してください。"), address)
 51 |             served += 1
```

不正UTF-8のときは `UnicodeDecodeError` を捕捉し、UTF-8利用を促す日本語メッセージを返信。`served += 1` は通常分岐/UnicodeDecodeError分岐を終えた後だけ実行されるため、返信処理中に別の未捕捉例外が出れば加算されません。

### L52–L57：Ctrl+Cと終了処理

```text
 52 |     except KeyboardInterrupt:
 53 |         print("\n[server] 停止します。", flush=True)
 54 |     finally:
 55 |         sock.close()
 56 |         unlink_socket(path)
 57 |         print("[server] ソケットを片付けました。", flush=True)
```

`KeyboardInterrupt` はCtrl+C。`finally` 内の `sock.close()` でOSソケットを閉じ、`unlink_socket(path)` でソケットファイルを削除。強制終了などではfinallyが走らない場合もあります。

### L60–L68：CLI解析と明示掃除

```text
 60 | def main() -> None:
 61 |     parser = argparse.ArgumentParser(description="Local Chat Messenger (3) サーバー")
 62 |     parser.add_argument("--socket", default=DEFAULT_SERVER_PATH, help="サーバー側のUNIXソケットパス")
 63 |     parser.add_argument("--max-messages", type=int, default=None, help="指定件数返信したら終了（テスト用）")
 64 |     parser.add_argument("--clean-socket", action="store_true", help="残存するソケットファイルを明示的に除去")
 65 |     args = parser.parse_args()
 66 |     if args.clean_socket:
 67 |         unlink_socket(args.socket)
 68 |     run_server(args.socket, args.max_messages)
```

`--socket` は待受パス、`--max-messages` は終了件数、`--clean-socket` は `action="store_true"` で指定すると真になります。掃除は `unlink_socket` を呼びますが、**稼働中サーバーのアドレスを消さないようユーザーの確認が必要**です。

### L71–L72：直接起動の条件

```text
 71 | if __name__ == "__main__":
 72 |     main()
```

`__name__ == "__main__"` のときだけ `main()` を実行。他のモジュールから `run_server()` をimportしてテスト可能にしています。

## 第3部：このファイルを理解したか確認

1. このファイルは**何を受け取り、何を外部に返す／作用する**か説明できるか。
2. 呼び出す他ファイルの関数と、呼び出される関数を指せるか。
3. エラー時に起こる処理を追跡できるか。
4. 重要な変数の型（`str` / `bytes` / `socket` / `int` など）を区別できるか。
5. コードの一部を変更した際、テストや別ファイルに与える影響を予測できるか。

元ファイルと解説がずれていないかは、実装を修正した後に改めて確認してください。
