# Architecture Decision Records

ADR番号は連番です。候補・寸法図・公開資料は現物受入や製造承認とは区別し、置換された案も履歴として残します。

## 共通の履歴・旧7軸設計

- [ADR-0001: 旧構成と履歴を保存](0001-preserve-legacy-structure.md)
- [ADR-0002: 装飾歯車の初期駆動候補](0002-gear-drive-candidate.md)
- [ADR-0003: 旧G5のNVS/遠隔制御レビュー](0003-g5-05-isolated-secure-nvs-and-remote-lock.md)
- [ADR-0004: 既製品優先の旧7軸構成見直し](0004-module-first-system-review.md)（履歴）

## 単一モーター置き時計の現行検討

- [ADR-0005: 単一モーター・不規則二層歯車列](0005-cots-single-motor-layered-gears.md)
- [ADR-0006: 37歯車の寸法入り案](0006-dimensioned-one-off-37-gear-baseline.md)（ADR-0007で配置を置換）
- [ADR-0007: 左下へ寄せた28歯車配置](0007-asymmetric-28-gear-layout.md)（暫定CAD候補。個数は仕様ではない）
- [ADR-0008: 一台試作のCOTS候補](0008-one-off-cots-part-selection.md)
- [ADR-0009: 3.4C・電源・文字盤ソフト基準](0009-display-power-interface-and-dial-format.md)（#3411給電案を含む旧候補。source部はADR-0014で置換）
- [ADR-0010: 3.4C公称寸法によるCAD包絡](0010-catalog-values-as-display-cad-baseline.md)（外形・穴・厚さ・表示面位置の旧値はADR-0016で更新）
- [ADR-0011: 外付けDS3231候補](0011-external-ds3231-rtc.md)
- [ADR-0012: 保護板と28歯車の暫定CAD基準](0012-cost-first-guard-and-gear-baseline.md)
- [ADR-0013: 表示基板クリアランス用の小径継手候補](0013-smaller-coupling-board-clearance.md)
- [ADR-0014: Desk Editionの独立電源枝とモーター抑止](0014-new-power-and-motor-safety-baseline.md)
- [ADR-0015: BSS1-20C・6mm軸支持の現行機械候補](0015-bss20-axis-support-candidate.md)（ADR-0012の機械部品選択とADR-0013の4↔5mm継手候補を置換。旧Z位置はADR-0020で更新）
- [ADR-0016: Waveshare 3.4C取付図と表示すき間の更新](0016-waveshare-34c-mounting-and-clearance.md)（公開Drawing/STEPのカタログ寸法を設計基準にする。配置はADR-0020で更新）
- [ADR-0017: 回転部を覆う前面ガードの材料候補](0017-transparent-guard-material-candidate.md)（PC 3mmを初号機評価材に選定。SKU/外観/保護性能の受入前）
- [ADR-0018: 3.4C用Type-C給電基板の方針更新](0018-usb-c-source-board-replacement.md)（TPS25810EVMを筐体内候補から除外し、TPS25810搭載専用基板を設計候補化。回路/PCB/購入仕様は未完）
- [ADR-0019: 既製USB-C給電モジュールの採用](0019-cots-usb-c-power-module.md)（DFRobot DFR0758と標準15V PD入力へ更新。#4092特注とTPS25810専用基板を外す）
- [ADR-0020: 表示器を前に置く軸方向スタック](0020-display-first-axial-stack.md)（画面→歯車→モーターへ並べ直し、ケース奥行167mmを暫定候補とする）

現行要求と受入状態は[要求台帳](../docs/01-requirements/requirements.yaml)および[作業一覧](../docs/10-desk-redesign/worklist.csv)を参照してください。
