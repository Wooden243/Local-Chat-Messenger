# setup.sh — ソース全文と逐次解説

- **実装ファイル**：`scripts/setup.sh`
- **本書の目的**：このファイルを単独で読んでも、各行・関数の入力、出力、状態変化、設計意図が分かるようにする。
- **注意**：以下の全文は作成時点の実ファイルから自動取得しています。動作例のFaker結果は毎回変わります。

## 第1部：ソースコード全文（省略なし）

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
printf '\nセットアップ完了。次のコマンドで開始できます:\n'
printf '  .venv/bin/python server.py\n'
```

## 第2部：コード順の詳細解説

### L1–L3：Bashと安全な実行

```text
  1 | #!/usr/bin/env bash
  2 | set -euo pipefail
  3 | cd "$(dirname "$0")/.."
```

`#!/usr/bin/env bash` はBashで実行する宣言。`set -euo pipefail` はコマンド失敗・未定義変数・パイプライン失敗を検知しやすくする。`cd "$(dirname "$0")/.."` はスクリプトの親（プロジェクト直下）へ移動。

### L4–L5：仮想環境・依存導入

```text
  4 | python3 -m venv .venv
  5 | .venv/bin/python -m pip install -r requirements.txt
```

`python3 -m venv .venv` は分離されたPython環境を作成。`.venv/bin/python -m pip install -r requirements.txt` はそこでFakerを導入します。

### L6–L7：セットアップ完了の案内

```text
  6 | printf '\nセットアップ完了。次のコマンドで開始できます:\n'
  7 | printf '  .venv/bin/python server.py\n'
```

`printf` でサーバーの起動コマンドを表示します。

## 第3部：このファイルを理解したか確認

1. このファイルは**何を受け取り、何を外部に返す／作用する**か説明できるか。
2. 呼び出す他ファイルの関数と、呼び出される関数を指せるか。
3. エラー時に起こる処理を追跡できるか。
4. 重要な変数の型（`str` / `bytes` / `socket` / `int` など）を区別できるか。
5. コードの一部を変更した際、テストや別ファイルに与える影響を予測できるか。

元ファイルと解説がずれていないかは、実装を修正した後に改めて確認してください。
