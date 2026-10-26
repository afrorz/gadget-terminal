#!/usr/bin/env python3
"""全記事の写真が今も表示できるかを点検し、消えた写真の一覧を Markdown で出す。

    python scripts/dead_images.py                    # 一覧を画面に出す
    python scripts/dead_images.py --out report.md    # ファイルにも書く

週に1回の自動点検(.github/workflows/image-check.yml)が使う。作り手が写真を消したり
名前を変えたりすると、記事の一番上の写真が出なくなる(2026-10-27 Figurobot・PELADN WO5 で発覚)。

checkimages.py は公開前の門番で、x_hook の有無なども見る。こちらは写真だけを見て、
次の2つを分けて報告する。
- 消えた: 404/410、または写真の代わりに別のページ(HTML)が返ってきたもの
- 確かめられなかった: 403・429・500番台・時間切れなど。GitHub のサーバーからのアクセスを
  止めているサイトもあるので、消えたとは限らない
Content-Type が application/octet-stream でも、中身が画像なら表示できるので「生きている」とみなす。

終了コードは常に 0(点検の結果で自動処理を失敗にしない)。件数は最後の行に出す。
"""
from __future__ import annotations

import argparse
import glob
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import yaml

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
SITE = "https://gadgetterminal.com/posts/"


def front_matter(path: str) -> dict:
    t = open(path, encoding="utf-8").read()
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", t, re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def looks_like_image(head: bytes) -> bool:
    return (head[:3] == b"\xff\xd8\xff" or head[:8] == b"\x89PNG\r\n\x1a\n"
            or head[:6] in (b"GIF87a", b"GIF89a")
            or (head[:4] == b"RIFF" and head[8:12] == b"WEBP")
            or head[4:12] in (b"ftypavif", b"ftypheic", b"ftypmif1"))


def check(url: str) -> tuple[str, str]:
    """('ok'|'dead'|'unknown', 理由)"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "image/*,*/*"})
        with urllib.request.urlopen(req, timeout=25) as r:
            ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            head = r.read(4096)
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return "dead", f"見つからない(HTTP {e.code})"
        return "unknown", f"HTTP {e.code}"
    except Exception as e:  # 時間切れ・接続できない
        return "unknown", type(e).__name__
    if ctype.startswith("image/") or looks_like_image(head):
        return "ok", ctype
    if ctype == "text/html":
        return "dead", "写真ではなくページが返ってきた"
    return "unknown", f"形式が不明({ctype or '不明'})"


def collect() -> list[dict]:
    items = []
    for f in sorted(glob.glob("content/posts/*.md")):
        fm = front_matter(f)
        slug = fm.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", f.split("/")[-1].split("\\")[-1][:-3])
        title = str(fm.get("seo_title") or fm.get("title") or slug)
        imgs = []
        for it in (fm.get("images") or []):
            u = it if isinstance(it, str) else (it or {}).get("url")
            if u:
                imgs.append(str(u).strip())
        if not imgs and fm.get("thumbnail"):
            imgs.append(str(fm["thumbnail"]).strip())
        for i, u in enumerate(imgs):
            items.append({"slug": slug, "title": title, "where": "一番上の写真" if i == 0 else f"写真{i + 1}枚目", "url": u})
        for key, label in (("alternatives", "代わりの製品"), ("gear", "一緒に使えるもの")):
            for x in (fm.get(key) or []):
                if isinstance(x, dict) and x.get("image"):
                    items.append({"slug": slug, "title": title, "where": f"{label}「{x.get('name', '')}」の写真",
                                  "url": str(x["image"]).strip()})
    return items


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    items = collect()
    # 同じ URL は1回だけ見る。サイトに負担をかけないよう同時に8本まで
    uniq = sorted({it["url"] for it in items})
    with ThreadPoolExecutor(max_workers=8) as ex:
        res = dict(zip(uniq, ex.map(check, uniq)))
    dead = [dict(it, why=res[it["url"]][1]) for it in items if res[it["url"]][0] == "dead"]
    unknown = [dict(it, why=res[it["url"]][1]) for it in items if res[it["url"]][0] == "unknown"]

    lines = [f"点検した写真: {len(uniq)}枚(記事 {len({it['slug'] for it in items})}本)", ""]
    if dead:
        lines += ["## 消えた写真", "", "作り手が写真を消したか、名前を変えた可能性が高い。今の公式ページの写真に差し替える。", ""]
        for it in dead:
            lines.append(f"- [ ] [{it['title']}]({SITE}{it['slug']}.html) — {it['where']}: {it['why']}  \n  `{it['url']}`")
        lines.append("")
    if unknown:
        lines += ["## 確かめられなかった写真(消えたとは限らない)", ""]
        for it in unknown:
            lines.append(f"- [{it['title']}]({SITE}{it['slug']}.html) — {it['where']}: {it['why']}")
        lines.append("")
    if not dead and not unknown:
        lines.append("すべての写真が表示できました。")
    lines.append(f"DEAD={len(dead)} UNKNOWN={len(unknown)}")
    text = "\n".join(lines)
    print(text)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
