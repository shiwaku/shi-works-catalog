# shi-works catalog

[English](en/README.md)

[shi-works.com](https://shi-works.com/) で配信している地理空間データのカタログです。[Portolan](https://github.com/portolan-sdi) の仕様に沿った STAC カタログで、データは `https://catalog.shi-works.com/` から直接読めます。

- カタログ: `https://catalog.shi-works.com/catalog.json`
- 構成: `<管理者>/<コレクション>/`。管理者は提供元の組織（`jp-npa` は警察庁、`jp-ksj` は国土数値情報）

## コレクション

| テーマ | コレクション | 提供元 |
|---|---|---|
| 交通 | [交通事故統計（本票）](jp-npa/traffic-accident/README.md) | 警察庁 |
| 境界・住所 | [行政区域](jp-ksj/admin-boundaries/README.md) | 国土交通省（国土数値情報） |
