---
name: deploy
description: "本番ブランチへのリリースPRマージ後に実行するデプロイスキル。Lint・型チェックの事前確認を行い、eas build --auto-submit で本番ビルド＆ストア提出を一括実行して結果を報告する。設定は plugin.config.json から読み込む。 / Deploy skill run after a release PR is merged to the production branch. Runs lint/type checks, then `eas build --auto-submit` to build and submit to the store. Reads settings from plugin.config.json. 使用例: /eas-flow:deploy"
hint: "本番ブランチ上で実行してください。EAS CLI にログイン済みであること（eas whoami）と、プロジェクト直下に plugin.config.json があることを確認してください。"
tools: Bash, Read
allowed-tools:
  - Read
  - Bash(python3 *)
  - Bash(cd *)
  - Bash(git branch *)
  - Bash(git status *)
  - Bash(git pull *)
  - Bash(eas whoami)
  - Bash(eas build *)
  - Bash(npm run *)
  - Bash(npx tsc *)
  - Bash(gh release view *)
---

あなたはリリースエンジニアとして以下の手順を順番に実行します。途中でエラーが発生した場合は処理を停止してユーザーに報告してください。

## ⛔ 停止・確認条件（必ず守る）

- 現在のブランチが本番ブランチ（`productionBranch`）でない・未コミットの変更がある・`eas whoami` が失敗する場合は停止する。
- デプロイ内容（バージョン・platform・profile・auto-submit）はユーザーの承認を得てから実行する。
- Lint・型チェックにエラーがある場合はビルドせず停止する。
- 各ステップでエラーが発生したら停止してユーザーに報告する。勝手にリカバリーしない。

> **前提**: このスキルはプロジェクトルート（`plugin.config.json` がある階層）を作業ディレクトリとして実行します。

## 0. 設定の読み込み

最初に設定ローダを実行し、以降の全ステップで参照する解決済み設定を取得する。

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/load-config.py"
```

出力 JSON から次を使用する。取得できない場合は停止し、`plugin.config.json` の作成を促す（`plugin.config.example.json` を参照）。

- `productionBranch`（本番ブランチ / 既定 `main`）
- `appDir`（EAS/npm コマンドを実行するアプリのルート）
- `appConfigPath`（`expo.version` を読む app.json のパス）
- `platform`（`ios` / `android` / `all`）
- `easProfile`（既定 `production`）
- `commands.lint` / `commands.typecheck`
- `storeUrl`（任意 / ステップ8で使用）

以降、`{productionBranch}` などの表記は上記の解決値に読み替える。

---

## 手順

### 1. 事前確認

プロジェクトルートで以下を実行する。

```bash
git branch --show-current
git status --porcelain
```

- 現在のブランチが `{productionBranch}` でなければ停止し「`{productionBranch}` ブランチに切り替えてから実行してください」と伝える。
- 未コミットの変更がある場合は停止し、変更内容をリストアップしてユーザーに確認を求める。

### 2. 最新コードへの同期

```bash
git pull origin {productionBranch}
```

### 3. EAS ログイン確認

```bash
cd {appDir} && eas whoami
```

- 失敗した場合は停止し「`eas login` でログインしてから実行してください」と伝える。

### 4. デプロイ対象バージョンの確認

Read ツールで `{appConfigPath}` の `expo.version` を読み取り、以下をユーザーに提示して承認を得る。

```
デプロイ対象バージョン: <expo.version>

以下の内容でデプロイを開始してよいですか？
  - platform: {platform}
  - profile: {easProfile}
  - auto-submit: 有効（ビルド完了後にストアへ自動提出）
```

### 5. Lint チェック＆型チェック

`{appDir}` で設定のコマンドを実行する。

```bash
cd {appDir} && {commands.lint} && {commands.typecheck}
```

- いずれかでエラーが発生した場合は停止し、エラー内容を報告する。

### 6. EAS ビルド＆サブミット

```bash
cd {appDir} && eas build --platform {platform} --profile {easProfile} --auto-submit --non-interactive
```

- `--non-interactive` で対話なしに実行する。
- 実行後、EAS ダッシュボードの URL をユーザーに提示する。
- ビルドは EAS サーバー上で非同期に走るため、完了を待たずに次へ進む。

### 7. 完了報告

```
✅ EAS ビルド＆サブミットを開始しました

バージョン: <expo.version>
プラットフォーム: {platform}
プロファイル: {easProfile}
auto-submit: 有効

ビルドの進捗は EAS ダッシュボードで確認してください:
<EAS ダッシュボード URL>

ビルド完了後、自動的にストアへ提出されます。
```

### 8. ストア掲載テキスト生成（任意）

直近リリースのリリースノートを取得する。

```bash
gh release view --json tagName,body
```

取得したリリースノートをもとに、ストアに貼り付ける以下2テキストを日本語で生成してユーザーに提示する。`storeUrl` が設定されていればリンクを添える。

- **プロモーション用テキスト**: 170文字以内。今回のリリースで良くなった点をユーザー目線で訴求。
- **最新情報（What's New）**: 機能改修・不具合修正・改善を、専門用語を避けて箇条書き。先頭に「Ver<バージョン> アップデート内容」の見出しを付ける。
