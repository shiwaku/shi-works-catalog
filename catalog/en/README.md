# shi-works catalog

[日本語](../README.md)

Catalog of geospatial data served by [shi-works.com](https://shi-works.com/). It is a STAC catalog following the [Portolan](https://github.com/portolan-sdi) specification, and the data can be read directly from `https://catalog.shi-works.com/`.

- Catalog: `https://catalog.shi-works.com/en/catalog.json` (Japanese, the primary version: `https://catalog.shi-works.com/catalog.json`)
- Layout: `<publisher>/<collection>/`. The publisher is the organization that provides the data (`jp-npa` is the National Police Agency, `jp-ksj` is the National Land Numerical Information, `gtfs-gis` is GTFS-GIS.jp, `jp-stat` is the Statistics Bureau of Japan, `jp-mlit` is the Ministry of Land, Infrastructure, Transport and Tourism)

## Collections

| Theme | Collection | Provider |
|---|---|---|
| transport | [Traffic accident statistics (main records)](jp-npa/traffic-accident/README.md) | National Police Agency |
| transport | [Road traffic census (2021)](jp-mlit/road-traffic-census-2021/README.md) | Ministry of Land, Infrastructure, Transport and Tourism |
| boundaries | [Administrative boundaries](jp-ksj/admin-boundaries/README.md) | Ministry of Land, Infrastructure, Transport and Tourism (National Land Numerical Information) |
| population | [Simplified 100 m mesh population (2020)](gtfs-gis/population-mesh-100m-2020/README.md) | Akira Nishizawa (GTFS-GIS.jp) |
| population | [Densely inhabited districts (2020)](jp-stat/densely-inhabited-districts-2020/README.md) | Statistics Bureau of Japan |
