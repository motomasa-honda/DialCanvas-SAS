# Forest Guardian — CI障害の是正・48件台帳の原子性

- 日付：2026-10-16
- 対象：Draft PR #2、作業枝 `review/forest-guardian-phase66-idf`
- 目的：設計完了数が増えたときに旧検証が失敗する障害、および1ファイルごとのPR更新によるCI大量起動を防ぐ

## 原因と是正事実

旧 `execution/bom_reconciled_2026-10-16/check_contract.py` はG4-02という **過去の限定成果** を検証するのに、全プロジェクトの状態を `(17,7,20,4)` と固定していた。G6-02を正しく完了扱いにすると `(18,6,20,4)` になり、設計が破綻していなくても以前の検証が赤くなる。

- 旧不合格例：[38848470808](https://github.com/motomasa-honda/DialCanvas-SAS/actions/runs/38848470808)、`check_contract.py:31` のAssertionError。
- 修正コミット：`3d323fe511665313e0b98dd33fe6bc16f6cc90c1`。G4-02の完了を現在の台帳から照合し、現在の全体完了数をテストスクリプトへ固定しない。
- 修正後の[同BOM CI 38850095410](https://github.com/motomasa-honda/DialCanvas-SAS/actions/runs/38850095410) **SUCCESS**、[進捗台帳CI 38850095503](https://github.com/motomasa-honda/DialCanvas-SAS/actions/runs/38850095503) **SUCCESS**。
- 直近100件のCI履歴に表示された失敗6件は、BOM回帰スクリプトや48件台帳の**更新途中状態**に由来。ハードウェア試験の合格宣言や破損が見つかったわけではない。履歴の失敗は消さずに残す。

## 今後の開発フロー

1. **完成判定の証拠を作り、範囲を確認する。** Gx-yy成果物をレビュー用に検証し、原本SHA/ソースを記録する。
2. 変更が必要な `tasks.csv`、`progress.json`、検証コード、報告書を作業ツリーで同時更新する。
3. `python3 execution/preflight.py` で全体台帳整合性、M1旧BOM、G6内装型紙、その他既存静的検証を**先に**通す。
4. **1つのGitコミット**で全ファイルをHEADへ反映する。GitHub APIなら `create_tree(base_tree_sha)` → `create_commit(parent_sha)` → `update_ref(expected_sha=旧HEAD, force=false)` の順に使い、変更は単一のfast-forward。
5. CIは**コミットSHAが一致する実行結果**だけを採用し、完了前にSUCCESSと書かない。赤ならログから行番号・原因を特定し、修正後のSHAと結果を提示する。
6. 統合リリースでは必要な全CIと実機ゲートを独立して照合する。設計向けPASSを製造ゲート0/6の解除に使わない。

### 現在の重要状態

- 48件の分母固定、`18 DONE_SCOPE / 6 WORKING / 20 OPEN / 4 HARDWARE_WAIT`
- 製造ゲート0/6、ソフトウェア証拠11/14
- 実機の独立安全ラッチ、eFuseのモーター動作、木部強度、加工、実配線は承認されていない
- Draft PR維持、`main`変更・製造・購買・モーター通電は禁止

この文書は運用規則であり、物理安全性や設計完成の証拠ではない。

## 2026-10-18 — PR累積差分をやめるCI選択実行

48本を `push` の変更パス+対象ブランチに変更し、PRでは常時動く軽量 `ci-scope-gate.yml` に固定。全体回帰は `execution/ci/full-regression.marker` の変更をpushし全48本を起動する。既存ジョブのテスト内容・pass/fail基準・KiCad ERC監査は変更しない。詳細は `execution/ci/README.md`。この節の変更時点で安全G1-05/06はWORKING、20/48、製造ゲート0/6。旧版に記載の18/48は2026-10-16の履歴値であり現行値ではない。GitHub branch protectionはAPI権限不足で取得できておらずmainマージ禁止継続。

## 2026-10-18 — GitHub連携経由push非発火の修正（実測）

GitHub連携の `update_ref` からpushトリガーが発火せず、軽量PRゲートのみ実行されることを実測。**push差分だけに依存する設計は不適合**。従来48本に `pull_request.branches: review/forest-guardian-phase66-idf` と同じ `paths` を追加し、短期feature PRを**長期レビュー作業ブランチへ向ける**。これでfeature PRの3-dot差分によって関連テストのみ実行。長期 Draft PR #2（base main）は軽量 `ci-scope-gate` のみ。feature PRのCI成功後にだけreviewブランチへ統合する。全体回帰は専用 `full-regression.marker` を変更したfeature PRで48本一斉に起動。`workflow_dispatch` や本来のGit pushも残す。全体回帰が未実施のまま正式DONEとしない。branch protectionの内容は読み出し不可のまま、mainへのマージ禁止。
