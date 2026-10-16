# G1-82 実KiCad9検証ゲート

元のG1-82 CIは364端子のPython静的検証のみであり、KiCad自身に読み込ませていない。その欠落を解消するため独立の `g1-82-kicad-native-erc.yml` を追加した。Ubuntu24.04に公式KiCad9 PPA版を導入し、native XML netlist・SVGの生成およびERC JSONの生成を試みる。成果物はGitHub Actions artifactに保存され、後続の正規部品置換時の差分比較に用いる。

- **ゲートの意味を分離する:** native形式パーサー・エクスポートの成功と、電気的ERC違反0件は全く別の主張である。ERCに違反が残っても本workflowは設計を合格認定しない。仮想部品98個は全てPCB非実装指定であり、部品のピン電気種別もpassiveのためERC成功で実配線安全性を主張できない。
- **禁則:** G1-77/78/81の実配線元ネットおよびeFuse U7.EN 10k GND、28相OE HIGHを変更しない。KiCad ERCレポートの警告を抑制/除外して合格としない。製造0/6、19/48は維持。
- 実行後、ジョブログとダウンロード可能な native evidence をレビューし、エラーが発生した場合は先に回路図の構文/登録漏れを直す。
