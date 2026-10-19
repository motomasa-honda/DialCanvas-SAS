# G5-05 — ESP32-P4 ↔ ESP32-C6 Hosted Wi-Fi + HTTPSの実装・未承認安全境界

既存の `G5-05`を引き続き作業。前段の認証実装とHTTPS6ハンドラーを再利用し、新規 `fg_hosted_wifi.c`と`fg_net_service.c`を既存製品ソースへ連結する。ESP32-P4は無線機を持たないため、XCボード搭載ESP32-C6のSDIO Hostedを利用。公式ボードwifistation (ESP-IDF 5.5系) に合わせ、ホスト依存関係を `esp_hosted 1.4.*` / `esp_wifi_remote 0.14.*` に固定。**C6側ファームウェアの実互換性は未検証、書き換え禁止。**

## 起動・安全条件
1. `nvs_flash_init()`後、**CONFIG_NVS_ENCRYPTION有効時のみ**専用NVS`fg_secure_web`をREADONLYで確認する。`sta_ssid`(32文字以下)、`sta_pass`(8-63文字WPA2以上)、`tls_cert`(PEM certificate)、`tls_key`(PEM private key) の4つが完全かつ一意に存在しなければネットワーク無効。TLS鍵はソース・CI・通常NVSに書き込まない。TLS秘密鍵PEMはメモリ内のみ。Wi-Fiドライバの設定は`WIFI_STORAGE_RAM`。
2. ESP32-C6 Hosted StationのIP取得イベントで原子フラグIP_READY=1、切断またはIP_LOSTで0。最大5回の再接続依頼までとし無限再試行しない。
3. 制御タスクとは別の低優先`fg_wifi_https`タスクが250ms周期でIP状態を確認。IPと暗号化NVSの証明書/秘密鍵が揃った場合だけ`httpd_ssl_start`。IP喪失時にはHTTPSサーバーを停止。**暗号化されていないHTTPにはフォールバックしない**。
4. ネットワーク処理からモーターのARM/相GPIOを直接操作する経路は禁止。実運転の許可は独立HW停止+元の5ms制御タスクで再確認。

## この実装で完了しないこと
- **ESP32-P4/C6の実機でのHosted通信・DHCP・再接続/切断・TLS handshakeは一切未実行。** 実機側C6 firmwareバージョン不明。製造承認0/6。
- Wi-FiやTLSの秘密情報を保護NVSへ入れる安全な**初期プロビジョニング作業が未実装**。NVS暗号化はFlash Encryption/eFuseを前提にする場合があり、これを有効化・焼き込みする操作は**明示承認まで禁止**。暗号化済みNVSでも同じFlash上への秘密鍵保持について脅威モデルを確定する必要がある。
- この通常CIビルドはNVS暗号化を有効化しないため、Wi-Fi接続/HTTPSは**未起動が正しい**。Wi-Fiスタックの**ESP32-P4向け実コンパイル+リンク**だけをチェックし、実通信確認済みと偽らない。
- OTA署名/ロールバック G5-06 はOPEN。G5-05もWORKING、正式20/48、製造0/6、SW11/14。発注、切削、実機書込、eFuse、main merge禁止。

**G5-05の残完了条件**：承認したprovisioningと機密保持、実ボードP4/C6の相互接続+IP再接続、検証されたTLSハンドシェイク、認証付き6 API+欠権/悪用時拒否、電源隔離済みHILで単一writer経路のログ、確定した運用リセット/鍵失効。

参考一次資料: https://docs.waveshare.net/ESP32-P4-WIFI6-Touch-LCD-XC/ESP-IDF/ 、 https://docs.espressif.com/projects/esp-idf/en/v5.5.1/esp32/api-reference/storage/nvs_encryption.html

## 追加の必須検査：製品バイナリがRAW A/B候補に収まること

ESP32-C6 Hosted・HTTPS追加により実ビルドサイズが増えるため、G5-05の実製品ビルドCIで `0x380000` bytes（3.5MiB）を超えたら**失敗**させる。これはPhase68/69の既存RAW A/B候補の真の境界であり、模擬テストではない。ただし格納可能は実デバイスのOTA/ロールバック成功を意味しない。後工程G5-06は別途未完了。

## 2026-10-17機密保持・遠隔モーター制限の補強

HTTPSで要求を受け付けても、**未完成のG1-05/06およびG5-08が未合格の間は remote START と remote FAULT CLEAR を 423 Locked で拒否**。どちらも制御タスクのキューへ絶対に投入しない。認証済みのSTOPだけをキューへ投入できる。物理スイッチによる停止は既存どおり。新たな実機安全ゲートが承認されるまで、この拒否処理は解除しない。

機密情報は一般NVSではなく独立したfg_cfg領域に格納し、nvs_flash_secure_init_partition()でNVS XTSを要求する。保護鍵が存在しない/暗号化未設定のビルドではネットワーク無効。ハードウェアのflash encryption/eFuse操作を行わない。
