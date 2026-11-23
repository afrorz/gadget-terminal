#!/usr/bin/env python3
"""写真に元から入っている白い余白を測り、front matter の images に書く crop の値を出す(2026-11-22 本人「余白少なくしたい」)。

画像は自社のサーバーに置けない(CLAUDE.md)ので、切り抜いた画像は作らない。メモリ上で一度読んで
白以外が写っている範囲を測るだけ。build.py はこの値を見て、表示のときに CSS でその範囲だけを見せる。

    python scripts/img_trim.py <画像URL> [<画像URL> ...]          # 測って表示だけ
    python scripts/img_trim.py --save <画像URL> [<画像URL> ...]   # data/img_crop.json に書く
    python scripts/img_trim.py --heroes                          # まだ測っていない記事の最初の写真をまとめて測る(毎晩 ks_prefetch.py が呼ぶ)

img_crop.json の値が null の写真は「測った・切らない」。自動で測った範囲が製品を欠いてしまう写真は、
手で null にしておくと次から切られない(2026-11-23 に2枚そうした)。

値は [左, 上, 右, 下, 幅, 高さ](元画像のピクセル)。URL ごとに持つので、見出しの写真・本文の写真・
一覧表の小さな写真のどこに出しても同じように切られる。余白が3%未満なら「切る必要なし」と出す。
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path
import urllib.request

from PIL import Image, ImageChops

PAD = 0.015      # 切りすぎて影や縁が欠けないよう、見つけた範囲の外に残す幅(画像の長い辺に対する割合)
MIN_GAIN = 0.03  # これ未満しか減らないなら切らない
THRESH = 18      # 白(背景色)との差がこれ以下なら余白とみなす
NOISE = 0.004    # 1列(1行)のうち、これ未満の割合しか色が無ければ余白とみなす(端の細い線・ゴミを無視する)
OUT = Path(__file__).resolve().parent.parent / "data" / "img_crop.json"


def measure(url: str) -> tuple[list[int], tuple[int, int]] | None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=30).read()
    im = Image.open(io.BytesIO(raw))
    im = im.convert("RGBA")
    w, h = im.size
    # 透明部分は白として扱う
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    rgb = Image.alpha_composite(bg, im).convert("RGB")
    # 背景は四隅の色(白に近いとは限らない。薄い色の背景もある)
    corner = rgb.getpixel((1, 1))
    diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, corner)).convert("L")
    mask = diff.point(lambda v: 1 if v > THRESH else 0)
    px = mask.load()
    cols = [sum(px[x, y] for y in range(0, h, 2)) for x in range(w)]
    rows = [sum(px[x, y] for x in range(0, w, 2)) for y in range(h)]
    xs = [x for x, n in enumerate(cols) if n > NOISE * h / 2]
    ys = [y for y, n in enumerate(rows) if n > NOISE * w / 2]
    if not xs or not ys:
        return None
    box = (xs[0], ys[0], xs[-1] + 1, ys[-1] + 1)
    pad = int(max(w, h) * PAD)
    l, t, r, b = max(0, box[0] - pad), max(0, box[1] - pad), min(w, box[2] + pad), min(h, box[3] + pad)
    if (r - l) / w > 1 - MIN_GAIN and (b - t) / h > 1 - MIN_GAIN:
        return None
    return [l, t, r, b, w, h], corner


def first_image(text: str) -> str:
    """記事の front matter から最初の写真の URL を取る(build.py と同じく images の1枚目、無ければ thumbnail)。"""
    import yaml
    try:
        fm = yaml.safe_load(text.split("---")[1]) or {}
    except Exception:  # noqa: BLE001
        return ""
    imgs = fm.get("images") or []
    first = imgs[0] if imgs else fm.get("thumbnail")
    if isinstance(first, dict):
        first = first.get("url")
    return str(first or "").strip()


def heroes() -> int:
    data = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    posts = Path(__file__).resolve().parent.parent / "content" / "posts"
    todo = []
    for f in sorted(posts.glob("*.md")):
        u = first_image(f.read_text(encoding="utf-8"))
        if u.startswith("http") and u not in data:
            todo.append(u)
    n = 0
    for u in todo:
        try:
            res = measure(u)
        except Exception as e:  # noqa: BLE001  読めない写真は次の晩にまた試す
            print(f"読めない: {u} ({e})", file=sys.stderr)
            continue
        # 横長の写真(高さが幅の 0.68 以下)は、もともと記事の幅いっぱいに出て左右に余白が出ないので切らない。
        # 切ると宣伝画像の文字が半分欠ける(2026-11-23 に53枚見て決めた)
        c = res[0] if res else None
        data[u] = c if c and c[5] / c[4] > 0.68 else None
        n += 1
    OUT.write_text(json.dumps(dict(sorted(data.items())), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"img_crop.json: {n}枚を新しく測った(全{len(data)}件)")
    return 0


def main() -> int:
    if "--heroes" in sys.argv:
        return heroes()
    save = "--save" in sys.argv
    data = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    for url in [a for a in sys.argv[1:] if not a.startswith("--")]:
        res = measure(url)
        if not res:
            print(f"切る必要なし: {url}")
            continue
        c, corner = res
        print(url)
        print(f"    crop: [{', '.join(map(str, c))}]   # 背景色 {corner}、"
              f"幅 {100 * (c[2] - c[0]) / c[4]:.0f}%・高さ {100 * (c[3] - c[1]) / c[5]:.0f}% を残す")
        data[url] = c
    if save:
        OUT.write_text(json.dumps(dict(sorted(data.items())), ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")
        print(f"img_crop.json: {len(data)}件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
