# Local Chat Messenger (3)

Recursion課題の **Python + UNIXドメインソケット（`AF_UNIX` / `SOCK_DGRAM`）+ Faker** による最小チャットアプリです。

## 課題に対応した動作

- クライアントが標準入力でメッセージを受け取る
- クライアントがUNIXドメインソケット経由で送信
- サーバーがメッセージを受信してFakerでダミー文章を生成
- 生成した文章をサーバーがクライアントに返送
- クライアントが返答を表示（何度も送信可能）
- 通信は **ローカルの同一マシン内**。TCP/UDPのIP通信ではない

## ディレクトリ構成

```text
local-chat-messenger-3/
├── README.md                   # 導入・動作説明
├── requirements.txt            # Fakerの依存関係
├── pyproject.toml              # Pythonプロジェクト定義
├── .gitignore
├── server.py                   # サーバー起動用
├── client.py                   # クライアント起動用
├── src/
│   ├── __init__.py
│   ├── protocol.py             # 通信設定・UTF-8・ソケット後片付け
│   ├── server.py               # Fakerで返信するサーバー
│   └── client.py               # 対話型クライアント
├── scripts/
│   ├── setup.sh                # 仮想環境と依存関係のインストール
│   └── demo.sh                 # 自動デモ
└── tests/
    ├── test_protocol.py
    └── test_integration.py
```

## 実行環境

- **WSL Ubuntu / Linux / macOS** 推奨（UNIXドメインソケット対応環境）
- Python 3.10以上
- Windowsネイティブ環境での動作は対象外（WSLを利用）
- Fakerライブラリ（インストール時のみインターネット接続が必要）

## インストール

```bash
cd local-chat-messenger-3
bash scripts/setup.sh
```

手動セットアップなら：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## 動かし方（ターミナルを2枚使う）

**ターミナルA — サーバー**

```bash
.venv/bin/python server.py
```

**ターミナルB — クライアント**

```bash
.venv/bin/python client.py
```

クライアントでメッセージを入力すると、Fakerが生成したランダムな日本語の文章が返ります。終了は `/quit`。サーバーは `Ctrl+C` で停止します。

**1回だけ送信する場合：**

```bash
.venv/bin/python client.py --message "こんにちは"
```

**サンプルを自動実行：**

```bash
bash scripts/demo.sh
```

## テスト

```bash
.venv/bin/python -m unittest discover -s tests -v
```

## 技術上の注意

1. **`SOCK_DGRAM` はデータグラム方式**です。TCPのような `listen()` や `accept()` は不要です。今回は `sendto()` と `recvfrom()` を使います。
2. サーバーが返送できるように、**クライアント側も `bind()` で自分のソケットパスを登録**しています。
3. UNIXソケットのパスは通常 `/tmp/` 以下です。Linux上のソケットファイルなので、プロジェクトフォルダー（特に `/mnt/c/` 側）には配置しません。
4. ソケットファイルは正常終了時に削除します。異常終了で残った場合は、**ほかのサーバーが稼働していないと確認してから** `python server.py --clean-socket` を使ってください。
5. データグラム1通あたり最大4096バイトです。これは学習用に決めた制限です。
6. Fakerは**LLMではありません**。受信した質問の意味に応じて回答するわけではなく、ダミー文章を生成します。
7. 今回の実装は単純な同期サーバーです。認証、暗号化、複数プロセスによる処理、データ永続化などは対象外です。

## 学習ポイント

- `socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)`：ソケット生成
- `sock.bind(path)`：送受信するローカルアドレスを登録
- `sock.sendto(data, address)`：指定アドレスへ送信
- `sock.recvfrom(4096)`：データと送信元を受信
- `.encode('utf-8')` / `.decode('utf-8')`：文字列とバイト列を相互変換
- `Faker('ja_JP').sentence()`：ダミーの日本語文章を生成
- `try/finally`：例外が起きてもリソースを解放

## GitHubへ提出する場合

`.venv/` や `*.sock` はGitで管理しないよう `.gitignore` に登録済みです。作成した公開リポジトリのURLをRecursionの課題画面へ提出してください。
