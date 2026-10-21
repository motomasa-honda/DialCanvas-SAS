# DialCanvas-SAS / Forest Guardian

このリポジトリは、旧 DialCanvas 腕時計構想の資料を保持しながら、置き時計 **Forest Guardian / DialCanvas Desk Edition** の設計を管理します。リポジトリ名と既存資料の配置は維持します。

## 現在の設計状態

- **現行設計の正本**: [単一モーター置き時計案](docs/10-desk-redesign/README.md)
- **現状と証拠区分**: [2026-10-21 状態記録](docs/10-desk-redesign/status-2026-10-21.md)
- **残作業と完了条件**: [新設計の作業一覧](docs/10-desk-redesign/worklist.csv)
- 新設計の方向は、静音モーター1基で装飾歯車群を連動させる構成。7軸固定・独立駆動は現行要求ではない。
- 新設計の文字盤・表示・制御ソースは、会話上の実装報告に含まれるが、このリポジトリには未収録。現時点で新設計の実機受入や製造リリースはない。

## 旧設計資料との関係

`docs/01-requirements/requirements.yaml` v0.8、`execution/tasks.csv`、`execution/progress.json` は旧7軸設計の要求・作業台帳である。履歴保全のため残し、新設計の完了数や7軸要件の根拠には使わない。新設計の要求台帳への移行は [作業一覧 DR-08](docs/10-desk-redesign/worklist.csv) で管理する。

旧構成の `docs/requirements/DC-000/` と `docs/{architecture,hardware,firmware,mobile,assets,testing}/` も、履歴と参照先を保つため残す。既存のPhase 0資料は内容に応じて履歴または旧設計資料として扱い、実装済み機能や新設計の証拠とはみなさない。

## 整合性確認

旧Phase 0要求台帳の文書整合性はPython 3標準ライブラリのみで確認できる。

```sh
python3 tests/check_design.py
```

この検査は旧要求台帳のリンク・ID・状態・対応表を確認する。新設計の部品性能、ファームウェア、実機動作、安全性を証明するものではない。
