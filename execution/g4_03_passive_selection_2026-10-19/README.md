# G4-03 — TPS259474L 周辺受動部品の型番選定記録

**状態:** 部品候補選定と回路要求との机上照合を完了。G4-03のレビュー範囲のみ。基板BOM・回路安全承認・製造リリースではない。
**基準回路:** execution/g1_85_efuse_analog/forest_guardian_g1_85_analog_review.kicad_sch / G1-85
**部品台帳:** passive_bom.csv

## 選定

5部品すべてについてメーカー型番、電気定格、公称寸法を記録した。抵抗は Panasonic ERJ-3EKF 精密厚膜 0603、コンデンサは Murata GRM 0603 C0G/NP0 系列とした。各型番の一次資料URLは台帳に記載。型番は発注可能性を追跡する候補であり、在庫・価格・代替品・購入承認を意味しない。

| Ref | 用途 | 候補型番 | 公称条件 |
|---|---|---|---|
| R50 | OVLO上側 | Panasonic ERJ3EKF4702V | 47 kΩ、±1%、0.1 W、0603 |
| R51 | OVLO下側 | Panasonic ERJ3EKF1202V | 12 kΩ、±1%、0.1 W、0603 |
| R52 | ILM設定 | Panasonic ERJ3EKF2211V | 2.21 kΩ、±1%、0.1 W、0603 |
| C14 | dVdt | Murata GRM1885C1H332JA01D | 3.3 nF、±5%、50 Vdc、C0G、0603 |
| C15 | ITIMER | Murata GRM1885C1H222JA01D | 2.2 nF、±5%、50 Vdc、C0G、0603 |

Panasonic公式仕様は該当型番について抵抗値、±1%、0603 (1.6 × 0.8 mm)、0.1 Wを示す。Murata型番の製品資料と公式SimSurfingは部品系列・値・温度特性の照合元。実装ランドは正式PCB設計時にメーカー推奨寸法とKiCadフットプリントを再確認する。

## 回路値の机上照合（安全承認ではない）

TI TPS25947 Rev. C の式とG1-85の暫定値を使い、再計算可能な単位テストを添付した。

- OVLO rising の公称値: 1.20 × (47 kΩ + 12 kΩ) / 12 kΩ = 5.900 V。TIの1.183–1.223 V閾値と抵抗±1%だけを含む静的範囲は約5.725–6.111 V。入力漏れ、温度、電源変動等は含めない。
- ILM: 3334 / 2210 = 1.509 A は代表式による典型試算。保証最小電流制限値はここから決められず、未確定。7軸負荷が適合するとは主張しない。
- dVdt: 2000 / 3300 = 0.606 V/ms、5 Vでの理想化立上り概算は約8.25 ms。出力総容量、突入電流、損失、実測波形は未確認。
- ITIMER: 1.51 V × 2.2 nF / 1.8 µA = 1.846 ms は代表値のみの概算。最悪値・実短絡・温度動作は未評価。

## 制約と保留

- G1-85回路図はレビュー記号のまま。5部品とも in_bom=no / on_board=no / フットプリント空欄を維持する。
- この選定で回路値自体を変更していない。TIの式は候補値の照合にだけ使い、許容誤差全体で必要機能が成立する証明には使わない。
- eFuse ILMの保証最小値、7モーターとファンの実負荷・ピーク、熱、入力/COUT、OVLO実測、基板配線/クリアランス、実機故障試験は未完了。
- 購入、基板製造、加工、書込み、モーター通電は未承認。M1 eFuse ENはGND保持のまま。安全リリースは6ゲート中0。

## 検証

python3 execution/g4_03_passive_selection_2026-10-19/check_contract.py はCSVの5参照と値・型番・定格・出典ドメイン、G1-85回路図との公称値一致、式の計算範囲、非リリース条件を検証する。PASSは選定記録の一貫性だけを示し、KiCad ERC/DRCや実機安全性を示さない。

## 一次資料

- TI TPS25947 datasheet Rev. C (May 2026): https://www.ti.com/lit/ds/symlink/tps25947.pdf （OVLO、ILM、dVdt、ITIMERの式と条件）
- Panasonic ERJ3EKF4702V: https://industrial.panasonic.com/jp/products/pt/general-purpose-chip-resistors/models/ERJ3EKF4702V
- Panasonic ERJ3EKF1202V: https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ3EKF1202V
- Panasonic ERJ3EKF2211V: https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ3EKF2211V
- Murata GRM1885C1H332JA01D: https://www.murata.com/en-global/products/productdetail?partno=GRM1885C1H332JA01D
- Murata GRM1885C1H222JA01D: https://www.murata.com/en-global/products/productdetail?partno=GRM1885C1H222JA01D
