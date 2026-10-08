# DialCanvas-SAS / Forest Guardian

このリポジトリは、旧 DialCanvas 腕時計構想の資料を保持しながら、置き時計 **Forest Guardian / DialCanvas Desk Edition** の設計を管理します。リポジトリ名と既存資料の配置は維持します。Phase 0 は設計基盤の整備段階であり、製品コード・CAD・回路図の完成を意味しません。

## 現在の状態

- 要求ベースライン: [Phase 0 v0.7](docs/01-requirements/phase0-v0.7.md)
- 要求の機械可読な原本: [要求台帳](docs/01-requirements/requirements.yaml)
- [未決定事項](docs/01-requirements/open-questions.md) / [技術リスク](docs/01-requirements/risks.md)
- [既存資産調査](docs/00-project/existing-assets.md) / [安全な移行計画](docs/00-project/migration-plan.md)
- [設計判断の順序](docs/02-architecture/priority-plan.md) / [システム境界](docs/02-architecture/system-boundaries.md) / [Phase 1 移行条件](docs/09-verification/phase1-gate.md)
- [ADR](adr/README.md) / [変更履歴](CHANGELOG.md)

## 既存資料との関係

旧構成の `docs/requirements/DC-000/` と `docs/{architecture,hardware,firmware,mobile,assets,testing}/` は履歴と参照先を保つため、そのまま残します。現在は大半が Draft または配置案内であり、実装済み機能の証拠ではありません。新しい `docs/00-project/` から `docs/09-verification/` には Phase 0 で内容のある資料だけを追加しました。`hardware/`、`firmware/`、`web/`、`dialcanvas/`、`assets/` の空ディレクトリは作りません。実体ができた段階で追加します。

## 整合性確認

Python 3 の標準ライブラリのみで実行できます。

```sh
python3 tests/check_design.py
```

対象はローカル Markdown リンク、要求 ID・状態、ADR 番号、未決定事項、要求と検証項目の対応です。部品の性能や機構の成立性を実証する検査ではありません。
