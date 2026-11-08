"""令和2年 簡易100mメッシュ人口（GTFS-GIS.jp）の GeoParquet を、カタログの規則（docs/geoparquet.md）に合わせて作る。

    python scripts/gtfs-gis-population-mesh-100m-2020/build.py --src <CSV を展開したフォルダ>

入力は「令和2年簡易100mメッシュ人口データのダウンロード」のページにある、1次メッシュ別の
zip（100m_mesh_pop2020_<1次メッシュ>.zip、151 個。うち 5434 は 404 で、海だけの区画）を
展開した CSV（100m_mesh_pop2020_<1次メッシュ>.csv）。
https://gtfs-gis.jp/teikyo/kani_100m_download2020.html

値は CSV から読む。同じ zip の shape ファイルは、総人口（PopT）が 0.1 人未満のメッシュ
（99,499 件）で値が 100 倍・1,000 倍になっていて、全国の合計が国勢調査と合わないため使わない
（CSV の合計は 126,128,118 人で、国勢調査の 126,146,099 人とほぼ一致する）。
形は mesh_code から計算する（shape ファイルの形と同じ長方形になる）。

座標系は元データが JGD2000（EPSG:4612）で、値はそのまま EPSG:4326 として書く
（緯度経度の差は数 cm 以下。docs/geoparquet.md 第2章）。

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
    ROOT / "catalog" / "gtfs-gis" / "population-mesh-100m-2020" / "gtfs-gis-population-mesh-100m-2020.parquet"
)


def load_columns() -> list[dict]:
    return list(yaml.safe_load((HERE / "columns.yaml").read_text(encoding="utf-8"))["columns"])


# 10桁のメッシュコードの南西の角（度）。
#   1次メッシュ: 緯度 = 上2桁 / 1.5、経度 = 次の2桁 + 100（40分 × 1度）
#   2次メッシュ: 5桁目が緯度、6桁目が経度（5分 × 7分30秒）
#   3次メッシュ: 7桁目が緯度、8桁目が経度（30秒 × 45秒）
#   100mメッシュ: 9桁目が緯度、10桁目が経度（3秒 × 4.5秒）
LAT0 = (
    "(substr(m, 1, 2)::INT / 1.5 + substr(m, 5, 1)::INT * 5 / 60.0"
    " + substr(m, 7, 1)::INT * 30 / 3600.0 + substr(m, 9, 1)::INT * 3 / 3600.0)"
)
LON0 = (
    "(substr(m, 3, 2)::INT + 100 + substr(m, 6, 1)::INT * 7.5 / 60.0"
    " + substr(m, 8, 1)::INT * 45 / 3600.0 + substr(m, 10, 1)::INT * 4.5 / 3600.0)"
)


def select_sql(src: Path) -> str:
    exprs = [f"{c.get('sql') or chr(34) + c['src'] + chr(34)} AS {c['name']}" for c in load_columns()]
    pattern = (src / "100m_mesh_pop2020_*.csv").as_posix()
    return f"""
WITH src AS (
  SELECT *, Meshcode AS m
  FROM read_csv('{pattern}', header = true, types = {{'Meshcode': 'VARCHAR'}})
)
SELECT
  {(','+chr(10)+'  ').join(exprs)},
  ST_MakeEnvelope({LON0}, {LAT0}, {LON0} + 4.5 / 3600.0, {LAT0} + 3 / 3600.0) AS geometry
FROM src
ORDER BY mesh_code
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True, help="CSV を展開したフォルダ")
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
    n, codes, bad, total = con.execute(
        f"SELECT count(*), count(DISTINCT mesh_code), count(*) FILTER (WHERE length(mesh_code) <> 10), "
        f"sum(pop_total) FROM read_parquet('{args.dst.as_posix()}')"
    ).fetchone()
    print(f"{args.dst}: {n:,} 行（コード {codes:,} 種類、10桁でないもの {bad}）、総人口 {total:,.0f}")


if __name__ == "__main__":
    main()
