# 04 | デバッグ・トラブルシューティング

## 起動前の確認

```bash
python3 --version
bash scripts/setup.sh
.venv/bin/python -m unittest discover -s tests -v
```

サーバーを**先に**起動してからクライアントを起動してください。

## エラー別対処

| 症状 | 主な原因 | 対処 |
|---|---|---|
| `ModuleNotFoundError: faker` | Faker未インストール | `.venv/bin/python -m pip install -r requirements.txt` |
| `FileNotFoundError` / サーバー宛先なし | サーバー未起動、パス違い | 先にサーバーを起動、双方の `--socket` を一致させる |
| `パスが使用中です` | ソケットが残っている、または別サーバー稼働中 | サーバーの稼働確認後、必要なら `server.py --clean-socket` |
| `socket.timeout` | サーバー未応答 | サーバーログ、`--timeout`、同じパスか確認 |
| `UnicodeDecodeError` | UTF-8でないデータ | 送信側で `encode('utf-8')` を使う |
| `ValueError: メッセージが長すぎます` | UTF-8で4096バイト超 | 入力を短くする。日本語は文字数≠バイト数 |
| `Operation not supported` など | OSやファイルシステムが不適切 | WSL UbuntuのLinux側 `/home/...` などで実行する |
| 通信は成功するが返事が的外れ | Fakerは会話AIではない | 仕様通り。意味に沿う応答はLLMが必要 |

## 最短の切り分け手順

1. `.venv/bin/python -m unittest discover -s tests -v` の結果を見る。
2. ターミナルAでサーバーを起動し、`[server] 待受中` が出るか調べる。
3. ターミナルBで `.venv/bin/python client.py --message 'こんにちは'` を実行する。
4. サーバー側で `[server] 受信:` と `[server] 返信:` が出るか確認する。
5. 受信が表示されなければパスやbind/sendtoを調べ、受信後に問題があればFaker・decode・encodeを調べる。

## ログを追加するポイント

- `src/client.py` の送信直前：`print('送信バイト数', len(payload))`
- `src/server.py` の受信直後：`print('送信元', address, 'バイト数', len(payload))`
- `src/client.py` の受信直後：`print('返信バイト数', len(received))`

本番向けなら `logging` の利用を検討してください。

## ファイル削除の注意

`--clean-socket` はソケットファイルを削除します。ほかのサーバープロセスが使用中なら誤動作の原因になります。**実行前にほかのサーバーが動いていないことを確認**してください。

## デバッグ用の小実験

`src/protocol.py` の `MAX_BYTES` は4096。Pythonのコンソールで `len('あ'.encode('utf-8'))` を実行すると3が返ります。日本語と英語でバイト長が異なることを確認してください。
