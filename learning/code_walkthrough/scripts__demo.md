# demo.sh — ソース全文と逐次解説

- **実装ファイル**：`scripts/demo.sh`
- **本書の目的**：このファイルを単独で読んでも、各行・関数の入力、出力、状態変化、設計意図が分かるようにする。
- **注意**：以下の全文は作成時点の実ファイルから自動取得しています。動作例のFaker結果は毎回変わります。

## 第1部：ソースコード全文（省略なし）

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-.venv/bin/python}"
"$PY" server.py --max-messages 2 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT
sleep 0.4
"$PY" client.py --message 'こんにちは'
"$PY" client.py --message 'おすすめの名前を教えて'
wait "$SERVER_PID"
trap - EXIT
```

## 第2部：コード順の詳細解説

### L1–L4：デモ準備

```text
  1 | #!/usr/bin/env bash
  2 | set -euo pipefail
  3 | cd "$(dirname "$0")/.."
  4 | PY="${PYTHON:-.venv/bin/python}"
```

Bash安全設定とプロジェクトルート移動。`PY="${PYTHON:-.venv/bin/python}"` はPYTHON環境変数があればそれを、なければ仮想環境のPythonを使用。

### L5–L8：サーバーをバックグラウンドで起動

```text
  5 | "$PY" server.py --max-messages 2 &
  6 | SERVER_PID=$!
  7 | trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT
  8 | sleep 0.4
```

`&` がバックグラウンド起動、`$!` は直前のプロセスID。`trap ... EXIT` はデモ途中で終了したときも停止を試みる。`sleep 0.4` は簡易的な起動待ちで、起動完了の厳密な保証ではありません。

### L9–L12：2件送信と終了処理

```text
  9 | "$PY" client.py --message 'こんにちは'
 10 | "$PY" client.py --message 'おすすめの名前を教えて'
 11 | wait "$SERVER_PID"
 12 | trap - EXIT
```

`--message` 付きで2回クライアント起動、サーバーは2件応答すると終了。`wait "$SERVER_PID"` で待ち、完了後 `trap - EXIT` でトラップを解除します。

## 第3部：このファイルを理解したか確認

1. このファイルは**何を受け取り、何を外部に返す／作用する**か説明できるか。
2. 呼び出す他ファイルの関数と、呼び出される関数を指せるか。
3. エラー時に起こる処理を追跡できるか。
4. 重要な変数の型（`str` / `bytes` / `socket` / `int` など）を区別できるか。
5. コードの一部を変更した際、テストや別ファイルに与える影響を予測できるか。

元ファイルと解説がずれていないかは、実装を修正した後に改めて確認してください。
