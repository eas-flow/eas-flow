---
name: develop-work
description: "イシュー番号を引数に、最新の統合ブランチから規約準拠の作業ブランチを作成し、実装後にLint・型チェック（・テスト）を通してから統合ブランチへのPRを作成する開発着手スキル。引数が無い場合はオープンなイシューを一覧して対応対象を確認する。設定は plugin.config.json から読み込む。 / Development-start skill: given an issue number, cuts a convention-compliant work branch from the latest integration branch, implements the change, runs lint/typecheck(/test) as a quality gate, then opens a PR into the integration branch. Without an argument, lists open issues to pick from. Reads settings from plugin.config.json. 使用例: /eas-flow:develop-work 23"
hint: "引数にイシュー番号を指定してください（例: /eas-flow:develop-work 23）。統合ブランチ上・未コミット変更が無い状態で実行してください。"
tools: Bash, Read, Edit, Write, Task
allowed-tools:
  - Read
  - Edit
  - Write
  - Task
  - Bash(python3 *)
  - Bash(cd *)
  - Bash(git branch *)
  - Bash(git status *)
  - Bash(git switch *)
  - Bash(git pull *)
  - Bash(git fetch *)
  - Bash(git log *)
  - Bash(git diff *)
  - Bash(git add *)
  - Bash(git commit *)
  - Bash(git push *)
  - Bash(gh issue view *)
  - Bash(gh issue list *)
  - Bash(gh pr create *)
  - Bash(npm run *)
  - Bash(npx tsc *)
---

あなたは開発着手エンジニアとして以下の手順を順番に実行します。途中でエラーが発生した場合は処理を停止してユーザーに報告してください。

## ⛔ 停止・確認条件（必ず守る）

- 現在のブランチが統合ブランチ（`integrationBranch`）でない、または未コミットの変更がある場合は、作業ブランチを作成する前に停止する。
- 作業ブランチ（新規に切ったブランチ）以外への push は行わない。`integrationBranch` / `productionBranch` に直接 push しない。
- 品質ゲート（Lint・型チェック・任意のテスト）が全て通過するまで PR は作成しない。
- 実装方針に複数の選択肢があり判断が割れる場合は、実装前にユーザーに確認する。
- エラーが発生したら停止してユーザーに報告する。勝手にリカバリーしない。

> **前提**: このスキルはプロジェクトルート（`plugin.config.json` がある階層）を作業ディレクトリとして実行します。

## 引数

`$ARGUMENTS` にイシュー番号（例: `23`）が渡されます。

引数が空の場合は、オープンなイシュー一覧を取得してユーザーに提示し、対応対象を確認してから以降の手順に進む。

```bash
gh issue list --repo {repo} --state open
```

## 0. 設定の読み込み

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/load-config.py"
```

出力 JSON から次を使用する。

- `repo`（`owner/repo`）
- `integrationBranch`（既定 `develop`）
- `appDir` / `commands.lint` / `commands.typecheck` / `commands.test`（`test` は任意）
- `labelPrefixMap`（イシューラベル → ブランチ/コミットのプレフィックス。既定は `bug→fix` / `feature→feat` / `improvement→chore` / `docs→docs`）

以降、`{integrationBranch}` 等は解決値に読み替える。

---

## 手順

### 1. 事前確認

```bash
git branch --show-current
git status --porcelain
```

- 現在のブランチが `{integrationBranch}` でなければ停止し「`{integrationBranch}` ブランチに切り替えてから実行してください」と伝える。
- 未コミットの変更がある場合は停止し、変更内容をリストアップしてユーザーに確認を求める。

### 2. イシューの取得

```bash
gh issue view $ARGUMENTS --repo {repo} --json number,title,body,labels
```

- イシューが見つからない場合は停止してユーザーに報告する。
- イシューの `labels` を `labelPrefixMap` と突き合わせ、ブランチ/コミットのプレフィックス（例: `feat`）を決定する。一致するラベルが無い場合はユーザーに確認する。

### 3. 作業ディレクトリのルール確認（任意参照）

`.claude/rules/`（このプロジェクト固有の規約）が存在すれば読み、命名規則やアーキテクチャ上の制約など、実装時に守るべき事項を把握する。存在しなくても処理は継続する（必須ではない）。

### 4. 作業ブランチの作成

```bash
git switch {integrationBranch}
git pull origin {integrationBranch} --ff-only
git switch -c "<prefix>/#$ARGUMENTS"
```

- ブランチ名は `<prefix>/#$ARGUMENTS`（例: `feat/#23`）。

### 5. 調査の委任（explorer サブエージェント）

Task ツールで `explorer` サブエージェント（読み取り専用、独立コンテキスト）に、イシューのタイトル・本文を渡して以下を調査させる。

- 変更が必要になりそうな対象ファイル
- 参考にすべき既存の実装パターン
- 変更の影響範囲（関連するテスト・ドキュメント・設定）
- 未確定な点

返ってきた要約を踏まえて、次の実装ステップの方針を立てる。方針に複数の選択肢がある場合はユーザーに確認する。

### 6. 実装

イシューの内容と explorer サブエージェントの調査結果に基づいて実装する。

- 既存の実装パターン・命名規則に合わせる（`.claude/rules/` があればそれに従う）。
- テストが必要な変更であれば、既存のテスト配置・書き方に合わせて追加/更新する。
- 変更はイシューの範囲に留め、無関係なリファクタリングを混ぜない。

### 7. 品質ゲート

`{appDir}` で設定のコマンドを実行する。

```bash
cd {appDir} && {commands.lint} && {commands.typecheck}
```

`commands.test` が設定されていれば併せて実行する。

```bash
cd {appDir} && {commands.test}
```

- いずれかでエラーが発生した場合は停止し、エラー内容を報告する。修正後に再実行する。
- 全て通過するまで次のステップ（コミット・PR作成）へ進まない。

### 8. コミット＆プッシュ

```bash
git add -A
git commit -m "<prefix>: <変更内容の要約> #$ARGUMENTS"
git push origin "<prefix>/#$ARGUMENTS"
```

- コミット件名は `<prefix>: <要約> #$ARGUMENTS` の形式。

### 9. PR の作成

`.github/pull_request_template.md` があればそれに従い、無ければ以下の本文で PR を作成する。

- **タイトル**: `<prefix>: <変更内容の要約> #$ARGUMENTS`
- **ベースブランチ**: `{integrationBranch}`
- **ヘッドブランチ**: `<prefix>/#$ARGUMENTS`

```bash
gh pr create \
  --repo {repo} \
  --base {integrationBranch} \
  --head "<prefix>/#$ARGUMENTS" \
  --title "<prefix>: <変更内容の要約> #$ARGUMENTS" \
  --body "$(cat <<'EOF'
## 変更内容

<実装した変更を箇条書きで記載>

## 変更理由

- Closes #$ARGUMENTS

## 動作確認方法

- Lint / 型チェック（/ テスト）が通過済み

## レビュー観点

-

## 懸念点

-

---
🤖 Generated with eas-flow
EOF
)"
```

### 10. 完了報告

```
✅ #$ARGUMENTS の開発着手からPR作成まで完了しました

ブランチ: <prefix>/#$ARGUMENTS
PR URL: <PR の URL>
品質ゲート: Lint ✅ / 型チェック ✅ (/ テスト ✅)
```
