# AGENTS.md — 国土交通省

国土交通省の道路・交通などのデータのカタログ。国土数値情報は `jp-ksj`、PLATEAU は `jp-plateau` で、ここには入らない。利用条件は国土交通省ウェブサイトの利用ルール（公共データ利用規約第1.0版準拠）で、`license` は `other`。

## コレクション

- `road-traffic-census-2021/`: 道路交通センサス（令和3年度 一般交通量調査 箇所別基本表）。1区間1行のマルチライン。`section_id` で一意。使う前に [road-traffic-census-2021/AGENTS.md](road-traffic-census-2021/AGENTS.md) の「落とし穴」を読むこと（市町村道がほぼないこと、交通量の約3分の1が推定値であること、調査単位区間の値であること）。
