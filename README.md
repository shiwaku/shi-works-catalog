# shi-works-catalog

[shi-works.com](https://shi-works.com/) で配信している地理空間データを、[Portolan](https://github.com/portolan-sdi) の仕様に沿った STAC カタログとして整備するためのリポジトリ。

- カタログの公開先（予定）: `https://catalog.shi-works.com/catalog.json`
- データの置き場所: Cloudflare R2 の専用バケット `shi-works-catalog`（既存データは `shi-works` バケット、`https://shi-works.com/` のまま）
- 手元のカタログ: [catalog/](catalog/)
- 要件定義: [docs/requirements.md](docs/requirements.md)

## 注意

- 公開リポジトリ。R2 の認証情報、`.env`、Cloudflare のアカウントID、非公開バケットの情報は**コミットしない**。
- R2 への書き込みは、手元の AWS プロファイルを使う（名前だけ書き、値は書かない）。
