# Forest Guardian / DialCanvas 一台用設計図・組立図 v0.1

更新: 2026-10-23。寸法単位はmm。形状基準はmainの`033f460`、ケース見積図v0.4、BSS1-20Cの現行28位置CSVです。表示キャリア図/モーター線文書に残っていた旧奥行を172mm、背板内面をz=148mmへ整合修正しています。

## PDF

- [設計図10ページ](forest_guardian_design_v0.1.pdf): D00全体、ケース見積A01/A02 v0.4の2ページ、D03/D04支持板の全穴座標、D05軸断面、D06表示器保持、D07背面電装、D08電源、D09制御線。
- [分解組立図・組立手順5ページ](forest_guardian_assembly_v0.1.pdf): A00分解図、A01軸ユニット、A02ケースと表示器、A03背面電装/ハーネス、A04完成品の確認。

PDFはA3横。新規ページは日本語フォントを埋め込み、形状と文字をベクターで保持しています。ケース見積2ページは既存v0.4 PDFを変更せず挿入しています。図の倍率から寸法を拾わず、記載寸法とCSVを優先します。加工承認/CAMデータや実機合格証ではありません。

## 編集用SVGと原典

[D00](D00.svg) / [D03](D03.svg) / [D04](D04.svg) / [D05](D05.svg) / [D06](D06.svg) / [D07](D07.svg) / [D08](D08.svg) / [D09](D09.svg)

[A00](A00.svg) / [A01](A01.svg) / [A02](A02.svg) / [A03](A03.svg) / [A04](A04.svg)

- [ケース外形/断面SVG v0.4](../../03-mechanical/walnut_case_quote_drawing_v0.4.svg) / [ケース部材SVG v0.4](../../03-mechanical/walnut_case_quote_parts_v0.4.svg)
- [軸配置CSV](../../03-mechanical/gear_axis_schedule_bss20_candidate.csv) / [ケース部材CSV](../../03-mechanical/walnut_case_quote_parts_v0.4.csv)
- [表示器の取付仕様](../../03-mechanical/display-board-interface.md) / [背面取付・配線仕様](../../04-electronics/rear-harness-and-mount-candidate-v0.1.md)
- [入力ファイルのSHA-256](source_manifest.json) / [一台用組立文書](../assembly-plan.md)

SVGは文字を編集できます。日本語表示にはNoto Sans JP相当のフォントが必要です。28個/27軸は今回の数量例で、製品要求に固定しません。歯形、分解間隔、電装の破線予約域は模式です。

## 図面上の状態

| 内容 | 扱い |
|---|---|
| ケース外寸270×205×172、内寸246×181×148、P1〜P4、溝9×4、板外形 | 一台用の名目寸法・ケース見積基準 |
| 軸CSV・ブッシュØ8 H7・表示器M4取付パターン | 既存カタログ/設計値を転記。CAD小数桁は一律の加工公差ではない |
| 小型基板/取付台穴、M2.5/M3ねじ長さ、木部下穴、配線経路 | 実物と実スタックに合わせる通常の組立調整。推定寸法は指定しない |
| モーター支持金具 | 取付面z=108のみ定義済み。支持金具の形状・固定穴・締結具は机上詳細未定義。D05/A02に明示 |
| ケース接合、前ガード保持、材等級 | 工房見積回答で具体化。問い合わせ未送信 |
| 実機 | 未組立・未受入。表示コネクター、開閉配線、全負荷/温度/保護、噛み合い/滑り/音を完成品で確認 |

先行試験片や専用治具を購入前の必須条件にはしません。モーター支持金具の製作だけは詳細設計を要します。支持板はケース壁を閉じる前に溝へ組み込みます。

## 再生成

リポジトリルートで、`reportlab`、`pypdf`、`fonttools`を使えるPythonとNoto Sans JP TrueTypeフォントを指定します。変数フォントも内部で静的フォントへ変換できます。

```bash
python3 -B docs/08-manufacturing/generate_drawing_set.py --font /path/to/NotoSansJP.ttf
python3 tests/check_design.py
git diff --check
```

生成スクリプトはSVGとPDFを同じ描画命令から作り、軸数/共通軸数、原点変換、隣接軸間の20mmを入力時に照合します。既存の機械スクリプトをimportしないため、既存`__pycache__`を変更しません。
