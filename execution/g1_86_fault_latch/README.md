# G1-86 — 実配線されたSET優先の独立NOR故障保持サブ回路

元G1-85の374実ピンを変更せず、**SN74LVC2G02DCUR (dual NOR 8pin)、SN74LVC1G04DBVR (INV 5pin)、SN74LVC1G08DBVR (AND 5pin)** のTI実端子を各々登録。新規3×100nF、クリア要求用J18コネクタ、10kプルダウン×2も追加。合計**404ピン・112部品・110ネット**。KiCad9 XML端子・ネット完全一致をCI必須にする。

既存 `B77__QUAL_CLR_N`（POR/STOP/WDI由来）をINV U21.pin2とAND U22.pin2へ**現実の図面上で接続**する。TRIP_ASSERT=NOT QUAL_CLR_N、RESET_EFFECTIVE=J18.CLEAR_REQUEST AND QUAL_CLR_N。デュアルNORの実ピンは U20.[1,2→7] = NOR(RESET_EFFECTIVE,QBAR)、U20.[5,6→3] = NOR(TRIP_ASSERT,Q)。帰還線 Qbar=U20.3→U20.2、FAULT_Q=U20.7→U20.6 としてSET優先の非同期保持回路を作成。解除要求は10kΩでGND初期固定、実解除回路**未接続**、FAULT_Qは10kΩプルダウン付きステータス専用（eFuse ENやOEに配線しない）。

**重要な未解決：** CLEAR_REQUESTを押したまま異常が解消するとFAULTが自動解除され得る。これを否定試験で再現しており、安全回路としては**リリース→新規押下を保証する物理ワンショット/エッジ回路が必須**。PG（モーター起動後）と独立5Vレール異常はまだこのSETへ合流していない。QUAL_CLR_N stuck HIGH、電源断立上り・競合・グリッチ・ゲート間伝搬、NC STOP短絡も未検証。実footprint、KiCad完全ERC、基板DRC/HILは未。**従ってG1-05/G1-06 WORKINGのまま**。

FFの理想真理値表と100,000ランダム遷移をPythonで実行、ただしアナログ/SPICE/実機でのフェイルセーフは証明しない。製造承認0/6、19/48、SW11/14、U7.1 EN=10k GND、28相/OE=HIGH固定、main/発注/加工/PCB製造/通電/書込み禁止。

TI datasheets: https://www.ti.com/lit/ds/symlink/sn74lvc2g02.pdf ・ https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf ・ https://www.ti.com/lit/ds/symlink/sn74lvc1g08.pdf

## G1-86 NC端子のKiCad本体照合是正

初回KiCad9実CLIでは、メーカー指定のU21.1 = NCを電気ネットB86__INV_NCにつながる配線として表記すると、KiCad native XMLは `unconnected-(U21-NC-Pad1)` として返した。**NCピンを導通させるよう見せかけない**ため、その1端子の仮配線・ラベルを外して正規KiCad `no_connect` をピン先端に置き、KiCadが実際に出力する未接続ネットを端子マップに登録した。旧374端子の配線は不変。

追加した9部品の行がA0用紙から下にはみ出していたため、回路図を**Userカスタム1200×1000mm**へ変更した（製造用型紙ではない）。XML全404端子照合、no-connect1個、実線403本、ラベル403個をCIで検証。これで「KiCad NCの扱いを弱いpin typeに偽装してPASS」とはしない。
