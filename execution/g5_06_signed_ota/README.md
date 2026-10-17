# G5-06 署名付きOTA・ロールバック — 実製品への最小構成統合（WORKING：署名済み実機更新は未承認）

**今回の完了条件**は「ESP32-P4実製品のOTA実行経路をトランザクションとして実装し、改竄された署名、途中切断、誤区画、未承認通電のときに**起動対象を変更しない**こと」。本リポジトリのRAW A/Bアプリ各3.5MiB、`otadata` 8KiBを利用。更新先は`esp_ota_get_next_update_partition`で選び、現実の区画位置 0x10000/0x390000、サイズ0x380000、subtype app/ota_0,ota_1 を同時一致で確認する。文字盤データのA/B(各10MiB)は**OTAアプリ区画と無関係で、書込み禁止**。

## コードと保護

- `fg_ota_gate.c`: 1KiB毎ストリーミング、原本画像バイト数上限、通電停止/HILの両方未合格ならフラッシュ消去前に拒否、部分受信/書込み失敗時には`esp_ota_abort`、完了検証失敗時は起動選択しない。
- `fg_ota_port.c`: **ESP-IDF標準 `esp_ota_begin/write/end/set_boot_partition`**。アプリ署名を勝手にSHA比較だけで認証したことにはせず、`CONFIG_SECURE_SIGNED_APPS_NO_SECURE_BOOT` + `CONFIG_SECURE_SIGNED_ON_UPDATE_NO_SECURE_BOOT` と `CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE` が有効でなければ拒否。**esp_ota_endが正規の署名検証を担当**。
- 初回起動の `ESP_OTA_IMG_PENDING_VERIFY` は**安全実機未検証なので必ずロールバックを要求**。合格自動宣言 (`esp_ota_mark_app_valid_cancel_rollback`) 禁止。安全なハードウェア自己検査を組み込むのは独立のHIL承認後。
- 現在の`fg_ota_native_stage_for_review()`は`fg_ota_stage(...,false,false)`固定。**モータeFuseやOTAアプリ領域は物理的に一切変更しない**。実装を静的に検証できても今は発動できない。
- 送信URL/OTA操作のHTTPSエンドポイントは**設けない**。G5-05のTLS実通信が未検証のため、ネットワークからファームウェアを書けるパスを開かない。

## 現状と次のゴール

ホストで署名必須→開始→書込→署名認証→次回起動区画の順番と失敗時復旧を確認する。ESP-IDF 5.5.2本物のESP32-P4アプリにmoduleを統合してビルドし、RSA3072の**テスト専用鍵**で正規署名作成/検証と改竄拒否を実行する。実機C6/IP/TLS、個体ごとの署名鍵の保護と初回鍵の確立、APP_ROLLBACK bootloader有効化、初回起動/電源断と回帰確認は未実施。不要な新しいPhaseは増やさない。

正式完了判定は次の順：
1. 署名付き専用OTA構築モードのESP32-P4ターゲットビルド（正規鍵の使い方を決め、実機eFuseは触れない）。
2. 本番署名鍵はローカル秘匿、過去正規署名と改竄品/誤署名が通らない実機検証。
3. 安全なHTTPS転送経路・中断／逆送と並行リクエスト拒否。
4. 旧署名済アプリへの実機rollback/電源断復元、健康ゲートの安全確認。
5. これらすべてを満たすまでは`G5-06 DONE_SCOPE`にしない。

参考：[ESP-IDF OTA](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32p4/api-reference/system/ota.html) ／ [ESP-IDF Signed Apps](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32p4/api-reference/kconfig-reference.html)。

**無許可の実機フラッシュ/eFuse/通電はゼロ。PR #2はDraft、20/48 DONE_SCOPE、製造0/6、eFuse EN LOWと28相/OE HIGHを維持。**

## 2026-10-17：正式WORKING移行の検証証拠

[GitHub Actions run 38994400580/job/117283621612](https://github.com/motomasa-honda/DialCanvas-SAS/actions/runs/38994400580/job/117283621612)：ESP32-P4製品ビルド成功、OTAを含む1,040,976バイトのアプリが3.5MiB A/B内に格納可能、Espressif RSA3072の一時テスト鍵で署名検証成功/改ざん拒否、ホストで更新中断・署名検証失敗・区画上限と誤起動選択を検査。これは正真正銘の本体ソース組込みだが、**現行ファームウェアの署名付き更新モードは無効**。サーバー/個体鍵/実電源断/実機復帰は未試験につき G5-06 `WORKING`、20/48の完了数は増やさない。

## 検証強化：実ESP32-P4の**署名検証有効モード**を別CIで試験する

前段の署名済データ生成テストは、通常の製品ビルドが実際に署名検証を**要求する**設定で動くことまで証明しなかった。このため別CIジョブで、**一時RSA3072鍵**を生成し、`CONFIG_SECURE_SIGNED_APPS_NO_SECURE_BOOT`＋`CONFIG_SECURE_SIGNED_ON_UPDATE_NO_SECURE_BOOT`＋`CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE` を**試験用構築時だけ**有効にして、ESP32-P4製品全体をビルドする。実ビルドの署名検証・1bit改ざん拒否・3.5MiB区画サイズを確認し、実物の公開鍵と秘密鍵をGitHubに登録しない。ハードSecure BootやeFuse Anti-Rollbackはこの試験では**無効**。製造・通電・デバイスへの書き込みは引き続き禁止。

## 重要なRAW A/B統合修正（2026-10-17）

現行の元製品`firmware/partition.csv`は旧5MiB A/B (`app_b=0x510000`) であり、G5-06のソースが要求する新3.5MiB A/B (`app_b=0x390000`) と一致しないことを発見。コンパイルだけで成功と判定すると、実機では `fg_ota_native_stage_for_review` が区画不一致で必ず拒否する。**OTAは起動先の物理アドレスと一致して初めて意味がある**。専用CIはオリジナルSHAを保全し、展開したコピーだけ `partition-review-raw-ab.csv`へ差し替えて完全ビルドする。署名モードの方は、同じアプリ領域を維持しつつ独立`fg_cfg/nvs_keys`も備えた統合区画レビュー案を使う。両方ともIDFネイティブパーティションBINと元CSVを比較して、電源・実機書込を一切伴わない。正式な製造/暗号化承認は依然0/6。

## 署名ビルドの初回CI診断（2026-10-17）

ESP32-P4の署名モード候補CIで、`CONFIG_SECURE_SIGNED_ON_BOOT_NO_SECURE_BOOT` を設定しても有効化されなかったため、試験は意図的に失敗した。**G5-06で必要なのはOTA時の署名検証と初回起動ロールバック**であり、起動時の追加署名再検証はこのモードで必須とはしない。`CONFIG_SECURE_SIGNED_APPS_NO_SECURE_BOOT`、`CONFIG_SECURE_SIGNED_ON_UPDATE_NO_SECURE_BOOT`、`CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE` の3つは元のログ上で有効だった。追加の署名起動フラグだけを試験モードから外し、再ビルドする。必要ないKconfig選択肢で製品完成を遅らせない。

## G5-06 安全修正：ロールバック不成立なら通常起動へ進めない（2026-10-17）

初回署名更新後 `ESP_OTA_IMG_PENDING_VERIFY` で `esp_ota_mark_app_invalid_rollback_and_reboot()` が失敗または復帰不能だった場合、旧実装はログ出力後に app_main を続行する欠陥があった。`fg_ota_boot_guard_unqualified()` を成否付きに変更し、PENDING_VERIFY のロールバック要求が戻った場合・署名更新済イメージ状態取得失敗・INVALID/ABORTED/NEW は `false` を返す。呼出側は物理 ARM LOW を再指定して `app_main` から戻り、UI/ネットワーク/制御タスクの通常初期化を禁止。`VALID`/初期`UNDEFINED`のみ通過。未署名レビュー構成ではOTA書込が依然物理HIL偽値で拒否されるため、通常レビューGUI起動のみ許可する。

ESP-IDF実ビルドで構文/リンクを検証しても、実際のブートローダー戻り先・電源断・タスク停止安全性のHIL証拠にはならない。**G5-06 WORKING、20/48、製造0/6、eFuse EN LOW。**
