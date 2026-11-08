# 行政区域

[English](../../en/jp-ksj/admin-boundaries/README.md)

国土交通省の国土数値情報「行政区域データ」（N03）の2026年（令和8年）1月1日時点の版です。全国の市区町村の範囲を、1市区町村1行のマルチポリゴンで持ちます。政令指定都市は区ごとの行です。事故や施設などの点を市区町村ごとに数えるときの、集計の単位として使えます。

- ファイル: [`jp-ksj-admin-boundaries.parquet`](https://catalog.shi-works.com/jp-ksj/admin-boundaries/jp-ksj-admin-boundaries.parquet)（GeoParquet 1.1、約179 MB）
- 件数: 1,905行（全国地方公共団体コードごとに1行）
- 範囲: 日本全国（47都道府県）。2026年1月1日時点の境界
- 座標参照系: EPSG:4326（緯度経度）。元データは JGD2011（EPSG:6668）で、値はそのまま

## 件数

| 種類 | 行数 |
|---|---:|
| 市（政令指定都市を除く） | 772 |
| 政令指定都市の区（20市） | 171 |
| 東京都の特別区 | 23 |
| 町 | 743 |
| 村 | 189 |
| 所属未定地 | 7 |
| 合計 | 1,905 |

市は政令指定都市20市を合わせて792市です。

## 使い方

DuckDB で、ダウンロードせずに読めます。交通事故統計（[jp-npa/traffic-accident](../../jp-npa/traffic-accident/README.md)）の事故の点を、市区町村ごとに数える例です。

```sql
INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial;
SELECT a.admin_code,
       a.pref_name || a.municipality_name || coalesce(a.ward_name, '') AS name,
       count(*) AS accidents
FROM read_parquet('https://catalog.shi-works.com/jp-npa/traffic-accident/jp-npa-traffic-accident.parquet') t
JOIN read_parquet('https://catalog.shi-works.com/jp-ksj/admin-boundaries/jp-ksj-admin-boundaries.parquet') a
  ON ST_Intersects(a.geometry, t.geometry)
WHERE t.statistics_year = 2025
GROUP BY ALL
ORDER BY accidents DESC
LIMIT 5;
```

QGIS など GDAL の Parquet ドライバを持つソフトでは、ファイルをダウンロードしてそのまま開けます。

## 使ってよいこと・いけないこと

- 市区町村ごとの集計の単位、地図の背景の境界線、点がどの市区町村にあるかの判定に使えます。
- 縮尺 1/25,000 相当の境界です。区域が変わった後の住所や、筆界の確認など、法的な境界の判断には使えません。
- 2026年1月1日時点の境界です。それより前のデータ（2019〜2025年の事故など）と重ねると、その間の合併・境界変更は反映されません。2020年以降の市町村の合併はほとんどありませんが、浜松市は2024年1月1日に区を7区から3区に再編したので、区ごとの集計を年をまたいで比べるときは注意してください。

## 既知の注意点

- **所属未定地が7行あります。** 境界が決まっていないため、どの市区町村にも属さない区域です。`admin_code` は「<都道府県コード>000」、`municipality_name` は「所属未定地」です。市区町村ごとの集計では除いてください。
- **海の上や海岸線の外の点は、どの行にも入りません。** 2025年の交通事故（座標のある287,020件）では、187件がどの市区町村の範囲にも入りませんでした。埋立地や橋の上、海沿いの道路が、境界のデータより外にあると考えられます。
- **北方領土の6村（色丹村、泊村、留夜別村、留別村、紗那村、蘂取村）を含みます。** 面積を合計すると約377,976 km² で、国土地理院が公表している国土の面積（北方領土を含む）とほぼ一致します。
- **政令指定都市は区ごとの行です。** 市全体で数えるときは、`pref_code` と `municipality_name` でまとめてください。
- **元データでは島ごとに別の行でした。** ここでは同じコードの行を1つのマルチポリゴンにまとめています（形は変えていません）。元データは125,130行です。

## 列

<!-- columns:start -->
| 列 | 型 | 説明 |
|---|---|---|
| `admin_code` | string | 元の列名: N03_007。全国地方公共団体コード（5桁の文字列。チェックディジットなし）。都道府県コード2桁と市区町村コード3桁。政令指定都市は区ごとのコード。所属未定地は「<都道府県コード>000」。1行に1つで、重複しない。 |
| `pref_code` | string | 元データにない、足した列。都道府県コード（2桁の文字列。01 北海道 〜 47 沖縄県）。admin_code の先頭2桁。 |
| `pref_name` | string | 元の列名: N03_001。都道府県名。 |
| `subprefecture_name` | string | 元の列名: N03_002。北海道の振興局名。北海道以外は空。 |
| `county_name` | string | 元の列名: N03_003。郡名。郡に属する町村だけにあり、市・区・郡に属さない町村（島しょなど）は空。 |
| `municipality_name` | string | 元の列名: N03_004。市区町村名（市、町、村、東京都の特別区）。政令指定都市の区の行では市の名前（「札幌市」など）で、区の名前は ward_name にある。所属未定地の行は「所属未定地」。 |
| `ward_name` | string | 元の列名: N03_005。政令指定都市の行政区名（「中央区」など）。政令指定都市以外は空。東京都の特別区はここではなく municipality_name にある。 |
<!-- columns:end -->

`bbox` は各行の範囲（GeoParquet 1.1 の bbox 列）、`geometry` は市区町村の範囲（マルチポリゴン）です。

## ライセンスと出典

License: CC-BY-4.0（[クリエイティブ・コモンズ 表示 4.0 国際](https://creativecommons.org/licenses/by/4.0/deed.ja)）。国土数値情報の行政区域データのページで、使用許諾条件が「オープンデータ（CC_BY_4.0）」と示されています。国土数値情報の[利用規約](https://nlftp.mlit.go.jp/ksj/other/agreement_01.html)（政府標準利用規約（第2.0版）に準拠）も合わせて読んでください。加工したデータを国が作ったように見せる使い方はできません。

Source: 「[国土数値情報（行政区域データ）](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html)」（国土交通省）（2026年1月1日時点）を加工して作成。元データは、国土地理院の「数値地図（国土基本情報）」の行政区域をもとに整備されたものです（測量法に基づく国土地理院長承認（複製）R 7JHf 351）。

地図や資料に載せるときは、国土数値情報の利用規約の書き方に合わせて、次のように書いてください。

> 「国土数値情報（行政区域データ）」（国土交通省）（https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html）を加工して作成

地図の隅など、URL を入れにくいところでは「「国土数値情報（行政区域データ）」（国土交通省）を加工して作成」と書き、URL はリンクにしてください。このデータからさらに加工したときも「加工して作成」と書いてください。

## 加工の記録

国土数値情報ダウンロードサイトの全国版 `N03-20260101_GML.zip` に入っている `N03-20260101.geojson`（125,130行）から、このリポジトリの [`scripts/jp-ksj-admin-boundaries/build.py`](https://github.com/shiwaku/shi-works-catalog/blob/main/scripts/jp-ksj-admin-boundaries/build.py) で次のように作りました。

1. 属性名（`N03_001` など）を英語の snake_case にし、都道府県コード（`pref_code`）を足す
2. 全国地方公共団体コードごとに、島ごとのポリゴンを1つのマルチポリゴンにまとめる（125,130行 → 1,905行）
3. 座標系の指定を JGD2011（EPSG:6668）から EPSG:4326 に変える（座標の値は変えない）
4. `portolan add` で、Hilbert 曲線の順に並べ、bbox 列を足し、GeoParquet 1.1 で書き直す
