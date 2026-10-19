# G4-04 — 7軸モーター／ドライバー既製品組合せ比較

Date: 2026-10-19  
Branch: `review/g4-04-cots-motor-pairing-20261019`  
Disposition: **COTS候補の価格・電力比較まで。部品受入・回路受入・発注承認ではない。**

## 現時点の低価格候補

7軸の独立交換構造を保ち、1軸につき市販モーター1個と市販ULN2003ドライバーボード1枚を組み合わせる。これまでの候補群の中では **Adafruit #858 + ElectroPeak MTR-09-004** を低電流側の優先評価候補とする。MTR-09-004は販売元がXH-5P端子、TTL入力、40×20mmを明記し、MTR-09-024より機械・信号の情報が多い。どちらも専用モーター/専用ドライバーPCBを作らないCOTS構成だが、#858とXH-5P基板の直接嵌合は確認できないため、モジュールを加工せず既製コネクタで作る交換式アダプターハーネスを次の評価対象にする。ただし今回さらに安い国内流通品も発見したため、最安構成と電源適合候補は分けて評価する。

US掲載価格の部材小計は、Adafruit #858が1–9個でUS$4.95、MTR-09-004がUS$0.36。7軸で **US$37.17**。送料・税・日本への実着価格を含まない単純比較値であり、見積・発注額ではない。MTR-09-024はMTR-09-004とは別基板の販売SKU。混用しない。

日本のDigiKey製品ページではAdafruit #858を税込¥891、147個在庫として掲載。ドライバーは別売であり、7枚を含めた国内実着見積は未取得。

## 日本で入手できる一体セットとの比較

| 構成 | 価格・掲載在庫（2026-10-19） | 7軸分の部材小計 | 電力・調達評価 |
|---|---|---:|---|
| Adafruit #858 + ElectroPeak MTR-09-004（優先評価） | US$4.95 + US$0.36 / 軸。日本のDigiKeyではモーター税込¥891 / 個 | US掲載値US$37.17（送料・税別） | 42Ω/相の低電流候補。基板はXH-5P・TTL・40×20mmと掲載。#858の0.1インチ5端子とは直接嵌合未確認で、交換式アダプターハーネス候補。ドライバー7枚の日本実着価格も未確定 |
| Adafruit #858 + ElectroPeak MTR-09-024（代替） | US$4.95 + US$0.36 / 軸 | 同額、送料・税別 | 35×31mm。モーター端子・ピン順・VIHの掲載根拠が#004より少なく、採用優先度を下げる。
| Seeed 105990072 Gear Stepper Motor Driver Pack | マルツ税込¥1,117 / 個、掲載在庫25個 | ¥7,819（税込、送料別） | モーター・ドライバー・ケーブルが同梱され、1軸単位の完成COTSセット。抵抗21Ω±7%を5Vに当てた理想計算では7軸単相で約1.67A、抵抗下限では約1.79A。既存eFuseの典型ILM 1.509Aを超えるため、現行電源構成では受入れできない。実電流・保証限界は未検証 |
| Whadda WPI401 | Velleman公式€7.90 / 個（個人向け直接購入不可の表示）。DigiKey Marketplace US$9.58 / 個 | Marketplace表示を7個へ適用するとUS$67.06 | 5Vモーター＋ULN2003基板＋ケーブルのセット。マニュアルは50Ω±7%を掲載するため理想計算電流はSeeedより低い。一方、step/rev・減速比・電圧の表記に不整合があり、価格・寸法・仕様の根拠が候補より弱い |

価格・在庫は掲載値で、変動する。通貨換算はしていない。マルツは税込3,300円以上の購入で送料無料と掲載しているため、Seeed品7個を同一注文する場合は商品価格¥7,819が該当条件を超える。調達総額の確定ではない。

Seeedのモーター巻線について、メーカーWikiの抵抗値表記は単位を省略しているが、同梱モーターのCX28BYJ48データシートの表示は5VDC・21Ω。ドライバー基板のトランジスター電圧降下で実電流は理想計算より小さくなる。しかし7軸全ての実測最大電流、ドライバー/LED負荷、eFuseの保証最小ILMが揃っていないため、Seeedセットは現行電源で承認できない。

## さらに安価な国内流通品のスクリーニング

| 構成 | 価格・数量情報（2026-10-19閲覧） | 判断 |
|---|---|---|
| 秋月 28BYJ-48 5V（販売コード113256）+ ElectroPeak MTR-09-004 | モーター税込¥250/個、MTR-09-004 US$0.36/枚。秋月ページは在庫僅少・11月中旬入荷予定で、閲覧時の購入可能数は7軸分未満。モーター端子はXH、MTR-09-004販売ページはXH-5P・TTL入力・40×20mmを掲載 | **価格だけならさらに安いが、現行電源の候補から除外。** 秋月リンク先の28BYJ48-W01仕様書は22Ω±7%/相。5V/22Ωの抵抗ベース計算は227mA/相、7軸1相で約1.59Aとなり、eFuse典型1.509Aを超える。ドライバーの電圧降下を無視したスクリーニング値であり実測値ではない。モーターSKU・基板SKUの組合せも受入れ試験前。 |
| イーストラクト Yahoo!店 MEA0050 完成セット | 税込¥987/セット、全国送料無料。商品ページの購入上限3点 | 5Vの28BYJ-48-5Vとドライバーモジュールの一体セットで、個別基板・コネクタを探す必要がない。ただし7軸分を同一販売枠からそろえられず、相抵抗・最大電流の掲載もないため、7軸電源計算へ採用できない。 |

## 追加スクリーニング：DFRobot DFR1199一体型モーター／ドライバー

国内販売ページにDFRobot DFR1199が税込¥2,113/個、メーカー取り寄せとして掲載されている。メーカー販売ページは5V動作・内蔵A4988・STEP/DIR/5V/GNDの4ピン・42×42mmを掲示する。一方、A4988メーカーの電気特性表はモーター負荷電源VBBの動作範囲を8～35Vと規定しており、5V動作というセット販売仕様と矛盾する。掲載内容だけではモーター電源経路や回路変更が解決できず、5V_RAWモーター電源へつなぐ候補から除外する。現行の4相ロジック入力とも異なり、STEP/DIR方式へのFW・インターフェース変更が必要。7個調達時の単価だけでも税込¥14,791、現時点で納期・7個在庫も確認できないため、既製品優先のコスト・調達・電源条件を満たさない。メーカーの正式な回路／5V駆動説明が得られた場合にのみ再評価する。

## ファームウェアの励磁数と電源判定

既存の製品ファームウェア検査は、7軸の出力を **one-hot wave-drive（1軸につき論理1相）** と判定し、テストもそのパターンを検証する。一方、motor_current_acceptance.json と電源予算は物理ドライバー過渡を含む測定前の保守仮定として2相/軸を保持しているため、部品比較は両方を区別する。

Adafruit #858は約42Ω/相なので、現行1相パターンのモーター分だけなら理想値は約0.833A/7軸。eFuse典型値1.509Aの80%を使う暫定スクリーニング目標は約1.207Aであり、差の約0.374Aは**保護されたモーター枝内の仮想ヘッドルーム**である。これは共有5V_RAW上のbuck入力、表示・制御基板、LED等に使える余裕ではない。3.3V常時系はeFuseより上流の5V_RAWから給電されるため、上流5V電源はモーター枝入力電流とbuck入力電流（効率込み）、その他の5V_RAW負荷を合算して別途選定する。各負荷、5V電源SKU/保証最小容量、eFuse保証最小ILIMは未確定なので、**モーター枝の典型値ベースのスクリーニングにとどまり、電源適合判定は保留**。2相/軸の保守仮定では約1.67Aとなり典型ILIMを超える。

秋月28BYJ48-W01（22Ω）とSeeed 105990072（21Ω）は、1相/軸の理想計算でもそれぞれ約1.59A、約1.67Aとなるため、現行eFuseの典型値に対する一次スクリーニングを通らない。いずれもドライバー電圧降下を含む実測ではなく、型番・電流・電源の最終受入れを置き換えない。

## 仕様・電力のスクリーニング

### Adafruit #858

- メーカー掲載：5Vユニポーラ、516 steps/rev、減速比1:16.128、28mm径、モーター高さ20mm（軸を除く）、軸径5mm、巻線抵抗約42Ω、保持トルク15N·mm。
- 5V / 42Ωからの単相電流概算は約119mA/軸。7軸すべてが同時に各1相を励磁すると約0.833A。これはメーカー掲載の概算抵抗を使った理想計算で、測定値・電流上限ではない。
- 既存の `motor_current_acceptance.json` は各軸2相同時を暫定仮定している。同じ42Ω/相の理想計算では約238mA/軸、7軸で約1.67Aとなり、R_ILM=2.21kΩからのeFuse典型ILIM約1.509Aを超える。ULN2003の電圧降下はこの実電流を下げるため、これは不適合確定値ではなく、2相駆動を前提にするなら実測・保証値確認なしに電源適合と扱えないというスクリーニング結果。
- 1相wave-driveならモーター枝の抵抗ベース理想値は約0.833A。これはモーター枝のeFuse制限とのスクリーニングである。3.3V buckはeFuse上流の5V_RAWから給電されるため、5V_RAW供給源の容量はモーター枝電流にbuck入力・LED・制御/表示基板等の電流を加えて別途評価する。各実負荷、電源定格、eFuse保証最小値が未確認のため、現状は電源適合を確定できない。
- 既存ファームウェアの1軸1相wave-driveと論理方式は合う候補。ただし実トルク、速度、発熱、脱調、寿命の受入れは未実施。

### ElectroPeak MTR-09-004（優先評価基板）

- 販売元掲載：US$0.36、在庫あり表示。ULN2003N、4入力、4表示LED、XH-5Pモーターソケット、TTL入力、40×20mm。
- #858側はメーカーが「0.1インチ間隔の5ピンケーブル端子」とするが、端子シリーズ/ハウジングは明記しない。MTR-09-004のXH-5P（2.50mm pitch）へ直接挿せるとは仮定しない。交換式アダプターハーネスで接続する案は、モーター側の実コネクタ嵌合とピン導通、モーター共通線/各相と基板端子の対応を現物で同定するまで保留。
- 基板入力は販売元がTTL対応を掲載する一方、搭載ULN2003Nの正確なメーカー/型番と保証VIH、3.3V GPIO直結の保証条件は未確認。購入BOM/配線表にはまだ固定しない。
- 40×20mm外形は販売元値。実基板リビジョン、取付穴、部品高さ、軸とのカセット干渉は未確認。

### ElectroPeak MTR-09-024

- 販売元掲載：ULN2003 DIPを使う4相ステッパードライバーボード、価格US$0.36、基板寸法35×31mm。
- 販売元は4入力、2つのモーター電源端子、モーター用コネクタヘッダー、ON/OFFジャンパーを掲載するが、ヘッダーのシリーズ/ピッチ/キー形状と5端子のピン順は公開記載から確定できない。制御入力の3.3V VIH適合値も記載がなく、現行ロジックへの直結は未確認。
- Adafruitのモーター側資料で巻線の色グループは確認できる：橙/桃が一方の相、青/黄がもう一方、赤が共通線。これはモーター側のグループ定義で、MTR-09-024ソケットの端子順を示すものではない。現物ヘッダーの嵌合・導通を照合するまで基板側ピン割当てやアダプター配線表は作らない。
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

**専用モーター／専用ドライバーを作らず、既製品の組合せを軸ごとに使う方針を維持する。** Adafruit #858 + MTR-09-004を優先評価ペア、MTR-09-024を代替基板として比較する。現電源条件への適合は未成立。既存電流受入れ表の2相/軸仮定でモーター枝の抵抗ベース理想値がeFuse典型ILIMを上回る。1相/軸ではモーター枝の典型値ベース一次スクリーニングには入るが、eFuse保証最小ILIMと実負荷は未確認。さらにeFuse上流の5V_RAW電源は、モーター枝とbuck入力、その他の5V負荷を合算した容量確認が必要。Seeed 105990072も1相のモーター理想値だけで典型ILIMを上回るため現状では選定しない。したがって価格順位は「受入れ候補」の順位ではない。MTR-09-004の実コネクタ/端子マップ/3.3V入力保証確認、適合アダプターハーネス、駆動相数を固定した7軸電流検証を残す。

#858 と MTR-09-004 のペアはまだ受入れ済み構成ではない。確定BOM、基板レイアウト、製造図へ移す前に必要：

1. モーターとボードのコネクタ嵌合、ピン順、VCC/GND/4相の分離を一次資料または現物で確認。
2. 既存CADにモーター28×20mm本体、軸、ボード35×31mm、コネクタ、ハーネス、工具および55mmサービス包絡を統合し、干渉を検査。
3. 7軸同時駆動時の実測電流、保持・始動トルク、温度、騒音、連続動作を電源予算・遮断器の保証値と照合。
4. 同一SKUを7軸分調達できる現行価格・在庫・代替品と日本への実着費用を確認。

実物未確認のためG4-04はOPEN、製造ゲートは0/6。モーター電源ENはLOWを維持。この記録は製作・購入・通電の承認ではない。

## Sources

- Adafruit, [Small Reduction Stepper Motor #858](https://www.adafruit.com/product/858) — 5V、速度、寸法、抵抗、トルク、価格。
- DigiKey Japan, [Adafruit 858 listing](https://www.digikey.jp/en/products/detail/adafruit-industries-llc/858/5629414) — 日本価格、在庫、製品ID。
- ElectroPeak, [MTR-09-004 UL2003 4-Phase Stepper Motor Driver](https://electropeak.com/ul2003-4-phase-stepper-motor-driver) — 販売元掲載のXH-5P、TTL、40×20mm、価格/在庫表示。
- ElectroPeak, [ULN2003 Stepper Motor Driver Board MTR-09-024](https://electropeak.com/five-wire-four-phase-uln2003stepper-motor-driver-board) — 代替SKU、基板サイズ、価格。
- Akizuki, [28BYJ-48 5V](https://akizukidenshi.com/catalog/g/g113256/) and linked [28BYJ48-W01 specification](https://akizukidenshi.com/goodsaffix/28BYJ48-W01.pdf) — domestic price/availability, XH connector, 22Ω winding resistance and mechanical/electrical data.
- ElectroPeak, [MTR-09-004](https://electropeak.com/ul2003-4-phase-stepper-motor-driver) — separate driver SKU, XH-5P, TTL listing and dimensions.
- Yahoo! Shopping, [Easttract MEA0050 complete motor/driver set](https://store.shopping.yahoo.co.jp/e-struct/mea0050.html) — set contents, price, shipping and quantity limit.
- Seeed, [105990072 product](https://www.seeedstudio.com/Gear-Stepper-Motor-Driver-Pack-p-3200.html) and [manufacturer Wiki](https://wiki.seeedstudio.com/Gear_Stepper_Motor_Driver_Pack/) — set identity, motor data, power pins, control pins, drawing.
- Marutsu, [Seeed 105990072 domestic listing](https://www.marutsu.co.jp/pc/i/1558561/) — Japan price and stock observed 2026-10-19.
- Mouser Japan, [Seeed 105990072 listing](https://www.mouser.jp/ja/ProductDetail/Seeed-Studio/105990072?qs=0lSvoLzn4L99CUdct3Gvjw%3D%3D) — exact product number and stock cross-check.
- DFRobot, [DFR1199 product page](https://www.dfrobot.com/product-2979.html) — 5V/A4988/STEP-DIR and 42×42mm seller specifications. Allegro, [A4988 datasheet](https://www.allegromicro.com/-/media/files/datasheets/a4988-datasheet.pdf) — VBB operating minimum of 8V. Marutsu, [DFRobot DFR1199 Japan listing](https://www.marutsu.co.jp/pc/i/3758464/) — tax-included listing price and order/stock state observed 2026-10-19.
- Velleman / Whadda, [WPI401 official product page](https://www.velleman.eu/products/view/5-vdc-stepper-motor-with-uln2003-driver-board-wpi401/?id=459144) and [official manual](https://cdn.velleman.eu/downloads/25/prototyping/manual_wpi401.pdf) — bundled set and inconsistent specs.
- DigiKey Marketplace, [WPI401 listing](https://www.digikey.com/en/products/detail/velleman/WPI401/25966344) — price and shipping context.
