# AGENTS.md — shi-works catalog

shi-works.com の地理空間データのカタログ。エージェント向けの手引き。

## 構成

- `catalog.json` → 管理者のカタログ（`<管理者>/catalog.json`）→ コレクション（`<管理者>/<コレクション>/collection.json`）の2段。
- 日本語が正本。英語版は `en/` に同じ形の木で置き、データは日本語の木のファイルを指す。
- データの URL は `https://catalog.shi-works.com/<管理者>/<コレクション>/<管理者>-<コレクション>.<拡張子>`。ベクタは GeoParquet 1.1（EPSG:4326、Hilbert 曲線の順、bbox 列あり）。
- コレクションごとの AGENTS.md に、落とし穴と集計の例がある。使う前に読むこと。

## コレクション

- `jp-npa/traffic-accident`: 交通事故統計（本票）。警察庁。人身事故1件ごとの点
- `jp-ksj/admin-boundaries`: 行政区域（N03）。国土交通省（国土数値情報）。市区町村ごとのマルチポリゴン。交通事故統計とは空間結合で組み合わせる
- `gtfs-gis/population-mesh-100m-2020`: 令和2年 簡易100mメッシュ人口。西澤明（GTFS-GIS.jp）。国勢調査の250mメッシュ人口を100mメッシュに按分した推計。範囲の人口の足し上げ、事故の発生率の分母に使う

## 用語集

日英で訳語をそろえるための一覧。英語版のメタデータはこれに従う。

| 日本語 | 英語 |
|---|---|
| 交通事故 | traffic accident |
| 人身事故 | injury accident |
| 物損事故 | property-damage-only accident |
| 死亡事故 | fatal accident |
| 本票 | main record |
| 当事者 | party |
| 生活道路 | residential road |
| 車道幅員 | roadway width |
| 統計に計上された年 | statistics year |
| 警察庁 | National Police Agency (NPA) |
| 国土交通省 | Ministry of Land, Infrastructure, Transport and Tourism (MLIT) |
| 国土数値情報 | National Land Numerical Information (KSJ) |
| 行政区域 | administrative boundaries |
| 市区町村 | municipality |
| 政令指定都市 | designated city |
| 所属未定地 | area of undetermined jurisdiction |
| 全国地方公共団体コード | local government code |
| 国勢調査 | census |
| 簡易100mメッシュ人口 | simplified 100 m mesh population |
| 按分 | apportion |
| 1次メッシュ・2次メッシュ・3次メッシュ | primary, secondary, tertiary mesh |
| 常住人口（夜間人口） | resident (night-time) population |
