# G1-94 — KiCad ERC「孤立ラベル」16件の実修正

## 実体のある問題解消

G1-93のネイティブKiCad9回路は618物理端子/182部品。ERCに19件（`label_dangling` 16件、`power_pin_not_driven` 3件）が残る。G1-87に固定されたERC台帳 `erc_open_register.json` を起点に、16件それぞれの該当端子が**配線先を持たない単独端子**であることを確認した。

用途上も未接続が正しい Q_N (未使用)・LVCゲートのメーカーNC・TPS3808のCTオープン・WDI ENOUT NC・28相バッファの未使用Y端子を、孤立したラベルと5.08mmワイヤではなく、KiCad正規の `no_connect` マーカーへ変換。単なるERC除外設定やラベル名変更ではない。

変換対象は正確に16端子で、その他602端子を変更しない。製造用の実部品名・実フットプリントを新たに確定したわけではない。元G1-93への影響を防ぐため、正本を保持してG1-94レビューを親から再生成し、変更されたネットと端子を `nc_conversion_audit.json` に全数記録。

CIでは真のKiCad9 XML ネットリストと618端子の接続一致、KiCad ERCと各型の実数まで照合する。**期待ERCは残り3件の `power_pin_not_driven` のみ**。数量を偽るERC例外設定は使わない。モーターは物理ENと/OEが引き続き禁止。

## 残すべき3件

ERC U14.5=5V_RAW入力、U14.8=GNDおよびU20.8=3V3_AON。`power_pin_not_driven` は本当の5V源/3.3V源/GNDリターンの統合がまだ未定である兆候。未定の供給元をPWR_FLAGで捏造することは認めない。G1-05/G1-06 WORKING、G1-07基板作成OPEN、20/48・製造0/6継続。

今後は電源設計の具体化・レギュレータと5V入力の実電流/ヒューズ/GNDリターン/逆給電確認、実部品footprintの確定、PCB DRC、厳格な電源投入/瞬断/停止故障注入が必要。通電/発注/製造/flash/main merge禁止。

## 残3件の真の電源供給元欠落を追跡（2026-10-18）

新しい `power_source_blockers.json` は KiCad 実端子 U14.5（5V_RAW入力）、U14.8（GNDパワーリターン）、U20.8（3V3_AON入力）とERC3件の対応を固定する。製造許可や電源選定を捏造せず、各実部品の供給元・帰線・故障時の測定と電流仕様を受入条件として登録した。

`check_supply_blockers.py` は既存618実端子・182部品、EN R4/R67のGND保持、4バッファ8本/OEの遮断と、3電源指摘の未解決状態を検証する。実KiCad ERC JSONの違反3件の型と総数も検査する。**指摘を消すためのPWR_FLAGや電源ラベル追加は禁止**。各電源供給元の実寸・レギュレータ・最大電流・電圧ランプ・瞬断/逆給電実測が完了するまで、G1-05/G1-06はWORKING、G1-07はOPEN、製造0/6。


## 2026-10-18: G1-SRC residual ERC exact-identity regression

The physical KiCad9 ERC JSON must still contain exactly three **ERROR** findings at the *exact expected power-input terminals*: U14.5 (5V_RAW), U14.8 (GND), and U20.8 (3V3_AON). A former count-only check would pass if three *other* pins became undriven or an unrelated new error replaced one original. The strengthened `check_supply_blockers.py` verifies each real ERC violation's manufacturer KiCad symbol reference and physical pin number, issue description, severity and uniqueness. It explicitly mutates the real ERC snapshot three ways (wrong reference, duplicate pin, downgraded severity) and requires all three to be rejected. **It does not suppress/waive those errors or claim that the actual supply exists.** No motor enable, PCB fabrication, or DONE_SCOPE change.
