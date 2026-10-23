# ADR-0018: 3.4C用Type-C給電基板の方針更新

- 日付: 2026-10-22
- 状態: **SUPERSEDED**。特注変換器と専用source基板を使わない既製品案へ更新（[ADR-0019](0019-cots-usb-c-power-module.md)）。本書は判断履歴。
- 関連: [設計ベースラインv0.21](../docs/10-desk-redesign/design-baseline-v0.21.md)、[電源・制御](../docs/04-electronics/power-and-control.md)、[購入準備監査](../docs/02-architecture/purchase-readiness-audit-2026-10-21.md)
- 置換: ADR-0014の「TPS25810EVM-745を表示器用sourceとして据え付ける」判断と、それに依存する機械/受入条件。旧本文の9V PD等の構成もADR-0019で再評価済みであり、現行判断はADR-0019を参照。

## 背景

TIのTPS25810EVM-745 User's Guideは、EVMを研究開発評価用とし、完成品または生産システムへ直接/間接に組み込まないよう定めている。またTIの製品ページでは同EVMはTI.comで入手不可と表示される。一方、TPS25810 ICはTIがACTIVEとして掲載するUSB Type-C DFP source controllerで、5V/3A power path、CC電流広告、過電流/過熱保護を持つ。従って評価基板そのものと、ICを使った製品用回路を分ける。

## 判断

1. **TPS25810EVM-745を完成品/初号機の筐体内へ組み込まない。** EVM購入を部品表から外す。
2. 一台試作の回路候補としてTPS25810 ICを用いる専用Type-C sourceを設計する。3A広告は目標だが、実装条件としては未凍結。#2851固定5V±4%を直接入力するとTPS25810の通過損失込みでsource receptacleが4.75Vを下回り得るため、この直結案は除外する。上流変換器はPololu D36V50F6 #4092のメーカー設定変更で5.2V出力とする候補を立てるが、特注条件/価格/納期は未確認（[回路設計候補v0.1](../docs/04-electronics/tps25810-usb-c-source-circuit-candidate-v0.1.md)）。
   Pololu USB-C breakout #3411は標準CC終端がsink設定で、sourceとして使うにはCC抵抗の変更と別途source電源/保護回路が必要なため、完成sourceとしては扱わない（[メーカー説明](https://www.pololu.com/product/3411)）。
3. 3.4C側の入力はUSB TO UART Type-Cを維持する。40-pinヘッダーへの5V注入は行わない。通常使用はsource基板から給電し、書込み/デバッグ時はsourceケーブルを外してPCを接続する。
4. TPS25810は20-pin WQFN (3×4mm)のICである。専用基板の回路図、受動部品、コネクター、PCB外形/固定、実装方法、熱設計、調達費は別途確定する。評価基板の図面や大きさを専用基板の寸法に流用しない。
5. これをもって電源系の設計/受入が完了したとは扱わない。FG-048およびDR-05はOPENのまま維持し、実負荷・電圧降下・温度・短絡/過負荷・PD入力からの全負荷を実機で受入れる。

## 購入への影響

- 既製完成モジュールとしての表示USB-C sourceは未選定。ここで選んだのは専用回路のIC候補と上流変換器の見積候補であり、TPS25810 IC単体、#4092標準6V品、特注品、専用基板一式はいずれも発注指示ではない。
- EVM価格スナップショットを見積/BOMから除く。専用基板の実装見積ができるまで金額を空欄とする。
- #2851、表示器、モーター枝の配線・保護選定は別途継続する。供給元表示器の実消費電流が3A広告内に収まる証拠は受領/計測時に取得する。

## 受入条件

- TPS25810データシートの標準DFP回路に基づき、入力電圧源、回路図、PCB、部品表を作成し、5.2V公称入力候補の動作範囲・CC広告・電流制限・出力放電・故障/熱保護・配線降下を照合する。
- USB Type-C receptacle、ケーブル、基板固定とケース内サービス空間を同一座標の図面へ反映する。
- 表示器の最大輝度、無線、microSD動作時の5V電流と起動ピークを測り、5V枝全体の電流/電圧降下/温度を確認する。
- 給電の着脱、逆向き挿入、短絡/過負荷、PCデバッグ時の二重給電回避を確認する。

## 根拠資料

- TI [TPS25810EVM-745 User's Guide](https://www.ti.com/lit/ug/slvuai0a/slvuai0a.pdf)：§1.1でEVMを完成品へ組み込まない条件を記載。
- TI [TPS25810製品ページ](https://www.ti.com/product/TPS25810)：ACTIVE、Type-C source controller、5V/3A power path。
- TI [TPS25810データシート](https://www.ti.com/lit/ds/symlink/tps25810.pdf)：DFP標準回路、入力/出力、CCと保護。
- Waveshare [ESP32-P4-WIFI6-Touch-LCD-XC公式回路図](https://files.waveshare.com/wiki/ESP32-P4-WIFI6-Touch-LCD-XC/ESP32-P4-WIFI6-Touch-LCD-XC-Schematic.pdf)：USB TO UART Type-Cの5V入力回路。入手基板の改版照合は未実施。
