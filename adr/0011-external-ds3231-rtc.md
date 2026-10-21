# ADR-0011: 外付けDS3231で電源断後の時刻を保持する

- 日付: 2026-10-21
- 状態: **一台試作の候補として採用。実機受入前**
- 対象: FG-035 / OQ-08

## 背景

3.4C基板にはESP32-P4のRTCバックアップ端子があるが、Waveshare公開資料は充電式電池のみを指定している。さらにEspressifのESP-IoT-Solution資料では、ESP32-P4のVBAT機能はESP-IDFで完全サポートされず、ドライバー変更を伴う試験手順として扱われている。現行の時計アプリには起動時のRTC復旧経路がなく、3.4Cの充電電池の型番・コネクター・充電条件も公開情報から確定できない。

## 決定

1. 時刻保持は既製のAdafruit DS3231 Precision RTC Breakout #3013で行う。CR1220はこのモジュール自身の電池ホルダーだけに装着する。
2. モジュールのVINを3.3V、I²Cアドレスを0x68、GPIO28=SDA/GPIO29=SCL・I2C1を接続候補とする。GPIO割当、バス共用、プルアップ電圧は実基板リビジョンで照合してから接続する。
3. 起動時にOSFが解除され、2000〜2099年の有効なカレンダー値が得られた場合だけUTCとしてシステム時刻へ復元する。Wi-Fi接続後はSNTPで時刻を同期し、同期コールバックからキュー経由でRTCへ書き込む。
4. 3.4C基板上のRTCバックアップ端子は使わず、そこへCR1220等の一次電池を接続しない。
5. ESP-IDFアプリをビルド・実機確認するまではFG-035をOPEN、OQ-08を未完了のままとする。

## 理由

- 完成RTCモジュールと標準コイン電池を使い、VBATドライバー改変やRTC用専用基板の設計を避けられる。
- RTCが未設定・不在・OSF状態の場合は無効時刻を表示に使わず、SNTPが成功すればRTCを書き直す。
- 時刻変換は依存なしCコアへ分け、UTC/BCD往復、12時間形式、うるう日、OSF、不正日付をホスト試験できる。

## 費用メモ

- Adafruit #3013: DigiKey掲載 ¥2,864（税抜）/ ¥3,150.40（税込）。
- Maxell CR1220.1BS: ヨドバシ掲載 ¥220（税込）。
- 合計参考価格: 約¥3,370。送料・価格変動を含まず、一台用BOMには丸めて加算。

## 受入条件

- ESP-IDF v5.5.5でアプリをビルドし、I2C1のGPIO28/29が他の機能と競合しないことを基板資料と実測で確認する。
- RTC未設定/OSF、不在、I²C読書き失敗から安全に起動し、`TIME NOT SET`またはSNTP時刻へ復帰する。
- SNTP同期後のRTC書込み、短時間・長時間の主電源断後の復元、時刻ずれ、電池消耗、日付境界を確認する。
- RTCの電源/信号配線と電池極性を無通電で確認し、3.4CのRTC充電端子へ一次電池が接続されていないことを確認する。

## 参照

- [Waveshare 3.4C公式資料](https://docs.waveshare.com/ESP32-P4-WIFI6-Touch-LCD-XC)
- [Espressif ESP32-P4 VBAT資料](https://docs.espressif.com/projects/esp-iot-solution/en/latest/low_power_solution/esp32p4_vbat.html)
- [ESP-IDF v5.5.5 System Time](https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-reference/system/system_time.html)
- [Adafruit DS3231 #3013](https://www.adafruit.com/product/3013) / [DigiKey Japan](https://www.digikey.jp/ja/products/detail/adafruit-industries-llc/3013/5875808)
- [Maxell CR1220.1BS (ヨドバシ)](https://www.yodobashi.com/category/21484/53821/53827/)
- [RTC UTC変換コア](../firmware/cots_clock_core/src/dial_rtc_ds3231.c) / [時計アプリ](../firmware/cots_clock_app/README.md)
