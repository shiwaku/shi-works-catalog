# AGENTS.md — 国土数値情報

国土交通省の国土数値情報のカタログ。使用許諾条件はデータごとに違うので、コレクションの `license` を見ること。

## コレクション

- `admin-boundaries/`: 行政区域（N03）。市区町村（政令指定都市は区）のマルチポリゴン。`admin_code` は全国地方公共団体コード5桁。使う前に [admin-boundaries/AGENTS.md](admin-boundaries/AGENTS.md) の「落とし穴」を読むこと（所属未定地、政令指定都市の区、交通事故統計とはコードで結合できないこと）。
