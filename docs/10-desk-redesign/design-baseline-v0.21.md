# Forest Guardian / DialCanvas Desk Edition — 設計ベースライン v0.21

- 基準日: 2026-10-22
- 状態: **一台試作の机上設計ベースライン。製作・通電・量産リリースではない**
- 要求台帳: [v0.21 requirements.yaml](../01-requirements/requirements.yaml)
- 決定記録: [ADR一覧](../../adr/README.md)
- 現在の作業/受入状態: [worklist.csv](worklist.csv)、[状態記録](status-2026-10-21.md)

この文書を現行Desk Editionの構成・インターフェース・候補値の統合基準とする。旧7軸設計の資料とブランチは履歴・参照専用で、新設計の要求、証拠、進捗へ混ぜない。部品、寸法、電気値に `PROVISIONAL` を付した項目は試作候補として一つに揃えた値であり、実物で受入れるまで製造値にはならない。

**このv0.21と参考BOMは完成機の全量購入指示ではありません。** 1軸用の市販部品は候補型番まで特定しましたが、支持板材・圧入/溝クーポン・測定治具・基板/配線包絡を含む発注可能な評価パッケージは未完了です。完成機用の全量BOMは保留です。表示基板寸法と位置の現行判断は[ADR-0016](../../adr/0016-waveshare-34c-mounting-and-clearance.md)、購入区分は[購入前設計監査](../02-architecture/purchase-readiness-audit-2026-10-21.md)を参照してください。

## 1. 製品の固定方針

- 製品は Forest Guardian / DialCanvas Desk Edition の一台用置き時計。
- 承認済み Forest Guardian の意匠、曲線ウォールナット外装、アンティークブラス色、暖色の間接照明を維持する。
- 基準外形は幅270 × 高さ205 × 奥行145 mm。最終外形は実部品・保護板・配線を含めて受入れる。
- 中央円形ディスプレイにアナログ文字盤画像とソフトウェア時計針を表示する。タッチ操作を使わない。
- 装飾歯車は静かなモーター1基で連動させる。**7軸固定でも歯車数固定でもない。** 28個のCADは配置候補に限る。
- 時刻計測と装飾歯車の制御は独立させる。モーター停止中も時計表示、SNTP同期、文字盤選択を継続する。
- 文字盤画像は電源OFF時にmicroSDへ追加・削除し、本体ロータリーエンコーダーで選択する。Web管理は初号機の範囲外。

## 2. システム構成

| サブシステム | ベースライン構成 | 状態 |
| --- | --- | --- |
| 表示・主制御 | Waveshare ESP32-P4-WIFI6-Touch-LCD-3.4C、SKU31523、3.4型円形IPS、800×800、USB TO UART Type-Cから5V給電 | 公式Drawingの前面Ø115.00mm、表示Ø87.60mm、4×M4×4.00表記、外周穴ピッチ75×78.5mmをCAD反映。PDF厚15.10mm/STEP包絡15.50mmの大きい方を採用。公開参照回路図は設計rev1.1。入手個体のPCB版、ねじ実仕様、端子/挿抜包絡、消費電力、画質は未受入 |
| 時刻 | Wi-Fi接続後SNTP。Adafruit DS3231 #3013をUTC保持用RTC候補として3.3V I²C接続。表示TZはJST (`JST-9`) | 構成PROVISIONAL。ネット断、電源断、電池保持は未受入 |
| 文字盤 | `DialCanvas/faces/<name>/face.jpg`、800×800 sRGB Baseline JPEG、最大8MiB、任意のversion 1 `dial.json`。既定文字盤は削除不可。SDは読取専用 | 形式FIXED。表示器上の操作と保持は未受入 |
| 入力 | ALPS EC11系ロータリーエンコーダー。回転でプレビュー、短押しで保存、900ms長押しで歯車の開始/停止要求 | 操作FIXED。GPIO割当はPROVISIONAL |
| 照明 | DFRobot FIT0836 5V暖色LED、330mm候補、独立SPSTスイッチ、乳白2mm拡散材 | 部品・光量・温度PROVISIONAL |
| 歯車駆動 | Adafruit NEMA-8 #4411、Adafruit TMC2209 #6121、単一駆動軸、出力軸1.6rpm候補 | 型番と電流設定PROVISIONAL。機構・静音性・熱は未受入 |
| 筐体 | ウォールナット木製ケース、透明前面ガード、前後整備、二層透明歯車支持板 | 寸法と材料PROVISIONAL。製造図と現物適合は未受入 |

## 3. 文字盤・時刻・操作インターフェース

| インターフェース | ベースライン |
| --- | --- |
| 表示器 | 3.4CのUSB TO UART Type-Cを通常時の5V入力に使う。40-pin GPIOヘッダーへ5Vを注入しない。画面は800×800、LCD有効領域Ø87.60mm、外周ガラスØ112.50mm+0.10mm、円形前面外径Ø115.00mm。115×115mmは最大矩形包絡。 |
| サービス接続 | TPS25810EVM側のType-C sourceは給電用候補。書込み/デバッグ時はsource cableを外し、USB TO UART端子をPCへ接続する。二つの5V源を同時に接続しない。モーター電源スイッチはOFFにする。 |
| 文字盤媒体 | microSD直下の `DialCanvas/faces/` のみを走査。英数字・`_`・`-`の1〜32文字フォルダー名、JPEG 8MiB以下。フォーマットや自動修復はしない。 |
| 描画 | 時・分・秒の3針をミリ秒補間し、16ms間隔で更新要求する。16msは実測フレームレート保証ではない。最低30fps、目標60fpsの表示確認を実機受入条件とする。 |
| 時刻復旧 | 有効なDS3231 UTCを起動時に復元し、Wi-Fi接続後のSNTP値をRTCへ書く。ネットワークも有効RTC値もない場合は `TIME NOT SET` を表示する。 |
| 操作入力GPIO候補 | A=GPIO2、B=GPIO3、SW=GPIO21。 |
| RTC GPIO候補 | SDA=GPIO28、SCL=GPIO29、I²C1、3.3V。RTC端子やI²C電圧は正確な基板改版で照合する。 |
| モーターGPIO候補 | STEP=GPIO4、DIR=GPIO5、ENN=GPIO32。正確な基板改版と拡張端子を確認するまで配線しない。GPIO6は割当てない。 |

GPIO候補の一次資料はWaveshare [3.4C公式ドキュメント](https://docs.waveshare.com/ESP32-P4-WIFI6-Touch-LCD-XC)と[公式回路図](https://files.waveshare.com/wiki/ESP32-P4-WIFI6-Touch-LCD-XC/ESP32-P4-WIFI6-Touch-LCD-XC-Schematic.pdf)。GPIO表は候補割当であり、実物基板の改版確認を置き換えない。

## 4. モーターと機械構成

### 4.1 駆動パラメーター

| 項目 | 試作候補値 | 判定 |
| --- | --- | --- |
| モーター | Adafruit NEMA-8 #4411、200 full-step/rev、定格0.6A/相、4mm軸 | PROVISIONAL |
| ドライバー | Adafruit TMC2209 #6121、MS1/MS2開放の1/8分割候補、StealthChop候補 | PROVISIONAL。現物ボードのジャンパ/既定値を確認 |
| 電流 | 0.30A RMS/相から評価開始 | PROVISIONAL。実設定、トルク、脱調、温度を測定 |
| 速度 | ドライバー出力軸1.600rpm候補 | PROVISIONAL。負荷時に確認 |
| STEP | 42.666… pulse/s平均、23,437/23,438µsの分数周期、2,560 pulse/60s | Cコア計算とホスト試験済み。GPIO波形とモーター速度は未測定 |
| 停止 | ソフトウェア停止はENN HIGH。ハードウェア停止はVM直列の独立SPSTスイッチ | 回路構成PROVISIONAL。リセット時、遮断、再起動を試験 |

### 4.2 歯車と軸

- 2026-10-22の現行機械候補はKHK BSS1-20C、M1・20T、6mm AH7穴/M4×4止めねじ付属、6mm h7軸、二層配置です。歯数や軸数は要求として固定しません。
- 28位置CADは再配置の計算例で、BSS1-20C×28とした候補です。全位置を1型番に揃えたので歯車外径は同一です。見た目、個数、座標は試作後に変更できます。
- 各単軸は一枚の支持板に通し、OILES #80 80B-0608で支持します。軸6mm h7、ハウジング穴8mm H7を仕様候補とし、ブッシュOD8.045〜8.157mmに対する公称しめしろは0.030〜0.157mmです。圧入後のIDはカタログ上+0.045〜+0.095mm。透明PC板の適合は同材試験片で確認するまで未受入です。
- 現行結合部品候補はNBK MJT-14-RD-4-6、4mm↔6mm、外径14mm、全長22mmです。候補Z位置z=57–79mm、モーター取付面z=81mmです。結合部の軸方向保持と実挿入長は未受入です。
- BSS1-20Cの止めねじはKHKが簡易固定と説明する方式です。校正有効なATG12CN-Sによる両方向0.070N·m指示の1軸保持試験がPASSするまで全量購入を保留します。計器へのアクセスと歯車保持具は未確保です。
- NEMA-8 #4411の約406mm 4芯リード線は、線径/端子適合、ドライバー位置、引出し/固定経路、ギアや軸との離隔が未確認です。配線と歯車を一つの包絡へモデル化するまでモーター/ケース/配線材の全量購入は保留します。
- CADは公称2D配置・外形包絡で、実歯形、公差、振れ、荷重、配線、板たわみを含みません。3.4Cは公式PDF/STEP差の安全側として15.50mm深さを置きましたが、個体受入とコネクター/ケーブル包絡は未完です。加工データへ直接使いません。

機械候補と受入ゲートの正本は[BSS1-20C軸支持候補](../03-mechanical/bss20_axis_support_candidate-2026-10-22.md)、[4歯車試験票](../03-mechanical/four-gear-manual-test.md)、[BSS20包絡モデル](../03-mechanical/bss20_clock_envelope_review.scad)、[歯車成立性ノート](../03-mechanical/gear-feasibility.md)です。旧DS1の軸支持不整合と旧候補の保留理由は[購入前設計監査](../02-architecture/purchase-readiness-audit-2026-10-21.md)に残しています。

## 5. 筐体・整備

| 項目 | 名目設計 |
| --- | --- |
| ケース外寸 | 270×205×145mm |
| 内寸 | 246×181×121mm、側板12mmを前提にした候補 |
| 材料 | 曲線部はウォールナット無垢材、広い化粧面はウォールナット突板候補 |
| 支持板 | 透明PC 8mm、252×187mmを2枚。側壁/上下壁へ各3mm入る捕捉溝の候補。溝は幅8.2mm、壁内側から深さ3.2mm。試験片PASSまで材料/溝加工は保留 |
| 前面保護 | 初号機評価材は透明PC呼び厚3mm（[ADR-0017](../../adr/0017-transparent-guard-material-candidate.md)）、周縁捕捉、着脱式押さえ縁。材料SKU、反射/傷、たわみ、保持、指到達は実物確認 |
| 前面保護板 | 前面内面をz=0、板内面候補z=-3。外形、押さえ縁、指到達は未受入 |
| 前面支持板A | z=7–15mm、中央Ø112mm開口。14個のØ8 H7候補ブッシュ座 |
| 歯車層A | BSS1-20Cのボスz=16–24mm、歯面z=24–30mm |
| 歯車層B | 歯面z=33–39mm、ボスz=39–47mm。A/B歯面間は名目3mm |
| 後面支持板B | z=48–56mm、中央120×120mm開口。14個のØ8 H7候補ブッシュ座 |
| 表示器 | 公式Drawingを反映しガラス前面z=44.50mm候補、円形外径Ø115mm、奥行包絡15.50mm（z=44.50…60.00）。後面支持板の120mm角開口を通す保守的な矩形すき間2.5mm/辺。外周穴はM4×4.00表記、75×78.5mmピッチ。B歯面終端z=39mmとの名目軸方向すき間5.50mm。取付キャリア/背面部品との適合と物理すき間は未受入 |
| 背面整備 | 背面板をねじ止めで外せる構成。支持板と表示器を背面から点検できる候補 |
| モーター | NBK継手z=57–79mm、NEMA-8取付面z=81mm、本体z=81–114mm、ケース内壁z=121mm。公称後方余裕7mm |

公称寸法は[BSS20包絡モデル](../03-mechanical/bss20_clock_envelope_review.scad)へ反映した候補です。画面をz=44.50mmへ置き、旧案の1mm軸方向すき間を5.50mmへ増やしました。正確な基板改版、外周穴の実仕様、保持キャリア、USB/SD挿抜、支持板たわみ/歯車振れ込みの最小すき間、モーター後方7mm、PC捕捉溝、圧入後内径は実物/試験片で受け入れるまで製作寸法ではありません。ウォールナット無垢材の曲線枠とウォールナット突板の広面材を使用し、木材の等級/木目/仕上げ/切出しは購入前に確定します。リポジトリの[概念参照JPG](../assets/forest-guardian-dialcanvas-concept-reference.jpg)は意匠方向の参照用で、旧概寸の注記を含み製作用輪郭ではありません。高解像度文字盤原画と利用条件はFG-038/OQ-10に残ります。

## 6. 電源とモーター保護

### 6.1 電源の流れ

```mermaid
flowchart TD
  A[USB-C PD 9V/3A] --> B[HUSB238 9V要求]
  B --> C[入力 3Aヒューズと分岐点]
  C --> D[モーター 1Aヒューズ→物理スイッチ→TMC2209]
  C --> E[Pololu #2851 5V]
  E --> F[5V主幹 4Aヒューズ]
  F --> G[TPS25810EVM 3A広告→3.4C]
  F --> H[LED 1Aヒューズ→物理スイッチ→暖色LED]
```

9Vのモーター戻りと5V/表示の戻りは、電源分岐点まで別配線とする。モーター相電流を表示器のGND配線やUSBケーブルへ流さない。ヒューズ値は一台試作の候補値で、導線・コネクター・突入・故障試験後に確定する。

| 電源経路 | 試作ベースライン | 保護/検証 |
| --- | --- | --- |
| ACアダプター | Anker 511 Charger (Nano 3, 30W) とUSB-C PDケーブル | 9V/3A PDOを持つ候補。HUSB238のPD契約を実測 |
| PDシンク | Adafruit HUSB238 #5807。9V固定要求、3A設定 | 契約失敗時は5V側へ安全に停止すること、極性・出力電圧を実測 |
| 9V入力 | 3Aヒューズ候補後に星形分岐 | ヒューズ定格/時間特性、入力電圧、全負荷電流を確認 |
| 5V変換 | Pololu D24V50F5 #2851、9V→5V | 公称typical continuous up to 5A、温度依存。5Aを筐体内連続許容量とはみなさない |
| 5V主幹 | 4Aヒューズ候補 | #2851、基板、端子、配線の定格に合わせて検証 |
| 表示USB-C source | TI TPS25810EVM-745、TPS25810 DFP、3A広告設定 | 5V入力。ICの電流制限は3A広告時typ.3.40Aだが、USB-C sinkへ3.4A引出しを許可する意味ではない。CC設定・動作・温度を確認 |
| 表示ケーブル | ELECOM MPA-XCCECSS03BK、C-C、0.3m | EVM sourceから3.4C USB TO UART入力。基板改版指定入力と電圧降下を測定 |
| モーター | 9V分岐→1Aヒューズ候補→NKK MN11SS1W01 SPST→TMC2209 VM | 旧M1 eFuseを使わない独立枝。スイッチOFFでVMを直接遮断 |
| モーター抑止 | ENNはactive-low。10kΩでENNをVIO/3.3Vへ外部プルアップ。GPIOは初期化時にENN HIGH。STEPは外部10kΩ pulldown候補 | reset/brownout/未接続/長押し停止を試験。実ドライバー基板の論理極性を確認 |
| VM過電圧 | SMBJ12A TVSをTMC2209 VM/GND近傍へ、ドライバー基板の既設コンデンサーと併用 | VRWM=12V、仕様上最大クランプ19.9V候補。回生エネルギーと実波形は未受入 |
| LED | 5V分岐→1Aヒューズ候補→独立SPST→FIT0836 330mm | 4W/m仕様値による最大1.32W/0.264Aの計算。電流、拡散、木部温度を測定 |

TPS25810EVM-745は評価用基板で、量産モジュールではない。TIガイド記載の3A広告ジャンパ設定を用い、実Type-Cケーブル使用時はCCテストジャンパを外す。評価基板そのものの取付、5V入力端子、ジャック、ジャンパ保持、入手性を確認する。設計上の意図はPololu #3411の手作業CC抵抗変更を避けること。

### 6.2 静的電力予算

次の値は候補仕様と仮定からの計算で、実測値ではない。

| 負荷/条件 | 計算 |
| --- | ---: |
| 表示sourceの広告上限 | 5V×3A = 15W |
| LED 330mm | 4W/m×0.330m = 1.32W、0.264A@5V |
| #2851の5V側合計上限 | 15W+1.32W = 16.32W、約3.264A |
| #2851入力側（効率85%仮定） | 約19.2W、約2.13A@9V |
| モーター巻線銅損（0.30A RMS/相、6.5Ω/相仮定） | 2×0.30²×6.5 = 約1.17W。ドライバー損失は別途 |
| 参考総負荷 | モーター枝の変換効率を仮に85%と置くと約20.6W、約2.29A@9V |
| 9V PD候補との参考差 | 27W−20.6W = 約6.4W (約24%) |

この余裕値は設計採否の証明ではない。表示器の実ピーク、無線送信、microSD、モーター電流波形、変換効率、起動電流、閉箱温度、PD再交渉を同時測定するまではFG-048をOPENとする。

## 7. 実機受入の定義

段階と暫定pass条件は[一台試作受入計画v0.21](../09-verification/prototype-acceptance-plan-v0.21.md)に定義する。

| ID | 実機で記録するもの | 完了条件 |
| --- | --- | --- |
| DR-02 | 3.4C現物改版、電源/USB/UART/SD/表示、各GPIOとEN | 一次資料と基板現物の対応表、全候補GPIOの未競合確認。ESP-IDFビルドのみでは完了しない |
| DR-03 | JPEG表示、エンコーダー、SD読取専用、選択NVS、針描画、SNTP/RTC | 起動/再起動、ネット断、時刻復旧、30fps最低/60fps目標の記録 |
| DR-04 | ギア嵌合、1.6rpm、逆回転、始動/再始動、連続運転、騒音/振動/温度 | 無通電手回しから段階実施し、負荷/停止時も噛合いと静音目標を満たす |
| DR-05 | PD 9V/3A、枝電流/電圧降下、短絡/過負荷、ヒューズ、TVS、閉箱温度 | 5V・9Vの定常/起動/異常記録。保護部品と配線の定格が測定値へ適合 |
| DR-06 | 前面ガード、支持板、保護、指到達防止、表示取付、端子/カード挿抜、前後整備 | 原本外観と実寸部品に整合する製作図、BOM、組立・検査順が同一改版で揃う |
| DR-07 | DR-01〜06証拠、未解決リスク、リリースレビュー | DR-02〜06がPASSし、別途の製作許可が記録されるまでHOLD |

## 8. 状態の読み方

要求の状態語は要求台帳と同じ意味で使う。

- `FIXED`: ユーザー要求または現行方針として固定。
- `PROVISIONAL`: 一台試作に使う候補値。測定で変更可能。
- `OPEN`: 決定または検証が残る。
- `REJECTED`: 現行範囲に採用しない。
- `SUPERSEDED`: 旧案として置換済み。

作業一覧の `DesignStatus` は設計文書の整備状態、`ValidationStatus` は根拠/受入状態を表す。`BASELINED` は候補設計が具体化され、次に検証できる状態を示す。実機の未検証項目を完了に読み替えない。

## 9. 参照資料

- Waveshare [3.4C公式製品/基板資料](https://docs.waveshare.com/ESP32-P4-WIFI6-Touch-LCD-XC)、[3.4C公式Drawing ZIP](https://files.waveshare.com/wiki/ESP32-P4-WIFI6-Touch-LCD-XC/ESP32-P4-WIFI6-TOUCH-LCD-3_4C.zip)、[公式回路図](https://files.waveshare.com/wiki/ESP32-P4-WIFI6-Touch-LCD-XC/ESP32-P4-WIFI6-Touch-LCD-XC-Schematic.pdf)
- TI [TPS25810EVM-745製品](https://www.ti.com/tool/TPS25810EVM-745)、[TPS25810EVM-745 User's Guide](https://www.ti.com/lit/pdf/slvuai0)
- Pololu [D24V50F5 #2851](https://www.pololu.com/product/2851)
- Adafruit [NEMA-8 #4411](https://www.adafruit.com/product/4411)、[TMC2209 #6121](https://www.adafruit.com/product/6121)、[HUSB238 #5807](https://www.adafruit.com/product/5807)、[DS3231 #3013](https://www.adafruit.com/product/3013)
- Analog Devices [TMC2209 data sheet](https://www.analog.com/media/en/technical-documentation/data-sheets/TMC2209_datasheet_rev1.09.pdf)
- Littelfuse [SMBJ12A](https://www.littelfuse.com/ja-jp/products/overvoltage-protection/tvs-diodes/surface-mount/smbj/smbj12a)
- 機構/取付候補: [KHK DS歯車](https://khkgears.net/pdf/ds.pdf)、[OILES #80](https://www.oiles.co.jp/en/products/bearing/assets/oiles-80_en.pdf)、[NBK MJT継手](https://www.nbk1560.com/products/coupling/couplicon/jaw_type/MJT-RD/)
