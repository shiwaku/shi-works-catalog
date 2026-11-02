# AGENTS.md — 交通事故統計（本票）

このコレクションを使って集計・地図化するエージェント向けの手引き。件数・範囲・ライセンスは `collection.json` と README.md にある。

## すぐ動く読み方

```sql
-- DuckDB
INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial;
CREATE VIEW accidents AS
SELECT * FROM read_parquet('https://catalog.shi-works.com/jp-npa/traffic-accident/jp-npa-traffic-accident.parquet');
```

```python
# GeoPandas（全件で約132 MB。列を絞ると速い）
import geopandas as gpd
gdf = gpd.read_parquet(
    "https://catalog.shi-works.com/jp-npa/traffic-accident/jp-npa-traffic-accident.parquet",
    columns=["statistics_year", "accident_severity", "party_a_type", "party_b_type", "geometry"],
)
```

- 行は空間の順（Hilbert 曲線）に並んでいる。範囲で絞るときは `bbox` 列で条件を書くと、関係のない行グループを読み飛ばせる。
  ```sql
  WHERE bbox.xmin BETWEEN 139.6 AND 139.9 AND bbox.ymin BETWEEN 35.5 AND 35.8
  ```
- 年で絞っても読み飛ばしはほとんど効かない（どの行グループにも全部の年が入っている）。列を絞って読む量を減らす。

## 1件の識別

一意のキーは `statistics_year` + `prefecture` + `police_station` + `record_number`。`record_number` は警察署の中の番号で、単独では一意ではない。

## 落とし穴

1. **年は既定で `statistics_year` を使う。** 警察庁の公表件数と一致するのはこちら。`occurred_year`（事故が起きた年）で数えると、年末の事故の一部が翌年の統計に計上されているため、最新の年が約3%少なく出て、経年の推移に向かない。利用者への説明では「統計に計上された年」「事故が起きた年」と書く。
2. **年齢は実年齢ではなく年齢層**（`party_a_age_group`）。最も若い区分が「0～24歳」なので、10代・20代・未成年の事故は数えられない。聞かれたら数字を作らずに、この制約を伝える。
3. **当事者Aは過失が最も重い側、Bはその相手。** 被害者の区分ではない。Bが死傷している事故が多いが、Bが無傷の事故もある。
4. **年齢と種別は同じ当事者の組で見る。** 「高齢の歩行者」は `party_a_age_group` と `party_a_type` の組、または `party_b_*` の組で判定する。A の年齢と B の種別を組み合わせない。
5. **「AまたはB」の条件を、別々に数えて足さない。** 歩行者が関わる事故と自転車が関わる事故を別々に数えて足すと、両方に当てはまる事故を二重に数える。1つの WHERE に OR で書く。
6. **人身事故だけ。** 物損事故はない。死亡事故は7年で約1.9万件しかなく、細かく絞ると年に数件になる。
7. **2020年はコロナ禍で全体が約19%減。** 件数の増減だけで語らず、全事故に対する割合や指数を合わせて見る。
8. **ジオメトリが空の行が171件ある**（座標がおかしかったもの）。地図や空間結合では落ちるが、件数の集計には入れる。
9. **2019〜2021年は空になる列がある**: `sunrise_*`、`sunset_*`、`party_*_automatic`、`party_*_support_car`、`party_*_cognitive_test_days`、`party_*_driving_practice`（2022年に加わった項目）。
10. `municipality_code` は警察庁の3桁のコードで、総務省の5桁の全国地方公共団体コードとは結合できない。市区町村で集計するなら、ジオメトリと行政区域を空間結合する。
11. `prefecture` は警察の区分で、北海道は5つの方面（「北海道（札幌方面）」など）に分かれる。

## 生活道路

生活道路は「車道幅員5.5m未満の道路」。`roadway_width` で判定する。交差点の扱いで2通りあり、どちらを使ったか必ず利用者に書く。

| 含める道 | `roadway_width` の値 | 件数（7年） |
|---|---|---:|
| 5.5m未満の道と、5.5m未満どうしの交差点 | 「単路－3.5m未満」「単路－3.5m以上」「交差点－小（5.5m未満）－小」 | 355,708 |
| 5.5m未満の道と、5.5m未満の道が1本以上交わる交差点 | 上の3つに「交差点－中（5.5m以上）－小」「交差点－大（13.0ｍ以上）－小」を足す | 639,132 |

- 「単路－3.5m以上」は 3.5m以上5.5m未満を表す。
- 後者は国土交通省・警察庁の「生活道路の交通安全対策のための地図化マニュアル」（令和7年7月）の抽出条件と同じ。どちらも警察庁が公表している生活道路の件数とは一致しない。公表値を再現したとは言わない。

## 列の値

値は日本語のラベル。主な列の値:

- `accident_severity`: 死亡事故、負傷事故
- `accident_type`: 「人対車両－横断中」のように「大分類－小分類」。大分類は 人対車両、車両相互、車両単独、列車
- `party_a_type` / `party_b_type`: 「乗用車－普通車」「歩行者」「軽車両－自転車」「特定小型原付自転車」（電動キックボードなど。2024年から）など。自転車は「軽車両－自転車」と「軽車両－駆動補助機付自転車」（電動アシスト）
- `party_a_injury_severity` / `party_b_injury_severity`: 死亡、負傷、損傷なし、対象外当事者
- `party_*_cognitive_test_days`: 4桁の文字列。「9999」は受検なしか2,555日超
- `party_*_driving_practice`: 「0」はコード表にない値で、元データのまま残してある
- 「対象外当事者」は、その項目が当事者に当てはまらないこと（歩行者の車両形状など）

列ごとの説明は `collection.json` の `table:columns` にある。

## 集計の例

```sql
-- 歩行者が関わる死亡事故（統計に計上された年ごと）
SELECT statistics_year, count(*) AS accidents
FROM accidents
WHERE accident_severity = '死亡事故'
  AND (party_a_type = '歩行者' OR party_b_type = '歩行者')
GROUP BY ALL ORDER BY ALL;

-- 生活道路（5.5m未満の道と、5.5m未満どうしの交差点）の事故の割合
SELECT statistics_year,
       count(*) FILTER (WHERE roadway_width IN ('単路－3.5m未満', '単路－3.5m以上', '交差点－小（5.5m未満）－小')) * 1.0 / count(*) AS share
FROM accidents
GROUP BY ALL ORDER BY ALL;

-- 時間帯ごとの件数
SELECT occurred_hour, count(*) FROM accidents GROUP BY ALL ORDER BY ALL;
```

## 作り方

```bash
# 1. 入力を作る（別のリポジトリ）
#    npa-traffic-accident-converter: python -m converter --all --merge && ./export_geo.sh
#    npa-traffic-accident-analytics: python pipeline/build_parquet.py
# 2. 列名・型・ジオメトリを整える
python scripts/jp-npa-traffic-accident/build.py --src ../npa-traffic-accident-analytics/output/honhyo_2019-2025.parquet
# 3. 空間の順に並べ、bbox 列を足し、GeoParquet 1.1 で書き直す。collection.json を作る
cd catalog && portolan add jp-npa/traffic-accident/jp-npa-traffic-accident.parquet --force
# 4. 列の説明・キーワード・期間・言語を足し、英語版を作る
cd .. && python scripts/finalize_metadata.py
```

列の定義（名前、元の列名、型の変換、説明）は `scripts/jp-npa-traffic-accident/columns.yaml` にまとめてある。
