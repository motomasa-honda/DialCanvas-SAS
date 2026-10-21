# Forest Guardian / DialCanvas Desk Edition 作業指針

- 現行の製品方針と進捗の正本は `docs/10-desk-redesign/`、現行要求の正本は `docs/01-requirements/requirements.yaml` とする。
- 現行の駆動案は静音モーター1基で装飾歯車群を連動させる構成。7軸固定ではなく、歯車数も固定しない。28個のCADは配置候補である。
- 旧7軸要求、回路、CAD、`execution/` の台帳と証拠は履歴として保持し、新設計の完了証拠や進捗に流用しない。旧設計専用のブランチは更新しない。
- `FIXED`、`PROVISIONAL`、`OPEN`、`REJECTED`、`SUPERSEDED` を区別し、部品候補や静的CADを実機受入・製造承認として扱わない。
- 購入、加工、通電、実機への書込みは、設計作業の指示だけから許可されたものと解釈しない。
- 設計文書は日本語で書き、要求・ADR・作業一覧の状態と根拠を同期する。
- 変更後は `python3 tests/check_design.py` を実行する。ホストCコアは `cmake -S firmware/cots_clock_core -B /tmp/dialcanvas-clock-core-build`、`cmake --build /tmp/dialcanvas-clock-core-build`、`ctest --test-dir /tmp/dialcanvas-clock-core-build --output-on-failure` で確認する。
- ESP-IDF対象ビルドは `.github/workflows/desk-redesign.yml` で確認する。成功しても基板GPIO、電気安全、実表示、モーター負荷、筐体加工の合格を意味しない。
