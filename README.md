# DialCanvas-SAS / Forest Guardian

このリポジトリは、Forest Guardian / DialCanvas Desk Edition の設計とソフトウェアを管理します。旧DialCanvas腕時計資料と旧7軸置き時計設計は、由来を残すため履歴として保持しています。

## 現行設計

- [新設計の基準](docs/10-desk-redesign/README.md)：ウォールナット筐体、円形画面、microSD文字盤、単一モーターで連動する装飾歯車。
- [要求台帳](docs/01-requirements/requirements.yaml)：状態付き要求、未決定事項、検証項目。
- [現状と証拠](docs/10-desk-redesign/status-2026-10-21.md)：確認済みソース、ホスト試験、未実施の実機検証。
- [残作業一覧](docs/10-desk-redesign/worklist.csv)：各項目の状態と完了条件。
- [要求移行表](docs/10-desk-redesign/requirements-migration-v0.8-to-v0.21.csv)：旧7軸要求から現行v0.21要求への対応。

現行方針は7軸固定ではなく、歯車数も固定しません。現時点の28歯車図は配置候補です。TMC2209、Waveshare 3.4C、モーター、電源、材料も、実物と安全条件を受け入れるまでは候補です。

## ソフトウェア

- `firmware/cots_clock_core/`：針角度、エンコーダー、文字盤選択、ステッパー周期、DS3231 UTC変換のホスト検証可能なCコア。
- `firmware/cots_clock_app/`：ESP-IDF/LVGLアプリ。文字盤表示、microSD走査、操作、時刻同期、RTC処理を含みます。モーターGPIO出力は明示的なビルド設定がない限り無効です。
- ホストテストとESP-IDFビルドは `.github/workflows/desk-redesign.yml` で実行します。

ホスト試験成功は実基板のGPIO割当、表示性能、RTC保持、電源安全、歯車負荷、騒音、温度を証明しません。製作・購入・通電・書込みの受入状態は作業一覧を参照してください。

## 旧設計資料

`execution/` と旧設計向け文書・回路・ブランチはその時点の証拠を保つため残しています。現行の進捗率や新設計の合格根拠には使用しません。旧ブランチは更新しません。

## 設計文書の整合性確認

```sh
python3 tests/check_design.py
cmake -S firmware/cots_clock_core -B /tmp/dialcanvas-clock-core-build
cmake --build /tmp/dialcanvas-clock-core-build
ctest --test-dir /tmp/dialcanvas-clock-core-build --output-on-failure
```
