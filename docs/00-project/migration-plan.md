# 設計資料・ソフトウェアの移行方針

1. 現行の製品要求、状態、残作業を `docs/10-desk-redesign/` と `docs/01-requirements/` に記録する。
2. 旧7軸設計の `execution/`、回路、CAD、各ブランチを履歴として保ち、現行コードや合格証拠に流用しない。
3. 新設計のソースは `firmware/cots_clock_core/` と `firmware/cots_clock_app/` に置き、ホストテストとESP-IDFビルドを継続的に実行する。
4. 個々の部品、ピン、価格、材料は一次資料や現物で確認するまで候補として扱う。
5. 実機表示、microSD、時刻復旧、モーター、電源、保護板、整備性はそれぞれの作業一覧で検証証拠が揃ってから完了扱いにする。

旧資料の経緯と現行要求への対応は[要求移行表](../10-desk-redesign/requirements-migration-v0.8-to-v0.20.csv)を参照します。
