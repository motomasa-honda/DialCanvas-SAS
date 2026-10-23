# 背面補助電装・操作部の一台用配置

更新日：2026-10-22

状態：**公開カタログ仕様で部品、接続、取付座標を選定済み。注文・組立・通電は未実施。**

## 配置基準

外箱候補は幅270×高さ205×奥行172mm、背面カバーの内面は前面ガード内側からz=148mmです。座標は背面カバーを内側から見て中心を(0,0)、右を+X、上を+Yとします。背面機器の配置図は[背面図](rear-electronics-layout-candidate-v0.1.svg)、前後方向は[組立配置図](assembled-layout-overview-candidate-v0.1.png)を参照。

## 選定部品・取り付け

| 部品 | 一台用の位置/保持 |
|---|---|
| HUSB238 #5807 | X=-86,Y=+58mm。AdafruitガイドどおりM2.5×6mmねじ2本で絶縁キャリアへ固定 |
| DFRobot DFR0758 | 左の125×120mmサービス域。基板の外形穴を使わず、3mm PCトレイ上の幅2.5mmナイロン結束バンド2本で保持。USB-A口とDC入力は外周へ向ける |
| DFRobot DFR1015 | DFR0758と同じトレイ上。公称27×20mm。9V選択位置へ設定し、ねじ/結束バンドで保持 |
| Pololu #2851 | X=-48,Y=+58mm。メーカー穴を使い、3mm PCトレイへ樹脂スペーサーとM2.5ねじで固定 |
| DS3231 #3013 | X=+85,Y=+50mm。取付穴で二点固定し、CR1220へ背面カバーを外してアクセス |
| TMC2209 #6121 | X=+35,Y=+68mm。4穴21.59×14.48mmを使いM2ねじで絶縁キャリアへ固定。モーター端子を内側へ向ける |
| WAGO 221-415×2 / 221-505×2 | 5極コネクターを+15V分配と共通GNDに1個ずつ使用。各221-505を木製内桟へねじ止め |
| Amon 3367ヒューズホルダー×3 | 15V入力、9Vモーター、5V LEDの各枝に1個。リード線をサービス域の結束点へ固定 |
| Neutrik NAUSBC-5G-FL10 | 背面カバー中心X=-86,Y=+78mm。メーカーD型開口24×19mm、固定穴2×Ø3.2mm/31mmピッチ。2×M3×25mm貫通ねじと座金/ナイロックナット。内側一体USB-Cリード100mmをHUSB238へ接続 |
| NKK MN11SS1W01×2 | 右側板、y=+75mm、前面ガード内面からz=84/108mm。Ø6.5mm穴+キー溝。12mm壁の裏面を18×18×9.4mm座ぐりし、残り2.6mmをメーカーの最大パネル厚に合わせる |
| ALPS EC11E15244G1 + Adafruit #5527 knob | 右側板、y=+75mm,z=132mm。φ7mm軸穴。内側を18×18×9.4mm座ぐりして本体/端子の逃げを作る。#5527は黒色・外径20mm・6mm D軸用で、つまみ押下も使う |

DFR0758の外形はメーカーが寸法図を公開していないため、基板穴位置を推定して固定しません。広いPCトレイと結束バンド保持を採用し、コネクター面は露出させます。その他の基板は公開外形/取付穴と市販スペーサーを使います。

## 配線と保護

| 枝 | 接続順 |
|---|---|
| 外部PD | Anker 511 A2147 → USB-Cケーブル → Neutrik NAUSBC-5G-FL10 → HUSB238 #5807（15V/2A設定） |
| 15V幹線 | HUSB238 → Littelfuse 0297003.LXN 3Aヒューズ → WAGO 221-415(+15V) → DFR0758 / DFR1015 / #2851 |
| 表示 | DFR0758 USB-A（標準5V）→ ELECOM MPA-ACECSS03BK A-C 0.3m → 3.4C USB TO UART Type-C |
| モーター | DFR1015 9V → 0297002.LXN 2A → NKK SPST → TMC2209 VM。TMCの戻りはWAGO共通GNDへ |
| LED | #2851 5V → 0297002.LXN 2A → NKK SPST → FIT0836暖色LED 330mm。LED戻りは#2851 GNDへ |
| RTC | 3.4C GPIO28/29、3.3V/GND → DS3231 SDA/SCL/VCC/GND |
| 操作ノブ | 3.4C GPIO2/3/21、3.3V/GND → EC11E15244G1 A/B/SW/COM。GPIO内部プルアップを使用 |
| モーター制御 | 3.4C GPIO4/5/32、3.3V/GND → TMC2209 STEP/DIR/ENN/VIO/GND |
| モーター相線 | #4411の4芯を抵抗値で2相に分け、AWG22 UL1007の4線へ個別にはんだ接続し、TMC2209 1A/1B/2A/2Bへ |

配線はUL1007 AWG22の赤/黒線を各10m巻から切り出します。モーター線は色に頼らずA1/A2/B1/B2と表示します。信号線は標準2.54mmジャンパー線を使い、モーター相線とは別経路で固定します。実ルートに合わせて切るので、個別ケーブルの長さ寸法や特注ハーネスは不要です。PD入力、モーターVM、LEDには各独立ヒューズとスイッチを設けます。USB給電の二重接続を避けるため、PC書込み時は内部A-C給電線を外します。

## 一台の組立後に行う確認

1. 無通電で極性、導通、短絡、スイッチ/ヒューズ直列経路、基板固定と端子の保持を確認する。
2. 表示器、RTC、エンコーダーを起動し、表示・SD・操作・SNTP/RTCを確認する。
3. 歯車を手回しした後、低速で正逆運転し、噛み込み、滑り、異音、線との接触を確認する。
4. LED/モーターを個別と同時に動かし、PD再接続、電圧、閉箱温度を確認する。
5. 背面カバーを複数回開閉し、挟み込みや引張りがないことを確認する。

これらは完成した一台の受入であり、部品購入前の試験片・治具・個体寸法再測定ではありません。異常が起きた箇所だけ変更します。

## 参照仕様

[Waveshare 3.4C](https://docs.waveshare.com/ESP32-P4-WIFI6-Touch-LCD-XC)、[Adafruit HUSB238](https://learn.adafruit.com/case-for-husb238/assembly)、[WAGO 221-415](https://www.wago.com/global/installation-terminal-blocks-and-connectors/splicing-connector-with-levers/p/221-415)、[WAGO 221-505](https://www.wago.com/global/installation-terminal-blocks-and-connectors/mounting-carrier/p/221-505_000-004)、[NKK MN11SS1W01](https://www.nkkswitches.com/part/MN11SS1W01)、[Neutrik NAUSBC-5G](https://www.neutrik.com/en/product/nausbc-5g)、[ALPS EC11E15244G1](https://tech.alpsalpine.com/e/products/detail/EC11E15244G1/)、[Adafruit #5527 knob](https://www.adafruit.com/product/5527)。
