# Road traffic census (2021)

[日本語](../../../jp-mlit/road-traffic-census-2021/README.md)

The section table (箇所別基本表) of the general traffic volume survey of the 2021 Road Traffic Census (全国道路・街路交通情勢調査), published by the Ministry of Land, Infrastructure, Transport and Tourism (MLIT). For each section of expressways, national highways, prefectural roads and the main city roads of designated cities, it has traffic volumes (12-hour and 24-hour, by direction, small and large vehicles), travel speeds (peak and off-peak), the congestion degree, and road conditions such as lanes, widths, sidewalks, medians, speed limits and roadside conditions. Use it to look up the traffic volume and structure of the roads where accidents happened, or to compare accident rates per traffic volume.

- File: [`jp-mlit-road-traffic-census-2021.parquet`](https://catalog.shi-works.com/jp-mlit/road-traffic-census-2021/jp-mlit-road-traffic-census-2021.parquet) (GeoParquet 1.1, about 56 MB)
- Rows: 99,417 (one per section, the same as the rows of the section table). 353 rows have no line (see Known issues)
- Coverage: all of Japan. Road conditions as of 1 April 2021; traffic volumes mainly from weekday observations and estimates in September to December 2021
- Total length: 196,237.7 km
- Coordinate reference system: EPSG:4326 (longitude/latitude). The source lines are JGD2000 (EPSG:4612); the values are unchanged

The number of sections (by road type) and the lengths were checked against the summary tables published by MLIT. Only two sections are classified differently between national highways and national expressways (29,418 and 2,364 sections here, 29,416 and 2,366 in the summary table).

## Usage

DuckDB reads the file without downloading it. This example counts the 2025 traffic accidents ([jp-npa/traffic-accident](../../jp-npa/traffic-accident/README.md)) within about 20 m of a census section.

```sql
INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial;
CREATE TABLE census AS
SELECT section_id, road_type, traffic_24h, length_km, geometry
FROM read_parquet('https://catalog.shi-works.com/jp-mlit/road-traffic-census-2021/jp-mlit-road-traffic-census-2021.parquet')
WHERE geometry IS NOT NULL;
SELECT count(*) AS accidents,
       count(*) FILTER (WHERE EXISTS (
         SELECT 1 FROM census c WHERE ST_DWithin(c.geometry, t.geometry, 0.0002))) AS near_census_road
FROM read_parquet('https://catalog.shi-works.com/jp-npa/traffic-accident/jp-npa-traffic-accident.parquet') t
WHERE t.statistics_year = 2025 AND t.geometry IS NOT NULL;
```

The result was 163,033 of 287,020 accidents (56.8%). The distance is in degrees: 0.0002 degrees is about 22 m north-south and 18-20 m east-west. Most of the rest probably happened on municipal roads, which the census does not cover.

Vehicle-kilometres by road type (24-hour traffic × length) are computed as follows. They are close to the values in MLIT's summary table of traffic volumes.

```sql
SELECT road_type, count(*) AS sections, round(sum(length_km), 1) AS length_km,
       round(sum(traffic_24h * length_km) / 1000) AS vehicle_km_24h_thousand
FROM census GROUP BY road_type ORDER BY road_type;
```

Software with the GDAL Parquet driver, such as QGIS, can open the downloaded file directly.

## Suitable and unsuitable uses

- Suitable for maps of traffic volume, travel speed and road structure on arterial roads, for overlays with accidents, and for accident rates per traffic volume.
- **Only arterial roads are covered**: expressways, national highways, prefectural roads and the main city roads of designated cities. Most municipal roads (residential streets) are not included.
- **About a third of the traffic volumes are estimates.** Sections that were not observed were estimated from the 2015 volume and the growth of other sections (`up_traffic_observed` and `down_traffic_observed` are "非観測（推定値）"). The MLIT document notes that estimates may differ from actual traffic. When using values for individual sections, check whether they were observed or estimated.
- The volumes are for autumn weekdays. Holidays and seasonal differences are not included.
- The survey was carried out while the effects of COVID-19 remained. Keep this in mind when comparing with the previous survey (2015).

## Known issues

- **353 sections have no line.** These are sections without a line in the MLIT visualization tool (ramps, connecting sections and so on). The rows are kept with a null geometry. They count in attribute totals but do not appear on maps.
- **The lines are not necessarily road centre lines.** The lines of the visualization tool are used as they are. Some sections are drawn with separate lines for each direction, so the line length is longer than the section length (18,570 sections have two or more lines). Use `length_km` for lengths.
- **Traffic volumes, travel speeds and road conditions are values of survey unit sections.** They were surveyed per unit section, which groups several basic sections, and all sections in a unit section have the same values (`traffic_unit_section_number` and so on). Averaging over rows gives more weight to unit sections split into many short sections, so weight by length.
- **Some sections have no traffic volume.** 3,413 sections, such as those that could not be estimated, have a null 24-hour traffic volume.
- **Codes are converted to labels.** Codes such as road type, administrator and roadside condition are converted to the category names (in Japanese) of the MLIT document. Yes/no columns (such as `has_railway_crossing`) are booleans. The source codes are given in the column descriptions.
- **Leading zeros dropped in the source were restored.** `admin_code` (municipality code), survey unit section numbers and area codes are 5-character strings.
- **Municipality codes are as of 1 April 2021.** Codes changed by later reorganizations, such as the wards of Hamamatsu, cannot be joined by code with the administrative boundaries ([jp-ksj/admin-boundaries](../../jp-ksj/admin-boundaries/README.md)).
- **The densely inhabited districts in the roadside condition are those of the 2015 Census.** Their extents differ from [Densely inhabited districts (2020)](../../jp-stat/densely-inhabited-districts-2020/README.md).
- **Some observation dates are those of individual surveys.** Sections using values from individual surveys after 2015 (`up_individual_survey_used` is true) have dates from 2016 to 2022. Their volumes are converted to 2021 values.

## Columns

<!-- columns:start -->
| Column | Type | Description |
|---|---|---|
| `section_id` | string | Original column: 交通調査基本区間番号. Traffic survey basic section number (11-character string): prefecture (2) + road type (1) + route number (4) + sequence (4), ascending from the start to the end of the route. One row per section; unique. |
| `pref_code` | string | Added column (not in the source). Prefecture code (2-character string), the first two characters of section_id. |
| `generation_split` | int16 | Original column: 世代管理番号（十の位）. Tens digit of the generation number: how many times the section has been split since the 2010 survey. |
| `generation_change` | int16 | Original column: 世代管理番号（一の位）. Units digit of the generation number: how many times the attributes of the section have changed. |
| `road_type` | string | Original column: 道路種別. Road type. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 1 national expressway (高速自動車国道), 2 urban expressway, 3 national highway (一般国道), 4 major local road (prefectural), 5 major local road (designated city), 6 general prefectural road, 7 general city road of a designated city. |
| `route_number` | int16 | Original column: 路線番号. Route number. The national highway number for national highways, the signed number for prefectural roads, and the number in the MLIT code table for expressways. |
| `route_name` | string | Original column: 路線名. Official route name (in Japanese). |
| `start_connection_type` | string | Original column: 起点側／接続区分. How the start point of the section connects. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): e.g. connection to another branch route, prefectural or municipal boundary, access point to a large facility, end of the branch route. |
| `start_connected_section_id` | string | Original column: 起点側／交通調査基本区間番号. Section number of the section connected at the start point (for connections to another branch route or at a prefectural boundary). |
| `start_connected_generation_split` | int16 | Original column: 起点側／世代管理番号（十の位）. Tens digit of the generation number of the section connected at the start point. |
| `start_connected_route_name` | string | Original column: 起点側／路線名等. Name of the route connected at the start point, or the boundary name (e.g. "○○市・△△町 境") at a municipal boundary (in Japanese). |
| `start_remarks` | string | Original column: 起点側／備考. Remarks on the start point, such as interchange or junction names on motorways, or the kind of large facility (in Japanese). |
| `end_connection_type` | string | Original column: 終点側／接続区分. How the end point of the section connects. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): e.g. connection to another branch route, prefectural or municipal boundary, access point to a large facility, end of the branch route. |
| `end_connected_section_id` | string | Original column: 終点側／交通調査基本区間番号. Section number of the section connected at the end point (for connections to another branch route or at a prefectural boundary). |
| `end_connected_generation_split` | int16 | Original column: 終点側／世代管理番号（十の位）. Tens digit of the generation number of the section connected at the end point. |
| `end_connected_route_name` | string | Original column: 終点側／路線名等. Name of the route connected at the end point, or the boundary name (e.g. "○○市・△△町 境") at a municipal boundary (in Japanese). |
| `end_remarks` | string | Original column: 終点側／備考. Remarks on the end point, such as interchange or junction names on motorways, or the kind of large facility (in Japanese). |
| `old_new_road_type` | string | Original column: 現道旧道区分. Whether the road is the current road, an old road or a new road. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 現道 current, 旧道 old, 新道 new, 旧道集約 aggregated old road. |
| `administrator` | string | Original column: 管理区分. Road administrator (the actual administrator for sections under delegated authority). Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): e.g. 国土交通大臣 Minister of MLIT, 都道府県知事又は都道府県 prefecture, 指定市の長又は指定市 designated city, expressway companies. |
| `admin_code` | string | Original column: 市区町村コード. Municipality code (5-character string, without the check digit), standard area code as of 1 April 2021, with designated cities split into wards. The leading zero dropped in the source has been restored. |
| `is_motorway` | bool | Original column: 自動車専用道路の別. True for motorway sections (national expressways or roads under Article 48-2 of the Road Act). Source codes 1 (motorway) and 0 (other). |
| `section_type` | string | Original column: 区間種別. Section type. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 通常区間 normal, 上下線分離区間 directionally separated, 複断面区間 multi-deck/parallel, 交通不能区間 impassable to motor vehicles, 循環区間 loop, 部分供用区間 partially open. |
| `separation_type` | string | Original column: 分離区間／分離区分. For separated or multi-deck sections, which direction or deck this row is. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 分離なし none, 上り線 up line, 下り線 down line or main deck, 上り複断面 up secondary deck, 複断面 secondary deck. |
| `separation_main_section_id` | string | Original column: 分離区間／交通調査基本区間番号. Section number of the corresponding main line, for up lines and secondary decks. |
| `length_km` | double | Original column: 区間延長（ｋｍ）. Section length along the road centre line (km, one decimal place). |
| `high_standard_road` | string | Original column: 高規格道路の別. Whether the road is a high-standard road. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 高規格幹線道路 high-standard arterial highway, 地域高規格道路 regional high-standard highway, 高規格道路以外の道路 other. |
| `national_road_designated_section` | string | Original column: 一般国道指定区間. Whether the national highway section is a designated section (managed by the national government). Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 一般国道（指定区間） designated, 一般国道（指定区間外） not designated, 一般国道以外の道路 not a national highway. |
| `one_way` | string | Original column: 一方通行フラグ. Permanent one-way restriction. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): なし none, 起点から終点方向 start to end, 終点から起点方向 end to start. |
| `h27_section_id` | string | Original column: 平成２７年度／交通調査基本区間番号. Section number in the 2015 survey corresponding to this section. Use it to join the 2015 data. |
| `h27_generation_split` | int16 | Original column: 平成２７年度／世代管理番号（十の位）. Tens digit of the generation number of the 2015 section. |
| `h27_generation_change` | int16 | Original column: 平成２７年度／世代管理番号（一の位）. Units digit of the generation number of the 2015 section. |
| `traffic_unit_area_code` | string | Original column: 交通量／都道府県指定市コード. Area code of the traffic volume survey (5-character string): code of the area (prefecture, designated city, etc.) within which the survey unit sections are numbered. Leading zeros restored. |
| `traffic_unit_section_number` | string | Original column: 交通量／調査単位区間番号. Traffic volume survey unit section number (5-character string): number of the survey unit section that groups basic sections. Identifies a unit section together with the area code. Leading zeros restored. Traffic volumes are the same for all basic sections in a unit section. |
| `up_observation_section_id` | string | Original column: 上り／観測地点交通調査基本区間番号. Section number of the basic section containing the observation point for the up direction (observed sections only). |
| `up_observation_place` | string | Original column: 上り／交通量観測地点地名. Place name of the observation point for the up direction, or the interchange section name (observed sections only; in Japanese). |
| `up_traffic_observed` | string | Original column: 上り／令和３年度調査交通量観測・非観測の別. Whether the up direction traffic volume was observed in 2021 or estimated. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 観測 observed, 非観測（推定値） estimated. Null where it could not be estimated. The MLIT document notes that estimates may differ from actual traffic. |
| `up_individual_survey_used` | bool | Original column: 上り／個別調査結果活用の別. True if the up direction traffic volume uses values from an individual survey after 2015. Source codes 1 (used) and 0 (not used). |
| `up_observation_hours` | string | Original column: 上り／１２時間・２４時間観測の別. Whether the up direction observation was 12-hour or 24-hour. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 12時間観測地点 12-hour, 24時間観測地点 24-hour, 調査対象区間外（非観測） not observed. |
| `up_observation_date` | string | Original column: 上り／交通量観測年月日. Observation date for the up direction (8-character string YYYYMMDD). The day is "00" when data from several days (e.g. permanent counters) were used. |
| `up_traffic_12h_small` | int32 | Original column: 上り／昼間１２時間自動車類交通量／小型車（台）. Daytime 12-hour (7:00-19:00) motor vehicle traffic in the up direction, small vehicles (vehicles). |
| `up_traffic_12h_large` | int32 | Original column: 上り／昼間１２時間自動車類交通量／大型車（台）. Daytime 12-hour (7:00-19:00) motor vehicle traffic in the up direction, large vehicles (vehicles). |
| `up_traffic_12h` | int32 | Original column: 上り／昼間１２時間自動車類交通量／合計（台）. Daytime 12-hour (7:00-19:00) motor vehicle traffic in the up direction, all vehicles (vehicles). |
| `up_traffic_24h_small` | int32 | Original column: 上り／２４時間自動車類交通量／小型車（台）. 24-hour motor vehicle traffic in the up direction, small vehicles (vehicles). |
| `up_traffic_24h_large` | int32 | Original column: 上り／２４時間自動車類交通量／大型車（台）. 24-hour motor vehicle traffic in the up direction, large vehicles (vehicles). |
| `up_traffic_24h` | int32 | Original column: 上り／２４時間自動車類交通量／合計（台）. 24-hour motor vehicle traffic in the up direction, all vehicles (vehicles). |
| `down_observation_section_id` | string | Original column: 下り／観測地点交通調査基本区間番号. Section number of the basic section containing the observation point for the down direction (observed sections only). |
| `down_observation_place` | string | Original column: 下り／交通量観測地点地名. Place name of the observation point for the down direction, or the interchange section name (observed sections only; in Japanese). |
| `down_traffic_observed` | string | Original column: 下り／令和３年度調査交通量観測・非観測の別. Whether the down direction traffic volume was observed in 2021 or estimated. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 観測 observed, 非観測（推定値） estimated. Null where it could not be estimated. The MLIT document notes that estimates may differ from actual traffic. |
| `down_individual_survey_used` | bool | Original column: 下り／個別調査結果活用の別. True if the down direction traffic volume uses values from an individual survey after 2015. Source codes 1 (used) and 0 (not used). |
| `down_observation_hours` | string | Original column: 下り／１２時間・２４時間観測の別. Whether the down direction observation was 12-hour or 24-hour. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 12時間観測地点 12-hour, 24時間観測地点 24-hour, 調査対象区間外（非観測） not observed. |
| `down_observation_date` | string | Original column: 下り／交通量観測年月日. Observation date for the down direction (8-character string YYYYMMDD). The day is "00" when data from several days (e.g. permanent counters) were used. |
| `down_traffic_12h_small` | int32 | Original column: 下り／昼間１２時間自動車類交通量／小型車（台）. Daytime 12-hour (7:00-19:00) motor vehicle traffic in the down direction, small vehicles (vehicles). |
| `down_traffic_12h_large` | int32 | Original column: 下り／昼間１２時間自動車類交通量／大型車（台）. Daytime 12-hour (7:00-19:00) motor vehicle traffic in the down direction, large vehicles (vehicles). |
| `down_traffic_12h` | int32 | Original column: 下り／昼間１２時間自動車類交通量／合計（台）. Daytime 12-hour (7:00-19:00) motor vehicle traffic in the down direction, all vehicles (vehicles). |
| `down_traffic_24h_small` | int32 | Original column: 下り／２４時間自動車類交通量／小型車（台）. 24-hour motor vehicle traffic in the down direction, small vehicles (vehicles). |
| `down_traffic_24h_large` | int32 | Original column: 下り／２４時間自動車類交通量／大型車（台）. 24-hour motor vehicle traffic in the down direction, large vehicles (vehicles). |
| `down_traffic_24h` | int32 | Original column: 下り／２４時間自動車類交通量／合計（台）. 24-hour motor vehicle traffic in the down direction, all vehicles (vehicles). |
| `traffic_12h_small` | int32 | Original column: 昼間１２時間自動車類交通量（上下合計）／小型車（台）. Daytime 12-hour (7:00-19:00) motor vehicle traffic, both directions, small vehicles (vehicles). |
| `traffic_12h_large` | int32 | Original column: 昼間１２時間自動車類交通量（上下合計）／大型車（台）. Daytime 12-hour (7:00-19:00) motor vehicle traffic, both directions, large vehicles (vehicles). |
| `traffic_12h` | int32 | Original column: 昼間１２時間自動車類交通量（上下合計）／合計（台）. Daytime 12-hour (7:00-19:00) motor vehicle traffic, both directions, all vehicles (vehicles). |
| `traffic_24h_small` | int32 | Original column: ２４時間自動車類交通量（上下合計）／小型車（台）. 24-hour motor vehicle traffic, both directions, small vehicles (vehicles). For 12-hour observations and estimated sections it is estimated from the day-night ratio. |
| `traffic_24h_large` | int32 | Original column: ２４時間自動車類交通量（上下合計）／大型車（台）. 24-hour motor vehicle traffic, both directions, large vehicles (vehicles). For 12-hour observations and estimated sections it is estimated from the day-night ratio. |
| `traffic_24h` | int32 | Original column: ２４時間自動車類交通量（上下合計）／合計（台）. 24-hour motor vehicle traffic, both directions, all vehicles (vehicles). This is the column usually used for traffic volume. For 12-hour observations and estimated sections it is estimated from the day-night ratio. |
| `day_night_ratio` | double | Original column: 昼夜率. Day-night ratio (24-hour traffic / daytime 12-hour traffic). |
| `peak_ratio_12h_pct` | double | Original column: 昼間１２時間ピーク比率（％）. Peak-hour ratio (%): traffic in the busiest hour / daytime 12-hour traffic. |
| `large_vehicle_ratio_12h_pct` | double | Original column: 昼間１２時間大型車混入率（％）. Share of large vehicles in daytime 12-hour traffic (%). |
| `congestion_degree` | double | Original column: 混雑度. Congestion degree (daytime 12-hour traffic / 12-hour traffic capacity). Above 1.0, traffic exceeds capacity. |
| `h27_traffic_unit_area_code` | string | Original column: 平成２７年度／交通量／都道府県指定市コード. Area code of the corresponding 2015 traffic survey unit section (5-character string): code of the area (prefecture, designated city, etc.) within which the survey unit sections are numbered. Leading zeros restored. |
| `h27_traffic_unit_section_number` | string | Original column: 平成２７年度／交通量／調査単位区間番号. Corresponding 2015 traffic survey unit section number (5-character string): number of the survey unit section that groups basic sections. Identifies a unit section together with the area code. Leading zeros restored. |
| `h27_traffic_12h` | int32 | Original column: 平成２７年度／昼間１２時間自動車類交通量（台）. Daytime 12-hour motor vehicle traffic in 2015, both directions (vehicles). |
| `h27_traffic_24h` | int32 | Original column: 平成２７年度／２４時間自動車類交通量（台）. 24-hour motor vehicle traffic in 2015, both directions (vehicles). |
| `speed_unit_area_code` | string | Original column: 旅行速度／都道府県指定市コード. Area code of the travel speed survey (5-character string): code of the area (prefecture, designated city, etc.) within which the survey unit sections are numbered. Leading zeros restored. |
| `speed_unit_section_number` | string | Original column: 旅行速度／調査単位区間番号. Travel speed survey unit section number (5-character string): number of the survey unit section that groups basic sections. Identifies a unit section together with the area code. Leading zeros restored. |
| `peak_up_speed_measured` | string | Original column: 朝夕（混雑時）／上り／旅行速度計測・非計測の別. Whether the travel speed for peak hours (7:00-9:00 and 17:00-19:00), up direction was measured. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 計測 measured, 非計測（共通） filled from the opposite direction, another time band or an adjacent section, 非計測（H27調査値） filled with the 2015 value. |
| `peak_up_speed_small` | double | Original column: 朝夕（混雑時）／上り／旅行速度／小型車（ｋｍ／ｈ）. Travel speed for peak hours (7:00-9:00 and 17:00-19:00), up direction, small vehicles (km/h), including stops at signals and in congestion. By vehicle type only for sections surveyed with ETC2.0 probe data. |
| `peak_up_speed_large` | double | Original column: 朝夕（混雑時）／上り／旅行速度／大型車（ｋｍ／ｈ）. Travel speed for peak hours (7:00-9:00 and 17:00-19:00), up direction, large vehicles (km/h), including stops at signals and in congestion. By vehicle type only for sections surveyed with ETC2.0 probe data. |
| `peak_up_speed` | double | Original column: 朝夕（混雑時）／上り／旅行速度／合計（ｋｍ／ｈ）. Travel speed for peak hours (7:00-9:00 and 17:00-19:00), up direction, all vehicles (km/h), including stops at signals and in congestion. |
| `peak_up_probe_count_small` | int32 | Original column: 朝夕（混雑時）／上り／取得件数／小型車（件）. Number of ETC2.0 probe records used for the travel speed for peak hours (7:00-9:00 and 17:00-19:00), up direction, small vehicles. |
| `peak_up_probe_count_large` | int32 | Original column: 朝夕（混雑時）／上り／取得件数／大型車（件）. Number of ETC2.0 probe records used for the travel speed for peak hours (7:00-9:00 and 17:00-19:00), up direction, large vehicles. |
| `peak_up_probe_count` | int32 | Original column: 朝夕（混雑時）／上り／取得件数／合計（件）. Number of ETC2.0 probe records used for the travel speed for peak hours (7:00-9:00 and 17:00-19:00), up direction, all vehicles. |
| `peak_down_speed_measured` | string | Original column: 朝夕（混雑時）／下り／旅行速度計測・非計測の別. Whether the travel speed for peak hours (7:00-9:00 and 17:00-19:00), down direction was measured. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 計測 measured, 非計測（共通） filled from the opposite direction, another time band or an adjacent section, 非計測（H27調査値） filled with the 2015 value. |
| `peak_down_speed_small` | double | Original column: 朝夕（混雑時）／下り／旅行速度／小型車（ｋｍ／ｈ）. Travel speed for peak hours (7:00-9:00 and 17:00-19:00), down direction, small vehicles (km/h), including stops at signals and in congestion. By vehicle type only for sections surveyed with ETC2.0 probe data. |
| `peak_down_speed_large` | double | Original column: 朝夕（混雑時）／下り／旅行速度／大型車（ｋｍ／ｈ）. Travel speed for peak hours (7:00-9:00 and 17:00-19:00), down direction, large vehicles (km/h), including stops at signals and in congestion. By vehicle type only for sections surveyed with ETC2.0 probe data. |
| `peak_down_speed` | double | Original column: 朝夕（混雑時）／下り／旅行速度／合計（ｋｍ／ｈ）. Travel speed for peak hours (7:00-9:00 and 17:00-19:00), down direction, all vehicles (km/h), including stops at signals and in congestion. |
| `peak_down_probe_count_small` | int32 | Original column: 朝夕（混雑時）／下り／取得件数／小型車（件）. Number of ETC2.0 probe records used for the travel speed for peak hours (7:00-9:00 and 17:00-19:00), down direction, small vehicles. |
| `peak_down_probe_count_large` | int32 | Original column: 朝夕（混雑時）／下り／取得件数／大型車（件）. Number of ETC2.0 probe records used for the travel speed for peak hours (7:00-9:00 and 17:00-19:00), down direction, large vehicles. |
| `peak_down_probe_count` | int32 | Original column: 朝夕（混雑時）／下り／取得件数／合計（件）. Number of ETC2.0 probe records used for the travel speed for peak hours (7:00-9:00 and 17:00-19:00), down direction, all vehicles. |
| `offpeak_up_speed_measured` | string | Original column: 昼間（非混雑時）／上り／旅行速度計測・非計測の別. Whether the travel speed for off-peak daytime (9:00-17:00), up direction was measured. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 計測 measured, 非計測（共通） filled from the opposite direction, another time band or an adjacent section, 非計測（H27調査値） filled with the 2015 value. |
| `offpeak_up_speed_small` | double | Original column: 昼間（非混雑時）／上り／旅行速度／小型車（ｋｍ／ｈ）. Travel speed for off-peak daytime (9:00-17:00), up direction, small vehicles (km/h), including stops at signals and in congestion. By vehicle type only for sections surveyed with ETC2.0 probe data. |
| `offpeak_up_speed_large` | double | Original column: 昼間（非混雑時）／上り／旅行速度／大型車（ｋｍ／ｈ）. Travel speed for off-peak daytime (9:00-17:00), up direction, large vehicles (km/h), including stops at signals and in congestion. By vehicle type only for sections surveyed with ETC2.0 probe data. |
| `offpeak_up_speed` | double | Original column: 昼間（非混雑時）／上り／旅行速度／合計（ｋｍ／ｈ）. Travel speed for off-peak daytime (9:00-17:00), up direction, all vehicles (km/h), including stops at signals and in congestion. |
| `offpeak_up_probe_count_small` | int32 | Original column: 昼間（非混雑時）／上り／取得件数／小型車（件）. Number of ETC2.0 probe records used for the travel speed for off-peak daytime (9:00-17:00), up direction, small vehicles. |
| `offpeak_up_probe_count_large` | int32 | Original column: 昼間（非混雑時）／上り／取得件数／大型車（件）. Number of ETC2.0 probe records used for the travel speed for off-peak daytime (9:00-17:00), up direction, large vehicles. |
| `offpeak_up_probe_count` | int32 | Original column: 昼間（非混雑時）／上り／取得件数／合計（件）. Number of ETC2.0 probe records used for the travel speed for off-peak daytime (9:00-17:00), up direction, all vehicles. |
| `offpeak_down_speed_measured` | string | Original column: 昼間（非混雑時）／下り／旅行速度計測・非計測の別. Whether the travel speed for off-peak daytime (9:00-17:00), down direction was measured. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 計測 measured, 非計測（共通） filled from the opposite direction, another time band or an adjacent section, 非計測（H27調査値） filled with the 2015 value. |
| `offpeak_down_speed_small` | double | Original column: 昼間（非混雑時）／下り／旅行速度／小型車（ｋｍ／ｈ）. Travel speed for off-peak daytime (9:00-17:00), down direction, small vehicles (km/h), including stops at signals and in congestion. By vehicle type only for sections surveyed with ETC2.0 probe data. |
| `offpeak_down_speed_large` | double | Original column: 昼間（非混雑時）／下り／旅行速度／大型車（ｋｍ／ｈ）. Travel speed for off-peak daytime (9:00-17:00), down direction, large vehicles (km/h), including stops at signals and in congestion. By vehicle type only for sections surveyed with ETC2.0 probe data. |
| `offpeak_down_speed` | double | Original column: 昼間（非混雑時）／下り／旅行速度／合計（ｋｍ／ｈ）. Travel speed for off-peak daytime (9:00-17:00), down direction, all vehicles (km/h), including stops at signals and in congestion. |
| `offpeak_down_probe_count_small` | int32 | Original column: 昼間（非混雑時）／下り／取得件数／小型車（件）. Number of ETC2.0 probe records used for the travel speed for off-peak daytime (9:00-17:00), down direction, small vehicles. |
| `offpeak_down_probe_count_large` | int32 | Original column: 昼間（非混雑時）／下り／取得件数／大型車（件）. Number of ETC2.0 probe records used for the travel speed for off-peak daytime (9:00-17:00), down direction, large vehicles. |
| `offpeak_down_probe_count` | int32 | Original column: 昼間（非混雑時）／下り／取得件数／合計（件）. Number of ETC2.0 probe records used for the travel speed for off-peak daytime (9:00-17:00), down direction, all vehicles. |
| `daytime_12h_speed_up` | double | Original column: 昼間１２時間平均旅行速度（時間帯別交通量加重）／上り（ｋｍ／ｈ）. Daytime 12-hour average travel speed, up direction (km/h), weighted by hourly traffic. |
| `daytime_12h_speed_down` | double | Original column: 昼間１２時間平均旅行速度（時間帯別交通量加重）／下り（ｋｍ／ｈ）. Daytime 12-hour average travel speed, down direction (km/h), weighted by hourly traffic. |
| `h27_speed_unit_area_code` | string | Original column: 平成２７年度／旅行速度／都道府県指定市コード. Area code of the corresponding 2015 travel speed survey unit section (5-character string): code of the area (prefecture, designated city, etc.) within which the survey unit sections are numbered. Leading zeros restored. |
| `h27_speed_unit_section_number` | string | Original column: 平成２７年度／旅行速度／調査単位区間番号. Corresponding 2015 travel speed survey unit section number (5-character string): number of the survey unit section that groups basic sections. Identifies a unit section together with the area code. Leading zeros restored. |
| `h27_peak_up_speed` | double | Original column: 平成２７年度／混雑時／上り／平均旅行速度（ｋｍ／ｈ）. Average travel speed in 2015 for peak hours, up direction (km/h). |
| `h27_peak_down_speed` | double | Original column: 平成２７年度／混雑時／下り／平均旅行速度（ｋｍ／ｈ）. Average travel speed in 2015 for peak hours, down direction (km/h). |
| `h27_offpeak_up_speed` | double | Original column: 平成２７年度／昼間非混雑時／上り／平均旅行速度（ｋｍ／ｈ）. Average travel speed in 2015 for off-peak daytime, up direction (km/h). |
| `h27_offpeak_down_speed` | double | Original column: 平成２７年度／昼間非混雑時／下り／平均旅行速度（ｋｍ／ｈ）. Average travel speed in 2015 for off-peak daytime, down direction (km/h). |
| `road_unit_area_code` | string | Original column: 道路状況／都道府県指定市コード. Area code of the road condition survey (5-character string): code of the area (prefecture, designated city, etc.) within which the survey unit sections are numbered. Leading zeros restored. |
| `road_unit_section_number` | string | Original column: 道路状況／調査単位区間番号. Road condition survey unit section number (5-character string): number of the survey unit section that groups basic sections. Identifies a unit section together with the area code. Leading zeros restored. Road conditions such as widths are those of the representative cross-section of this unit section. |
| `improved_pct` | double | Original column: 区間延長／改良済み区間率（％）. Share of the length improved to the Road Structure Ordinance standards (%). |
| `improved_5_5m_pct` | double | Original column: 区間延長／5.5ｍ以上改良済み区間率（％）. Share of the length improved with a width of 5.5 m or more (%). |
| `road_width_m` | double | Original column: 幅員構成／道路部幅員（ｍ）. Road width: roadway, median, shoulders, planting strips, sidewalks, etc. (m). |
| `roadway_section_width_m` | double | Original column: 幅員構成／車道部幅員（ｍ）. Roadway section width: lanes, stopping lanes, shoulders and median (m). Wider than the roadway width (roadway_width_m). |
| `roadway_width_m` | double | Original column: 幅員構成／車道幅員（ｍ）. Roadway width: lanes and stopping lanes, excluding median and shoulders (m). |
| `median_width_m` | double | Original column: 幅員構成／中央帯幅員（ｍ）. Median width (m). |
| `sidewalk_width_up_m` | double | Original column: 幅員構成／歩道幅員／上り（ｍ）. Sidewalk width (including shared bicycle-pedestrian paths), up side (m). |
| `sidewalk_width_down_m` | double | Original column: 幅員構成／歩道幅員／下り（ｍ）. Sidewalk width (including shared bicycle-pedestrian paths), down side (m). |
| `bicycle_track_width_up_m` | double | Original column: 幅員構成／自転車道幅員／上り（ｍ）. Bicycle track width, up side (m). |
| `bicycle_track_width_down_m` | double | Original column: 幅員構成／自転車道幅員／下り（ｍ）. Bicycle track width, down side (m). |
| `stopping_lane_width_up_m` | double | Original column: 幅員構成／停車帯等幅員／上り（ｍ）. Width of stopping lanes and slow lanes (including bicycle lanes), up side (m). |
| `stopping_lane_width_down_m` | double | Original column: 幅員構成／停車帯等幅員／下り（ｍ）. Width of stopping lanes and slow lanes (including bicycle lanes), down side (m). |
| `lanes` | int16 | Original column: 車線数. Number of lanes (both directions, except one-way sections), excluding climbing, passing and turning lanes. Single-lane roads with a roadway narrower than 5.5 m are 1. |
| `sidewalk_pct` | double | Original column: 交通安全施設等／歩道設置率（％）. Share of the length with a sidewalk (including shared paths) on one or both sides (%). |
| `bike_ped_path_pct` | double | Original column: 交通安全施設等／自転車歩行者道設置率（％）. Share of the length with a shared bicycle-pedestrian path on one or both sides (%). |
| `bicycle_track_pct` | double | Original column: 交通安全施設等／自転車道設置率（％）. Share of the length with a bicycle track on one or both sides (%). |
| `bicycle_lane_pct` | double | Original column: 交通安全施設等／自転車レーン設置率（％）. Share of the length with a bicycle lane on one or both sides (%). |
| `sidewalk_both_sides_pct` | double | Original column: 交通安全施設等／両側歩道設置率（％）. Share of the length with sidewalks on both sides (%). |
| `bike_ped_path_both_sides_pct` | double | Original column: 交通安全施設等／両側自転車歩行者道設置率（％）. Share of the length with shared paths on both sides (%). |
| `bicycle_track_both_sides_pct` | double | Original column: 交通安全施設等／両側自転車道設置率（％）. Share of the length with bicycle tracks on both sides (%). |
| `bicycle_lane_both_sides_pct` | double | Original column: 交通安全施設等／両側自転車レーン設置率（％）. Share of the length with bicycle lanes on both sides (%). |
| `sidewalk_typical_width_m` | double | Original column: 交通安全施設等／歩道代表幅員（ｍ）. Typical sidewalk width (m). |
| `bicycle_track_typical_width_m` | double | Original column: 交通安全施設等／自転車道代表幅員（ｍ）. Typical bicycle track width (m). |
| `bus_route_pct` | double | Original column: バス路線／バス路線延長率（％）. Share of the length served by route buses (%). |
| `bus_lane` | string | Original column: バス路線／バス優先・専用レーンの有無. Bus priority or bus-only lane. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): バス優先レーンあり priority lane, バス専用レーンあり bus-only lane, なし none. |
| `signalized_intersections_per_km` | double | Original column: 交差点密度／信号交差点（箇所／ｋｍ）. Signalized intersections per km, including signalized pedestrian crossings. |
| `unsignalized_intersections_per_km` | double | Original column: 交差点密度／信号のない交差点（箇所／ｋｍ）. Unsignalized intersections per km, excluding driveways. |
| `rep_signal_green_ratio_pct` | int16 | Original column: 代表信号交差点／青時間比（％）. Green time ratio of the representative signalized intersection (%). Only for sections with 3+ lanes (or 2+ one-way) and a signalized intersection. |
| `rep_signal_right_turn_lane` | string | Original column: 代表信号交差点／右折専用車線の有無等. Right-turn lane at the representative signalized intersection. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 右折専用車線あり yes, なし no, 右折禁止 right turn prohibited, 調査路線が右折 the surveyed route turns right. |
| `has_railway_crossing` | bool | Original column: 鉄道との平面交差箇所の有無. True if there is a level crossing with a railway. Source codes 1 (yes) and 2 (no). |
| `speed_limit_kmh` | int16 | Original column: 指定最高速度（ｋｍ／ｈ）. Speed limit (km/h): the posted limit, or the statutory limit where none is posted. |
| `has_climbing_lane_up` | bool | Original column: 付加車線及び登坂車線設置箇所の有無／上り. True if there is an additional or climbing lane in the up direction. Source codes 1 (yes) and 2 (no). |
| `has_climbing_lane_down` | bool | Original column: 付加車線及び登坂車線設置箇所の有無／下り. True if there is an additional or climbing lane in the down direction. Source codes 1 (yes) and 2 (no). |
| `roadside_status` | string | Original column: 代表沿道状況. Representative roadside condition (the longest in the unit section). Densely inhabited districts are those of the 2015 Census. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 人口集中地区かつ商業地域 DID and commercial zone, 人口集中地区 DID, その他市街部 other built-up area, 平地部 flat rural, 山地部 mountainous. |
| `median_type` | string | Original column: 中央分離帯／中央分離帯の種類. Type of median. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): from physical separation and guard fences to rubber poles, markings only, and no median. |
| `median_installation` | string | Original column: 中央分離帯／中央分離帯の設置状況. How much of the section has the median (only for physical medians). Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 区間全体 whole section, 一部区間 most of it, あまり設置されていない little. |
| `tramway` | string | Original column: 軌道の有無. Tramway on the roadway. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 軌道あり with tram tracks (driving on the tracks allowed, partly allowed or not allowed), 軌道なし none. |
| `bicycle_on_sidewalk` | string | Original column: 自転車通行可能区分. Whether bicycles may use the sidewalks or bicycle tracks. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 全区間通行可 whole section, 一部通行可又は通行可能な歩道なし partly or none. |
| `weather_regulation` | string | Original column: 異常気象時等通行規制区分. Traffic restrictions in severe weather and winter closures. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): rainfall, snow or other restrictions, with or without winter closure. |
| `has_reversible_lane` | bool | Original column: リバーシブルレーン運用の有無. True if a reversible lane is operated. Source codes 1 (yes) and 2 (no). |
| `access_control` | string | Original column: アクセスコントロール. Access control. Values are the category names (in Japanese) of the MLIT explanation document, converted from the source codes (listed with their codes in the Japanese description): 完全出入制限 full, 部分出入制限 partial, 地形要因等により出入路なし no access due to terrain, 出入自由 none. |
| `h27_road_unit_area_code` | string | Original column: 平成２７年度／道路状況／都道府県指定市コード. Area code of the corresponding 2015 road condition survey unit section (5-character string): code of the area (prefecture, designated city, etc.) within which the survey unit sections are numbered. Leading zeros restored. |
| `h27_road_unit_section_number` | string | Original column: 平成２７年度／道路状況／調査単位区間番号. Corresponding 2015 road condition survey unit section number (5-character string): number of the survey unit section that groups basic sections. Identifies a unit section together with the area code. Leading zeros restored. |
<!-- columns:end -->

`bbox` is each row's bounding box (the GeoParquet 1.1 bbox column) and `geometry` is the section line (multilinestring).

## License and source

License: the [terms of use of the MLIT website](https://www.mlit.go.jp/link.html), based on the Public Data License (Version 1.0). You may copy, modify, redistribute and use the data commercially if you credit the source and state that it has been modified. You may not use modified data in a way that suggests it was produced by the government. The Public Data License (Version 1.0) is compatible with CC BY 4.0 (section 1.7.3 of the license).

Source: "[2021 Road Traffic Census, general traffic volume survey, section table](https://www.mlit.go.jp/road/census/r3/index.html)" (MLIT), modified

When showing the data on maps or in documents, credit it in the form the MLIT terms give:

> 「令和3年度 全国道路・街路交通情勢調査 一般交通量調査 箇所別基本表」（国土交通省）（https://www.mlit.go.jp/road/census/r3/index.html）を加工して作成
> ("2021 Road Traffic Census, general traffic volume survey, section table" (MLIT) (https://www.mlit.go.jp/road/census/r3/index.html), modified)

Where a URL does not fit, such as the corner of a map, write: "2021 Road Traffic Census, general traffic volume survey, section table" (MLIT), modified, and make it a link. If you modify the data further, still state that it has been modified.

## Processing

Made from the following two MLIT sources with [`scripts/jp-mlit-road-traffic-census-2021/build.py`](https://github.com/shiwaku/shi-works-catalog/blob/main/scripts/jp-mlit-road-traffic-census-2021/build.py) in this repository:

- The [section table](https://www.mlit.go.jp/road/census/r3/index.html) (per-prefecture CSV files, 47 files)
- The GeoJSON line tiles of the [visualization tool (web map)](https://www.mlit.go.jp/road/ir/ir-data/census_visualizationR3/index.html) (zoom 12, per road type, 18,004 tiles)

1. Concatenate the 47 CSV files (99,417 rows). The last six columns repeat the first six and are not used
2. Rename the columns to English snake_case, convert codes to labels or booleans and numbers to integers and decimals, and restore dropped leading zeros
3. Join the lines cut at tile edges into one multilinestring per section number (127,363 lines into 99,064 sections)
4. Attach the lines to the section table by section number. Sections without a line get a null geometry
5. Change the declared coordinate reference system from JGD2000 (EPSG:4612) to EPSG:4326 (coordinate values unchanged)
6. With `portolan add`, sort along a Hilbert curve, add the bbox column and rewrite as GeoParquet 1.1

The codes and labels follow chapter 5 of the MLIT document "[Explanation of the section table and the hourly traffic table](https://www.mlit.go.jp/road/census/r3/data/pdf/kasyorep.pdf)".
