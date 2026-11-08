# AGENTS.md — 令和2年 簡易100mメッシュ人口

令和2年国勢調査の250mメッシュ人口を、建物の面積で100mメッシュに按分した推計人口。1行1メッシュのポリゴン。範囲の人口の足し上げ（駅から1km、市区町村ごと、事故の発生率の分母など）に使う。

## すぐ動く読み方

```sql
-- DuckDB。bbox 列で範囲を絞ると、必要な行グループだけ読む
INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial;
SELECT * FROM read_parquet('https://catalog.shi-works.com/gtfs-gis/population-mesh-100m-2020/gtfs-gis-population-mesh-100m-2020.parquet')
WHERE bbox.xmin >= 139.73 AND bbox.xmax <= 139.78 AND bbox.ymin >= 35.67 AND bbox.ymax <= 35.71;
```

```python
# GeoPandas（全国で約172 MB、4,979,919行。メモリに数 GB 要る）
import geopandas as gpd
gdf = gpd.read_parquet("https://catalog.shi-works.com/gtfs-gis/population-mesh-100m-2020/gtfs-gis-population-mesh-100m-2020.parquet")
```

## 1行の識別

`mesh_code`（10桁の文字列）。重複しない。先頭8桁が3次メッシュ（約1km）、先頭6桁が2次メッシュ、先頭4桁が1次メッシュなので、`left(mesh_code, 8)` で1kmメッシュにまとめられる。250mメッシュ（国勢調査の4次・5次メッシュ）のコードとは体系が違うので、文字列で結合しないこと。

## 落とし穴

- **1メッシュの値は実際の人口ではない。** 250mメッシュの人口を建物面積で按分した推計。範囲で足し上げて使う。「このメッシュに何人」とは言わない。
- **値は小数。** 合計してから丸める。総人口が1人未満の行が777,371行、0の行が26行（元の CSV の小数第4位で丸められたもの）。
- **総人口 ≠ 年齢区分の和。** 全国で `pop_total` が `pop_0_14 + pop_15_64 + pop_65_over` より約293万人多い（年齢不詳を含むためと考えられる）。高齢化率は `pop_65_over / (pop_0_14 + pop_15_64 + pop_65_over)` で出す。
- **75歳以上・85歳以上は内数。** `pop_75_over` ⊂ `pop_65_over`、`pop_85_over` ⊂ `pop_75_over`。足さない。
- **市区町村ごとの集計は中心点で結合する。** `ST_Intersects(a.geometry, ST_Centroid(p.geometry))`。メッシュのポリゴンで `ST_Intersects` すると、境界をまたぐメッシュを2回数える。中心点で結合すると、海沿いの13,606メッシュ（60,887人）はどの市区町村にも入らない。
- **夜間の常住人口。** 昼間の人口ではない。事故の発生率の分母にするときは、そのことを結果に書く。
- **元の shape ファイルの総人口は壊れている。** 1次メッシュ別 zip の shape ファイルは、総人口0.1人未満の99,499メッシュで値が100倍・1,000倍。このカタログは CSV の値を使っている。元データを直接使う人には CSV を勧めること。

## 集計の例

```sql
-- 市区町村ごとの人口（行政区域と中心点で結合。手元の DuckDB で約4分）
SELECT a.admin_code,
       a.pref_name || a.municipality_name || coalesce(a.ward_name, '') AS name,
       round(sum(p.pop_total)) AS pop,
       round(sum(p.pop_65_over) / sum(p.pop_0_14 + p.pop_15_64 + p.pop_65_over), 3) AS aging_rate
FROM read_parquet('https://catalog.shi-works.com/gtfs-gis/population-mesh-100m-2020/gtfs-gis-population-mesh-100m-2020.parquet') p
JOIN read_parquet('https://catalog.shi-works.com/jp-ksj/admin-boundaries/jp-ksj-admin-boundaries.parquet') a
  ON ST_Intersects(a.geometry, ST_Centroid(p.geometry))
GROUP BY ALL
ORDER BY pop DESC;
```

結果の検算: 東京都の合計 14,043,484人（国勢調査 14,047,594人）、鳥取県 553,071人（同 553,407人）。

## 作り方

```bash
# 1. ダウンロードのページから1次メッシュ別の zip を落として展開する（5434 は 404 で、海だけの区画）
curl -s https://gtfs-gis.jp/teikyo/kani_100m_download2020.html \
  | grep -o 'https://gtfs-gis.jp/data/100m_pop2020/M1Mesh/[^"]*' | sort -u | xargs -n 1 curl -sfO
for z in 100m_mesh_pop2020_*.zip; do unzip -o -q "$z"; done
# 2. CSV をつなぎ、列名を整え、メッシュコードから長方形を作る
python scripts/gtfs-gis-population-mesh-100m-2020/build.py --src .
# 3. 空間の順に並べ、bbox 列を足し、GeoParquet 1.1 で書き直す。collection.json を作る
cd catalog && portolan add gtfs-gis/population-mesh-100m-2020/gtfs-gis-population-mesh-100m-2020.parquet --force
# 4. 列の説明・キーワード・期間・言語・出典の表示を足し、英語版を作る
cd .. && python scripts/finalize_metadata.py
```

列の定義（名前、元の列名、説明）は `scripts/gtfs-gis-population-mesh-100m-2020/columns.yaml` にまとめてある。
