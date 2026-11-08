# AGENTS.md — 人口集中地区（2020年）

令和2年国勢調査の人口集中地区（DID）。1行1地区のマルチポリゴン。市街地かどうかの区分に使う。

## すぐ動く読み方

```sql
-- DuckDB（約20 MB、1,463行。まるごと読んでよい）
INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial;
CREATE TABLE did AS
SELECT * FROM read_parquet('https://catalog.shi-works.com/jp-stat/densely-inhabited-districts-2020/jp-stat-densely-inhabited-districts-2020.parquet');
```

```python
# GeoPandas
import geopandas as gpd
gdf = gpd.read_parquet("https://catalog.shi-works.com/jp-stat/densely-inhabited-districts-2020/jp-stat-densely-inhabited-districts-2020.parquet")
```

## 1行の識別

`admin_code`（2020年10月1日時点の全国地方公共団体コード5桁）と `did_number`（市区町村の中での番号）の組。`did_number` だけでは重複する。

## 落とし穴

- **点の判定は EXISTS で。** 隣り合う行の境界線上の点は2行に入る（2025年の交通事故で6件）。`LEFT JOIN` で数えると二重に数える。「DID の中か外か」は `EXISTS (SELECT 1 FROM did d WHERE ST_Intersects(d.geometry, t.geometry))`。
- **市区町村ごとに設定。** 地図の上でつながっていても、市区町村が違えば別の行。都市圏の広がりとしてまとめるときは `ST_Union_Agg` などで結合する。
- **コードは2020年時点。** 浜松市の旧区（22131〜22137）は2026年の行政区域（`jp-ksj/admin-boundaries`）にない。行政区域とはコードではなく位置で結合する。
- **`area_km2` は元データの値。** geometry から計算した面積と最大約2 km² 違う行がある。密度を出すときは、どちらの面積かを結果に書く。
- **2020年時点の範囲。** 2019〜2025年の事故に重ねるのは近似。年をまたいだ比較で、DID の範囲が変わったことは考慮できない。
- **統計上の地域。** 都市計画の市街化区域・用途地域ではない。

## 集計の例

```sql
-- 2025年の交通事故のうち、DID の中で起きた件数（手元の DuckDB で約5秒）
-- 結果: 287,020件中 195,204件（68.0%）
SELECT count(*) AS accidents,
       count(*) FILTER (WHERE EXISTS (SELECT 1 FROM did d WHERE ST_Intersects(d.geometry, t.geometry))) AS in_did
FROM read_parquet('https://catalog.shi-works.com/jp-npa/traffic-accident/jp-npa-traffic-accident.parquet') t
WHERE t.statistics_year = 2025 AND t.geometry IS NOT NULL;
```

```sql
-- 都道府県ごとの DID 人口
SELECT pref_code, sum(population) AS did_population, round(sum(area_km2), 1) AS did_area_km2
FROM did
GROUP BY pref_code
ORDER BY pref_code;
```

## 作り方

```bash
# 1. e-Stat の境界データダウンロードから、都道府県別の shape ファイル（世界測地系緯度経度）を落として展開する
for i in $(seq -w 1 47); do
  curl -s -o $i.zip "https://www.e-stat.go.jp/gis/statmap-search/data?dlserveyId=D002005112020&code=$i&coordSys=1&format=shape&downloadType=5&datum=2011"
  unzip -o -q $i.zip; sleep 1
done
# 2. つないで、列名を整え、不正な形を直す
python scripts/jp-stat-densely-inhabited-districts-2020/build.py --src .
# 3. 空間の順に並べ、bbox 列を足し、GeoParquet 1.1 で書き直す。collection.json を作る
cd catalog && portolan add jp-stat/densely-inhabited-districts-2020/jp-stat-densely-inhabited-districts-2020.parquet --force
# 4. 行グループをジオメトリ約 4 MB ごとに分け直し（1つだと範囲で絞っても全体を読むため）、もう一度登録する
cd .. && python scripts/rowgroups.py catalog/jp-stat/densely-inhabited-districts-2020/jp-stat-densely-inhabited-districts-2020.parquet
cd catalog && portolan add jp-stat/densely-inhabited-districts-2020/jp-stat-densely-inhabited-districts-2020.parquet --force
# 5. 列の説明・キーワード・期間・言語・出典の表示を足し、英語版を作る
cd .. && python scripts/finalize_metadata.py
```

列の定義（名前、元の属性名、説明）は `scripts/jp-stat-densely-inhabited-districts-2020/columns.yaml` にまとめてある。
