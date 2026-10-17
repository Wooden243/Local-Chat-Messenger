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
