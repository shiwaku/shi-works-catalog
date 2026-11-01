# カタログの構成（区分と管理者）と、既存データの割り振り

最終更新: 2026-11-01（案。#3）

下位カタログは、テーマではなく**データの管理者（元の提供元）**で分ける（[requirements.md](requirements.md) 第6章）。根拠は Portolan のベストプラクティス [philosophy.md](https://github.com/portolan-sdi/portolan-spec/blob/main/specs/best-practices/philosophy.md) の "Scope by steward, not by theme" と "Shallow and uniform beats deep and clever"。

ここでは、`shi-works` バケットの既存データ（2026-11-01 時点）をすべて割り振る。フォルダ名は URL の一部になるので、後から変えにくい。フォルダ名の書き方（ハイフンかアンダースコアか、都道府県コードを付けるか）は #4 で決め、ここでは仮の名前を使う。

## 構成

```
<区分>/<管理者>/<コレクション>/
```

どのコレクションもこの深さにそろえる。

| 区分 | 中身 | 管理者の例 |
|---|---|---|
| `national/` | 国の機関 | `gsi`（国土地理院）、`mlit`（国土交通省）、`ksj`（国土数値情報）、`plateau`、`npa`（警察庁）、`stat`（総務省統計局）、`jma`（気象庁）、`digital-agency`（デジタル庁）、`rinya`（林野庁） |
| `prefectures/` | 都道府県 | `osaka`、`shizuoka`、`tokyo` など |
| `municipalities/` | 市区町村 | `shizuoka-city`、`saitama-city` |
| `others/` | 国外の機関、大学、民間、コミュニティ | `osm`、`worldpop`、`google`、`usgs`、`gebco`、`mapterhorn`、`jartic`、`tohoku-u` |
| `shi-works/` | shi-works が複数の提供元を組み合わせて作ったもの | 管理者の段は、作ったものの系統で分ける（例: `food-access`、`transport-analysis`） |

`ksj` と `plateau` は国土交通省のデータだが、製品の系統ごとにデータが多く、利用条件もデータごとに決まっているので、`mlit` とは別の管理者の段にする（Portolan の「製品の系統で下位カタログにまとめる」に当たる）。

## 迷うものの決め方

1. **元データの提供元が1つなら、その提供元に置く。** 形式の変換、集計、可視化（CS立体図、メッシュ集計など）をしても、出典とライセンスは元の提供元のものを受け継ぐので、元の提供元に置く。
2. **複数の提供元のデータを組み合わせて新しく作ったものは `shi-works/` に置く。** 例: 食料品アクセス（店舗、人口、道路）、公共交通の空白地帯（バス停、人口）。使った提供元は、すべて `providers` に書く。
3. **OSM から作ったタイルは `others/osm/` に置く。** OpenMapTiles と Protomaps はどちらも OSM のデータで、ライセンス（ODbL）が同じ。
4. **同じデータの地区違いは、1つのコレクションの Item にする。** 例: PLATEAU の市ごとの建物、東京都の CS立体図（23区、多摩、島しょ）。コレクションの深さは崩さずに済む。Item が20以上になるときは、コレクションの下にカタログを置いてまとめる（例: PLATEAU は都道府県ごと）。
5. **テーマや地域から探せるようにする。** ルートの README に、テーマ（地形、交通、人口、防災など）ごとのコレクションの表を載せる。各コレクションの `keywords` にもテーマを書く。

## 子の数

| 下位カタログ | 管理者の数（今） | 注意 |
|---|---|---|
| `national/` | 9 | — |
| `prefectures/` | 18 | 最大47。子はどれもカタログ（管理者）なので、PTL-CAT-001 の数には入らない |
| `municipalities/` | 3 | — |
| `others/` | 10前後 | — |
| `shi-works/` | 数個 | — |

## 決めること

- フォルダ名の書き方は #4 で決める。

## 既存データの割り振り

パスは `https://shi-works.com/` からの相対パス。古い版・作業用のファイル（`_v2` と無印が並ぶもの、CSV の中間ファイルなど）をどれだけ載せるかは、移行（#7）のときに決める。ここではフォルダ単位で割り振る。

### national/ 国の機関

| 管理者 | 既存のパス | 中身 |
|---|---|---|
| `gsi` | `raster-tiles/gsi/gsi-dem-terrain-rgb/` | 標高タイル |
| `gsi` | `pmtiles/gsi/hinanbasho/` | 指定緊急避難場所 |
| `gsi` | `pmtiles/gsi/denshouhi/` | 自然災害伝承碑 |
| `gsi` | `pmtiles/gsi/gsimaps_vector/` | 地理院地図ベクタ |
| `gsi` | `pmtiles/gsi/optimal_bvmap/` | 最適化ベクタタイル（道路中心線など） |
| `gsi` | `pmtiles/gsi/kokuarea/` | 空港等の周辺空域（地理院タイルの形式。元は航空局） |
| `gsi` | `mvt/gsi-3dmap-bldg-tiles/`、`3dtiles/gsi-3dmap/` | 3D地図の建物 |
| `gsi` | `pmtiles/landform/` | 地形分類（自然地形）。地理院の GeoJSON タイルを PMTiles にしたもの（推定） |
| `mlit` | `json/mlit-road-traffic-census/`、`pmtiles/mlit-road-traffic-census/`、`pmtiles/traffic-census/traffic_census_*` | 道路交通センサス |
| `mlit` | `pmtiles/mlit/toshik/a.pmtiles` | 都市計画決定 GIS データ（防火地域、地区計画、都市計画道路など） |
| `mlit` | `pmtiles/boring-data-converter/` | ボーリング柱状図（国土地盤情報の XML から作成） |
| `ksj` | `pmtiles/ksj/`（A29、N02、N03、N05、N06、N07、P05、P11、W05、A16、prefectures） | 用途地域、鉄道、行政区域、高速道路、バス路線、役場、バス停、河川、DID、都道府県 |
| `ksj` | `pmtiles/ksj-route-search/` | 道路（N13） |
| `ksj` | `pmtiles/mlit-ksj/C28-21_Airport.pmtiles`、`L01-24.pmtiles`、`L03-b-21*`、`raster-tiles/mlit-ksj/` | 空港、地価公示、土地利用細分メッシュ |
| `ksj` | `pmtiles/traffic-accident/P29-21_primary_school.pmtiles`、`pmtiles/mlit/toshik/P05-*` | 学校、役場 |
| `plateau` | `pmtiles/plateau/` | 建物 LOD1（市ごとに Item） |
| `plateau` | `pmtiles/plateau-osaka-expo-2025-3d/`、`3dtiles/plateau/` | 万博会場、竹芝 |
| `plateau`（推定） | `3dtiles/tokyo/` | 東京駅・丸の内付近の 3D Tiles（東経139.758〜139.776度、北緯35.676〜35.689度、約1.7GB）。タイルの作成ツールが `cesiumtiles-gltf`（PLATEAU GIS Converter が使うライブラリ）で、`{z}/{x}/{y}.glb` の構成も同じなので、PLATEAU の建物を変換したものと推定 |
| `npa` | `geoparquet/npa-traffic-accident-analytics/`、`pmtiles/npa-traffic-accident/`、`pmtiles/traffic-accident/`（honhyo、mesh） | 交通事故統計 |
| `npa` | `pmtiles/npa/hanzaiopendata/` | 犯罪オープンデータ |
| `jma` | `pmtiles/jma-earthquake/`、`mlt/jma-earthquake/` | 震度・震源 |
| `digital-agency` | `pmtiles/digital/abr/` | アドレス・ベース・レジストリ |
| `rinya` | `raster-tiles/rinya/noto-2024-csmap-tiles/` | 能登の CS立体図 |
| `stat` | `pmtiles/r2DID/`、`pmtiles/traffic-census/2020_did_*` | 人口集中地区（2020、総務省統計局の e-Stat 境界データ） |

### prefectures/ 都道府県

| 管理者 | 既存のパス | 中身 |
|---|---|---|
| `akita` | `pmtiles/pref-akita/` | 地震被害想定（震度、液状化など。想定地震ごとのレイヤー） |
| `saitama` | `raster-tiles/pref-saitama/`、`3dtiles/pref-saitama/`、`3dtiles/saitama-rpc/` | CS立体図、河川の点群 |
| `saitama`（推定） | `geoparquet/pcp/` | 点群を Point Cloud Parquet にした試作（平面直角座標系 第IX系、秩父付近の1図郭、約2.5億点）。試作なので、載せるかは移行（#7）で決める |
| `tokyo` | `raster-tiles/tokyo-digitaltwin/`（CS立体図は1つのコレクションに地区ごとの Item、DSM）、`copc/tokyo-digitaltwin/`、`3dtiles/toyko-23ku-pc/` | デジタルツインの点群、CS立体図、DSM |
| `tokyo` | `pmtiles/tokyo/R03Building.pmtiles`、`mvt/13103_minato-ku_pref_2023_bldg_mvt/` | 都市計画基礎調査の建物 |
| `kanagawa`、`kyoto`、`miyagi`、`nagano`、`okayama`、`osaka`、`toyama`、`wakayama`、`hiroshima` | `raster-tiles/pref-*/` | CS立体図 |
| `toyama` | `pmtiles/pref-toyama/` | 森林の単木データ（樹種、胸高直径など） |
| `ishikawa` | `raster-tiles/pref-ishikawa/notowest-red-tiles/` | 赤色立体地図（能登西部） |
| `shizuoka` | `raster-tiles/pref-shizuoka/`、`cog/VIRTUAL_SHIZUOKA/`、`3dtiles/shizuoka-pc/` | CS立体図、標高、DSM、オルソ画像、点群 |
| `yamanashi` | `raster-tiles/pref-yamanashi/`、`pmtiles/pref-yamanashi/` | CS立体図、標高 |
| `tottori` | `raster-tiles/pref-tottori/`、`pmtiles/pref-tottori/`、`geojson/pref-tottori/` | CS立体図、標高、点群の範囲 |
| `yamagata` | `raster-tiles/pref-yamagata/rpc-dsm/` | DSM |
| `nagasaki` | `3dtiles/open_nagasaki/`、`cog/open-nagasaki/` | 3D（駅、ハウステンボスなど）、CS立体図 |

### municipalities/ 市区町村

| 管理者 | 既存のパス | 中身 |
|---|---|---|
| `shizuoka-city` | `cog/city-shizuoka/`、`pmtiles/city-shizuoka/` | オルソ画像、基本図 |
| `saitama-city` | `pmtiles/city-saitama/` | 建物、陰影 |
| `nakano-city` | `3dtiles/nakano-sunplaza-pc/` | 中野サンプラザの点群（[中野区](https://www.city.tokyo-nakano.lg.jp/kanko/city-promotion/Sunplaza_3D.html)、CC BY 4.0。元は LAS、東京都オープンデータカタログで配布） |

### others/ 国外の機関、大学、民間、コミュニティ

| 管理者 | 既存のパス | 中身 |
|---|---|---|
| `osm` | `pmtiles/osm/`、`pmtiles/protomaps/` | OpenMapTiles、Protomaps（日本） |
| `worldpop` | `pmtiles/WorldPop/` | WorldPop |
| `google` | `pmtiles/google/` | 建物ポリゴン |
| `usgs` | `mlt/usgs-hypocenter/` | 震源 |
| `gebco` | `raster-tiles/gebco/` | 海底地形 |
| `mapterhorn` | `pmtiles/mapterhorn/` | 標高 |
| `jartic` | `pmtiles/jartic-traffic-regulation-converter/`、`pmtiles/traffic-accident/*kisei*` | 交通規制 |
| `tohoku-u` | `pmtiles/tohoku-u_tsunami/` | 津波の痕跡 |
| `gosenzo-net` | `geojson/yamajiro/` | 城の一覧（[gosenzo.net](https://gosenzo.net/yamajiro/) の記事から作成。掲載の許可を得ている。ライセンスと出典の書き方は #13 で決める） |
| `hello-cycling` | `pmtiles/sharecycle/hellocycling_*` | HELLO CYCLING のポート（GBFS） |
| `docomo-bikeshare` | `pmtiles/sharecycle/docomo*` | ドコモ・バイクシェアのポート（GBFS） |
| `gtfs-gis` | `pmtiles/100m_mesh_pop2020/` | 令和2年 簡易100mメッシュ人口（西沢明、[GTFS-GIS.jp](https://gtfs-gis.jp/teikyo/kani_100m_download2020.html)）。ページには免責の記載だけで、ライセンスと出典表記の指定がない（#13 で扱う） |
| `gtfs-gis`（推定） | `pmtiles/gtfs-gis/railway_honsu/` | 鉄道の運行本数（2024）。GTFS-GIS.jp のデータか要確認 |

### shi-works/ 複数の提供元を組み合わせて作ったもの

| 管理者の段 | 既存のパス | 中身 |
|---|---|---|
| `food-access` | `pmtiles/japan-food-access-analysis/`、`pmtiles/food-access/`、`pmtiles/japan-food-store-master/` | 食料品アクセス、フードデザート、食料品店 |
| `transport-analysis` | `pmtiles/japan-legal-speed-30kmh-map/`、`pmtiles/mlit-ksj/transit_desert_*` | 法定速度 30km/h の道路、公共交通の空白地帯 |

### どこにも入れないもの

| 既存のパス | 理由 |
|---|---|
| `geoparquet/pref-saitama/`（`0` だけ） | 中身がない |
| `raster-tiles/expo2025/` | 万博の「非公式マップ」の画像。作者と利用条件がわからないので載せない（2026-11-01 決定） |
| `_previous/` | 移行前の旧版 |
| `LICENSE.md`、`MIGRATION.md` | データではない |
