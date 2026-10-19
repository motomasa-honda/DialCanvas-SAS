# 現在の設計判断

| 項目 | 現在の扱い | 記録 |
| --- | --- | --- |
| 旧資料の配置 | 保持。新 Phase 0 資料を併置 | [ADR-0001](../../adr/0001-preserve-legacy-structure.md) |
| 歯車の噛み合い | 必須要求は置換済み | [変更履歴](../01-requirements/change-history.md) |
| 歯車駆動・保守 | 現行A案：7軸のドライバーモジュールを個別交換。歯車/P3/他6軸を外さない。旧1モーター案は履歴 | [ADR-0004](../../adr/0004-module-first-system-review.md) |
| 表示器・基板 | Waveshare 3.4C・3.4型800×800 IPSの完成基板を継続候補。改版/実機表示は未受入 | [既製品全体監査](../02-architecture/module-first-audit-2026-10-19.md) |
| 電源・照明・保持部品 | 完成モジュール/標準部材を優先。候補のまま旧回路を削除しない | [ADR-0004](../../adr/0004-module-first-system-review.md) |
| 専用製作の範囲 | 外装・装飾歯車円板・ベゼル・共通カセット/アダプター・固有ソフトが中心。安全接続は同等性レビュー後 | [全体監査](../02-architecture/module-first-audit-2026-10-19.md) |

判断を更新するときは要求台帳の状態、未決定事項、検証計画を同時に見直す。

初期Phase 0の資料と後続の実装状態を区別する。現行48項目と製造ゲートは [tasks.csv](../../execution/tasks.csv) / [progress.json](../../execution/progress.json) が原本。部品候補が存在することは、寸法・電力・安全・外観の採用合格を意味しない。
