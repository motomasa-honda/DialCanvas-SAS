# ADR-0007: 左下へ寄せた28歯車の一台用候補

- 登録日：2026-10-20
- 状態：現行の寸法入り候補。製作図・購買確定・実機受入ではない。
- 対象：非量産の個人製作一台。
- 置換：[ADR-0006](0006-dimensioned-one-off-37-gear-baseline.md)の37歯車・外周枠状配置を置換する。表示、静かな単一駆動、滑らかな画面針、microSD文字盤、既製品優先の上位要求は維持する。

## 背景

ADR-0006の37歯車案は市販歯車・支持数・電源まで寸法を揃えたが、平面図は四辺を囲む整然とした枠に見えた。これはユーザーが拒否した見え方に近い。前面支持板を円形開口に変えると、3.4型表示面の外周へ軸を置きつつ、背面支持板は115×115mmの表示基板用開口を保てる。二層の歯車列を左側・下側へ寄せ、右上に意図的な空間を残す。

## 決定

1. **外形・表示**：ケース基準は270×205×145mm、内寸246×181×121mm。Waveshare ESP32-P4-WIFI6-Touch-LCD-3.4C（SKU31523）を3.4型800×800円形IPS候補とする。基板改版、端子、奥行き、画質、消費電力は現物確認を残す。
2. **歯車と配置**：KHK DS1 M1 POM歯車を28個使う。5mm穴の18/20/24/28Tに限定し、前列Aと後列Bを各14個にする。二つの開放列は左側と下側に偏らせ、均等なリング/外周枠を作らない。A00=20TとB00=18Tは同じ複合軸。残りの投影重なり15組は別Z面に分け、歯面は接触させない。

   | 型番 | 合計 | 前列A | 後列B |
   |---|---:|---:|---:|
   | DS1-18 | 11 | 7 | 4 |
   | DS1-20 | 10 | 4 | 6 |
   | DS1-24 | 3 | 1 | 2 |
   | DS1-28 | 4 | 2 | 2 |
   | **合計** | **28** | **14** | **14** |

3. **支持板**：透明PC 8mm厚、252×187mmを2枚。前列Aの支持板は中央Ø112mmの円形開口と14個のブッシュ座、後列Bは120×120mm角開口と14個のブッシュ座を持つ候補。外周の捕捉溝は深さ3mm・幅8.2mm。OILES座のØ7 H7は参考寸法で、板材への適合は試験片で決める。
4. **軸・ブッシュ**：MISUMI h7の5×28mm軸を26本、5×56mm共有軸を1本。OILES #80 80B-0508（内径5/外径7/長さ8mm）を28個。各平面14軸を一つずつ支持し、複合軸だけ前後の二支持点を使う。KHK成形穴の圧入とPCブッシュ圧入は未受入。
5. **駆動**：Adafruit NEMA-8 #4411とTMC2209 #6121を一台候補とする。複合軸1.6rpmを目標にした幾何上の回転周期はA列33.75〜52.5秒、B列37.5〜58.33秒。静音・始動トルク・脱調・温度は試験前の主張にしない。
6. **幾何チェック**：[配置生成器](../docs/03-mechanical/generate_irregular_layered_gear_layout_svg.py)の名目計算は、異層投影重なり15組、異層の別軸中心間最小7.85mm、同層非隣接歯車の最小外周すき間1.83mm、ケース縁最小余白5.42mm、有効表示面との最小すき間12.24mm、支持開口からブッシュ座までの最小ウェブ4.50mm、隣接M1中心距離誤差最大0.0027mm。カタログ公称値による2D検査で、歯当たり・軸公差・板変形・Z方向の実測ではない。
7. **既製品と費用**：表示、歯車、軸、ブッシュ、カラー、カップリング、モーター、ドライバー、USB-C PD受電、DC/DC、LED、操作部は市販品を優先する。既知価格は歯車28個で税別¥7,360、ブッシュ28個で¥1,428、合計¥8,788（送料別）。軸・カラー・電装・木工は含まない。
8. **電源・表示ソフト**：USB-C PDから固定9Vを要求し、モーター枝と5V表示/照明枝へ分ける既製構成を候補とする。基板メーカーBSP/ESP-IDF/LVGL 9/JPEGデコーダーを使い、microSD画像一覧・時計・操作・連続針描画アプリは本機用に実装する。文字盤は800×800 JPEGをmicroSDから切り替える。

## 図面と未受入項目

- [全体平面図PNG](../docs/03-mechanical/irregular_layered_gear_layout_preview.png)、[平面図SVG](../docs/03-mechanical/irregular_layered_gear_layout.svg)
- [軸方向断面SVG](../docs/03-mechanical/layered_gear_axial_section.svg)
- [前列A支持板SVG](../docs/03-mechanical/gear_support_plate_A.svg)、[後列B支持板SVG](../docs/03-mechanical/gear_support_plate_B.svg)
- [軸・ブッシュ座標CSV](../docs/03-mechanical/gear_axis_schedule.csv)

図面は座標と配置関係のレビュー用で、加工に渡す完成図ではない。未受入項目は、実表示基板の高さ/端子/SDアクセス、歯車圧入、支持板ウェブとOILES嵌合、軸端/カラー保持、全28歯車の始動トルクと静音、温度、USB-PD契約、文字盤JPEG/RTC動作、前面ガード、木箱の捕捉溝と整備性である。

実行台帳や製造ゲートの状態は変更しない。M1 eFuse EN LOWを維持し、購入、加工、モーター通電、ファーム書込み、mainマージは行わない。

## 一次資料

- [Waveshare公式資料](https://docs.waveshare.com/ESP32-P4-WIFI6-Touch-LCD-XC) / [回路図](https://files.waveshare.com/wiki/ESP32-P4-WIFI6-Touch-LCD-XC/ESP32-P4-WIFI6-Touch-LCD-XC-Schematic.pdf)
- [KHK DS1寸法](https://khkgears.net/pdf/ds.pdf) / [2025-12-01適用価格表](https://www.khkgears.co.jp/files/libs/5368/202511041428192234.pdf)
- [OILES #80寸法](https://www.oiles.co.jp/en/products/bearing/assets/oiles-80_en.pdf) / [組付要領](https://www.oiles.co.jp/products/bearing/manual/exchange/)
- [MISUMI h7軸](https://jp.misumi-ec.com/vona2/detail/221000746923/) / [KANAカラー](https://www.kana.co.jp/e-catalog/pdf/DOLS2020_single.pdf)
- [NEMA-8 #4411](https://www.adafruit.com/product/4411) / [TMC2209 #6121](https://www.adafruit.com/product/6121) / [HUSB238 #5807](https://www.adafruit.com/product/5807)
