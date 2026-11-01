# 公開 URL とファイル名の規則

最終更新: 2026-11-01（案。#4）

データの URL は、一度公開すると利用者のスクリプトや地図に書き込まれるので、後から変えにくい。Portolan のベストプラクティスも「名前は契約として選ぶ」としている（[philosophy.md](https://github.com/portolan-sdi/portolan-spec/blob/main/specs/best-practices/philosophy.md) の "Names outlive everything"）。

## 1. URL の形

```
https://catalog.shi-works.com/<区分>/<管理者>/<コレクション>/<ファイル>
```

- 例: `https://catalog.shi-works.com/jp-national/npa/traffic-accident/npa-traffic-accident.parquet`
- コレクションの ID は、ルートからのパス（例: `jp-national/npa/traffic-accident`）。Portolan の仕様どおり。
- 区分と管理者の一覧は [catalog-structure.md](catalog-structure.md)。

## 2. 使える文字

**英小文字、数字、ハイフン（`-`）だけを使う。先頭は英小文字にする。**

- Portolan の仕様（core.md）は「英小文字、数字、ハイフン、アンダースコア。先頭は英字」を SHOULD としている。先頭が数字の `27-osaka` は使えない。
- ハイフンにする理由:
  - 既存の URL（`pref-osaka/osaka-csmap-tiles` など）がハイフンなので、利用者にとって変わらない。
  - Portolan の参照カタログ（`boundaries/us-counties`、`reference/natural-earth-countries`）もハイフン。
  - ベストプラクティス（philosophy.md）は snake_case を勧めているが、仕様はハイフンを認めていて、参照カタログとも食い違っている。ここでは既存の URL と参照カタログに合わせる。
- 1つの名前の中でハイフンとアンダースコアを混ぜない。

## 3. 区分の名前

| 区分 | 付け方 |
|---|---|
| 政府 | `<国コード>-<種類>`。国コードは ISO 3166-1 alpha-2 の小文字。種類は `national`（国）、日本は `prefectures`、`municipalities` |
| 政府以外 | `others` |
| shi-works が作ったもの | `shi-works` |

例: `jp-national`、`jp-prefectures`、`jp-municipalities`、`us-national`。

## 4. 管理者の名前

| 種類 | 付け方 | 例 |
|---|---|---|
| 国の機関 | 英語の略称が広く使われていればそれ。なければ英語名 | `gsi`、`mlit`、`npa`、`jma`、`digital-agency`、`forestry-agency`、`stat`（総務省統計局。ドメインの `stat.go.jp` から） |
| 国の製品の系統 | 製品名 | `ksj`（国土数値情報）、`plateau` |
| 都道府県 | ローマ字（ヘボン式、長音記号なし）。「都・府・県」は付けない | `tokyo`、`osaka`、`hokkaido`、`kochi`、`oita` |
| 市区町村 | `<都道府県>-<名前>-<種類>`。種類は自治体の英語表記に合わせて `city`、`town`、`village` | `shizuoka-shizuoka-city`、`saitama-saitama-city`、`tokyo-nakano-city` |
| 外国の国の機関 | 英語の略称（`us-national/` などの下） | `usgs` |
| その他 | 団体やサービスの略称。なければ英語名 | `osm`、`worldpop`、`google`、`gebco`、`jartic`、`tohoku-university`、`gtfs-gis`、`gosenzo-net` |

- 都道府県コード・市区町村コードはフォルダ名に入れず、メタデータ（`keywords` と README）に書く。名前で探せるほうを優先する。
- 市区町村に都道府県を必ず付けるのは、同じ名前の市が別の県にあるため（府中市、伊達市など）。重なったときだけ付ける形にすると、後から増えたときに書き方がそろわなくなる。
- 東京の特別区は英語で "Nakano City" と名乗っているので `city` にする。
- [catalog-structure.md](catalog-structure.md) の仮の名前のうち、次を変える: `rinya` → `forestry-agency`、`tohoku-u` → `tohoku-university`、`shizuoka-city` → `shizuoka-shizuoka-city`、`saitama-city` → `saitama-saitama-city`、`nakano-city` → `tokyo-nakano-city`。

## 5. コレクションの名前

- **何のデータかを書く。** 形式（`pmtiles`、`fgb`）、ツールの名前、作業の段階（`converted`、`modified`、`v2`）は入れない。
- **管理者の名前は繰り返さない。** パスに入っているので、`jp-national/npa/npa-traffic-accident` ではなく `jp-national/npa/traffic-accident`。
- **定期的に更新される系列は、1つのコレクションにする。** 年次は Item か版で表し、コレクションの名前に入れない。例: 道路交通センサスの 2015 と 2021 は、`jp-national/mlit/road-traffic-census` の Item にする。
- **調査の年が中身を決めるものは、年を入れてよい。** 例: 国勢調査をもとにした `population-mesh-100m-2020` は、2025 年版が出ても別のデータとして並べる。
- 短くする。説明は `title`（日英）に書く。

## 6. ファイルの名前

コレクションの中:

```
<区分>/<管理者>/<コレクション>/
├── collection.json
├── README.md
├── AGENTS.md
├── thumbnail.png
├── <管理者>-<コレクション>.parquet     ← 正本（ベクタ）
├── <管理者>-<コレクション>.tif         ← 正本（ラスタ。COG）
├── styles/<スタイル名>.json
└── <Item の ID>/                        ← Item があるとき
    ├── <Item の ID>.json
    └── <管理者>-<コレクション>-<Item の ID>.<拡張子>
```

- **データのファイル名は `<管理者>-<コレクション>` にする。** 例: `npa-traffic-accident.parquet`、`osaka-csmap.tif`。ダウンロードしたファイルが手元で並んでも区別できるようにする（コレクション名だけの `csmap.tif` だと、県ごとのファイルが同じ名前になる）。
- `collection.json`、`README.md`、`AGENTS.md`、`thumbnail.png` は Portolan の決まった名前のまま。
- **ファイル名に版（`_v1` など）や日付を入れない。** 理由:
  - URL を変えずに、いつも最新のデータを指せる。利用者のスクリプトを書き換えずに済む。
  - portolan-cli は同じパスに上書きし、版の記録（ハッシュ、日時）を `versions.json` に残す作りになっている。ファイル名に版を入れると、この作りと合わない。
  - Portolan の仕様は、データの版を STAC の version 拡張で表すとしている（core.md）。
  - その代わり、上書きしたときにキャッシュに古い内容が残る問題が出る。キャッシュの扱い（短い TTL、Purge、ETag での再検証）は #5 と #6 で決める。

## 7. 分割したファイルの名前

GeoParquet が大きいとき（目安は 2 GB 超。1ファイル 200 MB〜1 GB にする。Portolan の formats.md）は分割する。

```
<コレクション>/
└── data/
    ├── pref_code=01/<管理者>-<コレクション>.parquet
    ├── pref_code=02/<管理者>-<コレクション>.parquet
    └── …
```

- Portolan の仕様は「分割のパスは空間の範囲を表す」ことを MUST にしている。日本全国のデータは、**都道府県コード**で分ける（Hive 形式の `キー=値`）。利用者にもわかりやすく、DuckDB などが読むときにファイルを絞り込める。
- **全球・複数の国にまたがるデータは、国コード**（`country=jp`、ISO 3166-1 alpha-2 の小文字）で分ける。国に分けられないもの（海域など）や、1か国でも大きすぎるものは、空間グリッド（H3 など）で分ける（そのときに決める）。
- 都道府県で分けても大きすぎるときは、3次メッシュなどでさらに分ける（そのときに決める）。
- `partition:glob` には `data/*/*.parquet` のように書く。
- Hive 形式のキー（`pref_code`）だけはアンダースコアを使う。列名と合わせるため（第2章の例外）。

## 8. タイルの URL

タイルは事前に作らず、Worker でリクエストのたびに作る（requirements.md 第4章）。タイルの URL は #8 で決める。
