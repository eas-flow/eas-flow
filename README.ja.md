# eas-flow

> Expo/EAS のリリース・デプロイ運用を自動化する Claude Code プラグイン。

English version: [README.md](./README.md)

**ステータス:** 開発初期（`v0.1.0` 作業中）。API・構成は変更される可能性があります。

`eas-flow` は、Expo + EAS + GitHub の開発フローを回すための Claude Code スキル集です。
リポジトリ名・ディレクトリ・ブランチをハードコードする代わりに、各スキルがプロジェクトごとの
`plugin.config.json` を読み込むため、同じプラグインを任意の Expo プロジェクトで使えます。

## スキル

| スキル | ステータス | 内容 |
| --- | --- | --- |
| `deploy` | v0.1.0 | Lint・型チェック後、`eas build --auto-submit` で本番ビルド＆ストア提出 |
| `release-draft` | v0.1.0 | `app.json` のバージョン（iOSはビルド番号も）を更新・push し、リリースPRとリリースノート草稿を生成 |
| `develop-work` | 予定（v0.2.0） | イシューから統合ブランチ基点で作業ブランチを作成し、品質ゲートを通してPRを作成 |
| `doc-sync` | 予定（v0.2.0） | 実装とドキュメントの乖離を検出し、更新案を提示 |

## 前提

- [Claude Code](https://claude.com/claude-code)
- [EAS](https://docs.expo.dev/eas/) で管理された Expo プロジェクト（`eas-cli` にログイン済み）
- [GitHub CLI](https://cli.github.com)（`gh`）認証済み
- Python 3（設定ローダで使用）

## インストール

```
/plugin marketplace add eas-flow/eas-flow
/plugin install eas-flow@eas-flow
```

## 設定

プロジェクト直下に `plugin.config.json` を置きます。
[`plugin.config.example.json`](./plugin.config.example.json) を雛形にしてください。

```jsonc
{
  "repo": "owner/repo",            // 省略可。gh repo view から自動取得
  "appDir": "src/MyApp",          // npm/eas を実行するディレクトリ
  "appConfigPath": "src/MyApp/app.json",
  "integrationBranch": "develop",
  "productionBranch": "main",
  "platform": "ios",             // ios | android | all
  "easProfile": "production",
  "commands": {
    "lint": "npm run lint",
    "typecheck": "npx tsc --noEmit",
    "test": "npm run test"
  }
}
```

必須は `appDir` と `appConfigPath` のみで、他は妥当なデフォルトがあります
（[`plugin.config.schema.json`](./plugin.config.schema.json) 参照）。各スキルは開始時に
`scripts/load-config.py` を実行して設定を解決します。

## 使い方

```
# リリースPRを本番ブランチにマージした後:
/eas-flow:deploy

# 統合ブランチ上で、次のリリースを草稿:
/eas-flow:release-draft 3.0.0
```

各スキルは安全ガードを備えています。誤ったブランチでは実行せず、未コミットの変更があれば停止し、
Lint・型チェックの通過を必須とし、ビルド・バージョン更新のpush・Release作成の前にユーザー承認を求めます。

## コントリビュート

開発は `develop` 基点のフローです。イシューごとに `develop` からブランチを切り、`develop` への PR を作成し、
リリースは `develop` → `main` で切ります。詳細は
[イシュートラッカー](https://github.com/eas-flow/eas-flow/issues)を参照してください。

## ライセンス

[MIT](./LICENSE)
