# G1-78：7軸×4相の28信号ハードウェア無効化候補（実208端子）

TI一次資料 SN74LVC244A 8-ch 3-state ×4個、`SN74LVC244APWR` PW TSSOP20を使用する**実番号の端子接続表**。ドライバ許可を与える以前の配線段階で28本すべてを**無効（High-Z）**にし、各出力に10kΩプルダウンを設ける。4ICの各2つのOEはアクティブLOWなので、1/19番端子を10kΩで3.3Vへプルアップ。28相のうちCPU信号と実ドライバーの間に **4×8bit 3ステートバッファ** を独立配置。最終4チャネルはGND入力と出力NC。

**現実のHOLD**：High-Z はHIGH/LOWを強制することではなく、下流プルダウンが弱い場合や、実モジュールドライバー自身に入力プルアップがある場合、入力がLOWと断定できない。電源3.3V喪失時の3ステート挙動、GPIO相電圧、実ドライバー入力しきい値/漏れ、20ピンPW footprint/ランドパターンとKiCad ERC/PCB DRC、28相の実配線長・クロストーク、STOP独立故障検出は未承認。

GitHubには**208端子・63ネットを全部記録した `nets_208.json`**、独立Python検査とメーカー出典を保存。実ネイティブ部分回路`G1_78_28PHASE_DISABLED_BUFFER_REVIEW.kicad_sch`（SHA `cb903ff4816802c6fd93152366b8ed985fbae1c789b13ee90d5188d803e97226`）、製造未承認の4x chip+28抵抗+4OE pullups+4 decoupler、50,000理想パターン、6誤配線検査の生成コードはユーザー配布 ZIP `Forest_Guardian_G1_140Pins_And_28Phase_Disabled_2026-10-16.zip`（SHA256 `b32927a5f45f963b3ca3de44323568c41c420a448196e0728932fb4ba160122b`）内に保存。ダウンロード後クリーン展開から双方の回路の再生成・独立テストPASS。

**G1-77と電気的にはまだ接続せず、U7.ENは10kΩでGND保持**。G1-05/06はWORKING、G1-07 ERC/DRCはOPEN。完了19/48、製造0/6、SW11/14、実機安全試験なし。main変更・発注・加工・通電・ファーム書込みは禁止。

メーカー：<https://www.ti.com/lit/ds/symlink/sn74lvc244a.pdf> / <https://www.ti.com/product/SN74LVC244A/part-details/SN74LVC244APWR>
