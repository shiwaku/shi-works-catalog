# shi-works catalog

[English](en/README.md)

[shi-works.com](https://shi-works.com/) で配信している地理空間データのカタログです。[Portolan](https://github.com/portolan-sdi) の仕様に沿った STAC カタログで、データは `https://catalog.shi-works.com/` から直接読めます。

- カタログ: `https://catalog.shi-works.com/catalog.json`
- 構成: `<管理者>/<コレクション>/`。管理者は提供元の組織（`jp-npa` は警察庁、`jp-ksj` は国土数値情報、`gtfs-gis` は GTFS-GIS.jp、`jp-stat` は総務省統計局）

## コレクション

| テーマ | コレクション | 提供元 |
|---|---|---|
| 交通 | [交通事故統計（本票）](jp-npa/traffic-accident/README.md) | 警察庁 |
| 境界・住所 | [行政区域](jp-ksj/admin-boundaries/README.md) | 国土交通省（国土数値情報） |
| 人口 | [令和2年 簡易100mメッシュ人口](gtfs-gis/population-mesh-100m-2020/README.md) | 西澤明（GTFS-GIS.jp） |
| 人口 | [人口集中地区（2020年）](jp-stat/densely-inhabited-districts-2020/README.md) | 総務省統計局 |
