# 7軸モーター・ドライバー既製品選定

- 対象ID：G4-04、G1-05、G3-06。FG-026 / OQ-05 に選定根拠を記録。48件のステータス・件数は変更しない。
- 選定した設計候補：Seeed Studio Gear Stepper Motor Driver Pack、メーカーMPN `105990072`、7セット。1セットに28mm径/5V/4相/1:64モーター1個とドライバー基板1枚。国内の調達候補はMarutsu `M0155-8561`、DigiKey Japan `1597-1699-ND`、Switch Science `SEEED-105990072`。
- 調達見積スナップショット（2026-10-19閲覧、発注時要再確認）：DigiKey JapanはActive/In-Stock 125、1個税込¥1,241.90の表示で、7個換算は税込¥8,693.30（送料・決済/配送条件除く）。Switch Scienceは在庫7、税込¥1,290/個の表示。いずれも在庫確保・購入実績・確定見積ではない。
- 既製化の利点：モーター単体と別出所のULN2003基板を組み合わせる従来案から、メーカー同一パック品に寄せ、SKU混同と別途ケーブル接続のリスクを減らす。
- 重要な電力影響：メーカー公称巻線21Ω±7%。5.25V/19.53Ωを使う保守的な巻線上限は全7軸1相で1.88A、2相で3.76A。2相上限は5V/5A源に20%余裕を取った4A総負荷枠をモーターだけでほぼ消費する。ULN2003電圧降下を引かない机上上限であり、測定値・電流定格・安全判定ではない。
- 変更ファイル：`components.json`, `power_budget.py`, `test_power_budget.py`, `check_contract.py`, `README.md`, `tasks.csv`, `progress.json`, `requirements.yaml`, `open-questions.md`, `decisions.md`, `change-history.md`。
- 検証方法：COTS契約チェック、巻線公差/1相・2相上下限を含む電力予算回帰、全体preflight、設計ID整合、JSON/CSV parse、差分空白検査。
- 検証結果：関連COTS/ネイティブ証拠契約PASS（618既存接続保持、EN/OE抑止、ERC既知2件を明示）、電力予算回帰7/7 PASS、全体preflight38/38 PASS、設計リンク/要求ID検査PASS、JSON/CSV parse PASS、`git diff --check` PASS。KiCad native出力は前コミットCI artifactの再照合であり、93afc54 CIは別途実行中。この記録の日本販売店在庫/価格は商品ページ表示を照合した情報で、予約・見積ではない。
- 未受入：Seeed配布EAGLEアーカイブは存在を確認したが取得/展開による寸法抽出は未完了。実基板外形・端子ピッチ/座標・コネクタ実寸、歯車軸ハブ、実負荷トルク、回転周期、騒音/温度、7軸同時負荷/電圧降下、国内在庫の発注時点再確認。
- 後続影響：候補SKUをG4-04・CAD・負荷境界の共通基準にする。基板外形/ピンと負荷電流が確定するまでPCB・ハーネスを製造確定しない。モーターEN/OEは抑止、購入/通電/加工/製造リリースなし。
- 状態：設計候補を決定。FG-026とG4-04はOPEN、G3-08はHARDWARE_WAIT、製造ゲート0/6。
