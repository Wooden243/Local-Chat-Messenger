# 07 | GitHubへ提出する — git init から push まで

Ubuntu / WSLで、展開したプロジェクトフォルダーに移動してから実行します。

## A. まず初回リポジトリを作る

```bash
cd ~/local-chat-messenger-3  # 実際に展開した場所に読み替える
git init
git branch -M main
git status
git add .
git status
git commit -m "Implement local chat messenger with UNIX sockets"
```

`git add .` の前に `.gitignore` を確認してください。`.venv/`、キャッシュ、ソケットファイルはコミットしません。Gitのユーザー名とメールが未設定なら `git config --global user.name 'YOUR_NAME'` / `git config --global user.email 'YOUR_EMAIL'` を設定します。

## B. GitHub CLI（gh）で新規リポジトリ作成＋push

GitHub CLIをインストール済みなら以下が便利です。`gh auth login` は初回認証が必要です。

```bash
gh auth status  # 未認証なら gh auth login
gh repo create local-chat-messenger-3 --public --source=. --remote=origin --push
```

**公開設定は課題提出要件と公開してよいコードかを確認して決めてください。** 公開不要なら `--private` に変更します。GitHub上でREADMEやLICENSEを先に追加すると履歴衝突の原因になるため、初回は空のリポジトリがおすすめです。

## C. GitHub Webで作った空リポジトリにpushする場合

GitHubで空のリポジトリを作成し、その画面に表示された実際のURLを使用します。

```bash
git remote add origin git@github.com:YOUR_USERNAME/local-chat-messenger-3.git
git push -u origin main
```

SSH認証未設定の場合はGitHub側のSSHキー登録が必要です。HTTPS URLを使う場合はGitHubのサポートする認証方法（ブラウザログイン、credential helper、トークン等）を使用します。パスワードでpushする方式ではありません。

## D. 2回目以降

```bash
git status
git add .
git commit -m "Update implementation and learning materials"
git push
```

## E. よくあるエラー

| エラー | 確認 |
|---|---|
| `fatal: not a git repository` | `git init` を行ったプロジェクト直下で実行しているか |
| `remote origin already exists` | `git remote -v` で確認。必要なら `git remote set-url origin <URL>` |
| `Permission denied (publickey)` | SSHキーとGitHubへの登録、`ssh -T git@github.com` を確認 |
| `rejected (fetch first)` | 既存リモート履歴を確認。勝手に `--force` しない |
| `nothing to commit` | 追加変更がなければコミット不要。`git status` を確認 |

## F. 提出前の確認

GitHub上で `src/`、`README.md`、`tests/`、`learning/` が見えることを確認し、Recursion指定の提出欄へURLを貼り付けます。**この教材の作成時点では、GitHubへの実際のpushは行っていません。**
