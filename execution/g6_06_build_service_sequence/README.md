# Forest Guardian G6-06 正式限定完了 — 組立順序・7軸個別交換手順

**成果物の意味**：既存D7原本1,774ソリッドのSHA照合付きで設計済みの**80個の実部品名**を、**重複・欠落なし**で17工程の依存順へ割り付けた「組立順序仕様」と、7軸それぞれについて15工程（**7×15=105件**）の独立交換レビュー票を作成した。全42個の制御/5V/GND接続端子を`execution/m1_inspection_42.csv`へ1対1に対応。これがG6-06のレビュー工程完了根拠。**加工/組立/交換そのものは一度も実施していない。**

## ソースと読み方
- `assembly_review.json`: **17工程（A01–A17）**、各工程の先行条件、source partsすべて列挙、工程ごとの停止/レビュー条件。80点はcore7, bezel8, cover8, gear7, ledBoards4, leds20, sensor14, lightWood12の8群。
- `service_review.json`: **G1–G7×15工程**、55mm+Z、対象軸以外6モジュールとP3/歯車は一切取り外さず、共通背面カバーと背面グリルだけ整備アクセスとして扱う。移設後ファン、個別ロックバー、secondary keeper、ケーブル取り回し確認を必須。
- `branch_register_42.json`: 各軸6ピン×7。実モジュール端子は **UNVERIFIED**、実切断長 **TBD**、実導通 **NOT_TESTED** のまま強制。現物で真のデータが出るまでは確認済みとしない。
- `check_contract.py`: 80部品の一意割当、工程17件の依存DAG、7軸各15段の全105行と55mm・6軸非取り外し・G5切削禁止を全件チェック。42ピンが元CSVと完全一致しているか監査。進捗台帳も20/48と整合することを自動検証。

## クリティカルパスとなる実機・安全ブロッカー
**実試作/交換作業のGOサインではない**。後部アクセスに必要な元60mmファンの移設は配置上必須だが、熱/騒音/109mA対100mAの問題は未解決（G3-06）。全7軸の55mm名目退避は、実PCB外形、実コネクタ、工具径、配線曲げRと実長で未検証（G2-03/04/05/07, G3-04/05/07）。G5 BACK_WOOD 48×35領域は81.346%が**既存空洞**で、G1–G7共通ポケット加工は**禁止**。二次keeperのねじボス肉厚/強度/締付トルクは未承認。5分割鋼製フレームの突合せ強度、背板3mmの余肉強度、fan開口も未完了。G6-04木接合仕様・G6-05配線レイヤー・G6-07実印刷・G6-08製造一式は**別件のまま OPEN**。G1-05/06ラッチ・G1-07 PCB、G2-08導通、G3-08強度/温度、G5-08モーター/HILは未完了。

安全: **eFuse EN は GND 10kΩ固定、28相の/OE HIGH＝運転不能を維持**。工具・切削・部品発注・PCB製造・通電・実機FW書込・main mergeは禁止。これは**「組立と個別交換の順序設計」を閉じたのであって製造/実運用を閉じたわけではない**。進捗は **19→20/48**、製造0/6、SW11/14。

**使用原本**:
- `execution/g6_03_80_source_faces/design_contract.json` (80 objects)
- `execution/cassettes/seven_axis_conditional_layout.json` (7 individual axis positions /55mm)
- `execution/m1_inspection_42.csv` (7×6 terminal source register)
- `execution/secondary_keeper_2026-10-16/design_contract.json`
- `execution/g5_fivepiece_2026-10-16/design_contract.json`
