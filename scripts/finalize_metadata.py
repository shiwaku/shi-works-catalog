"""portolan-cli が作った STAC に、portolan-cli では書けない項目を足し、英語版の木を作る。

    python scripts/finalize_metadata.py

`portolan add` のあとに実行する（docs/metadata.md 第3章）。何度実行しても同じ結果になる。

日本語の木（catalog/）に足すもの:
  - 列の説明（table:columns の description）: scripts/<コレクション>/columns.yaml から
  - キーワードと期間（keywords、extent.temporal）: 各コレクションの .portolan/metadata.yaml から
    （portolan-cli 0.8.0 は README にしか使わず、collection.json に書かないため）
  - 出典の表示（attribution）と STAC の attribution 拡張: 同じく .portolan/metadata.yaml から
    （portolan-cli 0.8.0 は attribution を扱わないため。docs/license.md 第3章）
  - STAC の Language 拡張と、英語版への alternate リンク
  - README の列の表（<!-- columns:start --> と <!-- columns:end --> の間）と、README のアセットの大きさ・チェックサム

英語版の木（catalog/en/）:
  - STAC ファイルを日本語版から作り、scripts/i18n/en.yaml の文言に置き換える
  - データのアセットは日本語の木のファイルを相対パスで指す
  - AGENTS.md は日本語のものを写す（hreflang: ja）。README.md は en/ に手で書いたものを使う
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import shutil
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CAT = ROOT / "catalog"
EN = CAT / "en"
SCRIPTS = ROOT / "scripts"

LANG_EXT = "https://stac-extensions.github.io/language/v1.0.0/schema.json"
ATTR_EXT = "https://stac-extensions.github.io/attribution/v0.1.0/schema.json"
LANG = {
    "ja": {"code": "ja", "name": "日本語", "alternate": "Japanese"},
    "en": {"code": "en", "name": "English"},
}
JST = timezone(timedelta(hours=9))

# どの表にも出る、GeoParquet が足す列の説明
EXTRA_COLUMNS = {
    "bbox": {
        "ja": "地物の範囲（xmin、ymin、xmax、ymax）。GeoParquet 1.1 の bbox 列で、範囲で絞るときに行グループを読み飛ばすのに使う。",
        "en": "Feature bounding box (xmin, ymin, xmax, ymax). The GeoParquet 1.1 bbox covering column, used to skip row groups in spatial filters.",
    },
    "geometry": {
        "ja": "事故の発生地点（点、EPSG:4326）。座標が日本の外か (0, 0) だった行は空。",
        "en": "Accident location (point, EPSG:4326). Null where the source coordinates were (0, 0) or outside Japan.",
    },
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # LF で書く。Windows の既定の CRLF だと、git の LF 固定（.gitattributes）と
    # README のチェックサムが食い違う
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def rel(target: Path, start_dir: Path) -> str:
    r = os.path.relpath(target, start_dir).replace(os.sep, "/")
    return r if r.startswith(".") else f"./{r}"


def multihash_sha256(path: Path) -> str:
    return "1220" + hashlib.sha256(path.read_bytes()).hexdigest()


def stac_paths() -> list[Path]:
    """日本語の木の catalog.json と collection.json（catalog/ からの相対パス）。"""
    out = []
    for p in sorted(CAT.rglob("*.json")):
        r = p.relative_to(CAT)
        if r.parts[0] == "en" or ".portolan" in r.parts:
            continue
        if p.name in ("catalog.json", "collection.json"):
            out.append(r)
    return out


def load_columns(collection_id: str) -> list[dict] | None:
    """scripts/<管理者>-<コレクション>/build.py の load_columns() を使う。"""
    build = SCRIPTS / collection_id.replace("/", "-") / "build.py"
    if not build.exists():
        return None
    spec = importlib.util.spec_from_file_location(f"build_{build.parent.name}", build)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.load_columns()


def column_descriptions(collection_id: str) -> dict[str, dict[str, str]]:
    cols = load_columns(collection_id)
    if cols is None:
        return {}
    out = {}
    for c in cols:
        ja = c["ja"]
        en = c["en"]
        if c.get("src"):
            ja = f"元の列名: {c['src']}。{ja}"
            en = f"Original column: {c['src']}. {en}"
        else:
            ja = f"元データにない、足した列。{ja}"
            en = f"Added column (not in the source). {en}"
        out[c["name"]] = {"ja": ja, "en": en}
    out.update(EXTRA_COLUMNS)
    return out


def temporal_interval(meta: dict) -> list | None:
    t = (meta.get("defaults") or {}).get("temporal") or {}
    if "start" not in t or "end" not in t:
        return None
    start = datetime.combine(date.fromisoformat(str(t["start"])), time.min, JST)
    end = datetime.combine(date.fromisoformat(str(t["end"])), time(23, 59, 59), JST)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    return [start.astimezone(timezone.utc).strftime(fmt), end.astimezone(timezone.utc).strftime(fmt)]


def set_link(links: list[dict], rel_name: str, href: str, **extra) -> None:
    links[:] = [l for l in links if l.get("rel") != rel_name]
    links.append({"rel": rel_name, "href": href, "type": extra.pop("type", "application/json"), **extra})


def add_extension(doc: dict, ext: str) -> None:
    exts = doc.setdefault("stac_extensions", [])
    if ext not in exts:
        exts.append(ext)


def add_language(doc: dict, lang: str) -> None:
    add_extension(doc, LANG_EXT)
    doc["language"] = LANG[lang]
    doc["languages"] = [LANG[l] for l in LANG if l != lang]


def fill_readme_columns(readme: Path, doc: dict, descs: dict, lang: str) -> None:
    if not readme.exists() or not descs:
        return
    text = readme.read_text(encoding="utf-8")
    start, end = "<!-- columns:start -->", "<!-- columns:end -->"
    if start not in text or end not in text:
        return
    head = "| 列 | 型 | 説明 |" if lang == "ja" else "| Column | Type | Description |"
    rows = [head, "|---|---|---|"]
    for c in doc.get("table:columns", []):
        if c["name"] in ("bbox", "geometry"):
            continue
        d = descs.get(c["name"], {}).get(lang, "").replace("|", "\\|")
        rows.append(f"| `{c['name']}` | {c['type']} | {d} |")
    table = "\n".join(rows)
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    readme.write_text(f"{before}{start}\n{table}\n{end}{after}", encoding="utf-8", newline="\n")


def refresh_doc_asset(doc: dict, directory: Path) -> None:
    asset = (doc.get("assets") or {}).get("documentation")
    readme = directory / "README.md"
    if asset and readme.exists():
        asset["href"] = "./README.md"
        asset["file:size"] = readme.stat().st_size
        asset["file:checksum"] = multihash_sha256(readme)


def finalize(r: Path, en_text: dict) -> None:
    ja_path = CAT / r
    en_path = EN / r
    ja_dir, en_dir = ja_path.parent, en_path.parent
    doc = read_json(ja_path)
    is_collection = doc.get("type") == "Collection"
    descs = column_descriptions(doc["id"]) if is_collection else {}

    # --- 日本語版 ---
    meta_file = ja_dir / ".portolan" / "metadata.yaml"
    meta = yaml.safe_load(meta_file.read_text(encoding="utf-8")) if meta_file.exists() else {}
    meta = meta or {}
    if is_collection:
        if meta.get("keywords"):
            doc["keywords"] = list(meta["keywords"])
        if meta.get("attribution"):
            add_extension(doc, ATTR_EXT)
            doc["attribution"] = meta["attribution"]
        interval = temporal_interval(meta)
        if interval:
            doc.setdefault("extent", {})["temporal"] = {"interval": [interval]}
        for c in doc.get("table:columns", []):
            if c["name"] in descs:
                c["description"] = descs[c["name"]]["ja"]
    add_language(doc, "ja")
    set_link(doc["links"], "alternate", rel(en_path, ja_dir), hreflang="en", title="English")
    fill_readme_columns(ja_dir / "README.md", doc, descs, "ja")
    refresh_doc_asset(doc, ja_dir)
    write_json(ja_path, doc)

    # --- 英語版 ---
    en_doc = copy.deepcopy(doc)
    t = en_text.get(r.as_posix(), {})
    for key in ("title", "description", "keywords", "attribution"):
        if key in t:
            en_doc[key] = t[key]
    for p in en_doc.get("providers", []):
        p["name"] = t.get("providers", {}).get(p["name"], p["name"])
    if "attribution" in en_doc and "attribution" not in t:
        raise SystemExit(f"{r.as_posix()}: scripts/i18n/en.yaml に attribution の英訳がない")
    if is_collection:
        for c in en_doc.get("table:columns", []):
            if c["name"] in descs:
                c["description"] = descs[c["name"]]["en"]
    add_language(en_doc, "en")
    set_link(en_doc["links"], "alternate", rel(ja_path, en_dir), hreflang="ja", title="日本語")
    for link in en_doc["links"]:
        if link.get("rel") == "agents":
            link["hreflang"] = "ja"
    for key, asset in (en_doc.get("assets") or {}).items():
        if key == "documentation":
            continue
        href = asset.get("href", "")
        if href.startswith("./") or not href.startswith(("http://", "https://", "/")):
            asset["href"] = rel(ja_dir / href, en_dir)

    en_dir.mkdir(parents=True, exist_ok=True)
    if (ja_dir / "AGENTS.md").exists():
        shutil.copyfile(ja_dir / "AGENTS.md", en_dir / "AGENTS.md")
    fill_readme_columns(en_dir / "README.md", en_doc, descs, "en")
    refresh_doc_asset(en_doc, en_dir)
    write_json(en_path, en_doc)
    print(f"{r.as_posix()} → en/{r.as_posix()}")


def main() -> None:
    en_text = yaml.safe_load((SCRIPTS / "i18n" / "en.yaml").read_text(encoding="utf-8"))
    for r in stac_paths():
        finalize(r, en_text)


if __name__ == "__main__":
    main()
