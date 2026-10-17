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
