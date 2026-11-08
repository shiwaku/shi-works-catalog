# Densely inhabited districts (2020)

[日本語](../../../jp-stat/densely-inhabited-districts-2020/README.md)

Boundary data of the densely inhabited districts (DID) of the 2020 Population Census, published by the Statistics Bureau of Japan on e-Stat. A densely inhabited district is an area within a municipality where adjacent basic unit blocks with a population density of 4,000 or more per km² together have a population of 5,000 or more. It is used as the extent of urban areas. Use it to tell whether an accident happened in an urban area, or to compare accidents in urban and suburban areas.

- File: [`jp-stat-densely-inhabited-districts-2020.parquet`](https://catalog.shi-works.com/jp-stat/densely-inhabited-districts-2020/jp-stat-densely-inhabited-districts-2020.parquet) (GeoParquet 1.1, about 20 MB)
- Rows: 1,463 (one per district, in 969 municipalities)
- Coverage: all of Japan, as of 1 October 2020 (the census date)
- Total population: 88,285,927 (about 70% of the census total of 126,146,099)
- Coordinate reference system: EPSG:4326 (longitude/latitude). The source is JGD2011 (EPSG:6668); the values are unchanged

## Usage

DuckDB reads the file without downloading it. This example counts the 2025 traffic accidents ([jp-npa/traffic-accident](../../jp-npa/traffic-accident/README.md)) that happened inside densely inhabited districts.

```sql
INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial;
CREATE TABLE did AS
SELECT * FROM read_parquet('https://catalog.shi-works.com/jp-stat/densely-inhabited-districts-2020/jp-stat-densely-inhabited-districts-2020.parquet');
SELECT count(*) AS accidents,
       count(*) FILTER (WHERE EXISTS (SELECT 1 FROM did d WHERE ST_Intersects(d.geometry, t.geometry))) AS in_did
FROM read_parquet('https://catalog.shi-works.com/jp-npa/traffic-accident/jp-npa-traffic-accident.parquet') t
WHERE t.statistics_year = 2025 AND t.geometry IS NOT NULL;
```

The result was 195,204 of 287,020 accidents (68.0%). Densely inhabited districts cover less than 4% of the land, but about two thirds of accidents happen in them.

Software with the GDAL Parquet driver, such as QGIS, can open the downloaded file directly.

## Suitable and unsuitable uses

- Suitable for classifying places as urban or not, for mapping the extent of urban areas, and for totals of DID population and area.
- The extents are as of the 2020 Census. Later development and population changes are not reflected. When the densely inhabited districts of the 2025 Census are published, they are planned to be added as a separate collection (`densely-inhabited-districts-2025`).
- Densely inhabited districts are statistical areas, not the urbanization promotion areas or zoning of city planning.

## Known issues

- **Densely inhabited districts are defined per municipality.** A district that touches one in a neighboring municipality on the map is still a separate row. `admin_code` and `did_number` together identify a row.
- **`did_number` is numbered within the municipality.** Districts are numbered from 1 in descending order of population (up to 9 in Toyota and in Kita Ward, Kobe). The same number in another municipality is a different district.
- **A point can fall in two rows.** A point on the shared edge of adjacent rows is in both. Among the 2025 traffic accidents there were six. When counting points, test with `EXISTS` as in the example above to avoid counting twice.
- **Municipality codes are as of 1 October 2020.** The wards of Hamamatsu (22131-22137) no longer exist after the ward reorganization of 1 January 2024. Some rows cannot be joined by code with the administrative boundaries ([jp-ksj/admin-boundaries](../../jp-ksj/admin-boundaries/README.md), as of 1 January 2026), so overlay them by location.
- **`area_km2` is the source value.** It differs from the area computed from the geometry by up to about 2 km² in some rows (such as Naka Ward, Hiroshima). When using areas, state which one you used.
- **Invalid shapes in five source rows were repaired.** Shapes that fail ST_IsValid, for example because of self-touching rings, were repaired with ST_MakeValid. The areas are unchanged.

## Columns

<!-- columns:start -->
| Column | Type | Description |
|---|---|---|
| `admin_code` | string | Added column (not in the source). Local government code (5-digit string, without the check digit), joining the source KEN (prefecture code) and CITY (municipality code). Codes as of 1 October 2020; designated cities are split into wards. |
| `pref_code` | string | Original column: KEN. Prefecture code (2-digit string, 01 Hokkaido to 47 Okinawa). |
| `municipality_name` | string | Original column: CITYNAME. Municipality name as of 1 October 2020 (in Japanese). Wards of designated cities include the city name, e.g. "札幌市北区". |
| `did_number` | int32 | Original column: CLASS. Number of the densely inhabited district within the municipality (from 1), in descending order of population; 1 is the largest. admin_code and did_number together identify a row. |
| `population` | int32 | Original column: JINKO. Population of the densely inhabited district (persons, 2020 Census). |
| `area_km2` | double | Original column: MENSEKI. Area of the densely inhabited district (km², two decimal places). The source value, not computed from the geometry. |
<!-- columns:end -->

`bbox` is each row's bounding box (the GeoParquet 1.1 bbox column) and `geometry` is the district boundary (multipolygon).

## License and source

License: the [terms of use of the e-Stat portal](https://www.e-stat.go.jp/terms-of-use), based on the Government of Japan Standard Terms of Use (Version 2.0). The boundary data is provided by the statistical GIS function of e-Stat, whose [terms](https://www.e-stat.go.jp/gis-terms) (article 6) say that the use of its content follows the e-Stat terms of use. You may copy, modify, redistribute and use the data commercially if you credit the source and state that it has been modified. You may not use it in a way that suggests it was produced by the government. The e-Stat terms of use are compatible with CC BY 4.0 (section 6, item c of the terms).

Source: "[2020 Population Census, boundary data of densely inhabited districts](https://www.e-stat.go.jp/gis/statmap-search?page=1&type=2&aggregateUnitForBoundary=D&toukeiCode=00200521&toukeiYear=2020&serveyId=D002005112020&datum=2011)" (Statistics Bureau of Japan), modified

When showing the data on maps or in documents, credit it in the form the e-Stat terms give:

> 「令和2年国勢調査 人口集中地区境界データ」（総務省統計局）（https://www.e-stat.go.jp/gis/statmap-search?page=1&type=2&aggregateUnitForBoundary=D&toukeiCode=00200521&toukeiYear=2020&serveyId=D002005112020&datum=2011）を加工して作成
> ("2020 Population Census, boundary data of densely inhabited districts" (Statistics Bureau of Japan) (https://www.e-stat.go.jp/gis/statmap-search?page=1&type=2&aggregateUnitForBoundary=D&toukeiCode=00200521&toukeiYear=2020&serveyId=D002005112020&datum=2011), modified)

Where a URL does not fit, such as the corner of a map, write: "2020 Population Census, boundary data of densely inhabited districts" (Statistics Bureau of Japan), modified, and make it a link. If you modify the data further, still state that it has been modified.

## Processing

Made from the per-prefecture shapefiles (latitude/longitude, 47 files) of "Population Census 2020, densely inhabited districts" in the e-Stat boundary data download, with [`scripts/jp-stat-densely-inhabited-districts-2020/build.py`](https://github.com/shiwaku/shi-works-catalog/blob/main/scripts/jp-stat-densely-inhabited-districts-2020/build.py) in this repository:

1. Concatenate the 47 shapefiles (1,463 rows)
2. Rename the attributes (`KEN` and so on) to English snake_case and add the local government code (`admin_code`)
3. Repair the invalid shapes (five rows) with ST_MakeValid and make all shapes multipolygons
4. Change the declared coordinate reference system from JGD2011 (EPSG:6668) to EPSG:4326 (coordinate values unchanged)
5. With `portolan add`, sort along a Hilbert curve, add the bbox column and rewrite as GeoParquet 1.1
