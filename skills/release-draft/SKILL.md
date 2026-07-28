---
name: release-draft
description: "統合ブランチ→本番ブランチへのリリースPRを作成する。引数にリリースバージョン（例: 3.0.0）を必ず指定すること。app.json のバージョン（と iOS ビルド番号）を更新してコミット・プッシュし、PRとリリースノートのドラフトを生成する。設定は plugin.config.json から読み込む。 / Creates a release PR from the integration branch to the production branch. Requires a version argument (e.g. 3.0.0). Bumps app.json version (and iOS build number), commits/pushes, and drafts a PR + release notes. Reads settings from plugin.config.json. 使用例: /eas-flow:release-draft 3.0.0"
hint: "引数にリリースバージョンを必ず指定してください（例: /eas-flow:release-draft 3.0.0）。統合ブランチ上で実行してください。"
tools: Bash, Read, Edit
allowed-tools:
  - Read
  - Edit
  - Bash(python3 *)
  - Bash(cd *)
  - Bash(git branch *)
  - Bash(git status *)
  - Bash(git fetch *)
  - Bash(git log *)
  - Bash(git add *)
  - Bash(git commit *)
  - Bash(git push *)
  - Bash(eas build:list *)
  - Bash(gh pr create *)
  - Bash(gh release create *)
---

あなたはリリースエンジニアとして以下の手順を順番に実行します。途中でエラーが発生した場合は処理を停止してユーザーに報告してください。

## ⛔ 停止・確認条件（必ず守る）

- 現在のブランチが統合ブランチ（`integrationBranch`）でない、または未コミットの変更がある場合は停止する。
- バージョン更新（app.json）はユーザーの承認を得てから行う。
- リリースノートはユーザーに提示して確認を得てから GitHub Release（`--draft`）を作成する。
- エラーが発生したら停止してユーザーに報告する。勝手にリカバリーしない。

> **前提**: このスキルはプロジェクトルート（`plugin.config.json` がある階層）を作業ディレクトリとして実行します。

## 引数

`$ARGUMENTS` にリリースバージョン文字列（例: `3.0.0`）が渡されます。
引数が空の場合は「バージョンを引数に指定してください（例: /eas-flow:release-draft 3.0.0）」と伝えて処理を停止する。

## 0. 設定の読み込み

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/load-config.py"
```

出力 JSON から次を使用する。

- `repo`（`owner/repo`）
- `integrationBranch`（既定 `develop`） / `productionBranch`（既定 `main`）
- `appDir` / `appConfigPath`
- `platform` / `easProfile`
- `storeUrl`（任意）

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

### 2. バージョンの確認

`{appConfigPath}` の `expo.version` を読み取り、ユーザーに確認する。

```
現在のバージョン: <expo.version>
新バージョン: $ARGUMENTS

バージョンをこの内容で更新してよいですか？
```

承認を得てから次へ進む。

### 3. コミット一覧の取得と分類

```bash
git fetch origin
git log origin/{productionBranch}..{integrationBranch} --oneline
```

コミットをプレフィックスで分類する。プレフィックス（`feat:` 等）は除去し、PR 番号（`#NNN`）は末尾に残す。

- **機能改修リスト**: `feat:` 始まり
- **不具合修正リスト**: `fix:` 始まり
- **備考リスト**: `refactor:` / `perf:` / `chore:` 始まり

### 4. app.json の更新

#### 4-1. ビルド番号の取得（iOS のみ）

`platform` が `ios` または `all` の場合、直近の production ビルド番号を取得する。

```bash
cd {appDir} && eas build:list --platform ios --profile {easProfile} --status FINISHED --limit 1 --json --non-interactive
```

JSON の `appBuildVersion` がビルド番号（CFBundleVersion）。取得できない場合はユーザーに確認する。`platform` が `android` のみの場合はこの手順をスキップする。

#### 4-2. app.json の書き換え

Edit ツールで `{appConfigPath}` を更新する。

| フィールド             | 更新値                              |
| ---------------------- | ----------------------------------- |
| `expo.version`         | `$ARGUMENTS`                        |
| `expo.ios.buildNumber` | 4-1 で取得したビルド番号（iOSのみ） |

#### 4-3. コミット＆プッシュ

```bash
git add {appConfigPath}
git commit -m "chore: バージョンを Ver$ARGUMENTS に更新"
git push origin {integrationBranch}
```

### 5. PR の作成

`.github/pull_request_template.md` があればそれに従い、無ければ以下の本文で PR を作成する。

- **タイトル**: `release: Ver$ARGUMENTS`
- **ベースブランチ**: `{productionBranch}`
- **ヘッドブランチ**: `{integrationBranch}`

```bash
gh pr create \
  --repo {repo} \
  --base {productionBranch} \
  --head {integrationBranch} \
  --title "release: Ver$ARGUMENTS" \
  --body "$(cat <<'EOF'
## 変更内容

<ステップ3で分類したコミット一覧を箇条書きで記載（feat/fix/refactor等を含む）>

## 変更理由

- Ver$ARGUMENTS のリリース

## 動作確認方法

- {integrationBranch} ブランチでの動作確認済み

## レビュー観点

- リリース内容に漏れ・誤りがないこと
- バージョンが正しく更新されていること（Ver$ARGUMENTS）

## その他

-

---
🤖 Generated with eas-flow
EOF
)"
```

### 6. リリースノートの確認と GitHub Release ドラフトの作成

ステップ3の分類結果を、以下のフォーマットに整形する。

```markdown
# 変更一覧

- **リリース日**： YYYY年MM月DD日
<storeUrl があれば「- [ストアリンク](storeUrl)」を追加>

## 👍機能改修

### <機能改修リストの各項目> #<PR番号>

## 🐛不具合修正

### <不具合修正リストの各項目> #<PR番号>

## 🔄改善

### <備考リストの各項目> #<PR番号>
```

- 該当するコミットがないセクションは省略する。
- 整形したリリースノートをユーザーに提示し、修正の有無を確認する。

確認後、GitHub Release をドラフトで作成する。

```bash
gh release create "Ver$ARGUMENTS" \
  --repo {repo} \
  --title "Ver$ARGUMENTS" \
  --notes "<確認済みのリリースノート内容>" \
  --draft
```

- タグは `Ver$ARGUMENTS`、`--draft` で下書き（公開しない）。
- 作成後、Release の URL を記録する。

### 7. 完了前チェックリスト

- [ ] `expo.version`（iOS なら `expo.ios.buildNumber` も）を更新した
- [ ] PR がタイトル `release: Ver$ARGUMENTS`・base `{productionBranch}`・head `{integrationBranch}` で作成されている
- [ ] リリースノートをユーザーに提示して確認を得た
- [ ] GitHub Release がタグ `Ver$ARGUMENTS`・`--draft` で作成されている

### 8. 完了報告

```
✅ リリース PR と GitHub Release ドラフトを作成しました

バージョン: <旧バージョン> → $ARGUMENTS
PR URL: <PR の URL>
Release URL: <GitHub Release の URL>

--- リリースノートドラフト ---
<確認済みのリリースノート内容>
```
