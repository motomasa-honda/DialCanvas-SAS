# 変更履歴

## 設計基準v0.21 — Forest Guardian / DialCanvas Desk Edition

- 単一モーター、歯車数非固定の現行設計を、部品・機械包絡・ソフトウェア・電源/制御を含む統合ベースラインに整理。
- 9V/3A PD、HUSB238、Pololu #2851、TI TPS25810EVM-745の表示給電、枝ヒューズ候補、独立モーターVM遮断、ENN安全初期値、TVS候補をADR-0014へ記録。
- 作業一覧を `DesignStatus` と `ValidationStatus` に分け、候補設計の整備と実機受入を別々に追跡。
- ESP-IDF v5.5.5 / ESP32-P4のCIビルドはmainで記録済み。実基板、表示、RTC、モーター、電源、筐体の実機受入と製作リリースは未完了。
- 旧7軸ブランチと旧`execution/`台帳は参照専用。新設計へ更新/進捗証拠として流用しない。

## 履歴 — Forest Guardian Phase 0 v0.7

- 旧リポジトリを調査し、再利用・適応・保存・置換の対象を記録。
- 既存の Draft 資料を保持して、置き時計の要求台帳、未決定事項、リスク、ADR、検証計画を追加。
- 標準ライブラリだけの設計資料整合性チェックを追加。

旧設計の経緯は [要求変更履歴](docs/01-requirements/change-history.md) を参照してください。
