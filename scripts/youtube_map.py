#!/usr/bin/env python3
"""記事ごとの YouTube 横長動画(1製品1本)の一覧 data/youtube.json を作る(2026-11-22 本人「ページに埋め込んでおこうよ」)。

動画は shorts\\gadget-shorts の make_single.py が作って上げ、videos\\single-*\\_uploaded.json に
動画 ID を、out\\single-*_description.txt に記事の URL を残している。その URL で記事と結びつける。
build.py はこの一覧を見て、動画のある記事の終わりに「押したら再生」の枠を出す。
自宅PCの ks_prefetch.py が毎晩呼び、popular.json と一緒に push する(gadget-shorts は GitHub に無いため)。

    python scripts/youtube_map.py            # 書く
    python scripts/youtube_map.py --print    # 書かずに表示だけ
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "youtube.json"
SHORTS = ROOT.parent.parent / "shorts" / "gadget-shorts"
URL_RE = re.compile(r"gadgetterminal\.com/posts/([a-z0-9-]+)\.html")
ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def post_slugs() -> set[str]:
    slugs = set()
    for p in (ROOT / "content" / "posts").glob("*.md"):
        m = re.search(r"^slug:\s*['\"]?([^'\"\n]+)", p.read_text(encoding="utf-8")[:3000], re.M)
        slugs.add(m.group(1).strip() if m else p.stem)
    return slugs


def build() -> dict[str, dict]:
    slugs = post_slugs()
    out: dict[str, dict] = {}
    for rec in sorted(SHORTS.glob("videos/single-*/_uploaded.json")):
        vid = rec.parent.name
        d = json.loads(rec.read_text(encoding="utf-8"))
        if not d.get("public") or not ID_RE.match(str(d.get("videoId") or "")):
            continue
        desc = SHORTS / "out" / f"{vid}_description.txt"
        m = URL_RE.search(desc.read_text(encoding="utf-8")) if desc.exists() else None
        name = m.group(1) if m else vid.removeprefix("single-")
        # 記事の名前に日付が付いている物(2026-11-12-epomaker-...)は、後ろが一致する記事に寄せる
        slug = name if name in slugs else next((s for s in slugs if s.endswith("-" + name)), None)
        if not slug:
            print(f"記事が見つからない: {vid}({name})", file=sys.stderr)
            continue
        out[slug] = {"id": d["videoId"], "title": str(d.get("title") or "")}
    return dict(sorted(out.items()))


def main() -> int:
    if not SHORTS.exists():
        print("gadget-shorts が無いので何もしない", file=sys.stderr)
        return 0
    data = build()
    text = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    if "--print" in sys.argv:
        print(text)
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"youtube.json: {len(data)}件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
