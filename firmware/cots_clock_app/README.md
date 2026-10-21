# DialCanvas 3.4C 表示アプリ

Waveshare ESP32-P4-WIFI6-Touch-LCD-3.4C用の独立ESP-IDFアプリ。LVGL表示を初期化し、microSDのJPEGを背景へ読み、`dial.json`の針設定を使って時・分・秒針を16ms間隔で更新する。Wi-Fi接続後にSNTPで時刻同期する。旧`phase67-core`とは別プロジェクトで、そちらの安全制御コードを参照・変更しない。

## ビルド環境

- ESP-IDF v5.5.5
- Waveshare BSP 3.0.1
- LVGL 9
- Espressif `esp_jpeg` 1.3.1
- Espressif `esp_wifi_remote` 0.14.x / `esp_hosted` 1.4.x
- ESP32-P4、3.4Cの800×800表示設定

Wi-Fi依存の組み合わせは[Waveshare公式のWi-Fi Station例](https://github.com/waveshareteam/ESP32-P4-WIFI6-Touch-LCD-XC/tree/main/examples/esp-idf/04_wifistation)に合わせた。ESP32-C6側は基板の工場出荷時Hostedファームウェアを使う想定だが、イメージの版・ハッシュはこの作業資料で固定できていない。実基板での接続確認まではWi-Fi同期を未受入とする。

ESP-IDF対象ビルドは `.github/workflows/desk-redesign.yml` で確認します。ビルド成功は正確な基板改版やGPIO配線を検証しません。実機書込み・通電は未実施です。

ESP-IDFを有効にしたシェルで実行する:

```sh
cd firmware/cots_clock_app
idf.py set-target esp32p4
idf.py build
```

Wi-Fiを使う場合は`idf.py menuconfig`の`DialCanvas Clock`でSSID/パスワードを設定してからビルドする。値はファームウェア設定に含まれる。ログにSSID/パスワードは出さない。SSIDが空ならWi-Fiを起動せず、表示アプリは`TIME NOT SET`を出したまま動作する。パスワードは空欄（オープンネットワーク）またはWPA2用8〜63文字に対応する。接続後は`pool.ntp.org`から非同期で時刻同期する。

## 外付けDS3231 RTC

3.4C基板のRTCバックアップ端子は充電式電池専用で、採用ESP-IDF v5.5.5にはP4 VBAT時刻復元の完全な対応がないため、この案では使用しない。Adafruit DS3231 breakout #3013をGPIO28=SDA、GPIO29=SCLのI2C1候補へ接続し、3.3Vで給電する。CR1220はDS3231モジュール自身の電池ホルダーだけに装着し、3.4C基板のRTC端子へ接続しない。

| DS3231 #3013 | 3.4C側 | 接続内容 |
|---|---|---|
| VIN | 3V3 | 3.3V給電。基板上のI²CプルアップもVINへ接続されるため、5V給電しない。|
| GND | GND | 共通GND |
| SDA | GPIO28 | I2C1のSDA候補 |
| SCL | GPIO29 | I2C1のSCL候補 |
| CR1220 | モジュール裏面ホルダー | プラス面を上向きに装着。3.4CのRTC端子にはつながない。|

起動時、DS3231のOSFが解除され有効な2000〜2099年のカレンダー値ならUTCとして`settimeofday()`へ復元する。SNTP同期後はコールバックから時刻を長さ1のキューへ送り、別タスクでRTCレジスターを更新する。RTC不在・未設定・不正値ではRTC復元を飛ばし、Wi-Fi/SNTPが利用できない場合は`TIME NOT SET`を表示する。I2Cピン共用、プルアップ電圧、電池保持、SNTP更新は実基板で未確認。

## microSDの文字盤

```text
microSD/
└── DialCanvas/
    └── faces/
        └── Forest/
            ├── face.jpg
            └── dial.json
```

`face.jpg`はBaseline JPEG、800×800ピクセル、8MiB以下。一般的な画像編集ソフトで用意し、既存ファイルを置き換えれば絵柄を変更できる。`dial.json`は任意。省略または値が不正なら組込み初期値を使う。

起動時に`DialCanvas/faces/`直下を走査し、名前がASCII英数字・`_`・`-`だけで1〜32文字、通常ファイルの`face.jpg`が0バイト超〜8MiB以下のフォルダーを候補にする。候補は名前順の先頭32件に絞って回転で巡り、現在のプレビュー名を画面に一時表示する。保存済み選択、`Forest`、名前順の先頭の順で起動画像を試し、JPEGを読めない候補は飛ばす。保存先はNVS。NVSが使えない場合も選択は動作中有効だが、再起動後は保持しない。候補がなければ簡易目盛り盤で起動する。SDは読取専用で、マウント失敗時に初期化・フォーマットしない。

## ロータリーエンコーダーとモーター出力

3.4Cの[公式回路図](https://files.waveshare.com/wiki/ESP32-P4-WIFI6-Touch-LCD-XC/ESP32-P4-WIFI6-Touch-LCD-XC-Schematic.pdf)にある40ピン拡張端子へ出ているGPIO2/3/21を既定割当とする。A/B/SWの順で割り当てる。GPIO20/22はC6側との共用可能性を確認できるまで割当から外す。モーター側GPIO4=STEP、GPIO5=DIR、GPIO32=ENNは候補割当で、正確な基板改版との照合前は配線しない。TMC2209のENNはHIGHでパワーステージを無効化します（[Analog Devicesデータシート](https://www.analog.com/media/en/technical-documentation/data-sheets/TMC2209_datasheet_rev1.09.pdf)）。MS1/MS2開放時の1/8設定や実ドライバーボードのプル状態は現物で照合します。エンコーダーの接点共通側をGNDへ接続します。GPIOは`menuconfig`で変更でき、既知の入力/I²Cとの重複と無効な番号は起動時に拒否します。

| 入力 | 既定GPIO | ソフト動作 |
|---|---:|---|
| A | 2 | 2ms目安でポーリング、4つの遷移ごとに一目盛り |
| B | 3 | A/Bの直交状態から方向を判定 |
| SW | 21 | 20msデバウンス、短押しで確定、900ms長押しで歯車の開始/停止要求 |

回転は文字盤をプレビューし、短押しでNVSへ選択を保存する。長押しで実験的なSTEP/DIR/ENN出力の開始/停止を行うコードを追加した一方、`CONFIG_DIALCANVAS_MOTOR_OUTPUT`は既定無効です。有効化するには`menuconfig`で明示設定し、GPIO・ENNの外部プルアップ・ドライバー・電流制限・独立物理遮断を現物で確認する必要があります。MCUリセット時の安全性は外部回路で保証してください。現時点ではGPIO改版照合、実機書込み、通電をしていません。

## 単一モーターの速度コア

共通コアへ、200 full-step/rev・1/8分割・1.600rpm用のSTEP間隔生成器を追加した。理論周波数42.666…Hzを固定小数点の余り配分で扱い、23,437µsと23,438µsを交互に出して平均周期を保つ。2,560パルスの合計は60秒になる。ホスト単体テストで平均周期・入力エラーを検証する。

ESP-IDFアプリはこの周期をSTEP出力に使い、10µsパルスとENN HIGHの停止状態を実装しています。既定ビルドではGPIO出力を無効にし、ハードウェアE-stopや電流保護を代替しません。GPIO改版、ENNのプルアップ、TMC2209基板、STEPパルス、始動トルク・振動・騒音・温度はすべて未受入です。

## この増分で動く範囲

- 3.4C向けLVGL/BSP表示初期化
- BSPのmicroSDマウントAPI呼出し
- 800×800 JPEG読込とRGB565展開
- `dial.json` v1の中心位置、各針の色・長さ・幅の読込と範囲検査
- 時刻が設定済みならミリ秒まで連続補間した針角度を16msタイマーで描画
- microSD文字盤の走査、ロータリーエンコーダーでのプレビュー/確定、NVSへの選択保存
- 文字盤名・角度遷移・リングインデックス処理のホスト単体テスト
- 単一ステッパーの分数STEP周期生成コアとホスト単体テスト（GPIO出力なし）
- 設定済みSSIDへのSTA接続、接続後のSNTP同期、接続失敗時の再試行
- 不正データ時の初期値/簡易文字盤への復帰
- 実験用単一モーター出力経路（通常ビルドでは無効。長押しで切替、タイマー異常時にENN HIGH）

時計時刻はESP-IDFのシステム時刻を使う。外付けDS3231の起動時読込・SNTP後書込のソースを追加したが、対象ビルドと実機時刻保持は未確認。Wi-Fi未設定・未接続かつ有効RTC時刻もない場合は`TIME NOT SET`を表示する。実機でのエンコーダー・文字盤切替・30/60fps測定、モーター負荷/停止確認は未実施。16msは更新要求周期であり、実測フレームレートの保証ではない。

Wi-Fi接続、SNTP初期化、文字盤走査/切替、エンコーダーのソースは追加済みだが、ESP-IDFツールチェーンがないため依存解決・ビルド・基板接続を確認できていない。SSID/パスワードは`menuconfig`からバイナリへコンパイルされるため、配布バイナリに秘密情報を含めないこと。
