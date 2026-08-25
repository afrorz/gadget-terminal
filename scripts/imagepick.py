#!/usr/bin/env python3
"""製品ページから掲載できる画像URLを集めて、front matter 用の YAML を出す。

    python3 scripts/imagepick.py <ページURL> [--max 6]

やること:
  1. ページを取得する（ブラウザUA。Kickstarter は UA が無いと403を返す）
  2. og:image / JSON-LD / <img> / srcset / data-src から候補を集める
  3. 1件ずつ実際に取得して、画像として返るものだけ残す
  4. ロゴ・アイコン・アバター・極小サイズを落とす

**出力されたURLは権利者のサーバー上のものである。**
ダウンロードして public/ に置いてはいけない。URLをそのまま front matter に書く。
"""
from __future__ import annotations

import argparse
import html as _html
import json
import re
import sys
import urllib.parse
import urllib.request

if sys.platform == "win32":  # Windows のコンソールは既定 cp932
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# ロゴ・UI部品・SNSアイコンなど、製品写真ではないもの
JUNK = re.compile(r"(logo|icon|favicon|sprite|avatar|placeholder|badge|banner|"
                  r"spinner|loading|blank|pixel|1x1|share|social|footer|header|"
                  r"payment|visa|mastercard|paypal|amex|thumb_|_thumb|-thumb|menu|nav|cart|collection|swatch)", re.I)
SIZE_SUFFIX = re.compile(r"[-_](\d{2,4})x(\d{2,4})(?=\.\w+$|$)")


def fetch(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ja,en;q=0.8",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def candidates(page_url: str, html_text: str) -> list[str]:
    """HTML から画像URLらしきものを、優先度の高い順に集める。"""
    out: list[str] = []

    def add(u: str) -> None:
        u = _html.unescape((u or "").strip())
        if not u or u.startswith("data:"):
            return
        u = urllib.parse.urljoin(page_url, u)
        if u.split("?")[0].lower().endswith(".svg"):
            return
        if u not in out:
            out.append(u)

    # 1. og:image / twitter:image。ページが「代表画像」として自ら指定したもの
    for m in re.finditer(r'<meta[^>]+>', html_text, re.I):
        tag = m.group(0)
        if re.search(r'(og:image|twitter:image)(:url)?["\']', tag, re.I):
            c = re.search(r'content=["\']([^"\']+)', tag, re.I)
            if c:
                add(c.group(1))

    # 2. JSON-LD の image
    for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>',
                         html_text, re.S | re.I):
        try:
            data = json.loads(m.group(1).strip())
        except Exception:
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                img = node.get("image")
                if isinstance(img, str):
                    add(img)
                elif isinstance(img, list):
                    for x in img:
                        add(x if isinstance(x, str) else (x or {}).get("url", ""))
                elif isinstance(img, dict):
                    add(img.get("url", ""))
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)

    # 3. クラファン系の埋め込み JSON（Indiegogo / Kickstarter）
    for key in ("window.__INITIAL_STATE__", "window.current_project"):
        i = html_text.find(key)
        if i < 0:
            continue
        j = html_text.find("{", i)
        if j < 0:
            continue
        try:
            obj, _ = json.JSONDecoder().raw_decode(html_text[j:])
        except Exception:
            continue
        blob = json.dumps(obj)
        for u in re.findall(r'https?://[^"\\ ]+?\.(?:jpg|jpeg|png|webp)', blob):
            add(u)

    # 4. 本文中の <img>。srcset があれば一番大きいものを採る
    for m in re.finditer(r'<img\b[^>]*>', html_text, re.I):
        tag = m.group(0)
        ss = re.search(r'srcset=["\']([^"\']+)', tag, re.I)
        if ss:
            best, best_w = "", -1
            for part in ss.group(1).split(","):
                bits = part.strip().split()
                if not bits:
                    continue
                w = int(re.sub(r"\D", "", bits[-1]) or 0) if len(bits) > 1 else 0
                if w >= best_w:
                    best, best_w = bits[0], w
            add(best)
        for attr in ("data-src", "data-original", "data-lazy-src", "src"):
            a = re.search(attr + r'=["\']([^"\']+)', tag, re.I)
            if a:
                add(a.group(1))
                break
    return out


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def looks_like_product(url: str, match: str = "") -> bool:
    path = urllib.parse.urlparse(url).path
    if JUNK.search(path):
        return False
    # --match が指定されたら、製品名を含むファイル名だけ残す。
    # ショップのページは他製品のナビ画像を大量に含むため、これが無いと
    # 「別の製品の写真」を載せてしまう。
    if match and not all(t in norm(path) for t in match):
        return False
    m = SIZE_SUFFIX.search(path)
    if m and (int(m.group(1)) < 400 or int(m.group(2)) < 300):
        return False   # サムネイル版。原寸が別にあるはず
    return True


def verify(url: str) -> tuple[bool, str]:
    """実際に取得して、画像として返るか確かめる。"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=25) as r:
            ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip()
            body = r.read(400_000)
    except Exception as e:
        return False, f"取得失敗 {type(e).__name__}"
    if not ctype.startswith("image/"):
        return False, f"画像ではない ({ctype or '不明'})"
    if len(body) < 12_000:
        return False, f"小さすぎる ({len(body)}B)"
    return True, f"{ctype} {len(body) // 1024}KB"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--max", type=int, default=6, help="採用する最大枚数")
    ap.add_argument("--all", action="store_true", help="落とした候補も表示する")
    ap.add_argument("--match", default="",
                    help="製品名。URLにこの語を含む画像だけ残す（例 v6-ultra-hybrid）")
    a = ap.parse_args()

    try:
        raw = fetch(a.url)
    except Exception as e:
        print(f"ページを取得できません: {e}")
        return 1
    text = raw.decode("utf-8", "replace")

    cands = candidates(a.url, text)
    print(f"候補 {len(cands)}件 → 検証します\n")

    match = [norm(t) for t in re.split(r"[\s,/_-]+", a.match) if norm(t)]
    if match:
        print(f"  （{a.match} を名前に含む画像だけ残します）")
    good: list[str] = []
    seen_asset: set[str] = set()
    for u in cands:
        if len(good) >= a.max:
            break
        if not looks_like_product(u, match):
            if a.all:
                print(f"  skip  {u[:88]}")
            continue
        # 同じ画像のサイズ違いは1枚だけ採る。パスが同じなら同一素材とみなす。
        asset = urllib.parse.urlparse(u).path
        if asset in seen_asset:
            continue
        seen_asset.add(asset)
        ok, why = verify(u)
        print(f"  {'OK  ' if ok else 'NG  '}{why:<24} {u[:88]}")
        if ok:
            good.append(u)

    if not good:
        print("\n掲載できる画像が見つかりませんでした。別の公式ページを当たってください。")
        return 2

    print("\n--- front matter に貼る ---")
    print("images:")
    for u in good:
        print(f'  - url: "{u}"')
        print(f'    caption: ""')
    print(f'credit: <メーカー名> 公式製品ページ')
    print()
    print("※ 貼る前に必ず1枚ずつ開いて確認すること。"
          "ショップのページは他製品のナビ画像を含むため、"
          "取得できた＝その製品の写真とは限らない。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
