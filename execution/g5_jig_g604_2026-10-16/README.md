# G5接合：製品外の位置決め治具・4接合部試験片・製法比較 / G6-04原本側帯

- 元D7 `assembly.json` SHA256 `20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f`、**1,774 source solids**をローカルで再読込・再ハッシュして実資料を生成。旧5部品はそのまま維持。**金属部品に新しいM2頭や穴を増設しない。**
- **8個の実部品下面接触点**を原本13部位の占有範囲から選出。外部加工治具の参考寸法は270×190×8mm板、G5全体でD7のZ116を原点にし、治具支柱高さ **0mm 2か所/11mm 3か所/14mm 3か所**。外部治具は完成品内部に入らず、他6軸の55mmサービス予約へ干渉しない。組立治具自体の精度・固定方式は未検証。
- **内部4接合面9/9/18/18mm²**に対して部品別試験片を設定。別にG5ガイド2接続と12mm木部アンカー4接続が必要。製品内で一般的M2有頭ネジを3mm部材へ直接使用する案は**不適合**。精密溶接、ろう付け、一体CNC、板金曲げ再設計、非構造樹脂試験片の **5製法を価格捏造なく比較**。いずれも調達・製造承認なし。
- フレーム質量 **153.546g**（鋼材仮定）を荷重に含め、搭載質量4条件×加速度3条件×均等分担2条件 = **24行の参考計算**。力を9mm²で割った値は局所溶接強度、曲げ剥離、疲労寿命を保証しない。
- **G6-04**：実80部品160面の資料を使って23種を原本の外周・内穴周長まで計算、**14一定断面/9段付き断面**。木製ベゼルの前後4ペアがZ1で接する原本面積 **810/567/567/810mm²**。紙モックアップの糊代5mm/ピッチ30mmは構想値に留まり、製品用接着剤、接着層厚み、剥離試験は未承認。G6-04はOPEN。
- **ユーザー成果物** `Forest_Guardian_G5_Jig_G6-04_And_Fan_Engineering_2026-10-16.zip`（**49ファイル**, SHA256 `75b75b75a3a0a209e8d81a087346ebd4a7dd86caea735490dc3321302aecc17b`）には完全な原本80部品の表裏形状資料コピー、DXF編集用治具、1:1 A3 PDF 2部×2頁、再生成コード、SHA256全ファイル検査スクリプト、23部品CSV、4接触面CSV、試験/RFQ表を収録。既存全履歴 `Forest_Guardian_Integrated_Handoff_G5_Jig_G6-04_2026-10-16.zip` SHA256 `22decdbf086676db66280eb525b50b2839b71ddf5323fab41b58ef9a569b40e8`。
- GitHub側の[設計契約](design_contract.json)と[独立8座面判定](check_contract.py)は**実際の面積CSVを再読込するものではない**。元65MB D7からの再計算とPDF/DXF/全出典の確認は配布ZIP内のソース＋独立検証で実行済み。
- **G3-04/G3-05 WORKING、G6-04 OPEN。19/48 DONE_SCOPE、製造0/6、ソフト11/14、モーターeFuse EN LOW。** 実加工/発注/通電/フラッシュ/main変更は不可。

## 接合方式ごとの実体試験片も追加（材料試験ではない）

旧金属部品の**9mm²接合J1/J2（Y突合せ）、18mm²接合J3（Y突合せ）、18mm²接合J4（Z突合せ）**をそれぞれ独立した参照用3D形状へ変換。3形式×未接合のA/B片＝**水密STL6個**、OpenSCAD各6個、A3比較図1頁、CSV試験計画を配布ZIP内 `TEST_COUPONS_NOT_FOR_PRODUCTION` に保管。3×3mmまたは3×6mm断面・各片30mmで、グリップ・熱影響部・溶接材料・接合強度・試験機適合は未設計。製造ゲート**0/6**を維持。

## G3-06 仮想30mmファンの名目3D再配置候補（未承認）

D7全1,774ソリッド、7軸50×41保守矩形、G5支持フレームの既存13部位に対して仮想30×30×10mmファンのZ125..135配置を網羅探索。元D7固定部品との投影距離と予約領域の最小3mmを満たす **(95,90)/(95,95)/(95,100)** の3代替座標を記録。最初の格子点評価では多数の候補を棄却、3mm保守予約・原本固定投影の二段目で**3件のみ残す**。3ファン同時設置を意味しない。

各30×30mm背板原本領域は木480mm²＋既存空洞420mm²で、換気穴・ブラケット・ファン固定が未設計。**旧ファン109mAは分岐100mAを9mA超えるため、実物選定と給電回路再設計までは稼働不可**。DXF編集用配置図、A3原寸図、二段階原本走査CSV/再生成コードをZIPに収録。

G3-06 OPEN、製造0/6、SW11/14、7軸交換A案は不変。GHの静的検証は元65MB D7モデルを再走査せず、結果の出典と禁止条件の整合性のみを確認。


## Previous 30mm FAN 3 body-clear locations corrected

Legacy 30mm fan candidates at (95,90), (95,95), (95,100) were ONLY nominal 3mm body-clear checks. They are NOT exhaust installation designs. A new actual original-D7 audit (1774 solids, SHA256 20ee6d8c001ee16d64e47edb5456eff3bc39f3390a85dd94b69b7eb1504d878f) re-read all 9 contiguous BACK_WOOD XY material slices from Z137 to 145mm.

The manufacturer's actual outlet diameter is 29.3mm (nominal 674.256mm²). Source nine-layer through-clear projections are **1.129 / 3.006 / 1.129 mm²**, or **0.167 / 0.446 / 0.167%**. Five other prior body-clear sites have 0mm². All eight original no-cut locations are **REJECTED AS UNMODIFIED-BACKWOOD EXHAUST**, not a ban on redesigned side-grille or certified new backwood vent.

See ../fan_full_thickness_2026-10-16/README.md . The original placement candidate check is NOT a vent engineering acceptance.
