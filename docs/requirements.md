# shi-works への Portolan 導入 要件定義

最終更新: 2026-10-31（たたき台）

## 0. 前提

- 対象は Cloudflare R2 のバケット `shi-works`。カスタムドメイン `https://shi-works.com/` で公開している。運用の記録は [shiwaku/cloudflare-infra](https://github.com/shiwaku/cloudflare-infra) にある。
- Portolan は STAC 1.1 の静的カタログに要件を足したもの。正本はクラウドネイティブ形式で置き、README.md と AGENTS.md を必ず付ける。サーバーは使わない。
- 根拠にした資料: [portolan-spec](https://github.com/portolan-sdi/portolan-spec) の `specs/portolan/core.md` と `formats.md`、[portolan-cli](https://github.com/portolan-sdi/portolan-cli) のソース（2026-10-31 時点）。

## 1. 目的

| 目的 | 中身 | 対象 |
|---|---|---|
| データの発見性 | STAC カタログと README で、何があるかを人と STAC ツールに伝える | ✅ |
| AIエージェント対応 | AGENTS.md と列の説明（`table:columns`）で、エージェントがデータを直接扱えるようにする | ✅ |
| 自分の管理の整理 | 出典、ライセンス、更新履歴をデータと同じ場所に決まった形で残す | ✅ |
| registry への登録 | portolan-registry に載せる | 将来の候補（第6段階） |

## 2. 対象データ（最終的にはすべて）

バケットにある形式と、Portolan での扱い。

| フォルダ | 形式 | 仕様上の位置づけ | 扱い |
|---|---|---|---|
| `geoparquet/` | GeoParquet | ベクタの正本（必須） | 対象。仕様の条件を満たすか検査する |
| `pmtiles/` | PMTiles（ベクタ） | ベクタの表示用（SHOULD） | 対象。正本の GeoParquet を用意する必要がある |
| `geojson/` | GeoJSON | 副データとしてなら可 | GeoParquet にして、元ファイルは副データとして残す |
| `cog/` | COG | ラスタの正本（必須） | 対象。オーバービューと統計値の埋め込みを検査する |
| `raster-tiles/` | XYZ（WebP、PNG） | 仕様に定めなし | 表示用として、COG の正本に付ける |
| `copc/` | COPC | 点群の正本（**仕様は準備中**） | 仕様が固まり次第 |
| `3dtiles/` | 3D Tiles | 仕様に定めなし | 点群や建物の表示用として付ける方法を検討する |
| `mvt/` `mlt/` | ディレクトリ形式のベクタタイル | 仕様に定めなし | 表示用として付けるか、PMTiles に置き換える |
| `json/` | 非空間の JSON | 非空間の正本は Parquet | Parquet にする |

## 3. 正本と表示用の組

| 種類 | 正本（`data`） | 表示用（`visual`） | スタイル | 状態 |
|---|---|---|---|---|
| ベクタ | GeoParquet | PMTiles（`rel: "pmtiles"` のリンク） | MapLibre のスタイル（`styles/*.json`） | 仕様が固まっている |
| ラスタ | COG（RGB でも可。WebP 圧縮も可） | XYZ タイル（web-map-links の `rel: "xyz"`、**検証が通るか未確認**） | ラスタのスタイルは検討中（incubating） | 一部未確認 |
| 点群 | COPC | 3D Tiles、またはブラウザで直接読む | — | 仕様が準備中 |
| 非空間 | Parquet | — | — | 仕様が固まっている |

共通の要件: 正本とは別に、README.md、AGENTS.md、サムネイル、ライセンス、出典（providers）を付ける。

## 4. 配信方式

| 方式 | 採用 | 対象 |
|---|---|---|
| ① 事前にタイルを作る | **基本の方式** | PMTiles（ベクタ）、XYZ（ラスタ）、3D Tiles（点群） |
| ② Worker でリクエストのたびに作る | 将来の選択肢 | COG から表示用タイルを作る。既存の `dem2tiles-tiles`（`tiles.shi-works.com`）を広げられるか調べる |
| ③ ブラウザで直接読む | 補助的に使う | COPC（Potree、viewer.copc.io）、小さい GeoParquet |

## 5. 既存URLの扱い

- 既存のパスは**変えない**（利用者がいるため。MIGRATION.md で移行が済んだばかり）。
- 新しいデータは、最初から Portolan の構成で置く。
- 既存のデータは、次のどちらかでカタログに載せる（第2段階以降で決める）。
  - **参照だけする**: カタログから既存の https URL を絶対パスで指す（`add-external`、または href を手で書く）。URL は変わらない。
  - **コピーする**: カタログ用のフォルダにコピーし、既存のパスはそのまま残す。容量は倍になる。

## 6. ファイルの置き方

**決定（2026-10-31）**: ルートは `catalog/`、下位カタログは**テーマ**で分ける。

```
s3://shi-works/catalog/          → https://shi-works.com/catalog/catalog.json
├── catalog.json / README.md / AGENTS.md
├── terrain/                     地形
│   ├── osaka-csmap/             ← コレクション（COG と XYZ）
│   └── shizuoka-csmap/
├── transport/                   交通
│   ├── npa-traffic-accident/    ← GeoParquet と PMTiles
│   └── mlit-road-traffic-census/
├── population/                  人口
├── disaster/                    防災
└── buildings/                   建物・3D
```

1つのコレクションの中身（ベクタの場合）:

```
<theme>/<collection>/
├── collection.json / README.md / AGENTS.md
├── <name>.parquet               ← 正本
├── <name>.pmtiles               ← 表示用
├── styles/<name>.json
└── thumbnail.png
```

決めた理由:

- **形式では分けない。** Portolan では、1つのコレクションに正本と表示用を別の形式で一緒に入れる。形式で分けると、1つのデータセットが2か所に分かれる。
- **フォルダはテーマにする。** 地域と提供元は、メタデータ（bbox、providers、keywords）に書いて絞り込めるようにする。フォルダの階層は1つの軸でしか分けられない。
- **ルート名を `catalog/` にする。** ツールの名前（portolan）を URL に入れないので、ツールを替えても名前が嘘にならない。

決まりごと:

- コレクションの ID は、ルートからのパス（例: `transport/npa-traffic-accident`）。
- コレクションの中にコレクションは入れられない（仕様の MUST）。
- 子が20以上になったら、さらに下位カタログを足す（仕様の SHOULD）。例: CS立体図が20県を超えたら `terrain/csmap/` を1段足す。
- テーマの一覧は、既存データをすべて割り振って確定させる（未決事項1）。
- 書き込みは `portolan push s3://shi-works/catalog`。AWS プロファイル `r2-shiworks` を使う。

## 7. 作業環境

| 項目 | 内容 |
|---|---|
| CLI | portolan-cli（Python 3.11 以上。uv で入れる） |
| GeoParquet と COG への変換 | portolan-cli の中で geoparquet-io と rio-cogeo を使う |
| PMTiles の作成 | portolan 標準は **tippecanoe**（Windows 版がないので WSL を使う）。代わりに **tylertoo**（pip で入る）も使える。**どちらにするかは検証して決める** |
| 3D Tiles など | 既存の作り方を続ける |

## 8. 非機能要件

| 項目 | 要件 | 現状（2026-10-31 に確認） | 対応 |
|---|---|---|---|
| Range リクエスト | 206、`Accept-Ranges: bytes` | ✅ | — |
| CORS: 許可するリクエストヘッダー | Range、If-Match、If-None-Match、If-Modified-Since、If-Unmodified-Since | ⚠️ **If-Modified-Since と If-Unmodified-Since は 403** | R2 の CORS ルールに追加する |
| CORS: 公開するレスポンスヘッダー | Content-Type、Content-Length、Content-Range、Accept-Ranges、ETag | ⚠️ **Content-Type がない** | 追加する |
| キャッシュ | — | 512 MB を超えるファイルはエッジでキャッシュされない | GeoParquet は 2 GB を超えたら分割する。PMTiles の大きさの方針を決める |
| コスト | — | R2 は転送料が無料 | 正本と表示用の両方を置くので容量が増える。段階ごとに見積もる |
| 更新 | — | — | `versions.json` によるバージョン管理と、差し替えの手順を決める |

## 9. 段階的な進め方

| 段階 | 内容 | 終わりの条件 |
|---|---|---|
| 0. 基盤 | CORS の修正、カタログのルート作成、作業環境の用意、tippecanoe と tylertoo の比較 | ルートの catalog.json が公開され、`check` に通る |
| 1. 新しいベクタ | 新しいデータセット1件を GeoParquet と PMTiles の組で公開する | `check --strict` に通る |
| 2. 既存のベクタ | `geoparquet/` と `pmtiles/` を載せる（参照するかコピーするかを決める）。PMTiles しかないものは GeoParquet を作る | 対象を一覧にし、順に載せる |
| 3. ラスタ | COG の正本と、XYZ タイルの表示用の組。まず CS立体図から | `rel: "xyz"` を含めて `check` に通る |
| 4. 点群と 3D | COPC と 3D Tiles。Portolan の点群仕様が固まってから | — |
| 5. 動的配信 | Worker で COG からタイルを作れるか調べる | — |
| 6. registry | portolan-registry への登録 | — |

## 10. 未決事項

1. ~~カタログのルートのフォルダ名と、下位カタログの分け方~~ → `catalog/` とテーマ別に決定（第6章）。残っているのは**テーマの一覧を確定させること**（既存データをすべて割り振って決める）
2. 第1段階で入れる新しいデータセット
3. PMTiles を tippecanoe と tylertoo のどちらで作るか
4. CORS の変更手順を cloudflare-infra の runbook として残すか
5. 既存データを参照で載せるかコピーで載せるか（`add-external` で作ったコレクションが strict の検証に通るかを確かめてから決める）
6. 更新の運用とバージョン管理
