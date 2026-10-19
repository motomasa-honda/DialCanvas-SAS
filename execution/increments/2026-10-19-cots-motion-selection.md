# 7軸モーター・ドライバー既製品選定

- 対象ID：G4-04、G1-05、G3-06。FG-026 / OQ-05 に選定根拠を記録。48件のステータス・件数は変更しない。
- 選定した設計候補：Seeed Studio Gear Stepper Motor Driver Pack、メーカーMPN `105990072`、7セット。1セットに28mm径/5V/4相/1:64モーター1個とドライバー基板1枚。国内取扱コードはMarutsu `M0155-8561`。
- 既製化の利点：モーター単体と別出所のULN2003基板を組み合わせる従来案から、メーカー同一パック品に寄せ、SKU混同と別途ケーブル接続のリスクを減らす。
- 重要な電力影響：メーカー公称巻線21Ω±7%。5.25V/19.53Ωを使う保守的な巻線上限は全7軸1相で1.88A、2相で3.76A。2相上限は5V/5A源に20%余裕を取った4A総負荷枠をモーターだけでほぼ消費する。ULN2003電圧降下を引かない机上上限であり、測定値・電流定格・安全判定ではない。
- 変更ファイル：`components.json`, `power_budget.py`, `test_power_budget.py`, `check_contract.py`, `README.md`, `tasks.csv`, `progress.json`, `requirements.yaml`, `open-questions.md`, `decisions.md`, `change-history.md`。
- 検証方法：COTS契約チェック、巻線公差/1相・2相上下限を含む電力予算回帰、全体preflight、設計ID整合、JSON/CSV parse、差分空白検査。
- 検証結果：関連COTS/ネイティブ証拠契約PASS（618既存接続保持、EN/OE抑止、ERC既知2件を明示）、電力予算回帰7/7 PASS、全体preflight38/38 PASS、設計リンク/要求ID検査PASS、JSON/CSV parse PASS、`git diff --check` PASS。KiCad native出力は前コミットCI artifactの再照合であり、この変更のKiCad CIは未実行。
- 未受入：メーカー配布EAGLE board outlineと実端子座標、実基板/コネクタ寸法、歯車軸ハブ、実負荷トルク、回転周期、騒音/温度、7軸同時負荷/電圧降下、国内在庫の発注時点再確認。
- 後続影響：候補SKUをG4-04・CAD・負荷境界の共通基準にする。基板外形/ピンと負荷電流が確定するまでPCB・ハーネスを製造確定しない。モーターEN/OEは抑止、購入/通電/加工/製造リリースなし。
- 状態：設計候補を決定。FG-026とG4-04はOPEN、G3-08はHARDWARE_WAIT、製造ゲート0/6。
