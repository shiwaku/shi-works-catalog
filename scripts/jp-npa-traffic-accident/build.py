"""交通事故統計（本票）の GeoParquet を、カタログの規則（docs/geoparquet.md）に合わせて作る。

    python scripts/jp-npa-traffic-accident/build.py --src <honhyo_2019-2025.parquet>

入力は npa-traffic-accident-analytics の pipeline/build_parquet.py が作る
honhyo_2019-2025.parquet（警察庁の本票 CSV をラベルに変換し、資料年次を足したもの）。
https://shi-works.com/geoparquet/npa-traffic-accident-analytics/honhyo_2019-2025.parquet と同じ。

ここでは列名・型・ジオメトリだけを整え、ZSTD で書く。空間の並べ替え（Hilbert）、
bbox 列、GeoParquet 1.1、行グループは、このあと `portolan add` が geoparquet-io で
書き直す（portolan-cli の既定。docs/geoparquet.md 第2章）。
"""
from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DEFAULT_DST = ROOT / "catalog" / "jp-npa" / "traffic-accident" / "jp-npa-traffic-accident.parquet"

# 日本の範囲（おおよそ）。この外の座標はジオメトリを空にする（docs/geoparquet.md 第4章）
LON_MIN, LON_MAX = 122.0, 154.0
LAT_MIN, LAT_MAX = 20.0, 46.0

LAT = '"地点_緯度（北緯）_10進数"'
LON = '"地点_経度（東経）_10進数"'


def load_columns() -> list[dict]:
    """columns.yaml を読み、当事者A・B の列を展開した一覧を返す。"""
    spec = yaml.safe_load((HERE / "columns.yaml").read_text(encoding="utf-8"))
    cols = list(spec["columns"])
    for p in ("A", "B"):
        for c in spec["parties"]:
            cols.append({
                "name": f"party_{p.lower()}_{c['name']}",
                "src": c["src"].format(p=p),
                "sql": c["sql"].format(p=p) if "sql" in c else None,
                "ja": c["ja"].format(p=p),
                "en": c["en"].format(p=p),
            })
    return cols


def select_sql(src: Path) -> str:
    exprs = []
    for c in load_columns():
        expr = c.get("sql") or f"NULLIF(\"{c['src']}\", '')"
        exprs.append(f'{expr} AS {c["name"]}')
    geom = (
        f"CASE WHEN {LON}::DOUBLE BETWEEN {LON_MIN} AND {LON_MAX} "
        f"AND {LAT}::DOUBLE BETWEEN {LAT_MIN} AND {LAT_MAX} "
        f"THEN ST_Point({LON}::DOUBLE, {LAT}::DOUBLE) END AS geometry"
    )
    exprs.append(geom)
    body = ",\n  ".join(exprs)
    return f"SELECT\n  {body}\nFROM read_parquet('{src.as_posix()}')"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--dst", type=Path, default=DEFAULT_DST)
    ap.add_argument("--print-sql", action="store_true", help="SQL を表示して終わる")
    args = ap.parse_args()

    sql = select_sql(args.src)
    if args.print_sql:
        print(sql)
        return

    args.dst.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial; SET TimeZone = 'Asia/Tokyo';")
    con.execute(
        f"COPY ({sql}) TO '{args.dst.as_posix()}' "
        "(FORMAT parquet, COMPRESSION zstd, ROW_GROUP_SIZE 100000)"
    )
    n, nulls = con.execute(
        f"SELECT count(*), count(*) FILTER (WHERE geometry IS NULL) FROM read_parquet('{args.dst.as_posix()}')"
    ).fetchone()
    print(f"{args.dst}: {n:,} 行（ジオメトリが空: {nulls:,} 行）")


if __name__ == "__main__":
    main()
