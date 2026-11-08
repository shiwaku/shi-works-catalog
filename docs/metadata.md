# メタデータの整備方針

最終更新: 2026-11-02（#12。作り方は #19 で確かめて書き足した）

メタデータの整備が、この仕組みの肝になる。portolan-cli が自動で作るのは、列の名前と型、範囲、統計値くらいで、データの意味は人が書く。この文書は、コレクションごとに何を、どこに、どの言語で書くかを決める。

根拠は Portolan の仕様（[core.md](https://github.com/portolan-sdi/portolan-spec/blob/main/specs/portolan/core.md)）と、ベストプラクティス（[documentation.md](https://github.com/portolan-sdi/portolan-spec/blob/main/specs/best-practices/documentation.md)、[multilingual-catalogs.md](https://github.com/portolan-sdi/portolan-spec/blob/main/specs/best-practices/multilingual-catalogs.md)）。

## 1. 書くファイル

| ファイル | 読む人 | 書くこと |
|---|---|---|
| `collection.json` | STAC Browser、検索、エージェント | タイトル、説明、提供元、ライセンス、範囲、キーワード、列の説明（`table:columns`） |
| `README.md` | 使うかどうかを決める人 | 何のデータか、件数、使い方、列の表、使ってよいこと・いけないこと、ライセンスと出典、加工の記録 |
| `AGENTS.md` | 使うと決めたエージェント | 結合のキー、すぐ動く読み方、落とし穴、座標系、列の意味、集計の例、作り方のコマンド |
| `thumbnail.png` | 一覧を見る人 | データの見た目（必須。PTL-VIZ-001） |

- README と AGENTS.md は役割が違うので、同じ内容を写さない（documentation.md の "Two files, two audiences"）。AGENTS.md には `collection.json` にある事実（範囲、ライセンス、件数）を繰り返さない。
- `collection.json` の `description` と README は重なってよいが、食い違ってはいけない。

## 2. 日本語と英語

**日本語を正本にし、英語版を `en/` に別の木として置く。** Portolan の推奨（multilingual-catalogs.md）と同じ形。前の決定（1つのファイルの中で項目ごとに併記する）は取りやめる。

```
catalog/
├── catalog.json            ← 日本語（正本）
├── README.md
├── AGENTS.md
├── jp-npa/
│   └── traffic-accident/
│       ├── collection.json
│       ├── README.md
│       ├── AGENTS.md
│       └── jp-npa-traffic-accident.parquet   ← データは正本の木にだけ置く
└── en/
    ├── catalog.json        ← 英語版
    ├── README.md
    ├── AGENTS.md
    └── jp-npa/
        └── traffic-accident/
            ├── collection.json   ← データは ../../../jp-npa/... を相対パスで指す
            ├── README.md
            └── AGENTS.md
```

- 取りやめる理由:
  - 項目の中で日英を並べると、STAC Browser の表示も README も日英が混ざって読みにくい。言語の切り替えもできない。
  - Portolan の検査（rashid）は言語別の木を前提にしている（PTL-LNK-010 など）。
- 各 `catalog.json` と `collection.json` に STAC の Language 拡張（v1.0.0）を宣言し、`language`（その文書の言語）と `languages`（ほかの言語）を書く。日本語は `{"code": "ja", "name": "日本語", "alternate": "Japanese"}`、英語は `{"code": "en", "name": "English"}`。
- 日本語のルートと英語のルートを `alternate` リンク（`hreflang` 付き）で結ぶ。コレクションどうしも同じように結ぶ。`child` では結ばない。
- **両方の言語で同じにするもの:** コレクション ID、アセットのキー、列名、スタイルのレイヤー ID、座標参照系、ライセンスの識別子。
- **翻訳するもの:** タイトル、説明、キーワード、列の説明、README.md。提供元の名前は、それぞれの言語の正式名にする（警察庁 / National Police Agency）。
- **AGENTS.md は日本語だけで書く。** Portolan では原語のままでよい。英語の木にも AGENTS.md は必要（PTL-FIL-001）なので、日本語のものを置き、`agents` リンクに `hreflang: "ja"` を付ける。
- **英語版は日本語版から作る。** 直すときは日本語版を先に直し、同じ PR で英語版を更新する。英語版を直接直さない。portolan-cli には言語版を作る機能がないので、[`scripts/finalize_metadata.py`](../scripts/finalize_metadata.py) で作る。英語の文言は [`scripts/i18n/en.yaml`](../scripts/i18n/en.yaml)（タイトル、説明、キーワード、提供元の名前）と、コレクションごとの `columns.yaml`（列の説明）に置く。README.md は英語版を `en/` に手で書く。
- **用語集をルートの AGENTS.md に置く。** 訳語がぶれると検索と意味が崩れるため。例: 交通事故 / traffic accident、人身事故 / injury accident、当事者 / party、生活道路 / residential road。

## 3. コレクションごとに書く項目

| 項目 | 書く場所 | 中身 |
|---|---|---|
| タイトル | `collection.json` の `title` | 何のデータかがわかる名前。提供元の名前は入れない（パスと提供元の欄にあるため）。例: 交通事故統計（本票） / Traffic accident statistics (main records) |
| 説明 | `description` | 1〜3文。何を何件、いつからいつまで、どこを |
| 提供元 | `providers` | 下の第4章 |
| ライセンス | `license` | SPDX の識別子。当てはまらないときは `other` と `rel: "license"` のリンク（PTL-LIC-001、002）。決め方は [license.md](license.md) 第2章 |
| 出典の表示 | `attribution`（STAC の attribution 拡張）、README | 地図や資料に載せるときの表示。提供元が決めた書き方に合わせる（[license.md](license.md) 第3章） |
| 元データ | `rel: "via"` のリンク（`text/html`） | 提供元の公開ページ（PTL-PRO-001） |
| 更新日時 | `updated` | 元データを取り込んだ日時（RFC 3339。PTL-PRO-003） |
| 列の説明 | `table:columns` | 下の第5章 |
| キーワード | `keywords` | 下の第6章 |
| 版 | `version`（STAC の version 拡張） | データの版。元データの年次など（#5、#6） |
| 使ってよいこと・いけないこと | README | 実際に使われた例と、使ってはいけない場面（documentation.md の "Evaluate the data"） |
| 既知の注意点 | README、AGENTS.md | 偏り、欠け、定義（何をその種類に数えたか） |
| 加工の記録 | README（要約）、AGENTS.md（コマンド） | 元データから何をしたか（列名の変更、型、不正な座標の扱いなど） |
| 使い方の例 | README（1つ）、AGENTS.md（いくつか） | 公開 URL を使った、そのまま動く DuckDB のクエリ。載せる前に実行して確かめる |

- `title`、`description`、`providers`、`license`、`keywords` などは `.portolan/metadata.yaml` に書き、portolan-cli に `collection.json` を作らせる。portolan-cli の項目にないものは、作ったあとに `scripts/finalize_metadata.py` で足す。#19 で確かめた portolan-cli 0.8.0 の振る舞い:
  - `collection.json` に書くもの: `title`、`description`、`providers`、`license`（`other` なら `license_url` から `rel: "license"` のリンク）、`source_url` から `via` のリンク
  - 書かないもの（スクリプトで足す）: `keywords`、`attribution`、`defaults.temporal`（Item にしか使わず、コレクションの `extent.temporal` は空のまま）、列の説明、Language 拡張、`alternate` のリンク
  - README.md と AGENTS.md は、既にあれば上書きしない。手で書いたものがそのまま残る
  - metadata.yaml を直しただけでは反映されない。`portolan add <ファイル> --force` で作り直す
  - サムネイルは `<ファイル名>.thumb.jpg` で作られ、PTL-VIZ-001 はこれで通る（第1章の `thumbnail.png` でなくてよい）
- 作る順番: `portolan add --force` → `python scripts/finalize_metadata.py` → `portolan check --strict`。
- 変更はすべて PR で確かめる。

## 4. 提供元（providers）

| 役割 | 誰 | 例（交通事故統計） |
|---|---|---|
| `producer` | データを作った組織 | 警察庁 |
| `licensor` | 利用条件を決めている組織 | 警察庁 |
| `processor` | 形式を変えた・加工した人 | shi-works |
| `host` | このカタログを運営している人（最後に1つだけ。URL かメールが必要） | shi-works |

- 作った組織（`producer`）と運営者（`host`）が違うので、Portolan では「ミラー」になる。ミラーには `via` のリンクと `updated` が必須（PTL-PRO-001、003）。shi-works が自分で作ったデータ（`shi-works-*`）は `producer` と `host` が同じになり、「公式」になる。公式のものには `via` を付けない（PTL-PRO-004）。
- 提供元にある URL は、組織のトップではなく、そのデータの公開ページにする。

## 5. 列の説明（`table:columns`）

- 列ごとに `name`、`type`、`description` を書く。名前と型は portolan-cli がファイルから取り出す。説明は人が書く。
- 説明に書くこと:
  - 元の列名（日本語）。例: `元の列名: 年齢（当事者A）`
  - 意味。単位があれば単位
  - コードの列なら、コード表の場所（短ければ説明に、長ければ README の表）
  - 空（null）になる場合
- 英語版の `collection.json` では説明を英語にする。列名は変えない。
- README の列の表と `table:columns` は、同じ元から作る。食い違いを防ぐため。

## 6. キーワード

`keywords` には次の3種類を入れる。英語版には英語で入れる。

| 種類 | 日本語 | 英語 |
|---|---|---|
| テーマ | 下の10個から当てはまるもの | 下の10個から当てはまるもの |
| 地域 | 「日本」と、都道府県・市区町村の名前（全国のデータは「全国」） | `Japan`、都道府県・市区町村の名前（`Tokyo` など） |
| 提供元 | 提供元の名前と略称（警察庁） | 英語名と略称（National Police Agency、NPA） |

テーマの一覧（カタログの構成をテーマにする案（#3）のときに作った一覧を、探すための言葉として使う）:

| 日本語 | 英語 | 入れるもの |
|---|---|---|
| 地形 | terrain | 標高、CS立体図、赤色立体地図、地形分類、河川 |
| 空中写真 | imagery | オルソ画像、空中写真 |
| 建物・3D都市 | buildings | 建物の形、PLATEAU、建物の点群・3D Tiles |
| 交通 | transport | 道路、鉄道、バス、交通事故、交通量、交通規制、シェアサイクル |
| 人口 | population | 人口メッシュ、人口集中地区 |
| 防災 | disaster | 地震、津波、避難場所、自然災害伝承碑 |
| 土地利用・都市計画 | land use | 用途地域、都市計画、土地利用、地価 |
| 境界・住所 | boundaries | 行政区域、住所、役所の位置 |
| 暮らし | livelihood | 食料品へのアクセス、店舗、犯罪 |
| ベースマップ | basemap | 背景地図として使う総合的なタイル |

- 都道府県コード・市区町村コードもキーワードに入れる（[naming.md](naming.md) 第3章）。例: `pref_code=13`。
- ルートの README には、テーマごとの表を載せる。

## 7. 検査

- `portolan check --strict` で、警告も含めてなくす。
- 次の検査は英語を前提にした判定なので、日本語の文書では誤って警告が出る。`--strict` に通すため、書き方で合わせる。
  - PTL-FIL-005（README にライセンスと出典があるか）: README の中に英語の `license` と `source` という語があるかで判定している。日本語の README でも、ライセンスの節に `License: CC-BY-4.0`、出典の節に `Source: 警察庁「交通事故統計情報のオープンデータ」` のように書く。
  - PTL-TTL-002（タイトルが読める文になっているか）: 日本語のタイトルで誤って出たら、中身を見て判断する。
