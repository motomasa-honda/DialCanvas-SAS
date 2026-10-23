# 3.4C用USB-C給電回路の設計候補 v0.1

- 日付: 2026-10-22
- 状態: **回路の機能構成と上流電源の候補を記録。回路図・PCB・購入BOMではない**
- 対象: ESP32-P4 3.4CのUSB TO UART Type-C端子へ、内部5V系から給電するsource
- 関連: [ADR-0018](../../adr/0018-usb-c-source-board-replacement.md)、[電源・制御](power-and-control.md)、[購入準備監査](../02-architecture/purchase-readiness-audit-2026-10-21.md)

## ここまで決まった回路の骨格

TIの「BC 1.2なしType-C DFP」の最小構成を基にする。USBデータ線を使わず、Type-Cの接続検出とVBUS電源制御だけを行う。

| 回路要素 | 接続/設定候補 | 根拠・状態 |
| --- | --- | --- |
| U1 | TPS25810RVC、20ピンWQFN、3×4mm | TIの現行IC。単体購入・実装は未確定 |
| 電源入力 | #4092メーカー設定変更品の公称5.2V候補をIN1、IN2、AUXへ接続 | 5.2V設定が未確認のため仮定値。IN1/IN2/AUXの動作範囲と起動時過電圧を、確定 converter specと照合する |
| Enable | ENを有効レベルへ固定 | 試作中にsourceを止める必要があれば、基板スイッチ/上流電源遮断との役割を別途決める |
| 3A広告 | CHG=High、CHG_HI=High | TIの標準アプリ条件。3A広告は負荷が3Aまで必ず動く保証ではない |
| 電流制限 | 3A広告設定に対応するTPS25810内蔵制限 | データシート値はtyp. 3.4A、条件範囲3.16〜3.64A。表示器の許容負荷や上流配線保護とは別に扱う |
| REF | REF–REF_RTN間に100kΩ、1% | IC直近に配置する指定 |
| 入力コンデンサ | INピン近傍に実効120µF以上を確保。150µF級を基準に部品を選ぶ | TI標準アプリ。電圧定格、許容差、リップル電流、実装寸法はBOM化時に決定 |
| 出力コンデンサ | receptacle VBUS近傍に10µF級セラミック | TI標準アプリ。容量のDCバイアス低下と電圧定格を部品選定時に確認 |
| USB-C receptacle | U1のCC1/CC2を各CC端子へ接続。VBUSはOUT、GNDは共通GND | 型番、フットプリント、シェル固定、ピン定格は未選定 |
| データ/未使用信号 | D+/D−/SBU/SuperSpeed信号、FAULT/LD_DET/UFP/POL/AUDIO/DEBUGは未接続候補 | 内部sourceから表示器へUSBデータを通さない。デバッグ時は内部C-Cケーブルを外してPCを接続 |
| 接続先 | 表示器のUSB TO UART Type-C端子 | Waveshare公開回路図ではUSB0_5VとCC1/CC2のRd(5.1kΩ)を確認。入手現物の改版照合は別途必要 |

未使用のオープンドレイン出力をNCにする場合は、採用回路とパッケージのピン処理をデータシートと照合する。USB-C receptacleとケーブルの型番、PCB外形、取付、熱設計はまだ指定していない。

## 5V電圧マージンと上流変換器候補

Pololu D24V50F5 (#2851)は調整式ではなく固定5V出力で、仕様精度は±4%。低側は4.80Vである。TPS25810のOUT通過抵抗は3A時に最大55mΩなので、最大0.165V下がり、配線/コネクター損失を引く前のsource receptacle電圧は約4.635Vとなり得る。TIが示すType-C source receptacleの範囲4.75〜5.5Vを下回るため、#2851をTPS25810へ直結する案は採らない。TIは可能な場合、配線損失を補うため入力を5Vより100〜200mV高くするよう推奨している。

Pololu USB 2.0 Type-C breakout #3411は標準状態でCC1/CC2を5.11kΩでGNDへプルダウンするsink/UFP設定であり、Pololuはsource用途では既設抵抗を切り離し、CCへ独自接続するよう案内している。同製品はコネクター信号のbreakoutで、電源source制御/電流制限を含む完成sourceではないため、完成機用の置換品にはしない。[Pololu製品説明](https://www.pololu.com/product/3411)

上流候補はPololu D36V50F6 (#4092)の**メーカー設定変更品を5.2V出力で見積もる案**とする。同製品ページは出力電圧のカスタマイズを受けると記載する。標準品は6V、入力6.5〜50V、外形25.4×25.4×9.5mm、固定穴3か所で、1個の標準品表示価格はUS$34.95。目標条件は公称9V入力で5.2V±4%、3A連続出力とするが、その設定/精度/電流/温度特性/価格/納期は未確認であり、標準6V品を買って代用できる意味ではない。

5.2V±4%がメーカー保証され、公称9V入力時に3A連続出力できると仮定した机上予算は次のとおり。4.992V（入力下限）−0.165V（TPS25810の3A時最大通過損失）−0.025V（変換器出力からsource receptacleまでの設計上限）= **4.802V**。無負荷側の上限は5.408Vで、TPS25810のIN2最大5.5VおよびType-C source receptacle最大5.5Vを下回る。この仮定条件なら成立余地があるが、Pololuの特注精度/電流、配線降下、閉箱温度を確認するまで確定値ではない。25mVの経路降下は基板間配線とPCB配線を合わせた上限で、配置・線径決定後に再計算する。

source receptacleで確認する電圧範囲は4.75〜5.5Vとする。C-Cケーブルの電圧降下後に3.4C端へ届く電圧は別に測る。Waveshare公開資料から入力許容範囲の下限/上限は確認できていないため、実負荷での表示・SD・Wi-Fi動作とリセット有無も受入対象にする。ケーブル側の電圧降下をsource端の4.75V基準と混同しない。

メーカーから5.2V設定と精度/連続電流の回答を得るまでは、上流変換器を決定品・注文品として扱わない。調達後はsource receptacle側と3.4C側の電圧を、3A広告・最大表示負荷・無線/SD動作で分けて測る。試験を終えるまで3A広告、上流変換器、source基板の購入仕様は凍結しない。

## 発注可能性

この文書が定めるのは標準回路の接続方針と阻害事項まで。TPS25810 IC、コンデンサ、USB-C receptacle、追加変換器、PCBの型番/数量/価格/外形/実装は発注可能なレベルに達していない。TIの標準アプリ回路を転記した確定回路図でもないため、発注・製作・通電には使わない。

## 一次資料

- TI [TPS25810製品ページ](https://www.ti.com/product/TPS25810)：製品状態、電流広告、電流制限、パッケージ。
- TI [TPS25810データシート Rev. C](https://www.ti.com/lit/ds/symlink/tps25810.pdf)：§5 pin map、§6 operating/limit values、§8.2.1標準DFP回路と容量/配線損失の注意。
- TI [TPS66020/21データシート](https://www.ti.com/lit/ds/symlink/tps66020.pdf)：USB-C source receptacleのVBUSが4.75〜5.5Vである旨と電圧降下注意。
- Pololu [D24V50F5 #2851](https://www.pololu.com/product/2851)：固定5V、±4%、typical最大連続5Aの注記。
- Pololu [D36V50F6 #4092](https://www.pololu.com/product/4092)：標準6V品、カスタム出力の対応、外形/取付穴、標準価格の参考。
- Waveshare [ESP32-P4-WIFI6-Touch-LCD-XC公式回路図](https://files.waveshare.com/wiki/ESP32-P4-WIFI6-Touch-LCD-XC/ESP32-P4-WIFI6-Touch-LCD-XC-Schematic.pdf)：Type-C UART、USB0_5V、CC1/CC2実装。
