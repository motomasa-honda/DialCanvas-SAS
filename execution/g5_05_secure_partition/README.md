# G5-05：暗号化NVS鍵領域レビュー（製造未承認）

RAW A/B原本にはNVS鍵領域がなく、G5-05のCONFIG_NVS_ENCRYPTIONを有効にする際の障害になる。既存の9領域のうち**8領域は一切変更せず**、reservedの先頭4KiBだけ `nvs_keys,data,nvs_keys,0x1E10000,0x1000,encrypted` に割当て、reservedの残りを 0x1E11000/0x1EF000 に変更した。アプリA/B各0x380000、旧NVS 0x4000、時計データ、総32MiBの全境界を維持。

`check_partition.py`がオリジナルのtar.gz SHAを検証して正規のRAW A/B CSVを実抽出、全行の一致と4096B整列/非重複を検証。別途CIは本物のESP-IDF gen_esp32part.pyでバイナリ変換を検証する。

**これはレビュー専用の候補であり、原本アーカイブ/firmware/partition.csv/flash/eFuseを変更しない。** 旧reservedの実装物、NVS暗号化キーの生成や初期化・移行/消去、eFuseセキュリティ設定は実機安全・製造承認まで全てHOLD。ソフトウェア動作証明やTLS通信確認ではない。正式進捗 G5-05 WORKING、20/48、製造0/6。
