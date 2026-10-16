# G1-77 — 140実端子・39ネットの物理回路配線レビュー

このブランチの`nets_140.json`は、Phase75の**実際のKiCad9生成コードと旧85端子表**から算出した、140個の物理IC端子と抵抗・コンデンサ端子を39個の接続ネットへ分けたソース導出台帳です。CIは全端子が重複せず、TIの実ピン番号に一致し、2段のゲートと故障後「一度ボタンを離してから押す」FFが物理配線になっていることを検証します。

- **CLK**: J_REARM押下→R10kΩ/C1µF候補→SN74LVC1G17DBVR（A2→Y4）→U_ARM.CLK1。
- **離したことを記憶**: 同じSchmitt Y4→SN74LVC1G04DBVR（A2→Y4）→U_RELEASE_FF.CLK1、D2=3V3_AON、CLR_N6=QUAL_CLR_N、Q5=RELEASE_SEEN_Q。
- **D**: U_RUN.Q5正常2エッジ∧NOT ARM_REQ(SN74LVC1G04)→SN74LVC1G08→もう一つのSN74LVC1G08∧RELEASE_SEEN_Q→U_ARM.D2。
- **電源**: U_ARM.Q5は孤立し、U7.1 ENは唯一の10kΩプルダウンでGNDへ保持。決して通電可能な回路と見なさない。

実際のネイティブKiCad9図面 **`fg_G1_phase77_release_required_rearm_partial.kicad_sch` SHA256 `d9ed0998a904b5450b4c8eee96c4b3468c2f0efe949cf6e19379e31fa7ee20a9`**、Phase75の**バイト一致元図面**、Python生成・独立検証、20,000の理想FF試行、RCのしきい値6表、配線レビューA3 2頁は [配布ZIP] に収録。配布ZIP `Forest_Guardian_G1_Phase77_140Pins_Rearm_Engineering_2026-10-16.zip` SHA256 `a03c7de50d13050af05053ddaf0b68137bf87a29df839a81d3875409bfd0239a`、43ファイル、独立ZIP展開→実ソース再生成PASS。

**GitHubの静的CIは140端子実台帳と回路条件を検査。** ZIP内の61KB超ネイティブ回路図のバイト整合・20k試験をGitHubでは実行しないことを明示する。今後は同じ実ソース発生器をリポジトリでも実行できる方式へ昇格する。

**絶対保留**：eFuse U7.EN有効化、PG故障保持（起動直後PGはプルアップ可能）、7軸28相独立遮断、RC実コンデンサ公差・ノイズ、POR立上りCLK競合、STOP短絡/溶着、メーカーランドパターン、KiCad ERC/DRC、実機故障注入。G1-05/G1-06はWORKING、19/48・製造0/6、モーターeFuse EN GND維持、main変更と発注・加工・通電は禁止。

TI一次資料：
- https://www.ti.com/lit/ds/symlink/sn74lvc2g74.pdf
- https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf
- https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf
- https://www.ti.com/lit/ds/symlink/sn74lvc1g08.pdf
