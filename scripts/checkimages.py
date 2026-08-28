#!/usr/bin/env python3
"""記事に製品画像があり、その画像が実際に表示できるかを確かめる。

    python3 scripts/checkimages.py                      # 全記事
    python3 scripts/checkimages.py content/posts/2026-08-25-*.md

画像が1枚も無い記事、またはURLが死んでいる画像があれば終了コード1で落ちる。
公開前の門番なので、ここを通らない記事はコミットしない。
"""
from __future__ import annotations

import glob
import re
import sys
import urllib.request
from pathlib import Path

import yaml

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def image_urls(meta: dict) -> list[str]:
    urls = []
    for it in (meta.get("images") or []):
        it = {"url": it} if isinstance(it, str) else (it or {})
        u = str(it.get("url") or "").strip()
        if u:
            urls.append(u)
    if not urls and meta.get("thumbnail"):
        urls.append(str(meta["thumbnail"]).strip())
    return urls


def alive(url: str) -> tuple[bool, str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=25) as r:
            ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip()
            size = len(r.read(200_000))
    except Exception as e:
        return False, f"取得できない ({type(e).__name__})"
    if not ctype.startswith("image/"):
        return False, f"画像ではない ({ctype or '不明'})"
    if size < 8_000:
        return False, f"小さすぎる ({size}B)"
    return True, f"{ctype} {size // 1024}KB"


def main(argv: list[str]) -> int:
    pats = argv[1:] or ["content/posts/*.md"]
    files = sorted({f for pat in pats for f in glob.glob(pat)})
    if not files:
        print("対象の記事がありません:", " ".join(pats))
        return 1

    bad_none, bad_dead, weak, bad_hook, ok_shots = [], [], [], [], 0
    for f in files:
        text = Path(f).read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not m:
            continue
        meta = yaml.safe_load(m.group(1)) or {}
        name = Path(f).name
        # x_hook は X 投稿の一言目。無いと seo_title が代用されて平坦な文になる。
        # 指示に書いてあっても書き忘れるので、ここで止める。
        if not str(meta.get("x_hook") or "").strip():
            bad_hook.append(name)
            print(f"NG  {name}: x_hook がありません")
        urls = image_urls(meta)
        yt = [e for e in (meta.get("embeds") or [])
              if (e.get("type") or "").lower() == "youtube" and e.get("id")]
        if not urls:
            if yt:
                # 動画のサムネイルは YouTube が配信しているので必ず表示される。
                # 表示は保証されるが、静止画のほうが情報量は多い。
                weak.append(name)
                print(f"△  {name}: 製品画像なし。YouTube のサムネイルで代用中")
                continue
            bad_none.append(name)
            print(f"NG  {name}: 製品画像も動画もありません")
            continue
        for u in urls:
            ok, why = alive(u)
            if ok:
                ok_shots += 1
            else:
                bad_dead.append((name, u, why))
                print(f"NG  {name}: {why}\n      {u}")
        if not any(n == name for n, _, _ in bad_dead):
            print(f"OK  {name}: {len(urls)}枚")

    print(f"\n記事 {len(files)}本 / 生きている画像 {ok_shots}枚 "
          f"/ 動画のみ {len(weak)}本 / 画像なし {len(bad_none)}本 "
          f"/ 表示できない画像 {len(bad_dead)}枚 / x_hook なし {len(bad_hook)}本")
    if bad_none or bad_dead or bad_hook:
        print("\n公開できません。7-2 に戻って画像を用意するか、その記事を削除してください。")
        return 1
    print("すべての記事に表示できる製品画像があります。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
