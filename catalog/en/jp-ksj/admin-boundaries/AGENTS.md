# AGENTS.md — 行政区域

市区町村（政令指定都市は区）の範囲。1行1市区町村のマルチポリゴン。点のデータを市区町村ごとに数えるときの集計の単位。

## すぐ動く読み方

```sql
-- DuckDB
INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial;
CREATE TABLE admin AS
SELECT * FROM read_parquet('https://catalog.shi-works.com/jp-ksj/admin-boundaries/jp-ksj-admin-boundaries.parquet');
```

```python
# GeoPandas（約179 MB）
import geopandas as gpd
gdf = gpd.read_parquet("https://catalog.shi-works.com/jp-ksj/admin-boundaries/jp-ksj-admin-boundaries.parquet")
```

## 1行の識別

`admin_code`（全国地方公共団体コード5桁、チェックディジットなし）。重複しない。総務省のコード（e-Stat の統計など）と結合するときは、チェックディジット付きの6桁と混同しないこと。

## 落とし穴

- **交通事故統計とはコードで結合できない。** 交通事故統計（`jp-npa/traffic-accident`）の `municipality_code` は警察庁の3桁のコードで、全国地方公共団体コードとは別の体系。結合は `ST_Intersects` で空間的に行う。
- **所属未定地（7行）。** `admin_code` が「<都道府県コード>000」、`municipality_name` が「所属未定地」。市区町村の集計では `WHERE municipality_name <> '所属未定地'` で除く。
- **政令指定都市は区ごと。** `municipality_name` に市の名前、`ward_name` に区の名前。市全体にするには `GROUP BY pref_code, municipality_name`。東京都の特別区は `ward_name` ではなく `municipality_name` にある。
- **表示名。** `pref_name || coalesce(county_name, '') || municipality_name || coalesce(ward_name, '')` で「北海道札幌市中央区」「長野県北佐久郡軽井沢町」のような名前になる。
- **海沿いの点は入らないことがある。** 2025年の交通事故では、座標のある287,020件のうち187件がどの行の範囲にも入らなかった（埋立地、橋の上など）。件数の合計が合わないときはこれを疑う。
- **北方領土の6村を含む。** 国内の集計で除くときは `admin_code` の 01695〜01700。
- **境界は2026年1月1日時点。** 過去のデータと重ねても、過去の境界にはならない。浜松市は2024年1月1日に7区から3区に再編された。
- **大きさ。** 1行あたりの形が細かい（全体で約179 MB）。全国の地図に表示するだけなら `ST_SimplifyPreserveTopology` などで簡略化すると軽い。

## 集計の例

```sql
-- 2025年の交通事故を市区町村ごとに数える（手元の DuckDB で約8秒）
SELECT a.admin_code,
       a.pref_name || a.municipality_name || coalesce(a.ward_name, '') AS name,
       count(*) AS accidents
FROM read_parquet('https://catalog.shi-works.com/jp-npa/traffic-accident/jp-npa-traffic-accident.parquet') t
JOIN read_parquet('https://catalog.shi-works.com/jp-ksj/admin-boundaries/jp-ksj-admin-boundaries.parquet') a
  ON ST_Intersects(a.geometry, t.geometry)
WHERE t.statistics_year = 2025
GROUP BY ALL
ORDER BY accidents DESC;
```

```sql
-- 政令指定都市を市でまとめた面積（km²）。DuckDB の ST_Area_Spheroid は (緯度, 経度) の順を
-- 前提にしているので、ST_FlipCoordinates で入れ替える（入れ替えないと NaN になる）
-- 結果の1位は岐阜県高山市の2,177.6 km²（国土地理院の公表値と一致）
SELECT pref_name, municipality_name,
       round(sum(ST_Area_Spheroid(ST_FlipCoordinates(geometry))) / 1e6, 1) AS area_km2
FROM read_parquet('https://catalog.shi-works.com/jp-ksj/admin-boundaries/jp-ksj-admin-boundaries.parquet')
WHERE municipality_name <> '所属未定地'
GROUP BY ALL
ORDER BY area_km2 DESC
LIMIT 5;
```

## 作り方

```bash
# 1. 国土数値情報ダウンロードサイトから全国版を落とし、GeoJSON を取り出す
curl -LO https://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2026/N03-20260101_GML.zip
unzip N03-20260101_GML.zip N03-20260101.geojson
# 2. 列名を整え、コードごとに1つのマルチポリゴンにまとめる
python scripts/jp-ksj-admin-boundaries/build.py --src N03-20260101.geojson
# 3. 空間の順に並べ、bbox 列を足し、GeoParquet 1.1 で書き直す。collection.json を作る
cd catalog && portolan add jp-ksj/admin-boundaries/jp-ksj-admin-boundaries.parquet --force
# 4. 列の説明・キーワード・期間・言語・出典の表示を足し、英語版を作る
cd .. && python scripts/finalize_metadata.py
```

列の定義（名前、元の属性名、説明）は `scripts/jp-ksj-admin-boundaries/columns.yaml` にまとめてある。
