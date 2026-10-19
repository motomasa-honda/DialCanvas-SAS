# Seeed motor envelope against the seven-axis cassette reservation

- 作業ID：G4-04、FG-026。根拠を追加し、完了ステータスはOPENを維持。
- 完了条件：採用候補モーターのメーカー図面最大寸法を既存40×31mmカセット候補および50×41mm軸予約へ当てはめ、姿勢制約と残る機械ブロックを明示する。
- 実装：`execution/g4_04_seeed_105990072/check_axis_envelope.py` が既存のハッシュ固定CAD寸法を入力として再計算し、`axis_envelope_screen.json` と README の機械インターフェース節へ結果を出力。G4-04の台帳Evidence/Limitを更新。
- 計算：取付穴中心間隔の上限35.2mm＋穴径上限4.35mmから、取付耳を含む保守的な平面包絡を39.55mmと算出。胴径上限28.1mm。40×31mm内で穴間隔を長辺方向へ向けた場合のみ入り、各辺マージンは0.225mm/1.45mm。90度回すと31mm辺を8.55mm超過する。既存50×41mm予約には同方向で各辺5.225mm/6.45mmの名目余裕。35×19.3mm基板も40×31mm内に入るが、モーターと基板は同一XY投影で重なるため実Z積層・ブラケット設計が必要。
- 検証：`check_axis_envelope.py`、`check_vendor_cad.py`、既存`execution/cassettes/check_manifest.py`、`execution/secondary_keeper_2026-10-16/check_motion.py`、`execution/preflight.py`（38/38）、`tests/check_design.py`、48 ID/JSON検査、`git diff --check`を実行しPASS。既存カセット/55mmチェックは元の候補を検査するもので、新しいモーターを統合したD7動作合格ではない。
- 残課題：0.225mmはハードウェア/工具/公差の余裕にならず、40×31のモーター保持方法は未成立。50×41予約内に低背の保持金具、基板エッジ保持、コネクタ、線の曲げを配置し、部品Z高さと全7軸の55mm掃引を元D7に重ねる。実品測定・保持強度・熱・負荷試験は別の受入。
- 後続影響：モーター取付穴間隔の軸を50mm側に限定し、従来の40×31 PCB包絡だけを使った機械前提を修正する必要がある。穴なし基板をモーターとは別に固定する専用ブラケットは本機固有。
- 安全/製造：作図上の静的包絡のみ。未購入、未加工、未通電、未承認。EN/OE inhibited。G4-04 OPEN、22/48、製造ゲート0/6。
- 実装コミットSHA：次の進捗追記コミットで記録。
