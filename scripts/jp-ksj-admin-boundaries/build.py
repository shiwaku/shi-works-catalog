"""行政区域（国土数値情報 N03）の GeoParquet を、カタログの規則（docs/geoparquet.md）に合わせて作る。

    python scripts/jp-ksj-admin-boundaries/build.py --src <N03-20260101.geojson>

入力は国土数値情報ダウンロードサイトの全国版 N03-20260101_GML.zip に入っている
N03-20260101.geojson（令和8年1月1日時点、125,130 行）。
https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html

元データは島ごとに別の行になっている。全国地方公共団体コード（N03_007）ごとに1行にし、
島の部分を1つのマルチポリゴンにまとめる（形は変えない）。座標系は JGD2011（EPSG:6668）で、
値はそのまま EPSG:4326 として書く（緯度経度の差は数 cm 以下。docs/geoparquet.md 第2章）。

空間の並べ替え（Hilbert）、bbox 列、GeoParquet 1.1、行グループは、このあと
`portolan add` が geoparquet-io で書き直す（docs/geoparquet.md 第2章）。
"""
from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DEFAULT_DST = ROOT / "catalog" / "jp-ksj" / "admin-boundaries" / "jp-ksj-admin-boundaries.parquet"
SRC_COLUMNS = ["N03_001", "N03_002", "N03_003", "N03_004", "N03_005", "N03_007"]


def load_columns() -> list[dict]:
    return list(yaml.safe_load((HERE / "columns.yaml").read_text(encoding="utf-8"))["columns"])


def select_sql(src: Path) -> str:
    exprs = []
    for c in load_columns():
        expr = c.get("sql") or f"NULLIF({c['src']}, '')"
        exprs.append(f"{expr} AS {c['name']}")
    keys = ", ".join(SRC_COLUMNS)
    # ST_Dump で島ごとのポリゴンに分け、コードごとに1つのマルチポリゴンにまとめる。
    # ::GEOMETRY で座標系の指定（EPSG:6668）を外し、GeoParquet の既定（OGC:CRS84）として書く
    return f"""
WITH parts AS (
  SELECT {keys}, unnest(ST_Dump(geom)).geom AS part
  FROM ST_Read('{src.as_posix()}')
),
merged AS (
  SELECT {keys}, ST_Multi(ST_Collect(list(part)))::GEOMETRY AS geometry
  FROM parts
  GROUP BY ALL
)
SELECT
  {(','+chr(10)+'  ').join(exprs)},
  geometry
FROM merged
ORDER BY N03_007
"""


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
    con.execute("INSTALL spatial; LOAD spatial;")
    con.execute(f"COPY ({sql}) TO '{args.dst.as_posix()}' (FORMAT parquet, COMPRESSION zstd)")
    n, codes, types = con.execute(
        f"SELECT count(*), count(DISTINCT admin_code), list(DISTINCT ST_GeometryType(geometry)) "
        f"FROM read_parquet('{args.dst.as_posix()}')"
    ).fetchone()
    print(f"{args.dst}: {n:,} 行（コード {codes:,} 種類、ジオメトリ {types}）")


if __name__ == "__main__":
    main()
