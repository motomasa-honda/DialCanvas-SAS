# Forest Guardian / DialCanvas 一台試作・未選定部品調達候補

更新日：2026-10-21

状態：**設計ベースラインv0.21の購入候補/参考価格。発注・寸法受入・電気受入・製作の承認ではない。**

本表は[設計ベースラインv0.21](../10-desk-redesign/design-baseline-v0.21.md)の部品候補です。静かな単一モーター、不規則な二層歯車、3.4型画面、microSD文字盤、USB-C給電を前提にします。旧7軸/M1部品は現行候補に含めません。

価格は調査時の税込表示を基本にし、税別表示は10%を加えた参考税込額も併記した。送料、為替、加工費、工具、予備部品は含まない。価格が表示されていても、在庫、見積、配送日、現物適合を保証しない。

## 1. 購入候補BOM

| 分類 | 部品・型番 | 数量/買い方 | 価格（参考） | 購入先 | 選定状態・残作業 |
|---|---|---:|---:|---|---|
| 表示・制御 | Waveshare ESP32-P4-WIFI6-Touch-LCD-3.4C / SKU31523、3.4型円形IPS 800×800 | 1 | **US$64.99（公式）/ £62.40税込（The Pi Hut）/ US$63.90（SpotPear）/ €72.20（RLX、税別価格€58.70併記）** | [Waveshare](https://www.waveshare.com/esp32-p4-wifi6-touch-lcd-3.4c.htm?sku=31523)・[The Pi Hut / WAV-31523](https://thepihut.com/products/esp32-p4-3-4-round-touch-display-dev-board-800x800)・[SpotPear](https://spotpear.com/shop/ESP32-P4-3.4-inch-Round-LCD-Display-TouchScreen-WIFI6/ESP32-P4-WIFI6-Touch-LCD-3.4C.html)・[RLX Components / WS-31523](https://rlx.sk/en/esp32-p4/10469-esp32-p4-34-round-touch-display-devboard-800800-dual-microphones-support-wi-fi-6bt5-le-ws-31523.html) | 2026-10-21確認：公式店SKU31523はOut of Stock、The Pi HutはSold out。SpotPearは同じ3.4C型番を$63.90・In Stock表示（販売元欄はSpotPear）。RLX ComponentsはWaveshare WS-31523として€72.20・残り1個表示。RLXは掲載在庫が実在庫と異なる場合があるため要確認。両代替店とも日本配送費/納期は未確認。発注候補は見つかったが、販売元確認・実在庫・配送先を注文前に照合する。3.4C/31523をサイズ・型番基準に固定し、メーカー公称115×115mm/表示87.6mmでCADは継続。購入後は基板改版、厚み・取付穴・端子奥行き・電流・表示品質を受入確認。|
| 表示基板取付 | タカチ HES3-10 M3樹脂スペーサー + 大里 M3×12/M3×6ステンレスなべ小ねじ | スペーサー20個袋、ねじ各50本袋 | **¥340 + ¥274 + ¥208 = ¥822** | [HES3-10](https://www.monotaro.com/p/5723/7717/)、[M3×12](https://www.monotaro.com/p/1714/2006/)、[M3×6](https://www.monotaro.com/p/1714/1979/) | 4点取付を想定。8mm支持板側はM3×12、基板側はM3×6を使う候補。3.4C実基板の穴径・穴位置がM3に適合し、ねじ頭/コネクターと干渉しないことを現物確認してから使う。モノタロウのHES3-10は別途特別運賃¥660表示。|
| 文字盤媒体 | KIOXIA microSDHC 32GB Class 10/UHS-I U1 | 1 | ¥2,390 税込 | [ヨドバシ](https://www.yodobashi.com/product/100000001006382817/) | 800×800 JPEGをPCからコピーする用途。FAT32で初期化し、本体で読取・破損復帰を確認。|
| 外付けRTC | Adafruit DS3231 Precision RTC Breakout #3013 | 1 | **約¥3,150 税込** | [DigiKey Japan](https://www.digikey.jp/ja/products/detail/adafruit-industries-llc/3013/5875808) | I²C 0x68。3.3V給電候補。CR1220はこのモジュールのホルダーへ装着し、3.4CのRTC端子には接続しない。回路・I2Cピン・保持動作は実機確認前。|
| RTCバックアップ電池 | Maxell CR1220.1BS | 1 | **約¥220 税込** | [ヨドバシ（CR1220一覧）](https://www.yodobashi.com/category/21484/53821/53827/) | DS3231モジュール自身の電池ホルダー用。3.4C基板のRTC電池端子には一次電池を絶対に接続しない。電池は消耗品。|
| 平歯車 | KHK DS1-18 / DS1-20 / DS1-24 / DS1-28、M1、POM、5mm穴 | 11 / 10 / 3 / 4 | 税別¥7,360、税込換算 **¥8,096** | [KHK寸法資料](https://khkgears.net/pdf/ds.pdf)・[価格表](https://www.khkgears.co.jp/files/libs/5368/202511041428192234.pdf) | 選定済み候補。歯車数28個。価格は2025-12-01適用表の値。成形穴とh7軸の圧入は端材で試験。|
| 回転ブッシュ | OILES #80 80B-0508、ID5×OD7×L8mm | 28 | 税別¥1,428、税込換算 **¥1,571** | [MonotaRO](https://www.monotaro.com/p/0045/9277/) | 選定済み候補。支持板の穴公差・圧入力・内径収縮・始動トルクを同じ材/厚みの端材で確認。|
| 軸ピン | 大阪魂 SUS303 B種 h7平行ピン 5×28mm、4本入 | 26本必要、7パック購入（28本） | ¥593/パック、**¥4,151** | [MonotaRO](https://www.monotaro.com/p/4215/6572/) | MISUMIの個別切断軸より安価な規格ピン候補。2本予備。歯車とブッシュの圧入/回転を現物確認。|
| 共通軸 | 大阪魂 SUS303 B種 h7平行ピン 5×60mm、2本入を58.5mmへ切断 | 1パック | **¥593** | [MonotaRO](https://www.monotaro.com/p/4215/6667/) | 1本使用、1本予備。モーター側先端を1.5mm切り、仕上がり58.5mmとする一度限りの追加工。歯車位置を保ち、継手z=48–70mmに5mm軸を7mm挿入。切断面を軽く面取りし、h7嵌合部は加工しない。|
| 軸カラー | KANA KSC0505、ID5×OD11×幅5mm、M3止めねじ | 26 | ¥208/個、**¥5,408** | [MonotaRO](https://www.monotaro.com/p/1029/5074/) | 選定済み候補。片側カラーと板の間にワッシャーを置く。止めねじの平面当たりと緩みを確認。|
| スラストワッシャー | POM M5×10×1.0mm、26枚入 | 1パック | **¥549** | [MonotaRO](https://www.monotaro.com/p/4293/0386/) | カラーの擦れを避ける候補。板との接触、摩擦、摩耗を手回し試験で確認。|
| ステッパー | Adafruit NEMA-8 #4411、4mm軸 | 1 | 税別¥3,265、税込換算 **¥3,592** | [DigiKey](https://www.digikey.jp/ja/products/detail/adafruit-industries-llc/4411/11497509) | 200 step/rev、0.6A/相の候補。保持トルク・始動余裕・温度・負荷音は実機受入。|
| モータードライバー | Adafruit TMC2209 breakout #6121 | 1 | 税別¥1,465、税込換算 **¥1,612** | [DigiKey](https://www.digikey.jp/ja/products/detail/adafruit-industries-llc/6121/25981358) | MS1/MS2開放で1/8、SPRD開放でStealthChop、EN HIGHで出力禁止。約0.3A RMSを初期評価点とするが、実電流調整と静音合格は未完。|
| モーターVM TVS | Littelfuse SMBJ12A、unidirectional | 1 | 参考価格は調達時確認 | [Littelfuse](https://www.littelfuse.com/ja-jp/products/overvoltage-protection/tvs-diodes/surface-mount/smbj/smbj12a) | VM/GND近傍へ置く候補。VRWM=12V、最大クランプ19.9V。回生過渡の波形/エネルギーは未検証。|
| ENN/STEP安全抵抗 | 10kΩ、ENN pull-upとSTEP pulldown | 2 | 価格僅少、購入候補表の小物へ別途追加 | 受動部品一般品 | ENN→VIO/3.3V、STEP→GNDの候補。実ドライバー基板のVIO/論理/外部プル状態と起動挙動を照合。|
| 軸継手 | NBK MJT-14-RD-4-5、4mm↔5mm、外径14×全長22mm、ハブ長L=7mm | 1 | **¥2,088 税込** | [MonotaRO](https://www.monotaro.com/p/3751/1844/)・[NBK製品情報](https://www.nbk1560.com/products/coupling/couplicon/jaw_type/MJT-RD/MJT-14-RD/MJT-14-RD-4-5/) | 継手z=48–70mm。共通軸/モーター軸ともL=7mm挿入。モーター面z=72mmとし、資料値9mm突出のうち2mmは継手外へ残す。MonotaROは5日以内出荷/返品不可を表示。公称表示基板外形との名目平面すき間3.5mm。軸同心、実挿入、止めねじ保持を確認。|
| USB-C PDアダプター | Anker 511 Charger (Nano 3, 30W) A2147 | 1 | **¥2,790 税込** | [Anker Japan](https://www.ankerjapan.com/products/a2147) | 9V/3A出力に対応する候補。9V時の電力上限は27W。全負荷時のPD契約、電圧降下、温度を測る。|
| USB-Cケーブル | ELECOM MPA-CC10PNBK、C-C、1m、PD 60W | 1 | **¥1,720 税込** | [ELECOM](https://www.elecom.co.jp/products/MPA-CC10PNBK.html) | 60W表示は本システムが60Wを得る意味ではない。ケーブル経由で9V契約・電圧降下を確認。|
| PD受電 | Adafruit HUSB238 #5807 搭載基板（Switch Science ADA-5807） | 1 | **¥1,265 税込** | [Switch Science](https://www.switch-science.com/products/9296) | 9V/3Aをジャンパー設定する。PD電源が対応する契約だけ成立する。出荷初期値は5V/1Aなので設定と保護を確認。|
| 5V変換 | Pololu D24V50F5 #2851、入力6–38V、5V出力 | 1 | 税別¥5,136、税込換算 **¥5,650** | [DigiKey](https://www.digikey.jp/ja/products/detail/pololu/2851/10451177)・[Pololu仕様](https://www.pololu.com/product/2851) | 旧#4082（3A級）から5A定格候補へ更新。Pololu直販ページは2026-10-21確認時に「Rationed (Active)」・バックオーダー可、US$32.95表示のため、購入前にDigiKey在庫/納期も再確認する。5Aは部品仕様であり、閉箱連続出力能力やシステム容量の保証ではない。画面最大輝度・SD・照明・モーターの同時負荷と熱を測る。|
| 5V出力端子 | Pololu #2494、0.1インチ/2.54mmピッチ5極ねじ端子台（2個入り） | #2851に1個使用、1個予備 | **US$4.37** | [Pololu](https://www.pololu.com/product/2494) | 26–18AWG、定格6Aの既製端子台。#2851の端子ピッチと周辺部品へのクリアランスを照合し、基板へはんだ付けする候補。|
| 表示基板給電用USB-C source | TI TPS25810EVM-745、5V入力、Type-C DFP、3A広告設定 | 1 | **約¥5,734（DigiKey掲載スナップショット、税/送料別途確認）** | [TI](https://www.ti.com/tool/TPS25810EVM-745)・[TIガイド](https://www.ti.com/lit/pdf/slvuai0)・[DigiKey](https://www.digikey.jp/ja/products/detail/texas-instruments/TPS25810EVM-745/5761581) | Pololu #3411のCC抵抗変更案を置換。TPS25810の実電流リミットtyp.3.40Aは3A広告を超える設計負荷を許可しない。EVMは評価基板であり据付、ジャンパ、端子、データ経路、温度、在庫を受入れる。|
| 表示基板内部USB-Cケーブル | ELECOM MPA-XCCECSS03BK、C-C、0.3m | 1 | **¥1,430税込** | [ELECOM](https://www.elecom.co.jp/products/MPA-XCCECSS03BK.html) | TPS25810EVM sourceから3.4CのUSB TO UART入力までの給電用候補。EVM経由でフラッシュデータを通す想定はしない。|
| 暖色LED | DFRobot FIT0836、5V、暖色、60LED/m、1m品 | 1本から約330mm使用 | 税別¥982、税込換算 **¥1,080** | [DigiKey](https://www.digikey.jp/en/products/detail/dfrobot/FIT0836/15283059)・[DFRobot仕様](https://www.dfrobot.com/product-2398.html) | 1m上限4Wから330mmは最大約1.32W/0.264Aの試算。調査時DigiKey在庫3、標準納期表示9週。切断長・拡散材・木部温度を確認。|
| LED拡散板 | 光 A032-2US、乳白半透明アクリル、2mm、160×180mm | 1枚 | **¥472 税込** | [MonotaRO](https://www.monotaro.com/g/00025130/) | 既製板を小片に切り出す候補。安価で扱いやすいが可燃性のため、LEDから距離をとり、閉箱連続点灯で板・木部温度を測ってから配置する。光量低下と点光源の消え方も確認。|
| ヒューズホルダー | エーモン 3367、MINI平型、電線約9cm | 4個（入力・モーター・5V主幹・LED枝） | ¥549/個、**¥2,196** | [MonotaRO](https://www.monotaro.com/g/05234920/) | ホルダーのみ。試作値は入力3A/モーター1A/5V主幹4A/LED1A。導線・端子・突入・故障試験後に定格/時間特性を確定。|
| 配線 | UL1007 AWG22、赤/黒、各10m | 各1ロール | ¥956/巻、**¥1,912** | [赤](https://www.monotaro.com/p/6242/6946/)・[黒](https://www.monotaro.com/p/6242/6928/) | 各枝の線長・端子・電流を確定後に切る。記載電流値をそのまま設計値にせず、ヒューズと配線温度を確認。|
| 電源分岐端子 | WAGO 221-413 3極レバー端子 + 221-503 ねじ固定キャリア | 各4個（9V+/9V GND/5V+/5V GNDの4節点） | 税込換算 **約¥1,914** | [221-413](https://www.digikey.jp/ja/products/detail/wago-corporation/221-413/13549610)・[221-503](https://www.digikey.jp/ja/products/detail/wago-corporation/221-503/15547037)・[WAGO寸法/取付](https://www.wago.com/global/installation-terminal-blocks-and-connectors/mounting-carrier/p/221-503) | 221-413は24–12AWG対応、221-503で木製内桟へねじ固定する候補。DigiKey表示の税別単価¥124/¥311から計算。各＋枝は分岐後に負荷別ヒューズを置く。モーター電流の戻りを画面基板GNDへ通さず、結線後に極性/導通/短絡を検査する。|
| ロータリーエンコーダー | ALPS Alpine EC11E15244G1、押し込み付き、15 pulse/30 detent | 1 | 税別¥273、税込換算 **¥300** | [フルタカパーツ](https://www.furutaka-netsel.co.jp/maker/alps/ec11) | 操作候補。6mm Dカット軸。回転方向、押下、長押し誤認とパネル配置を確認。|
| エンコーダーノブ | Sato Parts K-8075-6.1、穴6.1mm、M3止めねじ、φ26×17.3mm | 1 | **¥295 税込** | [マルツ](https://www.marutsu.co.jp/GoodsDetail.jsp?salesGoodsCode=2978) | 上記エンコーダーに組み合わせる候補。指が当たる周囲、木壁との隙間を模型で確認。|
| 独立スイッチ | NKK MN11SS1W01、SPST ON/OFF | 2 | ¥1,307/個、**¥2,614** | [DigiKey](https://www.digikey.jp/ja/products/detail/nkk-switches/MN11SS1W01/20840209) | モーター枝と照明枝に各1個。6.5mmパネル穴候補。モーター側は分岐1Aヒューズ候補の後段でTMC2209 VMを直接遮断。旧M1 eFuseを使わない。定格と実回路を照合。|
| 前後支持板 | 透明PC、300×450×8mm、1枚 | 1枚から252×187mmを2枚取り | 標準価格 税別¥7,960、税込換算 **¥8,756** | [AXEL / AS ONE](https://axel.as-1.co.jp/asone/d/68-7869-18/) | Web購入価格・在庫の確定表示なし。寸法上は2枚取れる見込み。ブッシュ試験片で割れ/圧入/歪みを確認してから材料と穴を固定。|
| 前面ガード | 透明PC板、300×450×3mm | 1枚 | **¥1,750 税込** | [ヨドバシ](https://www.yodobashi.com/product/100000001001981779/) | 調査時在庫僅少表示。光学反射、端面、固定方法、歯車への指の到達防止を確認。|
| 木箱材 | ラワン合板、12×300×600mm | 2枚 | ¥948/枚、**¥1,896** | [ナフコ](https://nafco-online.com/products/detail.php?product_id=23816701) | 店舗受取品。濃色仕上げの下地候補で、本ウォルナット無垢材ではない。曲面前板は別加工部材。|
| 着脱背面板 | ラワンT2カットベニヤ T2411、4×300×300mm | 1枚から270×205mmへ切出し | **¥362 税込** | [MonotaRO](https://www.monotaro.com/g/02947856/) | 既製カット板を使う候補。周辺の平坦度と箱内配線の逃げを現物合わせする。|
| 背面板/端子キャリアねじ | 八幡ねじ 3.1×13mm超低頭木ねじ NI(中) | 94本袋、背面板6本 + キャリア最大8本を想定 | **¥329 税込** | [MonotaRO](https://www.monotaro.com/p/0928/0635/) | 背面板を既存12mm箱材から作る連続桟へ留める候補。WAGOキャリアの取付穴に径/頭が合う場合は同じ袋から各2本使用する。穴適合、下穴、端距離、キャリア底厚を含むねじ先端の非貫通を実物で確認。ヒンジなし。|
| 木部仕上げ | WATCOオイル W-13 ダークウォルナット、200mL | 1缶 | **¥2,230 税込** | [ヨドバシ](https://www.yodobashi.com/product/100000001006190266/) | 端材で色と塗布量を試す。使用済み布の発熱/発火注意に従い水に浸して処分。|

## 2. 価格のまとめ

前版の概算 **¥73,203 + US$73.31** はPololu #3411を含み、新しいType-C source、TVS、ENN/STEP抵抗、枝ヒューズ候補を反映していないため、v0.21総額としては無効です。上表の価格は調査時の参考値で、税、為替、送料、加工費、工具、在庫を含めた購入総額ではありません。全品の価格が同じ調査日に取得できていないため、新しい総額は算出していません。

### 真鍮歯車の比較候補

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
- NBK MJT-20-RD-4-6（4mm↔6mm、¥2,528税込）[MonotaRO](https://www.monotaro.com/p/2193/5138/)。外径20mmの旧サイズ案。現行4↔5mmはより小さいMJT-14-RD-4-5。

価格比較はカタログ表と販売店表示を使った机上見積で、注文・部品手配はしていない。機械側の暫定Z位置、後支持板、モーター余裕は[歯車成立性ノート](../03-mechanical/gear-feasibility.md#外観用の既製真鍮歯車案未採用)に記載。

## 3. 設計候補と受入待ち

| 項目 | ベースライン候補 | 現物/証拠で閉じる条件 |
|---|---|---|
| 3.4Cの改版/表示 | Waveshare SKU31523、USB TO UART Type-Cから5V給電 | 基板改版、取付穴、厚み、端子、最大電流、画質、熱を受入。40-pinへ5Vを注入しない。|
| 外付けRTC | Adafruit DS3231 #3013 + CR1220をモジュール自身のホルダーへ。3.3V給電 | GPIO28/29、I²Cプルアップ、SNTP更新、電池保持、ネット断/停電後復旧を確認。CR1220を3.4C RTC端子へ接続しない。|
| Type-C表示source | TI TPS25810EVM-745、5V入力、3A広告 | EVMジャンパ、CC設定、接続方向、出力電圧、電流、温度、3.4Cの受入電流を確認。EVMは評価基板として現物据付を確認。|
| USBデバッグ | 通常運転時はsource EVMからUSB TO UARTへ給電 | フラッシュ/デバッグ時はsource cableを外しPCへ接続。二つの5V源を同時接続しない。|
| ヒューズ | 入力3A、モーター1A、5V主幹4A、LED1Aの候補 | 実負荷、突入、故障電流、導線/端子/ホルダーの許容値と時間特性で確定。|
| モーター停止 | 9V→1Aヒューズ候補→独立SPST→TMC2209 VM | リセット/brownout/無配線時のENN HIGH、長押し停止、SPSTでの直接VM遮断を確認。旧M1 eFuseは含めない。|
| モーター過電圧 | SMBJ12A VM clamp候補、10kΩ ENN pull-up、10kΩ STEP pulldown | back-drive/急停止時のVM波形、TVS温度、ドライバー定格、起動中のSTEP/ENNを測定。|
| 5V容量 | #2851、表示15W上限+LED1.32W上限の静的見積もり | 最大輝度、Wi-Fi/SD、LED、モーターの全負荷で電流・電圧降下・閉箱温度を記録。|
| 機械取付 | 270×205×145mm参照、ウォールナット、8mm透明支持板、3mmガード候補 | 基板/配線/端子/保護板の実寸、穴/溝、指到達、前後整備、原本外観を照合し加工図を出す。|
| 外観素材 | 承認済みForest Guardian参照ボード | 高解像度文字盤原画・使用条件・出典を確認する（FG-038/OQ-10）。|

## 4. 基板設計とソフトウェアの境界

- 表示/主制御は完成開発基板、PD受電はHUSB238、5V変換はPololu基板、Type-C sourceはTI評価基板、モーター駆動はTMC2209ブレークアウトを候補とする。
- 新設計で使うモーター保護のベースラインは分岐ヒューズ、独立スイッチ、ENN安全初期値、VM TVS候補。旧M1 eFuse、故障ラッチ、旧7軸ワンホット配線を新設計へ持ち込まない。
- ESP-IDF v5.5.5、Waveshare BSP 3.0.1、LVGL 9、Espressif `esp_jpeg` 1.3.1をソフトウェア基準に記録。mainのCIで安全既定設定とモーター出力有効設定の対象ビルドは成功済み。
- CI/ホストテストは基板GPIO、実表示、RTC保持、モーター音/温度、電源容量、筐体加工の受入ではない。DR-02〜06はValidationStatus OPEN、DR-07はHOLD。

## 5. 調査元

価格・型番は各行の購入先へ記載。技術仕様は[Waveshare公式資料](https://docs.waveshare.com/ESP32-P4-WIFI6-Touch-LCD-XC)、[NEMA-8 #4411](https://www.adafruit.com/product/4411)、[TMC2209 #6121](https://www.adafruit.com/product/6121)、[NBK MJT資料](https://www.nbk1560.com/products/coupling/couplicon/jaw_type/MJT-RD/)、[HUSB238 #5807](https://www.adafruit.com/product/5807)、[Pololu #2851](https://www.pololu.com/product/2851)、[DFRobot FIT0836](https://www.dfrobot.com/product-2398.html)を参照。オンライン価格・在庫は変動するため、調達時に再確認する。
