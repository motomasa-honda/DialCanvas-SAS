# G1-87 — 「解除押しっぱなしで故障復帰」が起動解除に化ける欠陥を物理ゲートで修正

## 今回修正した本質的問題
前版G1-86では、故障ラッチのRESETに使用する **CLEAR_REQUEST** に「一度離した」という履歴が無かったため、押したままFAULT→正常に戻ると勝手にFAULT保持が消える。また解除コネクタJ18は**CLEAR_REQUESTとGNDの間**、抵抗R53も10kΩでGNDへ引くため、通常のNOスイッチ操作でHIGHにできない配線不具合もあった。

### 修正した旧404端子は厳密に4か所
- J18.1：B86__CLEAR_REQUEST→**B87__CLEAR_SWITCH_RAW**
- J18.2：GND→**3V3_AON**（NOスイッチでHIGH）
- R53.1：B86__CLEAR_REQUEST→**B87__CLEAR_SWITCH_RAW**（10kΩ pulldown、切断時はLOW）
- U22.1：B86__CLEAR_REQUEST→**B87__CLEAR_QUALIFIED**（直結禁止）

他の400物理端子は番号もネットも変えず、12部品＋42端子を追加。**計446端子・124部品・119ネット**。

### 独立 release-first latch（追加したTI部品の実ピン）
- U27 **SN74LVC1G17DBVR Schmitt buffer**: CLEAR_SWITCH_RAW→10kΩ R55→CLEAR_FILTERED、1µF C19→GND、U27.2入力、U27.4→CLEAR_DEBOUNCED。タイムスケール約10ms（候補、閾値・コンタクトバウンス実測未）。
- U25 **SN74LVC1G04DBVR**: U25.2 CLEAR_DEBOUNCED、U25.4 CLEAR_NOT。
- U26 **SN74LVC1G08DBVR**: U26.1 QUAL_CLR_N、U26.2 CLEAR_NOT、U26.4 RELEASE_SET。
- U23 **SN74LVC2G02DCUR**: U23.1 TRIP_ASSERT、U23.2 RELEASE_QBAR、U23.7 RELEASE_SEEN；U23.5 RELEASE_SET、U23.6 RELEASE_SEEN、U23.3 RELEASE_QBAR。**tripが立ったらrelease_seen=0**で保持、故障後に入力LOWを観測しない限り立ち上がらない。
- U24 **SN74LVC1G08DBVR**: U24.1 CLEAR_DEBOUNCED、U24.2 RELEASE_SEEN、U24.4 CLEAR_QUALIFIED。既存U22がさらにQUAL_CLR_NとANDして故障保持ラッチRESET_EFFECTIVEへ送る。FAULT_Qは依然モータEN/OEと非接続。
- 新IC5個にはそれぞれ100nFデカップリング (C20–24)、ハード指定NC端子U25.1/U27.1はKiCad本物の no_connect。

`controller.py`で回路の整定後ブールモデルを構築し、全16組合せとランダム10万遷移、再アーム押しっぱなし→FAULT→復帰、解除後に押す、ボタン離さず故障を繰り返す等を自動検証。KiCad9ネイティブXMLの446端子・124記号・119ネット1対1一致がCIの合否。**本物のアナロググリッチ・メタステーブル・電源再投入時の非同期ラッチ状態・シュミット入力閾値・瞬断故障を証明するものではない**。

残る本当に重要な設計：PG立上げ後・独立5V監視からFAULTトリップへの物理合流、物理起動期限タイマー、AON喪失と3V3再投入時のcold POR、QUAL_CLR_N stuck-high・STOP短絡診断、承認済み正規メーカーfootprintとERC全クリア・PCB DRC・HIL。U7.1 ENはGNDへ10kΩ、28相/OEはHIGHで電源無効のまま。**G1-05/06 WORKING、19/48、製造0/6**、Draft PR #2でmainは変更禁止、購買・加工・製造・通電は行わない。

TI一次資料： https://www.ti.com/lit/ds/symlink/sn74lvc2g02.pdf ・ https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf ・ https://www.ti.com/lit/ds/symlink/sn74lvc1g08.pdf ・ https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf
