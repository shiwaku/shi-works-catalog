# Portolan のクライアントでカタログを見る

shi-works カタログを Portolan 公式のクライアントで開くときの仕組みと、カタログ側で気にすることをまとめる。

- QGIS: [portolan-registry-qgis](https://github.com/portolan-sdi/portolan-registry-qgis)（QGIS プラグイン「Portolan Registry」）
- Web: [portolan-browser](https://github.com/portolan-sdi/portolan-browser)（公開インスタンスは <https://browser.portolan-sdi.org>）

調べたソース: portolan-registry-qgis `b18e6d9`（2026-11-04）、portolan-browser `15af013`（2026-11-06）。

## QGIS プラグイン（portolan-registry-qgis）

静的な STAC カタログを HTTP で読んでツリーにし、データの形式に合わせて QGIS のレイヤにする。サーバー側の API は使わず、カタログの JSON とデータファイルを直接読む。

```
registry_url（カタログの一覧）
   │  rel: child 1 本 ＝ 左の一覧の 1 行（publisher）
   ▼
catalog.json ──child──▶ catalog.json / collection.json ──item──▶ item.json
   │                              │
   │                       assets（データファイル）と links（PMTiles など）
   ▼                              ▼
左ペイン：ツリー            右ペイン：About / Add to map / All files / Details
                                  │
           ┌──────────────────────┼─────────────────────┐
     View on map            Load full data             Download
  PMTiles → ローカルの     GeoParquet → DuckDB で     カタログと同じ並びで
  タイルサーバー経由       GeoPackage にコピー        保存し、checksum で確かめる
  COG → HTTP で直接読む    FGB/GeoJSON/CSV → 直接読む
```

### コードの 3 層

| 層 | 役割 |
|---|---|
| `core/` | STAC・registry・GeoParquet・PMTiles・ダウンロードの判断。QGIS にも Qt にも依存しない |
| `qgis_io/` | 通信（`QgsNetworkAccessManager` を通すので、プロキシや認証の設定が効く）、レイヤ作成、タイルサーバー、DuckDB の実行 |
| `gui/` | ウィンドウ、一覧、ツリー、右ペイン、範囲の選択、SQL タブ |

### 1. 一覧（`core/registry.py`）

- `PortolanRegistry/registry_url` が指すのは**カタログの一覧**（registry の export）。既定は公式 registry の `exports/catalogs.json`
- 一覧の JSON は `type: "Catalog"` で、`rel: child` のリンク 1 本が一覧の 1 行になる
- 一覧の小さな地図・件数・サイズ・ライセンスは、子リンクに付いた `bbox` と `portolan_registry:*`（`collection_count`、`total_size_bytes`、`licenses` など）から出す。公式 registry はカタログを巡回してこれらを書く
- shi-works の `catalog.json` を直接指しても読める。行になるのは shi-works ではなく、提供元ごとのカタログ（警察庁・国土数値情報など）で、地図や件数は空になる。データの読み込みには関係しない
- `registry_url` を読むのは、ウィンドウを最初に開いたときだけ。変えたら QGIS を再起動する
- 2026-11-11 時点で、公式 registry（89 カタログ）に shi-works は載っていない

### 2. ツリー（`core/stac.py`、`gui/catalog_tree.py`）

- `child` と `item` のリンクを、開くたびにたどる。読んだ JSON はキャッシュする
- 子がすべて item のコレクションは、「240 files」のような 1 行にまとめる

### 3. どのボタンを出すか（`core/loadable.py`、`core/stac.py`）

- 形式は、asset の `type`（メディアタイプ）で決め、なければ拡張子で決める。http(s) でない href は読めないものとして扱う
- **View on map**: PMTiles、なければ COG。PMTiles は asset のほか、`rel: "pmtiles"` のリンクでも探す
- **Load full data**: GeoParquet、なければ FlatGeobuf・GeoJSON・CSV の順
- 役割が `source`・`collection-mirror`・`archive` の asset はデータとして出さない。`thumbnail`・`overview`・`metadata` も同じ
- `table:columns` にジオメトリの列がなければ、ジオメトリのない表として読む（ボタンは「Load table」）

### 4. GeoParquet の読み込み（`core/geoparquet.py`、`qgis_io/parquet_layer.py`）

- HTTP の GeoParquet を DuckDB が読み、範囲内の地物だけを GeoPackage にコピーする。QGIS はその GeoPackage を開く
- 範囲で絞るときは、GeoParquet 1.1 の `covering`（`bbox` 列）を使って行グループを読み飛ばす。行グループを細かく分ける（[geoparquet.md](geoparquet.md)）と、ここが速くなる
- SQL タブの絞り込みは、値をパラメータとして DuckDB に渡す。保存したプロジェクトを開き直すと、もう一度コピーする
- DuckDB は QGIS に入っていないので、1.5.0 以上を QGIS の Python に入れる。Windows では `python-qgis.bat -m pip install --user duckdb==1.5.6` のように `>` を使わずに指定する（`.bat` を通すと `>` がリダイレクトになる）

### 5. PMTiles（`qgis_io/tileserver.py`、`core/style.py`）

- QGIS は PMTiles をベクタタイルとして直接読めないので、プラグインが `127.0.0.1` にタイルサーバーを立て、XYZ タイルとして渡す
- コレクションに MapLibre スタイル（役割 `style`）があれば、QGIS のスタイルに変換して付ける

### 6. 分割された Parquet と多数の item

- `partition:glob` は、`s3://` か `gs://` でないと DuckDB がファイルを列挙できない。それ以外のホストでは item を 1 つずつ読む
- `collection-mirror`（stac-geoparquet）があれば、item の範囲を 1 回のクエリでまとめて引く

### 7. ダウンロード（`core/download.py`）

- カタログと同じ相対パスで保存するので、保存先がそのままローカルの STAC カタログになる
- `file:checksum` で確かめ、止まっても続きから再開できる

## Web 版（portolan-browser）

[STAC Browser](https://github.com/radiantearth/stac-browser) を Portolan 向けに改造したもの。地図は MapLibre GL で、サーバー側の部品はない（静的サイト）。

- 公開インスタンスで外部のカタログを開ける（`allowExternalAccess: true`）。shi-works カタログは <https://browser.portolan-sdi.org/#/external/catalog.shi-works.com/catalog.json> で開ける形。QGIS プラグインの「Open in Portolan browser」もこの形の URL を作る
- 自前で立てるときは `SB_catalogUrl` にカタログを指定して `pnpm run build` し、`dist/` を静的ホストに置く
- GeoParquet は、ブラウザの中で [hyparquet](https://github.com/hyparam/hyparquet) が読み、MapLibre に渡して描く。**上限は 50 MB、10,000 地物**（`src/utils/parquetShared.js`）。超えると描かずに知らせる
- 表のプレビューは 10,000 行まで
- PMTiles と MapLibre スタイルは、そのまま描く。COG はブラウザの中で描く
- CORS が要る。`catalog.shi-works.com` は `Access-Control-Allow-Origin: *` と Range の応答（206）を返すので、条件は満たしている

### shi-works のデータを Web 地図に描けるか（2026-11-11 時点）

| コレクション | GeoParquet | Web 地図 |
|---|---|---|
| jp-stat/densely-inhabited-districts-2020 | 20.6 MB | 描ける見込み（1,463 地物） |
| jp-mlit/road-traffic-census-2021 | 56.4 MB | 上限を超える |
| jp-npa/traffic-accident | 132.1 MB | 上限を超える |
| jp-ksj/admin-boundaries | 170.7 MB | 上限を超える |
| gtfs-gis/population-mesh-100m-2020 | 180.4 MB | 上限を超える |

大きなデータを Web 地図で見せるには、**PMTiles を作って asset か `rel: pmtiles` で載せる**のが Portolan の想定する道。PMTiles なら QGIS の「View on map」でも軽く見られる。タイルの作り方は #8・#11 で決める。

## カタログ側で気にすること

- asset に `type` を必ず付ける（拡張子より優先される）
- 大きなデータには PMTiles と MapLibre スタイル（役割 `style`）を足す
- 範囲で絞る読み込みの速さは、`bbox` 列（covering）と行グループの細かさで決まる
- 一覧をきれいに見せたいときは、registry 形式の JSON を別に置いて `bbox` と `portolan_registry:*` を書くか、公式 registry に登録する（登録は外に出す話なので別に決める）
