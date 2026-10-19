# G1-86 の正真正銘のKiCad 9 ERC監査結果（製造HOLD）

検証run: https://github.com/motomasa-honda/DialCanvas-SAS/actions/runs/38898970539/job/116966222534

- 実KiCad9.0.9のXMLに含まれる**404端子／112部品／110ネットが全件一致**。8＋5＋5ピンのTI NOR/INV/ANDロジックの物理ピン表と旧374端子を維持。
- ERC実測：**19件**。未接続端子ラベル16件、電源ソース未定義3件（U14.5 IN＝5V_RAW、U14.8 GND、U20.8 VCC＝3V3_AON）。既存G1-85の18件に対し、新NORのpower pin typeによる1件を顕在化させた。新回路の未接続問題を黙って隠していない。
- メーカー指定`U21.1 NC`はNative KiCad `no_connect`として扱い、実端子を架空の電気ネットに短絡しない。
- `erc_open_register.json` に現行19件の指摘名・型・対象ピンを完全登録。`validate_native_netlist.py`で新しいKiCadエラーが増えた場合、旧エラーが突然消えた場合、対象名が変化した場合は**必ず失敗**する。検査例外を追加していない。
- 残作業の優先：実電源の供給元の具体化、FAULT時出力遮断、PG立上げ後のラッチ入力統合、CLEAR_REQUESTの立ち上がりエッジかつrelease-firstでの物理認定、電源喪失時の失効/HIL、正規footprintとPCB DRC。製造0/6、19/48のまま、モーターは無通電。

これは抽象回路図のネイティブ検証であり、実PCBおよび安全回路を通電していない。