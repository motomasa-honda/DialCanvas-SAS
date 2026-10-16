# G5-05：暗号化NVS鍵領域レビュー（製造未承認）

RAW A/B原本にはNVS鍵領域がなく、G5-05のCONFIG_NVS_ENCRYPTIONを有効にする際の障害になる。既存の9領域のうち**8領域は一切変更せず**、reservedの先頭4KiBだけ `nvs_keys,data,nvs_keys,0x1E10000,0x1000,encrypted` に割当て、reservedの残りを 0x1E11000/0x1EF000 に変更した。アプリA/B各0x380000、旧NVS 0x4000、時計データ、総32MiBの全境界を維持。

`check_partition.py`がオリジナルのtar.gz SHAを検証して正規のRAW A/B CSVを実抽出、全行の一致と4096B整列/非重複を検証。別途CIは本物のESP-IDF gen_esp32part.pyでバイナリ変換を検証する。

**これはレビュー専用の候補であり、原本アーカイブ/firmware/partition.csv/flash/eFuseを変更しない。** 旧reservedの実装物、NVS暗号化キーの生成や初期化・移行/消去、eFuseセキュリティ設定は実機安全・製造承認まで全てHOLD。ソフトウェア動作証明やTLS通信確認ではない。正式進捗 G5-05 WORKING、20/48、製造0/6。

## G5-05 承認前の機密情報分離（2026-10-17追補）

暗号化鍵区画に加え、**Wi-Fi認証情報・TLS証明書・秘密鍵専用のNVS領域 fg_cfg (0x1E11000/0x8000)** を予約領域に設ける。元の一般NVS（故障履歴、役割トークンのハッシュ等）をまったく上書きせずに初期プロビジョニングできる配置。reservedは0x1E19000/0x1E7000へ縮小。運用用8区画のオフセット/サイズ/フラグは完全一致をCIで強制し、ESP-IDFネイティブパーサでも確認する。

専用領域はただ追加するだけでは暗号化されない。**Flash Encryptionに守られたnvs_keysの鍵を読み、nvs_flash_secure_init_partition("fg_cfg",…)を成功させ、nvs_open_from_partition("fg_cfg",…)で読み込む**構成へ実コードも修正。異常・欠落・未承認構成はネットワークを起動させない。通常のCONFIG_NVS_ENCRYPTION無効ビルドは通信が無効なまま。外部機器/Flash/eFuseは一切変更しない。

**秘密情報の書込みは実施禁止**。オフラインでのみ候補イメージを生成する`make_provisioning_image.py`を追加。テストはCIの一時領域に偽のSSID/証明書/鍵を生成して実IDF generatorへ流すものであり、本番キーはGitHub/CIに渡さない。
