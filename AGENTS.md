# Forest Guardian 作業指針

- 旧腕時計資料と Git 履歴を保持する。削除・移動・全面書き換えの前に影響を調査する。
- Phase 0 の現在要求は `docs/01-requirements/requirements.yaml` を原本とする。仕様文、未決定事項、検証表との整合を保つ。
- `FIXED`、`PROVISIONAL`、`OPEN`、`REJECTED`、`SUPERSEDED` の意味を混同しない。部品型番・価格・互換性や製作可能性を未検証のまま確定しない。
- 承認済み外観 Version 1.0 の参照画像・寸法原本は本リポジトリにない。新しい外観案を承認済みとして扱わない。
- 設計判断の変更は ADR と `docs/01-requirements/change-history.md` に記録する。旧要求は消さず状態を更新する。
- 設計文書は日本語で書く。変更後は `python3 tests/check_design.py` を実行する。
