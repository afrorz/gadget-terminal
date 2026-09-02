#!/usr/bin/env python3
"""
build.py — content/posts/*.md から静的サイト public/ を生成する。

出力:
    public/index.html
    public/posts/<slug>.html
    public/category/<slug>.html
    public/about.html
    public/feed.xml
    public/sitemap.xml
    public/assets/style.css

使い方:
    python3 scripts/build.py
    python3 scripts/build.py --serve      # ローカルで確認 (http://localhost:8000)
"""
from __future__ import annotations

import argparse
import html
import json
from urllib.parse import quote, urlparse
import re
import shutil
import sys
from datetime import datetime, timezone, timedelta
from email.utils import format_datetime
from pathlib import Path

import markdown
import yaml

if sys.platform == "win32":  # Windows のコンソールは既定 cp932。出力を UTF-8 に固定する
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import ogp
except Exception:  # Pillow 未導入などでもビルドは通す
    ogp = None

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "content" / "posts"
FEATURES_DIR = ROOT / "content" / "features"
PUBLIC = ROOT / "public"
SITE_CFG = ROOT / "config" / "site.yaml"
JST = timezone(timedelta(hours=9))

MD = markdown.Markdown(extensions=["extra", "sane_lists", "toc", "tables"])

# base_url がサブディレクトリ配下（例: https://user.github.io/gadget-signal）のとき、
# サイト内リンクにそのプレフィックスを付ける。独自ドメイン（ルート直下）なら空文字になる。
BASE_PATH = ""


def u(path: str) -> str:
    """サイト内リンクを base_path 付きの絶対パスにする。"""
    if path in ("/", ""):
        return f"{BASE_PATH}/" if BASE_PATH else "/"
    return f"{BASE_PATH}/{path.lstrip('/')}"


# ────────────────────────────── 読み込み ──────────────────────────────
def load_site() -> dict:
    return yaml.safe_load(SITE_CFG.read_text(encoding="utf-8"))


def parse_post(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        print(f"  ! front matter がありません: {path.name}")
        return None
    meta = yaml.safe_load(m.group(1)) or {}
    body_md = m.group(2).strip()
    if meta.get("draft"):
        print(f"  - draft をスキップ: {path.name}")
        return None

    MD.reset()
    meta["body_html"] = MD.convert(body_md)
    meta["slug"] = meta.get("slug") or path.stem
    meta["date"] = str(meta.get("date", datetime.now(JST).strftime("%Y-%m-%d")))
    meta["reading_min"] = max(1, round(len(body_md) / 500))
    meta["path"] = f"posts/{meta['slug']}.html"
    meta.setdefault("tags", [])
    meta["keyword"] = meta.get("keyword") or (meta["tags"][0] if meta.get("tags") else "")
    meta.setdefault("sources", [])
    # 編集部ピックアップ: 運営者が自分で選んだ記事。自動選定と区別する。
    # pick_note は運営者自身の言葉なので、あれば必ず本人の文章として扱う（要約も改変もしない）。
    meta["pick"] = bool(meta.get("pick"))
    meta["pick_note"] = str(meta.get("pick_note") or "").strip()
    # 画像。images（複数枚）を正とし、旧 thumbnail は1枚目として取り込む。
    # ガジェット記事は実物が見えないと意味がないので、取れた分だけ全部載せる。
    imgs, seen_url = [], set()
    for it in (meta.get("images") or []):
        it = {"url": it} if isinstance(it, str) else (it or {})
        url = str(it.get("url") or "").strip()
        if not url or url in seen_url:
            continue
        seen_url.add(url)
        imgs.append({"url": url,
                     "caption": str(it.get("caption") or "").strip(),
                     "credit": str(it.get("credit") or meta.get("credit")
                                   or meta.get("thumbnail_credit") or "").strip()})
    if not imgs and meta.get("thumbnail"):
        imgs = [{"url": str(meta["thumbnail"]).strip(), "caption": "",
                 "credit": str(meta.get("thumbnail_credit") or "").strip()}]
    meta["images"] = imgs
    meta["thumbnail"] = imgs[0]["url"] if imgs else ""
    meta["thumbnail_credit"] = imgs[0]["credit"] if imgs else ""
    meta.setdefault("excerpt", re.sub(r"<[^>]+>", "", meta["body_html"])[:110].strip() + "…")
    return meta


# ────────────────────────────── テンプレート ──────────────────────────────
# merchant が指すストアのドメイン。ここに無いものはアフィリエイト変換しない。
MERCHANT_HOSTS = {
    "amazon": ("amazon.co.jp",),
    "rakuten": ("rakuten.co.jp",),
    "yahoo": ("yahoo.co.jp", "paypaymall.yahoo.co.jp"),
}


def affiliate_url(s: dict, url: str, merchant: str) -> tuple[str, bool]:
    """商品URLをアフィリエイトリンクに変換する。

    もしもアフィリエイトは提携先ごとにリンク形式が違うため、site.yaml に
    テンプレート（{url} が商品URLの位置）を持たせて差し替える方式にしている。
    無効・テンプレート未設定・対象外の提携先なら素のURLをそのまま返す。

    **merchant と URL のドメインが一致しない場合も変換しない。**
    例えば merchant: amazon なのに URL がメーカー直販だと、Amazon の
    アフィリエイトリンクに別ストアのURLを包むことになり、成果も発生せず
    リンクとしても不正になる。書き手の注意に頼らず、ここで弾く。
    戻り値: (URL, アフィリエイトリンクか)
    """
    aff = s.get("affiliate") or {}
    if not aff.get("enabled"):
        return url, False
    hosts = MERCHANT_HOSTS.get(merchant)
    if not hosts:
        return url, False
    host = urlparse(url).netloc.lower()
    if not any(host == h or host.endswith("." + h) for h in hosts):
        print(f"! merchant={merchant} だが URL のドメインは {host}。"
              f"アフィリエイト変換せず素のリンクにする")
        return url, False
    tmpl = str(aff.get(f"moshimo_{merchant}") or "").strip()
    if not tmpl or "{url}" not in tmpl:
        # ここを黙って素通ししていたせいで、merchant: amazon の記事が20本たまるまで
        # 誰も収益ゼロに気づけなかった（2026-08-16〜28）。未提携のストアを指定して
        # いるのは書き手の誤りなので、ビルドのたびに必ず見えるようにする。
        print(f"! merchant={merchant} は moshimo_{merchant} が未設定。"
              f"素のリンクになり報酬は発生しない: {url}")
        return url, False
    return tmpl.replace("{url}", quote(url, safe="")), True


def alternatives_section(s: dict, p: dict) -> tuple[str, bool]:
    """「今すぐ買えるオススメガジェット」セクション。

    クラファン案件は出荷が先で技適も未取得のことが多い。読者が実際に取れる行動を
    示すのが本来の目的で、アフィリエイトはその副産物として置く。
    リンクが無効でもセクション自体は出す（編集上の価値はリンクと無関係のため）。
    戻り値: (HTML, アフィリエイトリンクを含むか)
    """
    items = [x for x in (p.get("alternatives") or []) if x.get("name") and x.get("url")]
    if not items:
        return "", False
    has_aff = False
    rows = []
    for x in items:
        # merchant 未指定は「対応ストアではない」の意味。amazon に寄せない。
        link, is_aff = affiliate_url(s, str(x["url"]), str(x.get("merchant") or ""))
        has_aff = has_aff or is_aff
        why = f'<p class="alt-why">{html.escape(str(x["why"]))}</p>' if x.get("why") else ""
        # image は任意（楽天APIから拾えたときだけ入る。scripts/find_rakuten_alt.py 参照）。
        # 無ければ今までどおり画像無しで出す。
        img = (f'<a href="{html.escape(link)}" class="alt-thumb" rel="nofollow sponsored noopener" '
               f'target="_blank"><img src="{html.escape(str(x["image"]))}" alt="" loading="lazy"></a>'
               if x.get("image") else "")
        rows.append(
            f'<li class="alt-item">{img}<div class="alt-text">'
            f'<a href="{html.escape(link)}" rel="nofollow sponsored noopener" '
            f'target="_blank">{html.escape(str(x["name"]))}</a>{why}</div></li>')
    label = ('<span class="alt-ad">広告</span>' if has_aff else "")
    return (f'<section class="alts"><h2>今すぐ買えるオススメガジェット{label}</h2>'
            f'<ul>{"".join(rows)}</ul></section>', has_aff)


def analytics(s: dict) -> str:
    """アクセス解析のタグを出す。設定が空なら何も出さない（外部スクリプトを読み込まない）。

    - cf_analytics_token: Cloudflare Web Analytics。Cookie を使わないので同意表示が不要
    - analytics_id: GA4。使う場合は G- で始まる測定ID
    両方入れれば両方出る。
    """
    tags = []
    token = str(s.get("cf_analytics_token") or "").strip()
    if token:
        tags.append('<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
                    f"data-cf-beacon='{{\"token\": \"{token}\"}}'></script>")
    gid = str(s.get("analytics_id") or "").strip()
    if gid:
        tags.append(f'<script async src="https://www.googletagmanager.com/gtag/js?id={gid}"></script>'
                    "<script>window.dataLayer=window.dataLayer||[];"
                    "function gtag(){dataLayer.push(arguments);}"
                    "gtag('js',new Date());"
                    f"gtag('config','{gid}');</script>")
    return "".join(tags)


def adsense(s: dict) -> str:
    """AdSense のコードスニペット。

    `adsense_client`（ca-pub- で始まる発行ID）を site.yaml に入れると出る。
    **空のあいだは何も出さない。** 審査を受けるまでIDは発行されないので、
    それまでサイトには一切広告関連のコードが入らない状態にしておく。

    審査時のサイト確認でも、この同じスニペットを全ページの <head> に
    置くよう求められる。だから広告を出す前の確認段階でも、ここにIDを
    入れるだけで足りる。
    """
    cid = str(s.get("adsense_client") or "").strip()
    if not cid:
        return ""
    return ('<script async crossorigin="anonymous" '
            f'src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={html.escape(cid)}">'
            "</script>")


def head(site: dict, title: str, desc: str, url_path: str, extra: str = "",
         image: str = "ogp/default.png") -> str:
    s = site["site"]
    # image が外部URL（公式サイトの製品画像）ならそのまま使う。
    # 自社生成のアイキャッチだけがサイト相対パスで渡ってくる。
    is_ext_img = image.startswith(("http://", "https://"))
    img_url = image if is_ext_img else f"{s['base_url'].rstrip('/')}/{image.lstrip('/')}"
    # 寸法は自社生成画像（1200x630 固定）のときだけ書く。
    # 外部画像は実寸が分からず、誤った値を書くとカードの描画が崩れる。
    dims = ('<meta property="og:image:width" content="1200">' '<meta property="og:image:height" content="630">')
    img_dims = "" if is_ext_img else dims
    _p = "" if url_path in ("index.html", "/") else url_path.lstrip("/")
    full_url = f"{s['base_url'].rstrip('/')}/{_p}"
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0b0d10">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{html.escape(full_url)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{html.escape(s['title'])}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{html.escape(full_url)}">
<meta property="og:locale" content="{s.get('locale', 'ja_JP')}">
<meta property="og:image" content="{html.escape(img_url)}">{img_dims}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{html.escape(img_url)}">
<link rel="icon" type="image/svg+xml" href="{u('assets/favicon.svg')}">
<link rel="alternate" type="application/rss+xml" title="{html.escape(s['title'])}" href="{u('feed.xml')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{u('assets/style.css')}">
{adsense(s)}
{analytics(s)}
{extra}
</head>
<body>"""


def header(site: dict) -> str:
    s = site["site"]
    cats = "".join(
        f'<a href="{u("category/" + c["slug"] + ".html")}" class="nav-item cat-{k}">'
        f'<span class="nav-code">{c.get("code", "---")}</span>'
        f'<span class="nav-label">{html.escape(c["label"])}</span></a>'
        for k, c in site["categories"].items()
    )
    return f"""
<header class="site-head">
  <div class="wrap head-inner">
    <a class="brand" href="{u("/")}">
      <span class="brand-name">{html.escape(s['title'])}</span><span class="caret" aria-hidden="true"></span>
    </a>
    <nav class="nav">{cats}<a href="{u("features.html")}" class="nav-item nav-ft"><span class="nav-code">FTR</span><span class="nav-label">特集</span></a><a href="{u("jpn.html")}" class="nav-item nav-jp"><span class="nav-code">JPN</span><span class="nav-label">国内クラファン</span></a><a href="{u("about.html")}" class="nav-item nav-about"><span class="nav-code">INF</span><span class="nav-label">運営</span></a></nav>
    <span class="head-clock" aria-hidden="true"><small>JST</small><b data-clk="h">--</b><i>:</i><b data-clk="m">--</b></span>
  </div>
</header>"""


def footer(site: dict) -> str:
    s = site["site"]
    year = datetime.now(JST).year
    span = f"{s['copyright_from']}" if year == s["copyright_from"] else f"{s['copyright_from']}–{year}"
    return f"""
<footer class="site-foot">
  <div class="wrap">
    <div class="foot-board">
      <span class="foot-code">SYS</span>
      <span class="foot-status">ONLINE</span>
      <span class="foot-tag">{html.escape(s['tagline'])}</span>
    </div>
    <div class="foot-cols">
      <p class="foot-meta">
        <a href="{u("feed.xml")}">RSS</a><a href="{u("features.html")}">特集</a><a href="{u("jpn.html")}">国内クラファン</a><a href="{u("about.html")}">運営・免責</a><a href="{u("privacy.html")}">プライバシー</a><a href="mailto:{s.get('contact_email','')}">お問い合わせ</a>
      </p>
      <p class="foot-copy">© {span} {html.escape(s['title'])} — {html.escape(s['author'])}</p>
    </div>
  </div>
</footer>
{BOARD_JS}
</body>
</html>"""


def jp(text) -> str:
    """日本語を、句読点でしか改行させない形に組む。

    CSS は日本語の文節を知らないので、放っておくと「日本／語」のような位置で割れる。
    句読点で区切った塊を inline-block にすると、その塊の途中では改行されなくなる。
    塊と塊の間には <wbr>（幅ゼロの改行可能点）を置いて、そこだけで折り返させる。

    塊が1行に収まらないほど長い場合は、塊の内部でも折り返す。そこは CSS 側の
    word-break:auto-phrase に任せる（対応ブラウザなら文節単位で折り返す）。
    """
    parts = [x for x in re.split(r"(?<=[、。！？])", str(text)) if x]
    if len(parts) <= 1:
        return html.escape(str(text))
    return "<wbr>".join(f'<span class="nb">{html.escape(x)}</span>' for x in parts)


def jp_em(text) -> str:
    """jp() に **強調** だけ効かせる版。

    jp() は HTML をエスケープするので、front matter に <strong> は書けない。
    かといって Markdown を通すと段落タグが混ざる。特集の短い解説文で欲しいのは
    太字だけなので、** で割ってから塊ごとに jp() をかける。
    先に jp() をかけると、強調の途中に句読点があったとき span をまたいで
    しまい、タグの入れ子が壊れる。順番を変えないこと。
    """
    out = []
    for i, seg in enumerate(str(text).split("**")):
        if not seg:
            continue
        out.append(f"<strong>{jp(seg)}</strong>" if i % 2 else jp(seg))
    return "".join(out)


def card(site: dict, p: dict, featured: bool = False) -> str:
    key = p.get("category", "misc")
    cat = site["categories"].get(key, {"label": "その他", "slug": "misc", "code": "---"})
    cls = ("card card-featured" if featured else "card") + f" cat-{key}"
    blurb = p.get("kicker") or p["excerpt"]
    img, is_ext = card_image(p)
    return f"""
<article class="{cls}">
  <a class="card-thumb{' card-thumb-real' if is_ext else ''}" href="{u(p['path'])}" aria-hidden="true" tabindex="-1">
    <img src="{img}" alt="" loading="lazy" width="1200" height="675"
         decoding="async" referrerpolicy="no-referrer"
         onerror="this.onerror=null;this.src='{u("cards/" + p['slug'] + ".png")}'">
  </a>
  <p class="card-meta">
    <a class="card-code" href="{u("category/" + cat['slug'] + ".html")}">{cat.get('code','---')}</a>
    <span class="card-cat">{html.escape(cat['label'])}</span>
    <time datetime="{p['date']}">{p['date'].replace('-', '.')}</time>
    <span class="card-read">{p['reading_min']}MIN</span>
  </p>
  <h2 class="card-title">{'<span class="pick-badge">PICK</span>' if p.get('pick') else ''}<a href="{u(p['path'])}">{jp(p['title'])}</a></h2>
  <p class="card-excerpt">{html.escape(blurb)}</p>
</article>"""



# ── 到着案内板 ───────────────────────────────────────────────
# 空港の案内板は「今どういう状態か」を出すから案内板として機能する。
# 装飾で語彙を増やさず、記事のデータから確実に言えるものだけを出す。
STATUS_STYLE = {
    "NOW ARRIVING": "live",   # 本日掲載
    "NOW BOARDING": "live",   # クラウドファンディング受付中
    "FINAL CALL":   "urgent", # 締切まで7日以内
    "GATE CLOSED":  "done",   # 募集終了
    "FULLY BOOKED": "done",   # 品切れ
    "DELAYED":      "warn",   # 発売・出荷の延期
    "LOCAL ONLY":   "warn",   # 現地限定。日本展開は未定
    "SCHEDULED":    "plain",  # 発売日が決まっている未発売品
    "LANDED":       "plain",  # 日本で今すぐ買える
    "ARRIVED":      "done",   # 掲載済み（既定値）
}


def post_status(p: dict, today: str) -> tuple[str, str]:
    """記事の状態を (表示ラベル, 補足) で返す。

    front matter の status が最優先。無ければ deadline から機械的に決める。
    どちらも無い記事は掲載日で「本日 / 既出」を出す。推測はしない。
    """
    label = str(p.get("status") or "").strip().upper()
    note = str(p.get("status_note") or "").strip()
    if label:
        return (label if label in STATUS_STYLE else "ARRIVED", note)

    deadline = str(p.get("deadline") or "").strip()
    if deadline:
        try:
            end = datetime.strptime(deadline[:10], "%Y-%m-%d").date()
            days = (end - datetime.strptime(today, "%Y-%m-%d").date()).days
        except ValueError:
            days = None
        if days is not None:
            if days < 0:
                return ("GATE CLOSED", "")
            if days <= 7:
                return ("FINAL CALL", f"残り{days}日" if days else "本日締切")
            return ("NOW BOARDING", f"残り{days}日")

    return ("NOW ARRIVING", "") if p["date"] == today else ("ARRIVED", "")


def post_origin(site: dict, p: dict) -> tuple[str, str]:
    """FROM 列。(空港コード, 都市名) を返す。分からなければ ('---', '')。

    front matter の origin が最優先。無ければ config の origins から
    タイトル・タグに出てくるブランド名で引く。当たらなければ空欄にする。
    **推測して埋めない。** 出所は事実なので、外すと記事の信頼に響く。
    """
    raw = str(p.get("origin") or "").strip()
    # sources に国内クラファンのURLがあれば、それが一番確実な出所の証拠。
    # ブランド名の推測より先に見る。
    if not raw and domestic_cf_source(p):
        raw = "JPN 国内"
    if not raw:
        table = site.get("origins") or {}
        haystack = (p.get("title", "") + " " + " ".join(str(t) for t in (p.get("tags") or [])))
        hit = [(brand, val) for brand, val in table.items()
               if re.search(r"(?<![A-Za-z])" + re.escape(brand) + r"(?![A-Za-z])",
                            haystack, re.I)]
        if hit:
            # 長いブランド名を優先（Redmi と Xiaomi が両方当たる場合など）
            raw = max(hit, key=lambda kv: len(kv[0]))[1]
    if not raw:
        return ("---", "")
    parts = raw.split(None, 1)
    return (parts[0].upper(), parts[1] if len(parts) > 1 else "")


def flight_no(p: dict, order: dict) -> str:
    """便名。掲載順の通し番号なので、記事ごとに一意で変わらない。"""
    return f"GT {order.get(p['slug'], 0):04d}"


def board_posts(site: dict, posts: list[dict], limit: int = 6) -> list[dict]:
    """案内板に出す記事を選ぶ。

    空港の到着案内板は「これから着く便」を上に出す。それに倣って、
    **まだ出資できるクラウドファンディング案件を締切が近い順に上へ置く。**
    掲載日順にすると、読者が今日行動できる案件が下に沈んで案内板の意味が無くなる。
    残りは新着順で埋める。
    """
    today = datetime.now(JST).strftime("%Y-%m-%d")
    live, rest = [], []
    for p in posts:
        label, _ = post_status(p, today)
        if label in ("FINAL CALL", "NOW BOARDING"):
            live.append(p)
        else:
            rest.append(p)
    live.sort(key=lambda x: str(x.get("deadline") or "9999"))
    return (live + rest)[:limit]


def board_row(site: dict, p: dict, i: int) -> str:
    key = p.get("category", "misc")
    cat = site["categories"].get(key, {"code": "---", "label": "その他"})
    today = datetime.now(JST).strftime("%Y-%m-%d")
    label, note = post_status(p, today)
    style = STATUS_STYLE.get(label, "done")
    code, city = post_origin(site, p)
    return f"""<a class="board-row cat-{key}" href="{u(p['path'])}">
  <span class="b-flt" data-flap>{p['flight']}</span>
  <span class="b-from"><b data-flap>{html.escape(code)}</b>{f'<span>{html.escape(city)}</span>' if city else ''}</span>
  <span class="b-code" data-flap>{cat.get('code','---')}</span>
  <span class="b-key">{html.escape(p.get('keyword') or '')}</span>
  <span class="b-title">{html.escape(p['title'])}</span>
  <span class="st st-{style}" data-flap-status>{html.escape(label)}{f'<em>{html.escape(note)}</em>' if note else ''}</span>
  <span class="b-arrow" aria-hidden="true">→</span>
</a>"""


def page_path(n: int) -> str:
    """ページ番号 → サイト内パス。1ページ目だけルートに置く。"""
    return "index.html" if n <= 1 else f"page/{n}.html"


def pager(current: int, total: int) -> str:
    """前へ／次へ と現在位置を出すページ送り。1ページしかないときは何も出さない。"""
    if total <= 1:
        return ""
    prev = (f'<a class="pager-link" href="{u(page_path(current - 1))}" rel="prev">← 新しい記事</a>'
            if current > 1 else '<span class="pager-link is-off">← 新しい記事</span>')
    nxt = (f'<a class="pager-link" href="{u(page_path(current + 1))}" rel="next">古い記事 →</a>'
           if current < total else '<span class="pager-link is-off">古い記事 →</span>')
    nums = "".join(
        f'<span class="pager-num is-here">{n}</span>' if n == current
        else f'<a class="pager-num" href="{u(page_path(n))}">{n}</a>'
        for n in range(1, total + 1))
    return f'<nav class="pager" aria-label="ページ送り">{prev}<span class="pager-nums">{nums}</span>{nxt}</nav>'


def picks_section(site: dict, posts: list[dict], limit: int = 3) -> str:
    """編集部ピックアップ。運営者が自分で選んだ記事だけを並べる。

    自動選定の記事と同じ見た目にすると意味が消えるので、カードではなく
    「選んだ理由」を主役にした横並びの形にしている。pick_note が無い記事は
    kicker で代替するが、**本人の言葉があるときは必ずそちらを出す**。
    """
    picked = [p for p in posts if p.get("pick")][:limit]
    if not picked:
        return ""
    rows = []
    for p in picked:
        img, is_ext = card_image(p)
        note = p.get("pick_note") or p.get("kicker") or p["excerpt"]
        own = bool(p.get("pick_note"))
        rows.append(f"""
  <article class="pick">
    <a class="pick-thumb" href="{u(p['path'])}" aria-hidden="true" tabindex="-1">
      <img src="{img}" alt="" loading="lazy" width="1200" height="675"
           decoding="async" referrerpolicy="no-referrer"
           onerror="this.onerror=null;this.src='{u("cards/" + p['slug'] + ".png")}'">
    </a>
    <div class="pick-body">
      <h3 class="pick-title"><a href="{u(p['path'])}">{html.escape(p['title'])}</a></h3>
      <p class="pick-note{' pick-note-own' if own else ''}">{html.escape(note)}</p>
    </div>
  </article>""")
    return f"""
<section class="picks">
  <h2 class="picks-head">編集部ピックアップ<span class="picks-sub">運営者が選んだガジェット</span></h2>
  <div class="picks-list">{''.join(rows)}
  </div>
</section>"""


BOARD_JS = """<script>
(function(){"use strict";
var reduced=window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/* 時計。JSTで24時間表記。閲覧者の端末が海外時刻でも日本時間を出す。 */
function tick(){
  var t=new Date(Date.now()+new Date().getTimezoneOffset()*60000+32400000);
  document.querySelectorAll('[data-clk="h"]').forEach(function(e){
    e.textContent=String(t.getHours()).padStart(2,"0");});
  document.querySelectorAll('[data-clk="m"]').forEach(function(e){
    e.textContent=String(t.getMinutes()).padStart(2,"0");});
}
tick();setInterval(tick,10000);

/* スプリットフラップ。本物の案内板は文字が回って目当ての字で止まる。
   全行を派手に回すと悪趣味なので、等幅の記号列だけ・読み込み時に一度だけ。
   日本語のタイトルは動かさない（実際の案内板もコード列しか回らない）。 */
var G="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
function rnd(s,n){return s.replace(/[A-Z0-9]/g,function(){
  return G[Math.floor(Math.random()*(n||G.length))];});}

function flap(el){
  var fin=el.getAttribute("data-f");
  if(fin===null){fin=el.textContent;el.setAttribute("data-f",fin);}
  if(reduced){el.textContent=fin;return;}
  var n=0,t=setInterval(function(){
    if(++n>=7){clearInterval(t);el.textContent=fin;return;}
    el.textContent=rnd(fin);},42);
}
function flapStatus(el){
  var node=el.firstChild;
  if(!node||node.nodeType!==3)return;
  var fin=el.getAttribute("data-f");
  if(fin===null){fin=node.nodeValue;el.setAttribute("data-f",fin);}
  if(reduced){node.nodeValue=fin;return;}
  var n=0,t=setInterval(function(){
    if(++n>=9){clearInterval(t);node.nodeValue=fin;return;}
    node.nodeValue=rnd(fin,26);},40);
}
var rows=document.querySelectorAll(".board-row");
rows.forEach(function(row,i){
  setTimeout(function(){
    row.querySelectorAll("[data-flap]").forEach(flap);
    var st=row.querySelector("[data-flap-status]");
    if(st)flapStatus(st);
  },reduced?0:i*55);
});
})();
</script>"""


def render_index(site: dict, posts: list[dict], page: int = 1, total_pages: int = 1,
                 all_posts: list[dict] | None = None) -> str:
    s = site["site"]
    if not posts:
        body = '<p class="empty">まだ記事がありません。</p>'
    elif page <= 1:
        # 1ページ目だけ、案内板と大きい先頭記事を出す。
        lead, rest = posts[0], posts[1:]
        rows = "".join(board_row(site, p, i + 1)
                       for i, p in enumerate(board_posts(site, all_posts or posts)))
        body = f"""
<section class="board">
  <h2 class="board-title">
    <svg class="pict-arr" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <g transform="rotate(22 12 11)"><path d="M21 11 L14.5 11.8 L10 17 L7.5 17 L9.8 11.9
        L4.5 12 L3 14 L1.5 14 L2.6 11 L1.5 8 L3 8 L4.5 10 L9.8 10.1 L7.5 5 L10 5 L14.5 10.2 Z"/></g>
      <rect x="2.5" y="20" width="19" height="1.5" rx=".75"/>
    </svg>
    <span class="board-title-en">ARRIVALS</span>
    <span class="board-title-ja">到着案内 — 海外発ガジェットの入荷状況</span>
  </h2>
  <div class="board-head">
    <span>FLIGHT</span><span>FROM</span><span>CAT</span><span>KEY</span><span>ENTRY</span><span>STATUS</span><span></span>
  </div>
  {rows}
</section>
<section class="lead">
  {card(site, lead, featured=True)}
</section>
<section class="grid">
  {''.join(card(site, p) for p in rest)}
</section>
{picks_section(site, all_posts or posts)}
{pager(page, total_pages)}"""
    else:
        # 2ページ目以降はカードだけを並べる。
        body = f"""
<section class="grid">
  {''.join(card(site, p) for p in posts)}
</section>
{pager(page, total_pages)}"""
    title = f"{s['title']} — {s['tagline']}" if page <= 1 else f"{s['title']} — {page}ページ目"
    return (
        head(site, title, s["description"], page_path(page))
        + header(site)
        + f"""
<main class="wrap">
  <section class="hero{'' if page <= 1 else ' hero-sm'}">
    <p class="eyebrow">{'DEPARTURES / 海外発' if page <= 1 else f'ARCHIVE / {page} of {total_pages}'}</p>
    <h1 class="hero-title">{jp(s['tagline']) if page <= 1 else f'過去の記事 — {page}ページ目'}</h1>
    <p class="hero-sub">{jp(s['description']) if page <= 1 else ''}</p>
  </section>
  {body}
</main>"""
        + footer(site)
    )


# 国内クラファンかどうかは sources の URL で判定する。front matter に手で
# 書かせるフィールドを増やすと書き忘れが起きる（現に origin は既存記事5本
# すべてで空だった）。sources は記事作成時に必ず埋まるので、そこから
# 機械的に判定するほうが確実。
DOMESTIC_CF_HOSTS = ("makuake.com", "camp-fire.jp", "greenfunding.jp")


def domestic_cf_source(p: dict) -> dict | None:
    """記事の sources に国内クラファンの URL があれば、その1件を返す。"""
    for src in (p.get("sources") or []):
        url = str(src.get("url") or "")
        if any(h in url for h in DOMESTIC_CF_HOSTS):
            return src
    return None


def render_domestic_cf(site: dict, posts: list[dict]) -> str:
    """国内クラファンのコーナー。専用ページにする（トップには置かない）。

    この媒体の顔は「海外の、まだ日本語になっていない話」。トップの中央に
    国内クラファンを並べると、その顔と衝突する。かといって埋もれさせても
    意味が無いので、独立ページを作って about.html と同格でナビから飛べる
    ようにする。
    """
    s = site["site"]
    items = [p for p in posts if domestic_cf_source(p)]
    if items:
        rows = "".join(card(site, p) for p in items)
        body = f'<section class="grid">{rows}</section>'
    else:
        body = '<p class="empty">現在、国内クラウドファンディングの記事はまだありません。</p>'
    return (
        head(site, f"国内クラファン注目 — {s['title']}",
             "Makuake・CAMPFIRE等、国内クラウドファンディングのガジェットをまとめて確認。",
             "jpn.html")
        + header(site)
        + f"""
<main class="wrap">
  <section class="hero hero-sm">
    <p class="eyebrow">JPN / DOMESTIC</p>
    <h1 class="hero-title">国内クラファン注目</h1>
    <p class="hero-sub">Makuake・CAMPFIRE など、国内クラウドファンディングで見つけたガジェットです。
    海外発の記事と違い、すでに日本語で読める案件なので、当メディアでは
    海外の類似品との比較や国内先行の背景など、独自の角度を添えて扱います。</p>
  </section>
  {body}
</main>"""
        + footer(site)
    )


# ---------------------------------------------------------------- 特集ページ
# 特集は「まとめ記事」ではなく買い物の判断ページ。日々のニュース記事とは
# 別の生き物として content/features/ に置く。
#
# ニュース記事の選定基準は「海外で報じられて、まだ日本語記事が無い話」だが、
# **特集ページだけはこの制限を外している。**（2026-09-01 決定）
# 特集は「すぐ欲しい」と思って読む人のためのページなので、そこに買えない
# ものしか無いと役に立たない。国内で普通に買える製品を並べてよい。
#
# ただし外した制限の代わりに、必ず守る縛りを1つ入れている:
# **載せる製品には入手性の判定（買えるか・技適はどうか）を必ず付ける。**
# ここを外すと「白いガジェット10選」と同じになり、誰でも書けるページに
# 落ちる。技適まで踏み込んで言い切るのが、この媒体が持っている差分。

# 入手性の判定。ラベルと、カードに出す色の分類。
AVAIL_STYLE = {
    "verified": ("買える", "ok"),           # 国内正規流通＋技適が一次ソースで確認できた
    "official": ("公式直販で買える", "ok"),  # メーカー公式が日本発送＋技適を明記
    "caution": ("条件つき", "warn"),        # 買えるが注意点がある（対象モデル限定など）
}


def parse_feature(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        print(f"  ! front matter がありません: {path.name}")
        return None
    meta = yaml.safe_load(m.group(1)) or {}
    if meta.get("draft"):
        print(f"  - draft をスキップ: {path.name}")
        return None
    MD.reset()
    meta["body"] = MD.convert(m.group(2).strip())
    meta.setdefault("slug", path.stem)
    meta["path"] = f"features/{meta['slug']}.html"
    meta.setdefault("products", [])
    meta.setdefault("excluded", [])
    meta.setdefault("related", [])
    return meta


def feature_product(item: dict, n: int = 0) -> str:
    """製品1件を、記事の一節として縦に組む。

    横並びのカードにすると比較表になってしまい、上から読ませる記事にならない。
    見出し → 大きな写真 → 本文 → 事実の箱 → リンク、の順に置く。
    本文は空行で段落に割る。ここが記事の実体なので、いちばん広く取る。
    """
    key = str(item.get("availability") or "").strip()
    label, tone = AVAIL_STYLE.get(key, ("判定なし", "bad"))
    name = html.escape(str(item.get("name") or ""))
    brand = html.escape(str(item.get("brand") or ""))
    price = html.escape(str(item.get("price") or ""))
    where = jp(str(item.get("where") or ""))
    giteki = jp(str(item.get("giteki") or ""))
    url = str(item.get("url") or "").strip()
    src = str(item.get("source") or "").strip()

    body = "".join(f"<p>{jp_em(para.strip())}</p>"
                   for para in str(item.get("note") or "").split("\n\n")
                   if para.strip())

    # ガジェットは写真が無いと読まれない。特集の製品は画像を必須扱いにする。
    # PLAYBOOK 3.5 のとおり、公式ページの画像をホットリンクし、credit を必ず出す。
    img = str(item.get("image") or "").strip()
    credit = str(item.get("credit") or "").strip()
    shot = ""
    if img:
        cap = (f'<figcaption class="fp-credit">出典: {html.escape(credit)}</figcaption>'
               if credit else "")
        shot = f'<figure class="fp-shot">{ext_img(img, name)}{cap}</figure>'

    buy = (f'<a class="fp-buy" href="{html.escape(url)}" target="_blank" '
           f'rel="noopener nofollow">購入ページを開く</a>') if url else ""
    src_link = (f'<a class="fp-src" href="{html.escape(src)}" target="_blank" '
                f'rel="noopener">確認したソース</a>') if src else ""

    return f"""
<section class="fp fp-{tone}">
  <header class="fp-head">
    <p class="fp-kicker"><span class="fp-no">{n:02d}</span><span class="fp-brand">{brand}</span></p>
    <h2 class="fp-name">{name}</h2>
    <span class="fp-badge fp-badge-{tone}">{label}</span>
  </header>
  {shot}
  <div class="fp-body">{body}</div>
  <dl class="fp-meta">
    <dt>価格</dt><dd>{price or "&mdash;"}</dd>
    <dt>買えるところ</dt><dd>{where or "&mdash;"}</dd>
    <dt>技適</dt><dd>{giteki or "&mdash;"}</dd>
  </dl>
  <p class="fp-links">{buy}{src_link}</p>
</section>"""


def render_feature(site: dict, f: dict, posts: list[dict]) -> str:
    s = site["site"]
    items = "".join(feature_product(x, i) for i, x in enumerate(f["products"], 1))
    grid = f'<div class="fp-list">{items}</div>' if items else ""

    excluded = ""
    if f["excluded"]:
        rows = "".join(
            f'<li><strong>{html.escape(str(x.get("name") or ""))}</strong>'
            f' &mdash; {jp_em(str(x.get("why") or ""))}</li>'
            for x in f["excluded"])
        excluded = f"""
<section class="fx">
  <h2 class="fx-head">今回入れなかったもの</h2>
  <p class="fx-lead">条件を満たさなかった製品と、その理由です。
  買えないものを「買える」と書かないために残しています。</p>
  <ul class="fx-list">{rows}</ul>
</section>"""

    by_slug = {p["slug"]: p for p in posts}
    rel = [by_slug[x] for x in f["related"] if x in by_slug]
    related = ""
    if rel:
        related = f"""
<section class="fr">
  <h2 class="fr-head">この特集に関連する記事</h2>
  <section class="grid">{''.join(card(site, p) for p in rel)}</section>
</section>"""

    # SNS に貼られたときのカード画像。1製品目の写真を使う。
    # 特集はテーマページなので、自動生成のアイキャッチより実物のほうが強い。
    ogp_img = next((str(x.get("image")).strip() for x in f["products"]
                    if str(x.get("image") or "").strip()), "ogp/default.png")
    updated = html.escape(str(f.get("updated") or ""))
    upd_html = f'<p class="fp-updated">最終確認 {updated}</p>' if updated else ""
    return (
        head(site, f"{f.get('seo_title') or f['title']} — {s['title']}",
             str(f.get("description") or ""), f["path"], image=ogp_img)
        + header(site)
        + f"""
<main class="wrap">
  <section class="hero hero-sm">
    <p class="eyebrow">{html.escape(str(f.get('eyebrow') or 'FEATURE'))}</p>
    <h1 class="hero-title">{html.escape(f['title'])}</h1>
    <p class="hero-sub">{jp_em(str(f.get('lede') or ''))}</p>
    {upd_html}
  </section>
  <div class="prose feature-intro">{f['body']}</div>
  {grid}
  {excluded}
  {related}
</main>"""
        + footer(site)
    )


def render_features_index(site: dict, features: list[dict]) -> str:
    s = site["site"]
    if features:
        rows = "".join(
            f'<a class="fi" href="{u(f["path"])}">'
            f'<p class="fi-eyebrow">{html.escape(str(f.get("eyebrow") or "FEATURE"))}</p>'
            f'<h2 class="fi-title">{html.escape(f["title"])}</h2>'
            f'<p class="fi-lede">{jp(str(f.get("lede") or ""))}</p>'
            f'<p class="fi-count">{str(len(f["products"]))+"製品" if f["products"] else "解説"}</p></a>'
            for f in features)
        body = f'<section class="fi-grid">{rows}</section>'
    else:
        body = '<p class="empty">特集はまだありません。</p>'
    return (
        head(site, f"特集 — {s['title']}",
             "テーマごとに、日本で実際に買えるガジェットを入手性と技適の判定つきでまとめています。",
             "features.html")
        + header(site)
        + f"""
<main class="wrap">
  <section class="hero hero-sm">
    <p class="eyebrow">FEATURE / 特集</p>
    <h1 class="hero-title">特集</h1>
    <p class="hero-sub">ひとつのテーマで複数のガジェットをまとめています。
    日々のニュースと違い、<strong>日本で実際に買えるものだけ</strong>を並べ、
    製品ごとに入手先と技適の状況を書いています。</p>
  </section>
  {body}
</main>"""
        + footer(site)
    )


def render_category(site: dict, key: str, cat: dict, posts: list[dict]) -> str:
    s = site["site"]
    items = [p for p in posts if p.get("category") == key]
    body = "".join(card(site, p) for p in items) or '<p class="empty">このカテゴリの記事はまだありません。</p>'
    return (
        head(site, f"{cat['label']} — {s['title']}", cat["description"], f"category/{cat['slug']}.html")
        + header(site)
        + f"""
<main class="wrap">
  <section class="hero hero-sm cat-{key}">
    <p class="eyebrow">{cat.get('code','---')} / CATEGORY</p>
    <h1 class="hero-title">{html.escape(cat['label'])}</h1>
    <p class="hero-sub">{jp(cat['description'])}</p>
  </section>
  <section class="grid">{body}</section>
</main>"""
        + footer(site)
    )


def card_image(p: dict) -> tuple[str, bool]:
    """カードに出す画像を決める。

    優先順位:
      1. front matter の thumbnail（自社撮影・許諾済み素材を置く用）
      2. YouTube のサムネイル（動画を埋め込んでいる場合）
         YouTube はサムネイルを表示用に配信しており、oEmbed でも
         thumbnail_url として公開されている。転載ではなく正規の利用。
      3. 自動生成のアイキャッチ
    戻り値: (URL, 外部URLか)
    """
    if p.get("thumbnail"):
        th = str(p["thumbnail"])
        return (th, th.startswith("http"))
    for e in (p.get("embeds") or []):
        if (e.get("type") or "").lower() == "youtube" and e.get("id"):
            return (f"https://i.ytimg.com/vi/{e['id']}/hqdefault.jpg", True)
    return (u("cards/" + p["slug"] + ".png"), False)


def ext_img(src: str, alt: str, *, lazy: bool = True, fallback: str = "") -> str:
    """権利者のサーバー上の画像をそのまま参照する img タグを作る。

    referrerpolicy="no-referrer" は必須。多くのCDNが Referer を見て
    ホットリンクを弾くため、これが無いと他サイトからの表示だけ壊れる。
    読み込めなかったときは、生成アイキャッチに差し替えるか、figure ごと消す。
    """
    onerr = ("this.onerror=null;this.src=" + repr(fallback) if fallback
             else "this.closest('figure').remove()")
    lazy_attr = 'loading="lazy" ' if lazy else ""
    return (f'<img src="{html.escape(src)}" alt="{html.escape(alt)}" '
            f'{lazy_attr}decoding="async" '
            f'referrerpolicy="no-referrer" onerror="{onerr}">')


def render_gallery(p: dict) -> str:
    """1枚目以外の製品画像をまとめて出す。1枚しか無ければ何も出さない。"""
    imgs = p.get("images") or []
    if len(imgs) < 2:
        return ""
    figs = []
    for im in imgs[1:]:
        cap = im.get("caption") or ""
        figs.append(f'<figure class="shot">{ext_img(im["url"], cap or p["title"])}'
                    + (f'<figcaption>{html.escape(cap)}</figcaption>' if cap else "")
                    + "</figure>")
    credit = imgs[0].get("credit") or ""
    return ('<section class="gallery"><h2>製品画像</h2>'
            f'<div class="gallery-grid">{"".join(figs)}</div>'
            + (f'<p class="gallery-credit">出典: {html.escape(credit)}</p>' if credit else "")
            + "</section>")


def render_embeds(p: dict) -> tuple[str, bool]:
    """front matter の embeds を、プラットフォーム公式の埋め込みHTMLに変換する。

    画像を自社サーバーにコピーせず、権利者が公開している投稿をそのまま表示する方式。
    転載にあたらないため、メーカー公式アカウントの製品写真を合法的に見せられる。
    戻り値: (HTML, X埋め込みスクリプトが必要か)
    """
    items = p.get("embeds") or []
    if not items:
        return "", False
    blocks, needs_x = [], False
    for e in items:
        kind = (e.get("type") or "").lower()
        url = e.get("url", "")
        caption = html.escape(e.get("caption", ""))
        if kind in ("x", "twitter"):
            needs_x = True
            blocks.append(
                f'<figure class="embed embed-x">'
                f'<blockquote class="twitter-tweet" data-lang="ja" data-dnt="true">'
                f'<a href="{html.escape(url)}"></a></blockquote>'
                f'{f"<figcaption>{caption}</figcaption>" if caption else ""}</figure>')
        elif kind == "youtube":
            vid = html.escape(e.get("id", ""))
            blocks.append(
                f'<figure class="embed embed-video">'
                f'<iframe src="https://www.youtube-nocookie.com/embed/{vid}" '
                f'title="{caption or "YouTube"}" loading="lazy" allowfullscreen '
                f'referrerpolicy="strict-origin-when-cross-origin"></iframe>'
                f'{f"<figcaption>{caption}</figcaption>" if caption else ""}</figure>')
        elif kind == "link":
            # 権利上そのまま出せない画像は、元記事へのリンクカードで代替する
            title = html.escape(e.get("title", url))
            pub = html.escape(e.get("publisher", ""))
            blocks.append(
                f'<figure class="embed embed-link">'
                f'<a href="{html.escape(url)}" rel="nofollow noopener" target="_blank">'
                f'<span class="embed-link-title">{title}</span>'
                f'<span class="embed-link-pub">{pub} — 製品画像は元記事でご覧いただけます</span>'
                f'</a></figure>')
    return "\n".join(blocks), needs_x


def render_post(site: dict, p: dict, others: list[dict]) -> str:
    s = site["site"]
    cat = site["categories"].get(p.get("category"), {"label": "その他", "slug": "misc"})
    embeds_html, needs_x = render_embeds(p)
    gallery_html = render_gallery(p)
    # 出発地 → 成田。この媒体がやっているのは「海外の製品を日本に着陸させること」なので、
    # 出所が分かる記事ではそれを1行で見せる。分からない記事では何も出さない。
    o_code, o_city = post_origin(site, p)
    route = ""
    # 日本発の製品に「✈ NRT 日本」を出すと意味を成さないので、その場合は出さない。
    if o_code not in ("---", "JPN", "NRT", "HND", "KIX"):
        route = (f'<span class="dot"></span><span class="meta-route">'
                 f'{html.escape(o_code)}{f" {html.escape(o_city)}" if o_city else ""}'
                 f'<i aria-hidden="true">✈</i>NRT 日本</span>')
    # 最初の1本は本文の前に出す。下端に置くと誰も見ないため。
    lead_embed, rest_embed = "", ""
    if embeds_html:
        parts = embeds_html.split("</figure>")
        blocks = [x + "</figure>" for x in parts if x.strip()]
        lead_embed = f'<section class="embeds embeds-lead">{blocks[0]}</section>' if blocks else ""
        if len(blocks) > 1:
            rest_embed = ('<section class="embeds"><h2>関連する投稿・動画</h2>'
                          + "".join(blocks[1:]) + '</section>')
    embeds_html = rest_embed

    # 動画がある記事は生成画像を出さない。実写のほうが情報量が多い。
    # 動画が無く thumbnail がある場合は、そちらを実写として出す。
    # 外部URLのときは自社サーバーに複製せず、権利者のサーバーを直接参照する。
    fallback = u("cards/" + p["slug"] + ".png")
    if lead_embed:
        hero_block = lead_embed
    elif p.get("thumbnail"):
        th = str(p["thumbnail"])
        credit = p.get("thumbnail_credit")
        cap = (f'<figcaption class="hero-credit">出典: {html.escape(str(credit))}</figcaption>'
               if credit else "")
        hero_block = (f'<figure class="article-hero article-hero-real">'
                      + ext_img(th, p["title"], lazy=False, fallback=fallback)
                      + f'{cap}</figure>')
    else:
        hero_block = (f'<figure class="article-hero">'
                      f'<img src="{fallback}" '
                      f'alt="{html.escape(p["title"])}" width="1200" height="675"></figure>')
    sources = ""
    if p["sources"]:
        rows = "".join(
            f'<li><a href="{html.escape(src["url"])}" rel="nofollow noopener" target="_blank">'
            f'{html.escape(src.get("title", src["url"]))}</a>'
            f'<span class="src-pub">{html.escape(src.get("publisher", ""))}</span></li>'
            for src in p["sources"]
        )
        sources = f"""
<section class="sources">
  <h2>参照した一次ソース</h2>
  <ol>{rows}</ol>
  <p class="sources-note">本記事は上記の海外報道をもとに編集部が構成したものです。日本国内の発売・価格は各社の公式発表をご確認ください。</p>
</section>"""

    # 関連記事はタグの一致数で選ぶ。同数ならカテゴリ一致、それも同じなら新しい順。
    # 機械的に先頭3本を出すより回遊率が上がり、内部リンクの意味も強くなる。
    my_tags = {str(t).lower() for t in (p.get("tags") or [])}
    def relevance(o: dict) -> tuple:
        shared = len(my_tags & {str(t).lower() for t in (o.get("tags") or [])})
        same_cat = 1 if o.get("category") == p.get("category") else 0
        return (-shared, -same_cat, o["date"] < p["date"], o["date"])
    related = sorted((o for o in others if o["slug"] != p["slug"]), key=relevance)[:3]
    rel_html = ""
    if related:
        rel_html = f"""
<section class="related">
  <h2>ほかの記事</h2>
  <div class="grid">{''.join(card(site, r) for r in related)}</div>
</section>"""

    base = s["base_url"].rstrip("/")
    page_url = f"{base}/{p['path']}"
    # OGP画像は必ず存在する（生成される）ので、これを構造化データの image にも使う。
    # thumbnail がある記事は実写のほうが望ましいので、そちらを優先する。
    ld_image = str(p["thumbnail"]) if p.get("thumbnail") else f"{base}/ogp/{p['slug']}.png"
    article_ld = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": p["title"][:110],
        "description": p["excerpt"],
        "image": [ld_image],
        "datePublished": f"{p['date']}T09:00:00+09:00",
        "dateModified": f"{p.get('modified') or p['date']}T09:00:00+09:00",
        "url": page_url,
        "mainEntityOfPage": {"@type": "WebPage", "@id": page_url},
        "inLanguage": "ja",
        "articleSection": cat["label"],
        "author": {"@type": "Organization", "name": s["author"], "url": base + "/about.html"},
        "publisher": {"@type": "Organization", "name": s["title"],
                      "logo": {"@type": "ImageObject", "url": f"{base}/ogp/default.png"}},
    }
    if p.get("tags"):
        article_ld["keywords"] = ", ".join(str(t) for t in p["tags"])
    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": s["title"], "item": base + "/"},
            {"@type": "ListItem", "position": 2, "name": cat["label"],
             "item": f"{base}/category/{cat['slug']}.html"},
            {"@type": "ListItem", "position": 3, "name": p["title"], "item": page_url},
        ],
    }
    # front matter の faq を FAQPage として出す。検索結果に Q&A が展開されることがある。
    # ガジェット記事は「技適は?」「日本で使える?」が定番クエリなので効きやすい。
    faq = [x for x in (p.get("faq") or []) if x.get("q") and x.get("a")]
    faq_ld = None
    faq_html = ""
    if faq:
        faq_ld = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": str(x["q"]),
                            "acceptedAnswer": {"@type": "Answer", "text": str(x["a"])}}
                           for x in faq],
        }
        rows = "".join(
            f'<div class="faq-item"><h3><span class="faq-q">Q</span>'
            f'{html.escape(str(x["q"]))}</h3>'
            f'<p>{html.escape(str(x["a"]))}</p></div>' for x in faq)
        faq_html = f'<section class="faq"><h2>よくある質問</h2>{rows}</section>'

    alts_html, has_aff = alternatives_section(s, p)
    # ステマ規制。アフィリエイトリンクがある記事は、本文の先頭で広告を含む旨を示す。
    # 「サイトのどこかに書いてある」では足りないため、記事ごとに出す。
    disclosure = ""
    if has_aff:
        text = str((s.get("affiliate") or {}).get("disclosure") or "この記事にはアフィリエイト広告を含みます")
        disclosure = f'<p class="ad-notice">{html.escape(text)}</p>'

    ld = "".join(
        f'<script type="application/ld+json">{json.dumps(d, ensure_ascii=False, separators=(",", ":"))}</script>'
        for d in (article_ld, breadcrumb_ld, faq_ld) if d)

    return (
        head(site, f"{p.get('seo_title') or p['title']} — {s['title']}", p["excerpt"], p["path"],
             ld + ('\n<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'
                   if needs_x else ""),
             # thumbnail は外部URLのまま、生成アイキャッチはサイト相対で渡す
             image=(str(p["thumbnail"]) if p.get("thumbnail")
                    else f"ogp/{p['slug']}.png"))
        + header(site)
        + f"""
<main class="wrap article-wrap">
  <article class="article cat-{p.get("category", "misc")}">
    <p class="eyebrow"><a href="{u("category/" + cat['slug'] + ".html")}"><span class="eyebrow-code">{cat.get('code','---')}</span>{html.escape(cat['label'])}</a></p>
    <h1 class="article-title">{jp(p['title'])}</h1>
    {f'<p class="article-lede">{jp(p["kicker"])}</p>' if p.get('kicker') else ''}
    {f'<aside class="pick-callout"><p class="pick-callout-head">編集部ピックアップ</p><p class="pick-callout-note">{html.escape(p["pick_note"])}</p></aside>' if p.get('pick') and p.get('pick_note') else (f'<p class="pick-callout pick-callout-bare">編集部ピックアップ<span>運営者が選んだガジェットです</span></p>' if p.get('pick') else '')}
    {disclosure}
    <p class="article-meta"><time datetime="{p['date']}">{p['date'].replace('-', '.')}</time><span class="dot"></span>{p['reading_min']} MIN READ{route}</p>
    {hero_block}
    <div class="prose">{p['body_html']}</div>
    {gallery_html}
    {embeds_html}
    {alts_html}
  {faq_html}
  {sources}
  </article>
  {rel_html}
</main>"""
        + footer(site)
    )


def render_privacy(site: dict) -> str:
    """プライバシーポリシー。

    参加しているアフィリエイトプログラムは config から組み立てる。
    **手で書くと、提携が増減したときに嘘になる。** 提携していないプログラムを
    「参加しています」と書くのは規約違反にもなるため、設定を唯一の情報源にする。
    """
    s = site["site"]
    aff = s.get("affiliate", {}) or {}
    programs = []
    if aff.get("enabled"):
        for key, label in (("moshimo_amazon", "Amazon.co.jp"),
                           ("moshimo_rakuten", "楽天市場"),
                           ("moshimo_yahoo", "Yahoo!ショッピング")):
            if str(aff.get(key) or "").strip():
                programs.append(f"{label}（もしもアフィリエイト経由）")

    if programs:
        aff_block = (
            "<p>本サイトは以下のアフィリエイトプログラムに参加しており、"
            "商品リンク経由での購入によって紹介料を得ることがあります。</p>"
            "<ul>" + "".join(f"<li>{html.escape(x)}</li>" for x in programs) + "</ul>"
            "<p>アフィリエイトリンクを含む記事には、記事上部にその旨を表示します。"
            "リンクをクリックすると、成果を測定するために各プログラムの Cookie が"
            "お使いのブラウザに保存されることがあります。この Cookie は購入の成否を"
            "計測する目的にのみ使われ、当サイトが内容を参照することはありません。</p>"
            "<p><strong>紹介料の有無は、掲載する製品の選定や評価に影響しません。</strong>"
            "取り上げる製品は編集方針に従って選び、提携の有無で扱いを変えることはしません。</p>")
        if str(aff.get("moshimo_amazon") or "").strip():
            # 承認後。運営規約が定める文言そのもの（現在形・確定表現）。
            aff_block += (f"<p>Amazonのアソシエイトとして、{html.escape(s['title'])} は"
                          "適格販売により収入を得ています。</p>")
        elif aff.get("amazon_applicant"):
            # 審査中。「もう得ています」と書くのは事実に反するので出さない。
            # ただし Amazon の審査は「承認されたら規約どおり開示できる状態か」を
            # 申請時点で見ている。開示が一切無いプライバシーポリシーのまま
            # 審査に出して否認された実例があるため、申請中である旨は明記する。
            aff_block += (f"<p>{html.escape(s['title'])} は、Amazon.co.jp を宣伝しリンクすることによって"
                          "サイトが紹介料を獲得できる手段を提供することを目的に設定された"
                          "Amazonアソシエイト・プログラムへの参加を申請しています。"
                          "承認された場合は、Amazonアソシエイト・プログラム運営規約に基づき、"
                          "本ページに「Amazonのアソシエイトとして、"
                          f"{html.escape(s['title'])} は適格販売により収入を得ています。」"
                          "と明記します。</p>")
    else:
        aff_block = "<p>現在、参加しているアフィリエイトプログラムはありません。</p>"

    # 広告配信の開示。AdSense のプログラムポリシーが掲載者に義務づけている。
    # **adsense_client が空なら丸ごと出さない。** 配信していないのに
    # 「広告を配信しています」と書くのは、Amazon の件と同じ種類の嘘になる。
    ad_block = ""
    if str(s.get("adsense_client") or "").strip():
        ad_block = """
      <h2>広告配信について</h2>
      <p>当サイトは、第三者配信の広告サービス <strong>Google AdSense</strong> を利用しています。</p>
      <p>Google を含む第三者配信事業者は、Cookie を使用して、利用者が当サイトや他のサイトに
      過去にアクセスした際の情報にもとづいて広告を配信することがあります。この Cookie により、
      当サイトや他のサイトへのアクセス情報が広告の表示に使われますが、
      <strong>氏名・住所・メールアドレス・電話番号は含まれません。</strong></p>
      <p>パーソナライズド広告は、
      <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener">
      広告設定</a>から無効にできます。第三者配信事業者の Cookie 利用を一括で無効にしたい場合は
      <a href="https://optout.aboutads.info/" target="_blank" rel="noopener">aboutads.info</a>
      をご利用ください。ブラウザの設定から Cookie を無効にすることもできます。</p>
      <p>Google が広告で情報をどのように使用するかについては、
      <a href="https://policies.google.com/technologies/ads?hl=ja" target="_blank" rel="noopener">
      Google の広告に関するポリシー</a>をご確認ください。</p>
      <p>欧州経済領域（EEA）・英国・スイスからアクセスされた場合は、Cookie の使用について
      同意を確認するメッセージを表示します。同意しない選択もでき、その場合は
      利用者の興味関心にもとづかない広告が表示されます。</p>"""

    analytics = []
    if str(s.get("cf_analytics_token") or "").strip():
        analytics.append(
            "<li><strong>Cloudflare Web Analytics</strong> — ページの表示回数や参照元を"
            "集計するために利用しています。<strong>Cookie を使用せず</strong>、"
            "ブラウザの指紋採取（フィンガープリンティング）も行いません。"
            "個人を特定できる情報は収集していません。</li>")
    if str(s.get("analytics_id") or "").strip():
        analytics.append(
            "<li><strong>Google アナリティクス</strong> — Cookie を使用してアクセス状況を"
            "集計します。ブラウザの設定で Cookie を無効にすると収集を拒否できます。</li>")
    analytics_block = ("<ul>" + "".join(analytics) + "</ul>") if analytics else (
        "<p>アクセス解析ツールは利用していません。</p>")

    body = f"""
<main class="wrap article-wrap">
  <article class="article">
    <p class="eyebrow">PRIVACY</p>
    <h1 class="article-title">プライバシーポリシー</h1>
    <div class="prose">
      <p>{html.escape(s['author'])}（以下「当社」）は、{html.escape(s['title'])}
      （{html.escape(s['base_url'])}、以下「当サイト」）における利用者の情報の取り扱いについて、
      以下のとおり定めます。</p>

      <h2>収集する情報</h2>
      <p>当サイトは、閲覧にあたって氏名・住所・電話番号などの個人情報の入力を求めません。
      会員登録の仕組みもありません。</p>
      <p>お問い合わせをいただいた場合に限り、返信のためにメールアドレスと本文をお預かりします。
      これらは回答の目的にのみ使用し、ご本人の同意なく第三者に提供することはありません。</p>

      <h2>アクセス解析</h2>
      {analytics_block}

      <h2>Cookie とアフィリエイトプログラム</h2>
      {aff_block}
{ad_block}

      <h2>外部サイトへのリンク</h2>
      <p>当サイトは記事中で外部サイトへのリンクを掲載しています。リンク先での個人情報の
      取り扱いについては、各サイトのプライバシーポリシーをご確認ください。当サイトは
      リンク先の内容および個人情報の取り扱いについて責任を負いません。</p>

      <h2>埋め込みコンテンツ</h2>
      <p>記事には YouTube などの外部サービスの埋め込みを含むことがあります。埋め込みの
      表示にあたり、各サービスが利用者の情報を取得する場合があります。YouTube の埋め込みには、
      再生するまで視聴履歴に記録されない <code>youtube-nocookie.com</code> を使用しています。</p>

      <h2>免責</h2>
      <p>当サイトの記事は公開情報をもとに編集したものです。掲載内容の正確性には努めますが、
      完全性を保証するものではありません。詳細は<a href="{u("about.html")}">運営について</a>を
      ご確認ください。</p>

      <h2>本ポリシーの変更</h2>
      <p>法令の改正や取り扱いの変更に応じて、本ポリシーを予告なく改定することがあります。
      改定後の内容は当ページに掲載した時点で効力を生じます。</p>

      <h2>お問い合わせ窓口</h2>
      <p>本ポリシーおよび情報の取り扱いに関するお問い合わせは、
      <a href="mailto:{s.get('contact_email','')}">{html.escape(s.get('contact_email',''))}</a> までご連絡ください。</p>
      <p>運営： {html.escape(s['author'])}</p>
    </div>
  </article>
</main>"""
    return (head(site, f"プライバシーポリシー — {s['title']}",
                 "個人情報・Cookie・アフィリエイトプログラムの取り扱いについて", "privacy.html")
            + header(site) + body + footer(site))


def render_about(site: dict) -> str:
    s = site["site"]
    body = f"""
<main class="wrap article-wrap">
  <article class="article">
    <p class="eyebrow">ABOUT</p>
    <h1 class="article-title">{html.escape(s['title'])}について</h1>
    <div class="prose">
      <p>{html.escape(s['description'])}</p>

      <h2>編集方針</h2>
      <ul>
        <li>海外メディア・メーカー公式発表を毎日巡回し、複数媒体が報じた話題を優先して扱います。</li>
        <li>スペックや価格などの数値は、参照元に記載のある範囲でのみ記載します。推測値は「未発表」と明示します。</li>
        <li>リーク情報は、その旨と確度を本文中に明記します。</li>
        <li>すべての記事に参照した一次ソースへのリンクを掲載します。</li>
      </ul>

      <h2>免責</h2>
      <p>本サイトの記事は海外の公開情報をもとに編集したものです。掲載時点の情報であり、価格・仕様・発売時期は変更される場合があります。
      日本国内での販売可否および技適等の認証状況は保証しません。購入・輸入の判断は読者ご自身の責任でお願いします。</p>

      <h2>権利について</h2>
      <p>各製品名・企業名は各社の商標です。記事中の画像は、自社作成のもの、権利者から許諾を得たもの、
      またはメーカー公式ページ・クラウドファンディングのプロジェクトページを出典として引用したものです。
      引用にあたって画像を当サイトのサーバーに複製することはなく、出典を明示のうえ必要最小限の範囲で行います。
      掲載の停止をご希望の場合は下記までご連絡ください。速やかに対応します。</p>

      <h2>お問い合わせ</h2>
      <p>記事内容の訂正・削除のご依頼、その他のお問い合わせは下記までご連絡ください。</p>
      <ul>
        <li>一般のお問い合わせ： <a href="mailto:{s.get('contact_email','')}">{html.escape(s.get('contact_email',''))}</a></li>
        <li>製品情報・取材のご連絡： <a href="mailto:{s.get('press_email','')}">{html.escape(s.get('press_email',''))}</a></li>
      </ul>
      <p>運営： {html.escape(s['author'])}</p>
      <p>個人情報・Cookie・アフィリエイトの取り扱いは
      <a href="{u("privacy.html")}">プライバシーポリシー</a>をご確認ください。</p>
    </div>
  </article>
</main>"""
    return head(site, f"運営について — {s['title']}", "編集方針・免責・お問い合わせ", "about.html") + header(site) + body + footer(site)


def _json_str(v: str) -> str:
    import json
    return json.dumps(v, ensure_ascii=False)


def render_feed(site: dict, posts: list[dict]) -> str:
    s = site["site"]
    base = s["base_url"].rstrip("/")
    items = []
    for p in posts[:30]:
        dt = datetime.strptime(p["date"], "%Y-%m-%d").replace(tzinfo=JST)
        items.append(f"""  <item>
    <title>{html.escape(p['title'])}</title>
    <link>{base}/{p['path']}</link>
    <guid isPermaLink="true">{base}/{p['path']}</guid>
    <pubDate>{format_datetime(dt)}</pubDate>
    <description>{html.escape(p['excerpt'])}</description>
  </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <title>{html.escape(s['title'])}</title>
  <link>{base}/</link>
  <description>{html.escape(s['description'])}</description>
  <language>ja</language>
{chr(10).join(items)}
</channel></rss>"""


def render_sitemap(site: dict, posts: list[dict], features: list[dict] | None = None) -> str:
    base = site["site"]["base_url"].rstrip("/")
    # jpn.html は 2026-09 まで漏れていた。増えた固定ページはここに足すこと。
    urls = [f"{base}/", f"{base}/about.html", f"{base}/privacy.html",
            f"{base}/jpn.html", f"{base}/features.html"]
    urls += [f"{base}/{f['path']}" for f in (features or [])]
    per_page = int(site["site"].get("posts_per_page") or 20)
    total_pages = max(1, -(-len(posts) // per_page))
    urls += [f"{base}/{page_path(n)}" for n in range(2, total_pages + 1)]
    urls += [f"{base}/category/{c['slug']}.html" for c in site["categories"].values()]
    urls += [f"{base}/{p['path']}" for p in posts]
    # lastmod があるとクローラーが再訪問すべきURLを判断できる。
    # 記事は自身の日付、一覧系は最新記事の日付を使う。
    latest = max((p["date"] for p in posts), default="")
    by_url = {f"{base}/{p['path']}": p["date"] for p in posts}
    def entry(loc: str) -> str:
        d = by_url.get(loc, latest)
        return f"<url><loc>{loc}</loc>" + (f"<lastmod>{d}</lastmod>" if d else "") + "</url>"
    body = "".join(entry(u) for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>'


# ────────────────────────────── CSS ──────────────────────────────
CSS = """
/* ============================================================
   Gadget Terminal — 出発案内板を設計言語にしたダークテーマ
   ============================================================ */
:root{
  --bg:#0b0d10; --surface:#12161b; --raised:#171c22;
  --ink:#e9edf1; --ink-2:#96a0ac; --ink-3:#5f6975;
  --rule:#1e242c; --rule-2:#2a323c;
  --accent:#ff6b3d;
  --cat:var(--accent);
  --max:1280px; --measure:36rem;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --disp:"Space Grotesk","Hiragino Sans","Noto Sans JP","Yu Gothic",sans-serif;
  --sans:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP","Yu Gothic",sans-serif;
}
.cat-smartphone{--cat:#ff6b3d}
.cat-pc{--cat:#4fb3c4}
.cat-weird{--cat:#d9b45f}

/* 生成する画像がダーク固定のため、UIもダークに統一する。
   ライトモードにすると画像だけ黒い板になって不整合が出る。 */

*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;color-scheme:dark}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);
  font-size:15px;line-height:1.72;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
a{color:inherit;text-decoration:none}
img{max-width:100%}
.wrap{max-width:var(--max);margin:0 auto;padding:0 24px}

/* ── ヘッダー ───────────────────────────────── */
.site-head{position:sticky;top:0;z-index:20;border-bottom:1px solid var(--rule);
  background:color-mix(in srgb,var(--bg) 82%,transparent);backdrop-filter:blur(14px) saturate(1.4)}
.head-inner{display:flex;align-items:center;justify-content:space-between;gap:20px;height:48px}
/* 空港・駅・管制室に共通する記号は「常に動いている現在時刻」。
   コロンだけ明滅させると、静止画に見えない。 */
.head-clock{font-family:var(--mono);font-size:12px;letter-spacing:.1em;color:var(--ink-2);
  font-variant-numeric:tabular-nums;display:flex;align-items:center;gap:7px;flex:none}
.head-clock small{font-size:9.5px;letter-spacing:.16em;color:var(--ink-3)}
.head-clock i{font-style:normal;animation:clk-blink 1s steps(1,end) infinite}
.meta-route{font-family:var(--mono);letter-spacing:.06em;color:var(--ink-3)}
.meta-route i{font-style:normal;margin:0 7px;color:var(--cat)}
@keyframes clk-blink{50%{opacity:.25}}
.brand{display:inline-flex;align-items:center;font-family:var(--mono);font-weight:600;
  font-size:14px;letter-spacing:.16em;text-transform:uppercase;white-space:nowrap}
.caret{width:9px;height:16px;background:var(--accent);margin-left:7px;display:inline-block;
  animation:blink 1.25s steps(1) infinite}
@keyframes blink{0%,55%{opacity:1}56%,100%{opacity:0}}
.nav{display:flex;gap:4px;overflow-x:auto;scrollbar-width:none}
.nav::-webkit-scrollbar{display:none}
.nav-item{display:inline-flex;align-items:center;gap:7px;padding:5px 9px;border-radius:2px;
  white-space:nowrap;transition:background .18s}
.nav-item:hover{background:var(--raised)}
.nav-code{font-family:var(--mono);font-size:10.5px;font-weight:600;letter-spacing:.1em;
  color:var(--cat);border:1px solid var(--cat);padding:2px 5px;border-radius:2px;opacity:.9}
.nav-label{font-size:12px;color:var(--ink-2)}
.nav-item:hover .nav-label{color:var(--ink)}
.nav-about{--cat:var(--ink-3)}
.nav-jp{--cat:#d9b45f}

/* ── ヒーロー ───────────────────────────────── */
.hero{padding:30px 0 20px}
.hero-sm{padding:32px 0 22px;border-bottom:1px solid var(--rule);margin-bottom:0}
.eyebrow{font-family:var(--mono);font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--cat);margin:0 0 10px;font-weight:600}
.hero-title{font-family:var(--disp);font-size:clamp(22px,2.9vw,34px);line-height:1.4;
  margin:0 0 10px;font-weight:700;letter-spacing:-.015em;max-width:30em}
.hero-sub{margin:0;color:var(--ink-2);font-size:13px;max-width:44em;line-height:1.75}
/* 日本語の折り返し。塊の途中では改行させない（jp() が挿入する span） */
.nb{display:inline-block}
/* 対応ブラウザ（Chromium系）では、塊の内部も文節単位で折り返す */
.hero-title,.hero-sub,.article-title,.article-lede,.card-title,.card-excerpt,
.pick-title,.pick-note,.pick-callout-note,.board-title,.prose p,.prose li,
.faq dt,.faq dd{word-break:auto-phrase}

/* ── 出発案内板 ─────────────────────────────── */
.board{border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);margin-bottom:40px}
/* 見出しの飛行機は ISO 7001 の到着ピクトグラム（機首を下げた機体＋接地線）。
   本物の案内板に飛行機の絵は無く、あるのはこの見出しの位置だけ。
   サイト内の他の場所にアイコンを散らさないこと。空港ではなく旅行ブログに見える。 */
.board-title{display:flex;align-items:center;gap:11px;margin:0;padding:16px 4px 13px;
  font-family:var(--mono);font-weight:600;font-size:13px;letter-spacing:.2em;
  border-bottom:1px solid var(--rule)}
.pict-arr{width:19px;height:19px;flex:none;fill:var(--accent)}
.board-title-en{color:var(--ink)}
.board-title-ja{font-family:var(--sans);font-size:11.5px;font-weight:400;letter-spacing:0;
  color:var(--ink-3);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
@media (max-width:620px){.board-title-ja{display:none}}
.board-head,.board-row{display:grid;
  grid-template-columns:64px 74px 44px 150px minmax(0,1fr) 150px 20px;
  align-items:center;gap:14px;font-family:var(--mono);font-size:11.5px}
.board-head{padding:7px 4px;color:var(--ink-3);font-size:9.5px;letter-spacing:.16em;
  border-bottom:1px solid var(--rule)}
.board-row{padding:8px 4px;border-bottom:1px solid var(--rule);position:relative;
  transition:background .16s,padding-left .16s}
.board-row:last-child{border-bottom:0}
.board-row::before{content:"";position:absolute;left:0;top:0;bottom:0;width:2px;
  background:var(--cat);transform:scaleY(0);transition:transform .2s}
.board-row:hover{background:var(--raised);padding-left:10px}
.board-row:hover::before{transform:scaleY(1)}
.b-no{color:var(--ink-3)}
.b-code{color:var(--cat);font-weight:600;letter-spacing:.08em}
.b-date{color:var(--ink-3);font-variant-numeric:tabular-nums}
.b-flt{color:var(--ink-2);letter-spacing:.06em;font-variant-numeric:tabular-nums}
.b-from{color:var(--ink);letter-spacing:.05em;overflow:hidden;white-space:nowrap}
.b-from span{color:var(--ink-3);font-family:var(--sans);letter-spacing:0;
  margin-left:6px;font-size:11px}
/* 運航ステータス。カテゴリ色（--cat）とは別系統にして、意味だけを担わせる。
   同じ色で分類と状態の両方を表すと、どちらの意味か読めなくなる。 */
.st{display:inline-flex;align-items:center;gap:7px;letter-spacing:.1em;font-weight:500;
  white-space:nowrap;overflow:hidden}
.st::before{content:"";width:6px;height:6px;border-radius:50%;background:currentColor;flex:none}
.st em{font-style:normal;font-family:var(--sans);letter-spacing:0;color:var(--ink-3);
  font-size:11px;margin-left:2px}
.st-live{color:#5ad19a}
.st-live::before{animation:st-pulse 1.6s ease-in-out infinite}
@keyframes st-pulse{50%{opacity:.3}}
.st-urgent{color:var(--accent)}
.st-warn{color:#d9b45f}
.st-done{color:var(--ink-3)}
.st-plain{color:var(--ink-2)}
.b-key{font-family:var(--sans);font-size:13px;color:var(--ink);font-weight:600;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.b-title{font-family:var(--sans);font-size:12.5px;color:#bcc6d1;overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.b-min{color:var(--ink-3);text-align:right}
.b-arrow{color:var(--ink-3);text-align:right;transition:transform .2s,color .2s}
.board-row:hover .b-arrow{color:var(--cat);transform:translateX(3px)}
.board-row:hover .b-title{color:var(--ink)}

/* ── ページ送り ─────────────────────────────── */
.pager{display:flex;align-items:center;justify-content:space-between;gap:16px;
  margin:36px 0 8px;padding-top:20px;border-top:1px solid var(--rule);
  font-family:var(--mono);font-size:12px;letter-spacing:.04em}
.pager-link{color:var(--ink-2);text-decoration:none;padding:6px 10px;border:1px solid var(--rule-2);border-radius:3px}
.pager-link:hover{color:var(--ink);border-color:var(--accent)}
.pager-link.is-off{opacity:.32;border-style:dashed}
.pager-nums{display:flex;gap:4px;flex-wrap:wrap;justify-content:center}
.pager-num{color:var(--ink-3);text-decoration:none;min-width:26px;text-align:center;padding:6px 4px;border-radius:3px}
.pager-num:hover{color:var(--ink)}
.pager-num.is-here{color:var(--bg);background:var(--accent);font-weight:600}
@media (max-width:520px){
  .pager{flex-direction:column;gap:12px}
}

/* ── カード ─────────────────────────────────── */
.picks{margin:0 0 40px;padding:22px 0 6px;border-bottom:1px solid var(--rule)}
.picks-head{font-family:var(--mono);font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--ink-3);margin:0 0 18px;display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.picks-sub{font-family:inherit;font-size:12px;letter-spacing:0;text-transform:none;color:var(--ink-3)}
.picks-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:24px 28px}
.pick{display:grid;grid-template-columns:96px 1fr;gap:14px;align-items:start}
.pick-thumb{display:block;overflow:hidden;border-radius:2px;background:var(--surface)}
.pick-thumb img{width:100%;height:64px;object-fit:cover;display:block}
.pick-title{font-size:15px;line-height:1.5;margin:0 0 6px;font-weight:600}
.pick-title a{text-decoration:none;color:inherit}
.pick-title a:hover{text-decoration:underline}
.pick-note{font-size:13px;line-height:1.75;color:var(--ink-3);margin:0}
.pick-note-own{color:var(--ink-2);border-left:2px solid var(--rule);padding-left:10px}
.pick-badge{font-family:var(--mono);font-size:9.5px;letter-spacing:.14em;vertical-align:2px;
  border:1px solid var(--rule);border-radius:2px;padding:1px 5px;margin-right:8px;color:var(--ink-3)}
.pick-callout{margin:22px 0 0;padding:14px 16px;background:var(--surface);border-radius:3px}
.pick-callout-head{font-family:var(--mono);font-size:10px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--ink-3);margin:0 0 7px}
.pick-callout-note{margin:0;font-size:14.5px;line-height:1.85}
.pick-callout-bare{font-family:var(--mono);font-size:10px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--ink-3);display:flex;gap:12px;align-items:baseline;flex-wrap:wrap}
.gallery{margin:44px 0 0}
.gallery h2{font-size:16px;margin:0 0 14px}
.gallery-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.gallery .shot{margin:0;background:var(--panel);border:1px solid var(--line);
  border-radius:10px;overflow:hidden}
.gallery .shot img{display:block;width:100%;height:auto;aspect-ratio:4/3;object-fit:cover;
  background:var(--panel)}
.gallery .shot figcaption{padding:8px 10px;font-size:11.5px;line-height:1.6;color:var(--ink-3)}
.gallery-credit{margin:12px 0 0;font-size:11.5px;color:var(--ink-3)}
@media (max-width:520px){.gallery-grid{grid-template-columns:1fr 1fr;gap:8px}}
.pick-callout-bare span{font-family:inherit;font-size:12.5px;letter-spacing:0;text-transform:none}
@media(max-width:520px){.pick{grid-template-columns:72px 1fr}.pick-thumb img{height:48px}}
.lead{margin-bottom:8px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(268px,1fr));
  gap:1px;background:var(--rule);border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}
.card{background:var(--bg);padding:18px 18px 22px}
.card-featured{background:transparent;padding:0 0 22px;border-bottom:1px solid var(--rule);margin-bottom:26px;
  display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.25fr);gap:24px;align-items:start;
  grid-template-rows:auto auto auto}
.card-thumb{display:block;margin:0 0 12px;overflow:hidden;background:var(--surface);
  border:1px solid var(--rule);border-radius:3px}
.card-thumb img{display:block;width:100%;height:124px;object-fit:cover;object-position:left center;
  background:var(--surface);
  transition:transform .55s cubic-bezier(.2,.6,.2,1),opacity .3s}
.card:hover .card-thumb img,.card-featured:hover .card-thumb img{transform:scale(1.03)}
.card-featured .card-thumb{margin:0;grid-column:1;grid-row:1/span 3;align-self:start}
.card-featured .card-thumb img{height:186px}
.card-featured .card-meta{grid-column:2;grid-row:1;margin-top:2px}
.card-featured .card-title{grid-column:2;grid-row:2}
.card-featured .card-excerpt{grid-column:2;grid-row:3}
.card-meta{display:flex;align-items:center;gap:9px;margin:0 0 8px;
  font-family:var(--mono);font-size:10px;letter-spacing:.06em;color:var(--ink-3)}
.card-code{color:var(--cat);font-weight:600;border:1px solid var(--cat);padding:1px 5px;
  border-radius:2px;opacity:.92}
.card-cat{color:var(--ink-2);font-family:var(--sans);font-size:11px;letter-spacing:0;overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.card-read{margin-left:auto}
.card-title{font-family:var(--disp);font-weight:700;font-size:15.5px;line-height:1.55;
  margin:0 0 8px;letter-spacing:-.005em}
.card-featured .card-title{font-size:clamp(18px,1.7vw,23px);line-height:1.46;margin-bottom:9px}
.card-title a{background-image:linear-gradient(var(--cat),var(--cat));background-size:0 1.5px;
  background-position:0 100%;background-repeat:no-repeat;transition:background-size .3s}
.card-title a:hover{background-size:100% 1.5px}
.card-excerpt{margin:0;color:var(--ink-2);font-size:12.5px;line-height:1.78;
  display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.card-featured .card-excerpt{font-size:13px;max-width:40em;line-height:1.8;-webkit-line-clamp:3}

/* ── 記事 ───────────────────────────────────── */
.article-wrap{padding-top:38px}
.article{max-width:var(--measure);margin:0 auto}
.eyebrow-code{font-family:var(--mono);border:1px solid var(--cat);padding:2px 6px;
  border-radius:2px;margin-right:10px}
.article-title{font-family:var(--disp);font-size:clamp(23px,2.9vw,33px);line-height:1.42;
  font-weight:700;margin:0 0 14px;letter-spacing:-.012em}
.article-lede{font-size:15px;color:var(--ink-2);line-height:1.82;margin:0 0 16px}
.article-meta{font-family:var(--mono);font-size:11px;letter-spacing:.08em;color:var(--ink-3);
  display:flex;align-items:center;gap:10px;padding-bottom:20px;border-bottom:1px solid var(--rule);margin:0}
.dot{width:3px;height:3px;border-radius:50%;background:var(--ink-3);display:inline-block}
.article-hero{margin:0 0 30px;border-bottom:1px solid var(--rule)}
.hero-credit{padding:8px 0 10px;color:var(--ink-3);font-family:var(--mono);font-size:11px;letter-spacing:.03em}
.article-hero img{display:block;width:100%;height:auto;max-height:220px;object-fit:cover;object-position:left center}
.prose{font-size:15.5px;line-height:1.9;color:var(--ink)}
.prose h2{font-family:var(--disp);font-size:19px;line-height:1.5;margin:38px 0 14px;font-weight:700;
  letter-spacing:-.01em;padding-top:8px;position:relative}
.prose h2::before{content:"";position:absolute;top:-1px;left:0;width:38px;height:2px;background:var(--cat)}
.prose h3{font-size:15.5px;margin:26px 0 8px;font-weight:700}
.prose p{margin:0 0 18px}
.prose ul,.prose ol{margin:0 0 18px;padding-left:1.3em}
.prose li{margin-bottom:6px}
.prose li::marker{color:var(--cat)}
.prose a{color:var(--cat);border-bottom:1px solid color-mix(in srgb,var(--cat) 40%,transparent)}
.prose a:hover{border-bottom-color:var(--cat)}
.prose strong{font-weight:700;color:var(--ink)}
.prose blockquote{margin:30px 0;padding:2px 0 2px 22px;border-left:2px solid var(--cat);
  color:var(--ink-2);font-size:15.5px}
.prose table{width:100%;border-collapse:collapse;margin:22px 0;font-size:13.5px;
  font-variant-numeric:tabular-nums}
.prose th,.prose td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--rule);vertical-align:top}
.prose thead th{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink-3);font-weight:600;border-bottom:1px solid var(--rule-2)}
.prose td:first-child{color:var(--ink-2);width:34%}
.prose tbody tr:hover{background:var(--raised)}
.prose code{font-family:var(--mono);font-size:.86em;background:var(--raised);padding:2px 7px;
  border-radius:3px;color:var(--cat)}
.prose hr{border:0;border-top:1px solid var(--rule);margin:44px 0}

/* ── 埋め込み・出典 ─────────────────────────── */
.embeds,.sources{margin-top:38px;padding-top:22px;border-top:1px solid var(--rule)}
.embeds-lead{margin:0 0 30px;padding-top:0;border-top:0}
.embeds-lead .embed{margin-bottom:0}
.embeds h2,.sources h2{font-family:var(--mono);font-size:10.5px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--ink-3);margin:0 0 20px;font-weight:600}
.embed{margin:0 0 30px}
.embed figcaption{font-size:13px;color:var(--ink-3);margin-top:11px;line-height:1.75}
.embed-video{background:var(--surface);border:1px solid var(--rule);border-radius:3px;overflow:hidden}
.embed-video iframe{width:100%;aspect-ratio:16/9;border:0;display:block;background:var(--surface)}
.embed-video figcaption{padding:0 2px}
.embed-link a{display:block;padding:22px 24px;border:1px solid var(--rule);border-radius:3px;
  background:var(--surface);transition:border-color .2s,background .2s}
.embed-link a:hover{border-color:var(--cat);background:var(--raised)}
.embed-link-title{display:block;font-family:var(--disp);font-weight:600;font-size:16px;
  line-height:1.6;margin-bottom:8px}
.embed-link-pub{display:block;font-family:var(--mono);font-size:11.5px;color:var(--ink-3);letter-spacing:.04em}
.sources ol{margin:0 0 20px;padding-left:1.3em;font-size:14px;line-height:1.8}
.sources li{margin-bottom:11px}
.sources li::marker{font-family:var(--mono);color:var(--ink-3)}
.sources a{border-bottom:1px solid var(--rule-2)}
.sources a:hover{border-bottom-color:var(--cat)}
.src-pub{font-family:var(--mono);color:var(--ink-3);font-size:11.5px;margin-left:9px}
.sources-note{font-size:12.5px;color:var(--ink-3);line-height:1.85;margin:0}

.ad-notice{max-width:var(--measure);margin:0 0 18px;padding:7px 11px;border:1px solid var(--rule-2);
  border-radius:3px;color:var(--ink-3);font-family:var(--mono);font-size:11px;letter-spacing:.03em}
.alts{max-width:var(--measure);margin:44px 0 0;padding-top:24px;border-top:1px solid var(--rule)}
.alts h2{font-family:var(--mono);font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--ink-2);margin:0 0 16px;display:flex;align-items:center;gap:8px}
.alt-ad{background:var(--rule-2);color:var(--ink-2);padding:2px 6px;border-radius:2px;letter-spacing:.1em}
.alts ul{list-style:none;padding:0;margin:0}
.alt-item{margin:0 0 16px;display:flex;gap:14px;align-items:flex-start}
.alt-thumb{flex:none;display:block;width:64px;height:64px;border-radius:4px;overflow:hidden;
  background:var(--surface);border:1px solid var(--rule)}
.alt-thumb img{width:100%;height:100%;object-fit:contain;display:block}
.alt-text{min-width:0}
.alt-item>a{font-size:15px;line-height:1.6}
.alt-why{margin:4px 0 0;color:var(--ink-2);font-size:13.5px;line-height:1.8}
.faq{max-width:var(--measure);margin:44px 0 0;padding-top:24px;border-top:1px solid var(--rule)}
.faq h2{font-family:var(--mono);font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--ink-3);margin:0 0 18px}
.faq-item{margin:0 0 18px}
.faq-item h3{font-size:15px;margin:0 0 6px;line-height:1.6;display:flex;align-items:baseline;gap:9px}
.faq-q{font-family:var(--mono);font-size:10.5px;font-weight:600;letter-spacing:.05em;
  color:var(--cat);border:1px solid var(--cat);border-radius:2px;padding:1px 6px;
  flex:none;opacity:.9}
.faq-item p{margin:0;color:var(--ink);font-size:14px;line-height:1.85}
.related{max-width:var(--max);margin:56px auto 0}
.related h2{font-family:var(--mono);font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--ink-3);margin:0 0 22px;font-weight:600}
.empty{color:var(--ink-3);padding:60px 0}

/* ── フッター ───────────────────────────────── */
.site-foot{margin-top:64px;border-top:1px solid var(--rule);padding:26px 0 44px}
.foot-board{display:flex;align-items:center;gap:14px;font-family:var(--mono);font-size:11.5px;
  letter-spacing:.1em;padding-bottom:26px;border-bottom:1px solid var(--rule);margin-bottom:26px}
.foot-code{color:var(--ink-3);border:1px solid var(--rule-2);padding:2px 6px;border-radius:2px}
.foot-status{color:var(--accent);font-weight:600}
.foot-status::before{content:"● "}
.foot-tag{font-family:var(--sans);letter-spacing:0;color:var(--ink-2);font-size:13px;margin-left:auto;
  text-align:right}
.foot-cols{display:flex;justify-content:space-between;align-items:baseline;gap:24px;flex-wrap:wrap}
.foot-meta{margin:0;display:flex;gap:22px;font-size:13px}
.foot-meta a{color:var(--ink-2);border-bottom:1px solid transparent;padding-bottom:2px}
.foot-meta a:hover{color:var(--ink);border-bottom-color:var(--accent)}
.foot-copy{font-family:var(--mono);font-size:10.5px;color:var(--ink-3);margin:0;letter-spacing:.06em}

/* ── レスポンシブ ───────────────────────────── */
/* 案内板は狭くなるほど列を落とす。最後まで残すのは KEY と STATUS。
   「何の話か」と「今どうなっているか」が案内板の本体なので。 */
@media (max-width:1100px){
  .board-head,.board-row{grid-template-columns:64px 74px 44px minmax(0,1fr) 150px 20px}
  .b-title,.board-head span:nth-child(5){display:none}
}
@media (max-width:900px){
  .nav-label{display:none}
  .board-head,.board-row{grid-template-columns:74px 44px minmax(0,1fr) 132px 20px}
  .b-flt,.board-head span:nth-child(1){display:none}
}
@media (max-width:620px){
  .board-head,.board-row{grid-template-columns:46px 40px minmax(0,1fr) 104px 16px;gap:10px}
  .b-from span,.st em{display:none}
  .st{letter-spacing:.04em;font-size:10.5px;gap:5px}
}
@media (max-width:820px){
  .card-featured{grid-template-columns:1fr;gap:14px}
  .card-featured .card-thumb{grid-row:auto}
}
@media (max-width:640px){
  .wrap{padding:0 18px}
  .hero{padding:52px 0 34px}
  .board{margin-bottom:48px}
  .article-wrap{padding-top:38px}
  .grid{grid-template-columns:1fr}
  .card-featured .card-thumb img{height:170px}
  .card-thumb img{height:150px}
  .foot-tag{margin-left:0;text-align:left;width:100%}
  .foot-board{flex-wrap:wrap}
}

/* ── 特集ページ ───────────────────────────────────────────── */
.nav-ft{--cat:#5fb0d9}
.feature-intro{max-width:70ch;margin:0 auto 40px}
.fp-updated{margin:14px 0 0;font-size:.78rem;color:var(--ink-3);
  font-family:var(--mono,ui-monospace,monospace);letter-spacing:.06em}

/* 特集の製品セクション。横並びのカードではなく、上から読む記事として組む */
.fp-list{max-width:760px;margin:0 auto 56px}
.fp{padding:0 0 44px;margin-bottom:44px;border-bottom:1px solid var(--rule)}
.fp:last-child{border-bottom:0;margin-bottom:0}
.fp-head{position:relative;margin-bottom:20px}
.fp-kicker{margin:0 0 6px;display:flex;align-items:center;gap:10px;
  font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3)}
.fp-no{color:var(--accent);font-weight:700;font-family:var(--mono,ui-monospace,monospace)}
.fp-brand{color:var(--ink-3)}
.fp-name{margin:0 0 10px;font-size:1.5rem;line-height:1.35;letter-spacing:.01em}
.fp-badge{display:inline-block;font-size:.72rem;letter-spacing:.06em;padding:4px 10px;border-radius:2px}
.fp-badge-ok{background:rgba(63,158,106,.14);color:#6cc492;border:1px solid rgba(63,158,106,.35)}
.fp-badge-warn{background:rgba(217,160,63,.14);color:#e0b054;border:1px solid rgba(217,160,63,.35)}
.fp-badge-bad{background:rgba(200,80,60,.14);color:#e0806c;border:1px solid rgba(200,80,60,.35)}
.fp-shot{margin:0 0 22px;position:relative;border-radius:3px;overflow:hidden;background:var(--raised)}
.fp-shot img{width:100%;height:auto;display:block}
.fp-credit{position:absolute;right:0;bottom:0;font-size:.64rem;color:var(--ink-2);
  background:rgba(11,13,16,.82);padding:4px 9px;letter-spacing:.02em}
.fp-body{margin-bottom:24px}
.fp-body p{margin:0 0 1.1em;line-height:2;font-size:1rem;color:var(--ink-2)}
.fp-body p:last-child{margin-bottom:0}
.fp-body strong{color:var(--ink);font-weight:600}
.fp-meta{display:grid;grid-template-columns:auto 1fr;gap:10px 18px;margin:0 0 20px;
  font-size:.88rem;background:var(--surface);border:1px solid var(--rule);
  border-left:3px solid var(--rule-2);border-radius:3px;padding:18px 20px}
.fp-ok .fp-meta{border-left-color:#3f9e6a}
.fp-warn .fp-meta{border-left-color:#d9a03f}
.fp-bad .fp-meta{border-left-color:#c8503c}
.fp-meta dt{color:var(--ink-3);white-space:nowrap}
.fp-meta dd{margin:0;color:var(--ink-2);line-height:1.85}
.fp-links{margin:0;display:flex;gap:18px;flex-wrap:wrap;font-size:.86rem}
.fp-buy{color:var(--accent);font-weight:600}
.fp-src{color:var(--ink-3)}
@media(max-width:560px){
  .fp-name{font-size:1.28rem}
  .fp-meta{grid-template-columns:1fr;gap:4px 0}
  .fp-meta dt{margin-top:8px}
}

.fx{background:var(--surface);border:1px solid var(--rule);border-radius:3px;padding:22px 24px;margin-bottom:52px}
.fx-head{margin:0 0 8px;font-size:1rem}
.fx-lead{margin:0 0 14px;font-size:.86rem;color:var(--ink-3);line-height:1.8}
.fx-list{margin:0;padding-left:1.1em;font-size:.88rem;line-height:1.9;color:var(--ink-2)}
.fx-list li{margin-bottom:8px}
.fx-list strong{color:var(--ink)}

.fr-head{font-size:1rem;margin:0 0 16px}

.fi-grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}
.fi{display:block;background:var(--surface);border:1px solid var(--rule);border-radius:3px;
  padding:22px 24px;text-decoration:none;transition:border-color .15s}
.fi:hover{border-color:var(--accent)}
.fi-eyebrow{margin:0 0 6px;font-size:.7rem;letter-spacing:.14em;color:var(--ink-3)}
.fi-title{margin:0 0 8px;font-size:1.12rem;line-height:1.4;color:var(--ink)}
.fi-lede{margin:0 0 12px;font-size:.86rem;line-height:1.8;color:var(--ink-2)}
.fi-count{margin:0;font-size:.74rem;color:var(--accent);letter-spacing:.06em}

@media(max-width:520px){
  .fi-grid{grid-template-columns:1fr}
}
"""


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#fbfaf8"/>
  <circle cx="32" cy="32" r="7" fill="#b4472b"/>
  <circle cx="32" cy="32" r="15" fill="none" stroke="#b4472b" stroke-width="3" stroke-opacity=".55"/>
  <circle cx="32" cy="32" r="23" fill="none" stroke="#b4472b" stroke-width="3" stroke-opacity=".25"/>
</svg>
"""


# ────────────────────────────── メイン ──────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--serve", action="store_true")
    args = ap.parse_args()

    site = load_site()

    global BASE_PATH
    from urllib.parse import urlparse
    BASE_PATH = urlparse(site["site"]["base_url"]).path.rstrip("/")
    print(f"■ base_path: {BASE_PATH or '(ルート直下)'}")

    posts = [p for p in (parse_post(f) for f in sorted(POSTS_DIR.glob("*.md"))) if p]
    features = []
    if FEATURES_DIR.exists():
        features = [f for f in (parse_feature(x)
                                for x in sorted(FEATURES_DIR.glob("*.md"))) if f]
        features.sort(key=lambda f: str(f.get("updated") or ""), reverse=True)
    # 日付 → priority（front matter で 1 以上を指定するとその日の先頭に来る）→ slug
    posts.sort(key=lambda p: (p["date"], p.get("priority", 0), p["slug"]), reverse=True)
    # 便名は掲載が古い順の通し番号。既存記事の番号がずれないよう昇順で振る。
    for n, q in enumerate(sorted(posts, key=lambda x: (x["date"], x["slug"])), start=1):
        q["flight"] = f"GT {n:04d}"
    print(f"■ 記事 {len(posts)}本")
    long_titles = [p for p in posts if len(p.get("seo_title") or p["title"]) > 34]
    if long_titles:
        print(f"! 検索用タイトルが長い記事 {len(long_titles)}本 "
              f"(Google は全角32字前後で切る。front matter に seo_title を足すと直る)")
        for p_ in long_titles[:3]:
            print(f"    {len(p_.get('seo_title') or p_['title'])}字 {p_['slug']}")

    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    (PUBLIC / "posts").mkdir(parents=True)
    (PUBLIC / "category").mkdir(parents=True)
    (PUBLIC / "assets").mkdir(parents=True)

    (PUBLIC / "assets" / "style.css").write_text(CSS, encoding="utf-8")
    (PUBLIC / "assets" / "favicon.svg").write_text(FAVICON, encoding="utf-8")

    # OGP画像（フォントが無い環境では静かにスキップ）
    if ogp is not None:
        made = 0
        for p in posts:
            cat = site["categories"].get(p.get("category"), {"label": "その他"})
            if ogp.render(p["title"], cat["label"], s_title := site["site"]["title"],
                          PUBLIC / "ogp" / f"{p['slug']}.png"):
                made += 1
        ogp.render(site["site"]["tagline"], site["site"]["title"].upper(), site["site"]["title"],
                   PUBLIC / "ogp" / "default.png")

        cards = 0
        for p in posts:
            key = p.get("category")
            cat = site["categories"].get(key, {"label": "その他"})
            word = p.get("keyword") or cat["label"]
            if ogp.render_card(word, cat["label"], key or "", site["site"]["title"],
                               p["slug"], PUBLIC / "cards" / f"{p['slug']}.png"):
                cards += 1
        print(f"■ OGP画像 {made}枚 / アイキャッチ {cards}枚" if made
              else "■ 画像生成: フォントが無いためスキップ")

    # 実物画像の充足率。ガジェット記事は実物が見えないと成立しないため必ず出す。
    shots = sum(len(p.get("images") or []) for p in posts)
    naked = [p["slug"] for p in posts
             if not (p.get("images")
                     or any((e.get("type") or "").lower() == "youtube"
                            for e in (p.get("embeds") or [])))]
    print(f"■ 実物画像 {shots}枚 / 画像も動画も無い記事 {len(naked)}本")
    for slug in naked:
        print(f"  ! 画像なし: {slug}")
    # ページ送り。site.yaml の posts_per_page 件ずつに切る（1ページ目は先頭記事を含む）。
    per_page = int(site["site"].get("posts_per_page") or 20)
    pages = [posts[i:i + per_page] for i in range(0, len(posts), per_page)] or [[]]
    total_pages = len(pages)
    for n, chunk in enumerate(pages, start=1):
        out = PUBLIC / page_path(n)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_index(site, chunk, n, total_pages, all_posts=posts),
                       encoding="utf-8")
    if total_pages > 1:
        print(f"■ ページ送り {total_pages}ページ ({per_page}件/ページ)")
    (PUBLIC / "about.html").write_text(render_about(site), encoding="utf-8")
    (PUBLIC / "jpn.html").write_text(render_domestic_cf(site, posts), encoding="utf-8")
    (PUBLIC / "features.html").write_text(render_features_index(site, features),
                                          encoding="utf-8")
    if features:
        (PUBLIC / "features").mkdir(parents=True, exist_ok=True)
        for f in features:
            (PUBLIC / f["path"]).write_text(render_feature(site, f, posts),
                                            encoding="utf-8")
        # 入手性の判定が抜けている製品はビルド時に見えるようにする。
        # 判定こそが特集ページの存在理由なので、黙って通してはいけない。
        bad = [(f["slug"], x.get("name"), "入手性の判定なし")
               for f in features for x in f["products"]
               if str(x.get("availability") or "") not in AVAIL_STYLE]
        # ガジェットは写真が命。写真の無い製品カードは公開しない。
        bad += [(f["slug"], x.get("name"), "写真なし")
                for f in features for x in f["products"]
                if not str(x.get("image") or "").strip()]
        print(f"■ 特集 {len(features)}本 / 掲載製品 "
              f"{sum(len(f['products']) for f in features)}件")
        for slug, name, why in bad:
            print(f"  ! {why}: {slug} / {name}")
    (PUBLIC / "privacy.html").write_text(render_privacy(site), encoding="utf-8")
    for p in posts:
        (PUBLIC / p["path"]).write_text(render_post(site, p, posts), encoding="utf-8")
    for key, cat in site["categories"].items():
        (PUBLIC / "category" / f"{cat['slug']}.html").write_text(
            render_category(site, key, cat, posts), encoding="utf-8")
    (PUBLIC / "feed.xml").write_text(render_feed(site, posts), encoding="utf-8")
    (PUBLIC / "sitemap.xml").write_text(render_sitemap(site, posts, features), encoding="utf-8")
    # ads.txt。AdSense が「この発行者にこのサイトの広告枠を売る権限がある」
    # ことを確認するためのファイル。無いと収益が出ない場合がある。
    # 発行IDを入れるまでは作らない（空のファイルを置くと逆に警告される）。
    _cid = str(site["site"].get("adsense_client") or "").strip()
    if _cid:
        pub = _cid.replace("ca-pub-", "pub-")
        (PUBLIC / "ads.txt").write_text(
            f"google.com, {pub}, DIRECT, f08c47fec0942fa0" + chr(10), encoding="utf-8")
        print(f"■ ads.txt: {pub}")

    (PUBLIC / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {site['site']['base_url'].rstrip('/')}/sitemap.xml\n",
        encoding="utf-8")
    (PUBLIC / ".nojekyll").write_text("", encoding="utf-8")

    # IndexNow の所有者確認ファイル。ルートに <key>.txt を置き、中身はキーそのもの。
    # これが無いと通知が 403 で弾かれる。
    key_file = ROOT / ".indexnow-key"
    if key_file.exists():
        k = key_file.read_text(encoding="ascii").strip()
        if k:
            (PUBLIC / f"{k}.txt").write_text(k, encoding="ascii")
            print(f"■ IndexNow キーファイル: {k}.txt")

    # 独自ドメイン用の CNAME。base_url のホスト名から自動生成する。
    # GitHub Pages はこのファイルを見て独自ドメインを認識するため、
    # 成果物に必ず含める必要がある（無いと設定がリセットされる）。
    from urllib.parse import urlparse as _up
    host = _up(site["site"]["base_url"]).netloc
    if host and not host.endswith("github.io"):
        (PUBLIC / "CNAME").write_text(host + "\n", encoding="utf-8")
        print(f"■ CNAME: {host}")

    print(f"■ 出力 public/ ({len(list(PUBLIC.rglob('*.html')))} ページ)")

    if args.serve:
        import http.server, socketserver, os
        os.chdir(PUBLIC)
        with socketserver.TCPServer(("", 8000), http.server.SimpleHTTPRequestHandler) as httpd:
            print("http://localhost:8000 で確認できます (Ctrl+C で停止)")
            httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
