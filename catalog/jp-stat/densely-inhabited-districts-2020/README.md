# 人口集中地区（2020年）

[English](../../en/jp-stat/densely-inhabited-districts-2020/README.md)

令和2年（2020年）国勢調査の人口集中地区（DID）の境界データです。総務省統計局が e-Stat で公開しています。人口集中地区は、市区町村の中で、人口密度が1 km² あたり4,000人以上の基本単位区などが隣り合い、合わせて人口5,000人以上になる地域で、市街地の範囲として使われます。事故が市街地で起きたかどうかを分ける、市街地と郊外で事故の起き方を比べる、といった分析に使えます。

- ファイル: [`jp-stat-densely-inhabited-districts-2020.parquet`](https://catalog.shi-works.com/jp-stat/densely-inhabited-districts-2020/jp-stat-densely-inhabited-districts-2020.parquet)（GeoParquet 1.1、約20 MB）
- 件数: 1,463行（1地区1行。969市区町村）
- 範囲: 日本全国。2020年10月1日時点（国勢調査の調査日）
- 人口の合計: 88,285,927人（同じ国勢調査の総人口126,146,099人の約70%）
- 座標参照系: EPSG:4326（緯度経度）。元データは JGD2011（EPSG:6668）で、値はそのまま

## 使い方

DuckDB で、ダウンロードせずに読めます。2025年の交通事故（[jp-npa/traffic-accident](../../jp-npa/traffic-accident/README.md)）のうち、人口集中地区の中で起きたものを数える例です。

```sql
INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial;
CREATE TABLE did AS
SELECT * FROM read_parquet('https://catalog.shi-works.com/jp-stat/densely-inhabited-districts-2020/jp-stat-densely-inhabited-districts-2020.parquet');
SELECT count(*) AS accidents,
       count(*) FILTER (WHERE EXISTS (SELECT 1 FROM did d WHERE ST_Intersects(d.geometry, t.geometry))) AS in_did
FROM read_parquet('https://catalog.shi-works.com/jp-npa/traffic-accident/jp-npa-traffic-accident.parquet') t
WHERE t.statistics_year = 2025 AND t.geometry IS NOT NULL;
```

結果は287,020件のうち195,204件（68.0%）でした。人口集中地区の面積は国土の4%に足りませんが、事故の約3分の2がその中で起きています。

QGIS など GDAL の Parquet ドライバを持つソフトでは、ファイルをダウンロードしてそのまま開けます。

## 使ってよいこと・いけないこと

- 市街地かどうかの区分、市街地の広がりの地図、人口集中地区の人口や面積の集計に使えます。
- 2020年国勢調査の時点の範囲です。その後の開発や人口の変化は入っていません。2025年国勢調査の人口集中地区が公表されたら、別のコレクション（`densely-inhabited-districts-2025`）として載せる予定です。
- 人口集中地区は統計上の地域で、都市計画の市街化区域や用途地域とは別のものです。

## 既知の注意点

- **人口集中地区は市区町村ごとに設定されています。** 隣の市区町村の人口集中地区と地図の上でつながっていても、別の行です。`admin_code` と `did_number` の組で1行が決まります。
- **`did_number` は市区町村の中での番号です。** 人口の多い順に1から振られています（豊田市と神戸市北区は9まで）。別の市区町村の同じ番号は、別の地区です。
- **点が2つの行に入ることがあります。** 隣り合う行の境界線上の点は、両方の行に入ります。2025年の交通事故では6件ありました。点を数えるときは、上の例のように `EXISTS` で判定すると二重に数えません。
- **市区町村コードは2020年10月1日時点です。** 浜松市の区（22131〜22137）は、2024年1月1日の区の再編で今はありません。行政区域（[jp-ksj/admin-boundaries](../../jp-ksj/admin-boundaries/README.md)、2026年1月1日時点）とはコードで結合できない行があるので、位置で重ねてください。
- **`area_km2` は元データの値です。** geometry から計算した面積とは、行によって最大で約2 km² 違います（広島市中区など）。面積を使うときは、どちらを使ったかを書いてください。
- **元データの5行にあった不正な形を直しました。** 自己接触などで ST_IsValid が偽になる形を ST_MakeValid で直しています。面積は変わりません。

## 列

<!-- columns:start -->
| 列 | 型 | 説明 |
|---|---|---|
| `admin_code` | string | 元データにない、足した列。全国地方公共団体コード（5桁の文字列。チェックディジットなし）。元の KEN（都道府県コード）と CITY（市区町村コード）をつないだもの。2020年10月1日時点のコードで、政令指定都市は区ごと。 |
| `pref_code` | string | 元の列名: KEN。都道府県コード（2桁の文字列。01 北海道 〜 47 沖縄県）。 |
| `municipality_name` | string | 元の列名: CITYNAME。市区町村名（2020年10月1日時点）。政令指定都市の区は「札幌市北区」のように市の名前から書く。 |
| `did_number` | int32 | 元の列名: CLASS。市区町村の中での人口集中地区の番号（1から）。人口の多い順で、1が最大。admin_code と did_number の組で1行が決まる。 |
| `population` | int32 | 元の列名: JINKO。人口集中地区の人口（人。令和2年国勢調査）。 |
| `area_km2` | double | 元の列名: MENSEKI。人口集中地区の面積（km²。小数第2位まで）。元データの値で、geometry から計算したものではない。 |
<!-- columns:end -->

`bbox` は各行の範囲（GeoParquet 1.1 の bbox 列）、`geometry` は人口集中地区の範囲（マルチポリゴン）です。

## ライセンスと出典

License: 政府標準利用規約（第2.0版）に準拠する [政府統計の総合窓口（e-Stat）の利用規約](https://www.e-stat.go.jp/terms-of-use)。境界データは e-Stat の統計地理情報システムで提供されていて、その[利用規約](https://www.e-stat.go.jp/gis-terms)の第6条で、コンテンツの利用条件は e-Stat の利用規約に準じるとされています。出典を示し、加工したことを示せば、複製・加工・再配布・商用利用ができます。国が作ったように見せる使い方はできません。e-Stat の利用規約は CC BY 4.0 と互換性があります（利用規約の6）のウ）。

Source: 「[令和2年国勢調査 人口集中地区境界データ](https://www.e-stat.go.jp/gis/statmap-search?page=1&type=2&aggregateUnitForBoundary=D&toukeiCode=00200521&toukeiYear=2020&serveyId=D002005112020&datum=2011)」（総務省統計局）を加工して作成

地図や資料に載せるときは、e-Stat の利用規約の書き方に合わせて、次のように書いてください。

> 「令和2年国勢調査 人口集中地区境界データ」（総務省統計局）（https://www.e-stat.go.jp/gis/statmap-search?page=1&type=2&aggregateUnitForBoundary=D&toukeiCode=00200521&toukeiYear=2020&serveyId=D002005112020&datum=2011）を加工して作成

地図の隅など、URL を入れにくいところでは「「令和2年国勢調査 人口集中地区境界データ」（総務省統計局）を加工して作成」と書き、URL はリンクにしてください。このデータからさらに加工したときも「加工して作成」と書いてください。

## 加工の記録

e-Stat の境界データダウンロードにある「国勢調査 2020年 人口集中地区」の都道府県別の shape ファイル（世界測地系緯度経度、47個）から、このリポジトリの [`scripts/jp-stat-densely-inhabited-districts-2020/build.py`](https://github.com/shiwaku/shi-works-catalog/blob/main/scripts/jp-stat-densely-inhabited-districts-2020/build.py) で次のように作りました。

1. 47個の shape ファイルをつなぐ（1,463行）
2. 属性名（`KEN` など）を英語の snake_case にし、全国地方公共団体コード（`admin_code`）を足す
3. 不正な形（5行）を ST_MakeValid で直し、すべてマルチポリゴンにそろえる
4. 座標系の指定を JGD2011（EPSG:6668）から EPSG:4326 に変える（座標の値は変えない）
5. `portolan add` で、Hilbert 曲線の順に並べ、bbox 列を足し、GeoParquet 1.1 で書き直す
