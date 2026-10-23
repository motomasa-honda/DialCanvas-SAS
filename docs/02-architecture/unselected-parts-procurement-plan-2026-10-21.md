# Forest Guardian / DialCanvas 一台試作・部品選定状況と調達候補

更新日：2026-10-22

状態：**一台用の市販部品型番と数量、ケース見積寸法/曲線図を選定済み。28位置CADを今回の一台の数量根拠にする。ケース価格と実機受入は別途残る。発注実行の記録ではない。**

購入前監査で見つかった旧DS1/5mm案の不整合は[KHK BSS1-20C・6mm軸支持案](../03-mechanical/bss20_axis_support_candidate-2026-10-22.md)へ置き換えた。初号機は完成品一台を組む方針で、独立した圧入片・保持治具・4歯車試験片を全量購入前の必須条件にしない。市販部品はカタログ仕様で選定し、実際の取付と動作は完成品の組立時に確認する。

旧DSF1は価格比較用に残し、現行候補の購入数量/寸法には使わない。BSS20候補ノートには公称寸法と28位置の数量計算例を残すが、4歯車先行購入や独立試験キットは現行方針に含めない。

本表は[設計ベースラインv0.21](../10-desk-redesign/design-baseline-v0.21.md)の部品候補です。静かな単一モーター、不規則な二層歯車、3.4型画面、microSD文字盤、USB-C給電を前提にします。旧7軸/M1部品は現行候補に含めません。

価格は調査時の税込表示を基本にし、税別表示は10%を加えた参考税込額も併記した。送料、為替、加工費、工具、予備部品は含まない。価格が表示されていても、在庫、見積、配送日、現物適合を保証しない。

## 2026-10-22 部品選定の到達点

**一台分の市販部品の型番と数量は選定済みです。** 現行28位置CADを今回の一台の数量根拠として採用します。歯車数/軸数を製品要求に固定する意味はありません。

| 区分 | 現在の判断 |
|---|---|
| 既製品の型番/数量選定済み | 表示器SKU31523×1、RTC #3013×1、ギアBSS1-20C×28、軸/ブッシュ/カラー/ワッシャー、モーター #4411×1、ドライバー #6121×1、継手×1、PD受電/電源変換、ケーブル、microSD、LED/拡散板、側面操作部、WAGO/ヒューズ/保持具。数量は現行一台構成用。 |
| 板材/ガード材を選定済み | 支持板はAS ONE 68-7869-18（透明PC 300×450×8mm）、前面ガードは光 KPAC303-1（透明PC 300×450×3mm）。公開商品仕様から型番選定済み。材料取りは一台用図面に記載。独立試験片は作らない。 |
| 電気小物を選定済み | エーモン3367×3、Littelfuse MINI 297 0297002.LXN 2A×2枝、0297003.LXN 3A×1枝。枝はPD入力3A、モーター2A、LED2A。5V補助主幹ヒューズは追加しない。 |
| カタログ型番ではなく製作するもの | 表示基板キャリア、完成支持板、前面ガード、背面電装サービス板/小型絶縁パッド、ウォールナットケース、配線ハーネス。加工輪郭は一台用CAD/見積図v0.4とハーネス表に定義。独立試験片は作らない。 |
| 物理受入が残るもの | 噛み合い、音/温度、ケース溝の保持、電装全負荷。部品選定やカタログ購入を止めず、完成品の一台で確認する。 |

1Aから2Aへの変更根拠は、Littelfuse 297 MINIの標準系列が32V・2〜30Aで、同社の小売5個箱も2Aから用意されていることです。試作時の電流が候補を超える場合は値を見直します。ここで列挙した部品モデル選定と、購入/製作/物理合格は別のゲートです。

### 現在の発注区分

| 区分 | 対象 | 次の条件 |
|---|---|---|
| 型番・一台分数量を選定済みの市販購入候補 | 下のBOMの電子部品、歯車/軸支持部品、操作部品、板材、配線小物 | 設計上の部品選定は完了。実際に注文する時点で在庫・価格・配送条件を通常確認する。完成品の物理受入は購入前条件ではない。 |
| 木工所の見積後に決める部品 | ウォールナット製P1〜P4と、見積に含める背板用木ねじ | かない製作所の見積で材等級、接合/着脱方法、価格、納期、送料を確認してから採否を決める。G1/G2のPC材はこの木工見積に含めず、下の別BOM行で調達する。 |
| 購入材料から切り出す部品 | PC支持板G1×2、前面ガードG2×1、表示基板キャリア、配線ハーネス | 材料型番と切出し寸法は選定済み。製作は本体用材料から行い、独立試験片は作らない。 |
| 完成品を組んだ後に受け入れる項目 | 噛み合い、表示/SD/RTC、配線、全負荷、温度、保護動作、ケース整備性 | 実機がないと確認できないため、購入前の設計残件には数えない。結果は受入記録へ残す。 |
| 製作リリース | 木工加工開始・完成品の製作承認 | HOLD。見積確認、部品と図面の最終整合、完成品受入の後に別途判断する。 |

## 1. 購入候補BOM

| 分類 | 部品・型番 | 数量/買い方 | 価格（参考） | 購入先 | 選定状態・残作業 |
|---|---|---:|---:|---|---|
| 表示・制御 | Waveshare ESP32-P4-WIFI6-Touch-LCD-3.4C / SKU31523、3.4型円形IPS 800×800 | 1（技術サンプル候補） | 旧価格スナップショット。見積/在庫未確認 | [Waveshare](https://www.waveshare.com/esp32-p4-wifi6-touch-lcd-3.4c.htm?sku=31523)・[The Pi Hut / WAV-31523](https://thepihut.com/products/esp32-p4-3-4-round-touch-display-dev-board-800x800)・[SpotPear](https://spotpear.com/shop/ESP32-P4-3.4-inch-Round-LCD-Display-TouchScreen-WIFI6/ESP32-P4-WIFI6-Touch-LCD-3.4C.html)・[RLX Components / WS-31523](https://rlx.sk/en/esp32-p4/10469-esp32-p4-34-round-touch-display-devboard-800800-dual-microphones-support-wi-fi-6bt5-le-ws-31523.html) | 型番選定済み。技術サンプルはWaveshare ESP32-P4-WIFI6-Touch-LCD-3.4C / SKU31523を1台とする。公式Drawingの前面Ø115mm、LCD有効Ø87.60mm、STEP包絡15.50mm、外周4×M4穴/75×78.5mmを設計基準にする。改版シルクやポート操作は受領後、キャリア/ケースの恒久加工前に確認し、小さな差は調整可能なキャリア側で吸収する。公開値の販売元照会は不要。販売元、在庫、日本配送、返品条件は注文時の通常確認。|
| 表示基板保持 | KPAC303-1透明PC 3mmの4本腕キャリア。基板側M4×4、支持板A側M3×4 | 前面ガード材の余りから1個切出し | 前面ガード用PC材と共用 | なし | M4×8ねじ/2mm POM絶縁スペーサ、M3×25ねじ/7mm支持スペーサ・座金・ナット各4組。個体改版照合は不要。組立時に問題が出た場合はキャリア側を調整。|
| 文字盤媒体 | KIOXIA microSDHC 32GB Class 10/UHS-I U1 | 1 | ¥2,390 税込 | [ヨドバシ](https://www.yodobashi.com/product/100000001006382817/) | 800×800 JPEGをPCからコピーする用途。FAT32で初期化し、本体で読取・破損復帰を確認。|
| 外付けRTC | Adafruit DS3231 Precision RTC Breakout #3013 | 1 | **約¥3,150 税込** | [DigiKey Japan](https://www.digikey.jp/ja/products/detail/adafruit-industries-llc/3013/5875808) | I²C 0x68。3.3V給電候補。CR1220はこのモジュールのホルダーへ装着し、3.4CのRTC端子には接続しない。回路・I2Cピン・保持動作は実機確認前。|
| RTCバックアップ電池 | Maxell CR1220.1BS | 1 | **約¥220 税込** | [ヨドバシ（CR1220一覧）](https://www.yodobashi.com/category/21484/53821/53827/) | DS3231モジュール自身の電池ホルダー用。3.4C基板のRTC電池端子には一次電池を絶対に接続しない。電池は消耗品。|
| 平歯車 | KHK BSS1-20C、M1、20T、6mm AH7穴、M4×4止めねじ1本付属 | 28個（今回の一台のCAD数量） | ¥1,868/個、表示合計 **¥52,304** | [MonotaRO](https://www.monotaro.com/p/8339/7215/)・[KHK寸法表](https://khkgears.net/pdf/bss.pdf) | 今回の一台の構成数量として決定。製品要求/量産数ではない。カタログ穴と付属ねじを使い、独立保持治具は作らない。|
| 回転ブッシュ | OILES #80 80B-0608、内径6×外径8×長さ8mm | 28個 | ¥51/個、表示合計 **¥1,428** | [MonotaRO](https://www.monotaro.com/p/0045/9313/)・[OILES仕様](https://www.oilesglobal.com/en/files/bearing34.pdf) | 6mm h7軸/Ø8 H7ハウジング穴。完成支持板へ組み、個別圧入試験片は作らない。|
| 単軸ピン | 大阪魂 SUS303 B種h7平行ピン 6×30mm、3本入 | 26本使用、9袋（27本） | ¥493/袋、合計 **¥4,437** | [MonotaRO](https://www.monotaro.com/p/4215/6807/) | 今回の一台で26本を使用し、1本予備。|
| 共通軸 | 大阪魂 SUS303 B種h7平行ピン 6×65mm、2本入 | 1本使用、1袋 | **¥648** | [MonotaRO](https://www.monotaro.com/p/4215/6886/) | A00/B00共通軸z=26–91mmに選定済み。1本予備。|
| 軸カラー | KANA KSC0605、ID6×OD12×幅5mm、M3止めねじ | 26個 | ¥208/個、合計 **¥5,408** | [MonotaRO](https://www.monotaro.com/p/1029/5117/) | 共通軸には継手を使う。各単軸へ1個。|
| スラストワッシャー | 廣杉計器 0612-10、POM、ID6.3×OD12×t1mm、12枚入 | 54枚使用、5袋（60枚） | ¥615/袋、合計 **¥3,075** | [MonotaRO](https://www.monotaro.com/p/4213/5143/) | 今回の軸方向スタックに合わせた数量。6枚予備。|
| ステッパー | Adafruit NEMA-8 #4411、4mm軸 | 1 | 税別¥3,265、税込換算 **¥3,592** | [DigiKey](https://www.digikey.jp/ja/products/detail/adafruit-industries-llc/4411/11497509) | 200 step/rev、0.6A/相の候補。保持トルク・始動余裕・温度・負荷音は実機受入。|
| モータードライバー | Adafruit TMC2209 breakout #6121 | 1 | 税別¥1,465、税込換算 **¥1,612** | [DigiKey](https://www.digikey.jp/ja/products/detail/adafruit-industries-llc/6121/25981358) | MS1/MS2開放で1/8、SPRD開放でStealthChop、EN HIGHで出力禁止。約0.3A RMSを初期評価点とするが、実電流調整と静音合格は未完。|
| モーターVM TVS | Littelfuse SMBJ12A、unidirectional | 1 | 参考価格は調達時確認 | [Littelfuse](https://www.littelfuse.com/ja-jp/products/overvoltage-protection/tvs-diodes/surface-mount/smbj/smbj12a) | VM/GND近傍へ置く候補。VRWM=12V、最大クランプ19.9V。回生過渡の波形/エネルギーは未検証。|
| ENN/STEP安全抵抗 | 汎用軸型スルーホール抵抗、10kΩ、0.25W以上、±5%以下 | 2本 | 一般受動部品。メーカー/販売店の固定指定なし | 電子部品店等 | 1本をENN→VIO/3.3Vのpull-up、1本をSTEP→GNDのpulldownに使用。抵抗値・数量・実装形状を選定済み。基板内蔵プルと起動動作は完成品受入で確認。|
| 軸継手 | NBK MJT-14-RD-4-6、4mm↔6mm、外径14×全長22mm、ハブ長7mm | 1 | **¥2,167税込参考** | [NBK仕様](https://www.nbk1560.com/products/coupling/couplicon/jaw_type/MJT-RD/MJT-14-RD/MJT-14-RD-4-6/) | 6mm共通軸へ7mm挿入。モーター軸突出、後壁、実挿入深さ、止めねじ保持は現物確認。価格/在庫は注文前に再確認。|
| USB-C PDアダプター | Anker 511 Charger (Nano 3, 30W) A2147 | 1 | **¥2,790 税込** | [Anker Japan](https://www.ankerjapan.com/products/a2147) | 15V/2A出力（30W）を使用。全負荷時のPD契約、電圧降下、温度は完成品で確認する。|
| USB-Cケーブル | ELECOM MPA-CC10PNBK、C-C、1m、PD 60W | 1 | **¥1,720 税込** | [ELECOM](https://www.elecom.co.jp/products/MPA-CC10PNBK.html) | 60W表示は本システムが60Wを得る意味ではない。ケーブル経由で15V/2A契約を使う。|
| PD受電 | Adafruit HUSB238 #5807 搭載基板（Switch Science ADA-5807） | 1 | **¥1,265 税込** | [Switch Science](https://www.switch-science.com/products/9296) | 15V/2Aへ設定する。出荷初期値は5V/1Aなのでジャンパーを設定。|
| 表示5V変換 | DFRobot DFR0758、10.5–32V入力、USB-A/Type-C出力、標準5V/最大3A | 1 | **US$6.50**（確認時表示） | [DFRobot](https://www.dfrobot.com/product-2166.html) | USB-A出力のみ使用し、ELECOM MPA-ACECSS03BKで3.4Cへ接続。Type-C出力は並列なので未使用。基板外形は非公表のため予約域内へ調整式キャリアで固定。|
| モーター9V変換 | DFRobot DFR1015、15V入力、選択式9V出力 | 1 | **US$5.30**（確認時表示） | [DFRobot](https://www.dfrobot.com/product-2599.html) | 9V/2.5A（25°C、追加放熱なし）、基板27×20mm。受領後に9V設定を確認し、完成品のモーター負荷で温度を見る。|
| 補助5V変換 | Pololu D24V50F5 #2851、入力6–38V、5V出力 | 1 | 税別¥5,136、税込換算 **¥5,650** | [DigiKey](https://www.digikey.jp/ja/products/detail/pololu/2851/10451177)・[Pololu仕様](https://www.pololu.com/product/2851) | 15V入力でLED等の補助負荷へ供給。5Aは部品仕様であり、閉箱連続出力能力やシステム容量の保証ではない。表示器はDFR0758から給電する。|
| 5V出力端子 | Pololu #2494、0.1インチ/2.54mmピッチ5極ねじ端子台（2個入り） | #2851に1個使用、1個予備 | **US$4.37** | [Pololu](https://www.pololu.com/product/2494) | 26–18AWG、定格6A。#2851の5端子も0.1インチピッチなので選定可能。横出し本体の逃げは完成品で確認し、干渉時は#2851付属のピンヘッダーへAWG22線を接続する。|
| #2851固定金物 | M2×12mmなべ小ねじ×2、M2ナット×2、長さ3mmのナイロンスペーサー×2 | 1組 | 調達時確認 | 一般金物店 | Pololu #2851のメーカー取付穴は#2/M2ねじ用。3mm PC絶縁パッド上で固定する。|
| 小型基板固定金物 | M2.5機械ねじ×8、M2.5ナット×8 | HUSB238 #5807×2、DS3231 #3013×2、TMC2209 #6121×4 | 調達時確認 | 一般金物店 | Adafruit各取付例はM2.5×6mmねじを使用。本機はM2.5を標準金物の選択として採用し、公開例の長さは転用しない。TMC2209の取付例は2本だが、本機は基板の4穴すべてを使う。基板穴の座標/径は公開寸法として扱わず、実基板からパッドへ写す。ねじ長さは3mm PCパッド/基板/ナットの実スタックに合わせる。|
| 表示基板給電用専用PCB/特注変換器 | #4092特注5.2V変換器、TPS25810専用source PCB | 0 | **現行案では不使用** | — | [ADR-0019](../../adr/0019-cots-usb-c-power-module.md)で市販DFRobot DFR0758へ置換。特注見積・専用PCB設計・EVM購入は不要。|
| 表示基板内部USB給電ケーブル | ELECOM MPA-ACECSS03BK、USB-A - USB Type-C、0.3m、最大5V/3A | 1 | **¥1,144税込**（公式表示） | [ELECOM](https://www.elecom.co.jp/products/MPA-ACECSS03BK.html) | DFR0758 USB-A出力から3.4C USB TO UART入力へ給電。書込み/デバッグ時は内部給電ケーブルを外し、PCを接続。|
| 暖色LED | DFRobot FIT0836、5V、暖色、60LED/m、1m品 | 1本から約330mm使用 | 税別¥982、税込換算 **¥1,080** | [DigiKey](https://www.digikey.jp/en/products/detail/dfrobot/FIT0836/15283059)・[DFRobot仕様](https://www.dfrobot.com/product-2398.html) | 1m上限4Wから330mmは最大約1.32W/0.264Aの試算。調査時DigiKey在庫3、標準納期表示9週。切断長・拡散材・木部温度を確認。|
| LED拡散板 | 光 A032-2US、乳白半透明アクリル、2mm、160×180mm | 1枚 | **¥472 税込** | [MonotaRO](https://www.monotaro.com/g/00025130/) | 既製板を小片に切り出す候補。安価で扱いやすいが可燃性のため、LEDから距離をとり、閉箱連続点灯で板・木部温度を測ってから配置する。光量低下と点光源の消え方も確認。|
| ヒューズホルダー | エーモン 3367、MINI平型、電線約9cm | 3個（入力・モーター・LED枝） | ¥549/個、**¥1,647** | [MonotaRO](https://www.monotaro.com/g/05234920/) | Littelfuse MINI 297系列用。15V入力、9Vモーター、5V LEDの3枝へ各1個。|
| ヒューズ素子 | Littelfuse MINI 297、0297002.LXN (2A) / 0297003.LXN (3A) | MIN2×1箱、MIN3×1箱。使用は2A×2、3A×1 | 調達時確認 | [Littelfuse MINI aftermarket](https://www.littelfuse.com/products/fuses-overcurrent-protection/fuses/automotive-aftermarket-products-fuses/blade-fuses-shunts-automotive-aftermarket/mini)・[297公式データシート](https://www.littelfuse.com/assetdocs/littelfuse-datasheet-297-mini32v?assetguid=42c9dd21-a88e-4328-8e67-2f832444faf1) | 3枝構成として数量選定済み。5V補助主幹の4Aヒューズは使わない。余りは予備。|
| 配線 | UL1007 AWG22、赤/黒、各10m | 各1ロール | ¥956/巻、**¥1,912** | [赤](https://www.monotaro.com/p/6242/6946/)・[黒](https://www.monotaro.com/p/6242/6928/) | 電源枝とモーター延長線に使う。モーターは赤/黒各2本をA1/A2/B1/B2として両端表示し、#4411リードへ個別にはんだ接続。22AWGは#6121の公開26–20AWG端子範囲内。|
| モーター接続部の絶縁 | TRUSCO TRPW6.4-2.0-10、黒色・接着剤付きポリオレフィン熱収縮チューブ、3:1、収縮前Ø6.4mm/収縮後Ø2.0mm、120mm×10本 | 1セット | ¥2,418 税込（2026-10-22表示） | [MonotaRO](https://www.monotaro.com/p/5725/9536/) | #4411-AWG22の4接続を個別に約25mmずつ覆う。必要量100mmに対して1セットで足りる。掲載価格はスナップショットで購入実行ではない。|
| 電源分岐端子 | WAGO 221-415 5極レバー端子 + 221-505 取付台 | 2組（+15V分配/GND共通） | 調達時確認 | [221-415](https://www.wago.com/global/installation-terminal-blocks-and-connectors/splicing-connector-with-levers/p/221-415)・[221-505](https://www.wago.com/global/installation-terminal-blocks-and-connectors/mounting-carrier/p/221-505_000-004) | 1組35×52.8mmの配置域を確保し、2組を100×120mmサービス域内で横並びにする。各取付台2点、合計4点をメーカー図から使用。M3機械ねじ・座金・ナットを使い、穴位置はキャリア現物から板へ写す。ねじ長さは3mm PC板を含む実スタックで選ぶ。[221-505資料](https://media.distrelec.com/Web/Downloads/_t/ds/221-505_eng_tds.pdf)にM3機械ねじ用開口の記載あり。|
| WAGO取付台固定金物 | M3機械ねじ×4、M3平座金×4、M3ナット×4 | 221-505各2点 | 調達時確認 | 一般金物店 | 標準長は3mm PCサービス板・座金・取付台・ナットの実スタックに合わせて選ぶ。穴位置は現物から板へ転記し、穴径・座標は指定しない。|
| ロータリーエンコーダー | ALPS Alpine EC11E15244G1、押し込み付き、15 pulse/30 detent | 1 | 税別¥273、税込換算 **¥300** | [フルタカパーツ](https://www.furutaka-netsel.co.jp/maker/alps/ec11) | 回転で文字盤を移動、短押しで選択、長押しで歯車停止/再開。右側面z=132mm。|
| エンコーダーノブ | Adafruit #5527、黒、外径20mm、6mm D軸用 | 1 | 参考価格は調達時確認 | [Adafruit](https://www.adafruit.com/product/5527) | EC11E15244G1の6mm D軸に組合せ。|
| 独立スイッチ | NKK MN11SS1W01、SPST ON/OFF | 2 | ¥1,307/個、**¥2,614** | [DigiKey](https://www.digikey.jp/ja/products/detail/nkk-switches/MN11SS1W01/20840209) | モーター枝と照明枝に各1個。6.5mmパネル穴候補。モーター側は分岐2Aヒューズ候補の後段でTMC2209 VMを直接遮断。旧M1 eFuseを使わない。定格と実回路を照合。|
| 前後支持板材 | AS ONE 68-7869-18 透明PC 300×450×8mm。252×187mmを2枚切出し | 1枚 | ¥11,180税別/枚（価格スナップショット） | [AXEL / AS ONE](https://axel.as-1.co.jp/asone/d/68-7869-18/) | 一枚の規格板から二枚を材料取り。独立試験板/圧入片は作らない。|
| 前面ガード | 光 KPAC303-1、透明PC 300×450×3mm | 1枚 | **¥1,750 税込**（調査時表示） | [ヨドバシ](https://www.yodobashi.com/product/100000001001981779/)・[AS ONE仕様](https://axel.as-1.co.jp/asone/d/61-2121-64/) | ガード270×205×3と表示キャリアを同一板から切出す一台用材料。曲線開口輪郭はケース見積図A01/A02 v0.4に座標指定済み。|
| 背面電装キャリア材 | 光 KPAC303-1、透明PC 300×450×3mm | 前面ガード材とは別に1枚 | **¥1,750 税込**（調査時表示） | [ヨドバシ](https://www.yodobashi.com/product/100000001001981779/)・[AS ONE仕様](https://axel.as-1.co.jp/asone/d/61-2121-64/) | 230×120×3mmのサービス板1枚と、HUSB238/#2851/DS3231/TMC2209用の小型絶縁パッド4枚を切り出す。サービス板のP4固定穴はØ3.5を4か所（板中心X=±105,Y=±50mm）。WAGO 221-505、DFR0758/1015、ヒューズリードを保持。DFR0758の結束スロットと部品ごとの穴は、実部品を置いて加工する。|
| サービス板固定具 | 木ねじ3.1×12mm、なべ頭×4 + M3大径平座金×4 | 1セット | 調達時確認 | 一般金物店 | 3mm PC板を12mm厚P4背板の内側へ固定する標準金物の選択。名目の木部への入り代は約9mm。P4側の穴は見積図v0.4で指定せず、組立時に実際のサービス板から位置を転記し、P4材と選んだ木ねじに合わせて下穴を決める。|
| 小型基板パッド固定具 | 木ねじ3.1×12mm×8 + M3大径平座金×8 | 4パッド各2本 | 調達時確認 | 一般金物店 | 3mm PC絶縁パッドをP4内面へ固定する一台用標準金物。P4の追加穴はケース見積図へ含めず、部品到着後に位置を合わせて通常組立で開ける。ねじ位置・下穴径は指定せず、実物と木部に合わせる。|
| 結束バンド | ナイロン、幅2.5mm×長さ150mm | 20本程度 | 調達時確認 | 一般電材店 | DFR0758/DFR1015、ヒューズリード、サービス板上の配線固定用。余りは予備。|
| ウォールナットケース木製キット | P1無垢枠1 (270×205×9); P2突板合板2 (205×148×12); P3突板合板2 (246×148×12); P4着脱背板1 (270×205×12) | 1式 | かない製作所へ見積予定 | [A01/A02 v0.4](../03-mechanical/walnut_case_candidate-2026-10-22.md) | 外寸270×205×172/内寸246×181×148。P1波形下辺、9×4溝、操作/USB口を指定。P4の8本のケース留めねじ穴は側/上下壁の中心へ合わせる。背面サービス板と小型基板パッド用のP4穴は先加工せず、実部品を使う通常組立時に位置転記/下穴加工する。自然色・艶消しクリア。木材・加工・送料を見積。透明PC支持板G1と前面ガードG2は別行で購入し、この見積には含めない。|
| ケース留め具 | 背面板用 3.1×25mm木ねじ8本（製作先の適合品） | 木製キットに含める見積項目 | 見積対象 | かない製作所 | P4の8穴に合わせたねじを木製キットに含める費用を確認する。キャリア固定ねじ等は別途の標準金物を使う。|



## 2. 価格のまとめ

前版の概算 **¥73,203 + US$73.31** はPololu #3411を含み、新しいType-C source、TVS、ENN/STEP抵抗、枝ヒューズ候補を反映していないため、v0.21総額としては無効です。上表の価格は調査時の参考値で、税、為替、送料、加工費、工具、在庫を含めた購入総額ではありません。全品の価格が同じ調査日に取得できていないため、新しい総額は算出していません。

### 過去の比較案：一部真鍮歯車の混載（現行候補ではない）

以下は2026-10-21以前に作った比較履歴です。2026-10-22時点の現行候補はBSS1-20C 1型番の軸支持案で、下表の混載案は数量・軸径・穴位置の購入根拠に使いません。

全POM案を最安の基準として維持し、見た目を真鍮色に寄せる場合の差額を比較した。KHK BSS1-18B/BSS1-20CはM1・20°、歯幅6mm、6mm穴、M4止めねじ付きの黄銅歯車で、DS1と同じモジュール/圧力角で噛み合う。ハブ長8mm・全長14mmのため、現行の5mm軸・全長12mmの位置へそのまま置き換えられない。[BSS寸法表](https://khkgears.net/pdf/bss.pdf)

| 比較案 | 追加する部品 | 必要な軸・支持品 | 全POM案からの既知価格差（税込換算） | 参考総額 |
|---|---|---|---:|---:|
| 少数アクセント | BSS1-18B ×10（A01/A03/A05/A07/A09/A11/A13/B02/B10/B13） | 6×28mm軸10本、80B-0608ブッシュ10個、KSC0605カラー10個、6×12×1mm POMワッシャー1袋。残り16本の短軸と共有軸は5mmのまま。 | **約¥15,392** | **約¥88,595** |
| 広い真鍮面 | BSS1-18B ×11 + BSS1-20C ×10 | 6×28mm軸19本、共有軸6×60mm、80B-0608を21個、80B-0508を7個、KSC0605を19個、KSC0505を7個、6×12mm/5mm用ワッシャー各1袋、4↔6mm継手。 | **約¥32,331** | **約¥105,534** |

歯車候補の価格差は前版の部品リストを基準にした機械側だけの比較で、v0.21の完成BOM総額ではない。送料、工具、支持板・表示キャリアの再設計、表面処理、軸長の追加調整費は含まない。10個案は既存5mm共有軸の保持と必要長が未確定。

価格根拠は、KHKの現行適用価格表（2025-12-01改定・税別）でDS1-18/20各¥260、BSS1-18B¥1,560、BSS1-20C¥1,590。よって歯車差額は10個案が税別¥13,000（税別から換算して税込¥14,300）、21個案が税別¥27,600（同税込¥30,360）。残額は軸ピンの販売単位、6mmブッシュ、追加ワッシャー、6mm継手の差し替えを含む。[KHK 2025価格表](https://www.khkgears.co.jp/files/libs/5368/202511041428192234.pdf)

購入先の現行表示では、BSS1-18B（[MonotaRO](https://www.monotaro.com/p/8339/7127/)）とBSS1-20C（[MonotaRO](https://www.monotaro.com/p/8339/7215/)）は各¥1,868税込、調査時5営業日表示・返品不可。21個をこの表示価格で買う場合、真鍮歯車だけで¥39,228（送料別）。基準価格差の計算にはこの小売表示を混ぜず、同じKHK公式価格表同士を比較した。

追加部品の現行候補：

- 6×28mm SUS303 B種h7平行ピン（3本入、¥593/袋）[MonotaRO](https://www.monotaro.com/p/4215/6791/)。21個案は7袋（19本使用、2本予備）、10個案は4袋（10本使用、2本予備）。
- 6×60mm SUS303 B種h7平行ピン（2本入、¥934/袋）[MonotaRO](https://www.monotaro.com/p/4294/2453/)。21個案の共有軸候補。断面図では1mm切り、z=0–59mmに配置して継手へ10mm挿入する仮寸法。セットねじ保持、面取り後のh7区間、底付き、組立順を確認するまで加工長は未受入。
- OILES #80 80B-0608（ID6×OD8×L8mm、¥51税込/個）[MonotaRO](https://www.monotaro.com/p/0045/9313/)。既存80B-0508はID5×OD7×L8mm、¥56税込/個。
- KANA KSC0605（ID6×OD12×幅5mm、¥208税込/個）[MonotaRO](https://www.monotaro.com/p/1029/5117/)。
- 6×12×1mm POMワッシャー（20枚入、¥549税込）[MonotaRO](https://www.monotaro.com/g/00428118/)。
- NBK MJT-20-RD-4-6（4mm↔6mm、¥2,528税込）[MonotaRO](https://www.monotaro.com/p/2193/5138/)。外径20mmの旧サイズ案。上記比較は履歴のみで、現行候補はBSS1-20C設計ノート記載のMJT-14-RD-4-6（4mm↔6mm）。

価格比較はカタログ表と販売店表示を使った机上見積で、注文・部品手配はしていない。現行の軸/Zスタックは[BSS1-20C候補](../03-mechanical/bss20_axis_support_candidate-2026-10-22.md)を参照。

## 3. 設計候補と受入待ち

| 項目 | ベースライン候補 | 現物/証拠で閉じる条件 |
|---|---|---|
| 3.4Cの改版/表示 | Waveshare SKU31523、USB TO UART Type-Cから5V給電 | 基板改版、取付穴、厚み、端子、最大電流、画質、熱を受入。40-pinへ5Vを注入しない。|
| 外付けRTC | Adafruit DS3231 #3013 + CR1220をモジュール自身のホルダーへ。3.3V給電 | GPIO28/29、I²Cプルアップ、SNTP更新、電池保持、ネット断/停電後復旧を確認。CR1220を3.4C RTC端子へ接続しない。|
| 表示5V source | DFRobot DFR0758のUSB-A標準5V出力をMPA-ACECSS03BKでUSB TO UART Type-Cへつなぐ（ADR-0019） | 標準型番を選定済み。完成品で表示器を起動し、最大輝度/Wi-Fi/microSD負荷のときに電圧と安定動作を一度確認する。特注確認・専用PCB設計は不要。|
| USBデバッグ | 通常運転時はDFR0758 USB-AからA-CケーブルでUSB TO UARTへ給電 | フラッシュ/デバッグ時は内部給電ケーブルを外しPCへ接続。二つの5V源を同時接続しない。|
| ヒューズ | Littelfuse MINI 297、入力3A/モーター2A/LED2Aの3枝選定済み。5V補助主幹ヒューズは追加しない | 完成品の実負荷・異常時保護を受入。枝の追加は現行構成に含めない。|
| モーター停止 | 9V→2A MINIヒューズ候補→独立SPST→TMC2209 VM | リセット/brownout/無配線時のENN HIGH、長押し停止、SPSTでの直接VM遮断を確認。旧M1 eFuseは含めない。|
| モーター過電圧 | SMBJ12A VM clamp候補、10kΩ ENN pull-up、10kΩ STEP pulldown | back-drive/急停止時のVM波形、TVS温度、ドライバー定格、起動中のSTEP/ENNを測定。|
| 電源容量 | PD入力は15V/2A（30W）。DFR0758表示枝、DFR1015 9Vモーター枝、#2851補助5V/LED枝 | 画面/無線/SD、LED、モーターを同時に動かし、PD入力と各枝が安定することを完成品で確認。電力余裕は実機受入で確定。|
| 機械取付 | 外寸270×205×172mm、内寸246×181×148mm。ウォールナットケース見積図A01/A02 v0.4。8mm透明支持板、前面ガード、3mm背面電装板を選定済み | 見積回答と接合方法を発注前に図へ反映。表示/配線/保護板/整備性は完成品の組立で受入。|
| 外観素材 | 承認済みForest Guardian参照ボード | 高解像度文字盤原画・使用条件・出典を確認する（FG-038/OQ-10）。|

## 4. 基板設計とソフトウェアの境界

- 表示/主制御は完成開発基板、PD受電はHUSB238、表示5VはDFRobot DFR0758、モーター9VはDFRobot DFR1015、補助5VはPololu基板、モーター駆動はTMC2209ブレークアウトを候補とする。TPS25810専用基板とEVMは現行案に含めない。
- 新設計で使うモーター保護のベースラインは分岐ヒューズ、独立スイッチ、ENN安全初期値、VM TVS候補。旧M1 eFuse、故障ラッチ、旧7軸ワンホット配線を新設計へ持ち込まない。
- ESP-IDF v5.5.5、Waveshare BSP 3.0.1、LVGL 9、Espressif `esp_jpeg` 1.3.1をソフトウェア基準に記録。mainのCIで安全既定設定とモーター出力有効設定の対象ビルドは成功済み。
- CI/ホストテストは基板GPIO、実表示、RTC保持、モーター音/温度、電源容量、筐体加工の受入ではない。DR-02〜06はValidationStatus OPEN、DR-07はHOLD。

## 5. 調査元

価格・型番は各行の購入先へ記載。技術仕様は[Waveshare公式資料](https://docs.waveshare.com/ESP32-P4-WIFI6-Touch-LCD-XC)、[NEMA-8 #4411](https://www.adafruit.com/product/4411)、[TMC2209 #6121](https://www.adafruit.com/product/6121)、[NBK MJT資料](https://www.nbk1560.com/products/coupling/couplicon/jaw_type/MJT-RD/)、[HUSB238 #5807](https://www.adafruit.com/product/5807)、[DFRobot DFR0758](https://www.dfrobot.com/product-2166.html)、[DFRobot DFR1015](https://www.dfrobot.com/product-2599.html)、[ELECOM MPA-ACECSS03BK](https://www.elecom.co.jp/products/MPA-ACECSS03BK.html)、[Pololu #2851](https://www.pololu.com/product/2851)、[DFRobot FIT0836](https://www.dfrobot.com/product-2398.html)を参照。オンライン価格・在庫は変動するため、調達時に再確認する。
