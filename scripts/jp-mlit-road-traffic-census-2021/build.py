"""道路交通センサス（令和3年度 一般交通量調査 箇所別基本表）の GeoParquet を、
カタログの規則（docs/geoparquet.md）に合わせて作る。

    python scripts/jp-mlit-road-traffic-census-2021/build.py --csv <箇所別基本表 CSV のフォルダ> --tiles <線の GeoJSON タイルのフォルダ>

入力は2つ。どちらも国土交通省の公開データ。

1. 箇所別基本表（都道府県別の CSV、kasyo01.csv 〜 kasyo47.csv。Shift_JIS）
   https://www.mlit.go.jp/road/census/r3/index.html
2. 可視化ツール（WEBマップ）の線の GeoJSON タイル（ズーム12、道路種別ごと、約18,000枚。EPSG:4612）
   https://www.mlit.go.jp/road/ir/ir-data/census_visualizationR3/index.html
   取り方は shiwaku/mlit-road-traffic-census-converter の `python scripts/download_geojson_tiles.py --year r03`
   （箇所別基本表も `python scripts/download_kasho_csv.py --year r03` で取れる）。

1行は1つの交通調査基本区間（箇所別基本表の1行。99,417行）。タイルの線はタイルの境目で切れて
いるので、区間番号（census）ごとにつないでマルチラインにする。可視化ツールに線がない区間は
ジオメトリを空（null）にして残す（docs/geoparquet.md 第4章）。座標系は EPSG:4612（JGD2000）で、
値はそのまま EPSG:4326 として書く（docs/geoparquet.md 第2章）。

CSV の末尾の6列（交通調査基本区間番号〜路線名）は先頭の6列の繰り返しなので使わない
（宮城県の6行は、末尾の路線名が途中で切れている）。

空間の並べ替え（Hilbert）、bbox 列、GeoParquet 1.1、行グループは、このあと
`portolan add` が geoparquet-io で書き直す（docs/geoparquet.md 第2章）。
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import duckdb
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DEFAULT_DST = (
    ROOT / "catalog" / "jp-mlit" / "road-traffic-census-2021" / "jp-mlit-road-traffic-census-2021.parquet"
)
N_SRC_COLUMNS = 153  # 末尾の繰り返しの6列を除いた列の数


def load_columns() -> list[dict]:
    return list(yaml.safe_load((HERE / "columns.yaml").read_text(encoding="utf-8"))["columns"])


def q(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"


def expr(c: dict) -> str:
    if c.get("sql"):
        return c["sql"]
    v = f'NULLIF(trim("{c["src"]}"), \'\')'
    if c.get("pad"):
        return f"lpad({v}, {c['pad']}, '0')"
    if c.get("codes"):
        whens = " ".join(f"WHEN {q(str(k))} THEN {q(l)}" for k, l in c["codes"].items())
        return f"CASE {v} {whens} END"
    if c.get("bool"):
        whens = " ".join(f"WHEN {q(str(k))} THEN {'true' if b else 'false'}" for k, b in c["bool"].items())
        return f"CASE {v} {whens} END"
    if c.get("type"):
        return f"CAST({v} AS {c['type']})"
    return v


def read_csvs(src: Path) -> pd.DataFrame:
    files = sorted(src.glob("kasyo*.csv"))
    if len(files) != 47:
        raise SystemExit(f"{src}: kasyo*.csv が {len(files)} 個（47 個のはず）")
    header = None
    rows = []
    for f in files:
        with f.open(encoding="cp932", newline="") as fh:
            r = csv.reader(fh)
            h = next(r)
            if header is None:
                header = h
            elif h != header:
                raise SystemExit(f"{f}: 見出しがほかの CSV と違う")
            for row in r:
                if not any(x.strip() for x in row):
                    continue  # 空行
                if len(row) != len(header):
                    raise SystemExit(f"{f}: 列の数が {len(row)}（{len(header)} のはず）")
                rows.append(row[:N_SRC_COLUMNS])
    return pd.DataFrame(rows, columns=header[:N_SRC_COLUMNS], dtype="string")


def build(con: duckdb.DuckDBPyConnection, csv_dir: Path, tiles: Path, dst: Path) -> None:
    cols = load_columns()
    df = read_csvs(csv_dir)
    con.register("src_df", df)
    con.execute("CREATE TABLE src AS SELECT * FROM src_df")

    # 表にないコードが残っていないか
    for c in cols:
        if c.get("codes") or c.get("bool"):
            n = con.execute(
                f'SELECT count(*) FROM src WHERE NULLIF(trim("{c["src"]}"), \'\') IS NOT NULL AND ({expr(c)}) IS NULL'
            ).fetchone()[0]
            if n:
                bad = con.execute(f'SELECT DISTINCT "{c["src"]}" FROM src WHERE ({expr(c)}) IS NULL AND trim("{c["src"]}") <> \'\'').fetchall()
                raise SystemExit(f"{c['name']}: コード表にない値が {n} 行（{bad}）")

    # 線: タイルの境目で切れた線を、区間ごとにつなぐ
    con.execute(f"""
        CREATE TABLE lines AS
        WITH f AS (
          SELECT unnest(features) AS ft
          FROM read_json('{tiles.as_posix()}/*.geojson', columns = {{features: 'JSON[]'}}, maximum_object_size = 200000000)
        )
        SELECT ft->>'$.properties.census' AS census,
               ST_Multi(ST_LineMerge(ST_Union_Agg(ST_GeomFromGeoJSON(ft->'$.geometry')))) AS geom,
               count(*) AS pieces
        FROM f GROUP BY 1
    """)
    orphans = con.execute(
        'SELECT count(*) FROM lines WHERE census NOT IN (SELECT "交通調査基本区間番号" FROM src)'
    ).fetchone()[0]
    if orphans:
        raise SystemExit(f"箇所別基本表にない区間の線が {orphans} 本ある")

    exprs = [f"{expr(c)} AS {c['name']}" for c in cols]
    sql = f"""
        SELECT {(','+chr(10)+'  ').join(exprs)},
               l.geom::GEOMETRY AS geometry
        FROM src LEFT JOIN lines l ON l.census = src."交通調査基本区間番号"
        ORDER BY section_id
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"COPY ({sql}) TO '{dst.as_posix()}' (FORMAT parquet, COMPRESSION zstd)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, required=True, help="箇所別基本表 CSV（kasyo01.csv 〜 kasyo47.csv）のフォルダ")
    ap.add_argument("--tiles", type=Path, required=True, help="可視化ツールの GeoJSON タイルのフォルダ")
    ap.add_argument("--dst", type=Path, default=DEFAULT_DST)
    args = ap.parse_args()

    con = duckdb.connect()
    con.execute("INSTALL spatial; LOAD spatial; SET enable_progress_bar = false;")
    build(con, args.csv, args.tiles, args.dst)
    n, keys, nogeom, types, invalid = con.execute(
        f"SELECT count(*), count(DISTINCT section_id), count(*) FILTER (WHERE geometry IS NULL), "
        f"list(DISTINCT ST_GeometryType(geometry)), count(*) FILTER (WHERE NOT ST_IsValid(geometry)) "
        f"FROM read_parquet('{args.dst.as_posix()}')"
    ).fetchone()
    print(f"{args.dst}: {n:,} 行（区間番号 {keys:,} 種類、線なし {nogeom}、不正な形 {invalid}、ジオメトリ {types}）")


if __name__ == "__main__":
    main()
