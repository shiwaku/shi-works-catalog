"""GeoParquet の行グループを、ジオメトリの大きさで細かく分けて書き直す。

    python scripts/rowgroups.py <file.parquet> [--target-mb 4]

行の並び・列・型・メタデータ（geo）はそのままにして、行グループだけを分け直す。
ジオメトリ（WKB）の合計がおよそ --target-mb を超えたところで次の行グループにする
（docs/geoparquet.md 第2章）。行グループは 122,880 行を超えない。

1行の形が大きいデータ（行政区域など）は、行数で分けると行グループが1つになり、
小さな範囲を表示するだけでもファイル全体を読むことになる。大きさで分けると、
範囲で絞ったときに要らない行グループを読み飛ばせる。

`portolan add` の後に実行し、もう一度 `portolan add --force` する（規則に合った
ファイルは書き直されない）。
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import pyarrow.compute as pc
import pyarrow.parquet as pq

MAX_ROWS = 122_880


def boundaries(sizes: list[int], target: int) -> list[tuple[int, int]]:
    out, start, acc = [], 0, 0
    for i, s in enumerate(sizes):
        if i > start and (acc + s > target or i - start >= MAX_ROWS):
            out.append((start, i))
            start, acc = i, 0
        acc += s
    out.append((start, len(sizes)))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path)
    ap.add_argument("--target-mb", type=float, default=4.0)
    ap.add_argument("--geometry", default="geometry")
    a = ap.parse_args()

    table = pq.read_table(a.path, memory_map=False)  # 置き換えの前にファイルを閉じる（Windows）
    geom = table[a.geometry]
    sizes = pc.fill_null(pc.binary_length(geom), 0).to_pylist()
    groups = boundaries(sizes, int(a.target_mb * 1024 * 1024))

    tmp = a.path.with_suffix(".rg.tmp")
    with pq.ParquetWriter(tmp, table.schema, compression="zstd", compression_level=15,
                         write_statistics=True) as w:
        for s, e in groups:
            w.write_table(table.slice(s, e - s), row_group_size=e - s)
    os.replace(tmp, a.path)

    rows = [e - s for s, e in groups]
    print(f"{a.path.name}: {table.num_rows:,} 行 → 行グループ {len(groups)} 個"
          f"（{min(rows):,}〜{max(rows):,} 行）, {a.path.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
