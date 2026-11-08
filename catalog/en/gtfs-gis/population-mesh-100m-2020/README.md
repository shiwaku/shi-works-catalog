# Simplified 100 m mesh population (2020)

[日本語](../../../gtfs-gis/population-mesh-100m-2020/README.md)

The "Simplified 100 m mesh population (2020)" created by Akira Nishizawa (Center for Spatial Information Science, the University of Tokyo) and published on GTFS-GIS.jp. It is an estimate that apportions the 250 m mesh population of the 2020 Census to 100 m cells by building floor area. Each row is one cell, as a polygon, with the total population and the population by age group. Use it to divide accident counts by population, or to count the population within a distance of stations or schools.

- File: [`gtfs-gis-population-mesh-100m-2020.parquet`](https://catalog.shi-works.com/gtfs-gis/population-mesh-100m-2020/gtfs-gis-population-mesh-100m-2020.parquet) (GeoParquet 1.1, about 172 MB)
- Rows: 4,979,919 (one per 100 m cell with population allocated; cells without population have no row)
- Coverage: all of Japan, as of 1 October 2020 (the census date)
- Total population: 126,128,118 (the published census figure is 126,146,099)
- Coordinate reference system: EPSG:4326 (longitude/latitude). The source is JGD2000 (EPSG:4612); the values are unchanged

## Usage

DuckDB reads the file without downloading it. This example counts the population around Chiyoda, Tokyo (139.73-139.78°E, 35.67-35.71°N); the result is about 192,000.

```sql
INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial;
SELECT round(sum(pop_total)) AS pop, round(sum(pop_65_over)) AS pop_65_over
FROM read_parquet('https://catalog.shi-works.com/gtfs-gis/population-mesh-100m-2020/gtfs-gis-population-mesh-100m-2020.parquet')
WHERE bbox.xmin >= 139.73 AND bbox.xmax <= 139.78
  AND bbox.ymin >= 35.67 AND bbox.ymax <= 35.71;
```

Filtering on the `bbox` column reads only the parts needed. Reading the whole country is about 172 MB.

For population by municipality, join with the administrative boundaries ([jp-ksj/admin-boundaries](../../jp-ksj/admin-boundaries/README.md)) on the centroid of each cell. The total for Tokyo is 14,043,484 (census: 14,047,594) and for Tottori 553,071 (census: 553,407), within 0.1% of the published figures. The nationwide join takes about four minutes in DuckDB on a desktop machine.

Software with the GDAL Parquet driver, such as QGIS, can open the downloaded file directly.

## Suitable and unsuitable uses

- Suitable for looking at population distribution over wide areas and for summing the population of an area (1 km from a station, 300 m from a road, a municipality, and so on).
- **The value of a single cell is not the actual population of that cell.** It is an estimate that mechanically apportions the 250 m mesh population by building floor area. Do not read a single cell as "this many people live here".
- According to the author, no population is in principle allocated to 100 m cells classified as "factory", "public facility land", "park or green space" or "golf course" in the urban land use mesh of the National Land Numerical Information.
- The population is the census resident (night-time) population, not the daytime population or people who commute to the area.

## Known issues

- **Values are fractional.** Since they are apportioned estimates, values like 0.01 occur. 777,371 cells have a total population below 1. The source CSV has four decimal places, so very small values became 0; 26 rows have a total population of 0.
- **The total population does not equal the sum of the age groups.** Nationwide, the total (126,128,118) is about 2.93 million more than the sum of ages 0-14, 15-64 and 65+ (123,196,289), probably because it includes persons of unknown age. To compute age shares, divide by the sum of the three groups.
- **Ages 75+ and 85+ are subsets.** `pop_75_over` is included in `pop_65_over`, and `pop_85_over` in `pop_75_over`. Do not add them together.
- **Coastal cells can fall outside the administrative boundaries.** Joining on cell centroids, 13,606 cells (60,887 people) fell in no municipality. This is why municipal totals are slightly below the published figures.
- **The source shapefiles are not used.** In the shapefiles in the per-primary-mesh zip files, the total population is 100 or 1,000 times too large for cells below 0.1 people (99,499 cells), making the national total 126,684,737. The CSV files in the same zip files have the correct values, and this dataset uses them. The shapes are computed from the mesh codes (they match the shapefile shapes).
- **The file for primary mesh 5434 is linked from the download page but cannot be retrieved (404).** It covers 36°00'-36°40'N, 134-135°E, open sea off Kyoto and Hyogo, and probably has no cells with population.

## Columns

<!-- columns:start -->
| Column | Type | Description |
|---|---|---|
| `mesh_code` | string | Original column: Meshcode. 100 m mesh code (10-digit string) - the 8-digit tertiary mesh (about 1 km) code followed by one digit each for the row (latitude) and column (longitude) of the cell when the tertiary mesh is divided into 10 by 10. Unique per row. |
| `pop_total` | double | Original column: PopT. Total population (estimated; fractional). The population of the census 250 m mesh, apportioned to 100 m cells by building floor area. Can be larger than the sum of the three age groups (by about 2.93 million nationwide), probably because it includes persons of unknown age. |
| `pop_0_14` | double | Original column: Pop0_14. Population aged 0-14 (estimated; fractional). |
| `pop_15_64` | double | Original column: Pop15_64. Population aged 15-64 (estimated; fractional). |
| `pop_65_over` | double | Original column: Pop65over. Population aged 65 and over (estimated; fractional). |
| `pop_75_over` | double | Original column: Pop75over. Population aged 75 and over (estimated; fractional). Included in pop_65_over. |
| `pop_85_over` | double | Original column: Pop85over. Population aged 85 and over (estimated; fractional). Included in pop_75_over. |
<!-- columns:end -->

`bbox` is each row's bounding box (the GeoParquet 1.1 bbox column) and `geometry` is the 100 m cell (polygon).

## License and source

License: CC-BY-4.0 ([Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)). The author's [explanation page](https://gtfs-gis.jp/teikyo/) states "ライセンスはCC-BYとします。" (the license is CC-BY). No version is given, so following the rules of this catalog ([docs/license.md](https://github.com/shiwaku/shi-works-catalog/blob/main/docs/license.md)) it is written as CC BY 4.0. The author accepts no liability for any damage arising from the data.

Source: "[Simplified 100 m mesh population (2020)](https://gtfs-gis.jp/teikyo/kani_100m_download2020.html)" (Akira Nishizawa, GTFS-GIS.jp), modified. The underlying population is the 250 m mesh tabulation of the 2020 Census (Statistics Bureau of Japan). The apportionment uses buildings from the Fundamental Geospatial Data of the Geospatial Information Authority of Japan and the urban land use mesh of the National Land Numerical Information ([method](https://gtfs-gis.jp/teikyo/method2020.pdf), in Japanese).

When showing the data on maps or in documents, credit it as follows:

> 「令和2年簡易100mメッシュ人口」（西澤明、GTFS-GIS.jp、CC BY 4.0）（https://gtfs-gis.jp/teikyo/kani_100m_download2020.html）を加工して作成
> ("Simplified 100 m mesh population (2020)" (Akira Nishizawa, GTFS-GIS.jp, CC BY 4.0) (https://gtfs-gis.jp/teikyo/kani_100m_download2020.html), modified)

Where a URL does not fit, such as the corner of a map, write: "Simplified 100 m mesh population (2020)" (Akira Nishizawa, GTFS-GIS.jp, CC BY 4.0), modified, and make it a link. If you modify the data further, still state that it has been modified.

## Processing

Made from the CSV files in the per-primary-mesh zip files (150) on the download page, with [`scripts/gtfs-gis-population-mesh-100m-2020/build.py`](https://github.com/shiwaku/shi-works-catalog/blob/main/scripts/gtfs-gis-population-mesh-100m-2020/build.py) in this repository:

1. Concatenate the 150 CSV files (4,979,919 rows, no duplicate mesh codes)
2. Rename the columns to English snake_case
3. Build the rectangle of each 100 m cell (3 seconds of latitude by 4.5 seconds of longitude) from its mesh code
4. With `portolan add`, sort along a Hilbert curve, add the bbox column and rewrite as GeoParquet 1.1
