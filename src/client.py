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
