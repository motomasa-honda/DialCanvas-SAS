# CI 差分実行運用（48本の製造レビューは削除しない）

## 運用

従来の48本の GitHub Actions は PR 累積差分での再実行から、作業ブランチ `review/forest-guardian-phase66-idf` への `push.paths` 差分だけで自動実行する形式へ変更。各ワークフロー内のテスト本体・ERC条件・安全HOLDは不変。`workflow_dispatch` は引き続き利用可能（GitHub上でワークフローがデフォルトブランチにも登録されている場合など、GitHub規則の制約あり）。

**毎PR更新時の最低限のチェック:** `ci-scope-gate.yml` は PR の `synchronize`/open に常時起動して `check_routes.py` と `execution/preflight.py` と `tests/check_design.py` を確認する。`execution-integrity.yml` も台帳などの `execution/**` 差分がある場合は push 差分で起動する。

**特定機能:** G1のKiCad回路を変更したら該当G1ワークフローと依存する後続G1チェック、G5は該当IDFターゲットテスト、G6は木工/組立の関連チェックのみ実行される。ワークフローファイル自身を変更した場合も該当CIが起動する。

## 全48本の回帰テスト（正式タスク完了判定・構成統合・製造前）

共通 `execution/ci/full-regression.marker` の内容を変更して**作業ブランチにコミットしてpush**すると、48本すべてが `push.paths` の同じマーカーを検出して起動する。これはブランチにのみ存在する新規workflowでも実行可能で、workflow_dispatchのデフォルトブランチ依存を回避する。

実施時は本コミットのSHAについて **全48件の結果が確定してから** 合格判定。`quick-revision-integrity` も別途PASS。進捗台帳の DONE_SCOPE を更新する場合は AGENTS.md の1コミット原子性と前段preflightを守る。

初回移行コミットは48本すべての `.github/workflows/*.yml` を変更するため、**一度だけ全件が起動する**。次の通常修正から差分だけが起動する。

## 安全性と留意点

- CI件数削減は安全条件の緩和ではない。M1のeFuse EN=LOW、相出力/OE=HIGH、製造ゲート0/6、mainマージ禁止は変えない。
- 電源端子未駆動によるKiCad ERC3件、実Footprint/PCB DRC/実機HILは引き続き受入対象。
- GitHub `main` のブランチ保護設定は今回の権限から取得不能（403）。必須ステータスチェックに旧ワークフローの固定名がある場合、マージ前に保護ルールを確認し変更する必要がある。この時点でmainへのマージは行わない。
- 新しいワークフローは `push` の対象ブランチ・`paths` に自分自身と共通マーカーを含み、手動 `workflow_dispatch` を持たせる。`execution/ci/check_routes.py` が全ワークフローを照合する。

## Pushトリガーの実行経路検証

GitHub連携を介する参照更新については、pushイベントの実行を推測しない。作業ブランチの実際の差分コミットに紐づいたCI結果を取得し、PR側の軽量チェックと区別する。Pushチェックが発火しなければpush専用選択実行方式を採用せず、PR由来の選択実行を検討する。
