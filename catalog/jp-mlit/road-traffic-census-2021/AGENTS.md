# AGENTS.md — 道路交通センサス（2021年）

令和3年度 道路交通センサス 一般交通量調査の箇所別基本表（国土交通省）。1行1区間（交通調査基本区間）のマルチライン、99,417行・153列＋geometry。幹線道路の交通量・旅行速度・道路構造を、事故の分析に結び付けるのに使う。

## すぐ動く読み方

```sql
-- DuckDB（約56 MB。列が多いので、要る列だけ選ぶ）
INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial;
CREATE TABLE census AS
SELECT section_id, road_type, route_name, admin_code, length_km,
       traffic_24h, traffic_12h, large_vehicle_ratio_12h_pct, congestion_degree,
       up_traffic_observed, lanes, roadway_width_m, sidewalk_pct, speed_limit_kmh, roadside_status, geometry
FROM read_parquet('https://catalog.shi-works.com/jp-mlit/road-traffic-census-2021/jp-mlit-road-traffic-census-2021.parquet');
```

```python
# GeoPandas
import geopandas as gpd
gdf = gpd.read_parquet("https://catalog.shi-works.com/jp-mlit/road-traffic-census-2021/jp-mlit-road-traffic-census-2021.parquet",
                       columns=["section_id", "road_type", "traffic_24h", "length_km", "geometry"])
```

## 1行の識別

`section_id`（交通調査基本区間番号、11桁の文字列）で一意。先頭2桁が都道府県（`pref_code`）、3桁目が道路種別の番号。

## 列の読み方

- 列名の頭: `up_` / `down_` は上り・下り、`peak_` は朝夕（混雑時：7〜9時、17〜19時）、`offpeak_` は昼間（非混雑時：9〜17時）、`h27_` は平成27年度（2015年）調査の値。頭なしの `traffic_12h` / `traffic_24h` は上下合計。
- 車種: 末尾 `_small` は小型車、`_large` は大型車、なしは合計。
- 交通量の主な列は `traffic_24h`（24時間、上下合計、台）。12時間観測と推定の区間では、昼夜率から推定した値。
- コードは日本語のラベルに直してある（`road_type` は「一般国道」など）。値の一覧は collection.json の列の説明にある。「あり・なし」の列は真偽値（`is_motorway`、`has_railway_crossing`、`has_climbing_lane_up` / `_down`、`has_reversible_lane`、`*_individual_survey_used`）。
- コードの列（`admin_code`、`*_unit_area_code`、`*_unit_section_number`）は5桁の文字列。`*_observation_date` は YYYYMMDD の文字列で、日が `00` のことがある。

## 落とし穴

- **市町村道はほぼない。** 対象は高速道路・一般国道・都道府県道・指定市の主な市道。2025年の事故のうち、区間から約20 m 以内は56.8%。「生活道路」の分析には使えない（車道幅員5.5m未満の区間も少しはあるが、生活道路の代表ではない）。
- **推定値が約3分の1。** `up_traffic_observed` / `down_traffic_observed` が「非観測（推定値）」の区間は、2015年の値からの推定。区間ごとの値を示すときは、観測か推定かを書く。
- **調査単位区間の値。** 交通量・旅行速度・道路状況は、いくつかの区間を集約した調査単位区間ごとの値で、同じ調査単位区間の行は同じ値。平均は `length_km` で重み付けする（`sum(x * length_km) / sum(length_km)`）。
- **線がない行が353。** ジオメトリが null。空間結合では落ちる。
- **線の長さを延長に使わない。** 上下線を別の線で描いた区間があり、線の長さは `length_km` より長い。
- **空の値。** 24時間交通量が null の行が3,413。旅行速度の車種別（`*_small` / `*_large`）と取得件数は、ETC2.0 プローブ情報で調べた区間だけ。
- **点との結合は EXISTS か最も近い1本で。** 交差点の事故は複数の区間から同じ距離にある。`JOIN ... ON ST_DWithin` で数えると二重に数える。1本に決めるときは距離の最小で選ぶ。
- **距離の単位は度。** 座標は緯度経度。`ST_DWithin(..., 0.0002)` は約20 m。正確な距離が要るときは平面直角座標系などに変換する。
- **コードは2021年4月1日時点。** `admin_code` は2021年時点の市区町村コード。行政区域（`jp-ksj/admin-boundaries`、2026年1月1日時点）とはコードが合わない行がある。
- **`roadside_status` の人口集中地区は2015年国勢調査のもの。** `jp-stat/densely-inhabited-districts-2020` とは範囲が違う。

## 集計の例

```sql
-- 2025年の交通事故のうち、センサスの区間から約20 m 以内で起きた件数（手元の DuckDB で数秒）
-- 結果: 287,020件中 163,033件（56.8%）
SELECT count(*) AS accidents,
       count(*) FILTER (WHERE EXISTS (
         SELECT 1 FROM census c WHERE ST_DWithin(c.geometry, t.geometry, 0.0002))) AS near_census_road
FROM read_parquet('https://catalog.shi-works.com/jp-npa/traffic-accident/jp-npa-traffic-accident.parquet') t
WHERE t.statistics_year = 2025 AND t.geometry IS NOT NULL;
```

```sql
-- 道路種別ごとの延長と走行台キロ（千台キロ/日）。国土交通省の集計結果整理表とほぼ合う
SELECT road_type, count(*) AS sections, round(sum(length_km), 1) AS length_km,
       round(sum(traffic_24h * length_km) / 1000) AS vehicle_km_24h_thousand
FROM census GROUP BY road_type ORDER BY road_type;
```

## 作り方

```bash
# 1. 箇所別基本表の CSV と、可視化ツールの線のタイルを取る（shiwaku/mlit-road-traffic-census-converter）
python scripts/download_kasho_csv.py --year r03      # → data/r03/csv/kasho/kasyo01.csv 〜 kasyo47.csv
python scripts/download_geojson_tiles.py --year r03  # → data/r03/geojson_tiles/（18,004枚）
# 2. つないで、列名と型を整え、線を区間ごとにつないで結び付ける
python scripts/jp-mlit-road-traffic-census-2021/build.py --csv <converter>/data/r03/csv/kasho --tiles <converter>/data/r03/geojson_tiles
# 3. 空間の順に並べ、bbox 列を足し、GeoParquet 1.1 で書き直す。collection.json を作る
cd catalog && portolan add jp-mlit/road-traffic-census-2021/jp-mlit-road-traffic-census-2021.parquet --force
# 4. 行グループをジオメトリ約 4 MB ごとに分け直し（1つだと範囲で絞っても全体を読むため）、もう一度登録する
cd .. && python scripts/rowgroups.py catalog/jp-mlit/road-traffic-census-2021/jp-mlit-road-traffic-census-2021.parquet
cd catalog && portolan add jp-mlit/road-traffic-census-2021/jp-mlit-road-traffic-census-2021.parquet --force
# 5. 列の説明・キーワード・期間・言語・出典の表示を足し、英語版を作る
cd .. && python scripts/finalize_metadata.py
```

取得に使った変換リポジトリは shiwaku/mlit-road-traffic-census-converter（コミット f5132ca）。列の定義（名前、元の列名、型、コード表、説明）は `scripts/jp-mlit-road-traffic-census-2021/columns.yaml` にまとめてある。
