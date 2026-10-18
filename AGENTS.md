# Forest Guardian 作業指針

- 旧腕時計資料と Git 履歴を保持する。削除・移動・全面書き換えの前に影響を調査する。
- Phase 0 の現在要求は `docs/01-requirements/requirements.yaml` を原本とする。仕様文、未決定事項、検証表との整合を保つ。
- `FIXED`、`PROVISIONAL`、`OPEN`、`REJECTED`、`SUPERSEDED` の意味を混同しない。部品型番・価格・互換性や製作可能性を未検証のまま確定しない。
- 承認済み外観 Version 1.0 の参照画像・寸法原本は本リポジトリにない。新しい外観案を承認済みとして扱わない。
- 設計判断の変更は ADR と `docs/01-requirements/change-history.md` に記録する。旧要求は消さず状態を更新する。
- 設計文書は日本語で書く。変更後は `python3 tests/check_design.py` を実行する。

## CIと進捗台帳の変更ルール（重要）

- 48件の進捗変更は `execution/tasks.csv`、`execution/progress.json`、対応する検証コード、証拠を **1コミットとして原子的に更新する**。ファイル別コミットで途中状態をPRへ公開しない。
- 更新前に `python3 execution/preflight.py` を必ず実行し、検証が全件PASSになることを確認する。CIで初めて整合性が判明する運用は禁止。
- 旧フェーズの実績は固定証拠として保存するが、旧フェーズ専用CIに「全体の完了数は永遠に16/17」といった**増分に弱い固定値を記述しない**。旧成果の状態を現行 `tasks.csv` で確かめる。
- Draft PR #2は長期継続PRであり、`pull_request.paths` が累積差分全体に一致するため1回のPR更新で多数のCIが動く。原則、変更を一括コミットし、確認完了したHEADに対するCIを報告する。過去の失敗を黙って無視せず原因と修正コミットを記録する。
- 静的検査PASSを、実際のKiCad ERC/DRC、木工強度、モータ通電、製造ゲートの完了と混同しない。M1 eFuse EN LOW、製造/購買/通電/フラッシュ/mainマージ禁止は維持。
- 詳細は `execution/CI_CHANGE_POLICY.md` を参照。

## 差分CIと全体回帰テスト（2026-10-18）

- GitHub連携由来のpushイベントは動作確認できなかったため、正式経路は**短期feature PR → review/forest-guardian-phase66-idf**。旧48本はこのreviewブランチ宛のPR三点差分に基づく `pull_request.paths` で対象のみ実行。長期PR #2（base main）は軽量 `ci-scope-gate.yml` のみ。通常Git pushも追加で対応するが連携によるupdate_refには依存しない。
- 正式DONE_SCOPE判定、構成統合、製造前に全体回帰が必要なら `execution/ci/full-regression.marker` を変更した短期PRをreviewブランチ宛に作成し48本すべての完了を確認。
- 新規CIは必ず変更ファイルと依存パス、共通full-regression.marker、自分自身のYAMLをreviewブランチ宛 `pull_request.paths` と `push.paths` の両方に登録する。安全回路の変更は関連KiCad/ERCとEN/OE禁止不変条件を必須にする。
- mainのbranch protectionは権限から取得できないため、必須チェックの設定はマージ前に別途照合。mainへのマージ禁止は維持する。
