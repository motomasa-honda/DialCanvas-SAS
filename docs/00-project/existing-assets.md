# 既存リポジトリ調査と資産分類

調査日: 2026-10-08。開始時の `main` SHA: `ba95dbced7f8ff2f92a6c993bb6dde6f792f5938`。リモート追跡 `origin/main` と一致し、複製直後の未コミット変更はなかった。履歴は `Add files via upload` の 1 コミット、タグなし。専用ブランチ `docs/forest-guardian-phase0-v0.7` で作業する。

## 実在するもの

ルートの README、PROJECT、RS-000、MASTER_PROMPT、AI_GOVERNANCE、DEVELOPMENT_WORKFLOW、ROLES は見出しと短い説明のみ。`docs/requirements/DC-000/` の 10 文書は全て `Draft` の見出しのみ。`docs/{architecture,hardware,firmware,mobile,assets,testing}/README.md` と `adr/README.md` は格納場所の案内のみ。全追跡ファイルの本文は約 1.2 KB。詳細仕様や設計図として扱えない。

言語・フレームワーク・ライブラリ・依存定義・ビルド手順・既存テスト・製品ソースコード・ハードウェア依存コード・針描画・時刻同期/RTC・ボタン・設定保存・文字盤画像/素材は確認できなかった。DialCanvas の名称と資料用ディレクトリはあるが、実装資産の存在は確認できない。ライセンスファイルと第三者依存一覧もないため、将来のコードや画像の利用条件は要確認。追跡ファイルの簡易文字列検索では秘密情報らしい値は見つからなかったが、完全な秘密情報監査ではない。

## 分類

| 分類 | 対象 | 根拠と扱い |
| --- | --- | --- |
| REUSE | `adr/README.md`、`docs/requirements/README.md`、`docs/requirements/DC-000/` の階層 | 設計記録と要求管理の置き場としてそのまま保存できる。内容は Draft で新要求の証拠にはしない。 |
| REUSE | `docs/architecture/`、`docs/hardware/`、`docs/firmware/`、`docs/testing/`、`docs/assets/` | 既存の分類と参照先を保持できる。新しい資料との関係を README に記す。 |
| ADAPT | `README.md`、`PROJECT.md`、`RS-000_Repository_Specification.md` | プロジェクト名の説明やルート情報は継承できるが、置き時計の入口として情報が不足。今回は README のみ加筆・再構成し、他の原文は保持。 |
| ADAPT | `DEVELOPMENT_WORKFLOW.md`、`MASTER_PROMPT.md`、`AI_GOVERNANCE.md`、`ROLES.md` | 将来の運用ルールの置き場。現在は本文がほぼ空なので、具体的な運用には新しい `AGENTS.md` を追加。原文は保持。 |
| ARCHIVE | `docs/mobile/README.md` | 腕時計時代のモバイル領域。今回の第一候補は Wi-Fi Web 管理。旧参照先は維持する。 |
| REPLACE | `docs/requirements/DC-000/*.md` の `Draft` 本文を現行製品仕様として使う案 | 実要求が書かれていない。旧文書を消さず、新しい `docs/01-requirements/` に現行仕様を設ける。 |
| REPLACE | `docs/*/README.md` の配置案内を設計成果物として使う案 | 具体的な寸法・回路・検証結果がない。実資料を追加して段階的に置き換える。 |

旧腕時計機能として**維持すべき実装は現時点で特定できない**。今後、別ブランチ・別リポジトリ・ローカル媒体に実装や文字盤素材が見つかった場合は、出典と利用条件を確認してから再分類する。
