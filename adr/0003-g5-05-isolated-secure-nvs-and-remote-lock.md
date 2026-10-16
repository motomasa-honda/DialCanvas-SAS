# ADR-0003 — G5-05 HTTPS資格情報の独立暗号化NVSと遠隔起動禁止

- 登録日: 2026-10-17
- 状態: PROVISIONAL（実機・製造承認前）
- 対象: G5-05 HTTPS pairing/権限API、G1-05/06 安全回路、G5-08 実機故障注入
- PR: #2（Draft）

## 問題

初期設計ではWi-FiパスワードとTLS秘密鍵を、故障履歴とロール認証ハッシュが使用する既存デフォルトNVSから直接読み込む想定だった。製造時にNVS生成イメージを一括書込みすると履歴や認証情報を消してしまう。さらにESP32-P4製品のG1-05/06は未承認にもかかわらず、HTTPSの認証済みSTART・FAULT CLEARが5ms制御タスクへ入る状態だった。

## 採択した設計

1. 32MiBの元RAW A/Bレイアウトの8運用区画は座標、サイズ、フラグを1つも変更しない。
2. 未使用予約領域の先頭に `nvs_keys` (4KiB; ESP-IDF data/nvs_keys, encrypted) と専用 `fg_cfg` (32KiB; data/nvs, **partition flag encryptedを付けない**) を追加し、残りのreservedは継続保持する。
3. 専用 `fg_cfg` には `fg_secure_web` 名前空間でSSID/Wi-Fiパスワード/TLS証明書/鍵のみを格納する。既存の `nvs` は故障履歴等を保持する。
4. 製品は `CONFIG_NVS_ENCRYPTION` とFlash Encryption保護スキームの両方を満たすときのみ `nvs_flash_read_security_cfg` による正規のNVS鍵取得、`nvs_flash_secure_init_partition("fg_cfg")` と `nvs_open_from_partition("fg_cfg")` を使用する。それ以外はWi-Fi/HTTPSを **fail-closed**。
5. 製造未承認の段階では `POST /v1/motors/start` と `POST /v1/fault/clear` は権限の有無にかかわらず423で拒否し、制御キューに一切流さない。STOPは認証したOPERATOR以上でのみキュー経由。物理停止/個別交換の方針を維持する。
6. 個体ごとの暗号化NVSイメージはリポジトリ外のローカル環境でのみ生成し、本番キーはGitHub/CIに投入しない。CIでは期限付きの偽TLS証明書と偽SSIDのみを使用し、生成ファイルをジョブ終了時に消去する。

## 不採用

- 通常NVSへの秘密情報書込み（他データの全領域上書きリスク）
- 暗号化有無だけを文字列・マクロで宣言する実態のない保護
- トライアル共通証明書を製品ソースへ埋め込む
- 静的G1-05/06未完了で遠隔起動を有効化する
- CI成功を実機ESP32-C6/Wi-Fi/TLS動作済みとみなす

## 解除に必要なゲート

製造前にESP32-P4実個体のFlash Encryption/eFuseの影響と可逆性を理解して明示承認する。保護鍵のライフサイクル、万一のキー喪失/ローテーション/バックアップ方法、デバイスへの初期プロビジョニング経路と媒体を決め、孤立したデバイス上でTLS接続・拒否条件・Wi-Fi切断時サーバー停止・実GPIO/OE/EN電気挙動をHIL検証する。eFuse/電源/フラッシュ操作はこのADRで許可されない。

実機と安全認可まで **G5-05 WORKING、G1-05/06 WORKING、製造0/6**。

一次資料: https://docs.espressif.com/projects/esp-idf/en/v5.5.1/esp32/api-reference/storage/nvs_encryption.html
