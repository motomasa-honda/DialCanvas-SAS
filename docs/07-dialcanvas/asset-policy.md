# DialCanvas文字盤・参照素材の扱い

現行ファイル形式は `DialCanvas/faces/<名前>/face.jpg` と任意の `dial.json` です。JSONスキーマは `firmware/cots_clock_core/dial.schema.json`、サンプルは `firmware/cots_clock_core/examples/Forest/dial.json`、形式・描画規則は[dialファイル設計](../05-display/dial-file-and-rendering-design.md)に記録しています。

ファームウェアはmicroSDを読取専用で使います。既定文字盤は内蔵フォールバックとして扱い、ユーザー文字盤は英数字・`_`・`-`のフォルダー名、Baseline JPEG、800×800、8MB以下を前提に検査します。

参照画像は[アセット一覧](../assets/README.md)に出典・ハッシュ・許諾状態を記録します。参照用の概念画像は承認済み外観原本や公開利用許諾の証拠ではありません。個別の高解像度文字盤と利用条件はFG-038/OQ-10で確認します。
