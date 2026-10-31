# shi-works-catalog

[shi-works.com](https://shi-works.com/) で配信している地理空間データを、[Portolan](https://github.com/portolan-sdi) の仕様に沿った STAC カタログとして整備するためのリポジトリ。

- カタログの公開先（予定）: `https://shi-works.com/catalog/catalog.json`
- データの置き場所: Cloudflare R2 バケット `shi-works` の `catalog/` 以下
- 要件定義: [docs/requirements.md](docs/requirements.md)

## 注意

- 公開リポジトリ。R2 の認証情報、`.env`、Cloudflare のアカウントID、非公開バケットの情報は**コミットしない**。
- R2 への書き込みは、手元の AWS プロファイルを使う（名前だけ書き、値は書かない）。
