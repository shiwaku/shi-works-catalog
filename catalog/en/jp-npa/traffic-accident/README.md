# Traffic accident statistics (main records)

[日本語](../../../jp-npa/traffic-accident/README.md)

Main records (one record per injury accident) of the National Police Agency's open traffic accident statistics, 2019-2025. Each row is one accident, with the location as a point and attributes on time, road, weather and the parties involved (A and B). Values are Japanese labels, not codes.

- File: [`jp-npa-traffic-accident.parquet`](https://catalog.shi-works.com/jp-npa/traffic-accident/jp-npa-traffic-accident.parquet) (GeoParquet 1.1, about 132 MB)
- Records: 2,182,298 accidents
- Coverage: all of Japan. Accidents counted in statistics years 2019-2025 (occurrence dates from 2015-12-12 to 2025-12-31)
- Coordinate reference system: EPSG:4326 (longitude/latitude)
- Injury accidents only. Property-damage-only accidents are not included.

## Counts

Counts by statistics year (`statistics_year`). They match the National Police Agency's published totals.

| Statistics year | Accidents | Fatal accidents | Killed | Injured |
|---|---:|---:|---:|---:|
| 2019 | 381,237 | 3,133 | 3,215 | 461,775 |
| 2020 | 309,178 | 2,784 | 2,839 | 369,476 |
| 2021 | 305,196 | 2,583 | 2,636 | 362,131 |
| 2022 | 300,839 | 2,550 | 2,611 | 356,602 |
| 2023 | 307,930 | 2,618 | 2,678 | 365,595 |
| 2024 | 290,895 | 2,598 | 2,663 | 344,395 |
| 2025 | 287,023 | 2,495 | 2,547 | 338,508 |

## Usage

DuckDB reads only the columns it needs, without downloading the whole file.

```sql
INSTALL httpfs; LOAD httpfs;
SELECT statistics_year, count(*) AS accidents, sum(fatalities) AS fatalities
FROM read_parquet('https://catalog.shi-works.com/jp-npa/traffic-accident/jp-npa-traffic-accident.parquet')
GROUP BY statistics_year
ORDER BY statistics_year;
```

QGIS and other software with the GDAL Parquet driver can open the downloaded file directly.

## Suitable and unsuitable uses

Suitable for:

- Finding where, when and on what road configurations accidents happen (maps, heat maps)
- Year-on-year trends, comparison between prefectures, counts by party type (pedestrian, bicycle, etc.)
- Analysing accidents on residential roads (roadway narrower than 5.5 m)

Not suitable for:

- Counting all accidents including property-damage-only ones (injury accidents only)
- Counting by fine age bands such as teenagers (ages are age groups; the youngest is 0-24)
- Identifying individuals or individual accidents

## Known issues

- **There are two ways to count years.** Counting by `statistics_year` (the year the accident was counted in the statistics) matches the published totals. Counting by `occurred_year` (the year it occurred) puts some year-end accidents in the following year's statistics, so the latest year comes out about 3% lower. Use `statistics_year` for trends.
- **Party A is the party most at fault; party B is the other party.** They are not victim/offender categories.
- **Fatal accidents are few:** 18,761 over seven years, so narrow filters leave only a few per year.
- **2020 fell by about 19% from the previous year because of COVID-19.** Look at shares as well as counts.
- For 2019-2021, the items added in 2022 (sunrise and sunset time, automatic transmission, Support Car, days since cognitive test, driving practice) are null.
- 171 records with invalid coordinates (150 at `(0, 0)`, 21 outside Japan) are kept with a null geometry. They count towards the totals but do not appear on maps.

## Columns

<!-- columns:start -->
| Column | Type | Description |
|---|---|---|
| `statistics_year` | int16 | Original column: 資料年次. Year in which the accident was counted in the statistics. Use this year to match the National Police Agency's published totals. Some accidents that occurred near the end of a year are counted in the following year, so it can differ from occurred_year. |
| `record_type` | string | Original column: 資料区分. Record type. Always "本票" (main record) in this dataset. |
| `prefecture` | string | Original column: 都道府県名. Name of the prefectural police that handled the accident (in Japanese). Hokkaido is split by regional headquarters, e.g. "北海道（札幌方面）". |
| `police_station` | string | Original column: 警察署等名. Name of the police station that handled the accident (in Japanese). |
| `record_number` | string | Original column: 本票番号. Record number within the police station (string, with leading zeros). Identifies one accident together with statistics_year, prefecture and police_station. |
| `accident_severity` | string | Original column: 事故内容. Whether the accident was fatal ("死亡事故") or injury-only ("負傷事故"). |
| `fatalities` | int16 | Original column: 死者数. Number of people killed (died within 24 hours of the accident). |
| `injuries` | int16 | Original column: 負傷者数. Number of people injured. |
| `route_name` | string | Original column: 路線名. Road route name (national route number, "一般市町村道" (municipal road), etc.). |
| `direction` | string | Original column: 上下線. Up or down carriageway. Null from 2022 onwards. |
| `location_code` | string | Original column: 地点コード. Location code along the route (string). |
| `municipality_code` | string | Original column: 市区町村コード. National Police Agency municipality code (3-digit string). It is numbered within each prefecture and is not the 5-digit local government code of the Ministry of Internal Affairs and Communications. |
| `occurred_at` | timestamp[us, tz=UTC] | Added column (not in the source). Date and time the accident occurred (Japan Standard Time). Built from the occurred_* columns. |
| `occurred_year` | int16 | Original column: 発生日時_年. Year the accident occurred. Use statistics_year for year-on-year trends. |
| `occurred_month` | int8 | Original column: 発生日時_月. Month the accident occurred. |
| `occurred_day` | int8 | Original column: 発生日時_日. Day of month the accident occurred. |
| `occurred_hour` | int8 | Original column: 発生日時_時. Hour the accident occurred (0-23). |
| `occurred_minute` | int8 | Original column: 発生日時_分. Minute the accident occurred (0-59). |
| `day_of_week` | string | Original column: 曜日(発生年月日). Day of the week of the accident (Japanese, e.g. "月" = Monday). |
| `holiday` | string | Original column: 祝日(発生年月日). Relation of the accident date to a public holiday ("当日" = on the holiday, "前日" = the day before, "その他" = other). |
| `sunrise_hour` | int8 | Original column: 日の出時刻　　時. Hour of sunrise on the day of the accident. Null for 2019-2021. |
| `sunrise_minute` | int8 | Original column: 日の出時刻　　分. Minute of sunrise on the day of the accident. Null for 2019-2021. |
| `sunset_hour` | int8 | Original column: 日の入り時刻　　時. Hour of sunset on the day of the accident. Null for 2019-2021. |
| `sunset_minute` | int8 | Original column: 日の入り時刻　　分. Minute of sunset on the day of the accident. Null for 2019-2021. |
| `day_night` | string | Original column: 昼夜. Day or night, including twilight categories (Japanese labels). |
| `weather` | string | Original column: 天候. Weather (Japanese labels, e.g. "晴" = clear, "雨" = rain). |
| `terrain` | string | Original column: 地形. Area type (Japanese labels, e.g. "市街地－人口集中" = urban, densely inhabited district). |
| `road_surface` | string | Original column: 路面状態. Road surface condition (Japanese labels). |
| `road_shape` | string | Original column: 道路形状. Road configuration, e.g. intersection or single road section (Japanese labels). |
| `roundabout_diameter` | string | Original column: 環状交差点の直径. Roundabout diameter class (Japanese labels). Null for 2019-2021. |
| `traffic_signal` | string | Original column: 信号機. Presence and type of traffic signal (Japanese labels). |
| `roadway_width` | string | Original column: 車道幅員. Roadway width class (Japanese labels). For intersections it describes both crossing roads. Used to identify residential roads (roadway narrower than 5.5 m). |
| `road_alignment` | string | Original column: 道路線形. Road alignment, e.g. straight/curve and grade (Japanese labels). |
| `collision_location` | string | Original column: 衝突地点. Where the collision occurred, e.g. road section or within an intersection (Japanese labels). |
| `zone_regulation` | string | Original column: ゾーン規制. Zone regulation such as "ゾーン30" (30 km/h zone) (Japanese labels). |
| `median` | string | Original column: 中央分離帯施設等. Median or centre-line facility (Japanese labels). |
| `sidewalk_separation` | string | Original column: 歩車道区分. Separation between sidewalk and roadway (Japanese labels). |
| `accident_type` | string | Original column: 事故類型. Accident type, e.g. vehicle-pedestrian, vehicle-vehicle rear-end, single vehicle (Japanese labels). |
| `party_a_stop_sign` | string | Original column: 一時停止規制_標識（当事者A）. Stop sign on party A's approach (Japanese labels). |
| `party_a_stop_marking` | string | Original column: 一時停止規制_表示（当事者A）. Stop road marking on party A's approach (Japanese labels). |
| `party_a_age_group` | string | Original column: 年齢（当事者A）. Age group of party A (Japanese labels, e.g. "0～24歳"). Not the exact age; the youngest class is 0-24, so teenagers cannot be separated. |
| `party_a_type` | string | Original column: 当事者種別（当事者A）. Type of party A, e.g. passenger car, pedestrian, bicycle (Japanese labels). |
| `party_a_vehicle_use` | string | Original column: 用途別（当事者A）. Use of party A's vehicle, e.g. private or commercial (Japanese labels). |
| `party_a_vehicle_shape` | string | Original column: 車両形状（当事者A）. Body shape of party A's vehicle (Japanese labels). |
| `party_a_speed_limit` | string | Original column: 速度規制（指定のみ）（当事者A）. Posted speed limit on party A's road (Japanese labels). Statutory default limits are not included. |
| `party_a_impact_point` | string | Original column: 車両の衝突部位（当事者A）. Impact points of party A's vehicle (first and second; Japanese labels). |
| `party_a_vehicle_damage` | string | Original column: 車両の損壊程度（当事者A）. Damage level of party A's vehicle (Japanese labels). |
| `party_a_airbag` | string | Original column: エアバッグの装備（当事者A）. Airbag fitted and deployed for party A's vehicle (Japanese labels). |
| `party_a_side_airbag` | string | Original column: サイドエアバッグの装備（当事者A）. Side airbag fitted and deployed for party A's vehicle (Japanese labels). |
| `party_a_injury_severity` | string | Original column: 人身損傷程度（当事者A）. Injury severity of party A (Japanese labels, e.g. "死亡" = killed, "負傷" = injured). |
| `party_a_automatic` | string | Original column: オートマチック車（当事者A）. Whether party A's vehicle is an automatic (Japanese labels). Applies to passenger cars and trucks only. Null for 2019-2021. Converted from the source codes using the official code table. |
| `party_a_support_car` | string | Original column: サポカー（当事者A）. Whether party A's vehicle is a "Support Car" with driver-assistance safety features (Japanese labels). Null for 2019-2021. Converted from the source codes using the official code table. |
| `party_a_cognitive_test_days` | string | Original column: 認知機能検査経過日数（当事者A）. Days between party A's cognitive function test and the accident (4-digit string). "9999" means no test taken or more than 2,555 days. Null for 2019-2021. Kept as in the source. |
| `party_a_driving_practice` | string | Original column: 運転練習の方法（当事者A）. How party A learned to drive (Japanese labels). Null for 2019-2021. Converted from the source codes using the official code table. "0" is not in the code table and is kept as in the source. |
| `party_b_stop_sign` | string | Original column: 一時停止規制_標識（当事者B）. Stop sign on party B's approach (Japanese labels). |
| `party_b_stop_marking` | string | Original column: 一時停止規制_表示（当事者B）. Stop road marking on party B's approach (Japanese labels). |
| `party_b_age_group` | string | Original column: 年齢（当事者B）. Age group of party B (Japanese labels, e.g. "0～24歳"). Not the exact age; the youngest class is 0-24, so teenagers cannot be separated. |
| `party_b_type` | string | Original column: 当事者種別（当事者B）. Type of party B, e.g. passenger car, pedestrian, bicycle (Japanese labels). |
| `party_b_vehicle_use` | string | Original column: 用途別（当事者B）. Use of party B's vehicle, e.g. private or commercial (Japanese labels). |
| `party_b_vehicle_shape` | string | Original column: 車両形状（当事者B）. Body shape of party B's vehicle (Japanese labels). |
| `party_b_speed_limit` | string | Original column: 速度規制（指定のみ）（当事者B）. Posted speed limit on party B's road (Japanese labels). Statutory default limits are not included. |
| `party_b_impact_point` | string | Original column: 車両の衝突部位（当事者B）. Impact points of party B's vehicle (first and second; Japanese labels). |
| `party_b_vehicle_damage` | string | Original column: 車両の損壊程度（当事者B）. Damage level of party B's vehicle (Japanese labels). |
| `party_b_airbag` | string | Original column: エアバッグの装備（当事者B）. Airbag fitted and deployed for party B's vehicle (Japanese labels). |
| `party_b_side_airbag` | string | Original column: サイドエアバッグの装備（当事者B）. Side airbag fitted and deployed for party B's vehicle (Japanese labels). |
| `party_b_injury_severity` | string | Original column: 人身損傷程度（当事者B）. Injury severity of party B (Japanese labels, e.g. "死亡" = killed, "負傷" = injured). |
| `party_b_automatic` | string | Original column: オートマチック車（当事者B）. Whether party B's vehicle is an automatic (Japanese labels). Applies to passenger cars and trucks only. Null for 2019-2021. Converted from the source codes using the official code table. |
| `party_b_support_car` | string | Original column: サポカー（当事者B）. Whether party B's vehicle is a "Support Car" with driver-assistance safety features (Japanese labels). Null for 2019-2021. Converted from the source codes using the official code table. |
| `party_b_cognitive_test_days` | string | Original column: 認知機能検査経過日数（当事者B）. Days between party B's cognitive function test and the accident (4-digit string). "9999" means no test taken or more than 2,555 days. Null for 2019-2021. Kept as in the source. |
| `party_b_driving_practice` | string | Original column: 運転練習の方法（当事者B）. How party B learned to drive (Japanese labels). Null for 2019-2021. Converted from the source codes using the official code table. "0" is not in the code table and is kept as in the source. |
<!-- columns:end -->

`bbox` is each feature's bounding box (the GeoParquet 1.1 bbox column) and `geometry` is the accident location.

## License and source

License: The [National Police Agency's terms of use](https://www.npa.go.jp/rules/index.html), based on the Public Data License (Version 1.0) (PDL1.0). You may copy, modify and redistribute the data if you credit the source and state that it has been modified. You may not use it in a way that suggests it was produced by the government.

Source: National Police Agency, "[Open data of traffic accident statistics](https://www.npa.go.jp/publications/statistics/koutsuu/opendata/index_opendata.html)" (main records, 2019-2025), modified

When showing the data on maps or in documents, credit it as:

> 出典: 警察庁「交通事故統計情報のオープンデータ」を加工して作成
> (Source: National Police Agency, open data of traffic accident statistics, modified)

## Processing

Made from the source data (Shift_JIS CSV with codes) as follows.

1. [npa-traffic-accident-converter](https://github.com/shiwaku/npa-traffic-accident-converter) (commit `583e891`): convert codes to labels using the official code tables, convert degree-minute-second coordinates to decimal degrees, and merge the seven years
2. `pipeline/build_parquet.py` in [npa-traffic-accident-analytics](https://github.com/shiwaku/npa-traffic-accident-analytics) (commit `c3e52f5`): add the statistics year column
3. [`scripts/jp-npa-traffic-accident/build.py`](https://github.com/shiwaku/shi-works-catalog/blob/main/scripts/jp-npa-traffic-accident/build.py) in this repository:
   - rename columns to English snake_case and cast counts, dates and times to integers
   - add the occurrence timestamp column (`occurred_at`)
   - convert the automatic transmission, Support Car and driving practice codes to labels
   - drop the coordinate columns and build the geometry; null the geometry for coordinates outside Japan
4. `portolan add` (portolan-cli 0.8.0): sort rows spatially (Hilbert curve), add the bbox column and write GeoParquet 1.1
