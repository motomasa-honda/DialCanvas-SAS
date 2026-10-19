# G4-04 — 7軸モーター／ドライバー既製品組合せ比較

Date: 2026-10-19  
Branch: `review/g4-04-cots-motor-pairing-20261019`  
Disposition: **低価格COTS組合せの設計候補を選定。部品受入・回路受入・発注承認ではない。**

## 推奨候補

7軸の独立交換構造を保ち、1軸につき市販モーター1個と市販ULN2003ドライバーボード1枚を組み合わせる。現時点の最安スクリーニング候補は **Adafruit #858 + ElectroPeak MTR-09-024**。この構成なら専用モーターも専用ドライバーPCBも作らずに済む。

価格掲載値からの部材小計は、Adafruit #858が1–9個でUS$4.95、MTR-09-024がUS$0.36なので、7軸分 **US$37.17**。送料・税・日本への実着価格を含まない単純比較値であり、見積・発注額ではない。MTR-09-024はMTR-09-004とは別基板の販売SKU。混用しない。

## 完成セットとの比較

| 構成 | 出典掲載価格 | 7軸の部材小計 | 評価 |
|---|---:|---:|---|
| Adafruit #858 + ElectroPeak MTR-09-024 | US$4.95 + US$0.36 / 軸 | US$37.17 | 現時点の低価格候補。異なるメーカーのコネクタ嵌合・ピン順・固定寸法が未検証 |
| Whadda WPI401（5Vモーター＋ULN2003基板＋ケーブルのセット） | Velleman公式 €7.90 / 個。DigiKey Marketplace表示 US$9.58 / 個 | 表示価格を各7個へ単純適用するとUS$67.06 | 部品の組合せは揃うが、比較掲載価格では高い。公式ページの個人向け直接購入不可表示があり、7個の日本国内調達と実仕様の確認が必要 |

価格は2026-10-19に確認した掲載値。通貨換算なし。輸送・税・関税・在庫変動を加えた調達総額は比較していない。WPI401の日本向け販売ページでは低価格の表示がある一方、残り1個の表示もあり、7台分の価格根拠には使わない。

## 仕様・電力のスクリーニング

### Adafruit #858

- メーカー掲載：5Vユニポーラ、516 steps/rev、減速比1:16.128、28mm径、モーター高さ20mm（軸を除く）、軸径5mm、巻線抵抗は約42Ω、保持トルク15N·mm。
- 5V / 42Ωからの単相電流概算は約119mA/軸。7軸すべてが同時に各1相を励磁すると約0.833A。抵抗値はメーカー掲載の概算値であり、測定結果ではない。
- 既存ファームウェアの1軸1相wave-driveと論理方式は合う候補。ただし実トルク、速度、発熱、脱調、寿命の受入れは未実施。

### ElectroPeak MTR-09-024

- 販売元掲載：ULN2003 DIPを使う4相ステッパードライバーボード、価格US$0.36、基板寸法35×31mm。
- 寸法と型番は販売元の製品ページ記載。メーカー図面・実装部品・コネクタ型番・ピン順の一次資料と現物証拠は未取得。
- Adafruit #858の0.1インチ5ピン端子と当該ボードのモーター端子が嵌合するとはまだ確認できない。JST XHP-5相当とも推定しない。接続は購入せずに確定できる資料が出ない限り、未確定のまま扱う。

### WPI401

- Velleman公式製品ページは5Vモーター、ULN2003基板、ケーブルを含むセットと説明し、モーター径28mm、4相、減速比1:64を掲載。
- 公式マニュアルは巻線抵抗50Ω±7%（25°C）とトルク等を掲載する一方、電圧表記・step/revと減速比の関係に製品ページとの不整合がある。ステップ数や電流、トルクを設計値として採用しない。
- メーカーのセット品として既製組合せの証拠にはなるが、現行機への選定推奨にはしない。コストが高く、正確な運転・取付・供給仕様を別途解決する必要がある。

## 現行設計への結論

**専用モーター／専用ドライバーを設計・製作せず、Adafruit #858とULN2003完成ボードを軸ごとに組み合わせる方針を進める。** 価格面からMTR-09-024を第一候補とする。7枚共通の同一改版を使い、他の6軸・歯車・P3を外さず1軸分をサービス交換するA案と両立させる。

ただし #858 と MTR-09-024 のペアはまだ受入れ済み構成ではない。確定BOM、基板レイアウト、製造図へ移す前に、次の証拠が必要：

1. モーター端子とドライバーボードのコネクタ嵌合、ピン順、VCC/GND/4相の分離を一次資料または現物で確認。
2. 既存CADにモーター28×20mm本体、軸、ボード35×31mm、コネクタ、ハーネス、A案の工具・55mmサービス包絡を統合し、干渉を検査。
3. モーターとドライバーを同時に動かした実測電流、保持・始動トルク、温度、騒音、連続動作を7軸電力予算・遮断器の保証値と照合。
4. 同一SKUを7軸分調達できる現行価格・在庫・代替品を確認。

実物未確認のためG4-04はOPEN、製造ゲートは従来どおり0/6。モーター電源ENはLOWを維持。製作・購入・通電の実施をこの設計記録で承認したことにはしない。

## Sources

- Adafruit, [Small Reduction Stepper Motor #858](https://www.adafruit.com/product/858) — 5V、速度、寸法、抵抗値、トルク、価格。
- ElectroPeak, [ULN2003 Stepper Motor Driver Board MTR-09-024](https://electropeak.com/five-wire-four-phase-uln2003stepper-motor-driver-board) — 販売SKU、基板サイズ、価格。
- Velleman / Whadda, [WPI401 official product page](https://www.velleman.eu/products/view/5-vdc-stepper-motor-with-uln2003-driver-board-wpi401/?id=459144) and [official manual](https://cdn.velleman.eu/downloads/25/prototyping/manual_wpi401.pdf) — complete kit identity and conflicting motor data.
- DigiKey Marketplace, [WPI401 listing](https://www.digikey.com/en/products/detail/velleman/WPI401/25966344) — marketplace price and seller/shipping context.
- DigiKey Japan, [Adafruit 858 listing](https://www.digikey.jp/en/products/detail/adafruit-industries-llc/858/5629414) — Japanese authorized distributor product identity.
