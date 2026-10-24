# 2026-10-23 引き継ぎ参照資料

元ZIPは会話添付の `Forest_Guardian_Chat_Reference_Pack_20261023(1).zip`（ローカル上の重複回避名）です。

- 期待配置先: `reference/2026-10-23/original-reference-pack.zip`
- 元ZIPサイズ: **883777 bytes**
- 元ZIP SHA-256: `b50177d12558f87b33673c1567680bf4b0e9ce875f49227431087a52c170b06d`
- ZIPエントリ数: **26**
- 状態: **ZIP本体のGitHub登録待ち**。このREADMEだけで原本保存済みと判断しないこと。

ZIPには `design-baseline-v0.21.md`、`display-board-interface.md`、`walnut_case_candidate-2026-10-22.md`、`assembly-plan.md`、PDF/SVG図面、`source_manifest.json` 等が含まれる。

参照ZIPは監査対象であり、ZIP中の旧資料をそのまま現行FIXED仕様へ昇格させない。現行正本はルート `AGENTS.md` の指定に従う。

## 取り込みチェック
- [ ] ZIP本体を上記配置先へ原本のままコミット
- [ ] SHA-256とファイルサイズを照合
- [ ] ZIP内の26エントリを監査・分類
- [ ] mainの既存資料との差分を記録
- [ ] 設計検証テスト実行
- [ ] Draft解除とレビュー
