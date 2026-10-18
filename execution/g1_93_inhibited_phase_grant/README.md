# G1-93 — PG/独立5V正常化後の相出力許可を実配線（起動禁止維持）

## 従来の未接続領域を閉じる
G1-92でeFuse ENまでの正常時起動許可経路を接続した一方、28相バッファの全/OE端子は異常側HIGH固定だった。本版は**実際のU34.B遮断入力へQ2のドレインを配線**し、RUN後かつPGと独立5Vが整った場合だけの相出力許可候補を生成する。

U42 TI TPS3808G01DBVR：既存U28.4のB88__PG_AND_RAIL_OK（実eFuse PG×独立5V supervisor）をR69=60.4kΩ/R70=10kΩでSENSE入力へ分圧。MR=3V3_AON、CTは本物KiCad no_connect、RESET_NはR71=100kΩ pull-up。CT openでメーカー公称約20ms安定後にRESET_NがHIGHとなる。**20msは公称値であり、20ms以上の厳格な連続保証ではない。**

U43 TI SN74LVC1G08：U12.5 RUN_Q（2回のHBエッジを通過した実ラッチ）AND U41.4 START_GRANT。U44 TI SN74LVC1G08：RUN_AND_START AND U42.RESET_N → B93__PHASE_GRANT_LOGIC。

Q2 Diodes DMN2056U G1/S2/D3（既存Q1と同じ実ピン）：DRAINは現U34.2 とR61.1のB90__OE_DISABLE_NOT_RELEASEDへ実配線。U34はCUT_REQUEST_ORと/OE_DISABLEをORして出力するため、今後の条件付き運転許可の接続先になる。実際のバッファU15-U18の8本/OEと28相へつながっている。

ただし**ここではQ2を意図的にONにできない**。U44.4→R72 68kΩ→B93__PHASE_LIMIT_STAGE→R73 68kΩ→Q2 GATE、さらにR74=1kΩでGNDへ固定。3.6V最高・抵抗±1%、R72/R73のどちらか一方が短絡してもゲート最大約0.053Vで、少なくともDS38480のVGS(th)最小0.4V@25℃を十分に下回る計算。全温度でのトランジスタOFF保証・単一故障耐性は別途試験必須。元R61 10kΩ→3V3 pullup、U34/OEすべて無効を維持。

ソース回路G1-92の579端子は完全保持し、新39端子・14部品。全618端子/182部品の実KiCad9 XML/SVG/ERCをCIで比較、静的条件と実回路構成の一致を要求する。

## G1-05/G1-06の残る未完了条件
R66/R68による実eFuse ENへの起動禁止、R72/R73/R74によるQ2/OE禁止は**設計レビューの電気的インターロック**であって正式通電許可ではない。次は3V3起動・故障時の全電圧条件、PG/5Vの継続時間のワースト値、NC STOP溶着短絡診断、WDI、eFuse/バッファのオフ時残留と逆給電、メーカー正式footprint、ERC19件解消/DRC、物理HILを通す。G1-05/06はWORKINGのまま、20/48と製造ゲート0/6を不変。発注/製造/通電/フラッシュ/mainマージは禁止。

一次資料: https://www.ti.com/lit/ds/symlink/tps3808.pdf ; https://www.ti.com/lit/ds/symlink/sn74lvc1g08.pdf ; https://www.diodes.com/datasheet/download/DMN2056U.pdf
