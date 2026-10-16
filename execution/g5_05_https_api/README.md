# G5-05 — 実HTTPSハンドラー＋物理ペアリングコード表示（未製造）

本成果は既存G5-05の続きであり、新Phase・新タスクを増やさない。`execution/g5_05_access_core/apply_product.py`で元ファームウェアを統合した後に`apply_https_product.py`を適用。既存ESP32-P4画面のSTATUS上に**物理SW1+SW2操作でのみ生成された6桁コード**を表示。ペアリング60秒後に消去し、未表示状態では物理操作しても受け付けない。通信タスクは検証済みSHA-256トークンのみでVIEWER/OPERATOR/ADMINを認可する。

### 実装済みHTTPS API（コンパイル・整合確認範囲）
| Method | Path | Auth | 運用 |
|--|--|--|--|
| POST | /v1/pair | 物理スイッチ後6桁コード | 管理者32byte tokenをHTTPSで1回返す |
| GET | /v1/status | VIEWER+ | 状態/故障番号のみ。PIN非公開 |
| POST | /v1/token/issue | ADMIN | VIEWER/OPERATOR token発行 |
| POST | /v1/motors/start | OPERATOR+ | 5ms制御タスクへ非同期intent、202 queuedだけ |
| POST | /v1/motors/stop | OPERATOR+ | 同上（ARM/phaseを直接書かない） |
| POST | /v1/fault/clear | ADMIN | 独立HW fault health/ARM LOWを制御タスクが再確認 |

Authorizationは`Bearer <64-digit-hex>`。全body長上限96B、役割対象と文字列を完全一致で検査、未知path/不正権限/非TLSは禁止。POST/GET以外のハンドラーを公開しない。NVS保存失敗ならトークンを返さない。全認証情報へのアクセスにmutex、制御ループ側からのロック取得は0msで安全側拒否。

### DONEにしない理由
このcommitでは**証明書・鍵を固定埋込しない**。`fg_https_start_if_ready`がネットワーク準備済みかつTLS証明書/秘密鍵を受け取るまで起動しない。ESP32-P4のESP32-C6 SDIO Wi-Fi hosted初期化、SSID/provisioning、真正のTLS証明書/鍵の安全な保存と更新、端末接続でのHTTPS handshake・API end-to-endは未完了。このプロジェクトは個人製作用だが、ダミーの証明書でアクセス可能と見せかけない。

ESP-IDF HTTPS公式: https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-reference/protocols/esp_https_server.html
Waveshare Wi-Fi: https://docs.waveshare.net/ESP32-P4-WIFI6-Touch-LCD-XC/ESP-IDF/

実ビルド証拠はGitHub Actionsで残す。進捗は20/48、G5-05 WORKING、製造0/6、eFuse EN LOW / 28相OE HIGH、HW通電やmain mergeはしない。
