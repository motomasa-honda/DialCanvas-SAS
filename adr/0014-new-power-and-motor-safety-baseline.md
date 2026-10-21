# ADR-0014: Desk Editionの独立電源枝とモーター抑止

- 日付: 2026-10-21
- 状態: **一台試作の暫定設計基準。現物受入・購入・加工・通電承認ではない**
- 関連: [設計ベースラインv0.21](../docs/10-desk-redesign/design-baseline-v0.21.md)、[要求台帳](../docs/01-requirements/requirements.yaml)、[電源・制御](../docs/04-electronics/power-and-control.md)
- 置換: ADR-0009内のPololu #3411手動CC抵抗変更案、および過去資料にある旧M1 eFuse依存。旧ADR本文は判断履歴として保持。

## 背景

新しいDesk EditionはESP32-P4完成基板、画面、暖色LED、1基のステッパーを使う。旧7軸設計のM1基板/eFuseは新設計の部品でも安全根拠でもない。従来の表示給電候補Pololu #3411はUSB-C受電側抵抗を送電側へ手作業で変更する必要があるため、Type-C source制御を含む既製評価基板を候補にする。

## 判断

1. PD入力をUSB-C 9V/3A候補とし、HUSB238 #5807で9Vを要求する。入力後は3Aヒューズ候補と星形分岐を置く。
2. 5V枝はPololu D24V50F5 #2851で生成し、4A主幹ヒューズ候補の下流を表示・照明へ分ける。
3. 3.4CのUSB TO UART Type-C入力への給電sourceはTI TPS25810EVM-745を暫定採用する。5V入力、CCの3A広告設定、過電流/過温度保護を使う。TIガイド上の3A広告時の電流リミットはtyp. 3.40Aだが、接続機器の設計上限は広告値の3Aとする。EVMは評価基板なので、据付形状・ジャンパ・端子・入手性を確認し、量産品として扱わない。
4. 表示用のELECOM MPA-XCCECSS03BK 0.3m C-CケーブルをEVMと3.4CのUSB TO UART端子間に用いる候補とする。EVM source経由ではデバッグデータ経路を前提にせず、書込み時は給電ケーブルを取り外してPCを接続する。同時給電は禁止する。
5. モーター枝は9V分岐から1Aヒューズ候補、パネルSPST、TMC2209 VMの順に接続する。物理スイッチがVMを直接遮断する。旧M1 eFuse、旧故障ラッチ、旧7軸配線を経路へ含めない。
6. TMC2209のactive-low ENNは10kΩでVIO/3.3Vへ外部pull-upし、MCU起動時もENN HIGHを保つ。STEPに外部10kΩ pulldownを置く候補とする。ソフトウェア長押しは要求信号で、物理遮断を置き換えない。
7. モーター電源の回生過電圧候補としてSMBJ12AをTMC2209 VM/GND近傍に置き、ドライバー基板上コンデンサーを残す。TVSの応答波形・エネルギー余裕は実測で受入れる。
8. 分岐ヒューズ候補はPD入力3A、モーター1A、5V主幹4A、LED1A。これは暫定値であり、実導線・端子・突入・閉箱熱・異常条件を測るまで確定ヒューズ値とみなさない。
9. モーター戻りと5V/表示の戻りは分岐点まで分離する。40-pin拡張端子への5V注入は行わない。
10. 候補条件の静的負荷見積もりは約20.6W、9Vで約2.29A。9V/3A=27Wに対して参考上約6.4Wの余裕となるが、実負荷合格の根拠にはしない。

## 影響

- Pololu #3411を#2851の5V sourceへ直接つなぐ案と、CC抵抗の手作業変更は現行候補から外す。
- モーター枝に旧M1 eFuse依存を持ち込まない。保護要素は分岐ヒューズ、ドライバー電流制限、ENNの安全初期値、独立ハードウェアスイッチ、TVS候補で構成する。
- 旧ADR-0008/0009/0012/0013と`execution/`の記載は過去判断の証跡として残す。現行設計上のM1/eFuse判断には使わない。
- EVMの3A広告・typ. 3.40Aリミット、#2851のtypical 5A連続出力はメーカー記載値であり、時計全体の連続負荷・閉箱温度・コネクター定格の受入を意味しない。

## 受入条件

- 正確なPD契約が9V/3Aであること、契約失敗時の各枝挙動、極性、電圧降下を測る。
- TPS25810EVMの3A広告設定、CC試験ジャンパの扱い、5V入力、Type-Cケーブル接続を確認する。
- 表示器の最大輝度/Wi-Fi/SD負荷、LED、モーター始動・連続の同時条件で電流、電圧、温度を測る。
- リセット、brownout、未接続GPIO、タイマー異常、モーター拘束でENN HIGHと物理遮断が成立することを確かめる。
- モーター停止/手回し時のVM波形とTVS温度を確認し、TMC2209の絶対最大定格内であることを記録する。
- ヒューズ定格/時間特性を導線・端子・負荷に対して確認する。

これらを受け入れるまでFG-026/FG-048およびDR-05のValidationStatusはOPENのまま、製作リリースDR-07はHOLDとする。

## 根拠資料

- TI [TPS25810EVM-745](https://www.ti.com/tool/TPS25810EVM-745)、[User's Guide](https://www.ti.com/lit/pdf/slvuai0)
- [Pololu D24V50F5 #2851](https://www.pololu.com/product/2851)
- [Adafruit HUSB238 #5807](https://www.adafruit.com/product/5807)
- [Adafruit TMC2209 #6121](https://www.adafruit.com/product/6121)、[Analog Devices TMC2209 data sheet](https://www.analog.com/media/en/technical-documentation/data-sheets/TMC2209_datasheet_rev1.09.pdf)
- Littelfuse [SMBJ12A](https://www.littelfuse.com/ja-jp/products/overvoltage-protection/tvs-diodes/surface-mount/smbj/smbj12a)
