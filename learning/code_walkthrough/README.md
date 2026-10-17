# 主要ファイルの全文・逐次解説

各ドキュメントには **(1) 実際のコード全文 (2) 行番号付きの抜粋 (3) 構文・処理・意図の詳細解説 (4) 理解度確認**を載せています。

| 学習順 | 詳細解説 | 対象 |
|---|---|---|
| 1 | [src__client.md](src__client.md) | `src/client.py` 送信側 |
| 2 | [src__server.md](src__server.md) | `src/server.py` 受信・返信側 |
| 3 | [src__protocol.md](src__protocol.md) | `src/protocol.py` 文字列変換・掃除 |
| 4 | [test_integration](tests__test_integration.md) | 結合テスト |
| 5 | [test_protocol](tests__test_protocol.md) | 単体テスト |
| 6 | [client.py](client.md) / [server.py](server.md) | 起動入口 |
| 7 | [setup.sh](scripts__setup.md) / [demo.sh](scripts__demo.md) | スクリプト |

※ `src/__init__.py` は空ファイルです。`src` をPythonパッケージとして使うために置いてあります。実行ロジックはありません。
