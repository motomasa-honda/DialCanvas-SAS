# G1-80 — 起動前後でPGを分離する故障保持・電源遮断の形式仕様

Status: **REVIEW MODEL ONLY**. G1-05/06 remain WORKING; G1-07 OPEN; official 19/48 scoped completions, 0/6 manufacturing gates, SW11/14. **There is NO new physical implementation of the rail-enable latch, timer, comparator, eFuse connection or 28-phase enable.**

## 今回解決した設計上の矛盾

既存G1-77ではU7.1 ENは10kΩ経由GND、モーターレール5V_MOTORはOFF、U7.3 PGはオープンドレイン+プルアップである。**PG=HIGHを起動前から必須にするとモーターレールが永遠に立ち上がらないデッドロックが発生する。逆にPG=HIGHだけで電圧正常と判断すると電源OFF中のプルアップを誤認する危険がある。**

採用する論理要求（未製作）：
1. 起動前は eFuse PGとモーターレールを正常条件に**使わない**。監視系(3V3 AON)、raw入力、独立STOP、独立WDI、fresh release→press が成立した場合だけ **仮想** rail_enable許可を発行。
2. STARTING中はレール起動を限定時間だけ許可するが、**28相ドライバー出力は停止**。PGとPGとは別系統の5V_MOTOR物理しきい値監視が同時に所定安定期間成立した場合だけRUN移行。
3. 起動期限超過はFAULTへラッチ、運転中のPG/5V_MOTORセンス消失または独立STOP/WDI/raw異常は即座にFAULTへ遷移。押しっぱなしボタンは復帰に使えず、一度離してから押す必要がある。
4. 3V3 AONが一度失われた場合はモデルを WAIT_RELEASE に初期化し、RUN復帰は禁止。実物でのアナログPOR競合は未検証。
5. STARTING仮想許可を**既存U7.ENへ配線しない**。物理安全IC、ラッチおよび独立タイマーを実装してERC/実波形試験を通すまで接続禁止。

### 状態と仮想出力

| 状態 | 仮想rail_enable | 仮想phase_enable | 遷移 |
|---|---|---|---|
| WAIT_RELEASE | 0 | 0 | 健全かつボタン解放を観測→READY |
| READY | 0 | 0 | 新規ボタン押下→STARTING |
| STARTING | 1 (健全時だけ) | 0 | PG∧独立rail_validが連続成立→RUN、期限超過→FAULT |
| RUN | 1 (健全時だけ) | 1 (PG∧rail_valid時だけ) | STOP/WDI/raw/PG/railが欠ければFAULT |
| FAULT | 0 | 0 | 故障解消してボタンを一度解放→WAIT_RELEASE |

**時間500ms / 20msはテスト例であり、実部品選定値・安全保証値ではない。** PythonモデルはCPU側の制御案であって、独立したハードウェア遮断ではない。モデル上の出力を実GPIO接続/制御に用いない。

### 既存GitHub物理台帳への逆参照

- G1-77 (140 actual pads /39 nets): U7.1=R_EN_PD.1=U7_EN_CLAMPED_DISABLED, U_ARM.5=ARM_LATCH_Q_ISOLATED, U7.3=EFUSE_PG_OD, U7.4=PGTH_SENSE, U7.5=5V_RAW, U7.6=5V_MOTOR.
- G1-78 (208 actual pads /63 nets): 4× U_BUF OE pins1,19=PHASE_OE_N_FIXED_HIGH, 28× output-resistors GND. The physical rail gate and OE drive are **NOT CONNECTED**.
- G1-80 does not alter either original pin netlist. Both native KiCad originals remain in previously reported ZIP, not included here; KiCad ERC/DRC **NOT run**.

### 自動検証と明確な限界

- 14 Python unittest: 起動中PG LOWの非デッドロック、安定要求、期限超過ラッチ、運転中5種類の異常、保持ボタン、電源再投入、全状態×128入力×4サンプリング幅 = 2,560単段入力の出力禁止不変条件、シード固定50,000ランダム遷移。
- net_guard: 140+208元物理端子の一意登録、7×4出力禁止、eFuse ENの接地保持。登録データを静的検査するのみ。
- **明示的に未解決**：PG+独立rail_validが両方HIGH固着するとモデルはRUNを誤許可できる。独立の正常性診断、PGTH閾値/電圧分圧、WDI無効化設定、単一NC STOP溶着、ESD、反転/電圧喪失時のeFuse EN、OEの全電源シーケンスはハードウェアで未実証。

### 次のG1-81に必要な現物設計証拠

1. 実装部品の物理ラッチ方式＋電源断の初期値。独立タイマー、独立しきい値検出、Stop二経路の**実ピン配線**を作る。
2. PGTH(VOUT vs VIN) の有効条件、TPS25947型番サフィックス、全アナログ閾値のメーカー資料を比較し、**逆給電/過電圧**まで包絡。
3. 正式KiCad9 schematicをGitHubにソース含め再現可能な形で追加、ERC実行、部品footprint/基板設計前DRC準備。
4. 実モジュールの入力LOW/VIL、相ドライバー28本の不定状態、OE/ENの電源OFF時挙動、2系統固着・単一STOP溶着を実物HILで故障注入。
5. メーカー型番/閾値と配線のレビュー完了まで製造承認 **0/6**、全軸OFF、mainマージ禁止を守る。

一次資料：TI TPS25947 https://www.ti.com/lit/ds/symlink/tps25947.pdf ; TI TPS3808 https://www.ti.com/product/TPS3808 ; TI SN74LVC244A https://www.ti.com/product/SN74LVC244A .
