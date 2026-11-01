# テーマの一覧と、既存データの割り振り

最終更新: 2026-11-01（案。#3）

カタログの下位カタログ（第1階層のフォルダ）は**テーマ**で分ける（[requirements.md](requirements.md) 第6章）。テーマはデータの URL の一部になるので、後から変えにくい。ここでは、`shi-works` バケットの既存データ（2026-11-01 時点）をすべて割り振って一覧を決める。

## テーマの一覧

| フォルダ | テーマ | 入れるもの |
|---|---|---|
| `terrain/` | 地形 | 標高（DEM、DSM）、CS立体図、赤色立体地図、地形分類、地形の点群、河川・水系 |
| `imagery/` | 空中写真 | オルソ画像、空中写真 |
| `buildings/` | 建物・3D都市 | 建物の形状（2D、3D）、PLATEAU、建物や構造物の点群・3D Tiles |
| `transport/` | 交通 | 道路、鉄道、バス、空港、交通事故、交通量、交通規制、シェアサイクル |
| `population/` | 人口 | 人口メッシュ、人口集中地区（DID） |
| `disaster/` | 防災 | 地震、津波、避難場所、自然災害伝承碑 |
| `land/` | 土地利用・都市計画 | 用途地域、都市計画、土地利用、地価 |
| `boundaries/` | 境界・住所 | 行政区域、都道府県、住所、役所の位置 |
| `livelihood/` | 暮らし | 食料品へのアクセス、店舗、犯罪 |
| `basemaps/` | ベースマップ | 背景地図として使う、多くの地物をまとめたタイル（OSM、地理院地図のベクタなど） |

## 迷うものの決め方

1. **形式ではなく、何を表すデータかで決める。** 点群は、地面を測ったもの（河川、ダム、島の地形）なら `terrain/`、建物や駅などの構造物を測ったものなら `buildings/` に入れる。
2. **主題が2つにまたがるときは、利用者が探しに来るほうに入れる。** もう一方のテーマからは、STAC の `keywords` と README で見つけられるようにする。例: 人口集中地区は `population/`（交通の分析に使っても）。
3. **提供元や地域ではフォルダを分けない。** 提供元は `providers`、地域は `bbox` と `keywords` に書く。
4. **ベースマップは、主題を1つに絞れない総合的な背景地図だけにする。** 主題が1つのタイル（例: 地理院の道路中心線から作ったタイル）は、その主題のテーマに入れる。

## 下位カタログ（子が20以上になるもの）

| 下位カタログ | 中身 | 子の数（見込み） |
|---|---|---|
| `terrain/csmap/` | CS立体図（都府県・地区ごと） | 約24 |
| `buildings/plateau/` | PLATEAU の建物（市区町村ごと） | 40以上 |

コレクションの単位（都府県ごとか、まとめて1つか）は #4 で決める。

## 既存データの割り振り

パスは `https://shi-works.com/` からの相対パス。古い版・作業用のファイル（`_v2` と無印が並ぶもの、CSV の中間ファイルなど）をどれだけ載せるかは、移行（#7）のときに決める。ここではフォルダ単位で割り振る。

### terrain/ 地形

| 既存のパス | 中身 |
|---|---|
| `raster-tiles/pref-*/*-csmap-tiles/`、`raster-tiles/tokyo-digitaltwin/*-csmap-tiles/`、`raster-tiles/rinya/noto-2024-csmap-tiles/`、`cog/open-nagasaki/FD251-3857-CSMAP-COG.tif` | CS立体図 → `terrain/csmap/` |
| `raster-tiles/pref-ishikawa/notowest-red-tiles/` | 赤色立体地図（能登西部） |
| `raster-tiles/gsi/gsi-dem-terrain-rgb/` | 地理院の標高タイル |
| `raster-tiles/gebco/` | GEBCO の海底地形 |
| `pmtiles/mapterhorn/` | Mapterhorn の標高 |
| `raster-tiles/pref-shizuoka/shizuoka-alb-*`、`pmtiles/pref-yamanashi/`、`pmtiles/pref-tottori/` | 県の標高（航空レーザ） |
| `raster-tiles/pref-shizuoka/shizuoka-dsm-sample-tiles/`、`raster-tiles/pref-shizuoka/kawanehon-cho-sample-1/`、`raster-tiles/pref-yamagata/rpc-dsm/`、`raster-tiles/tokyo-digitaltwin/tokyo-station-dsm/` | DSM |
| `pmtiles/landform/` | 地形分類 |
| `pmtiles/ksj/W05_Stream_01-47.pmtiles` | 河川（国土数値情報） |
| `copc/tokyo-digitaltwin/`（aogashima、ogochi-dam、takahata-fudoson-tumulus） | 地形の点群 |
| `3dtiles/pref-saitama/river-pointcloud/`、`3dtiles/shizuoka-pc/tenryu-river/`、`3dtiles/shizuoka-pc/kawanehon-cho-sample-1/`、`3dtiles/saitama-rpc/` | 河川・地形の点群（3D Tiles） |
| `geojson/pref-tottori/jptottori-coverage_v1.geojson` | 鳥取県の点群の範囲 |
| `pmtiles/boring-data-converter/` | ボーリング柱状図（地盤） |

### imagery/ 空中写真

| 既存のパス | 中身 |
|---|---|
| `cog/VIRTUAL_SHIZUOKA/lp_orthophoto/` | 静岡県のオルソ画像 |
| `cog/city-shizuoka/`、`pmtiles/city-shizuoka/aerial-photo.pmtiles` | 静岡市のオルソ画像 |
| `raster-tiles/expo2025/` | 大阪・関西万博の会場（要確認: 空中写真か） |

### buildings/ 建物・3D都市

| 既存のパス | 中身 |
|---|---|
| `pmtiles/plateau/` | PLATEAU の建物 → `buildings/plateau/` |
| `pmtiles/plateau-osaka-expo-2025-3d/`、`3dtiles/plateau/` | PLATEAU（万博、竹芝） |
| `mvt/13103_minato-ku_pref_2023_bldg_mvt/` | 港区の建物 |
| `mvt/gsi-3dmap-bldg-tiles/`、`3dtiles/gsi-3dmap/` | 地理院の3D地図の建物 |
| `3dtiles/tokyo/` | 東京都の3D（要確認: 中身） |
| `pmtiles/tokyo/R03Building.pmtiles` | 東京都の建物 |
| `pmtiles/city-saitama/` | さいたま市の建物と陰影 |
| `pmtiles/google/` | Google の建物ポリゴン |
| `3dtiles/open_nagasaki/` | 長崎の3D（駅、ハウステンボスなど） |
| `3dtiles/nakano-sunplaza-pc/`、`3dtiles/toyko-23ku-pc/`、`3dtiles/shizuoka-pc/sunen-substation/`、`copc/tokyo-digitaltwin/hachioji-station-*` | 建物・構造物の点群 |

### transport/ 交通

| 既存のパス | 中身 |
|---|---|
| `geoparquet/npa-traffic-accident-analytics/`、`pmtiles/npa-traffic-accident/`、`pmtiles/traffic-accident/` | 交通事故統計（警察庁） |
| `json/mlit-road-traffic-census/`、`pmtiles/mlit-road-traffic-census/`、`pmtiles/traffic-census/` | 道路交通センサス |
| `pmtiles/jartic-traffic-regulation-converter/` | 交通規制（JARTIC） |
| `pmtiles/japan-legal-speed-30kmh-map/` | 法定速度 30km/h の道路 |
| `pmtiles/ksj-route-search/` | 道路網（国土数値情報） |
| `pmtiles/ksj/`（N02、N05、N06、N07、P11） | 鉄道、高速道路、バス路線、バス停 |
| `pmtiles/mlit-ksj/C28-21_Airport.pmtiles` | 空港 |
| `pmtiles/gtfs-gis/railway_honsu/` | 鉄道の運行本数 |
| `pmtiles/mlit-ksj/transit_desert_*.pmtiles` | 公共交通の空白地帯 |
| `pmtiles/gsi/optimal_bvmap/` | 道路中心線（地理院の最適化ベクタ） |
| `pmtiles/sharecycle/` | シェアサイクルのポート |
| `geoparquet/pcp/` | 要確認: 中身 |

### population/ 人口

| 既存のパス | 中身 |
|---|---|
| `pmtiles/100m_mesh_pop2020/` | 100m メッシュ人口（2020） |
| `pmtiles/WorldPop/` | WorldPop |
| `pmtiles/r2DID/`、`pmtiles/traffic-census/2020_did_ddsw_01-47_JGD2011.pmtiles`、`pmtiles/ksj/ksj-A16-1960-2015_DID.pmtiles` | 人口集中地区（DID） |

### disaster/ 防災

| 既存のパス | 中身 |
|---|---|
| `pmtiles/jma-earthquake/`、`mlt/jma-earthquake/` | 気象庁の震度・震源 |
| `mlt/usgs-hypocenter/` | USGS の震源 |
| `pmtiles/pref-akita/` | 秋田県の地震被害想定（要確認） |
| `pmtiles/tohoku-u_tsunami/` | 津波の痕跡（東北大学） |
| `pmtiles/gsi/hinanbasho/` | 指定緊急避難場所 |
| `pmtiles/gsi/denshouhi/` | 自然災害伝承碑 |

### land/ 土地利用・都市計画

| 既存のパス | 中身 |
|---|---|
| `pmtiles/ksj/A29_*` | 用途地域 |
| `pmtiles/mlit/toshik/` | 都市計画（要確認: `a.pmtiles` の中身） |
| `pmtiles/mlit-ksj/L03-b-21*`、`raster-tiles/mlit-ksj/L03-b-21_dissolved/` | 土地利用細分メッシュ |
| `pmtiles/mlit-ksj/L01-24.pmtiles` | 地価公示 |
| `pmtiles/pref-toyama/` | 富山の樹木（単木）（要確認: `environment/` を作るか） |
| `pmtiles/gsi/kokuarea/` | 要確認: 中身（空域なら `transport/`） |

### boundaries/ 境界・住所

| 既存のパス | 中身 |
|---|---|
| `pmtiles/ksj/N03-23_230101_gyouseikai.pmtiles`、`pmtiles/ksj/prefectures.geojson` | 行政区域、都道府県 |
| `pmtiles/digital/abr/` | アドレス・ベース・レジストリ（デジタル庁） |
| `pmtiles/ksj/P05-*`、`pmtiles/mlit/toshik/P05-*` | 市区町村役場 |

### livelihood/ 暮らし

| 既存のパス | 中身 |
|---|---|
| `pmtiles/japan-food-access-analysis/`、`pmtiles/food-access/` | 食料品アクセス、フードデザート |
| `pmtiles/japan-food-store-master/` | 食料品店 |
| `pmtiles/npa/hanzaiopendata/` | 犯罪（警視庁のオープンデータ） |

### basemaps/ ベースマップ

| 既存のパス | 中身 |
|---|---|
| `pmtiles/osm/` | OpenMapTiles（日本） |
| `pmtiles/protomaps/` | Protomaps（日本） |
| `pmtiles/gsi/gsimaps_vector/` | 地理院地図ベクタ |
| `pmtiles/city-shizuoka/kihonzu_*.pmtiles` | 静岡市の基本図 |

### どこにも入れないもの

| 既存のパス | 理由 |
|---|---|
| `geojson/yamajiro/` | 山城の一覧。要確認（`livelihood/` か、`culture/` を作るか） |
| `geoparquet/pref-saitama/`（`0` だけ） | 中身がない |
| `_previous/` | 移行前の旧版 |
| `LICENSE.md`、`MIGRATION.md` | データではない |
