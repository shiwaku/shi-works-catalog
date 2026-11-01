# shi-works への Portolan 導入 要件定義

最終更新: 2026-11-01（たたき台）

## 0. 前提

- 既存のデータは Cloudflare R2 のバケット `shi-works` にあり、カスタムドメイン `https://shi-works.com/` で公開している。運用の記録は [shiwaku/cloudflare-infra](https://github.com/shiwaku/cloudflare-infra) にある。
- カタログは**別のバケット `shi-works-catalog`** に置き、`https://catalog.shi-works.com/` で公開する（第6章）。このバケットはカタログ専用ではなく、**shi-works のデータ配信の本体**になる（データもカタログと同じツリーに置く）。
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

**メタデータは日英併記にする**（title、description、README.md、AGENTS.md、列の説明）。書き方の細部は #12 で決める。

表示用は、事前に作ったファイルを置くのではなく、第4章の方式②（Worker でリクエストのたびに作る）で配ることを基本にする。表の「表示用」は、カタログから指す先の形式を表す。

## 4. 配信方式

| 方式 | 採用 | 対象 |
|---|---|---|
| ① 事前にタイルを作る | 方式②で間に合わないときだけ | 3D Tiles（点群）、方式②で速さや費用が合わないデータ |
| ② Worker でリクエストのたびに作る | **基本の方式** | GeoParquet からベクタタイル、COG からラスタタイルを作る。仕組みは #8 で決めて検証する |
| ③ ブラウザで直接読む | 補助的に使う | COPC（Potree、viewer.copc.io）、小さい GeoParquet |

**決定（2026-11-01、#20）**: タイルは動的に配信する（方式②を基本にする）。正本だけを置き、表示用のタイルを二重に持たないため（第8章の費用）。

## 5. 既存URLの扱い

**決定（2026-11-01、#20）**: 既存のデータは `shi-works-catalog` に**コピー**し、新しい仕組みで配信できるようになってから `shi-works` から**削除する**。

- 新しいデータは、最初から Portolan の構成で置く。
- 既存のデータは、コピーしてカタログに載せる。カタログから既存の URL を参照するだけの形（`add-external`）にはしない。
- コピーしてから削除するまでの間だけ、容量が倍になる。データを長く二重に持たない（第8章の費用）。
- 削除してよい条件と、既存の URL（`https://shi-works.com/...`）の利用者への対応（Worker で振り分けるか、告知して切り替えるか）は #7 で決める。

## 6. ファイルの置き方

**決定（2026-10-31）**: カタログは専用バケット `shi-works-catalog` のルートに置き、`catalog.shi-works.com` で公開する。下位カタログは**テーマ**で分ける。

**決定（2026-11-01、#2）**: `shi-works-catalog` はカタログ専用ではなく、**データ配信の本体**にする。バケット名とサブドメインは変えない。`shi-works.com` を Worker で新しいバケットへ振り分ける入口にするかどうかは、既存データの移行方針（#7）で決める。

```
s3://shi-works-catalog/          → https://catalog.shi-works.com/catalog.json
├── catalog.json / README.md / AGENTS.md
├── terrain/                     地形
│   └── csmap/                   ← 下位カタログ（CS立体図）
│       └── osaka/               ← コレクション（COG）
├── imagery/                     空中写真
├── buildings/                   建物・3D都市
│   └── plateau/                 ← 下位カタログ（PLATEAU）
├── transport/                   交通
│   └── npa-traffic-accident/    ← コレクション（GeoParquet）
├── population/                  人口
├── disaster/                    防災
├── land/                        土地利用・都市計画
├── boundaries/                  境界・住所
├── livelihood/                  暮らし
└── basemaps/                    ベースマップ
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
- **専用バケットにする。** R2 の API トークンはバケット単位でしか絞れない。既存の `shi-works` と同じバケットにすると、push 用のトークンで既存データも上書きできてしまう。専用バケットなら、トークンをカタログだけに絞れる。CORS の設定と容量も、既存データと分けて管理できる。
- **サブドメインで公開する。** R2 のカスタムドメインは1つのバケットに1つなので、`shi-works.com/catalog/` にはできない（Worker でパスを振り分ければできるが、仕組みが増える）。
- **名前を `catalog` にする。** ツールの名前（portolan）を URL に入れないので、ツールを替えても名前が嘘にならない。
- **データ配信の本体になっても名前は変えない。** Portolan では、データは各コレクションのフォルダに入り、カタログと同じツリーに置かれる。バケット全体が1つのカタログなので、`catalog` という名前は中身と合っている。作り直さないので、決めたこと（プロファイル名など）もそのまま使える。

決まりごと:

- コレクションの ID は、ルートからのパス（例: `transport/npa-traffic-accident`）。
- コレクションの中にコレクションは入れられない（仕様の MUST）。
- 子が20以上になったら、さらに下位カタログを足す（仕様の SHOULD）。例: CS立体図が20県を超えたら `terrain/csmap/` を1段足す。
- テーマの一覧と既存データの割り振り、迷うものの決め方は [themes.md](themes.md) に書く。
- 書き込みは `portolan push s3://shi-works-catalog`。`shi-works-catalog` だけに書き込める R2 の API トークンを新しく作り、専用の AWS プロファイル `r2-shiworks-catalog` に入れる。既存の `r2-shiworks` は使わない。
- 手元のカタログは、このリポジトリの `catalog/` に置く（メタデータは git で管理し、データ本体は .gitignore で除く）。

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
| Range リクエスト | 206、`Accept-Ranges: bytes` | ✅（`shi-works`） | `shi-works-catalog` でも確かめる |
| CORS: 許可するリクエストヘッダー | Range、If-Match、If-None-Match、If-Modified-Since、If-Unmodified-Since | ⚠️ `shi-works` は **If-Modified-Since と If-Unmodified-Since が 403** | `shi-works-catalog` は設定済み（2026-10-31）。`shi-works` は既存データを参照で載せないので、直すかどうかは #16 で判断する |
| CORS: 公開するレスポンスヘッダー | Content-Type、Content-Length、Content-Range、Accept-Ranges、ETag | ⚠️ `shi-works` は **Content-Type がない** | 同上 |
| キャッシュ | — | 512 MB を超えるファイルはエッジでキャッシュされない | GeoParquet は 2 GB を超えたら分割する。PMTiles の大きさの方針を決める |
| コスト | — | R2 は転送料が無料。今の利用量では、費用のほとんどが保存容量 | **データを二重に持たない**。表示用のタイルは事前に作らず動的に配信し、既存データは移行が済んだら削除する。Worker のリクエスト数と R2 の読み取り回数は、#8 の検証で見積もる |
| 更新 | — | — | `versions.json` によるバージョン管理と、差し替えの手順を決める |

## 9. 段階的な進め方

| 段階 | 内容 | 終わりの条件 |
|---|---|---|
| 0. 基盤 | `shi-works-catalog` バケット、カスタムドメイン `catalog.shi-works.com`、専用の API トークンと CORS の用意。カタログのルート作成、作業環境の用意 | `https://catalog.shi-works.com/catalog.json` が公開され、`check` に通る。Range と CORS は手で確かめる（データがないと `--live` は検査を飛ばすため）。**2026-11-01 に完了** |
| 1. 新しいベクタ | 新しいデータセット1件を GeoParquet の正本で公開する | `check --strict` と `check --live` に通る |
| 2. 既存のベクタ | `geoparquet/` と `pmtiles/` をコピーして載せる。PMTiles しかないものは GeoParquet を作る | 対象を一覧にし、順に載せる |
| 3. ラスタ | COG の正本と、XYZ タイルの表示用の組。まず CS立体図から | `rel: "xyz"` を含めて `check` に通る |
| 4. 点群と 3D | COPC と 3D Tiles。Portolan の点群仕様が固まってから | — |
| 5. 動的配信 | 基本の方式なので、段階としては独立させない。仕組みの決定と検証は #8 で、第1段階と並行して進める | — |
| 6. registry | portolan-registry への登録 | — |

## 10. 未決事項

1. ~~カタログの置き場所と、下位カタログの分け方~~ → 専用バケット `shi-works-catalog`（`catalog.shi-works.com`）とテーマ別に決定（第6章）。残っているのは**テーマの一覧を確定させること**（既存データをすべて割り振って決める）
2. 第1段階で入れる新しいデータセット
3. PMTiles を tippecanoe と tylertoo のどちらで作るか
4. CORS の変更手順を cloudflare-infra の runbook として残すか
5. ~~既存データを参照で載せるかコピーで載せるか~~ → コピーしてから削除すると決定（第5章）。削除の条件は #7
6. 更新の運用とバージョン管理
7. `shi-works.com` の位置づけ（Worker で `shi-works-catalog` へ振り分ける入口にするか）。既存データの移行方針（#7）と合わせて決める
