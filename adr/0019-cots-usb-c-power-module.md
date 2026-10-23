# ADR-0019: 既製USB-C給電モジュールの採用

- 日付: 2026-10-22
- 状態: **一台試作の既製品候補を選定。注文・通電・実機受入は未実施**
- 関連: [設計ベースライン](../docs/10-desk-redesign/design-baseline-v0.21.md)、[給電モジュール案](../docs/04-electronics/cots-usb-c-power-module-candidate-v0.1.md)、[ADR-0018](0018-usb-c-source-board-replacement.md)
- 置換: ADR-0018の「#4092特注5.2V変換器＋TPS25810専用PCB」。

## 背景

完成機は一台製作であり、電圧を細かく特注した変換器やsource用PCBを新規に作るより、公開定格が用途に合う市販モジュールを使う。Anker 511 A2147は15V/2A（30W）のUSB PD出力を持つ。Adafruit HUSB238 #5807は15Vを固定選択できる。DFRobot DFR0758は10.5–32V入力、Type-C出力、通常5V、最大3Aと過電流/短絡/温度保護を製品仕様に記載している。

## 判断

1. PD入力はAnker 511 A2147から**15V/2A**を要求する。HUSB238 #5807は15V/2Aに設定する。9V/3A設定は現行ベースラインから外す。
2. 表示器sourceは**DFRobot DFR0758 (SKU DFR0758)**を使う。15Vを入力し、USB-A出力からELECOM MPA-ACECSS03BK（0.3m、USB-A - USB Type-C、最大5V/3A）で3.4CのUSB TO UART Type-Cへ給電する。USB-A/Type-Cの出力電源は並列のため、USB-Aだけを使いType-C出力は未接続にする。製品仕様の標準5V・最大3Aを使う。
3. モーター枝は15Vから**DFRobot DFR1015**で9Vへ降圧する。製品の選択パッドを9Vへ設定する。TMC2209 #6121の公開モーター入力範囲5–29Vに9Vが含まれるため、既存の9Vモーター設計を維持する。#2851は15V入力から補助5Vを作る。
4. #4092標準6V品、#4092特注品、TPS25810 IC/専用基板、TPS25810EVMは現行構成へ入れない。特注問い合わせも不要。
5. 表示source枝のヒューズ、分岐、モーター出力スイッチ、SMBJ12A、配線の固定は既存候補を維持し、最終負荷・温度の受入で必要な調整をする。

## 選定範囲と受入

これは購入前の特注確認を不要にするカタログ品選定であり、未試験の適合保証ではない。DFR0758の公開ページに基板外形/取付穴寸法はないため、既存の125×120mmサービス予約域へ、寸法調整可能なキャリアで固定する。受領後に実寸を測り、ケースの恒久穴加工前に固定位置を決める。

DFR0758は急速充電プロトコルに応じて出力電圧が変わり得るため、標準USB-A出力からA-Cケーブルで接続する。初回の通電時に表示器端の電圧と起動を一度確認し、異常があればその枝を停止する。表示器の最大輝度・Wi-Fi・microSD負荷は全負荷確認の中で一緒に動かす。

15V/2Aは電源アダプターの30W上限である。DFR0758の5V/3Aは同モジュールの最大出力で、表示器の実消費電力ではない。表示器・LED・モーター同時運転時の総電力、電圧降下、閉箱温度は実機で受入れる。

## 参考一次資料

- Anker [511 Charger (Nano 3, 30W) A2147](https://www.ankerjapan.com/products/a2147)：5/9/15/20V出力プロファイル。
- Adafruit [HUSB238 #5807](https://www.adafruit.com/product/5807)：ジャンパーによる15Vと電流設定。
- DFRobot [DFR0758](https://www.dfrobot.com/product-2166.html)：10.5–32V入力、Type-C/USB出力、5V既定、最大3Aと保護。
- DFRobot [DFR1015](https://www.dfrobot.com/product-2599.html)：7.5–30V入力、選択式9V出力、9V/2.5A（25°C、追加放熱なし）、27×20mm。
- Adafruit [TMC2209 #6121](https://www.adafruit.com/product/6121)：5–29V motor supply input。
