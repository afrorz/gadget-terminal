#!/usr/bin/env python3
"""代替品ボックスに出す商品サムネイルを、楽天APIから拝借して image: に書き込む。

    python scripts/find_alt_images.py                 # 候補を出力ファイルに書く（確認用）
    python scripts/find_alt_images.py --apply         # 確認後、image: を追記する
    python scripts/find_alt_images.py --apply --skip a.md,b.md   # 誤爆した記事を除外

リンク先と merchant はAmazonのまま触らない。写真は商品そのものを写しているだけで
販売店を示さないので、同じ商品と確認できたものに限って楽天の商品画像を借りる。
Amazon公式の画像API(PA-API)は売上実績が無いと使えないための暫定措置。
書き換えは image: 行の追記だけ（front matter の他の行は再整形しない）。
"""
from __future__ import annotations

import glob
import re
import sys
import time
import urllib.error
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from find_rakuten_alt import (RATE_LIMIT_SEC, clean_keyword, item_image,  # noqa: E402
                              pick_best, search)

ROOT = Path(__file__).resolve().parent.parent


def insert_image(path: Path, url: str, image: str) -> bool:
    """alternatives の中で url が一致する項目の直後に image: を足す。"""
    lines = path.read_text(encoding="utf-8").split("\n")
    for i, ln in enumerate(lines):
        m = re.match(r"^(\s+)url:\s*(\S+)\s*$", ln)
        if not m or m.group(2).strip("\"'") != url:
            continue
        indent = m.group(1)
        j = i + 1
        while j < len(lines) and lines[j].startswith(indent) and not re.match(rf"^{indent}-\s", lines[j]):
            if lines[j].strip().startswith("image:"):
                return False
            j += 1
        lines.insert(j, f'{indent}image: "{image}"')
        path.write_text("\n".join(lines), encoding="utf-8")
        return True
    return False


def main(argv: list[str]) -> int:
    apply = "--apply" in argv
    skip = set()
    if "--skip" in argv:
        skip = set(argv[argv.index("--skip") + 1].split(","))
    site = yaml.safe_load((ROOT / "config" / "site.yaml").read_text(encoding="utf-8"))["site"]
    secrets = yaml.safe_load((ROOT / "config" / "secrets.local.yaml").read_text(encoding="utf-8")) or {}
    app_id = str(site.get("rakuten_app_id") or "").strip()
    key = str(secrets.get("rakuten_access_key") or "").strip()
    if not app_id or not key:
        print("NG rakuten_app_id / rakuten_access_key が空です")
        return 1

    found = 0
    for f in sorted(glob.glob(str(ROOT / "content" / "posts" / "*.md"))):
        p = Path(f)
        m = re.match(r"^---\n(.*?)\n---\n", p.read_text(encoding="utf-8"), re.S)
        if not m:
            continue
        fm = yaml.safe_load(m.group(1)) or {}
        for a in fm.get("alternatives") or []:
            if a.get("image") or not a.get("url"):
                continue
            kw = clean_keyword(str(a["name"]))
            print(f"■ {p.name}\n   name: {a['name']}\n   kw  : {kw}")
            if p.name in skip:
                print("   -> skip指定")
                continue
            time.sleep(RATE_LIMIT_SEC)
            try:
                best = pick_best(search(app_id, key, kw), kw)
            except urllib.error.HTTPError as e:
                print(f"   -> 検索失敗 {e.code}")
                continue
            if not best:
                print("   -> 候補なし")
                continue
            img = item_image(best)
            print(f"   楽天: {best['itemName'][:60]}  {best['itemPrice']}円")
            print(f"   img : {img}")
            if apply and img and insert_image(p, str(a["url"]), img):
                found += 1
                print("   -> 追記")
    print(f"\n追記 {found}件" if apply else "\n確認用の出力です。--apply で書き込みます")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
