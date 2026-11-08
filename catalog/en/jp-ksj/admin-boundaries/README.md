# Administrative boundaries

[日本語](../../../jp-ksj/admin-boundaries/README.md)

The administrative boundary data (N03) of the National Land Numerical Information (KSJ), published by the Ministry of Land, Infrastructure, Transport and Tourism, as of 1 January 2026. Each row is one municipality, as a multipolygon. Designated cities are split into wards. Use it as the unit for counting points such as accidents or facilities by municipality.

- File: [`jp-ksj-admin-boundaries.parquet`](https://catalog.shi-works.com/jp-ksj/admin-boundaries/jp-ksj-admin-boundaries.parquet) (GeoParquet 1.1, about 179 MB)
- Rows: 1,905 (one per local government code)
- Coverage: all of Japan (47 prefectures). Boundaries as of 1 January 2026
- Coordinate reference system: EPSG:4326 (longitude/latitude). The source is JGD2011 (EPSG:6668); the values are unchanged

## Counts

| Type | Rows |
|---|---:|
| City (excluding designated cities) | 772 |
| Ward of a designated city (20 cities) | 171 |
| Special ward of Tokyo | 23 |
| Town | 743 |
| Village | 189 |
| Area of undetermined jurisdiction | 7 |
| Total | 1,905 |

Including the 20 designated cities, there are 792 cities.

## Usage

DuckDB reads the file without downloading it. This example counts the accidents of the traffic accident statistics ([jp-npa/traffic-accident](../../jp-npa/traffic-accident/README.md)) by municipality.

```sql
INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial;
SELECT a.admin_code,
       a.pref_name || a.municipality_name || coalesce(a.ward_name, '') AS name,
       count(*) AS accidents
FROM read_parquet('https://catalog.shi-works.com/jp-npa/traffic-accident/jp-npa-traffic-accident.parquet') t
JOIN read_parquet('https://catalog.shi-works.com/jp-ksj/admin-boundaries/jp-ksj-admin-boundaries.parquet') a
  ON ST_Intersects(a.geometry, t.geometry)
WHERE t.statistics_year = 2025
GROUP BY ALL
ORDER BY accidents DESC
LIMIT 5;
```

Software with the GDAL Parquet driver, such as QGIS, can open the downloaded file directly.

## Suitable and unsuitable uses

- Suitable as the unit for aggregating by municipality, as boundary lines on a map, and for finding which municipality a point is in.
- The boundaries are at about 1:25,000 scale. Do not use them for legal decisions on boundaries, such as parcel boundaries.
- The boundaries are as of 1 January 2026. Overlaying them on older data (such as accidents in 2019-2025) does not reflect boundary changes in between. There have been very few municipal mergers since 2020, but Hamamatsu reorganized its wards from seven to three on 1 January 2024, so be careful when comparing ward totals across years.

## Known issues

- **Seven rows are areas of undetermined jurisdiction.** Their boundaries are not settled, so they belong to no municipality. `admin_code` is "<prefecture code>000" and `municipality_name` is "所属未定地". Exclude them when aggregating by municipality.
- **Points on the sea or outside the coastline fall in no row.** Of the 2025 traffic accidents (287,020 with coordinates), 187 were outside every municipality, likely on reclaimed land, bridges or coastal roads beyond the boundary data.
- **The six villages of the Northern Territories are included.** The total area is about 377,976 km², close to the national land area published by the Geospatial Information Authority of Japan (which includes the Northern Territories).
- **Designated cities are split into wards.** To aggregate whole cities, group by `pref_code` and `municipality_name`.
- **Islands were separate rows in the source.** Rows with the same code are combined into one multipolygon here (the shapes are unchanged). The source has 125,130 rows.

## Columns

<!-- columns:start -->
| Column | Type | Description |
|---|---|---|
| `admin_code` | string | Original column: N03_007. Local government code (5-digit string, without the check digit) - 2-digit prefecture code followed by a 3-digit municipality code. Designated cities are split into wards, each with its own code. Areas of undetermined jurisdiction are "<prefecture code>000". Unique per row. |
| `pref_code` | string | Added column (not in the source). Prefecture code (2-digit string, 01 Hokkaido to 47 Okinawa). The first two digits of admin_code. |
| `pref_name` | string | Original column: N03_001. Prefecture name (in Japanese). |
| `subprefecture_name` | string | Original column: N03_002. Name of the Hokkaido subprefecture (in Japanese). Null outside Hokkaido. |
| `county_name` | string | Original column: N03_003. County name (in Japanese). Only for towns and villages that belong to a county; null for cities, wards and towns or villages outside a county. |
| `municipality_name` | string | Original column: N03_004. Municipality name (city, town, village, or special ward of Tokyo; in Japanese). On rows for wards of designated cities this is the city name (e.g. "札幌市") and the ward is in ward_name. "所属未定地" on rows for areas of undetermined jurisdiction. |
| `ward_name` | string | Original column: N03_005. Ward name of a designated city (in Japanese, e.g. "中央区"). Null outside designated cities. Tokyo's special wards are in municipality_name, not here. |
<!-- columns:end -->

`bbox` is each row's bounding box (the GeoParquet 1.1 bbox column) and `geometry` is the municipality boundary (multipolygon).

## License and source

License: CC-BY-4.0 ([Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)). The page of the KSJ administrative boundary data states its terms of use as "open data (CC_BY_4.0)". Also read the KSJ [terms of use](https://nlftp.mlit.go.jp/ksj/other/agreement_01.html) (based on the Government of Japan Standard Terms of Use (Version 2.0)). You may not use modified data in a way that suggests it was produced by the government.

Source: "[National Land Numerical Information (administrative boundaries)](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html)" (Ministry of Land, Infrastructure, Transport and Tourism) (as of 1 January 2026), modified. The source data is based on the administrative boundaries of the Geospatial Information Authority of Japan's "Digital Map (Basic Geospatial Information)" (approved for reproduction by the Director-General of the GSI under the Survey Act, R 7JHf 351).

When showing the data on maps or in documents, credit it in the form the KSJ terms give:

> 「国土数値情報（行政区域データ）」（国土交通省）（https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html）を加工して作成
> ("National Land Numerical Information (administrative boundaries)" (Ministry of Land, Infrastructure, Transport and Tourism) (https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html), modified)

Where a URL does not fit, such as the corner of a map, write: "National Land Numerical Information (administrative boundaries)" (Ministry of Land, Infrastructure, Transport and Tourism), modified, and make it a link. If you modify the data further, still state that it has been modified.

## Processing

Made from `N03-20260101.geojson` (125,130 rows) in the nationwide file `N03-20260101_GML.zip` of the KSJ download site, with [`scripts/jp-ksj-admin-boundaries/build.py`](https://github.com/shiwaku/shi-works-catalog/blob/main/scripts/jp-ksj-admin-boundaries/build.py) in this repository:

1. Rename the attributes (`N03_001` and so on) to English snake_case and add the prefecture code (`pref_code`)
2. Combine the island polygons of each local government code into one multipolygon (125,130 rows to 1,905 rows)
3. Change the declared coordinate reference system from JGD2011 (EPSG:6668) to EPSG:4326 (coordinate values unchanged)
4. With `portolan add`, sort along a Hilbert curve, add the bbox column and rewrite as GeoParquet 1.1
