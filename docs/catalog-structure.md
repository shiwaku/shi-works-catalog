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
| `national/` | 国の機関 | `gsi`（国土地理院）、`mlit`（国土交通省）、`ksj`（国土数値情報）、`plateau`、`npa`（警察庁）、`jma`（気象庁）、`digital-agency`（デジタル庁）、`rinya`（林野庁） |
| `prefectures/` | 都道府県 | `osaka`、`shizuoka`、`tokyo` など |
| `municipalities/` | 市区町村 | `shizuoka-city`、`saitama-city` |
| `others/` | 国外の機関、大学、民間、コミュニティ | `osm`、`worldpop`、`google`、`usgs`、`gebco`、`mapterhorn`、`jartic`、`tohoku-u` |
| `shi-works/` | shi-works が複数の提供元を組み合わせて作ったもの | 管理者の段は、作ったものの系統で分ける（例: `food-access`、`transport-analysis`） |

`ksj` と `plateau` は国土交通省のデータだが、製品の系統ごとにデータが多く、利用条件もデータごとに決まっているので、`mlit` とは別の管理者の段にする（Portolan の「製品の系統で下位カタログにまとめる」に当たる）。

## 迷うものの決め方

1. **元データの提供元が1つなら、その提供元に置く。** 形式の変換、集計、可視化（CS立体図、メッシュ集計など）をしても、出典とライセンスは元の提供元のものを受け継ぐので、元の提供元に置く。
2. **複数の提供元のデータを組み合わせて新しく作ったものは `shi-works/` に置く。** 例: 食料品アクセス（店舗、人口、道路）、公共交通の空白地帯（バス停、人口）。使った提供元は、すべて `providers` に書く。
3. **OSM から作ったタイルは `others/osm/` に置く。** OpenMapTiles と Protomaps はどちらも OSM のデータで、ライセンス（ODbL）が同じ。
4. **同じデータの地区違いは、1つのコレクションの Item にする。** 例: PLATEAU の市ごとの建物、東京都の CS立体図（23区、多摩、島しょ）。子が20を超えても、深さを崩さずに済む。
5. **テーマや地域から探せるようにする。** ルートの README に、テーマ（地形、交通、人口、防災など）ごとのコレクションの表を載せる。各コレクションの `keywords` にもテーマを書く。

## 子の数

| 下位カタログ | 管理者の数（今） | 注意 |
|---|---|---|
| `national/` | 8 | — |
| `prefectures/` | 18 | 最大47。20を超えると PTL-CAT-001（SHOULD）の警告が出る。下の「決めること」を参照 |
| `municipalities/` | 2 | — |
| `others/` | 10前後 | — |
| `shi-works/` | 数個 | — |

## 決めること

- **都道府県が20を超えたときの扱い**: 地方（`kanto/` など）の段を足すと深さが崩れ、URL も変わる。都道府県は47で上限が決まっていて、一覧として読みやすいので、**警告を受け入れて地方の段は作らない**案にしている。
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
| `gsi` | `pmtiles/gsi/kokuarea/` | 要確認: 中身 |
| `gsi` | `mvt/gsi-3dmap-bldg-tiles/`、`3dtiles/gsi-3dmap/` | 3D地図の建物 |
| `mlit` | `json/mlit-road-traffic-census/`、`pmtiles/mlit-road-traffic-census/`、`pmtiles/traffic-census/traffic_census_*` | 道路交通センサス |
| `mlit` | `pmtiles/mlit/toshik/a.pmtiles` | 要確認: 都市計画か |
| `mlit` | `pmtiles/landform/` | 地形分類（要確認: 土地分類基本調査か） |
| `mlit` | `pmtiles/boring-data-converter/` | ボーリング柱状図（要確認: 国土地盤情報か） |
| `ksj` | `pmtiles/ksj/`（A29、N02、N03、N05、N06、N07、P05、P11、W05、A16、prefectures） | 用途地域、鉄道、行政区域、高速道路、バス路線、役場、バス停、河川、DID、都道府県 |
| `ksj` | `pmtiles/ksj-route-search/` | 道路（N13） |
| `ksj` | `pmtiles/mlit-ksj/C28-21_Airport.pmtiles`、`L01-24.pmtiles`、`L03-b-21*`、`raster-tiles/mlit-ksj/` | 空港、地価公示、土地利用細分メッシュ |
| `ksj` | `pmtiles/traffic-accident/P29-21_primary_school.pmtiles`、`pmtiles/mlit/toshik/P05-*` | 学校、役場 |
| `plateau` | `pmtiles/plateau/` | 建物 LOD1（市ごとに Item） |
| `plateau` | `pmtiles/plateau-osaka-expo-2025-3d/`、`3dtiles/plateau/` | 万博会場、竹芝 |
| `npa` | `geoparquet/npa-traffic-accident-analytics/`、`pmtiles/npa-traffic-accident/`、`pmtiles/traffic-accident/`（honhyo、mesh） | 交通事故統計 |
| `jma` | `pmtiles/jma-earthquake/`、`mlt/jma-earthquake/` | 震度・震源 |
| `digital-agency` | `pmtiles/digital/abr/` | アドレス・ベース・レジストリ |
| `rinya` | `raster-tiles/rinya/noto-2024-csmap-tiles/` | 能登の CS立体図 |
| 要確認 | `pmtiles/r2DID/`、`pmtiles/traffic-census/2020_did_*` | 人口集中地区（2020）。総務省統計局なら管理者 `stat` を足す |
| 要確認 | `pmtiles/100m_mesh_pop2020/` | 100m メッシュ人口。元データの提供元 |

### prefectures/ 都道府県

| 管理者 | 既存のパス | 中身 |
|---|---|---|
| `akita` | `pmtiles/pref-akita/` | 地震被害想定（要確認） |
| `saitama` | `raster-tiles/pref-saitama/`、`3dtiles/pref-saitama/`、`3dtiles/saitama-rpc/` | CS立体図、河川の点群 |
| `tokyo` | `raster-tiles/tokyo-digitaltwin/`（CS立体図は1つのコレクションに地区ごとの Item、DSM）、`copc/tokyo-digitaltwin/`、`3dtiles/toyko-23ku-pc/`、`3dtiles/tokyo/`（要確認） | デジタルツインの点群、CS立体図、DSM |
| `tokyo` | `pmtiles/tokyo/R03Building.pmtiles`、`mvt/13103_minato-ku_pref_2023_bldg_mvt/` | 都市計画基礎調査の建物 |
| `tokyo` | `pmtiles/npa/hanzaiopendata/` | 犯罪（警視庁のオープンデータ。要確認） |
| `kanagawa`、`kyoto`、`miyagi`、`nagano`、`okayama`、`osaka`、`toyama`、`wakayama`、`hiroshima` | `raster-tiles/pref-*/` | CS立体図 |
| `toyama` | `pmtiles/pref-toyama/` | 樹木（単木） |
| `ishikawa` | `raster-tiles/pref-ishikawa/notowest-red-tiles/` | 赤色立体地図（能登西部） |
| `shizuoka` | `raster-tiles/pref-shizuoka/`、`cog/VIRTUAL_SHIZUOKA/`、`3dtiles/shizuoka-pc/` | CS立体図、標高、DSM、オルソ画像、点群 |
| `yamanashi` | `raster-tiles/pref-yamanashi/`、`pmtiles/pref-yamanashi/` | CS立体図、標高 |
| `tottori` | `raster-tiles/pref-tottori/`、`pmtiles/pref-tottori/`、`geojson/pref-tottori/` | CS立体図、標高、点群の範囲 |
| `yamagata` | `raster-tiles/pref-yamagata/rpc-dsm/` | DSM |
| `nagasaki` | `3dtiles/open_nagasaki/`、`cog/open-nagasaki/` | 3D（駅、ハウステンボスなど）、CS立体図 |
| 要確認 | `3dtiles/nakano-sunplaza-pc/` | 中野サンプラザの点群。提供元（東京都か中野区か） |

### municipalities/ 市区町村

| 管理者 | 既存のパス | 中身 |
|---|---|---|
| `shizuoka-city` | `cog/city-shizuoka/`、`pmtiles/city-shizuoka/` | オルソ画像、基本図 |
| `saitama-city` | `pmtiles/city-saitama/` | 建物、陰影 |

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
| 要確認 | `pmtiles/sharecycle/` | シェアサイクルのポート（ドコモ・バイクシェア、HELLO CYCLING。2社なので `shi-works/` かもしれない） |
| 要確認 | `pmtiles/gtfs-gis/railway_honsu/` | 鉄道の運行本数（GTFS-GIS か、複数社の GTFS から作ったなら `shi-works/`） |

### shi-works/ 複数の提供元を組み合わせて作ったもの

| 管理者の段 | 既存のパス | 中身 |
|---|---|---|
| `food-access` | `pmtiles/japan-food-access-analysis/`、`pmtiles/food-access/`、`pmtiles/japan-food-store-master/` | 食料品アクセス、フードデザート、食料品店 |
| `transport-analysis` | `pmtiles/japan-legal-speed-30kmh-map/`、`pmtiles/mlit-ksj/transit_desert_*` | 法定速度 30km/h の道路、公共交通の空白地帯 |

### 要確認（区分も決まらないもの）

| 既存のパス | わからないこと |
|---|---|
| `geoparquet/pcp/` | 中身と提供元 |
| `geojson/yamajiro/` | 山城の一覧の提供元 |
| `raster-tiles/expo2025/` | 中身（空中写真か）と提供元 |

### どこにも入れないもの

| 既存のパス | 理由 |
|---|---|
| `geoparquet/pref-saitama/`（`0` だけ） | 中身がない |
| `_previous/` | 移行前の旧版 |
| `LICENSE.md`、`MIGRATION.md` | データではない |
