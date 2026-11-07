# ライセンスと出典の書き方

最終更新: 2026-11-08（#13）

コレクションごとのライセンスと出典を、どこに、どう書くかを決める。根拠は Portolan の仕様（[core.md](https://github.com/portolan-sdi/portolan-spec/blob/main/specs/portolan/core.md) の License と README.md）、rashid の検査（PTL-LIC-001〜003、PTL-FIL-005）、Portolan の参照カタログ（`examples/catalog/portolan-reference`）。

管理者ごとの利用規約は、ここではまとめて調べない。移行（#7、#10）でコレクションを載せるときに、1件ずつ調べて第2章の決め方に当てはめる。

## 1. 書く場所

| 何を | どこに | 決まり |
|---|---|---|
| ライセンス | `collection.json` の `license` | 必須（PTL-LIC-001）。第2章 |
| 利用規約の本文 | `collection.json` の `rel: "license"` のリンク | `license` が `other` なら必須（PTL-LIC-002） |
| 利用条件を決めている組織 | `providers` の `licensor` | [metadata.md](metadata.md) 第4章 |
| 出典の表示 | `collection.json` の `attribution`（STAC の attribution 拡張 v0.1.0） | 第3章 |
| 元データの公開ページ | `rel: "via"` のリンク | ミラーでは必須（PTL-PRO-001） |
| 上のすべての説明 | README の「ライセンスと出典」の節 | 第4章 |

- `license` と `attribution` はコレクションに書く。管理者の `catalog.json` には STAC の `license` の項目がないので書かない。管理者の README に、その管理者の利用規約を1〜2文でまとめる。
- 英語版の `collection.json` でも、`license` と `rel: "license"` のリンクは日本語版と同じにする（[metadata.md](metadata.md) 第2章）。`attribution` は英訳する。

## 2. `license` の決め方

| 提供元の利用条件 | `license` | `rel: "license"` のリンク先 | 例 |
|---|---|---|---|
| SPDX にあるライセンスそのもの | SPDX の識別子 | 付けてよい（提供元のライセンスのページ） | 中野区の点群（`CC-BY-4.0`）、OSM（`ODbL-1.0`） |
| 日本の官公庁の利用規約（政府標準利用規約2.0、公共データ利用規約（PDL1.0）、それに準拠する各機関の規約） | `other` | その機関の利用規約のページ | 警察庁（PDL1.0 に準拠） |
| 提供元から個別に掲載の許可を得たもの | `other` | そのコレクションの README の「ライセンスと出典」の節 | gosenzo-net（城の一覧） |
| 利用条件がわからないもの | 載せない | — | gtfs-gis（作者に確かめるまで保留）、万博の非公式マップ |

- **CC BY 4.0 と互換性がある規約でも、`CC-BY-4.0` とは書かない。** 互換性があっても同じライセンスではなく、第三者の権利や、国が作ったように見せてはいけないことなど、規約ごとの条項がある。誤った識別子を書くより、`other` と規約へのリンクのほうが正確。互換性は README に、規約の条項を挙げて書く（例: PDL1.0 の 1.7.3）。
- リンク先は、PDL1.0 などのひな形ではなく、**その機関が自分のデータに当てはめている規約のページ**にする。機関が条件を足していることがあるため。
- 個別の許可で載せるものは、README に、誰から、いつ、何を許可されたか（掲載だけか、再配布や加工もよいか）を書く。リンク先がその節になるので、節の見出しは変えない。
- 利用条件がわからないものは、作者や提供元に確かめて、答えが出るまで載せない。許可が出たら、上の「個別に掲載の許可を得たもの」として載せる。
- `proprietary` は使わない（PTL-LIC-003）。
- 複数の提供元のデータを組み合わせたもの（`shi-works-*`）:
  - ODbL のデータを含むなら `ODbL-1.0` にする（ODbL は組み合わせたデータベースにも同じライセンスを求める）。
  - それ以外は `other` にし、使ったデータの利用規約を、提供元ごとに `rel: "license"` のリンクで並べる。
  - `providers` に使った提供元をすべて `licensor` として書く。

## 3. 出典の表示（`attribution`）

地図の隅や資料にそのまま載せられる、1行の表示を書く。

- **提供元が書き方を決めていれば、その形に合わせる。** 日本の官公庁の規約は、加工したときの書き方を例で示している（PDL1.0 の 1.1.2: 「「○○動向調査」（D庁）（当該ページのURL）を加工して作成」）。
- **ミラーはすべて「加工して作成」と書く。** shi-works は形式を変えるだけでなく、列名を変えたり、コード値をラベルにしたり、不正な座標を空にしたりするので、元のデータそのままではない。
- `attribution` には URL を入れない（地図の隅では長すぎる）。URL は `rel: "via"` のリンクにあり、README の表示例には URL も入れる。
- 英語版の `attribution` は、日本語の表示を英訳する。資料名は英訳し、引用符でくくる。
- 書く場所は `.portolan/metadata.yaml` の `attribution`（日本語）と [`scripts/i18n/en.yaml`](../scripts/i18n/en.yaml) の `attribution`（英語）。portolan-cli 0.8.0 は `attribution` を扱わないので、[`scripts/finalize_metadata.py`](../scripts/finalize_metadata.py) が `collection.json` に attribution 拡張を宣言して書き込む。英訳がないと止まる。

例（交通事故統計）:

| | `attribution` |
|---|---|
| 日本語 | 「交通事故統計情報のオープンデータ」（警察庁）を加工して作成 |
| 英語 | "Open data of traffic accident statistics" (National Police Agency), modified |

## 4. README の「ライセンスと出典」の節

見出しは日本語版が `## ライセンスと出典`、英語版が `## License and source`。次の順に書く。

1. `License:` で始まる段落。規約の名前（リンク付き）、できること（複製・加工・再配布など）、できないこと、CC BY 4.0 などとの互換性（根拠の条項）
2. `Source:` で始まる段落。元データの名前（公開ページへのリンク付き）、提供元、使った範囲（年次など）、加工したこと
3. 地図や資料に載せるときの表示例。提供元の書き方どおりに URL まで入れたものと、URL を入れにくいときの短い形（`attribution` と同じ）
4. このデータをさらに加工した人も、加工したと書くこと

- `License:` と `Source:` は、日本語の README でも英語のまま書く。rashid の PTL-FIL-005 が README の中の `license` と `source` という語で判定しているため（[metadata.md](metadata.md) 第7章）。
- 英語版の README では、表示例を日本語の原文と英訳の両方で書く。日本の提供元の規約は日本語の表示を前提にしているため。
