---
name: doc-sync
description: "実装とドキュメントの乖離を検出し、更新案を提示するドキュメント同期スキル。plugin.config.json の docSync（対象ドキュメント / SSOTファイル）を比較範囲に沿って突き合わせる。乖離検出は読み取り専用サブエージェント doc-auditor に委任し、検出・提案までを自動、ドキュメントの実際の変更はユーザー承認後に行う。引数に比較範囲（例: main..develop）を指定できる。使用例: /eas-flow:doc-sync main..develop / Detects drift between implementation and documentation and proposes updates. Compares plugin.config.json's docSync (target docs / SSOT files) over an optional commit range. Drift detection is delegated to the read-only doc-auditor subagent; detection and proposals are automatic, but actual document edits happen only after user approval."
hint: "docSync（docs/ssot）が plugin.config.json に設定されていることを確認してください。引数は任意（例: /eas-flow:doc-sync main..develop）で、省略時は productionBranch..integrationBranch を使用します。"
tools: Bash, Read, Edit, Task
allowed-tools:
  - Read
  - Edit
  - Task
  - Bash(python3 *)
  - Bash(cd *)
  - Bash(git branch *)
  - Bash(git status *)
  - Bash(git fetch *)
  - Bash(git log *)
  - Bash(git diff *)
  - Bash(git add *)
  - Bash(git commit *)
---

あなたはドキュメント同期の担当者として以下の手順を順番に実行します。途中でエラーが発生した場合は処理を停止してユーザーに報告してください。

## ⛔ 停止・確認条件（必ず守る）

- `plugin.config.json` に `docSync` が設定されていない、または `docs` / `ssot` が空の場合は、検出を行わず停止して設定を促す（推測で対象を広げない）。
- 乖離の検出・更新案の提示までは自動で行うが、実際のドキュメント編集はユーザーの承認を得てから行う。
- 編集後のコミットはユーザーの承認を得てから行い、`integrationBranch` / `productionBranch` に直接 push しない。コミットする場合は必ず作業ブランチ上で行う（現在のブランチがどちらでもない場合のみコミット可、該当する場合は先にブランチを切るようユーザーに確認する）。
- エラーが発生したら停止してユーザーに報告する。勝手にリカバリーしない。

> **前提**: このスキルはプロジェクトルート（`plugin.config.json` がある階層）を作業ディレクトリとして実行します。

## 引数

`$ARGUMENTS` に比較範囲（例: `main..develop`、`v3.1.0..HEAD`）が渡されます。省略された場合は `{productionBranch}..{integrationBranch}` を既定値として使用する。

## 0. 設定の読み込み

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/load-config.py"
```

出力 JSON から次を使用する。

- `integrationBranch`（既定 `develop`） / `productionBranch`（既定 `main`）
- `docSync.docs`（比較対象のドキュメント一覧）
- `docSync.ssot`（単一情報源となる実装ファイル一覧）

`docSync.docs` または `docSync.ssot` が空の場合は、停止して「`plugin.config.json` の `docSync.docs` / `docSync.ssot` を設定してください」と伝える。

---

## 手順

### 1. 比較範囲の決定

`$ARGUMENTS` が指定されていればそれを比較範囲として使う。無ければ `{productionBranch}..{integrationBranch}` を使う。

```bash
git fetch origin
git log <比較範囲> --oneline
```

### 2. 乖離検出の委任（doc-auditor サブエージェント）

Task ツールで `doc-auditor` サブエージェント（読み取り専用、独立コンテキスト）に、以下を渡して乖離検出を依頼する。

- `docSync.docs`（比較対象のドキュメント一覧）
- `docSync.ssot`（SSOTとなる実装ファイル一覧）
- 比較範囲（手順1で決定したもの）

doc-auditor は各ドキュメントについて、乖離箇所・現状の記載・SSOT側の実際の値・種別（数値/設定値のズレ、手順・コマンドのズレ、リンク切れ、記載漏れ）を一覧で返す。

### 3. 検出結果の提示

doc-auditor の結果をそのままユーザーに提示する。乖離が無ければ「乖離は検出されませんでした」と報告して終了する。

### 4. 更新案の作成

検出された乖離それぞれについて、ドキュメント側の具体的な修正文案（差分イメージ）を作成し、ユーザーに提示する。

```
## 更新案

### <ドキュメントパス>
- 現状: <現在の記載>
- 修正案: <修正後の記載>
- 理由: <SSOT側の実際の値・根拠>
```

この時点ではまだファイルを編集しない。修正内容に誤りがないか、ユーザーに確認を求める。

### 5. ドキュメントの更新（承認後）

ユーザーの承認を得たら、Edit ツールで該当ドキュメントを更新する。承認されなかった項目は変更しない。

### 6. コミット（任意）

編集後、`git status` / `git diff` で変更内容を提示し、コミットするかどうかをユーザーに確認する。

- 現在のブランチが `{integrationBranch}` / `{productionBranch}` の場合は、直接コミットせず、作業ブランチ（例: `docs/#<issue>`）を切ってから改めて実行するようユーザーに提案する。
- 作業ブランチ上であれば、承認を得てコミットする。PR作成は含まない（必要であれば `develop-work` スキルの PR 作成手順を参照するようユーザーに案内する）。

### 7. 完了報告

```
✅ ドキュメント同期チェックが完了しました

比較範囲: <比較範囲>
検出された乖離: <件数>
反映した更新: <件数>（未承認/保留: <件数>）
```
