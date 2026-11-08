"""人口集中地区（令和2年国勢調査）の GeoParquet を、カタログの規則（docs/geoparquet.md）に合わせて作る。

    python scripts/jp-stat-densely-inhabited-districts-2020/build.py --src <shape ファイルを展開したフォルダ>

入力は e-Stat の境界データダウンロードにある「国勢調査 2020年 人口集中地区」の
都道府県別の shape ファイル（世界測地系緯度経度・Shapefile、R2_did_<都道府県コード>.shp、47 個）。
https://www.e-stat.go.jp/gis/statmap-search?page=1&type=2&aggregateUnitForBoundary=D&toukeiCode=00200521&toukeiYear=2020&serveyId=D002005112020&datum=2011

1行は1つの人口集中地区（市区町村ごとに設定される。元データのまま、1,463行）。
不正な形（5行）は ST_MakeValid で直し、すべてマルチポリゴンにそろえる。座標系は JGD2011
（EPSG:6668）で、値はそのまま EPSG:4326 として書く（docs/geoparquet.md 第2章）。

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
DEFAULT_DST = (
    ROOT / "catalog" / "jp-stat" / "densely-inhabited-districts-2020" / "jp-stat-densely-inhabited-districts-2020.parquet"
)


def load_columns() -> list[dict]:
    return list(yaml.safe_load((HERE / "columns.yaml").read_text(encoding="utf-8"))["columns"])


def select_sql(src: Path) -> str:
    shps = sorted(src.glob("R2_did_*.shp"))
    if len(shps) != 47:
        raise SystemExit(f"{src}: R2_did_*.shp が {len(shps)} 個（47 個のはず）")
    union = "\n  UNION ALL ".join(f"SELECT * FROM ST_Read('{p.as_posix()}')" for p in shps)
    exprs = [f"{c.get('sql') or chr(34) + c['src'] + chr(34)} AS {c['name']}" for c in load_columns()]
    # ::GEOMETRY で座標系の指定（EPSG:6668）を外し、GeoParquet の既定（OGC:CRS84）として書く
    return f"""
WITH src AS (
  {union}
)
SELECT
  {(','+chr(10)+'  ').join(exprs)},
  ST_Multi(ST_MakeValid(geom))::GEOMETRY AS geometry
FROM src
ORDER BY admin_code, did_number
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True, help="shape ファイルを展開したフォルダ")
    ap.add_argument("--dst", type=Path, default=DEFAULT_DST)
    ap.add_argument("--print-sql", action="store_true", help="SQL を表示して終わる")
    args = ap.parse_args()

    sql = select_sql(args.src)
    if args.print_sql:
        print(sql)
        return

    args.dst.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial; SET enable_progress_bar = false;")
    con.execute(f"COPY ({sql}) TO '{args.dst.as_posix()}' (FORMAT parquet, COMPRESSION zstd)")
    n, keys, invalid, types, pop = con.execute(
        f"SELECT count(*), count(DISTINCT (admin_code, did_number)), count(*) FILTER (WHERE NOT ST_IsValid(geometry)), "
        f"list(DISTINCT ST_GeometryType(geometry)), sum(population) FROM read_parquet('{args.dst.as_posix()}')"
    ).fetchone()
    print(f"{args.dst}: {n:,} 行（キー {keys:,} 種類、不正な形 {invalid}、ジオメトリ {types}）、人口 {pop:,}")


if __name__ == "__main__":
    main()
