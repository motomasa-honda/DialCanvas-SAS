# 新設計のシステム境界

本書は[設計ベースラインv0.21](../10-desk-redesign/design-baseline-v0.21.md)の機能分担を示します。機能の分離は設計方針です。表の実機受入項目が完了するまで製造・性能の合格とはしません。

| 機能 | 入力 | 責務 | 設計/実機状態 |
| --- | --- | --- | --- |
| 電源入力 | USB-C PD、HUSB238固定9V要求 | 9V入力ヒューズ後にモーター枝と5V変換枝へ分配 | 構成BASELINED。PD契約/全負荷/異常停止OPEN |
| 表示・主制御 | ESP32-P4-WIFI6-Touch-LCD-3.4C SKU31523 | 画面、microSD文字盤、SNTP、入力、TMC指令 | 部品/ GPIO候補BASELINED。基板改版と実表示OPEN |
| 時刻管理 | SNTP、DS3231 RTC候補 | UTC復旧/同期、JST変換 | アプリ実装。ネット断/停電/RTC保持OPEN |
| 文字盤 | microSDのJPEG、任意dial.json | 読込、針描画、一覧選択、既定盤保護 | 形式FIXED。表示器上の描画/SD/NVSはOPEN |
| 時計表示 | ESP-IDFシステム時刻、文字盤 | ミリ秒補間した3本針を描く | 16ms更新要求。実フレームレートOPEN |
| 歯車駆動 | 本体長押し要求、モーター電源状態 | 1基のステッパーで装飾歯車列を動かす | 既定GPIO出力無効。独立VMスイッチとENN外部プルアップを候補化。動作試験OPEN |
| 照明 | 5V枝、独立物理スイッチ | 暖色LEDを一定の間接照明として点灯 | LED候補BASELINED。明るさ、拡散、温度OPEN |
| 筐体 | 木材、PC保護板/支持板、取付金具 | 前後整備、指到達防止、部品保持 | 名目寸法BASELINED。現物/製作図OPEN |

モーター駆動の開始/停止は時計時刻を変更しません。物理モータースイッチはドライバーVMを直接切り、ソフトウェア停止だけに依存しません。旧M1 eFuseは新設計の経路に含めません。細部は[電源・制御](../04-electronics/power-and-control.md)と[ADR-0014](../../adr/0014-new-power-and-motor-safety-baseline.md)を参照してください。
