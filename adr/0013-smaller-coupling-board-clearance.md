# ADR-0013: 3.4C表示基板との余裕を確保する小径軸継手

- 日付: 2026-10-21
- 状態: **SUPERSEDED by ADR-0015。4mm↔5mm継手と5mm軸は履歴のみ。現行はMJT-14-RD-4-6/6mm軸候補で、現物受入・購入・加工承認ではない**
- 関連: [ADR-0008](0008-one-off-cots-part-selection.md)、[未決定事項](../docs/01-requirements/open-questions.md)、[28歯車配置](../docs/03-mechanical/gear-feasibility.md)

## 背景

CAD包絡モデルで、現行候補のNBK MJT-20-RD-4-5（外径20mm）と3.4C基板の公称115×115mmの平面包絡を重ねた。共有軸A00/B00から基板外形までの最小距離は10.5mmで、継手半径を引くと公称0.5mmしか余裕がない。端子・部品・改版差を考えるには狭すぎる。

NBKには同じ4mm↔5mm穴のMJT-14-RD-4-5があり、軸座標を変えずに継手半径を3mm小さくできる。メーカー/販売店の掲載寸法、価格、軸挿入推奨を確認した。

## 判断

1. 現行の一台用候補継手を**NBK MJT-14-RD-4-5**へ更新する。4mm↔5mm穴、外径14mm、全長22mm、各ハブ長L=7mm、M3止めねじ。MonotaROは¥2,088税込、5日以内出荷・返品不可と表示。旧サイズ20の掲載価格¥2,528から¥440下がる。
2. 5×60mm共通軸ピンを58.5mmに仕上げ、前端z=-3.5mm/後端z=55mmを維持する。継手をz=48–70mmへ置き、5mm軸を推奨ハブ長の7mm挿入する。
3. NEMA-8の4mm軸突出は約9mm。継手後端z=70mmに対しモーター取付面をz=72mmとし、2mmの露出軸区間を設けて、モーター軸の継手挿入も7mmにする。モーター本体をz=72–105mmに配置し、背面内壁z=121mmまでの名目余裕を16mmとする。
4. 名目CADで、外径14mmの継手と3.4C公称基板外形の平面すき間を3.5mm以上とする静的チェックを追加する。CSV座標・寸法変更時に配置生成器で再評価する。
5. FG-026はOPENのままにする。軸止めねじの保持、許容偏心、軸端の実挿入、振動/騒音、始動余力、温度は現物試験が必要。

## 影響と未解決事項

- 歯車軸座標と支持板穴座標は動かさない。カップリングを小さくし、部品費と基板際の名目干渉を同時に下げる。
- 円建て既知部品の候補合計は約¥73,203（税込換算）へ更新する。輸入部品US$73.31、送料、加工/工具は別。価格は調査時点の表示。
- 3.5mmは公称基板外形との名目平面すき間で、基板上部品、USB/SD端子、実装改版、軸振れを含まない。現物の立体クリアランス受入は残る。
- M1 eFuse EN LOW、購買/加工/通電/フラッシュ/main変更の既存保留は維持する。このADRは物理作業を開始する許可ではない。

## 根拠

- [NBK MJT-14-RD-4-5 掲載](https://www.nbk1560.com/products/coupling/couplicon/jaw_type/MJT-RD/MJT-14-RD/MJT-14-RD-4-5/)
- [MonotaRO 型番/寸法/価格](https://www.monotaro.com/p/3751/1844/)
- [NBK 軸挿入・取付説明](https://www.nbk1560.com/resources/coupling/article/couplicon-maintenance/)
- [包絡/断面レビュー](../docs/03-mechanical/cots_clock_envelope_review.md)
- [調達候補表](../docs/02-architecture/unselected-parts-procurement-plan-2026-10-21.md)
