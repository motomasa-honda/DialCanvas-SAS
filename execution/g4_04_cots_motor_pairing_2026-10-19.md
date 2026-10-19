# G4-04 — 7軸モーター／ドライバー既製品組合せ比較

Date: 2026-10-19  
Branch: `review/g4-04-cots-motor-pairing-20261019`  
Disposition: **COTS候補の価格・電力比較まで。部品受入・回路受入・発注承認ではない。**

## 現時点の低価格候補

7軸の独立交換構造を保ち、1軸につき市販モーター1個と市販ULN2003ドライバーボード1枚を組み合わせる。現時点の低価格スクリーニング候補は **Adafruit #858 + ElectroPeak MTR-09-024**。専用モーターも専用ドライバーPCBも作らずに済む。

US掲載価格の部材小計は、Adafruit #858が1–9個でUS$4.95、MTR-09-024がUS$0.36。7軸で **US$37.17**。送料・税・日本への実着価格を含まない単純比較値であり、見積・発注額ではない。MTR-09-024はMTR-09-004とは別基板の販売SKU。混用しない。

日本のDigiKey製品ページではAdafruit #858を税込¥891、147個在庫として掲載。ドライバーは別売であり、7枚を含めた国内実着見積は未取得。

## 日本で入手できる一体セットとの比較

| 構成 | 価格・掲載在庫（2026-10-19） | 7軸分の部材小計 | 電力・調達評価 |
|---|---|---:|---|
| Adafruit #858 + ElectroPeak MTR-09-024 | US$4.95 + US$0.36 / 軸。日本のDigiKeyではモーター税込¥891 / 個 | US掲載値US$37.17（送料・税別） | 最安スクリーニング候補。異なるメーカー間のコネクタ嵌合・ピン順・固定寸法が未検証。ドライバー7枚の日本実着価格も未確定 |
| Seeed 105990072 Gear Stepper Motor Driver Pack | マルツ税込¥1,117 / 個、掲載在庫25個 | ¥7,819（税込、送料別） | モーター・ドライバー・ケーブルが同梱され、1軸単位の完成COTSセット。抵抗21Ω±7%を5Vに当てた理想計算では7軸単相で約1.67A、抵抗下限では約1.79A。既存eFuseの典型ILM 1.509Aを超えるため、現行電源構成では受入れできない。実電流・保証限界は未検証 |
| Whadda WPI401 | Velleman公式€7.90 / 個（個人向け直接購入不可の表示）。DigiKey Marketplace US$9.58 / 個 | Marketplace表示を7個へ適用するとUS$67.06 | 5Vモーター＋ULN2003基板＋ケーブルのセット。マニュアルは50Ω±7%を掲載するため理想計算電流はSeeedより低い。一方、step/rev・減速比・電圧の表記に不整合があり、価格・寸法・仕様の根拠が候補より弱い |

価格・在庫は掲載値で、変動する。通貨換算はしていない。マルツは税込3,300円以上の購入で送料無料と掲載しているため、Seeed品7個を同一注文する場合は商品価格¥7,819が該当条件を超える。調達総額の確定ではない。

Seeedのモーター巻線について、メーカーWikiの抵抗値表記は単位を省略しているが、同梱モーターのCX28BYJ48データシートの表示は5VDC・21Ω。ドライバー基板のトランジスター電圧降下で実電流は理想計算より小さくなる。しかし7軸全ての実測最大電流、ドライバー/LED負荷、eFuseの保証最小ILMが揃っていないため、Seeedセットは現行電源で承認できない。

## 仕様・電力のスクリーニング

### Adafruit #858

- メーカー掲載：5Vユニポーラ、516 steps/rev、減速比1:16.128、28mm径、モーター高さ20mm（軸を除く）、軸径5mm、巻線抵抗約42Ω、保持トルク15N·mm。
- 5V / 42Ωからの単相電流概算は約119mA/軸。7軸すべてが同時に各1相を励磁すると約0.833A。これはメーカー掲載の概算抵抗を使った理想計算で、測定値・電流上限ではない。
- 既存の `motor_current_acceptance.json` は各軸2相同時を暫定仮定している。同じ42Ω/相の理想計算では約238mA/軸、7軸で約1.67Aとなり、R_ILM=2.21kΩからのeFuse典型ILIM約1.509Aを超える。ULN2003の電圧降下はこの実電流を下げるため、これは不適合確定値ではなく、2相駆動を前提にするなら実測・保証値確認なしに電源適合と扱えないというスクリーニング結果。
- 1相wave-driveならモーター分だけの理想値は約0.833A。ただし共有5V_RAW上の3.3V buck負荷、LED/基板負荷、eFuse ILIM公差、20%余裕を足した合計が未計測なので、現状はこれも適合確定ではない。
- 既存ファームウェアの1軸1相wave-driveと論理方式は合う候補。ただし実トルク、速度、発熱、脱調、寿命の受入れは未実施。

### ElectroPeak MTR-09-024

- 販売元掲載：ULN2003 DIPを使う4相ステッパードライバーボード、価格US$0.36、基板寸法35×31mm。
- 寸法と型番は販売元製品ページの掲載値。メーカー図面・実装部品・コネクタ型番・ピン順の一次資料と現物証拠は未取得。
- Adafruit #858の0.1インチ5ピン端子と当該ボードのモーター端子が嵌合するとは確認できていない。JST XHP-5相当とも推定しない。

### Seeed 105990072

- メーカーはモーター＋ドライバー基板のセットを販売。メーカーWikiには5V、4相、1/64減速、28mmモーター径、21±7%の抵抗値、4相8ステップ、VCC/VM電源選択とIN1–IN4ピン割当て、外形図を掲載。
- マルツは型番105990072を税込¥1,117、在庫25個として掲載。7個まとめて調達できる国内候補として、他2候補より同一SKUの手配が明瞭。
- 5V / 21Ω = 約238mA/軸。7軸同時の単相理想計算は約1.67A。抵抗の下限19.53Ωを使うと約1.79A。いずれもULN2003の電圧降下を無視したスクリーニング値で、実測最大電流ではない。既存のeFuse典型ILM約1.509Aを超える計算となるため、電源設計を変えずには選定しない。

### WPI401

- Velleman公式製品ページは5Vモーター、ULN2003基板、ケーブルを含むセットと説明し、モーター径28mm、4相、減速比1:64を掲載。
- 公式マニュアルは巻線抵抗50Ω±7%（25°C）とトルク等を掲載する一方、電圧表記・step/revと減速比の関係に不整合がある。ステップ数、電流、トルクを設計確定値として使わない。
- 同一SKUを7個そろえる国内調達価格と寸法証拠が不足するため、現行機の推奨にはしない。

## 現行設計への結論

**専用モーター／専用ドライバーを作らず、既製品の組合せを軸ごとに使う方針を維持する。** Adafruit #858 + MTR-09-024は部材単価上の最安スクリーニング候補として残すが、現電源条件への適合は未成立。既存電流受入れ表の2相/軸仮定で抵抗ベースの理想値が典型ILIMを上回り、1相/軸でも共有5V_RAWの他負荷と余裕を含む合計値が未確認。Seeed 105990072も1相のモーター理想値だけで典型ILIMを上回るため現状では選定しない。したがって価格順位は「受入れ候補」の順位ではない。MTR-09-024の実ピン・コネクタ証拠と、駆動相数を固定した7軸電流検証を残す。

#858 と MTR-09-024 のペアはまだ受入れ済み構成ではない。確定BOM、基板レイアウト、製造図へ移す前に必要：

1. モーターとボードのコネクタ嵌合、ピン順、VCC/GND/4相の分離を一次資料または現物で確認。
2. 既存CADにモーター28×20mm本体、軸、ボード35×31mm、コネクタ、ハーネス、工具および55mmサービス包絡を統合し、干渉を検査。
3. 7軸同時駆動時の実測電流、保持・始動トルク、温度、騒音、連続動作を電源予算・遮断器の保証値と照合。
4. 同一SKUを7軸分調達できる現行価格・在庫・代替品と日本への実着費用を確認。

実物未確認のためG4-04はOPEN、製造ゲートは0/6。モーター電源ENはLOWを維持。この記録は製作・購入・通電の承認ではない。

## Sources

- Adafruit, [Small Reduction Stepper Motor #858](https://www.adafruit.com/product/858) — 5V、速度、寸法、抵抗、トルク、価格。
- DigiKey Japan, [Adafruit 858 listing](https://www.digikey.jp/en/products/detail/adafruit-industries-llc/858/5629414) — 日本価格、在庫、製品ID。
- ElectroPeak, [ULN2003 Stepper Motor Driver Board MTR-09-024](https://electropeak.com/five-wire-four-phase-uln2003stepper-motor-driver-board) — 販売SKU、基板サイズ、価格。
- Seeed, [105990072 product](https://www.seeedstudio.com/Gear-Stepper-Motor-Driver-Pack-p-3200.html) and [manufacturer Wiki](https://wiki.seeedstudio.com/Gear_Stepper_Motor_Driver_Pack/) — set identity, motor data, power pins, control pins, drawing.
- Marutsu, [Seeed 105990072 domestic listing](https://www.marutsu.co.jp/pc/i/1558561/) — Japan price and stock observed 2026-10-19.
- Mouser Japan, [Seeed 105990072 listing](https://www.mouser.jp/ja/ProductDetail/Seeed-Studio/105990072?qs=0lSvoLzn4L99CUdct3Gvjw%3D%3D) — exact product number and stock cross-check.
- Velleman / Whadda, [WPI401 official product page](https://www.velleman.eu/products/view/5-vdc-stepper-motor-with-uln2003-driver-board-wpi401/?id=459144) and [official manual](https://cdn.velleman.eu/downloads/25/prototyping/manual_wpi401.pdf) — bundled set and inconsistent specs.
- DigiKey Marketplace, [WPI401 listing](https://www.digikey.com/en/products/detail/velleman/WPI401/25966344) — price and shipping context.
