# 02 | 重要技術・構文の解説

## 1. クライアントとサーバー【必須】

**サーバー**は先に起動してリクエストを受け取る側、**クライアント**は要求する側です。本件はブラウザを使わず、両方ともPythonのCLIプログラムです。HTTPも利用しません。サーバーが先に `bind` し、クライアントが `sendto` すると受信できます。

## 2. ソケット・アドレスファミリー【必須】

`socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)` は `socket` オブジェクトを作ります。`AF_UNIX` は同じマシン内のファイルシステム上のパスをアドレスとして用い、`SOCK_DGRAM` は一つの送信を一つのメッセージとして扱います。TCPで用いる `listen/accept` は不要です。ここでのソケットファイルは普通のテキストファイルではありません。

## 3. bind / sendto / recvfrom【必須】

- `sock.bind(path)` は自分のソケットの受信先アドレスを確立。サーバーは固定パス、クライアントは返信を受けるための一時パスを登録します。
- `sock.sendto(data, path)` は**bytes** と宛先パスを指定して送信します。メッセージを返信する側は `recvfrom` で得た `address` を宛先にします。
- `data, address = sock.recvfrom(buffer_size)` は受信データのバイト列と送信元アドレスの組を受け取ります。クライアント側では返信元を使わないので `_` に捨てています。
- `recvfrom` はデータが来るまで待つ操作です。クライアントは `settimeout(5.0)` で待ち時間を制限しています。

## 4. str と bytes / UTF-8【必須】

Pythonの `str` は文字の列、`bytes` はバイト列です。ソケットの `sendto` に渡すデータを `message.encode('utf-8')` で変換し、受信後に `payload.decode('utf-8')` で復元します。日本語1文字は通常UTF-8で3バイトなので、**文字数とバイト数は別**です。今回の上限 `MAX_BYTES=4096` はバイト数。

```python
s = 'あ'
b = s.encode('utf-8')
print(len(s))  # 1文字
print(len(b))  # 3バイト
print(b.decode('utf-8'))  # あ
```

## 5. `try/finally`【必須】

`try` 内の実行途中で例外が起きても `finally` が実行されるため、`sock.close()` と `unlink_socket(...)` でソケットやアドレスを片付けます。後片付けが例外を出す場合は新しい例外が発生することにも注意してください。

## 6. `argparse`【重要】

`ArgumentParser` は `python client.py --message 'こんにちは'` の `--message` のようなコマンドライン引数を解析します。`--socket` はサーバーのアドレス、`--timeout` は返信待ち秒数、`--max-messages` はテスト用の処理件数です。

## 7. `yield`【重要】

`input_messages()` の `yield message` は、`return` と異なり関数の実行位置を保ったまま**値を1件ずつ出すジェネレーター**です。`for message in messages` が次の値を求めたとき入力処理が再開します。これで連続的に入力を受け取れます。

## 8. Faker【参考】

`Faker('ja_JP').sentence(nb_words=8)` は日本語のダミー文を作ります。**意味に沿う回答ではありません**。`make_reply(message, fake)` では引数 `message` は使われず、サーバー側ログに別途表示されます。LLMは含まれていません。

## 9. `if __name__ == '__main__'`【重要】

ファイルを直接起動したときだけ `main()` を実行します。他のファイルから `import` しただけでは起動しません。テストやモジュール再利用に便利です。

## 10. 型ヒント `str`, `float`, `None`, `int | None`【重要】

引数・戻り値の意図を記します。`-> str` は文字列を返す設計、`-> None` は通常戻り値を使わない設計、`int | None` は整数か `None` を受け付ける型です。Pythonは通常、これらの型を実行時に自動強制しません。

## 11. `tempfile`, `os.getpid`, `uuid`【参考】

`tempfile.gettempdir()` は一時ディレクトリのパス、`os.getpid()` はプロセスID、`uuid.uuid4().hex[:8]` は衝突しにくくするランダム部分。**一時ソケット名を送信ごとに重複しにくくする**目的です。

## 12. `unittest` と結合テスト【重要】

単体テストは `encode_message` や保護ロジックを検査します。結合テストはサーバーを別スレッドで起動し、本当にメッセージの往復ができるか調べます。Fakerの文章は不定なので**文字列の内容は完全一致比較していません**。

## 13. よくある誤解【必須】

- `socket.sendto('こんにちは', path)` は誤り。原則bytesに変換する。
- `SOCK_DGRAM` はTCPではない。`listen()` を書く必要はない。
- `recvfrom()` の戻り値は文字列1つではなく、`(bytes, address)` の組。
- `sock.close()` とソケット**ファイルの削除**は別操作。
- `from src.client import main` は `main()` を実行しない。次の行で呼び出して初めて起動する。
- `Faker` は会話の理解・推論をしない。
