# 学習用フォルダー案内

これは Recursion「Local Chat Messenger (3)」の**実際の実装に対応**した学習教材です。説明用の別プログラムではありません。

## まず読む順番

1. [`00_START_HERE.md`](00_START_HERE.md) — 3分で全体像・15分で重要箇所
2. [`01_ARCHITECTURE.md`](01_ARCHITECTURE.md) — フォルダー、モジュールの依存関係
3. [`03_EXECUTION_FLOW.md`](03_EXECUTION_FLOW.md) — 1回の通信を時系列で追跡
4. [`02_KEY_CONCEPTS.md`](02_KEY_CONCEPTS.md) — API・構文を基礎から理解
5. [`code-walkthrough/`](code-walkthrough/README.md) — **コード全文＋行・ブロック単位の解説**
6. [`04_DEBUGGING.md`](04_DEBUGGING.md) — 問題が起きたとき
7. [`05_REVIEW.md`](05_REVIEW.md) — 演習と詳細解答
8. [`06_DESIGN_REVIEW.md`](06_DESIGN_REVIEW.md) — 今回の実装の限界・改善案

## 大切な読み方

最初にすべて暗記する必要はありません。`send_message()` の入力・戻り値、`run_server()` の受信・返信、`protocol.py` の文字列/バイト列変換、`try/finally` の後片付けを自分の言葉で説明できれば第一段階は完了です。次にコードを実行し、`--message` を変えるなどの小変更をしてください。

> 正確性の範囲：記述は本フォルダー作成時点の同梱ソースに対応します。課題画像の全記載事項と設計上の補足を区別しています。Fakerの応答内容は毎回変わります。
