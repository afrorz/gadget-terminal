#!/usr/bin/env python3
"""
ogp.py — 記事ごとのOGP画像（1200×630 PNG）を生成する。

build.py から呼ばれる。フォントが見つからない環境では静かにスキップし、
ビルド自体は止めない（OGP画像が無くてもサイトは成立するため）。

単体実行するとサンプルを1枚出す:
    python3 scripts/ogp.py
"""
from __future__ import annotations

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # Pillow 未導入でもビルドは通す
    Image = None

W, H = 1200, 630
# サイト本体（ダークテーマ）に合わせた配色
BG = (11, 13, 16)
SURFACE = (18, 22, 27)
INK = (233, 237, 241)
INK_2 = (150, 160, 172)
INK_3 = (95, 105, 117)
ACCENT = (255, 107, 61)
RULE = (30, 36, 44)

# 探索順にフォント候補を並べる（Linux / macOS / Windows）
FONT_CANDIDATES = {
    "bold": [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
        "C:/Windows/Fonts/YuGothB.ttc",
        "C:/Windows/Fonts/meiryob.ttc",
    ],
    "regular": [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "C:/Windows/Fonts/YuGothR.ttc",
        "C:/Windows/Fonts/meiryo.ttc",
    ],
}


def _font(weight: str, size: int):
    for path in FONT_CANDIDATES[weight]:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return None


def _tokenize(text: str) -> list[str]:
    """日本語は1文字ずつ、英数字の連なりは1語としてまとめる（語の途中で折り返さないため）。"""
    tokens, buf = [], ""
    for ch in text:
        if ch.isascii() and (ch.isalnum() or ch in ",.$%-+/'"):
            buf += ch
        else:
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append(ch)
    if buf:
        tokens.append(buf)
    return tokens


def _wrap(draw, text: str, font, max_width: int, max_lines: int) -> list[str]:
    """日本語は文字単位、英数は単語単位で折り返す。"""
    lines, cur = [], ""
    for ch in _tokenize(text):
        trial = cur + ch
        if draw.textlength(trial, font=font) > max_width and cur:
            # 行頭に来ると具合の悪い文字は前の行に送る
            if ch in "。、）」』】〉》・！？":
                lines.append(trial)
                cur = ""
                continue
            lines.append(cur)
            cur = ch
        else:
            cur = trial
        if len(lines) == max_lines:
            break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and draw.textlength(lines[-1], font=font) > max_width - 40:
        lines[-1] = lines[-1][:-2] + "…"
    return lines


def render(title: str, category_label: str, site_title: str, out_path: Path,
           size: tuple[int, int] = (W, H), photo_credit: str = "") -> bool:
    """OGP画像を1枚書き出す。成功したら True。

    size は X 記事の表紙(横長 5:2)用。note の見出し画像は既定の 1200×630。
    photo_credit は note の見出し画像用。タイトルとロゴの間の帯に、TamakoStock
    (x-poster の ingestNoteDraft)がその週の製品写真を並べて合成する。その出典を
    帯の下に小さく入れておく(2026-10-18 本人判断で写真入りに)。
    """
    w, h = size
    if Image is None:
        return False
    f_title = _font("bold", 52)
    f_small = _font("bold", 24)
    f_brand = _font("bold", 26)
    if not all([f_title, f_small, f_brand]):
        return False

    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)

    pad = 88

    # 上端のアクセントバー
    d.rectangle([0, 0, w, 8], fill=ACCENT)

    # カテゴリ
    d.text((pad, 108), category_label, font=f_small, fill=ACCENT)

    # タイトル
    lines = _wrap(d, title, f_title, w - pad * 2, 4)
    y = 168
    for ln in lines:
        d.text((pad, y), ln, font=f_title, fill=INK)
        y += 76

    # 下端：罫線＋ブランド
    d.line([(pad, h - 108), (w - pad, h - 108)], fill=RULE, width=1)
    cx, cy = pad + 9, h - 66
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=ACCENT)
    d.text((pad + 32, h - 80), site_title.upper(), font=f_brand, fill=INK)
    label = "海外ガジェットの、まだ日本語で読めない話"
    d.text((w - pad - d.textlength(label, font=f_small), h - 76), label, font=f_small, fill=INK_3)
    if photo_credit:
        f_credit = _font("regular", 16) or f_small
        d.text((w - pad - d.textlength(photo_credit, font=f_credit), h - 132), photo_credit,
               font=f_credit, fill=INK_3)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    return True


if __name__ == "__main__":
    ok = render(
        "Honor Robot Phone 実機レビュー — 背面からジンバルが生えるスマホ、中国限定でCNY 9,999",
        "スマホ・ウェアラブル",
        "Gadget Signal",
        Path(__file__).resolve().parent.parent / "public" / "ogp" / "_sample.png",
    )
    print("生成しました" if ok else "フォントが見つからないためスキップしました")


# ────────────────────────────── 記事アイキャッチ ──────────────────────────────
# OGP画像（タイトル入り）はSNS共有用。サイト内のカードでタイトルを二重に出さないため、
# アイキャッチは「記事のキーワード」を大きく組んだ別デザインにする。

CARD_W, CARD_H = 1200, 675

CAT_TONE = {
    "smartphone": (255, 107, 61),   # オレンジ
    "pc": (79, 179, 196),           # シアン
    "weird": (217, 180, 95),        # アンバー
}


def _seed(text: str) -> int:
    import hashlib
    return int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16)


def render_card(keyword: str, category_label: str, category_key: str,
                site_title: str, slug: str, out_path: Path) -> bool:
    """記事一覧・記事冒頭に使うアイキャッチ。タイトルは入れない。"""
    if Image is None:
        return False
    tone = CAT_TONE.get(category_key, ACCENT)
    f_word = _font("bold", 96)
    f_label = _font("bold", 24)
    f_brand = _font("bold", 22)
    if not all([f_word, f_label, f_brand]):
        return False

    img = Image.new("RGB", (CARD_W, CARD_H), BG)
    d = ImageDraw.Draw(img)
    s = _seed(slug)

    # 背景：slugから決まる角度のストライプ。記事ごとに違う模様になる。
    # 文字が読めるよう、地色にごく近い薄さにする（下地の白板を敷かずに済む）。
    import math
    angle = 20 + (s % 5) * 12
    gap = 30 + (s >> 3) % 18
    tint = tuple(int(BG[i] + (tone[i] - BG[i]) * 0.10) for i in range(3))
    dx = math.tan(math.radians(angle)) * CARD_H
    x = -int(abs(dx)) - 200
    while x < CARD_W + abs(dx) + 200:
        d.line([(x, CARD_H), (x + dx, 0)], fill=tint, width=11)
        x += gap + 11

    d.rectangle([0, 0, CARD_W, 7], fill=tone)

    pad = 76
    d.text((pad, 92), category_label, font=f_label, fill=tone)

    # キーワードを縦方向の中心に置く（最大2行）
    lines = _wrap(d, keyword, f_word, CARD_W - pad * 2, 2)
    line_h = 132
    block_h = line_h * len(lines)
    y = int((CARD_H - block_h) / 2) - 10
    for ln in lines:
        d.text((pad, y), ln, font=f_word, fill=INK)
        y += line_h

    # 下端：細い罫線とブランド
    by = CARD_H - 76
    d.line([(pad, by - 18), (CARD_W - pad, by - 18)], fill=RULE, width=1)
    d.ellipse([pad, by + 10, pad + 15, by + 25], fill=tone)
    d.text((pad + 28, by + 6), site_title.upper(), font=f_brand, fill=INK_2)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    return True


# ── note の週まとめの見出し画像(2026-11-01 本人決定の形) ──
# 「今週の海外最新ガジェット5選」を大きく出し、左に主役(記事の1本目)の写真と「今までにない所」の一言、
# 右に残り4本の写真を 2×2 で並べる。番号は付けない。数字を主役にしない。
# 文字はここで描き、写真は TamakoStock(x-poster の ingestNoteDraft)が NOTE_SLOTS の位置に重ねる
# (クラウドの関数には日本語の書体が無いため。写真はそちらで JPEG に変換済みのものを使う)。
NOTE_SIZE = (1280, 670)
# 形ごとの寸法。x は X 記事の表紙(横長 5:2、2026-11-01 から同じ形で作る)
_NH = {
    "note": {"size": NOTE_SIZE, "top": 214, "x0": 60, "hw": 580, "hh": 426, "ph": 262, "gap": 16,
             "head_y": 28, "lead_y": 86, "count_y": 40, "lead": 58, "count": 112, "hook_dy": (22, 96), "sub": (28, 22)},
    "x": {"size": (1500, 600), "top": 196, "x0": 60, "hw": 660, "hh": 364, "ph": 232, "gap": 16,
          "head_y": 24, "lead_y": 76, "count_y": 32, "lead": 56, "count": 104, "hook_dy": (14, 82), "sub": (26, 22)},
}


def _slots(layout: str) -> list[dict]:
    L = _NH[layout]
    gx = L["x0"] + L["hw"] + 18
    cw = (L["size"][0] - L["x0"] - gx - L["gap"]) // 2
    ch = (L["hh"] - L["gap"]) // 2
    return [{"left": L["x0"], "top": L["top"], "width": L["hw"], "height": L["ph"], "radius": 14, "corners": "top"}] + [
        {"left": gx + (k % 2) * (cw + L["gap"]), "top": L["top"] + (k // 2) * (ch + L["gap"]),
         "width": cw, "height": ch, "radius": 14, "corners": "all"} for k in range(4)]


NOTE_SLOTS = _slots("note")
X_SLOTS = _slots("x")

_HEAVY = {  # いちばん太い字(Black)。無ければ Bold で代わりにする
    900: ["/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc", "C:/Windows/Fonts/NotoSansJP-VF.ttf"],
    700: ["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "C:/Windows/Fonts/NotoSansJP-VF.ttf"],
    500: ["/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
          "C:/Windows/Fonts/NotoSansJP-VF.ttf"],
}


def _heavy(weight: int, size: int):
    for path in _HEAVY[weight]:
        if not Path(path).exists():
            continue
        try:
            f = ImageFont.truetype(path, size)
            if path.endswith("-VF.ttf"):
                f.set_variation_by_axes([weight])
            return f
        except (OSError, ValueError):
            continue
    return _font("bold" if weight >= 700 else "regular", size)


def _fit(draw, text: str, max_width: int, big: int, small: int, weight: int):
    for s in range(big, small - 1, -2):
        f = _heavy(weight, s)
        if f and draw.textlength(text, font=f) <= max_width:
            return f
    return _heavy(weight, small)


def render_note_header(title: str, label: str, hook: str, sub: str, site_title: str, out_path: Path,
                       layout: str = "note") -> bool:
    """note の週まとめの見出し画像の文字の部分を書き出す。写真の場所は白い枠のまま。成功したら True。

    title は「今週の海外最新ガジェット5選｜10月第1週」、label は「WEEKLY｜2026.09.27-10.03」の形。
    hook は主役の「今までにない所」(大きく)、sub は何の製品か(小さく)。
    layout="x" で X 記事の表紙(1500×600)。写真の場所は X_SLOTS。
    """
    if Image is None:
        return False
    import re
    L = _NH[layout]
    w, h = L["size"]
    head, _, week = title.partition("｜")
    m = re.match(r"^(.*?)(\d+選)$", head.strip())
    lead, count = (m.group(1), m.group(2)) if m else (head.strip(), "")
    span = label.partition("｜")[2].replace("2026.", "").strip() or label
    f_lead, f_count = _heavy(900, L["lead"]), _heavy(900, L["count"])
    if not (f_lead and f_count):
        return False
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 8], fill=ACCENT)
    x0, hy = L["x0"], L["head_y"]
    d.ellipse([x0, hy + 12, x0 + 14, hy + 26], fill=ACCENT)
    d.text((x0 + 24, hy), site_title.upper(), font=_heavy(700, 22), fill=INK)
    d.text((x0 + 262, hy), f"WEEKLY｜{week.strip()}（{span}）" if week else label, font=_heavy(500, 22), fill=INK_2)
    d.text((x0, L["lead_y"]), lead, font=f_lead, fill=INK)
    if count:
        d.text((x0 + d.textlength(lead, font=f_lead) + 8, L["count_y"]), count, font=f_count, fill=ACCENT)
    # 主役の枠(上が写真、下が一言)と、残り4本の枠。写真は TamakoStock が重ねる
    d.rounded_rectangle([x0, L["top"], x0 + L["hw"], L["top"] + L["hh"]], 14, fill=(255, 255, 255))
    ty = L["top"] + L["ph"]
    d.text((x0 + 26, ty + L["hook_dy"][0]), hook, font=_fit(d, hook, L["hw"] - 52, 46, 34, 900), fill=(17, 19, 23))
    d.text((x0 + 28, ty + L["hook_dy"][1]), sub, font=_fit(d, sub, L["hw"] - 56, L["sub"][0], L["sub"][1], 700),
           fill=(80, 86, 94))
    for s in _slots(layout)[1:]:
        d.rounded_rectangle([s["left"], s["top"], s["left"] + s["width"], s["top"] + s["height"]], 14, fill=SURFACE)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    return True
