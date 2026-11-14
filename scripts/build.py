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
import urllib.request
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
CLIPS = ROOT / "content" / "clips"  # 記事の動く映像(add_clips.py が置く)。public/clips に写す
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


GITEKI_FEATURE_SLUG = "giteki"


def link_giteki(body_html: str) -> str:
    """記事本文の最初の「技適」を、技適の特集ページへのリンクにする。

    技適の説明ページへ記事から入れるように。2026-10-11 本人了承。
    毎朝の記事生成の指示は変えず、ビルドで自動で付ける（過去記事にも効く）。
    リンクするのは <p>/<li> の本文中の最初の1か所だけ。見出し・既存リンク・
    コード・タグの属性の中には入れない。本文が特集ページへのリンクを既に持つなら何もしない。
    """
    if not (FEATURES_DIR / f"{GITEKI_FEATURE_SLUG}.md").exists():
        return body_html
    href = u(f"features/{GITEKI_FEATURE_SLUG}.html")
    if href in body_html or "技適" not in body_html:
        return body_html

    block = {"p", "li"}                                   # ここの中だけ対象
    skip = {"a", "h1", "h2", "h3", "h4", "h5", "h6", "code", "pre", "script", "style"}
    depth = {t: 0 for t in block | skip}
    parts = re.split(r"(<!--.*?-->|<[^>]+>)", body_html, flags=re.S)
    for i, part in enumerate(parts):
        if part.startswith("<!--"):
            continue
        tag = re.match(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)", part)
        if tag:
            name = tag.group(2).lower()
            if name in depth and not part.endswith("/>"):
                depth[name] = max(0, depth[name] + (-1 if tag.group(1) else 1))
            continue
        if part.startswith("<") or "技適" not in part:
            continue
        if sum(depth[t] for t in block) > 0 and sum(depth[t] for t in skip) == 0:
            parts[i] = part.replace("技適", f'<a href="{href}">技適</a>', 1)
            break
    return "".join(parts)


GITEKI_STATUSES = ("取得済み", "確認できない", "対象外")


def norm_giteki(raw, fname: str = "") -> dict | None:
    """front matter の giteki を正規化する。未記入・不正な値は None（一覧に載せない）。

    status は取得済み / 確認できない / 対象外 の3つだけ。「確認できない」は
    「取得していない」とは別物（型番が非公開・申請時の表記と違う等で引けない場合を含む）。
    number は文字列のリストに揃える。checked は YAML の日付型でも文字列に直す。
    """
    if raw in (None, "", {}):
        return None
    if not isinstance(raw, dict):
        print(f"  ! giteki の形式が不正（無視します）: {fname}")
        return None
    status = str(raw.get("status") or "").strip()
    if status not in GITEKI_STATUSES:
        print(f"  ! giteki.status が不正「{status}」（無視します）: {fname}")
        return None
    nums = raw.get("number")
    if nums is None or nums == "":
        nums = []
    elif not isinstance(nums, (list, tuple)):
        nums = [nums]
    nums = [str(n).strip() for n in nums if str(n).strip()]
    return {"status": status, "number": nums,
            "checked": str(raw.get("checked") or "").strip(),
            "radio": str(raw.get("radio") or "").strip(),
            "note": str(raw.get("note") or "").strip(),
            # found: 公開後の再確認(scripts/giteki_recheck.py)で取得を見つけた日。
            #        「公開時点では確認できなかったが、後から登録された」ことの印。
            # maker: 総務省DBの登録者名を引くときのブランド名(任意。giteki_makers.yaml のキー)
            "found": str(raw.get("found") or "").strip(),
            "maker": str(raw.get("maker") or "").strip()}


# ────────────────────────────── 価格表の円の目安 ──────────────────────────────
# 検索は「製品名 価格」が多い(2026-10-27 Search Console)ので、本文の表の価格に円の目安を添える
# (本人判断)。記事には円を書かず、ビルドのたびにその日のレートで計算する。為替で古くならないように。
# 取れなかったときは前回の data/fx.json を使い、それも無ければ何も足さない。
FX_CACHE = ROOT / "data" / "fx.json"
FX_URL = "https://open.er-api.com/v6/latest/JPY"
FX_UNITS = {"米ドル": "USD", "ドル": "USD", "USD": "USD", "US$": "USD", "$": "USD",
            "ユーロ": "EUR", "EUR": "EUR", "€": "EUR", "ポンド": "GBP", "GBP": "GBP", "£": "GBP",
            "元": "CNY", "人民元": "CNY", "CNY": "CNY", "RMB": "CNY", "ルピー": "INR"}
# 米ドル以外の「ドル」(香港ドル391ドル のように後ろが単に「ドル」になる)が混じる欄は、取り違えるので触らない
FX_OTHER_DOLLAR = re.compile(r"(香港|HK|カナダ|台湾|NT|豪|オーストラリア|シンガポール|ニュージーランド)\s*ドル")
FX_AMOUNT = re.compile(
    r"(?P<pre>(?<![予節契集要制規条公])約\s*)?(?:"  # 「予約134ドル」の約は換算の約ではない
    r"(?P<u1>US\$|\$|€|£|CNY|RMB|USD|EUR|GBP)\s?(?P<a1>\d{1,3}(?:,\d{3})+|\d+)(?:\.(?P<d1>\d+))?(?P<m1>万)?"
    r"|(?P<a2>\d{1,3}(?:,\d{3})+|\d+)(?:\.(?P<d2>\d+))?(?P<m2>万)?\s*"
    r"(?P<u2>米ドル|ドル|ユーロ|ポンド|人民元|元|ルピー|USD|EUR|GBP|CNY))")
_FX: dict | None = None


def fx_rates() -> dict:
    """{'date': 'YYYY-MM-DD', 'jpy': {'USD': 1ドルあたりの円, ...}}。取れなければ {}"""
    global _FX
    if _FX is not None:
        return _FX
    try:
        with urllib.request.urlopen(FX_URL, timeout=15) as r:
            d = json.loads(r.read())
        per_jpy = d["rates"]
        day = datetime.fromtimestamp(int(d["time_last_update_unix"]), JST).strftime("%Y-%m-%d")
        _FX = {"date": day, "jpy": {c: round(1 / per_jpy[c], 4) for c in set(FX_UNITS.values())}}
        FX_CACHE.write_text(json.dumps(_FX, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    except Exception as e:
        _FX = json.loads(FX_CACHE.read_text(encoding="utf-8")) if FX_CACHE.exists() else {}
        print(f"  ! 為替レートを取れませんでした({type(e).__name__})。"
              + (f"{_FX['date']} の値を使います" if _FX else "円の目安は出しません"))
    return _FX


def yen_label(v: float) -> str:
    if v < 10000:
        return f"約{round(v, -2):,.0f}円"
    if v < 100000:
        return f"約{v / 10000:.1f}万円".replace(".0万", "万")
    return f"約{round(v / 10000):,}万円"


def add_yen_cell(cell: str, jpy: dict) -> tuple[str, bool]:
    if FX_OTHER_DOLLAR.search(cell):
        return cell, False
    done = False

    def rep(m: re.Match) -> str:
        nonlocal done
        g = m.groupdict()
        unit = g["u1"] or g["u2"]
        n_int, n_dec, man = (g["a1"], g["d1"], g["m1"]) if g["u1"] else (g["a2"], g["d2"], g["m2"])
        # 「CNY 9,999(約1,482ドル)」の後ろのような、すでに換算された「約」の金額には付けない
        if done and g["pre"]:
            return m.group(0)
        v = float(n_int.replace(",", "") + (f".{n_dec}" if n_dec else "")) * (10000 if man else 1)
        rate = jpy.get(FX_UNITS[unit])
        if not rate or v <= 0:
            return m.group(0)
        done = True
        return f'{m.group(0)}<span class="fx-jpy">（{yen_label(v * rate)}）</span>'

    out = FX_AMOUNT.sub(rep, cell)
    return out, done


def add_yen_to_tables(body_html: str) -> str:
    fx = fx_rates()
    if not fx:
        return body_html

    def table(m: re.Match) -> str:
        t = m.group(0)
        heads = re.findall(r"<th[^>]*>(.*?)</th>", (re.search(r"<thead>.*?</thead>", t, re.S) or [""])[0], re.S)
        price_cols = {i for i, h in enumerate(heads) if "価格" in h}
        hit = False

        def row(rm: re.Match) -> str:
            nonlocal hit
            cells = re.findall(r"(<td[^>]*>)(.*?)(</td>)", rm.group(0), re.S)
            if not cells:
                return rm.group(0)
            label = re.sub(r"<[^>]+>", "", cells[0][1])
            if "価格" in label and not re.search(r"調達|目標|支援額", label):
                targets = set(range(1, len(cells)))
            else:
                targets = price_cols - {0}
            if not targets:
                return rm.group(0)
            new = []
            for i, (o, c, e) in enumerate(cells):
                if i in targets:
                    c, did = add_yen_cell(c, fx["jpy"])
                    hit |= did
                new.append(o + c + e)
            return re.sub(r"<td.*</td>", lambda _: "".join(new), rm.group(0), count=1, flags=re.S)

        t = re.sub(r"<tr>.*?</tr>", row, t, flags=re.S)
        if hit:
            y, mth, d = fx["date"].split("-")
            t += (f'<p class="fx-note">円は{int(y)}年{int(mth)}月{int(d)}日の為替レートで計算した目安です。'
                  '送料・関税・消費税は含みません。</p>')
        return t

    return re.sub(r"<table>.*?</table>", table, body_html, flags=re.S)


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
    meta["body_html"] = add_yen_to_tables(link_giteki(MD.convert(body_md)))
    meta["slug"] = meta.get("slug") or path.stem
    meta["date"] = str(meta.get("date", datetime.now(JST).strftime("%Y-%m-%d")))
    # 更新日。日本上陸の続報を書き足したら、その確認日を更新日として扱う
    # （構造化データの dateModified と sitemap の lastmod に効き、再クロールを促す）。
    _gk_found = str(meta["giteki"].get("found") or "") if isinstance(meta.get("giteki"), dict) else ""
    meta["modified"] = max(str(meta.get("modified") or ""),
                           str((meta.get("japan") or {}).get("checked") or ""),
                           _gk_found) or ""
    meta["reading_min"] = max(1, round(len(body_md) / 500))
    meta["path"] = f"posts/{meta['slug']}.html"
    meta.setdefault("tags", [])
    meta["name_short"] = str(meta.get("keyword") or "").strip()   # 技適一覧の製品名。tags 由来の代用はしない
    meta["giteki"] = norm_giteki(meta.get("giteki"), path.name)
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
    # 動く映像(2026-11-04 本人了承)。メーカー公式 YouTube 動画の3秒・音なしの切り出しだけを
    # content/clips/<slug>/ に置き、写真の位置で自動再生・くり返しで見せる。足すのは scripts/add_clips.py。
    # 「画像を自社サーバーに置かない」の唯一の例外。ファイルが無い行は黙って飛ばす
    clips = []
    for it in (meta.get("clips") or []):
        f = str((it or {}).get("file") or "").strip()
        if f and (CLIPS / f).exists():
            clips.append({"file": f,
                          "poster": f[:-4] + ".jpg" if (CLIPS / (f[:-4] + ".jpg")).exists() else "",
                          "caption": str(it.get("caption") or "").strip(),
                          "credit": str(it.get("credit") or "").strip(),
                          "source": str(it.get("source") or "").strip()})
    meta["clips"] = clips
    # 検索結果の説明文・RSS・構造化データに使う。本文の書き出しは「日本から見ると」の
    # 注意書きを含みやすいので、要点を書いた kicker を優先する(2026-09-30)。
    meta.setdefault("excerpt", str(meta.get("kicker") or "").strip()
                    or re.sub(r"<[^>]+>", "", meta["body_html"])[:110].strip() + "…")
    return meta


# ────────────────────────────── テンプレート ──────────────────────────────
# merchant が指すストアのドメイン。ここに無いものはアフィリエイト変換しない。
MERCHANT_HOSTS = {
    "amazon": ("amazon.co.jp",),
    "rakuten": ("rakuten.co.jp",),
    "yahoo": ("yahoo.co.jp", "paypaymall.yahoo.co.jp"),
    # A8.net 経由のメーカー日本公式ストア(2026-11-07 提携)。テンプレートは site.yaml の
    # affiliate.a8.<a8_ を除いた名前>。もしもに無いメーカー直販だけをここに置く
    "a8_minisforum": ("minisforum.jp",),
    "a8_gmktec": ("jp.gmktec.com",),
    "a8_huawei": ("consumer.huawei.com",),
    "a8_switchbot": ("switchbot.jp",),
    # 商品ページへのリンクが作れず、トップページ行きだけ(site.yaml のテンプレートに {url} が無い)
    "a8_earfun": ("myearfun.com",),
}
# 同じドメインに海外向けのページもある店は、日本向けのパスだけを変換する
# (A8 は広告主が決めた飛び先の外へのリンクを提携解除の理由にしている)
MERCHANT_PATHS = {
    "a8_huawei": "/jp/",
}

# 海外メーカー直販（front matter の buy）。国内ECの MERCHANT_HOSTS とは
# 別に持つ。こちらは「この製品そのものを本国から買う」導線で、
# alternatives（今すぐ国内で買える別の製品）とは役割が違う。
DIRECT_MERCHANTS = {
    "minisforum": (("store.minisforum.com", "minisforum.com"), "Minisforum 公式ストア"),
    "aliexpress": (("aliexpress.com", "ja.aliexpress.com"), "AliExpress"),
}

# buy に必須の技適判定。**自由記述にしない。**
# 無線を積んだ製品を技適の確認なしに買わせるのは、この媒体が
# 掲げている判断そのものを裏切る。機械が読める値にして、
# 判定を書かなければ購入リンクが出ないところまでコードで強制する。
#
# 「未取得」を買わせない選択も検討したが、採らなかった。技適が無くても
# 所持と有線での使用は合法で、ミニPCのように有線だけで完結する製品は
# 実際に成立するため。読者が判断できる材料を出したうえで選ばせる。
# **判定が付けられない（未確認）なら buy ごと書かない。** それが唯一の禁止。
GITEKI_BUY = {
    "取得済み": ("技適取得済み", "ok", ""),
    "対象外": ("技適の対象外", "na", ""),
    "未取得": ("技適未取得", "warn",
             "国内で Wi-Fi や Bluetooth をオンにすると電波法違反になります。"
             "有線接続だけで使う前提なら購入できます。"),
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
    path = MERCHANT_PATHS.get(merchant)
    if path and not urlparse(url).path.startswith(path):
        print(f"! merchant={merchant} は {path} の下だけが対象。素のリンクにする: {url}")
        return url, False
    if merchant.startswith("a8_"):
        tmpl = str((aff.get("a8") or {}).get(merchant[3:]) or "").strip()
        if tmpl and "{url}" not in tmpl:
            # A8 で商品ページへのリンクが作れない店(EarFun など)。広告主が決めたトップページ行き
            return tmpl, True
    else:
        tmpl = str(aff.get(f"moshimo_{merchant}") or "").strip()
    if not tmpl or "{url}" not in tmpl:
        # ここを黙って素通ししていたせいで、merchant: amazon の記事が20本たまるまで
        # 誰も収益ゼロに気づけなかった（2026-08-16〜28）。未提携のストアを指定して
        # いるのは書き手の誤りなので、ビルドのたびに必ず見えるようにする。
        print(f"! merchant={merchant} は moshimo_{merchant} が未設定。"
              f"素のリンクになり報酬は発生しない: {url}")
        return url, False
    return tmpl.replace("{url}", quote(url, safe="")), True


def alt_store(url: str, merchant: str) -> str:
    """おすすめ欄のボタンに出す店の名前。国内の大手は JAPAN_STORES、A8 のメーカー直販は「公式ストア」。"""
    name = japan_store(url)
    if name != "販売ページ":
        return name
    # 残りはメーカーの公式サイト・公式ストア(Apple・Google・Keychron など)
    return "公式ストア" if merchant.startswith("a8_") else "公式サイト"


def _alt_items_section(s: dict, items: list, heading: str, cls: str) -> tuple[str, bool]:
    """alternatives と gear が共有する、サムネ付きの商品リスト。"""
    items = [x for x in items if x.get("name") and x.get("url")]
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
               f'target="_blank"><img src="{html.escape(str(x["image"]))}" alt="{html.escape(str(x["name"]))}" loading="lazy"></a>'
               if x.get("image") else "")
        # 押す先のボタン。店の名前は URL から決める(書き手に書かせると揺れる)
        cta = (f'<a class="alt-cta" href="{html.escape(link)}" rel="nofollow sponsored noopener" '
               f'target="_blank">{html.escape(alt_store(str(x["url"]), str(x.get("merchant") or "")))}で見る '
               f'<span aria-hidden="true">↗</span></a>')
        rows.append(
            f'<li class="alt-item">{img}<div class="alt-text">'
            f'<a href="{html.escape(link)}" rel="nofollow sponsored noopener" '
            f'target="_blank">{html.escape(str(x["name"]))}</a>{why}{cta}</div></li>')
    label = ('<span class="alt-ad">広告</span>' if has_aff else "")
    return (f'<section class="{cls}"><h2>{heading}{label}</h2>'
            f'<ul>{"".join(rows)}</ul></section>', has_aff)


def alternatives_section(s: dict, p: dict) -> tuple[str, bool]:
    """「今すぐ買えるオススメガジェット」セクション。

    クラファン案件は出荷が先で技適も未取得のことが多い。読者が実際に取れる行動を
    示すのが本来の目的で、アフィリエイトはその副産物として置く。
    リンクが無効でもセクション自体は出す（編集上の価値はリンクと無関係のため）。
    戻り値: (HTML, アフィリエイトリンクを含むか)
    """
    return _alt_items_section(s, p.get("alternatives") or [],
                              "今すぐ買えるオススメガジェット", "alts")


def gear_section(s: dict, p: dict) -> tuple[str, bool]:
    """「一緒に使えるもの」セクション（front matter の gear）。

    その製品を使う人が実際に一緒に買う周辺機器・消耗品。alternatives（別の製品）とは
    役割が違い、製品そのものも alternatives と同じものも入れない。
    戻り値: (HTML, アフィリエイトリンクを含むか)
    """
    return _alt_items_section(s, p.get("gear") or [], "一緒に使えるもの", "alts gear")


def direct_url(s: dict, url: str, merchant: str) -> tuple[str, bool]:
    """海外直販のURLをアフィリエイトリンクに変換する。

    仕組みは affiliate_url と同じで、参照する設定だけが違う
    （もしも経由ではなく各社のプログラムに直接申し込むため、
    site.yaml の affiliate.direct に merchant ごとのテンプレートを置く）。
    戻り値: (URL, アフィリエイトリンクか)
    """
    aff = s.get("affiliate") or {}
    if not aff.get("enabled"):
        return url, False
    entry = DIRECT_MERCHANTS.get(merchant)
    if not entry:
        return url, False
    hosts, _ = entry
    host = urlparse(url).netloc.lower()
    if not any(host == h or host.endswith("." + h) for h in hosts):
        print(f"! merchant={merchant} だが URL のドメインは {host}。"
              f"アフィリエイト変換せず素のリンクにする")
        return url, False
    tmpl = str((aff.get("direct") or {}).get(merchant) or "").strip()
    if not tmpl or "{url}" not in tmpl:
        print(f"! merchant={merchant} は affiliate.direct.{merchant} が未設定。"
              f"素のリンクになり報酬は発生しない: {url}")
        return url, False
    return tmpl.replace("{url}", quote(url, safe="")), True


def buy_section(s: dict, p: dict) -> tuple[str, bool]:
    """「本国から直接買う」セクション。

    **この媒体の記事の多くは国内に流通していない製品を扱う。** そのため
    alternatives（今すぐ国内で買える別の製品）だけでは、肝心の
    「その製品自体をどう買うか」に答えられない記事が大半になる。

    ただし買わせる以上、技適の判定を省略できない。giteki が
    GITEKI_BUY に無い値（未確認を含む）の項目は**リンクごと出さない。**
    確認できていない無線機を買わせて、届いてから使えないと分かるのが
    読者にとって最悪の結果であり、それを避けることがこの媒体の存在理由。
    戻り値: (HTML, アフィリエイトリンクを含むか)
    """
    items = [x for x in (p.get("buy") or []) if x.get("url")]
    if not items:
        return "", False
    has_aff = False
    rows = []
    for x in items:
        giteki = str(x.get("giteki") or "").strip()
        if giteki not in GITEKI_BUY:
            print(f"! buy: {x.get('name') or x['url']} は giteki が "
                  f"{giteki or '未記入'}。購入リンクを出さずに飛ばす"
                  f"（使える値: {' / '.join(GITEKI_BUY)}）")
            continue

        merchant = str(x.get("merchant") or "").strip()
        link, is_aff = direct_url(s, str(x["url"]), merchant)
        has_aff = has_aff or is_aff
        # 店名は merchant から引く。書き手に書かせると表記が揺れる。
        store = DIRECT_MERCHANTS.get(merchant, (None, ""))[1] or str(x.get("store") or "販売ページ")
        gi_label, gi_kind, gi_warn = GITEKI_BUY[giteki]
        price = (f'<span class="buy-price">{html.escape(str(x["price"]))}</span>'
                 if x.get("price") else "")
        note = f'<p class="buy-note">{html.escape(str(x["note"]))}</p>' if x.get("note") else ""
        ship = ('<span class="buy-ship">日本へ発送</span>' if x.get("ships_jp") else "")
        # 技適未取得の警告は書き手に任せない。買う導線の中に必ず出す。
        warn = f'<p class="buy-warn">{html.escape(gi_warn)}</p>' if gi_warn else ""
        rows.append(
            f'<li class="buy-item">'
            f'<a href="{html.escape(link)}" rel="nofollow sponsored noopener" target="_blank">'
            f'{html.escape(store)}</a>'
            f'<p class="buy-meta">{price}{ship}'
            f'<span class="buy-giteki gi-{gi_kind}">{gi_label}</span></p>{warn}{note}</li>')
    if not rows:
        return "", False
    label = ('<span class="alt-ad">広告</span>' if has_aff else "")
    return (f'<section class="alts buys"><h2>本国から直接買う{label}</h2>'
            f'<ul>{"".join(rows)}</ul>'
            f'<p class="buy-caution">海外からの個人輸入になります。関税・送料・'
            f'保証の扱いは販売ページで確認してください。</p></section>', has_aff)


# 日本上陸の続報（front matter の japan）で、購入先の店名を URL から決める。
# 書き手に書かせると表記が揺れるため、buy の DIRECT_MERCHANTS と同じ考え方。
JAPAN_STORES = (
    (("amazon.co.jp",), "Amazon.co.jp"),
    (("rakuten.co.jp",), "楽天市場"),
    (("yahoo.co.jp",), "Yahoo!ショッピング"),
    (("makuake.com",), "Makuake"),
    (("greenfunding.jp",), "GREEN FUNDING"),
    (("camp-fire.jp",), "CAMPFIRE"),
    (("kibidango.com",), "kibidango"),
)

# 状況は選択式。自由記述にすると「発売」「販売開始」「上陸」が混ざり、
# 読者にも自動の見回り(scripts/followup.py)にも読めなくなる。
JAPAN_STATUS = ("発売済み", "予約受付中", "クラウドファンディング中", "発売予定")
# このうち「お金を払える」状態。日本上陸アラート(alert/)はここに入った時に1通送る。
# 「発売予定」は発表だけなので送らない(買えるようになった時に送る)
JAPAN_LANDED = ("発売済み", "予約受付中", "クラウドファンディング中")


def is_landed(p: dict) -> bool:
    return str((p.get("japan") or {}).get("status") or "").strip() in JAPAN_LANDED


# 公開したあとで日本上陸が確認できた記事の数。main() が数えて、登録欄の1行に出す。
# 「今は買えない」で終わらせず、先に書いた製品が実際に後から来ていることを自分の記録で示す
# (2026-11-01 本人「将来の日本発売に期待が持てそうな表現に」)
LANDED_AFTER = [0]


def count_landed_after(posts: list[dict]) -> int:
    return sum(1 for p in posts
               if is_landed(p) and str((p.get("japan") or {}).get("checked") or "") > str(p["date"]))


def alert_form(s: dict, p: dict) -> str:
    """「日本上陸アラート」の登録欄。まだ日本で買えない記事にだけ出す(2026-11-01 本人決定)。

    読者はその製品が欲しくて来るのに、記事は「技適が確認できない=今は無理」で終わることが多く、
    買う気が消えていた。代わりの品を勧めても「ふーん」で終わる。そこで、買えるようになった時に
    1通だけ知らせる登録で買う気を預かる。受け口は alert/ の Worker。`alert_api_url` が空なら出さない。
    JS が無くても form の POST で動く(Worker が HTML で返す)。
    """
    api = str(s.get("alert_api_url") or "").strip().rstrip("/")
    if not api or is_landed(p):
        return ""
    title = html.escape(p["title"])
    return (f'<aside class="jp-alert" id="jp-alert" data-api="{html.escape(api)}">'
            f'<p class="jp-head"><span class="jp-badge">日本上陸アラート</span></p>'
            f'<p class="jp-alert-text">「{title}」が日本で買えるようになったら、メールで1通だけお知らせします。'
            f'それまでメールは送りません。</p>'
            + (f'<p class="jp-alert-track">Gadget Terminal が先に紹介した製品のうち <strong>{LANDED_AFTER[0]}本</strong>は、'
               f'公開したあとで日本での発売・予約・国内クラウドファンディングが始まりました。'
               f'<a href="{u("jpn.html")}">日本上陸した製品</a></p>' if LANDED_AFTER[0] else "")
            + f'<form class="jp-alert-form" action="{html.escape(api)}/subscribe" method="post">'
            f'<input type="email" name="email" required placeholder="メールアドレス" autocomplete="email" aria-label="メールアドレス">'
            f'<input type="hidden" name="slug" value="{html.escape(p["slug"])}">'
            f'<input type="text" name="website" class="jp-alert-hp" tabindex="-1" autocomplete="off" aria-hidden="true">'
            f'<button type="submit">登録する</button></form>'
            f'<p class="jp-alert-note">確認メールが届きます。解除はいつでもできます。'
            f'<a href="{u("privacy.html")}#alert">メールの扱いについて</a></p>'
            f'<p class="jp-alert-msg" role="status" aria-live="polite"></p></aside>')


ALERT_JS = """<script>(function(){var f=document.querySelector('.jp-alert-form');if(!f)return;
var box=f.closest('.jp-alert'),msg=box.querySelector('.jp-alert-msg'),btn=f.querySelector('button');
f.addEventListener('submit',function(e){e.preventDefault();btn.disabled=true;msg.textContent='送信中…';
var d={};new FormData(f).forEach(function(v,k){d[k]=v});
fetch(f.action,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(d)})
.then(function(r){return r.json()}).then(function(j){msg.textContent=j.message||j.error||(j.ok?'確認メールを送りました':'登録できませんでした');
if(j.ok){f.querySelector('input[type=email]').value='';}btn.disabled=false;})
.catch(function(){msg.textContent='送れませんでした。時間をおいてもう一度お試しください';btn.disabled=false;});});})();</script>"""


JP_FACT_LI = re.compile(r"<li>\s*<strong>(.{1,40}?)[：:]\s*</strong>\s*(.*?)</li>", re.S)
JP_NEXT_WORDS = re.compile(r"今すぐ|待つ|選択肢|代わり|おすすめ|向いている|買うなら|急ぎ|別機種|必要なら|ほしいなら|欲しいなら")
JP_FOOT = re.compile(r"(情報源は|なお、|出典は|この記事の(価格|情報)|価格・(出荷|発売))")
JP_UNKNOWN = re.compile(r"(?:日本上陸を待つうえで、)?まだ分かって(?:い)?ない(?:こと|の)は、(.+?)の(\d)点[。.]?")


def style_japan_section(body_html: str, p: dict, has_alert: bool) -> str:
    """「日本で買える？使える？」の節を、文字の壁にしない形に組み直す(2026-11-07 本人「読むのめんどくさい」)。

    記事の文(Markdown)は変えず、出来上がった HTML の形だけを見て置き換える。記事づくりの指示文は継ぎ足さない。
    - 冒頭の「**結論。** 説明」の段落 → 結論の枠。上に技適・日本上陸の状況を札で出す(front matter から)
    - 「**見出し：** 本文」だけの箇条書き → 見出しを左に置いた表のような行
    - 短い項目だけの箇条書き(まだ分からないこと) → 「？」の付いたチェック欄
    - 最後の段落が次の行動の話なら → 「どうする？」の枠
    形が合わない部分は触らない(そのままの段落で出る)。
    """
    m = re.search(r"<h2[^>]*>\s*日本で買える？使える？\s*</h2>", body_html)
    if not m:
        return body_html
    nxt = re.search(r"<h2[\s>]", body_html[m.end():])
    end = m.end() + nxt.start() if nxt else len(body_html)
    seg = body_html[m.end():end]

    # 札: 技適(全記事にある)と日本上陸(続報で分かった記事だけ)
    chips = []
    g = p.get("giteki") or {}
    gs = str(g.get("status") or "").strip()
    if gs:
        # 札は柔らかい言い方と落ち着いた色にする(2026-11-07 本人「確認できない → 情報なし」)。本文の言い方は変えない
        tone = {"取得済み": "ok"}.get(gs, "na")
        nums = [str(x) for x in (g.get("number") or []) if str(x).strip()]
        label = {"確認できない": "情報なし"}.get(gs, gs) + (f"({nums[0]})" if gs == "取得済み" and nums else "")
        chips.append(f'<span class="jp-chip jp-chip-{tone}"><b>技適</b>{html.escape(label)}</span>')
    js = str((p.get("japan") or {}).get("status") or "").strip()
    if js:
        chips.append(f'<span class="jp-chip jp-chip-{"ok" if is_landed(p) else "warn"}"><b>日本</b>{html.escape(js)}</span>')
    if has_alert:
        chips.append('<a class="jp-chip jp-chip-alert" href="#jp-alert"><b>通知</b>日本に来たらメールで知らせる</a>')
    chip_html = f'<p class="jp-chips">{"".join(chips)}</p>' if chips else ""

    lead = re.match(r"\s*<p>\s*(<strong>.*?</strong>)(.*?)</p>", seg, re.S)
    if lead:
        seg = (f'<div class="jp-verdict">{chip_html}<p class="jp-verdict-head">{lead.group(1)}</p>'
               + (f'<p class="jp-verdict-text">{lead.group(2).strip()}</p>' if lead.group(2).strip() else "")
               + "</div>" + seg[lead.end():])
    elif chip_html:
        seg = f'<div class="jp-verdict">{chip_html}</div>' + seg

    def ul_sub(mm: re.Match) -> str:
        inner = mm.group(1)
        items = re.findall(r"<li>(.*?)</li>", inner, re.S)
        if not items:
            return mm.group(0)
        facts = JP_FACT_LI.findall(inner)
        if len(facts) == len(items):
            rows = "".join(f'<div class="jp-fact"><dt>{k}</dt><dd>{v.strip()}</dd></div>' for k, v in facts)
            return f'<dl class="jp-facts">{rows}</dl>'
        plain = [re.sub(r"<[^>]+>", "", x).strip() for x in items]
        if "<strong>" not in inner and all(len(x) <= 45 for x in plain):
            return '<ul class="jp-open">' + "".join(f"<li>{x.strip()}</li>" for x in items) + "</ul>"
        return mm.group(0)

    seg = re.sub(r"<ul>(.*?)</ul>", ul_sub, seg, flags=re.S)
    # 「まだ分かっていないのは次のとおり。」のような前置きは、チェック欄の小見出しにする
    seg = re.sub(r"<p>([^<]{4,60}(?:次のとおり|以下のとおり|次の\d+つ)[。：:]?)</p>(\s*)<ul class=\"jp-open\">",
                 r'<p class="jp-open-head">\1</p>\2<ul class="jp-open">', seg)
    # 段落だけで書かれた記事(多くの記事がこの形)向け。2026-11-07 本人「他の記事も同じように」
    def para_sub(mm: re.Match) -> str:
        text = mm.group(1).strip()
        plain = re.sub(r"<[^>]+>", "", text)
        if JP_FOOT.match(plain):
            return f'<p class="jp-foot">{text}</p>'
        u_ = JP_UNKNOWN.search(text)
        if u_:
            items = [x.strip() for x in re.split(r"、|，", u_.group(1)) if x.strip()]
            if len(items) == int(u_.group(2)) and all(len(re.sub(r"<[^>]+>", "", x)) <= 45 for x in items):
                before, after = text[:u_.start()].strip(), text[u_.end():].strip()
                return ((f"<p>{before}</p>" if before else "")
                        + '<p class="jp-open-head">日本上陸を待つうえで、まだ分かっていないこと</p>'
                        + '<ul class="jp-open">' + "".join(f"<li>{x}</li>" for x in items) + "</ul>"
                        + (f"<p>{after}</p>" if after else ""))
        return mm.group(0)

    seg = re.sub(r"<p>(.*?)</p>", para_sub, seg, flags=re.S)
    # 最後の段落が次の行動の話なら「どうする？」の枠に(後ろに出典などの注記だけが続いてもよい)
    paras = list(re.finditer(r"<p>(.*?)</p>", seg, re.S))
    if paras:
        last = paras[-1]
        tail = seg[last.end():]
        if JP_NEXT_WORDS.search(last.group(1)) and not re.search(
                r"<(p|ul|dl|ol)[\s>]", re.sub(r'<p class="jp-foot">.*?</p>', "", tail, flags=re.S)):
            seg = (seg[:last.start()] + f'<div class="jp-next"><p class="jp-next-head">どうする？</p>'
                   f'<p class="jp-next-text">{last.group(1)}</p></div>' + tail)

    # 残った地の段落は、続いているものをまとめて区切り線つきの行にする。「**見出し。**本文」は見出しを上に出す
    def row(pm: re.Match) -> str:
        text = pm.group(1).strip()
        h = re.match(r"<strong>(.{1,40}?)</strong>\s*", text, re.S)
        if h and h.end() < len(text):
            return (f'<div class="jp-fact"><p class="jp-fact-h">{h.group(1).rstrip("。：:")}</p>'
                    f'<p>{text[h.end():]}</p></div>')
        return f'<div class="jp-fact"><p>{text}</p></div>'

    seg = re.sub(r"(?:\s*<p>.*?</p>)+",
                 lambda g: '<div class="jp-rows">' + re.sub(r"\s*<p>(.*?)</p>", row, g.group(0), flags=re.S) + "</div>",
                 seg, flags=re.S)
    return body_html[:m.end()] + seg + body_html[end:]


def insert_alert_form(body_html: str, form_html: str) -> str:
    """登録欄を「日本で買える？使える？」の節の末尾(次の h2 の手前)に入れる。節が無ければ本文の末尾。"""
    if not form_html:
        return body_html
    m = re.search(r"<h2[^>]*>\s*日本で買える？使える？\s*</h2>", body_html)
    if not m:
        return body_html + form_html
    nxt = re.search(r"<h2[\s>]", body_html[m.end():])
    pos = m.end() + nxt.start() if nxt else len(body_html)
    return body_html[:pos] + form_html + body_html[pos:]


# 日本上陸の続報でだけ使える技適の判定(2026-09-27 本人判断)。
# 日本法人・正規代理店が国内向けに売っているのに、総務省のデータベースで
# 型番を特定できない(登録の反映待ち・型番が非公開)ことがある。その場合は
# 「確認した」とは書かずに、確認できていないことを明示したうえでリンクを出す。
# **海外直販の buy には使わせない。** 国内の販売元が責任を持つ場合に限る根拠が無くなるため。
GITEKI_JAPAN = {
    **GITEKI_BUY,
    "国内正規": ("国内正規品・技適番号は未確認", "na",
             "日本法人・正規代理店が国内向けに販売しています。技適の番号は掲載時点で"
             "総務省のデータベースから確認できていません。"),
    # メーカー自身の日本向け直販(販売元は海外の法人)で、技適も確かめられていない物
    # (2026-11-07 本人「入れて」)。日本語のサイト・円建て・国内倉庫・国内保証で売っているが、
    # 国内の正規代理店とは言えないので「国内正規」とは書かない。買う前に読者が確かめられるよう警告を必ず出す
    "未確認": ("技適未確認", "warn",
             "販売元はメーカーの日本向け直販(海外の法人)で、技適の番号は掲載時点で総務省の"
             "データベースから確認できていません。Wi-Fi や Bluetooth を使う前に、本体や箱の"
             "技適マークを確かめてください。"),
}


def japan_store(url: str) -> str:
    host = urlparse(url).netloc.lower()
    for hosts, name in JAPAN_STORES:
        if any(host == h or host.endswith("." + h) for h in hosts):
            return name
    return "販売ページ"


def coupon_html(p: dict, x: dict) -> str:
    """購入先のクーポン(japan.buy の coupon: {code, discount, until, note})。

    期限(until)を過ぎたら出さない(2026-11-07 本人「使用期限が過ぎたらとること」)。
    GT は毎朝の記事の公開でビルドし直すので、期限の翌朝には消える。
    front matter に残った期限切れのクーポンは、ビルドのたびに知らせる。"""
    c = x.get("coupon") or {}
    code, until = str(c.get("code") or "").strip(), str(c.get("until") or "").strip()
    if not code or not until:
        return ""
    if datetime.now(JST).strftime("%Y-%m-%d") > until:
        print(f"! coupon: {p['slug']} のクーポン {code} は {until} で期限切れ。出さない(front matter から消してよい)")
        return ""
    y, m, d = until.split("-")
    extra = f'{html.escape(str(c["note"]))}' if c.get("note") else ""
    return (f'<p class="buy-coupon">クーポンコード <code>{html.escape(code)}</code> で'
            f'{html.escape(str(c.get("discount") or ""))}（{int(y)}年{int(m)}月{int(d)}日まで）。{extra}</p>')


def japan_section(s: dict, p: dict) -> tuple[str, bool]:
    """「日本上陸」の続報枠。記事の冒頭に出す。

    この媒体は海外で出たばかりの製品を扱うので、公開時点では「日本では買えない」
    と書くことが多い。ところが日本で検索されるのは上陸したとき(Makuake開始・
    国内発売)で、その時点で記事が古いままだと、せっかく先に書いた記事が
    「買えない」と言い続けることになる。上陸を確認したらここに書き足す。

    本文は公開時点の記録として残し、続報はこの枠に分けて出す。
    購入リンクは buy と同じく技適の判定が無ければ出さない。
    戻り値: (HTML, アフィリエイトリンクを含むか)
    """
    j = p.get("japan") or {}
    status = str(j.get("status") or "").strip()
    if not j or status not in JAPAN_STATUS:
        if j:
            print(f"! japan: {p['slug']} の status が {status or '未記入'}。"
                  f"続報を出さずに飛ばす（使える値: {' / '.join(JAPAN_STATUS)}）")
        return "", False
    has_aff = False
    rows = []
    for x in (j.get("buy") or []):
        if not x.get("url"):
            continue
        giteki = str(x.get("giteki") or "").strip()
        if giteki not in GITEKI_JAPAN:
            print(f"! japan.buy: {p['slug']} {x['url']} は giteki が {giteki or '未記入'}。"
                  f"購入リンクを出さずに飛ばす（使える値: {' / '.join(GITEKI_JAPAN)}）")
            continue
        link, is_aff = affiliate_url(s, str(x["url"]), str(x.get("merchant") or ""))
        has_aff = has_aff or is_aff
        gi_label, gi_kind, gi_warn = GITEKI_JAPAN[giteki]
        name = str(x.get("name") or japan_store(str(x["url"])))
        price = (f'<span class="buy-price">{html.escape(str(x["price"]))}</span>'
                 if x.get("price") else "")
        warn = f'<p class="buy-warn">{html.escape(gi_warn)}</p>' if gi_warn else ""
        note = f'<p class="buy-note">{html.escape(str(x["note"]))}</p>' if x.get("note") else ""
        note += coupon_html(p, x)
        rows.append(
            f'<li class="buy-item"><a href="{html.escape(link)}" '
            f'rel="{"nofollow sponsored noopener" if is_aff else "nofollow noopener"}" target="_blank">'
            f'{html.escape(name)}</a><p class="buy-meta">{price}'
            f'<span class="buy-giteki gi-{gi_kind}">{gi_label}</span></p>{warn}{note}</li>')
    checked = str(j.get("checked") or "")
    src = j.get("source") or {}
    src_html = (f'<p class="jp-src">出典: <a href="{html.escape(str(src["url"]))}" rel="nofollow noopener" '
                f'target="_blank">{html.escape(str(src.get("title") or src["url"]))}</a></p>'
                if src.get("url") else "")
    time_html = (f'<time datetime="{html.escape(checked)}">{checked.replace("-", ".")} 確認</time>'
                 if checked else "")
    list_html = f'<ul>{"".join(rows)}</ul>' if rows else ""
    return (f'<aside class="jp-update"><p class="jp-head"><span class="jp-badge">日本上陸</span>'
            f'<span class="jp-status">{html.escape(status)}</span>{time_html}</p>'
            f'<p class="jp-summary">{html.escape(str(j.get("summary") or ""))}</p>'
            f'{list_html}{src_html}'
            f'<p class="jp-note">この枠は公開後の続報です。本文は公開時点の情報のまま残しています。</p>'
            f'</aside>', has_aff)


def giteki_followup_section(p: dict) -> str:
    """「技適の続報」枠。公開後の再確認で技適番号の登録を見つけた記事にだけ出す。

    japan_section と同じ見た目(.jp-update)。本文は公開時点の記録なので書き換えず、
    後から分かったことはこの枠に分けて出す。"""
    g = p.get("giteki") or {}
    found = g.get("found") or ""
    if not found or g.get("status") != "取得済み" or not g.get("number"):
        return ""
    nums = "、".join(html.escape(n) for n in g["number"])
    return (f'<aside class="jp-update"><p class="jp-head"><span class="jp-badge">技適の続報</span>'
            f'<time datetime="{html.escape(found)}">{found.replace("-", ".")} 確認</time></p>'
            f'<p class="jp-summary">{html.escape(found)} の再確認で、総務省のデータベースに技適番号 {nums} の'
            f'登録を確認しました。本文は公開時点の情報のままです。</p>'
            f'<p class="jp-note"><a href="{u(GITEKI_PATH)}">技適チェック一覧</a>で他の製品の状況も見られます。</p>'
            f'</aside>')


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


def click_beacon(s: dict) -> str:
    """紹介リンク（rel に sponsored が付いた a）が押されたら、ページ・ストア・置き場所を送る。

    もしもの報告は記事別に分からないので、記事ごとのクリックをここで数える（2026-10-27 開始）。
    リンクの href は書き換えない（Amazon の規約で転送・偽装リンクを避けるため）。受け口は
    x-poster の関数 gtClick で、数は Firestore の gtClicks に入り、司令塔が読む。
    `click_beacon_url` が空なら何も出さない。
    """
    url = str(s.get("click_beacon_url") or "").strip()
    if not url:
        return ""
    return ("<script>(function(){var U=" + json.dumps(url) + ";"
            "function f(e){var a=e.target.closest&&e.target.closest('a[rel~=\"sponsored\"]');"
            "if(!a||!navigator.sendBeacon)return;var h=a.href;try{h=decodeURIComponent(h)}catch(x){}"
            "var st=/amazon\./.test(h)?'amazon':/rakuten\./.test(h)?'rakuten':/yahoo\./.test(h)?'yahoo':'other';"
            "var w=a.closest('.buys')?'buy':a.closest('.gear')?'gear':a.closest('.alts')?'alternatives':"
            "a.closest('.fp')?'feature':a.closest('.jp-update')?'jp-update':'body';"
            "try{navigator.sendBeacon(U,JSON.stringify({p:location.pathname,s:st,w:w}))}catch(x){}}"
            "document.addEventListener('click',f,true);"
            "document.addEventListener('auxclick',function(e){if(e.button===1)f(e)},true);"
            "})();</script>")


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


def ad_unit(s: dict, slot_key: str) -> str:
    """手動の広告ユニット。

    **自動広告は使わない。** Google に任せると記事の途中・表の直前・
    特集の写真と本文の間に割り込む。この媒体は「技適まで踏み込んで
    言い切る信頼」で読ませているので、読んでいる最中に邪魔をして失うものが
    広告収益より大きいと判断している。位置はここで決め打ちする。

    `adsense_client` と該当スロットIDの**両方**が埋まったときだけ出す。
    スロットIDの無い <ins> を置いても広告は表示されず、管理画面に
    空のユニットが残るだけになる。
    """
    cid = str(s.get("adsense_client") or "").strip()
    slot = str((s.get("adsense_slots") or {}).get(slot_key) or "").strip()
    if not (cid and slot):
        return ""
    return (
        '<aside class="ad-slot"><p class="ad-slot-label">広告</p>'
        '<ins class="adsbygoogle" style="display:block" '
        f'data-ad-client="{html.escape(cid)}" data-ad-slot="{html.escape(slot)}" '
        'data-ad-format="auto" data-full-width-responsive="true"></ins>'
        "<script>(adsbygoogle=window.adsbygoogle||[]).push({});</script></aside>"
    )


def head(site: dict, title: str, desc: str, url_path: str, extra: str = "",
         image: str = "ogp/default.png", og_type: str = "website") -> str:
    s = site["site"]
    # image が外部URL（公式サイトの製品画像）ならそのまま使う。
    # 自社生成のアイキャッチだけがサイト相対パスで渡ってくる。
    is_ext_img = image.startswith(("http://", "https://"))
    img_url = image if is_ext_img else f"{s['base_url'].rstrip('/')}/{image.lstrip('/')}"
    # 寸法は自社生成画像（1200x630 固定）のときだけ書く。
    # 外部画像は実寸が分からず、誤った値を書くとカードの描画が崩れる。
    dims = ('<meta property="og:image:width" content="1200">' '<meta property="og:image:height" content="630">')
    img_dims = "" if is_ext_img else dims
    # 記事が X で共有されたとき、カードに媒体アカウントの帰属を出す。
    _xa = str(s.get("x_account") or "").strip().lstrip("@")
    x_site_meta = f'<meta name="twitter:site" content="@{html.escape(_xa)}">' if _xa else ""
    _p = "" if url_path in ("index.html", "/") else url_path.lstrip("/")
    full_url = f"{s['base_url'].rstrip('/')}/{_p}"
    # Search Console の所有権確認。「HTMLタグ」方式で出るメタタグの content= の
    # 中身だけを site.yaml に入れる。空なら何も出さない。
    _sc = str(s.get("search_console_verification") or "").strip()
    sc_meta = (f'<meta name="google-site-verification" content="{html.escape(_sc)}">'
               if _sc else "")
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#f6f7f9">
<script>(function(){{try{{if(localStorage.getItem("gt-theme")==="dark"){{document.documentElement.setAttribute("data-theme","dark");document.querySelector('meta[name=theme-color]').content="#0a0d16";}}}}catch(e){{}}}})();</script>
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">{sc_meta}
<meta name="robots" content="max-image-preview:large">
<link rel="canonical" href="{html.escape(full_url)}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{html.escape(s['title'])}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{html.escape(full_url)}">
<meta property="og:locale" content="{s.get('locale', 'ja_JP')}">
<meta property="og:image" content="{html.escape(img_url)}">{img_dims}
<meta name="twitter:card" content="summary_large_image">{x_site_meta}
<meta name="twitter:image" content="{html.escape(img_url)}">
<link rel="icon" type="image/svg+xml" href="{u('assets/favicon.svg')}">
<link rel="alternate" type="application/rss+xml" title="{html.escape(s['title'])}" href="{u('feed.xml')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
<noscript><link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet"></noscript>
<link rel="stylesheet" href="{u('assets/style.css')}?v={CSS_VER}">
{adsense(s)}
{analytics(s)}
{extra}
</head>
<body>"""


def home_ld(site: dict) -> str:
    """トップページの構造化データ。サイト名と運営組織を検索エンジンに宣言する。

    WebSite の name が検索結果の「サイト名」表示の元になる。無いとドメイン名が出る。
    """
    s = site["site"]
    base = s["base_url"].rstrip("/")
    xa = str(s.get("x_account") or "").strip().lstrip("@")
    org = {"@type": "Organization", "@id": f"{base}/#org", "name": s["title"], "url": base + "/",
           "logo": {"@type": "ImageObject", "url": f"{base}/ogp/default.png"},
           **({"sameAs": [f"https://x.com/{xa}"]} if xa else {})}
    web = {"@type": "WebSite", "@id": f"{base}/#website", "name": s["title"], "url": base + "/",
           "inLanguage": "ja", "description": s["description"], "publisher": {"@id": f"{base}/#org"}}
    d = {"@context": "https://schema.org", "@graph": [web, org]}
    return f'<script type="application/ld+json">{json.dumps(d, ensure_ascii=False, separators=(",", ":"))}</script>'


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
    <nav class="nav">{cats}<a href="{u("topic/")}" class="nav-item nav-tp"><span class="nav-code">TPC</span><span class="nav-label">話題</span></a><a href="{u("features.html")}" class="nav-item nav-ft"><span class="nav-code">FTR</span><span class="nav-label">特集</span></a><a href="{u("jpn.html")}" class="nav-item nav-jp"><span class="nav-code">JPN</span><span class="nav-label">日本上陸</span></a><a href="{u("about.html")}" class="nav-item nav-about"><span class="nav-code">INF</span><span class="nav-label">運営</span></a></nav>
    <button type="button" class="theme-toggle" data-theme-toggle aria-label="ダーク／ライト表示を切り替え">
      <span class="tt-ic tt-ic-moon" aria-hidden="true">☾</span><span class="tt-ic tt-ic-sun" aria-hidden="true">☀</span>
    </button>
    <span class="head-clock" aria-hidden="true"><small>JST</small><b data-clk="h">--</b><i>:</i><b data-clk="m">--</b></span>
  </div>
</header>
<script>(function(){{
var b=document.currentScript.previousElementSibling.querySelector("[data-theme-toggle]");
b.addEventListener("click",function(){{
  var dark=document.documentElement.getAttribute("data-theme")==="dark";
  var next=dark?"light":"dark";
  if(next==="dark")document.documentElement.setAttribute("data-theme","dark");
  else document.documentElement.removeAttribute("data-theme");
  try{{localStorage.setItem("gt-theme",next);}}catch(e){{}}
  var m=document.querySelector('meta[name=theme-color]');
  if(m)m.content=next==="dark"?"#0a0d16":"#f6f7f9";
}});
}})();</script>"""


def footer(site: dict) -> str:
    _xa = str(site["site"].get("x_account") or "").strip().lstrip("@")
    x_link = (f'<a href="https://x.com/{html.escape(_xa)}" target="_blank" '
              f'rel="noopener">X</a>') if _xa else ""
    s = site["site"]
    year = datetime.now(JST).year
    span = f"{s['copyright_from']}" if year == s["copyright_from"] else f"{s['copyright_from']}–{year}"
    return f"""
<footer class="site-foot">
  <div class="wrap">
    <div class="foot-board">
      <span class="foot-code">SYS</span>
      <span class="foot-status">ONLINE</span>
      <span class="foot-social">{x_link}<a href="{u("feed.xml")}">RSS</a></span>
      <span class="foot-tag">{html.escape(s['tagline'])}</span>
    </div>
    <div class="foot-cols">
      <p class="foot-meta">
        <span class="foot-social-pc">{x_link}<a href="{u("feed.xml")}">RSS</a></span><a href="{u("features.html")}">特集</a><a href="{u("topic/")}">話題から探す</a><a href="{u(GITEKI_PATH)}">技適一覧</a><a href="{u("jpn.html")}">日本上陸</a><a href="{u("about.html")}">運営・免責</a><a href="{u("privacy.html")}">プライバシー</a><a href="{u("media.html")}">メーカー・広報の方へ</a><a href="mailto:{s.get('contact_email','')}">お問い合わせ</a>
      </p>
      <p class="foot-copy">© {span} {html.escape(s['title'])} — {html.escape(s['author'])}</p>
    </div>
  </div>
</footer>
{BOARD_JS}
{click_beacon(s)}
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


def tagline_html(text) -> str:
    """TOP の大見出し。「」の中だけ途中で割らず、ほかは普通に折り返す。

    jp() だと「、」までの長い塊がスマホで塊ごと折り返し、その塊が行の幅を
    使い切るので、続く「毎日。」が余白を残して1行だけ下に落ちていた
    (2026-11-14 本人「最後の毎日のところは改行しなくてもよくない？」)。
    """
    # 「」の中と、最後の「、」のあと(「毎日。」)を割らない。後ろだけだと幅400pxで「毎／日。」と割れた
    t = html.escape(str(text), quote=False)
    t = re.sub(r"「[^」]*」", lambda m: f'<span class="nb">{m.group(0)}</span>', t)
    return re.sub(r"(」</span>)([^<]{1,8})$", r'\1<span class="nb">\2</span>', t)


def title_text(text) -> str:
    """記事タイトル。jp() の「句読点でしか折り返さない」細工はかけない。

    記事タイトルは「、」で区切った塊が長く、塊の途中で折り返せないせいで
    1行に余白を残したまま「、」ごとに改行され、段々に見えていた
    (2026-10-07 本人の指摘「途中で改行しなくてもいい」)。素のテキストにして、
    折り返しは CSS に任せる(2026-10-11 から文節単位をやめ、1文字単位+行頭禁則)。
    """
    return html.escape(str(text))


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


def bold_em(text) -> str:
    """** で囲んだ部分だけ <strong> にする。jp_em() と違い、句読点でしか
    改行させない span/wbr の細工はしない。

    jp()/jp_em() は見出し（1〜2行の短いテキスト）で、句読点以外の
    位置で改行されて不格好になるのを防ぐための技法。だが kicker・
    サイト概要・カテゴリ説明・特集リードのような**複数文にわたる
    説明文**にまで同じ技法を使うと逆効果になる。句読点の位置でしか
    改行できないせいで、短い文節が行頭に取り残されて階段状に見える
    （2026-09-06、記事の kicker で発覚。一覧のカード表示は素のテキストで
    正常に折り返っており、記事ページの .article-lede だけ jp() 経由で
    壊れていた）。word-break:auto-phrase 対応ブラウザなら文節単位の
    折り返しはこちらでも効くので、太字以外の細工を外して素のテキストに戻す。
    """
    out = []
    for i, seg in enumerate(str(text).split("**")):
        if not seg:
            continue
        out.append(f"<strong>{html.escape(seg)}</strong>" if i % 2 else html.escape(seg))
    return "".join(out)


def card_tags(p: dict) -> str:
    """カードの下の札: 日本で買える(緑)と、その記事の話題(最大2つ)。2026-11-11 本人了承"""
    tags = [f'<a class="cd-tag" href="{u(t["path"])}">{html.escape(t["label"])}</a>' for t in topics_of(p)[:2]]
    if is_landed(p):
        tags.insert(0, f'<a class="cd-tag jp" href="{u("jpn.html")}">日本で買える</a>')
    return f'<p class="cd-tags">{"".join(tags)}</p>' if tags else ""


def card(site: dict, p: dict, featured: bool = False, tags: bool = False) -> str:
    key = p.get("category", "misc")
    cat = site["categories"].get(key, {"label": "その他", "slug": "misc", "code": "---"})
    cls = ("card card-featured" if featured else "card") + f" cat-{key}"
    blurb = p.get("kicker") or p["excerpt"]
    img, is_ext = card_image(p)
    img = sized(img, 1100 if featured else 720)
    # 先頭の大きな記事の写真は後回しにしない(遅延読み込みにしない)。ただし最優先の指定はしない。
    # スマホは「今日の新着」の帯(today_strip)が最初の画面でいちばん大きく、そちらを最優先にしている。
    # 両方を最優先にすると回線を取り合い、PageSpeed のスマホの点数が 67→57 に落ちた(2026-11-14)
    load = 'loading="eager"' if featured else 'loading="lazy"'
    return f"""
<article class="{cls}">
  <a class="card-thumb{' card-thumb-real' if is_ext else ''}" href="{u(p['path'])}" aria-hidden="true" tabindex="-1">
    <img src="{html.escape(img)}" alt="" {load} width="1200" height="675"
         decoding="async" referrerpolicy="no-referrer"
         onerror="this.onerror=null;this.src='{u("cards/" + p['slug'] + ".png")}'">
  </a>
  <p class="card-meta">
    <a class="card-code" href="{u("category/" + cat['slug'] + ".html")}">{cat.get('code','---')}</a>
    <span class="card-cat">{html.escape(cat['label'])}</span>
    <time datetime="{p['date']}">{p['date'].replace('-', '.')}</time>
    <span class="card-read">{p['reading_min']}MIN</span>
  </p>
  <h2 class="card-title">{'<span class="pick-badge">PICK</span>' if p.get('pick') else ''}<a href="{u(p['path'])}">{title_text(p['title'])}</a></h2>
  <p class="card-excerpt">{html.escape(blurb)}</p>{card_tags(p) if tags else ""}
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
    """出発案内板(DEPARTURES)に出す記事を選ぶ。

    **まだ出資できる海外のクラウドファンディング案件を締切が近い順に上へ置く。**
    掲載日順にすると、読者が今日行動できる案件が下に沈んで案内板の意味が無くなる。
    残りは新着順で埋める。日本に上陸した記事は到着案内板(arrival_posts)に回す。
    (2026-11-05 本人了承で板を2枚に分けた。それまではこの1枚を ARRIVALS と呼んでいた)
    """
    today = datetime.now(JST).strftime("%Y-%m-%d")
    live, rest = [], []
    for p in posts:
        if is_landed(p):
            continue
        label, _ = post_status(p, today)
        if label in ("FINAL CALL", "NOW BOARDING"):
            live.append(p)
        else:
            rest.append(p)
    live.sort(key=lambda x: str(x.get("deadline") or "9999"))
    return (live + rest)[:limit]


def arrival_posts(posts: list[dict], limit: int = 6) -> list[dict]:
    """到着案内板(ARRIVALS)に出す記事。先に海外の話として書き、あとで日本で
    発売・予約・国内クラファンが始まった製品を、上陸を確かめた日が新しい順に出す。
    「発売予定」は発表だけなので載せない(日本上陸アラートと同じ線引き)。"""
    landed = [p for p in posts if is_landed(p)]
    landed.sort(key=lambda p: (str((p.get("japan") or {}).get("checked") or p["date"]), p["date"]),
                reverse=True)
    return landed[:limit]


ARRIVAL_NOTE = {"発売済み": "発売中", "予約受付中": "予約受付中", "クラウドファンディング中": "国内クラファン"}


def board_what(p: dict) -> str:
    """案内板の製品名の下に出す「何の製品か」の一言。記事の題名から製品名の部分を
    外した、最初の文をそのまま使う(新しく文を作らない。推測で書くと事実を外すため)。
    例: 「Arrowspace S1、カメラでネジを見分けて…AI電動ドライバー。Kickstarterで…」
        → 「カメラでネジを見分けて…AI電動ドライバー」"""
    full = re.sub(r"\s+", " ", str(p.get("title") or "")).strip()
    sentence = full.split("。")[0].strip("、, ")
    kw = str(p.get("keyword") or "").strip().lower()
    t = full
    m = re.search(r"」(?:は|が|、|,|の|を|で|も)?", t)
    if m and m.start() < 45:
        t = t[m.end():]
    else:
        i = t.find("、")
        first = t[:i]
        if 0 < i <= 40 and ((kw and kw in first.lower()) or re.fullmatch(r"[\x00-\x7f]+", first)):
            t = t[i + 1:]
    t = t.split("。")[0].strip("、, ")
    # 「発売、…」の「発売」のような短い頭は落とす
    head, sep, tail = t.partition("、")
    if sep and len(head) <= 4 and len(tail) >= 12:
        t = tail
    # 切りすぎて短い・カッコで始まる(「Nano36」「Nano72」を発売 など)ときは、最初の文をそのまま
    if len(t) < 12 or t.startswith("「"):
        t = sentence
    return t


def board_row(site: dict, p: dict, i: int, arrival: bool = False) -> str:
    key = p.get("category", "misc")
    cat = site["categories"].get(key, {"code": "---", "label": "その他"})
    if arrival:
        j = p.get("japan") or {}
        label, style = "LANDED", "live"
        note = ARRIVAL_NOTE.get(str(j.get("status") or "").strip(), "")
        price = str(((j.get("buy") or [{}])[0] or {}).get("price") or "")
        price = re.split(r"[（(]", price)[0].strip()
        what = f"国内 {price}" if price else board_what(p)
    else:
        today = datetime.now(JST).strftime("%Y-%m-%d")
        label, note = post_status(p, today)
        style = STATUS_STYLE.get(label, "done")
        what = board_what(p)
    code, city = post_origin(site, p)
    alt = " board-row-alt" if i % 2 == 0 else ""
    img = sized(card_image(p)[0], 160)
    return f"""<a class="board-row cat-{key}{alt}" href="{u(p['path'])}">
  <span class="b-thumb" aria-hidden="true"><img data-thumb="{html.escape(img)}" alt="" decoding="async"
    referrerpolicy="no-referrer" width="96" height="96"
    onerror="this.onerror=null;this.src='{u("cards/" + p['slug'] + ".png")}'"></span>
  <span class="b-flt" data-flap>{p['flight']}</span>
  <span class="b-from"><b data-flap>{html.escape(code)}</b>{f'<span>{html.escape(city)}</span>' if city else ''}</span>
  <span class="b-code" data-flap>{cat.get('code','---')}</span>
  <span class="b-key"><b>{html.escape(p.get('keyword') or '')}</b><small class="b-what">{html.escape(what)}</small></span>
  <span class="b-title">{html.escape(p['title'])}</span>
  <span class="st st-{style}" data-flap-status>{html.escape(label)}{f'<em>{html.escape(note)}</em>' if note else ''}</span>
  <span class="b-arrow" aria-hidden="true">→</span>
</a>"""


# よく読まれている記事。Cloudflare の閲覧の記録(抜き取りなので数字は粗い)を、自宅PCの
# ks_prefetch.py が毎晩 data/popular.json に書く。ここは並び順だけ使い、数は出さない。
POPULAR = ROOT / "data" / "popular.json"


def popular_section(posts: list[dict], limit: int = 5) -> str:
    try:
        data = json.loads(POPULAR.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    by_path = {"/" + p["path"].lstrip("/"): p for p in posts}
    picked = []
    for row in data.get("paths") or []:
        p = by_path.get(str(row.get("path") or ""))
        if p and p not in picked:
            picked.append(p)
        if len(picked) >= limit:
            break
    if len(picked) < 3:
        return ""
    items = []
    for n, p in enumerate(picked, 1):
        img = html.escape(sized(card_image(p)[0], 240))
        items.append(
            f'<li class="pop-item cat-{p.get("category", "misc")}"><a href="{u(p["path"])}">'
            f'<span class="pop-n">{n:02d}</span>'
            f'<img class="pop-img" src="{img}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer"'
            f' width="120" height="68" onerror="this.onerror=null;this.src=\'{u("cards/" + p["slug"] + ".png")}\'">'
            f'<span class="pop-title">{html.escape(p["title"])}</span></a></li>')
    days = int(data.get("days") or 30)
    return (f'<section class="popular"><h2 class="picks-head">よく読まれている記事'
            f'<span class="picks-sub">過去{days}日</span></h2><ol class="pop-list">{"".join(items)}</ol></section>')


def page_path(n: int) -> str:
    """ページ番号 → サイト内パス。1ページ目だけルートに置く。"""
    return "index.html" if n <= 1 else f"page/{n}.html"


def pager(current: int, total: int) -> str:
    """前へ／次へ と現在位置を出すページ送り。1ページしかないときは何も出さない。"""
    if total <= 1:
        return ""
    prev = (f'<a class="pager-link" href="{u(page_path(current - 1))}" rel="prev">← <span class="pager-pc">新しい記事</span><span class="pager-sp">前へ</span></a>'
            if current > 1 else '<span class="pager-link is-off">← <span class="pager-pc">新しい記事</span><span class="pager-sp">前へ</span></span>')
    nxt = (f'<a class="pager-link" href="{u(page_path(current + 1))}" rel="next"><span class="pager-pc">古い記事</span><span class="pager-sp">次へ</span> →</a>'
           if current < total else '<span class="pager-link is-off"><span class="pager-pc">古い記事</span><span class="pager-sp">次へ</span> →</span>')
    # 全ページを並べると毎週1つずつ増えて何行にもなる。最初・最後・今の前後だけ出し、あいだは「…」(2026-11-14 本人)
    # スマホは「新しい記事」「古い記事」のボタンと横一列に並べるので、前後1つずつに絞った版も作り CSS で出し分ける
    def nums_html(span: int) -> str:
        shown = sorted({1, total, *range(max(1, current - span), min(total, current + span) + 1)})
        parts, prev_n = [], 0
        for n in shown:
            if n - prev_n == 2:  # 1つだけ飛ぶなら「…」より番号のほうが短い
                parts.append(f'<a class="pager-num" href="{u(page_path(n - 1))}">{n - 1}</a>')
            elif n - prev_n > 2:
                parts.append('<span class="pager-gap" aria-hidden="true">…</span>')
            parts.append(f'<span class="pager-num is-here">{n}</span>' if n == current
                         else f'<a class="pager-num" href="{u(page_path(n))}">{n}</a>')
            prev_n = n
        return "".join(parts)
    nums = (f'<span class="pager-nums-wide">{nums_html(2)}</span>'
            f'<span class="pager-nums-narrow">{nums_html(1)}</span>')
    return f'<nav class="pager" aria-label="ページ送り">{prev}<span class="pager-nums">{nums}</span>{nxt}</nav>'


def next_page_tile(current: int, total: int) -> str:
    """カード一覧グリッドの最後に足す、次ページへの導線タイル。

    grid-template-columns は auto-fill なので、記事数が列数の倍数でないと
    最終行に空きマスができる（ビューポート幅で列数が変わるため何列できるかは
    ここでは分からない）。1枚追加するだけで全部の空きが必ず埋まるわけではないが、
    最低1マスは「次のページへ」として活かせる。最終ページでは何も出さない。
    """
    if current >= total:
        return ""
    nxt = current + 1
    return (f'<a class="card card-next" href="{u(page_path(nxt))}">'
            f'<span class="cn-tag">NEXT GATE</span>'
            f'<span class="cn-num">{nxt:02d}<i>/{total:02d}</i></span>'
            f'<span class="cn-label">次のページへ</span>'
            f'<span class="cn-arrow" aria-hidden="true">→</span></a>')


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
        img = html.escape(sized(img, 480))
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
  <h2 class="picks-head">編集部ピックアップ</h2>
  <div class="picks-list">{''.join(rows)}
  </div>
</section>"""


# スマホの「今日の新着」の帯を出すか。PageSpeed のスマホの点数が下がる原因か切り分けるため、いったん止める(2026-11-14)
TODAY_STRIP_ON = False


def today_strip(posts: list[dict]) -> str:
    """スマホの TOP、大見出しの下に「今日の新着」を4秒ずつ切り替えて出す帯(2026-11-14 本人了承)。

    いちばん新しい日の記事を3本まで。メーカー公式の映像がある記事を先に出す(本人「動画が
    あるガジェットは画面に動きがでると一気に見栄えが良くなる」)。PC では出さない(CSS)。
    SEO: 帯は最初の画面でいちばん大きな物になるので、1枚目だけ最優先で読み込み、2枚目以降は
    切り替える直前に読み込む。映像は静止画を先に出し、再生は表示中の1枚だけ。
    """
    if not posts:
        return ""
    day = posts[0]["date"]
    picks = [p for p in posts if p["date"] == day][:3]
    if len(picks) < 2:
        return ""
    picks.sort(key=lambda p: 0 if p.get("clips") else 1)  # 安定ソートなので記事の順は保たれる
    label = "今日の新着" if day == datetime.now(JST).strftime("%Y-%m-%d") else "新着"
    slides = []
    for i, p in enumerate(picks):
        hook = str(p.get("x_hook") or "").strip().splitlines()
        hook = hook[0].strip() if hook else str(p.get("seo_title") or p["title"])
        name = str(p.get("keyword") or "").strip() or p["title"]
        clip = (p.get("clips") or [None])[0]
        if clip and clip["poster"]:
            img_url, credit = u("clips/" + clip["poster"]), clip["credit"] or "メーカー公式 YouTube"
        elif p.get("thumbnail"):
            img_url, credit, clip = p["thumbnail"], p.get("thumbnail_credit") or "", None
        else:
            continue
        attr = 'src' if i == 0 else 'data-src'
        prio = ' fetchpriority="high" loading="eager"' if i == 0 else ''
        media = f'<img {attr}="{html.escape(img_url)}" alt="{html.escape(name)}" decoding="async"{prio}>'
        if clip:
            media += f'<video muted loop playsinline preload="none" data-v="{u("clips/" + clip["file"])}"></video>'
        slides.append(
            f'<a class="ts-slide{" on" if i == 0 else ""}" href="{u(p["path"])}">'
            f'<div class="ts-media{" is-img" if not clip else ""}">{media}</div>'
            f'<div class="ts-cap"><span class="ts-name">{html.escape(name)}</span>'
            f'<span class="ts-hook">{html.escape(hook)}</span></div>'
            + (f'<span class="ts-credit">{html.escape(credit)}</span>' if credit else "")
            + '</a>')
    if len(slides) < 2:
        return ""
    bars = '<span class="ts-bar"><i></i></span>' * len(slides)
    return f"""<section class="today-strip" aria-label="{label}">
  <div class="ts-top"><span class="ts-label">TODAY · {label}</span><span class="ts-bars" aria-hidden="true">{bars}</span></div>
  <div class="ts-stage">{''.join(slides)}</div>
</section>
<script>(function(){{
var r=document.querySelector('.today-strip');if(!r||getComputedStyle(r).display==='none')return;
var sl=r.querySelectorAll('.ts-slide'),bars=r.querySelectorAll('.ts-bar'),i=0,D=4000;
var calm=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
function load(s){{var im=s.querySelector('img[data-src]');if(im){{im.src=im.getAttribute('data-src');im.removeAttribute('data-src');}}}}
function show(n){{sl.forEach(function(s,k){{s.classList.toggle('on',k===n);var v=s.querySelector('video');if(!v)return;
if(k===n&&!calm){{if(!v.src)v.src=v.getAttribute('data-v');v.currentTime=0;var pr=v.play();if(pr)pr.then(function(){{s.classList.add('playing');}}).catch(function(){{}});}}
else{{v.pause();s.classList.remove('playing');}}}});
load(sl[(n+1)%sl.length]);
bars.forEach(function(b,k){{b.className='ts-bar '+(k<n?'done':'reset');}});void r.offsetWidth;
if(!calm)bars[n].className='ts-bar run';}}
show(0);if(calm)return;
var t=setInterval(function(){{if(document.hidden)return;i=(i+1)%sl.length;show(i);}},D);
}})();</script>"""


def hero_route_img() -> str:
    """トップの見出し横に残る余白を埋める、着陸してくる飛行機のシルエット。

    ユーザー提供の画像（assets/hero-plane.png、透過済み）を使う。
    ベクターで手描きしても実写的なシルエットには再現できないため、画像をそのまま使う。
    """
    return f'<img class="hero-route" src="{u("assets/hero-plane.png")}" alt="" aria-hidden="true">'


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
/* 案内板の写真はスマホの3列のときだけ使う。src を最初から書くと、パソコンでも
   見えない写真(元は数千ピクセルの公式画像)を全部取りに行き、記事一覧の写真が
   後回しになって出なくなった(2026-11-05)。見えている板の分だけ、スマホでだけ読む */
var small=window.matchMedia("(max-width:620px)");
function thumbs(panel){if(!small.matches||!panel)return;
  panel.querySelectorAll("img[data-thumb]").forEach(function(im){im.src=im.getAttribute("data-thumb");
    im.removeAttribute("data-thumb");});}
thumbs(document.getElementById("bp-dep"));
small.addEventListener&&small.addEventListener("change",function(){
  document.querySelectorAll(".board-panel:not([hidden])").forEach(thumbs);});
/* 出発・到着のタブ。左右の矢印キーでも動く */
var tabs=[].slice.call(document.querySelectorAll(".board-tab"));
function pick(t){tabs.forEach(function(x){var on=x===t;x.setAttribute("aria-selected",on?"true":"false");
  x.tabIndex=on?0:-1;var p=document.getElementById(x.getAttribute("aria-controls"));if(p)p.hidden=!on;});
  var p=document.getElementById(t.getAttribute("aria-controls"));thumbs(p);
  if(p)p.querySelectorAll(".board-row").forEach(function(row,i){setTimeout(function(){
    row.querySelectorAll("[data-flap]").forEach(flap);var st=row.querySelector("[data-flap-status]");
    if(st)flapStatus(st);},reduced?0:i*55);});}
tabs.forEach(function(t,i){t.addEventListener("click",function(){pick(t);});
  t.addEventListener("keydown",function(e){var d=e.key==="ArrowRight"?1:e.key==="ArrowLeft"?-1:0;
    if(d){var n=tabs[(i+d+tabs.length)%tabs.length];pick(n);n.focus();e.preventDefault();}});});
var rows=document.querySelectorAll(".board-row");
rows.forEach(function(row,i){
  setTimeout(function(){
    row.querySelectorAll("[data-flap]").forEach(flap);
    var st=row.querySelector("[data-flap-status]");
    if(st)flapStatus(st);
  },reduced?0:i*55);
});

/* 実物の案内板は、しばらく静止したあとも思い出したようにどこかの行が
   パタパタと回る。2秒に1回(2026-10-22 本人の指定。以前は4秒)、ランダムに1行だけ再生して、生きた掲示板に見せる。
   全行同時に回すと五月蝿いので1行ずつ。 */
if(!reduced&&rows.length){
  setInterval(function(){
    var row=rows[Math.floor(Math.random()*rows.length)];
    row.querySelectorAll("[data-flap]").forEach(flap);
    var st=row.querySelector("[data-flap-status]");
    if(st)flapStatus(st);
  },2000);
}
})();
</script>"""


def pinned_feature_strip() -> str:
    """TOP の案内板の上に、pin: true の特集を1本だけ細い帯で出す(2026-11-07 本人、ブラックフライデーの特集)。
    特集は一覧ページにしか出ておらず、TOP から見つけられなかった。pin を外せば帯も消える。"""
    f = next((x for x in FEATURES_FOR_HINT if x.get("pin")), None)
    if not f:
        return ""
    imgs = "".join(
        f'<img src="{html.escape(str(x["image"]).strip())}" alt="" loading="lazy" decoding="async" '
        f'referrerpolicy="no-referrer" onerror="this.remove()">'
        for x in f["products"] if str(x.get("image") or "").strip())
    n = len(f["products"])
    return (f'<a class="pin-ft" href="{u(f["path"])}">'
            f'<span class="pin-ft-text"><span class="pin-ft-eyebrow">{html.escape(str(f.get("eyebrow") or "FEATURE"))}</span>'
            f'<span class="pin-ft-title">{html.escape(f["title"])}</span>'
            f'<span class="pin-ft-go">{str(n) + "製品を見る" if n else "読む"} →</span></span>'
            f'<span class="pin-ft-imgs">{imgs}</span></a>')


def render_index(site: dict, posts: list[dict], page: int = 1, total_pages: int = 1,
                 all_posts: list[dict] | None = None) -> str:
    s = site["site"]
    if not posts:
        body = '<p class="empty">まだ記事がありません。</p>'
    elif page <= 1:
        # 1ページ目だけ、案内板と大きい先頭記事を出す。
        lead, rest = posts[0], posts[1:]
        everything = all_posts or posts
        dep = "".join(board_row(site, p, i + 1)
                      for i, p in enumerate(board_posts(site, everything)))
        arr_posts = arrival_posts(everything)
        arr = "".join(board_row(site, p, i + 1, arrival=True) for i, p in enumerate(arr_posts))
        plane = """<path d="M21 11 L14.5 11.8 L10 17 L7.5 17 L9.8 11.9
        L4.5 12 L3 14 L1.5 14 L2.6 11 L1.5 8 L3 8 L4.5 10 L9.8 10.1 L7.5 5 L10 5 L14.5 10.2 Z"/>"""
        head_row = """<div class="board-head">
    <span>FLIGHT</span><span>FROM</span><span>CAT</span><span>KEY</span><span>ENTRY</span><span>STATUS</span><span></span>
  </div>"""
        # 見出しの飛行機は ISO 7001 の出発(機首を上げる)と到着(機首を下げる)のピクトグラム
        # 2枚の板はタブで切り替える(2026-11-05 本人「案内板の存在感がでかすぎる」。縦に2枚並べたのはボツ)。
        # 最初は出発。到着の中身は HTML に入れておき hidden で隠す(JS が切り替える)
        lede = (f'<p class="board-lede">先に海外の話として紹介した製品のうち <b>{LANDED_AFTER[0]}件</b>が、'
                f'あとから日本で買えるようになりました。<a href="{u("jpn.html")}">日本上陸の一覧 →</a></p>'
                if LANDED_AFTER[0] else f'<p class="board-lede"><a href="{u("jpn.html")}">日本上陸の一覧 →</a></p>')
        arr_tab = ('<button class="board-tab" role="tab" id="bt-arr" aria-controls="bp-arr" aria-selected="false"'
                   ' tabindex="-1" type="button"><svg class="pict-arr" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
                   f'<g transform="rotate(22 12 11)">{plane}</g><rect x="2.5" y="20" width="19" height="1.5" rx=".75"/></svg>'
                   '<span class="board-title-en">ARRIVALS</span><span class="board-tab-ja">日本に上陸</span></button>'
                   if arr_posts else "")
        arr_panel = (f'<div class="board-panel" role="tabpanel" id="bp-arr" aria-labelledby="bt-arr" hidden>'
                     f'{lede}{head_row}{arr}</div>' if arr_posts else "")
        body = f"""
{pinned_feature_strip()}
<section class="board">
  <h2 class="visually-hidden">発着案内</h2>
  <div class="board-title" role="tablist" aria-label="案内板">
    <button class="board-tab" role="tab" id="bt-dep" aria-controls="bp-dep" aria-selected="true" type="button">
      <svg class="pict-arr" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <g transform="rotate(-22 12 11)">{plane}</g>
        <rect x="2.5" y="20" width="19" height="1.5" rx=".75"/>
      </svg>
      <span class="board-title-en">DEPARTURES</span><span class="board-tab-ja">締め切り間近</span>
    </button>{arr_tab}
  </div>
  <div class="board-panel" role="tabpanel" id="bp-dep" aria-labelledby="bt-dep">
  {head_row}
  {dep}
  </div>{arr_panel}
  {connections_section(everything)}
</section>
<section class="lead">
  {card(site, lead, featured=True, tags=True)}
</section>
{popular_section(everything)}
<section class="grid">
  {''.join(card(site, p, tags=True) for p in rest)}{next_page_tile(page, total_pages)}
</section>
{picks_section(site, all_posts or posts)}
{pager(page, total_pages)}"""
    else:
        # 2ページ目以降はカードだけを並べる。
        body = f"""
<section class="grid">
  {''.join(card(site, p, tags=True) for p in posts)}{next_page_tile(page, total_pages)}
</section>
{pager(page, total_pages)}"""
    title = f"{s['title']} — {s['tagline']}" if page <= 1 else f"{s['title']} — {page}ページ目"
    return (
        head(site, title, s["description"], page_path(page), home_ld(site) if page <= 1 else "")
        + header(site)
        + f"""
<main class="wrap">
  <section class="hero{'' if page <= 1 else ' hero-sm'}">
    <p class="eyebrow">{'INTERNATIONAL / 海外発' if page <= 1 else f'ARCHIVE / {page} of {total_pages}'}</p>
    <h1 class="hero-title">{tagline_html(s['tagline']) if page <= 1 else f'過去の記事 — {page}ページ目'}</h1>
    <p class="hero-sub">{html.escape(s['description']) if page <= 1 else ''}</p>
    {hero_route_img() if page <= 1 else ''}
  </section>
  {today_strip(posts) if page <= 1 and TODAY_STRIP_ON else ''}
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


JAPAN_LANDING_SECTIONS = (
    # (見出しの id, 見出し, 短い名前, 説明)
    ("now", "発売済み", "すぐ買える", "国内で発売され、日本の店や直販サイトで買えるもの。"),
    ("reserve", "予約受付中", "予約できる", "国内で予約を受け付けているもの。"),
    ("cf", "国内クラウドファンディング", "国内クラファン", "Makuake・CAMPFIRE・GREEN FUNDING など国内で支援できる(できた)もの。出資は購入ではありません。"),
    ("soon", "発売予定", "もうすぐ", "国内での発売が発表され、まだ買えないもの。"),
)


def render_domestic_cf(site: dict, posts: list[dict]) -> str:
    """日本上陸のページ(jpn.html)。海外で先に記事にした製品のうち、日本で買える・買えそうなもの。

    2026-10-27 本人の要望「日本に上陸したもの＝すぐ買えるものに、すぐたどり着けるように」で、
    それまでの「国内クラファン」ページを広げた。判定は記事の japan.status(続報の枠と同じ)と、
    sources の国内クラファンの URL。URL は検索に載っているのでそのまま使う。
    """
    s = site["site"]
    groups: dict[str, list[dict]] = {k: [] for k, *_ in JAPAN_LANDING_SECTIONS}
    by_status = {"発売済み": "now", "予約受付中": "reserve", "クラウドファンディング中": "cf", "発売予定": "soon"}
    for p in posts:
        st = str((p.get("japan") or {}).get("status") or "").strip()
        if st in by_status:
            groups[by_status[st]].append(p)
        elif domestic_cf_source(p):
            groups["cf"].append(p)
    for k in groups:
        groups[k].sort(key=lambda p: (str((p.get("japan") or {}).get("checked") or p["date"]), p["date"]),
                       reverse=True)
    tabs = "".join(
        f'<a class="jl-tab" href="#jl-{k}"><b>{len(groups[k])}</b><span>{short}</span></a>'
        for k, _, short, _ in JAPAN_LANDING_SECTIONS if groups[k])
    secs = "".join(
        f'<section class="jl-sec" id="jl-{k}"><h2 class="jl-h">{head_}<span>{len(groups[k])}件</span></h2>'
        f'<p class="jl-desc">{desc}</p><div class="grid">{"".join(card(site, p) for p in groups[k])}</div></section>'
        for k, head_, _, desc in JAPAN_LANDING_SECTIONS if groups[k])
    body = (f'<nav class="jl-tabs" aria-label="状況で絞る">{tabs}</nav>{secs}' if secs
            else '<p class="empty">日本に上陸した製品は、まだありません。</p>')
    return (
        head(site, f"日本上陸 — 日本で買える海外ガジェット — {s['title']}",
             "海外で先に記事にしたガジェットのうち、日本で発売・予約・国内クラファンが始まったものの一覧。技適と国内の販売先は各記事に。",
             "jpn.html")
        + header(site)
        + f"""
<main class="wrap">
  <section class="hero hero-sm">
    <p class="eyebrow">JPN / ✈ NRT 日本上陸</p>
    <h1 class="hero-title">日本上陸</h1>
    <p class="hero-sub">海外で先に記事にしたガジェットのうち、日本で発売・予約・国内クラファンが始まったものです。
    記事の「日本上陸」の枠に、国内の価格・販売先・技適をまとめています。状況は確認した日の時点のものです。</p>
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


def merchant_of(url: str) -> str:
    """URL のドメインから国内ECの merchant を引く。対象外なら空文字。"""
    host = urlparse(url).netloc.lower()
    for m, hosts in MERCHANT_HOSTS.items():
        if any(host == h or host.endswith("." + h) for h in hosts):
            return m
    return ""


MD_LINK = re.compile(r"\[([^\]]+)\]\((/[^)\s]+)\)")  # 特集の文の中の [言葉](/posts/...)


def md_link(t: str) -> str:
    return MD_LINK.sub(r'<a href="\2">\1</a>', t)


def feature_product(s: dict, item: dict, n: int = 0) -> tuple[str, bool]:
    """製品1件を、記事の一節として縦に組む。

    横並びのカードにすると比較表になってしまい、上から読ませる記事にならない。
    見出し → 大きな写真 → 本文 → 事実の箱 → リンク、の順に置く。
    本文は空行で段落に割る。ここが記事の実体なので、いちばん広く取る。
    戻り値: (HTML, アフィリエイトリンクか)
    """
    key = str(item.get("availability") or "").strip()
    label, tone = AVAIL_STYLE.get(key, ("判定なし", "bad"))
    name = html.escape(str(item.get("name") or ""))
    brand = html.escape(str(item.get("brand") or ""))
    price = html.escape(str(item.get("price") or ""))
    where = html.escape(str(item.get("where") or ""))
    giteki = html.escape(str(item.get("giteki") or ""))
    url = str(item.get("url") or "").strip()
    src = str(item.get("source") or "").strip()

    # 説明文の中の [言葉](/features/...) をリンクにする(書いたままの文字で出ていた。2026-11-07)
    def _md_link(t):
        return re.sub(r"\[([^\]]+)\]\((/[^)\s]+)\)", r'<a href="\2">\1</a>', t)
    body = "".join(f"<p>{_md_link(bold_em(para.strip()))}</p>"
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
        # 2枚目以降(images:)があれば、下に小さい写真を並べ、押すと上の大きい写真が切り替わる。
        # 写真1枚ではガジェットの形が伝わらない(2026-11-01 本人指摘)。出典は写真ごとに出す。
        extra = [x for x in (item.get("images") or []) if str(x.get("url") or "").strip()]
        if extra:
            shots = [{"url": img, "credit": credit}] + extra
            if not credit:
                shot = shot.replace("</figure>", '<figcaption class="fp-credit"></figcaption></figure>')
            swap = ("var g=this.closest('.fp-gallery'),i=g.querySelector('.fp-shot img'),"
                    "c=g.querySelector('.fp-credit');i.src=this.dataset.src;"
                    "c.textContent=this.dataset.credit?'出典: '+this.dataset.credit:'';"
                    "g.querySelectorAll('.fp-thumb').forEach(function(b){b.classList.remove('on')});"
                    "this.classList.add('on')")
            thumbs = "".join(
                f'<button type="button" class="fp-thumb{" on" if n == 0 else ""}" '
                f'data-src="{html.escape(str(x["url"]).strip())}" '
                f'data-credit="{html.escape(str(x.get("credit") or "").strip())}" '
                f'aria-label="{name}の写真 {n + 1}" onclick="{html.escape(swap)}">'
                f'<img src="{html.escape(str(x["url"]).strip())}" alt="" loading="lazy" decoding="async" '
                f'referrerpolicy="no-referrer" onerror="this.closest(\'button\').remove()"></button>'
                for n, x in enumerate(shots))
            shot = f'<div class="fp-gallery">{shot}<div class="fp-thumbs">{thumbs}</div></div>'

    # 特集の製品は merchant を書かせず、URL のドメインで決める（楽天・Amazon の
    # 店舗ページをそのまま貼る運用のため）。2026-10-12 まで変換を通しておらず、
    # 特集の購入ボタンは全部素のリンクで報酬が発生していなかった。
    # 購入ボタンは店の名前で書く(2026-11-07 本人「購入ページをクリックさせたい」)。
    # 「購入ページを開く」はどこへ飛ぶか分からず、文字のリンクで「確認したソース」と同じ重さだった。
    def btn(href, rel_, label, sub, primary):
        sub_html = f'<small>{html.escape(sub)}</small>' if sub else ""
        return (f'<a class="fp-buy{" fp-buy-main" if primary else ""}" href="{html.escape(href)}" '
                f'target="_blank" rel="{rel_}"><span>{label}</span>{sub_html}</a>')
    is_aff = False
    buy = ""
    if url:
        mer = merchant_of(url)
        url, is_aff = affiliate_url(s, url, mer)
        rel = "nofollow sponsored noopener" if is_aff else "noopener nofollow"
        main_label = {"amazon": "Amazonで見る", "rakuten": "楽天市場で見る",
                      "yahoo": "Yahoo!ショッピングで見る"}.get(mer, "公式ストアで見る")
        # クラファンや品切れの店は「公式ストア」と書くと違う。buy_label で言い換える(2026-11-11)
        main_label = html.escape(str(item.get("buy_label") or "").strip()) or main_label
        buy = btn(url, rel, main_label, "", True)
    # 楽天にもメーカー公式店・大手販売店がある製品は、2つ目の購入先として出す。
    # 特集は正規流通を勧めるページなので、転売価格の店や別型番のページは書かない。
    rk = item.get("rakuten") or {}
    rk_url = str(rk.get("url") or "").strip()
    if rk_url:
        rk_url, rk_aff = affiliate_url(s, rk_url, "rakuten")
        is_aff = is_aff or rk_aff
        shop = str(rk.get("shop") or "").strip()
        # 判定バッジの label と別の名前にする(同じ名前で上書きし、バッジが「楽天市場で見る」になっていた。2026-11-01 修正)
        buy += btn(rk_url, "nofollow sponsored noopener" if rk_aff else "noopener nofollow",
                   "楽天市場で見る", shop, not buy)
    src_link = (f'<a class="fp-src" href="{html.escape(src)}" target="_blank" '
                f'rel="noopener">確認したソース</a>') if src else ""
    # 価格は「23,400円」を大きく、「(BenQ公式ストア、掲載時点)」を小さく分ける
    pm = re.match(r"^([^(（]+?)\s*([(（].*)?$", str(item.get("price") or "").strip())
    p_main = html.escape(pm.group(1)) if pm else price
    p_sub = html.escape(pm.group(2) or "") if pm else ""
    # Amazon で売っている物は技適の行を出さない(2026-11-07 本人「Amazonで売ってる時点で技適の情報は必要ない」)。
    # 特集は国内の正規店だけを載せる決まりなので、Amazon で買える＝国内向けの正規品。確かめるのは今までどおり続け、原稿の giteki も残す
    on_amazon = merchant_of(str(item.get("url") or "")) == "amazon"
    cert_row = ("" if on_amazon else
                f'<dt>{html.escape(str(item.get("cert_label") or "技適"))}</dt><dd>{giteki or "&mdash;"}</dd>')
    # 購入の箱にも小さな写真を出す(2026-11-07 本人)。どの製品の箱か、ボタンの横で分かるように
    thumb = (f'<span class="fp-cta-img"><img src="{html.escape(img)}" alt="{name}" loading="lazy" decoding="async" '
             f'referrerpolicy="no-referrer" onerror="this.parentNode.remove()"></span>') if img else ""
    cta = ""
    if buy or price:
        cta = (f'<div class="fp-cta">{thumb}<div class="fp-cta-main"><p class="fp-price"><span>{p_main or "&mdash;"}</span>'
               f'{f"<small>{p_sub}</small>" if p_sub else ""}</p>'
               f'<div class="fp-buys">{buy}</div>'
               f'<p class="fp-cta-note">価格・在庫・ポイントは変わることがあります。リンク先で確かめてください。</p></div></div>')

    return f"""
<section class="fp fp-{tone}">
  <header class="fp-head">
    <p class="fp-kicker"><span class="fp-no">{n:02d}</span><span class="fp-brand">{brand}</span></p>
    <h2 class="fp-name">{name}</h2>
    <span class="fp-badge fp-badge-{tone}">{label}</span>
  </header>
  {shot}
  <div class="fp-body">{body}</div>
  <div class="fp-box">
  {cta}
  <dl class="fp-meta">
    <dt>買えるところ</dt><dd>{where or "&mdash;"}</dd>
{cert_row}
  </dl>
  </div>
  <p class="fp-links">{src_link}</p>
</section>""", is_aff


def render_feature(site: dict, f: dict, posts: list[dict]) -> str:
    s = site["site"]
    parts = [feature_product(s, x, i) for i, x in enumerate(f["products"], 1)]
    items = "".join(h for h, _ in parts)
    grid = f'<div class="fp-list">{items}</div>' if items else ""
    # ステマ規制。記事と同じく、アフィリエイトリンクがある特集はページ上部で示す。
    disclosure = ""
    if any(a for _, a in parts):
        text = str((s.get("affiliate") or {}).get("disclosure") or "この記事にはアフィリエイト広告を含みます")
        disclosure = f'<p class="ad-notice">{html.escape(text)}</p>'


    excluded = ""
    if f["excluded"]:
        rows = "".join(
            f'<li><strong>{html.escape(str(x.get("name") or ""))}</strong>'
            f' &mdash; {md_link(bold_em(str(x.get("why") or "")))}</li>'
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
    <p class="hero-sub">{bold_em(str(f.get('lede') or ''))}</p>
    {upd_html}
  </section>
  {disclosure}
  <div class="prose feature-intro">{f['body']}</div>
  {grid}
  {excluded}
  {ad_unit(s, "article_end")}
  {related}
</main>"""
        + footer(site)
    )


def render_features_index(site: dict, features: list[dict]) -> str:
    s = site["site"]
    def thumbs(f: dict) -> str:
        # 特集一覧にも製品の写真を3枚まで小さく並べる（2026-10-11 本人の要望）。
        # 画像は権利者のサーバーをホットリンク。読み込めない1枚だけ消す。
        imgs = [(str(x.get("name") or ""), str(x["image"]).strip())
                for x in f["products"] if str(x.get("image") or "").strip()][:3]
        if not imgs:
            return ""
        tags = "".join(
            f'<img src="{html.escape(src)}" alt="{html.escape(name)}" loading="lazy" '
            f'decoding="async" referrerpolicy="no-referrer" onerror="this.remove()">'
            for name, src in imgs)
        return f'<div class="fi-thumbs">{tags}</div>'

    if features:
        rows = "".join(
            f'<a class="fi" href="{u(f["path"])}">'
            f'<p class="fi-eyebrow">{html.escape(str(f.get("eyebrow") or "FEATURE"))}</p>'
            f'<h2 class="fi-title">{html.escape(f["title"])}</h2>'
            f'{thumbs(f)}'
            f'<p class="fi-lede">{html.escape(str(f.get("lede") or ""))}</p>'
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
    製品ごとに入手先と技適の状況を書いています。
    記事にした全製品の技適の状況は<a href="{u(GITEKI_PATH)}">技適チェック一覧</a>で見られます。</p>
  </section>
  {body}
</main>"""
        + footer(site)
    )


# ── 話題ページ・続報まとめ・週1メール(2026-11-10 本人了承) ──────────────
# 話題ページ: 記事のタグは836種類で表記もばらばらなので、config/topics.yaml で話題ごとにまとめ、
#   記事が min_posts 本以上ある話題だけ /topic/<slug>.html を作る(中身の薄いページを増やさない)。
# 続報まとめ: 同じ製品の記事が2本に分かれたら、古いほうに merged_into: <残す記事の slug> を書く。
#   古い記事は一覧・サイトマップから外れ、ページは残す記事へ転送する(検索の評価を1本に集める)。
#   残す記事の front matter に story: [{date, text}] を書くと「この製品の動き」が写真の上に出る。
#   日本上陸アラートの登録は古い slug のまま残るので、landing.json に古い slug も残す記事の状態で載せる。
# 週1メール: 毎週日曜、note の週まとめ(data/note/<日付>.md)と同じ5本と今週の日本上陸を送る。
#   登録は記事の終わりの欄から(alert/ の Worker が slug="weekly" として預かる)。中身は weekly.json。
TOPICS: list[dict] = []
MERGED: list[dict] = []


def load_topics(posts: list[dict]) -> list[dict]:
    f = ROOT / "config" / "topics.yaml"
    if not f.exists():
        return []
    cfg = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    mn = int(cfg.get("min_posts") or 5)
    out = []
    for t in cfg.get("topics") or []:
        ws = {str(x).strip().lower() for x in t.get("tags") or []}
        cs = [str(x).strip().lower() for x in t.get("contains") or []]

        def hit(p: dict) -> bool:
            tg = {str(x).strip().lower() for x in p.get("tags") or []}
            return bool(ws & tg) or any(c in x for c in cs for x in tg)
        items = [p for p in posts if hit(p)]
        if len(items) >= mn:
            out.append({**t, "path": f"topic/{t['slug']}.html", "posts": items})
    return out


def topics_of(p: dict) -> list[dict]:
    return [t for t in TOPICS if any(q is p for q in t["posts"])]


def topic_links(p: dict) -> str:
    ts = topics_of(p)
    if not ts:
        return ""
    links = "".join(f'<a href="{u(t["path"])}">{html.escape(t["label"])}<span>{len(t["posts"])}本</span></a>'
                    for t in ts)
    return (f'<nav class="tp-links" aria-label="この記事の話題"><p class="tp-links-h">この話題の記事をもっと見る</p>'
            f'{links}</nav>')


def jp_badge(p: dict) -> str:
    st = str((p.get("japan") or {}).get("status") or "").strip()
    if is_landed(p):
        return f'<span class="tp-jp now">日本で買える</span>'
    return f'<span class="tp-jp">{html.escape(st) if st else "日本未発売"}</span>'


def render_topic(site: dict, t: dict) -> str:
    s = site["site"]
    items = t["posts"]
    landed = [p for p in items if is_landed(p)]
    cards = []
    for p in items:
        c = card(site, p)
        c = c.replace('<article class="', f'<article data-g="{"now" if is_landed(p) else "other"}" class="', 1)
        cards.append(c.replace("</article>", jp_badge(p) + "</article>", 1))
    others = "".join(f'<a href="{u(x["path"])}">{html.escape(x["label"])}</a>' for x in TOPICS if x is not t)
    desc = (f'{t["desc"]}海外で発表された{len(items)}本の記事を、日本で買えるか・技適まで追っています。'
            + (f'うち{len(landed)}本は日本で買えます。' if landed else ""))
    chips = ('<div class="tp-chips"><button class="tp-chip on" type="button" data-f="all">すべて</button>'
             f'<button class="tp-chip" type="button" data-f="now">日本で買えるものだけ（{len(landed)}）</button></div>'
             if landed else "")
    return (
        head(site, f"{t['label']}の海外新製品と日本で買えるか — {s['title']}", desc, t["path"])
        + header(site)
        + f"""
<main class="wrap">
  <section class="hero hero-sm cat-weird">
    <p class="eyebrow"><a href="{u("topic/")}">TOPIC / 話題</a></p>
    <h1 class="hero-title">{html.escape(t['label'])}</h1>
    <p class="hero-sub">{html.escape(t['desc'])}海外で発表されたものを、日本で買えるか・技適はどうかまで追っています。</p>
    <div class="tp-stats">
      <div class="tp-stat"><b>{len(items)}</b><span>本の記事</span></div>
      <div class="tp-stat"><b>{len(landed)}</b><span>本が日本で買える</span></div>
      <div class="tp-stat"><b>{items[0]['date'].replace('-', '.')}</b><span>いちばん新しい記事</span></div>
    </div>
  </section>
  {chips}
  <section class="grid">{''.join(cards)}</section>
  <div class="tp-rel"><p class="tp-rel-h">ほかの話題</p>{others}</div>
</main>
<script>document.querySelectorAll('.tp-chip').forEach(function(b){{b.onclick=function(){{
document.querySelectorAll('.tp-chip').forEach(function(x){{x.classList.toggle('on',x===b)}});
document.querySelectorAll('.grid article').forEach(function(a){{a.style.display=(b.dataset.f==='all'||a.dataset.g===b.dataset.f)?'':'none'}})}}}})</script>"""
        + footer(site)
    )


def render_topics_index(site: dict) -> str:
    s = site["site"]
    rows = "".join(
        f'<a class="tp-card" href="{u(t["path"])}"><b>{html.escape(t["label"])}</b>'
        f'<span>{len(t["posts"])}本・日本で買える {sum(1 for p in t["posts"] if is_landed(p))}本</span>'
        f'<small>{html.escape(t["desc"])}</small></a>' for t in TOPICS)
    return (
        head(site, f"話題から探す — {s['title']}",
             "携帯ゲーム機・ミニPC・電子ペーパーなど、話題ごとに海外ガジェットの記事をまとめています。", "topic/")
        + header(site)
        + f"""
<main class="wrap">
  <section class="hero hero-sm">
    <p class="eyebrow">TOPIC / 話題</p>
    <h1 class="hero-title">話題から探す</h1>
    <p class="hero-sub">海外で発表されたガジェットの記事を、話題ごとにまとめています。それぞれ日本で買えるものだけに絞れます。</p>
  </section>
  <section class="tp-index">{rows}</section>
</main>"""
        + footer(site)
    )


def story_section(p: dict) -> str:
    st = [x for x in (p.get("story") or []) if isinstance(x, dict) and x.get("text")]
    if not st:
        return ""
    st.sort(key=lambda x: str(x.get("date") or ""), reverse=True)
    rows = "".join(f'<li><time datetime="{str(x.get("date") or "")}">{str(x.get("date") or "").replace("-", ".")}</time>'
                   f'<p>{html.escape(str(x["text"]))}</p></li>' for x in st)
    return f'<aside class="st-box"><h2>この製品の動き</h2><ol class="st-tl">{rows}</ol></aside>'


def merged_redirect(site: dict, m: dict, target: dict) -> str:
    base = site["site"]["base_url"].rstrip("/")
    to = f"{base}/{target['path']}"
    rel = u(target["path"])   # 転送はサイト内の相対(手元の確認でも本番へ飛ばない)、canonical は絶対
    return (f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>{html.escape(target["title"])}</title>'
            f'<link rel="canonical" href="{to}"><meta http-equiv="refresh" content="0;url={rel}">'
            f'<script>location.replace({json.dumps(rel)}+location.search+location.hash)</script></head>'
            f'<body><p>この記事は<a href="{rel}">こちら</a>にまとめました。</p></body></html>')


def weekly_form(s: dict) -> str:
    api = str(s.get("alert_api_url") or "").strip().rstrip("/")
    if not api or not s.get("weekly_mail"):
        return ""
    return (f'<aside class="wk-box"><p class="wk-h">週1回、海外ガジェット5選をメールで</p>'
            f'<p class="wk-t">毎週日曜の朝に1通。その週に紹介した5本と、日本で買えるようになった製品を届けます。</p>'
            f'<form class="wk-form" action="{html.escape(api)}/subscribe" method="post">'
            f'<input type="email" name="email" required placeholder="メールアドレス" autocomplete="email" aria-label="メールアドレス">'
            f'<input type="hidden" name="slug" value="weekly">'
            f'<input type="text" name="website" class="jp-alert-hp" tabindex="-1" autocomplete="off" aria-hidden="true">'
            f'<button type="submit">登録する</button></form><p class="wk-msg" aria-live="polite"></p>'
            f'<p class="wk-note">確認メールが届きます。解除はいつでもできます。'
            f'<a href="{u("privacy.html")}#alert">メールの扱いについて</a></p></aside>')


WEEKLY_JS = """<script>(function(){var f=document.querySelector('.wk-form');if(!f)return;
var msg=f.parentNode.querySelector('.wk-msg'),btn=f.querySelector('button');
f.addEventListener('submit',function(e){e.preventDefault();btn.disabled=true;msg.textContent='送信中…';
var d={};new FormData(f).forEach(function(v,k){d[k]=v});
fetch(f.action,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(d)})
.then(function(r){return r.json()}).then(function(j){msg.textContent=j.message||j.error||(j.ok?'確認メールを送りました':'登録できませんでした');
if(j.ok){f.querySelector('input[type=email]').value='';}btn.disabled=false;})
.catch(function(){msg.textContent='送れませんでした。時間をおいてもう一度お試しください';btn.disabled=false;});});})();</script>"""


def write_weekly_data(site: dict) -> None:
    """週1メールの中身(weekly.json)。いちばん新しい note の週まとめから、5本と今週の日本上陸を抜き出す。"""
    notes = sorted((ROOT / "data" / "note").glob("????-??-??.md"))
    if not notes:
        return
    f = notes[-1]
    raw = f.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", raw, re.S)
    fm, body = ((yaml.safe_load(m.group(1)) or {}), m.group(2)) if m else ({}, raw)
    secs = re.split(r"(?m)^## ", body)
    items, landed = [], []
    for sec in secs[1:]:
        head_line, _, rest = sec.partition("\n")
        mm = re.match(r"\d+\.\s*(.+)$", head_line.strip())
        if mm:
            img = re.search(r"!\[[^\]]*\]\((\S+?)\)", rest)
            url = re.search(r"詳しくは[:：]\s*(\S+)", rest)
            paras = [x.strip() for x in re.split(r"\n\s*\n", rest) if x.strip()
                     and not x.strip().startswith(("!", "詳しくは", "画像"))]
            text = re.sub(r"\*\*", "", paras[0]) if paras else ""
            sents = re.findall(r"[^。]+。", text)
            items.append({"title": mm.group(1).strip(), "image": img.group(1) if img else "",
                          "text": "".join(sents[:2]) or text[:120], "url": url.group(1) if url else ""})
        elif head_line.strip().startswith("今週の日本上陸"):
            for b in re.finditer(r"\*\*(.+?)\*\*\s*\n(.+?)(https://\S+)", rest, re.S):
                landed.append({"title": b.group(1).strip(), "text": b.group(2).strip(), "url": b.group(3)})
    data = {"date": f.stem, "title": str(fm.get("title") or ""), "lead": "", "items": items, "landed": landed}
    lead = [x.strip() for x in re.split(r"\n\s*\n", secs[0]) if x.strip()]
    data["lead"] = lead[0] if lead else ""
    (PUBLIC / "weekly.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n",
                                        encoding="utf-8")
    print(f"■ weekly.json: {f.stem} / {len(items)}本 + 日本上陸 {len(landed)}本")


HUB_CSS = """
/* 話題ページ・続報・週1メール(2026-11-10) */
.tp-stats{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0 6px}
.tp-stat{border:1px solid var(--rule-2);border-radius:4px;padding:10px 14px;min-width:120px}
.tp-stat b{display:block;font:700 22px/1.1 var(--disp);color:var(--ink)}
.tp-stat span{font:500 12px/1.4 var(--sans);color:var(--ink-3)}
.tp-chips{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0}
.tp-chip{padding:7px 12px;border:1px solid var(--rule-2);border-radius:999px;background:none;font:500 13px/1 var(--sans);color:var(--ink-2);cursor:pointer}
.tp-chip.on{border-color:var(--accent);color:var(--accent)}
.tp-jp{display:inline-block;margin:6px 0 0;font:600 11.5px/1 var(--sans);padding:4px 7px;border-radius:3px;background:var(--raised);color:var(--ink-2)}
.tp-jp.now{background:#e3f4ea;color:#1d7a46}
.tp-rel{margin:40px 0 0;padding:18px 0 0;border-top:1px solid var(--rule-2)}
.tp-rel-h{font-weight:600;margin:0 0 10px}
.tp-rel a{display:inline-block;margin:0 8px 8px 0;padding:6px 10px;border:1px solid var(--rule-2);border-radius:4px;font-size:13px;color:var(--ink-2);text-decoration:none}
.tp-rel a:hover{border-color:var(--accent);color:var(--accent)}
.tp-index{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;margin:24px 0 40px}
.tp-card{display:block;padding:16px;border:1px solid var(--rule-2);border-radius:6px;text-decoration:none;color:inherit}
.tp-card:hover{border-color:var(--accent)}
.tp-card b{display:block;font:700 16px/1.4 var(--sans);color:var(--ink)}
.tp-card span{display:block;margin:4px 0 0;font:500 12px/1.4 var(--mono);color:var(--accent)}
.tp-card small{display:block;margin:8px 0 0;font-size:13px;line-height:1.6;color:var(--ink-3)}
.tp-links{max-width:var(--measure);margin:28px 0 0}
.tp-links-h{margin:0 0 8px;font:600 13px/1.4 var(--sans);color:var(--ink-2)}
.tp-links a{display:inline-flex;gap:6px;align-items:baseline;margin:0 8px 8px 0;padding:7px 12px;border:1px solid var(--rule-2);border-radius:999px;font:500 13px/1 var(--sans);color:var(--ink)!important;text-decoration:none!important}
.tp-links a span{font:500 11px/1 var(--mono);color:var(--ink-3)}
.tp-links a:hover{border-color:var(--accent)}
.st-box{max-width:var(--measure);margin:22px 0;border:1px solid var(--rule-2);border-radius:6px;padding:16px 18px}
.st-box h2{margin:0 0 12px;font:700 15px/1.4 var(--sans)}
.st-tl{list-style:none;margin:0;padding:0}
.st-tl li{position:relative;padding:0 0 14px 20px;border-left:2px solid var(--rule-2);margin-left:5px}
.st-tl li:last-child{padding-bottom:0}
.st-tl li::before{content:"";position:absolute;left:-7px;top:3px;width:12px;height:12px;border-radius:50%;background:var(--bg);border:2px solid var(--accent)}
.st-tl time{font:600 12px/1 var(--mono);color:var(--accent)}
.st-tl p{margin:4px 0 0;font-size:14px;line-height:1.7;color:var(--ink-2)}
.wk-box{max-width:var(--measure);margin:28px 0 0;padding:16px 18px;border:1px solid var(--rule-2);border-radius:6px}
.wk-h{margin:0;font:700 15px/1.4 var(--sans);color:var(--ink)}
.wk-t{margin:6px 0 10px;font-size:13.5px;line-height:1.7;color:var(--ink-2)}
.wk-form{display:flex;gap:8px;flex-wrap:wrap}
.wk-form input[type=email]{flex:1;min-width:200px;padding:10px 12px;border:1px solid var(--rule-2);border-radius:4px;background:var(--bg);color:var(--ink);font-size:14px}
.wk-form button{padding:10px 16px;border:0;border-radius:4px;background:var(--ink);color:var(--bg);font:600 14px/1 var(--sans);cursor:pointer}
.wk-msg{margin:8px 0 0;font-size:13px;color:var(--accent)}
.wk-msg:empty{display:none}
.wk-note{margin:8px 0 0;font-size:12px;color:var(--ink-3)}
/* TOP の乗り継ぎ案内とカードの札(2026-11-11) */
.cx{border-top:1px solid var(--rule-2);margin-top:6px;padding:18px 0 26px}
.cx-title{display:flex;align-items:baseline;gap:12px;margin:0 0 14px;font:600 12px/1 var(--mono);letter-spacing:.2em;color:var(--ink)}
.cx-title span{font:400 11.5px/1 var(--sans);letter-spacing:0;color:var(--ink-2)}
.cx-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}
.cx-col{position:relative;display:flex;flex-direction:column;gap:10px;padding:4px 22px 4px 0;margin-right:22px;border-right:1px solid var(--rule);text-decoration:none!important;color:var(--ink)!important}
.cx-col:last-child{border-right:0;margin-right:0;padding-right:0}
.cx-code{font:500 10.5px/1 var(--mono);letter-spacing:.18em;color:var(--ink-2)}
.cx-code b{color:var(--accent);font-weight:600}
.cx-row{display:flex;align-items:flex-end;justify-content:space-between;gap:10px}
.cx-name{font:600 17px/1.35 var(--sans);color:var(--ink);transition:color .15s}
.cx-num{font:600 34px/1 var(--mono);letter-spacing:-.02em;color:var(--ink)}
.cx-num small{font:500 11px/1 var(--mono);letter-spacing:.1em;color:var(--ink-2);margin-left:4px}
.cx-thumbs{display:flex;gap:6px}
.cx-thumbs img{width:56px;height:56px;object-fit:contain;background:#fff;border-radius:3px;padding:3px;box-sizing:border-box}
.cx-list{display:flex;flex-wrap:wrap;gap:4px 14px;font:500 12.5px/1.6 var(--sans);color:var(--ink-2)}
.cx-list i{font-style:normal;font-family:var(--mono);font-size:11px;color:var(--ink-3);margin-left:4px}
.cx-go{font:600 12px/1 var(--mono);letter-spacing:.12em;color:var(--ink-2);transition:color .15s,letter-spacing .15s}
.cx-col:hover .cx-go,.cx-col:hover .cx-name{color:var(--accent)}
.cx-col:hover .cx-go{letter-spacing:.2em}
@media (max-width:700px){.cx-grid{grid-template-columns:1fr}.cx-col{border-right:0;margin:0;padding:14px 0;border-bottom:1px solid var(--rule)}
 .cx-col:last-child{border-bottom:0}.cx-num{font-size:26px}.cx-thumbs img{width:44px;height:44px}}
.cd-tags{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 0}
.cd-tag{font:500 11.5px/1 var(--sans);padding:5px 8px;border:1px solid var(--rule-2);border-radius:999px;color:var(--ink-2)!important;text-decoration:none!important}
.cd-tag:hover{border-color:var(--accent);color:var(--accent)!important}
.cd-tag.jp{border-color:#9fd3b4;background:#e3f4ea;color:#1d7a46!important}
[data-theme="dark"] .cd-tag.jp{border-color:#2f6b4b;background:#163526;color:#7fd8a6!important}
"""



def connections_section(posts: list[dict]) -> str:
    """発着案内板の下段「乗り継ぎ案内」。特集・話題・日本上陸への入口(2026-11-11 本人了承)。

    黒い箱を3つ並べた形は「かっこよくない」で没。案内板と同じ紺・等幅の字・細い線で板の中に組み込み、
    数字を大きく、中身(商品の写真・話題の名前)を見せる。
    """
    feats = [f for f in FEATURES_FOR_HINT if f.get("slug") != GITEKI_FEATURE_SLUG]
    landed = sorted((p for p in posts if is_landed(p)),
                    key=lambda p: str((p.get("japan") or {}).get("checked") or p["date"]), reverse=True)

    def th(url: str) -> str:
        return (f'<img src="{html.escape(sized(url, 160))}" alt="" loading="lazy" decoding="async" '
                f'referrerpolicy="no-referrer">' if url else "")
    ft_imgs = [str(x.get("image")) for f in feats for x in (f.get("products") or []) if x.get("image")][:3]
    ld_imgs = [card_image(p)[0] for p in landed[:3]]
    tp_top = sorted(TOPICS, key=lambda t: -len(t["posts"]))[:5]
    tp_list = "".join(f'<span>{html.escape(t["label"])}<i>{len(t["posts"])}</i></span>' for t in tp_top)
    cols = []
    if feats:
        cols.append(f'<a class="cx-col" href="{u("features.html")}"><span class="cx-code"><b>FTR</b> · GATE F</span>'
                    f'<span class="cx-row"><span class="cx-name">特集<br>いま買える物を比べる</span>'
                    f'<span class="cx-num">{len(feats):02d}<small>本</small></span></span>'
                    f'<span class="cx-thumbs">{"".join(th(x) for x in ft_imgs)}</span><span class="cx-go">特集を見る →</span></a>')
    if TOPICS:
        cols.append(f'<a class="cx-col" href="{u("topic/")}"><span class="cx-code"><b>TPC</b> · GATE T</span>'
                    f'<span class="cx-row"><span class="cx-name">話題から探す<br>ジャンルでまとめ読み</span>'
                    f'<span class="cx-num">{len(TOPICS):02d}<small>話題</small></span></span>'
                    f'<span class="cx-list">{tp_list}</span><span class="cx-go">話題を選ぶ →</span></a>')
    if landed:
        cols.append(f'<a class="cx-col" href="{u("jpn.html")}"><span class="cx-code"><b>JPN</b> · ARRIVALS</span>'
                    f'<span class="cx-row"><span class="cx-name">日本上陸<br>あとから日本に来た物</span>'
                    f'<span class="cx-num">{len(landed):02d}<small>本</small></span></span>'
                    f'<span class="cx-thumbs">{"".join(th(x) for x in ld_imgs)}</span><span class="cx-go">上陸した物を見る →</span></a>')
    if not cols:
        return ""
    return (f'<nav class="cx" aria-label="乗り継ぎ案内"><p class="cx-title">CONNECTIONS<span>乗り継ぎ案内</span></p>'
            f'<div class="cx-grid">{"".join(cols)}</div></nav>')


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
    <p class="hero-sub">{html.escape(cat['description'])}</p>
  </section>
  <section class="grid">{body}</section>
</main>"""
        + footer(site)
    )


def sized(url: str, w: int) -> str:
    """一覧の小さな枠に出す写真を、メーカーの配信元に縮めて出してもらう(2026-11-05)。
    公式ページの元画像は1枚で数百KB〜1MBあり、TOP の重さの大半だった。
    URL で幅を指定できると分かっている配信元(Shopify・Sanity)だけ書き換える。
    Kickstarter などは URL に署名があり、書き換えると表示できなくなるので触らない。"""
    if not url.startswith("http"):
        return url
    pu = urlparse(url)
    host = pu.netloc.lower()
    if "/cdn/shop/" in pu.path or host == "cdn.shopify.com":
        key = "width"
    elif host == "cdn.sanity.io":
        key = "w"
    else:
        return url
    q = [kv for kv in pu.query.split("&") if kv and not re.match(rf"(?:{key}|height|h|crop)=", kv)]
    q.append(f"{key}={w}")
    return pu._replace(query="&".join(q)).geturl()


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


def inline_photo(im: dict, title: str) -> str:
    """本文中に差し込む製品写真1枚。切り抜かずに全体を見せる。読み込めなければ figure ごと消える。"""
    cap = im.get("caption") or ""
    credit = im.get("credit") or ""
    parts = []
    if cap:
        parts.append(html.escape(cap))
    if credit:
        parts.append(f'<span class="inline-credit">出典: {html.escape(credit)}</span>')
    figcap = f'<figcaption>{" ".join(parts)}</figcaption>' if parts else ""
    return f'<figure class="inline-shot">{ext_img(im["url"], cap or title)}{figcap}</figure>'


def inline_clip(c: dict, title: str) -> str:
    """本文中に差し込む動く映像1つ(音なし・くり返し)。画面に入ってから読み込み、外れたら止める(CLIP_JS)。

    写真と同じ枠に入れるので、読者には動く写真に見える。出典はメーカー公式の YouTube 動画へのリンク。
    """
    cap = html.escape(c["caption"]) if c["caption"] else ""
    credit = html.escape(c["credit"] or "メーカー公式 YouTube")
    if c["source"]:
        credit = f'<a href="{html.escape(c["source"])}" rel="nofollow noopener" target="_blank">{credit}</a>'
    figcap = f'<figcaption>{cap}<span class="inline-credit">映像の出典: {credit}</span></figcaption>'
    poster = f' poster="{u("clips/" + c["poster"])}"' if c["poster"] else ""
    return (f'<figure class="inline-shot inline-clip">'
            f'<video muted loop playsinline preload="none" width="960" height="540"{poster} '
            f'data-clip="{u("clips/" + c["file"])}" aria-label="{html.escape(c["caption"] or title)}"></video>'
            f'{figcap}</figure>')


# 映像は画面に入ったときだけ読み込んで再生し、外れたら止める(ページの重さと通信量を抑える)。
# 動きを減らす設定の人には自動再生せず、止めた絵に再生ボタンだけ出す
CLIP_JS = """<script>(function(){var vs=document.querySelectorAll('video[data-clip]');if(!vs.length)return;
var calm=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
function load(v){if(!v.src){v.src=v.dataset.clip;}}
if(calm||!('IntersectionObserver' in window)){vs.forEach(function(v){load(v);v.controls=true;});return;}
var io=new IntersectionObserver(function(es){es.forEach(function(e){var v=e.target;
if(e.isIntersecting){load(v);var p=v.play();if(p&&p.catch)p.catch(function(){v.controls=true;});}else{v.pause();}});},{rootMargin:'200px 0px'});
vs.forEach(function(v){io.observe(v);});})();</script>"""


def insert_inline_media(body_html: str, media: list[str]) -> str:
    """本文の各 <h2 の直前にメディアを1つずつ割り当てて差し込む（上から順）。

    h2 は markdown が最上位にしか出さないので、分割しても表やリストの中には入らない。
    スロットより多いメディアは最後のスロットにまとめる。h2 が無ければ本文の後ろに全部足す。
    """
    if not media:
        return body_html
    pieces = re.split(r"(?=<h2[\s>])", body_html)
    # pieces[0] は最初の h2 より前の導入部。h2 で始まる断片がスロットになる
    n_slots = len(pieces) - 1
    if n_slots < 1:
        return body_html + _media_group(media)
    groups: list[list[str]] = [[] for _ in range(n_slots)]
    for i, m in enumerate(media):
        groups[min(i, n_slots - 1)].append(m)
    out = [pieces[0]]
    for g, piece in zip(groups, pieces[1:]):
        out.append(_media_group(g) + piece)
    return "".join(out)


def _media_group(items: list[str]) -> str:
    if not items:
        return ""
    cls = "inline-media inline-media-grid" if len(items) > 1 else "inline-media"
    return f'<div class="{cls}">{"".join(items)}</div>'


def render_embeds(p: dict) -> tuple[list[tuple[str, str]], bool]:
    """front matter の embeds を、プラットフォーム公式の埋め込みHTMLに変換する。

    画像を自社サーバーにコピーせず、権利者が公開している投稿をそのまま表示する方式。
    転載にあたらないため、メーカー公式アカウントの製品写真を合法的に見せられる。
    戻り値: ([(種別, HTML), ...], X埋め込みスクリプトが必要か)。種別は x / youtube / link。
    """
    items = p.get("embeds") or []
    if not items:
        return [], False
    blocks, needs_x = [], False
    for e in items:
        kind = (e.get("type") or "").lower()
        url = e.get("url", "")
        caption = html.escape(e.get("caption", ""))
        if kind in ("x", "twitter"):
            needs_x = True
            blocks.append(("x",
                f'<figure class="embed embed-x">'
                f'<blockquote class="twitter-tweet" data-lang="ja" data-dnt="true">'
                f'<a href="{html.escape(url)}"></a></blockquote>'
                f'{f"<figcaption>{caption}</figcaption>" if caption else ""}</figure>'))
        elif kind == "youtube":
            vid = html.escape(e.get("id", ""))
            blocks.append(("youtube",
                f'<figure class="embed embed-video">'
                f'<iframe src="https://www.youtube-nocookie.com/embed/{vid}" '
                f'title="{caption or "YouTube"}" loading="lazy" allowfullscreen '
                f'referrerpolicy="strict-origin-when-cross-origin"></iframe>'
                f'{f"<figcaption>{caption}</figcaption>" if caption else ""}</figure>'))
        elif kind == "link":
            # 権利上そのまま出せない画像は、元記事へのリンクカードで代替する
            title = html.escape(e.get("title", url))
            pub = html.escape(e.get("publisher", ""))
            blocks.append(("link",
                f'<figure class="embed embed-link">'
                f'<a href="{html.escape(url)}" rel="nofollow noopener" target="_blank">'
                f'<span class="embed-link-title">{title}</span>'
                f'<span class="embed-link-pub">{pub} — 製品画像は元記事でご覧いただけます</span>'
                f'</a></figure>'))
    return blocks, needs_x


# 記事の末尾に、分野の合う特集への案内を1行出す(2026-10-23 AI 会議の提案 20261022-monetizer-2、本人採用)。
# 特集には日本で買える製品の購入先が載っているのに、記事から特集へ行く道がナビの「特集」しかなかった。
# 記事生成の指示は変えずにビルドで付ける(技適の本文リンクと同じ考え方。過去記事にも効く)。
# 合うかどうかは、まず特集の related に入っている記事か、次に題名とタグの言葉で決める。
# 技適の特集は本文の「技適」のリンクで足りるので出さない。白いガジェットは言葉では決めにくいので related だけ。
# 固定の広告枠にしないため、合う特集が無い記事には何も出さない。
FEATURE_HINT_WORDS = {
    "eink-devices": ("電子ペーパー", "e ink", "eink", "e-ink"),
    "odd-keyboards": ("キーボード", "keyboard"),
    "retro-design": ("レトロ", "ゲームボーイ", "ファミコン", "retro", "anbernic"),
    "smart-glasses": ("スマートグラス", "arグラス", "aiグラス", "ディスプレイグラス", "xreal", "rayneo", "ray-ban"),
}
FEATURES_FOR_HINT: list[dict] = []   # main() が特集を読んだあとに入れる


def feature_buy_now(p: dict) -> str:
    """「日本で買える？使える？」の節の中に、日本で今すぐ買える物の特集への入口を出す(2026-11-01 本人)。

    特集は入口がメニューと記事末の1行しか無く、月に十数回しか開かれていなかった。読者はその製品が
    欲しくて来ているが、まだ日本で買えないことが多い。そこで、上陸アラートの登録欄(待つ)の隣に
    「今すぐ買うなら」の選択肢として特集を置く。対象は特集の related に入れた記事だけ(言葉の一致では
    ずれた特集が出るため)。特集に japan_hint が無ければ出さない。日本上陸済みの記事には出さない。
    リンクに ?from=japan を付けて、GA4 でこの入口から来た数を見分ける。
    """
    if is_landed(p):
        return ""
    hit = next((f for f in FEATURES_FOR_HINT
                if f.get("japan_hint") and p["slug"] in (f.get("related") or [])), None)
    if not hit:
        return ""
    n = len(hit.get("products") or [])
    return (f'<aside class="jp-buynow"><p class="jp-head"><span class="jp-badge jp-badge-buy">今すぐ買うなら</span></p>'
            f'<p class="jp-buynow-text">{html.escape(str(hit["japan_hint"]))}</p>'
            f'<a class="jp-buynow-link" href="{u(hit["path"])}?from=japan">'
            f'{html.escape(str(hit.get("title") or ""))}（{n}製品）</a></aside>')


def feature_hint(p: dict) -> str:
    # 節の中に「今すぐ買うなら」を出した記事では、末尾の1行は重ねて出さない
    if feature_buy_now(p):
        return ""
    feats = [f for f in FEATURES_FOR_HINT if f.get("slug") != GITEKI_FEATURE_SLUG]
    hit = next((f for f in feats if p["slug"] in (f.get("related") or [])), None)
    if not hit:
        text = " ".join([str(p.get("title") or "")] + [str(x) for x in (p.get("tags") or [])]).lower()
        hit = next((f for f in feats
                    if any(w in text for w in FEATURE_HINT_WORDS.get(f.get("slug"), ()))), None)
    if not hit:
        return ""
    return (f'<p class="feature-hint"><span class="feature-hint-label">特集</span>'
            f'この分野で、いま日本で買える物を製品ごとにまとめています。'
            f'<a href="{u(hit["path"])}?from=hint">{html.escape(str(hit.get("title") or ""))}</a></p>')


YORIMICHI: list[dict] = []  # 寄り道欄の棚。main が特集を読んだあとに詰める


def build_yorimichi(s: dict, features: list[dict]) -> list[dict]:
    """寄り道欄(偶然の出会い)の棚を、特集の商品から作る。

    GT の記事はまだ日本で買えない製品が多く、読者は「調べに来ている」のでアフィリエイトが押されにくい。
    ガジェット好きは「おっ、なにこれ」と思った物をその場で買うので、記事の終わりに
    「海外で話題、もう日本で買える」ちょっと変わった物を3つ置く(2026-11-08 本人の発案、モックB を採用)。
    載せるのは特集で入手方法・技適を確かめた商品のうち、hook(一文)があり、報酬になるリンクがある物だけ。
    """
    pool, seen = [], set()
    for f in features:
        for it in f.get("products") or []:
            name, hook, img = str(it.get("name") or ""), str(it.get("hook") or ""), str(it.get("image") or "")
            if not (name and hook and img) or name in seen:
                continue
            url = str(it.get("url") or "")
            mer = merchant_of(url)
            if mer not in ("amazon", "rakuten", "yahoo"):
                url, mer = str((it.get("rakuten") or {}).get("url") or ""), "rakuten"
            if not url:
                continue
            link, is_aff = affiliate_url(s, url, mer)
            if not is_aff:
                continue
            seen.add(name)
            brand = str(it.get("brand") or "")
            pm = re.match(r"^([^(（]+?)\s*(?:[(（].*)?$", str(it.get("price") or "").strip())
            pool.append({
                "name": name if (not brand or brand.lower() in name.lower()) else f"{brand} {name}",
                "hook": hook, "img": img, "price": pm.group(1).strip() if pm else "",
                "link": link, "store": alt_store(url, mer), "feature": u(f["path"]),
            })
    return pool


def yorimichi_section(p: dict) -> tuple[str, bool]:
    """記事の終わりの「寄り道」欄。記事ごとに決まった3つを出し、「ほかのを見る」で入れ替える。"""
    if len(YORIMICHI) < 3:
        return "", False
    import random
    own = {str(x.get("name") or "") for x in (p.get("alternatives") or []) + (p.get("gear") or [])}
    cand = [x for x in YORIMICHI if x["name"] not in own]
    # 同じ記事は同じ3つ(ビルドのたびに変わると、検索エンジンには中身が毎日変わるページに見える)
    picks = random.Random(p["slug"]).sample(cand, 3)

    def card(x: dict) -> str:
        return (f'<a class="yr-card" href="{html.escape(x["link"])}" rel="nofollow sponsored noopener" target="_blank">'
                f'<span class="yr-img"><img src="{html.escape(x["img"])}" alt="{html.escape(x["name"])}" loading="lazy" '
                f'decoding="async" referrerpolicy="no-referrer"></span>'
                f'<span class="yr-hook">{html.escape(x["hook"])}</span>'
                f'<span class="yr-meta">{html.escape(x["name"])}{"・" + html.escape(x["price"]) if x["price"] else ""}</span>'
                f'<span class="yr-store">{html.escape(x["store"])}で見る ↗</span></a>')
    return (f'<section class="yr" data-yr="{u("yorimichi.json")}"><div class="yr-head"><p class="yr-title">'
            f'<span class="yr-eyebrow">寄り道</span>海外で話題、もう日本で買える<span class="yr-ad">広告</span>'
            f'<small>編集部が特集で確かめた、ちょっと変わったガジェット</small></p>'
            f'<button class="yr-shuffle" type="button" hidden>↻ ほかのを見る</button></div>'
            f'<div class="yr-grid">{"".join(card(x) for x in picks)}</div></section>'), True


# 「ほかのを見る」。押したときに初めて棚(yorimichi.json)を読み、いま出ていない物から3つ選ぶ
YORIMICHI_JS = """<script>
(()=>{const s=document.querySelector('.yr');if(!s)return;const b=s.querySelector('.yr-shuffle'),g=s.querySelector('.yr-grid');
b.hidden=false;let pool=null,shown=[...g.querySelectorAll('.yr-card')].map(a=>a.href);
const e=t=>String(t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
b.addEventListener('click',async()=>{try{if(!pool)pool=await(await fetch(s.dataset.yr)).json();}catch(_){return}
let c=pool.filter(x=>!shown.includes(x.link));if(c.length<3){shown=[];c=pool.slice()}
c.sort(()=>Math.random()-.5);c=c.slice(0,3);shown=shown.concat(c.map(x=>x.link));
g.innerHTML=c.map(x=>`<a class="yr-card yr-in" href="${e(x.link)}" rel="nofollow sponsored noopener" target="_blank"><span class="yr-img"><img src="${e(x.img)}" alt="${e(x.name)}" decoding="async" referrerpolicy="no-referrer"></span><span class="yr-hook">${e(x.hook)}</span><span class="yr-meta">${e(x.name)}${x.price?'・'+e(x.price):''}</span><span class="yr-store">${e(x.store)}で見る ↗</span></a>`).join('');
if(window.gtag)gtag('event','yorimichi_shuffle');});})();
</script>"""


def videos_after_section(p: dict) -> str:
    """クラファン記事に、公開後に出た YouTube の実機動画を出す(scripts/cf_videos.py が足す)。

    出資から出荷まで数か月かかる間に、実機レビューや出資者への到着報告が YouTube に出る。
    公開時点の記事はキャンペーンの宣伝動画しか無いので、「本当に届くのか・実物はどうか」を
    後から出た動画で見せる(2026-11-01 本人の提案)。題名・チャンネル・公開日は add が YouTube から取った値。
    """
    items = [v for v in (p.get("videos_after") or []) if re.match(r"^[A-Za-z0-9_-]{11}$", str(v.get("id") or ""))]
    if not items:
        return ""
    figs = []
    for v in items:
        vid = html.escape(str(v["id"]))
        title = html.escape(str(v.get("title") or "YouTube"))
        meta = html.escape(str(v.get("channel") or ""))
        if v.get("published"):
            meta += f' / {str(v["published"]).replace("-", ".")} 公開'
        note = f'<span class="va-note">{html.escape(str(v["note"]))}</span>' if v.get("note") else ""
        figs.append(
            f'<figure class="embed embed-video">'
            f'<iframe src="https://www.youtube-nocookie.com/embed/{vid}" title="{title}" loading="lazy" '
            f'allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe>'
            f'<figcaption>{note}<span class="va-meta">{title}（{meta}）</span></figcaption></figure>')
    added = max(str(v.get("added") or "") for v in items)
    return (f'<section class="embeds videos-after"><h2>あとから追加した実機の動画</h2>'
            f'<p class="va-lead">記事の公開後に見つけた、実機のレビューや開封・動作の動画です。'
            f'クラウドファンディングは出荷まで時間がかかるので、その間に出た動画を足しています（最終追加 {added.replace("-", ".")}）。</p>'
            + "".join(figs) + '</section>')


def render_post(site: dict, p: dict, others: list[dict]) -> str:
    s = site["site"]
    cat = site["categories"].get(p.get("category"), {"label": "その他", "slug": "misc"})
    embed_blocks, needs_x = render_embeds(p)
    # 出発地 → 成田。この媒体がやっているのは「海外の製品を日本に着陸させること」なので、
    # 出所が分かる記事ではそれを1行で見せる。分からない記事では何も出さない。
    o_code, o_city = post_origin(site, p)
    route = ""
    # 日本発の製品に「✈ NRT 日本」を出すと意味を成さないので、その場合は出さない。
    if o_code not in ("---", "JPN", "NRT", "HND", "KIX"):
        route = (f'<span class="dot"></span><span class="meta-route">'
                 f'{html.escape(o_code)}{f" {html.escape(o_city)}" if o_city else ""}'
                 f'<i aria-hidden="true">✈</i>NRT 日本</span>')
    # ヒーローの優先順位: 1枚目の写真 → 最初のYouTube → 最初のその他の埋め込み → 生成カード。
    # 写真が1枚目にある記事ではYouTubeも本文中に回すので、1枚目の写真が埋もれない。
    # 外部URLのときは自社サーバーに複製せず、権利者のサーバーを直接参照する。
    fallback = u("cards/" + p["slug"] + ".png")
    imgs = p.get("images") or []
    has_photo = bool(p.get("thumbnail"))
    videos = [h for k, h in embed_blocks if k == "youtube"]
    others = [h for k, h in embed_blocks if k != "youtube"]
    lead_embed = ""
    if has_photo:
        inline_videos = videos
    elif videos:
        lead_embed, inline_videos = videos[0], videos[1:]
    elif others:
        lead_embed, others, inline_videos = others[0], others[1:], []
    else:
        inline_videos = []
    if lead_embed:
        hero_block = f'<section class="embeds embeds-lead">{lead_embed}</section>'
    elif has_photo:
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
    # 本文中に差し込むメディア。動くものが最も価値が高いので動画を先に、写真(2枚目以降)を続ける。
    clip_html = [inline_clip(c, p["title"]) for c in p.get("clips") or []]
    media = inline_videos + clip_html + [inline_photo(im, p["title"]) for im in imgs[1:]]
    body_with_media = insert_inline_media(p["body_html"], media)
    if clip_html:
        body_with_media += CLIP_JS
    alert_html = alert_form(s, p)
    body_with_media = style_japan_section(body_with_media, p, bool(alert_html))
    body_with_media = insert_alert_form(body_with_media, feature_buy_now(p) + alert_html)
    embeds_html = ('<section class="embeds"><h2>関連する投稿・動画</h2>'
                   + "".join(others) + '</section>') if others else ""
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
                      "logo": {"@type": "ImageObject", "url": f"{base}/ogp/default.png"},
                      # sameAs は「この組織の公式アカウントはこれ」という宣言。
                      # 検索エンジンが媒体とアカウントを同一の存在として扱えるようになる。
                      **({"sameAs": [f"https://x.com/{str(s['x_account']).lstrip('@')}"]}
                         if str(s.get("x_account") or "").strip() else {})},
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

    jp_html, jp_aff = japan_section(s, p)
    jp_html += giteki_followup_section(p)
    buy_html, buy_aff = buy_section(s, p)
    alts_html, alts_aff = alternatives_section(s, p)
    gear_html, gear_aff = gear_section(s, p)
    yr_html, yr_aff = yorimichi_section(p)
    has_aff = jp_aff or buy_aff or alts_aff or gear_aff or yr_aff
    modified = p.get("modified") or ""
    upd_meta = (f'<span class="dot"></span><span class="meta-updated">更新 {modified.replace("-", ".")}</span>'
                if modified and modified > p["date"] else "")
    # ステマ規制。アフィリエイトリンクがある記事は、本文の先頭で広告を含む旨を示す。
    # 「サイトのどこかに書いてある」では足りないため、記事ごとに出す。
    disclosure = ""
    if has_aff:
        text = str((s.get("affiliate") or {}).get("disclosure") or "この記事にはアフィリエイト広告を含みます")
        disclosure = f'<p class="ad-notice">{html.escape(text)}</p>'

    # og:type=article と公開・更新時刻。SNSやDiscoverが「記事」として扱う手がかりになる。
    _pub, _mod = p["date"], p.get("modified") or p["date"]
    og_times = (f'<meta property="article:published_time" content="{_pub}T09:00:00+09:00">'
                f'<meta property="article:modified_time" content="{_mod}T09:00:00+09:00">')
    ld = og_times + "".join(
        f'<script type="application/ld+json">{json.dumps(d, ensure_ascii=False, separators=(",", ":"))}</script>'
        for d in (article_ld, breadcrumb_ld, faq_ld) if d)

    return (
        head(site, f"{p.get('seo_title') or p['title']} — {s['title']}", p["excerpt"], p["path"],
             ld + ('\n<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'
                   if needs_x else ""),
             # thumbnail は外部URLのまま、生成アイキャッチはサイト相対で渡す
             image=(str(p["thumbnail"]) if p.get("thumbnail")
                    else f"ogp/{p['slug']}.png"),
             og_type="article")
        + header(site)
        + f"""
<main class="wrap article-wrap">
  <article class="article cat-{p.get("category", "misc")}">
    <p class="eyebrow"><a href="{u("category/" + cat['slug'] + ".html")}"><span class="eyebrow-code">{cat.get('code','---')}</span>{html.escape(cat['label'])}</a></p>
    <h1 class="article-title">{title_text(p['title'])}</h1>
    {f'<p class="article-lede">{html.escape(str(p["kicker"]))}</p>' if p.get('kicker') else ''}
    {f'<aside class="pick-callout"><p class="pick-callout-head">編集部ピックアップ</p><p class="pick-callout-note">{html.escape(p["pick_note"])}</p></aside>' if p.get('pick') and p.get('pick_note') else (f'<p class="pick-callout pick-callout-bare">編集部ピックアップ<span>運営者が選んだガジェットです</span></p>' if p.get('pick') else '')}
    {disclosure}
    <p class="article-meta"><time datetime="{p['date']}">{p['date'].replace('-', '.')}</time><span class="dot"></span>{p['reading_min']} MIN READ{upd_meta}{route}</p>
    {jp_html}
    {story_section(p)}
    {hero_block}
    <div class="prose">{body_with_media}</div>
    {videos_after_section(p)}
    {embeds_html}
    {buy_html}
    {alts_html}
    {gear_html}
    {feature_hint(p)}
    {topic_links(p)}
  {faq_html}
  {yr_html}
  {weekly_form(s)}
  {sources}
  </article>
  {ad_unit(s, "article_end")}
  {rel_html}
</main>{ALERT_JS if alert_html else ""}{YORIMICHI_JS if yr_html else ""}{WEEKLY_JS if s.get("weekly_mail") else ""}"""
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
    if str(s.get("click_beacon_url") or "").strip():
        analytics.append(
            "<li><strong>紹介リンクのクリック数</strong> — どの記事の紹介リンクが押されたかを"
            "数えるため、押されたときにページの場所とストアの種類だけを送っています。"
            "Cookie や個人を特定できる情報は使っていません。</li>")
    if str(s.get("analytics_id") or "").strip():
        analytics.append(
            "<li><strong>Google アナリティクス</strong> — Cookie を使用してアクセス状況を"
            "集計します。ブラウザの設定で Cookie を無効にすると収集を拒否できます。</li>")
    analytics_block = ("<ul>" + "".join(analytics) + "</ul>") if analytics else (
        "<p>アクセス解析ツールは利用していません。</p>")

    # 日本上陸アラート。メールアドレスを預かるので、何に使い・どこに置き・どう消すかを書く。
    # alert_api_url が空なら欄そのものが出ないので、ここも出さない
    alert_block = ""
    if str(s.get("alert_api_url") or "").strip():
        alert_block = """
      <h2 id="alert">日本上陸アラート（メール通知）</h2>
      <p>記事の「日本で買える？使える？」の欄から登録いただいたメールアドレスは、
      <strong>その製品が日本で買えるようになったことを1通お知らせする目的にのみ</strong>使用します。
      確認メールのリンクを開いた時点で登録が完了し、それまでお知らせは送りません。
      広告のメールは送りません。</p>
      <p>記事の終わりの欄から「週1回のメール」に登録いただいた場合は、毎週日曜に1通、その週に紹介した海外ガジェットと
      日本で買えるようになった製品のお知らせを送ります。こちらも確認メールのリンクを開いた時点で登録が完了し、
      メール内のリンクからいつでも解除できます。</p>
      <p>メールアドレスと登録した記事の組み合わせは、Cloudflare, Inc. のデータベース（Cloudflare D1）に
      保存し、メールの送信には Resend, Inc. のサービスを利用します。いずれも送信とその記録に
      必要な範囲でのみ使用し、ご本人の同意なく第三者に提供することはありません。
      登録時の迷惑登録対策として、接続元のネットワークアドレスを復元できない形（ハッシュ）で
      1時間だけ数えています。</p>
      <p>登録は、お知らせのメールおよび確認完了ページにある「登録を解除する」のリンクから
      いつでも解除できます。解除後はそのアドレスにお知らせを送りません。
      データの削除をご希望の場合は、下記のお問い合わせ窓口までご連絡ください。</p>"""

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
{alert_block}

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
    # 公式アカウント。読者が媒体の実在を確かめる場所なので運営ページにも出す。
    _xa = str(site["site"].get("x_account") or "").strip().lstrip("@")
    x_row = (f'<li>公式X： <a href="https://x.com/{html.escape(_xa)}" '
             f'target="_blank" rel="noopener">@{html.escape(_xa)}</a></li>') if _xa else ""
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
        <li>製品情報・取材のご連絡： <a href="mailto:{s.get('press_email','')}">{html.escape(s.get('press_email',''))}</a>
        （掲載基準は<a href="{u("media.html")}">メーカー・広報の方へ</a>をご確認ください）</li>
{x_row}
      </ul>
      <p>運営： {html.escape(s['author'])}</p>
      <p>個人情報・Cookie・アフィリエイトの取り扱いは
      <a href="{u("privacy.html")}">プライバシーポリシー</a>をご確認ください。</p>
    </div>
  </article>
</main>"""
    return head(site, f"運営について — {s['title']}", "編集方針・免責・お問い合わせ", "about.html") + header(site) + body + footer(site)


def render_media(site: dict, posts: list[dict]) -> str:
    """メディアキット(企業・メーカー向け)。PR TIMES 登録(2026-09-02 承認)を営業導線に変えるページ。

    2026-11-07 作り直し(本人「はい」): 海外メーカーが「日本に出る前から GT に載りたい」と思う材料を前に出す。
    GT が売れるのは閲覧数ではなく「日本に来る前に日本語の記事があり、待っている読者を預かり、
    買えるようになったら知らせる」流れ。数字はすべて記事の front matter から数える(手で書かない)。
    海外メーカー本人が読めるよう、英語の要約も付ける。

    **できないことを盛らない。** 署名記事は無い、閲覧数は載せない(小さいため、聞かれたら答える)。
    実機レビューは 2026-11-07 本人「実機もらえればレビューする」で「提供・貸し出しがあればレビューする」に変えた
    (公開前の確認はさせない・提供と明記する)。PR TIMES の審査でもここを正直に伝えて通っている(docs/PRTIMES申請.md)。
    誇張すると企業側の期待とのズレが後で問題になる。
    """
    s = site["site"]
    n = len(posts)
    dates = sorted(p["date"] for p in posts)
    since = dates[0].replace("-", ".") if dates else ""
    landed_after = count_landed_after(posts)
    waiting = sum(1 for p in posts if not is_landed(p))
    press = html.escape(s.get("press_email", ""))
    contact = html.escape(s.get("contact_email", ""))
    _xa = str(s.get("x_account") or "").strip().lstrip("@")
    x_row = (f'<li>公式X： <a href="https://x.com/{html.escape(_xa)}" '
             f'target="_blank" rel="noopener">@{html.escape(_xa)}</a></li>') if _xa else ""
    jpn = u("jpn.html")
    giteki = u(GITEKI_PATH)
    body = f"""
<main class="wrap article-wrap">
  <article class="article">
    <p class="eyebrow">FOR BRANDS / MEDIA KIT</p>
    <h1 class="article-title">メーカー・広報の方へ</h1>
    <div class="prose">
      <p>{html.escape(s['title'])}は、海外で発表されて、まだ日本語の記事が無いガジェットを毎日紹介するメディアです。
      とくにクラウドファンディング発の新製品を優先して扱います。
      日本での発売が決まる前から日本語の記事を出し、その製品を待つ読者を預かり、日本で買えるようになったらお知らせします。</p>

      <h2>日本に来る前から、日本の読者に届けます</h2>
      <ol>
        <li><strong>海外で発表された時点で、日本語の記事を出します。</strong>
        日本で製品名を検索した人が最初に読む記事になることを目指しています。</li>
        <li><strong>「日本で買える？使える？」を必ず書きます。</strong>
        技適(電波法)・国内流通・日本語対応を確かめ、技適が確認できない製品は毎週、総務省のデータベースで引き直しています
        (<a href="{giteki}">技適チェック一覧</a>)。</li>
        <li><strong>待っている読者をメールで預かります。</strong>
        まだ日本で買えない製品の記事には「日本上陸アラート」の登録欄があり、日本で発売・予約・国内クラウドファンディングが
        始まったことを確かめたら、登録した読者に1通だけ知らせます。</li>
      </ol>

      <h2>これまでの数字</h2>
      <ul>
        <li>公開記事: <strong>{n}本</strong>({since} 〜、毎日3本)</li>
        <li>先に紹介した製品のうち、公開したあとで日本に来た製品: <strong>{landed_after}本</strong>
        (<a href="{jpn}">日本上陸した製品</a>)</li>
        <li>日本上陸アラートの登録欄がある記事(まだ日本で買えない製品): <strong>{waiting}本</strong></li>
      </ul>
      <p>数字はこのページを作り直すたびに記事のデータから数えています。閲覧数などはお問い合わせいただければお答えします。</p>

      <h2>取り上げやすくなる情報</h2>
      <p>次のものがそろっていると、記事にしやすくなります。日本語の資料が無くても構いません(英語で大丈夫です)。</p>
      <ul>
        <li>価格・発売時期・仕様の一次情報(公式ページ・クラウドファンディングのページ・プレスキット)</li>
        <li>記事に使ってよい公式の画像・動画</li>
        <li>日本での展開の予定(発売・国内クラウドファンディング・代理店)と、技適の取得予定</li>
        <li>実機の提供・貸し出しの可否(いただければレビュー記事にします)</li>
      </ul>

      <h2>掲載基準</h2>
      <p>大手の新製品発表やプレスリリースの転載は扱いません。判断基準は次の3つです。</p>
      <ul>
        <li>海外で報じられて、まだ日本語の記事が無いこと</li>
        <li>価格・仕様・調達額など、数字が確認できること</li>
        <li>「日本から買えるか・使えるか」が論点になること</li>
      </ul>
      <p>クラウドファンディング案件は「まだ製品ではない」ことを必ず明記します。
      出資は購入ではなく、納期遅延や仕様変更のリスクがある前提で書きます。</p>

      <h2>実機レビューについて</h2>
      <p><strong>実機を提供・貸し出していただいた製品は、編集部が実際に使ってレビュー記事にします。</strong>
      良い点だけでなく、気になった点もそのまま書きます。記事の内容を公開前に確認していただくことはできませんが、
      事実の誤りのご指摘には対応します。記事には「メーカーから提供(貸し出し)を受けた製品」であることを明記します。</p>
      <p>実機の無い製品は、これまでどおり海外の一次情報をもとに編集部が構成した記事でお伝えします。</p>

      <h2>広告・PRの表記について</h2>
      <p>報酬を受けて掲載する場合は、本文中に<strong>【PR】</strong>と明記します(景品表示法の指定告示に従います)。
      無表記の記事はすべて編集部の独立した判断によるものです。報酬の有無にかかわらず、
      技適・PSE の適合状況や入手性についての記載は変えません。</p>

      <h2>ご連絡方法</h2>
      <p>製品情報・プレスリリース・取材のご連絡は下記までお願いします。掲載の可否は上記の基準に沿って編集部が判断します。</p>
      <ul>
        <li>製品情報・取材： <a href="mailto:{press}">{press}</a></li>
        <li>その他のお問い合わせ： <a href="mailto:{contact}">{contact}</a></li>
{x_row}
      </ul>

      <h2 lang="en">For brands planning to reach Japan</h2>
      <div lang="en">
      <p>{html.escape(s['title'])} is a Japanese-language site covering overseas gadgets, especially crowdfunded hardware,
      that have no Japanese coverage yet. We publish before a product is sold in Japan, check Japanese radio certification
      (Giteki) for every product, and let readers sign up to be emailed once when the product becomes available in Japan.</p>
      <ul>
        <li>{n} articles published since {since}; {landed_after} products we covered later launched in Japan.</li>
        <li>Send us your press kit, official images, pricing, and any plans for Japan (retail, crowdfunding, distributors,
        certification). English is fine.</li>
        <li>Send us a review unit and we will use it and publish a hands-on review, including any downsides we find.
        The review is not shown to you before publication, and it is labeled as a provided unit.</li>
        <li>Editorial coverage is decided by our editors under the criteria above. Paid content, if any, is always labeled [PR].</li>
        <li>Contact: <a href="mailto:{press}">{press}</a></li>
      </ul>
      </div>

      <p><a href="{u("about.html")}">運営・編集方針についてはこちら</a></p>
    </div>
  </article>
</main>"""
    # 行末の改行が和文の間に空白として出るので、日本語の直後の改行と字下げを詰める(英語の段落は残す)
    body = re.sub(r"(?<=[^\x00-\x7f])\n\s+", "", body)
    return (head(site, f"メーカー・広報の方へ — {s['title']}",
                 "日本で発売される前から日本語の記事を出し、待っている読者に日本上陸を知らせる海外ガジェットのメディアです。掲載基準・PR表記・ご連絡先", "media.html")
            + header(site) + body + footer(site))


# ────────────────────────────── 技適チェック一覧 ──────────────────────────────
# 総務省の検索画面(giteki.py と同じ SearchServlet)に技適番号を渡して開くための種別コード。
# この画面は RAD(特定無線設備の種別)が1つも無いと結果ではなく検索フォームを返す。
# 全種別を付けると4.5KBのURLになるので、リンクは href に検索フォームを置き、
# 一覧ページの JS が番号ごとに本物のURLへ組み替える(JS が無ければ検索フォームが開く)。
# 取得: python scripts/giteki.py の rad_codes()。2026-10-14 時点。制度改正で増えたら取り直す。
MIC_FORM = "https://www.tele.soumu.go.jp/giteki/SearchServlet?pageID=js01"
MIC_RAD = (
    "00-00-00-00 02-01-04-00 02-01-07-00 02-01-08-00 02-01-09-00 02-01-10-00 02-01-11-00 "
    "02-01-12-00 02-01-12-02 02-01-13-00 02-01-14-00 02-01-15-00 02-02-00-00 02-02-02-00 "
    "02-03-00-00 02-03-02-00 02-04-02-00 02-04-03-00 02-04-05-00 02-04-06-00 02-04-06-02 "
    "02-04-06-03 02-04-06-04 02-04-07-00 02-05-00-00 02-06-00-00 02-06-02-00 02-06-02-02 "
    "02-06-03-00 02-06-04-00 02-07-00-00 02-08-00-00 02-09-00-00 02-09-02-00 02-09-03-00 "
    "02-09-04-00 02-09-05-00 02-10-00-00 02-10-02-00 02-10-03-00 02-11-00-00 02-11-02-00 "
    "02-11-02-02 02-11-03-00 02-11-03-07 02-11-04-00 02-11-05-00 02-11-06-00 02-11-06-02 "
    "02-11-06-03 02-11-06-04 02-11-06-05 02-11-07-00 02-11-08-00 02-11-08-02 02-11-09-00 "
    "02-11-10-00 02-11-10-02 02-11-10-03 02-11-10-04 02-11-10-05 02-11-11-00 02-11-12-00 "
    "02-11-13-00 02-11-17-00 02-11-19-00 02-11-19-02 02-11-19-03 02-11-20-00 02-11-20-02 "
    "02-11-20-03 02-11-20-04 02-11-21-00 02-11-22-00 02-11-29-00 02-11-29-03 02-11-29-04 "
    "02-11-30-00 02-11-30-02 02-11-30-03 02-11-31-00 02-11-31-04 02-11-32-00 02-11-32-02 "
    "02-11-33-00 02-11-33-03 02-11-34-00 02-11-34-02 02-12-00-00 02-13-00-00 02-14-00-00 "
    "02-14-02-00 02-15-00-00 02-15-02-00 02-15-03-00 02-16-00-00 02-17-00-00 02-17-02-00 "
    "02-18-00-00 02-19-00-00 02-19-02-00 02-19-02-02 02-19-02-03 02-19-03-00 02-19-03-02 "
    "02-19-03-03 02-19-04-00 02-19-04-02 02-19-04-03 02-19-05-00 02-19-06-00 02-19-07-00 "
    "02-19-07-02 02-19-08-00 02-19-09-00 02-19-10-00 02-19-11-00 02-19-12-00 02-19-13-00 "
    "02-20-00-00 02-20-02-00 02-20-03-00 02-20-04-00 02-21-00-00 02-21-02-00 02-21-03-00 "
    "02-22-00-00 02-23-00-00 02-23-02-00 02-25-00-00 02-25-02-00 02-25-04-00 02-25-05-00 "
    "02-25-06-00 02-27-00-00 02-28-00-00 02-28-02-00 02-28-02-02 02-28-02-03 02-28-02-04 "
    "02-28-02-05 02-28-02-06 02-28-03-00 02-28-04-00 02-29-00-00 02-29-03-00 02-30-00-00 "
    "02-30-02-00 02-30-03-00 02-30-04-00 02-31-00-00 02-31-02-00 02-31-04-00 02-31-05-00 "
    "02-32-00-00 02-33-00-00 02-33-02-00 02-38-00-00 02-39-00-00 02-40-00-00 02-41-00-00 "
    "02-42-00-00 02-44-00-00 02-45-00-00 02-46-00-00 02-47-00-00 02-47-02-00 02-47-03-00 "
    "02-47-04-00 02-49-00-00 02-51-00-00 02-52-03-00 02-53-00-00 02-54-00-00 02-54-02-00 "
    "02-54-03-00 02-54-05-00 02-54-06-00 02-54-06-03 02-57-00-00 02-57-02-00 02-57-03-00 "
    "02-57-04-00 02-58-00-00 02-59-00-00 02-60-00-00 02-62-00-00 02-62-02-00 02-63-00-00 "
    "02-64-00-00 02-65-00-00 02-66-00-00 02-67-00-00 02-68-00-00 02-70-00-00 02-71-00-00 "
    "02-72-00-00 02-73-00-00 02-74-00-00 02-78-00-00 02-79-00-00 02-80-00-00 02-81-00-00 "
    "02-82-00-00 02-83-00-00 02-84-00-00 02-87-00-00 08-02-00-00 08-03-02-00 08-03-03-00 "
    "08-03-07-00 08-04-00-00 08-04-02-00 08-05-00-00 08-05-02-00 08-05-03-00 08-05-04-00 "
    "08-05-05-00 08-06-00-00 08-06-02-00 08-07-00-00 08-07-02-00 08-08-00-00 08-08-02-00 "
    "08-08-03-00 08-09-00-00 08-10-00-00 08-11-00-00 08-12-00-00 08-13-00-00 08-14-00-00 "
    "08-14-02-00 08-14-03-00 08-15-00-00 08-15-02-00 08-15-03-00 08-15-04-00 08-15-05-00 "
    "08-15-07-00 08-16-00-00 08-17-00-00 08-18-00-00 08-18-02-00 08-19-00-00 08-19-02-00 "
    "08-19-03-00 08-20-00-00 08-21-00-00 08-22-00-00 08-23-00-00 08-23-02-00 08-23-03-00 "
    "08-24-00-00 08-25-00-00 08-26-00-00 08-27-00-00 08-27-02-00 08-27-03-00 08-29-00-00 "
    "08-29-04-00 08-29-06-00 08-31-00-00 08-32-00-00 08-32-02-00 08-32-03-00 08-33-00-00 "
    "08-34-00-00 08-35-00-00 08-35-04-00 08-36-00-00 08-37-00-00 08-37-02-00 08-38-00-00 "
    "08-39-00-00 08-40-00-00 08-41-00-00 08-42-00-00"
).split()

GITEKI_PATH = "giteki/"
GITEKI_TITLE = "海外ガジェットの技適チェック一覧"
GITEKI_DESC = ("当メディアが記事にした海外ガジェットの技適の状況を、製品ごとに一覧にしました。"
               "総務省のデータベースで確認した結果を、取得済み・確認できない・対象外の3つで示し、毎週更新します。")
GITEKI_LICENSE = "https://creativecommons.org/licenses/by/4.0/deed.ja"
GITEKI_STATUS_CLS = {"取得済み": "gk-ok", "確認できない": "gi-warn", "対象外": "gk-na"}


def giteki_records(site: dict, posts: list[dict]) -> list[dict]:
    """giteki を持つ記事を、新しい順の記録に直す。一覧・CSV・JSON が同じ元を使う。"""
    base = site["site"]["base_url"].rstrip("/")
    out = []
    for p in posts:
        g = p.get("giteki")
        if not g:
            continue
        cat = site["categories"].get(p.get("category"), {})
        out.append({
            "slug": p["slug"],
            "name": p.get("name_short") or p.get("seo_title") or p["title"],
            "title": p["title"],
            "url": f"{base}/{p['path']}",
            "path": p["path"],
            "category": p.get("category") or "",
            "category_label": cat.get("label", ""),
            "radio": g["radio"],
            "status": g["status"],
            "numbers": g["number"],
            "checked": g["checked"],
            "note": g["note"],
            "found": g["found"],
            "published": p["date"],
        })
    return out


def giteki_counts(posts: list[dict]) -> dict:
    c = {s_: 0 for s_ in GITEKI_STATUSES}
    for p in posts:
        if p.get("giteki"):
            c[p["giteki"]["status"]] += 1
    c["公開後に取得"] = sum(1 for p in posts if p.get("giteki") and p["giteki"]["found"]
                      and p["giteki"]["status"] == "取得済み")
    c["未記入"] = sum(1 for p in posts if not p.get("giteki"))
    c["記録"] = len(posts) - c["未記入"]
    return c


def render_giteki(site: dict, posts: list[dict]) -> str:
    s = site["site"]
    base = s["base_url"].rstrip("/")
    page_url = f"{base}/{GITEKI_PATH}"
    recs = giteki_records(site, posts)
    cnt = giteki_counts(posts)
    latest = max((r["checked"] for r in recs if r["checked"]), default="")
    # 製品名の横に記事の写真を小さく出す(2026-10-27 本人の要望)。CSV・JSON には入れない
    thumbs = {p["slug"]: card_image(p) for p in posts if p.get("giteki")}

    def thumb(r: dict) -> str:
        src, is_ext = thumbs.get(r["slug"], ("", False))
        if not src:
            return ""
        fb = u("cards/" + r["slug"] + ".png")
        return (f'<img class="gk-thumb" src="{html.escape(src)}" alt="" loading="lazy" decoding="async" '
                f'width="64" height="48" referrerpolicy="no-referrer"'
                + (f''' onerror="this.onerror=null;this.src='{fb}'"''' if is_ext else "") + ">")

    def row(r: dict) -> str:
        st = r["status"]
        cls = GITEKI_STATUS_CLS[st]
        nums = " ".join(
            f'<a class="gk-num" href="{MIC_FORM}" data-num="{html.escape(n)}" '
            f'target="_blank" rel="noopener" title="総務省のデータベースで開く">{html.escape(n)}</a>'
            for n in r["numbers"])
        note = f'<span class="gk-note">{html.escape(r["note"])}</span>' if r["note"] else ""
        is_found = bool(r["found"]) and st == "取得済み"
        found_mark = (f'<span class="gk-found" title="{html.escape(r["found"])} の再確認で登録を確認">'
                      f'発表後に取得</span>' if is_found else "")
        found_attr = ' data-found="1"' if is_found else ""

        def cell(label: str, val: str, cls_: str = "") -> str:
            if val:
                return f'<td data-l="{label}"{cls_}>{val}</td>'
            return f'<td data-l="{label}" class="gk-empty"><span aria-hidden="true">&mdash;</span></td>'

        return (
            f'<tr data-status="{html.escape(st)}" data-cat="{html.escape(r["category"])}"{found_attr}>'
            f'<td class="gk-prod"><a href="{u(r["path"])}" title="{html.escape(r["title"])}">'
            f'{thumb(r)}<span>{html.escape(r["name"])}</span></a></td>'
            + cell("カテゴリ", html.escape(r["category_label"]))
            + cell("無線", html.escape(r["radio"]))
            + f'<td data-l="判定"><span class="buy-giteki {cls}">{html.escape(st)}</span>{found_mark}{note}</td>'
            + cell("技適番号", nums, ' class="gk-nums"')
            + cell("確認日", f'<time datetime="{r["checked"]}">{r["checked"].replace("-", ".")}</time>'
                   if r["checked"] else "")
            + "</tr>")

    tiles = "".join(
        f'<a class="gk-tile {cls}" href="#gk-list" data-status="{html.escape(key)}">'
        f'<b>{cnt_}</b><span>{html.escape(label)}</span></a>'
        for key, label, cnt_, cls in (
            ("", "記録した製品", cnt["記録"], "gk-all"),
            ("取得済み", "取得済み", cnt["取得済み"], "gk-ok"),
            ("確認できない", "確認できない", cnt["確認できない"], "gi-warn"),
            ("対象外", "対象外", cnt["対象外"], "gk-na")))
    found_line = (f'<p class="gk-foundline" data-gk-foundline><a href="#gk-list" data-status="found">'
                  f'公開後に取得を確認: <b>{cnt["公開後に取得"]}</b></a>'
                  f'<span>記事の公開時点では確認できず、あとから登録が見つかった製品</span></p>'
                  if cnt["公開後に取得"] else "")
    opts = '<option value="">すべてのカテゴリ</option>' + "".join(
        f'<option value="{html.escape(k)}">{html.escape(c["label"])}</option>'
        for k, c in site["categories"].items())
    if recs:
        table = f"""
    <div class="gk-filter" data-gk-filter hidden>
      <label class="gk-sel">カテゴリ <select data-gk-cat>{opts}</select></label>
      <p class="gk-count" data-gk-count aria-live="polite"></p>
    </div>
    <table class="gk-table" id="gk-list">
      <thead><tr><th>製品</th><th>カテゴリ</th><th>無線</th><th>判定</th><th>技適番号</th><th>確認日</th></tr></thead>
      <tbody>{"".join(row(r) for r in recs)}</tbody>
    </table>
    <p class="gk-none" data-gk-none hidden>この条件に合う製品はありません。</p>"""
    else:
        table = '<p class="empty">技適の記録はまだありません。</p>'

    # 構造化データ。Dataset は「この表そのものがデータである」ことを宣言する。
    # 引用してもらうことが狙いの一覧なので、出典を書けば自由に使える CC BY 4.0 にする
    # (2026-10-17。Search Console が license 欠落を指摘)。ページにも同じ条件を書く。
    ld_data = {
        "license": GITEKI_LICENSE,
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": GITEKI_TITLE,
        "description": GITEKI_DESC + "各行に判定、無線の種類、技適番号、確認日を付けています。"
                       "判定は確認した日の時点のものです。",
        "url": page_url,
        "inLanguage": "ja",
        "isAccessibleForFree": True,
        "keywords": ["技適", "技術基準適合証明", "海外ガジェット", "電波法", "総務省"],
        "creator": {"@type": "Organization", "@id": f"{base}/#org", "name": s["title"], "url": base + "/"},
        "isBasedOn": MIC_FORM,
        **({"dateModified": latest} if latest else {}),
        "distribution": [
            {"@type": "DataDownload", "encodingFormat": "text/csv",
             "contentUrl": f"{base}/{GITEKI_PATH}giteki.csv"},
            {"@type": "DataDownload", "encodingFormat": "application/json",
             "contentUrl": f"{base}/{GITEKI_PATH}giteki.json"},
        ],
        "variableMeasured": [
            {"@type": "PropertyValue", "name": "製品", "description": "記事で扱った製品名"},
            {"@type": "PropertyValue", "name": "判定",
             "description": "取得済み（総務省のデータベースで技適番号を確認）/ 確認できない（見つからない、"
                            "または型番が特定できない。取得していない、とは限らない）/ 対象外（無線機能がない）"},
            {"@type": "PropertyValue", "name": "無線", "description": "記事に書かれた無線の種類"},
            {"@type": "PropertyValue", "name": "技適番号", "description": "総務省のデータベースで確認できた番号"},
            {"@type": "PropertyValue", "name": "確認日", "description": "判定を確認した日"},
            {"@type": "PropertyValue", "name": "公開後に取得を確認した日",
             "description": "記事の公開時点では確認できず、その後の再確認で登録が見つかった日"},
        ],
    }
    ld_crumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": s["title"], "item": base + "/"},
            {"@type": "ListItem", "position": 2, "name": "特集", "item": f"{base}/features.html"},
            {"@type": "ListItem", "position": 3, "name": GITEKI_TITLE, "item": page_url},
        ],
    }
    ld = "".join(
        f'<script type="application/ld+json">{json.dumps(d, ensure_ascii=False, separators=(",", ":"))}</script>'
        for d in (ld_data, ld_crumb))
    feat = u(f"features/{GITEKI_FEATURE_SLUG}.html")
    legend = """
    <dl class="gk-legend">
      <div><dt><span class="buy-giteki gk-ok">取得済み</span></dt>
        <dd>総務省のデータベースで技適番号を確認できたもの。</dd></div>
      <div><dt><span class="buy-giteki gi-warn">確認できない</span></dt>
        <dd>データベースで見つけられない、または型番が公表されていなくて特定できなかったもの。
        <strong>「取得していない」と同じ意味ではありません。</strong>型番が非公開だったり、
        申請時の型番と販売時の表記が違ったりして、引けないことがあるためです。</dd></div>
      <div><dt><span class="buy-giteki gk-na">対象外</span></dt>
        <dd>無線機能がなく、技適が関係しないもの。</dd></div>
    </dl>"""
    js = GITEKI_JS.replace("@@RAD@@", " ".join(MIC_RAD))
    return (
        head(site, f"{GITEKI_TITLE} — {s['title']}", GITEKI_DESC, GITEKI_PATH, ld)
        + header(site)
        + f"""
<main class="wrap">
  <section class="hero hero-sm">
    <p class="eyebrow">FEATURE / 技適</p>
    <h1 class="hero-title">{GITEKI_TITLE}</h1>
    <p class="hero-sub">当メディアが記事にした海外ガジェットについて、技適の状況を確認した時点の記録を一覧にしました。編集部が総務省の「技術基準適合証明等を受けた機器の検索」で、メーカー名と型番から引いた結果です。判定が「確認できない」の製品は毎週、総務省のデータベースで引き直し、新しく登録が見つかれば更新します。</p>
  </section>
  <div class="gk" id="gk">
    {legend}
    <p class="gk-lead">判定は確認した日の時点のもので、あとから取得されて変わることがあります。
    技適の考え方そのものは<a href="{feat}">技適マークのない海外ガジェットを日本で使うとどうなるか</a>にまとめています。</p>
    <div class="gk-tiles" data-gk-tiles>{tiles}</div>
    {found_line}
    {table}
    <p class="gk-foot">掲載時点の確認です。購入前に総務省のデータベースで型番を確かめてください。
    <a href="{MIC_FORM}" target="_blank" rel="noopener">総務省の検索ページ</a>
    ／ 表のデータ： <a href="{u(GITEKI_PATH + "giteki.csv")}" download>CSV</a>
    <a href="{u(GITEKI_PATH + "giteki.json")}">JSON</a></p>
    <p class="gk-foot">この一覧のデータは<a href="{GITEKI_LICENSE}" target="_blank" rel="noopener license">CC BY 4.0</a>で公開しています。出典として「Gadget Terminal」とこのページのURLを書けば、自由に使えます。</p>
  </div>
</main>
{js}"""
        + footer(site)
    )


GITEKI_JS = """<script>(function(){
var root=document.getElementById("gk");if(!root)return;
var rows=[].slice.call(root.querySelectorAll("tbody tr"));
var tiles=[].slice.call(root.querySelectorAll("[data-gk-tiles] a,[data-gk-foundline] a"));
var bar=root.querySelector("[data-gk-filter]");
var sel=root.querySelector("[data-gk-cat]");
var cnt=root.querySelector("[data-gk-count]");
var none=root.querySelector("[data-gk-none]");
var st="",ct="";
function apply(){
  var n=0;
  rows.forEach(function(r){
    var ok=(!st||(st==="found"?r.getAttribute("data-found")==="1":r.getAttribute("data-status")===st))&&(!ct||r.getAttribute("data-cat")===ct);
    r.hidden=!ok;if(ok)n++;
  });
  if(cnt)cnt.textContent=n+"件を表示";
  if(none)none.hidden=n>0;
  tiles.forEach(function(t){t.setAttribute("aria-pressed",String(t.getAttribute("data-status")===st));});
}
if(bar&&rows.length){
  bar.hidden=false;
  tiles.forEach(function(t){
    t.addEventListener("click",function(e){e.preventDefault();st=t.getAttribute("data-status");apply();});
  });
  if(sel)sel.addEventListener("change",function(){ct=sel.value;apply();});
  apply();
}
var q=[];
"@@RAD@@".split(" ").forEach(function(c){q.push("RAD="+c);});
for(var i=1;i<=7;i++)q.push("TEC="+i);
[].forEach.call(root.querySelectorAll("a.gk-num"),function(a){
  a.href="https://www.tele.soumu.go.jp/giteki/SearchServlet?pageID=jk01&NUM_TYPE=1&NUM="+encodeURIComponent(a.getAttribute("data-num"))+"&SC=1&"+q.join("&");
});
})();</script>"""


def write_landing_data(site: dict, posts: list[dict]) -> None:
    """日本上陸アラート(alert/)が毎朝読む landing.json。全記事の slug と上陸状態。

    Worker はこれを読んで、landed が true になった記事の登録者に1通送る(記事ごとに1回)。
    登録時にも slug の実在確認と製品名の取得に使う。紹介リンクは入れない(メールに出さないため)。
    """
    base = site["site"]["base_url"].rstrip("/")
    items = []
    for p in posts:
        j = p.get("japan") or {}
        items.append({
            "slug": p["slug"],
            "title": p["title"],
            "url": f"{base}/{p['path']}",
            "category": p.get("category") or "",   # YouTube の再生リスト分け(x-poster)に使う
            "status": str(j.get("status") or "").strip() or "未上陸",
            "landed": is_landed(p),
            "summary": str(j.get("summary") or "").strip(),
            "checked": str(j.get("checked") or ""),
        })
    by = {x["slug"]: x for x in items}
    for m in MERGED:
        t = by.get(str(m["merged_into"]).strip())
        if t:
            items.append({**t, "slug": m["slug"]})
    data = {"generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "items": items}
    (PUBLIC / "landing.json").write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"■ landing.json: {len(items)}本 / 日本で買える {sum(1 for x in items if x['landed'])}本")


def write_giteki_data(site: dict, posts: list[dict]) -> None:
    """一覧と同じ元データを CSV（Excel 用に BOM 付き UTF-8）と JSON で出す。"""
    import csv
    recs = giteki_records(site, posts)
    out_dir = PUBLIC / GITEKI_PATH.strip("/")
    out_dir.mkdir(parents=True, exist_ok=True)

    def safe(v: str) -> str:   # Excel が数式として解釈しないように
        return "'" + v if v[:1] in ("=", "+", "@") else v

    with open(out_dir / "giteki.csv", "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["製品", "記事URL", "カテゴリ", "無線", "判定", "技適番号", "確認日", "公開後に取得を確認した日"])
        for r in recs:
            w.writerow([safe(r["name"]), r["url"], r["category_label"], safe(r["radio"]),
                        r["status"], ";".join(r["numbers"]), r["checked"], r["found"]])
    latest = max((r["checked"] for r in recs if r["checked"]), default="")
    data = {
        "title": GITEKI_TITLE,
        "page": f"{site['site']['base_url'].rstrip('/')}/{GITEKI_PATH}",
        "source": "総務省「技術基準適合証明等を受けた機器の検索」",
        "updated": latest,
        "note": "判定は確認日時点のもの。「確認できない」は「取得していない」と同じ意味ではない。",
        "items": [{"name": r["name"], "title": r["title"], "url": r["url"],
                   "category": r["category_label"], "radio": r["radio"], "status": r["status"],
                   "numbers": r["numbers"], "checked": r["checked"], "note": r["note"],
                   "found": r["found"], "published": r["published"]} for r in recs],
    }
    (out_dir / "giteki.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")



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
    urls = [f"{base}/", f"{base}/about.html", f"{base}/media.html", f"{base}/privacy.html",
            f"{base}/jpn.html", f"{base}/features.html", f"{base}/{GITEKI_PATH}"]
    urls += [f"{base}/{f['path']}" for f in (features or [])]
    if TOPICS:
        urls += [f"{base}/topic/"] + [f"{base}/{t['path']}" for t in TOPICS]
    per_page = int(site["site"].get("posts_per_page") or 20)
    total_pages = max(1, -(-len(posts) // per_page))
    urls += [f"{base}/{page_path(n)}" for n in range(2, total_pages + 1)]
    urls += [f"{base}/category/{c['slug']}.html" for c in site["categories"].values()]
    urls += [f"{base}/{p['path']}" for p in posts]
    # lastmod があるとクローラーが再訪問すべきURLを判断できる。
    # 記事は自身の日付、一覧系は最新記事の日付を使う。
    latest = max((p["date"] for p in posts), default="")
    by_url = {f"{base}/{p['path']}": max(p["date"], p.get("modified") or "") for p in posts}
    _gk = max((p["giteki"]["checked"] for p in posts if p.get("giteki")), default="")
    if _gk:
        by_url[f"{base}/{GITEKI_PATH}"] = _gk   # 技適一覧は最新の確認日
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
/* 既定はライト（薄いグレー）。data-theme="dark" のときだけダーク側の値に差し替える。
   .board（発着案内板）だけは常にダークパネル固定で、テーマの影響を受けない
   （下の .board 定義を参照）。 */
:root{
  --bg:#f6f7f9; --surface:#eff1f3; --raised:#e7eaed;
  --ink:#1a1e24; --ink-2:#5c6570; --ink-3:#8d95a0;
  --rule:#e7e9ec; --rule-2:#dadde1;
  --accent:#ff6b3d;
  --cat:var(--accent);
  /* 注意喚起。カテゴリ色(--cat)とは独立させる。技適の警告は記事の
     カテゴリで色が変わってよいものではない。 */
  --warn:#b4472b;
  --max:1280px; --measure:37.5rem;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --disp:"Space Grotesk","Hiragino Sans","Noto Sans JP","Yu Gothic",sans-serif;
  --sans:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP","Yu Gothic",sans-serif;
}
[data-theme="dark"]{
  --bg:#0a0d16; --surface:#10141f; --raised:#151a27;
  --ink:#e9edf1; --ink-2:#96a0ac; --ink-3:#5f6975;
  --rule:#1c212e; --rule-2:#272e40;
  --warn:#e08b6a;
}
.cat-smartphone{--cat:#ff6b3d}
.cat-pc{--cat:#4fb3c4}
.cat-weird{--cat:#d9b45f}

*{box-sizing:border-box}
/* 案内板の背景(.board::before)は 100vw で端まで伸ばしている。100vw は縦スクロールバーの幅を含むので、
   そのままだと右に8pxほどはみ出し、横スクロールバーが出ていた(2026-10-27 本人の指摘)。
   clip は hidden と違ってスクロール領域を作らないので、position:sticky のヘッダーは壊れない。 */
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;color-scheme:light;overflow-x:clip}
html[data-theme="dark"]{color-scheme:dark}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);
  font-size:15px;line-height:1.72;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
a{color:inherit;text-decoration:none}
img{max-width:100%}
.wrap{max-width:var(--max);margin:0 auto;padding:0 24px}

/* ── ヘッダー ───────────────────────────────── */
/* 案内板・NEXT GATEタイルと同じ紺色に固定。ページのライト/ダーク切り替えに
   関わらず、サイトの「常設の骨格」として常にこの色で統一する。 */
.site-head{
  --bg:#14172e; --raised:#212643;
  --ink:#e9edf1; --ink-2:#96a0ac; --ink-3:#5f6975;
  --rule:#262c4c; --rule-2:#333a5e;
  position:sticky;top:0;z-index:20;border-bottom:1px solid var(--rule);color:var(--ink);
  background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(14px) saturate(1.4)}
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

/* ダーク／ライト切り替え。案内板と違い、ページ全体はこのボタンで反転する。
   アイコンは「押すとどうなるか」ではなく「切り替え先」を示す
   （ライト表示中は月＝押すとダークになる、を出す）。 */
.theme-toggle{flex:none;display:inline-flex;align-items:center;justify-content:center;
  width:28px;height:28px;border:1px solid var(--rule-2);border-radius:2px;
  background:transparent;color:var(--ink-2);cursor:pointer;font-size:13px;line-height:1;
  transition:border-color .18s,color .18s}
.theme-toggle:hover{color:var(--ink);border-color:var(--accent)}
.tt-ic-sun{display:none}
[data-theme="dark"] .tt-ic-moon{display:none}
[data-theme="dark"] .tt-ic-sun{display:inline}

/* ── ヒーロー ───────────────────────────────── */
.hero{position:relative;padding:30px 0 20px}
.hero-sm{padding:32px 0 22px;border-bottom:1px solid var(--rule);margin-bottom:0}
/* 見出し横に残る余白を埋める、着陸してくる飛行機の写真的シルエット。
   案内板と役割が被らないよう、狭い画面では出さない。 */
.hero-route{position:absolute;top:6px;right:8px;width:300px;height:auto;
  opacity:.85;pointer-events:none}
/* 開いたときに1回だけ、右上から滑り込んで着陸する(2026-11-07 本人、モックの2だけ採用) */
@keyframes hero-land{0%{transform:translate(120px,-70px) rotate(-8deg);opacity:0}60%{opacity:.85}100%{transform:none;opacity:.85}}
@media (prefers-reduced-motion:no-preference){.hero-route{animation:hero-land 1.6s cubic-bezier(.16,1,.3,1) both}}
@media(max-width:1100px){.hero-route{display:none}}
.eyebrow{font-family:var(--mono);font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--cat);margin:0 0 10px;font-weight:600}
.hero-title{font-family:var(--disp);font-size:clamp(22px,2.9vw,34px);line-height:1.4;
  margin:0 0 10px;font-weight:700;letter-spacing:-.015em;max-width:30em}
.hero-sub{margin:0;color:var(--ink-2);font-size:13px;max-width:44em;line-height:1.75}
/* スマホだけの「今日の新着」(today_strip)。PC は出さない(2026-11-14 本人) */
.today-strip{display:none}
@media (max-width:767px){
.today-strip{display:block;margin:4px 0 18px}
.ts-top{display:flex;align-items:center;gap:10px;margin-bottom:6px}
.ts-label{font-family:var(--mono);font-size:10px;letter-spacing:.12em;color:var(--accent);white-space:nowrap}
.ts-bars{display:flex;gap:4px;flex:1}
.ts-bar{flex:1;height:3px;background:var(--rule-2);border-radius:2px;overflow:hidden}
.ts-bar i{display:block;height:100%;width:0;background:var(--accent)}
.ts-bar.done i{width:100%}
.ts-bar.run i{width:100%;transition:width 4s linear}
.ts-stage{position:relative;aspect-ratio:16/9;border-radius:6px;overflow:hidden;background:#11141c}
.ts-slide{position:absolute;inset:0;opacity:0;pointer-events:none;color:#fff;text-decoration:none}
.ts-slide.on{opacity:1;pointer-events:auto}
.ts-media img,.ts-media video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.ts-media.is-img img{object-fit:contain;background:#fff}
.ts-media video{opacity:0}
.ts-slide.playing video{opacity:1}
.ts-cap{position:absolute;left:0;right:0;bottom:0;padding:22px 12px 10px;
  background:linear-gradient(transparent,rgba(0,0,0,.72));display:flex;flex-direction:column;gap:2px}
.ts-name{font-size:11px;opacity:.85;letter-spacing:.02em}
.ts-hook{font-size:15px;font-weight:700;line-height:1.4}
.ts-credit{position:absolute;top:6px;right:8px;font-size:9px;opacity:.8;background:rgba(0,0,0,.4);
  padding:1px 5px;border-radius:2px}
}
/* 日本語の折り返し。塊の途中では改行させない（jp() が挿入する span） */
.nb{display:inline-block}
/* 対応ブラウザ（Chromium系）では、塊の内部も文節単位で折り返す */
.hero-sub,.article-lede,.card-excerpt,
.pick-note,.pick-callout-note,.prose p,.prose li,
.prose td,.prose th,.faq dt,.faq dd{word-break:auto-phrase}
/* タイトルは文節単位にしない。「手のひら」を「手の／ひら」と切るなど区切りを誤り、
   切れ目でしか折り返せないので各行の右に余白が残って段々に見えた(2026-10-11
   本人の指摘)。新聞・ニュースサイトと同じ1文字単位の折り返し+行頭禁則にする。 */
.hero-title,.article-title,.card-title,.pick-title,.board-title,.fi-title{word-break:normal;line-break:strict}

/* ── 出発案内板 ─────────────────────────────── */
/* 案内板は明るいターミナルビルの中で光る実物の掲示板と同じで、
   ページ全体のテーマ（ライト/ダーク）に関わらず常にダークパネル固定。
   中の要素は var(--bg)/var(--ink) 等しか参照していないので、
   ここで変数を上書きするだけで内部の設計は変えずに済む。 */
.board{
  --bg:#14172e; --surface:#1a1e38; --raised:#212643;
  --ink:#e9edf1; --ink-2:#96a0ac; --ink-3:#5f6975;
  --rule:#262c4c; --rule-2:#333a5e;
  position:relative;color:var(--ink);margin-bottom:40px;padding:0 16px 16px}
/* 背景だけをビューポート全幅までブリードさせ、中身（見出し・行）は
   .wrap と同じ位置に留める定番の breakout テクニック。
   50vw はビューポート基準の絶対値なので、祖先の max-width や
   padding に関係なく画面の左右端まで届く。 */
.board::before{content:"";position:absolute;top:0;bottom:0;
  left:50%;width:100vw;transform:translateX(-50%);
  background:var(--bg);z-index:-1}
/* 見出しの飛行機は ISO 7001 の到着ピクトグラム（機首を下げた機体＋接地線）。
   本物の案内板に飛行機の絵は無く、あるのはこの見出しの位置だけ。
   サイト内の他の場所にアイコンを散らさないこと。空港ではなく旅行ブログに見える。 */
.board-title{display:flex;align-items:center;gap:11px;margin:0;padding:16px 0 13px;
  font-family:var(--mono);font-weight:600;font-size:13px;letter-spacing:.2em;
  border-bottom:1px solid var(--rule)}
.pict-arr{width:19px;height:19px;flex:none;fill:var(--accent)}
.board-title-en{color:var(--ink)}
.board-title-ja{font-family:var(--sans);font-size:11.5px;font-weight:400;letter-spacing:0;
  color:var(--ink-2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
@media (max-width:620px){.board-title-ja{display:none}}
.board-head,.board-row{display:grid;
  grid-template-columns:64px 74px 44px 150px minmax(0,1fr) 182px 20px;
  align-items:center;gap:14px;font-family:var(--mono);font-size:11.5px}
.board-head{padding:7px 0;color:var(--ink-2);font-size:9.5px;letter-spacing:.16em;
  background:var(--raised);border-bottom:1px solid var(--rule)}
.board-row{padding:8px 0;border-bottom:1px solid var(--rule);position:relative;
  transition:background .16s,padding-left .16s}
.board-row:last-child{border-bottom:0}
/* 実物の空港案内板でよくある、1行おきの背景の縞。奇数行は素の --bg のまま、
   偶数行だけ --surface で少し明るくする。 */
.board-row-alt{background:var(--surface)}
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
.st{display:flex;align-items:center;gap:7px;letter-spacing:.1em;font-weight:500;
  white-space:nowrap;overflow:hidden}
.st::before{content:"";width:6px;height:6px;border-radius:50%;background:currentColor;flex:none}
/* 残りN日はラベルの長さに関係なく右端に揃える。ラベル直後に流すと
   FINAL CALL / NOW BOARDING の字数差でガタつくため margin-left:auto で固定位置に押し出す */
.st em{font-style:normal;font-family:var(--sans);letter-spacing:0;color:var(--ink-2);
  font-size:11px;margin-left:auto;padding-left:8px;flex:none}
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
.visually-hidden{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
/* 出発・到着のタブ。選んでいる方だけ明るく、下線はアクセント色 */
.board-title{gap:4px}
.board-tab{display:flex;align-items:center;gap:9px;background:none;border:0;cursor:pointer;
  padding:4px 14px 4px 0;margin-right:10px;font:inherit;letter-spacing:inherit;color:var(--ink-3);
  border-bottom:2px solid transparent;margin-bottom:-15px;padding-bottom:12px}
.board-tab .board-title-en{color:inherit}
.board-tab .pict-arr{fill:currentColor}
.board-tab[aria-selected="true"]{color:var(--ink);border-bottom-color:var(--accent)}
.board-tab[aria-selected="true"] .pict-arr{fill:var(--accent)}
.board-tab:hover{color:var(--ink-2)}
.board-tab[aria-selected="true"]:hover{color:var(--ink)}
.board-tab-ja{font-family:var(--sans);font-size:11px;font-weight:400;letter-spacing:0}
.board-lede{margin:10px 0 10px;font-family:var(--sans);font-size:12.5px;color:var(--ink-2)}
.board-lede b{color:#5ad19a;font-weight:600}
.board-lede a{color:var(--ink);margin-left:8px;white-space:nowrap}
@media (max-width:620px){.board-tab-ja{display:none}.board-tab{padding-right:4px;margin-right:6px}}
/* 製品名の下の「何の製品か」。広い画面は題名の列(ENTRY)があるので出さない */
.b-key b{font-weight:600;display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.b-what{display:none;font-weight:400;font-size:11px;color:var(--ink-2);line-height:1.45;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.b-thumb{display:none}
/* よく読まれている記事 */
.popular{margin:8px 0 44px}
.pop-list{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));
  gap:0 28px;border-top:1px solid var(--rule)}
.pop-item a{display:grid;grid-template-columns:28px 96px minmax(0,1fr);gap:12px;align-items:center;
  padding:12px 0;border-bottom:1px solid var(--rule);color:var(--ink);text-decoration:none}
.pop-n{font-family:var(--mono);font-size:13px;font-weight:600;color:var(--cat)}
.pop-img{width:96px;height:54px;object-fit:cover;border-radius:3px;background:var(--surface)}
.pop-title{font-size:13.5px;line-height:1.5;font-weight:600;display:-webkit-box;-webkit-line-clamp:3;
  -webkit-box-orient:vertical;overflow:hidden}
.pop-item a:hover .pop-title{color:var(--accent)}

/* ── ページ送り ─────────────────────────────── */
.pager{display:flex;align-items:center;justify-content:space-between;gap:16px;
  margin:36px 0 8px;padding-top:20px;
  font-family:var(--mono);font-size:12px;letter-spacing:.04em}
.pager-link{color:var(--ink-2);text-decoration:none;padding:6px 10px;border:1px solid var(--rule-2);border-radius:3px}
.pager-link:hover{color:var(--ink);border-color:var(--accent)}
.pager-link.is-off{opacity:.32;border-style:dashed}
.pager-nums{display:flex;gap:4px;flex-wrap:wrap;justify-content:center}
.pager-num{color:var(--ink-3);text-decoration:none;min-width:26px;text-align:center;padding:6px 4px;border-radius:3px}
.pager-num:hover{color:var(--ink)}
.pager-num.is-here{color:var(--bg);background:var(--accent);font-weight:600}
.pager-gap{color:var(--ink-3);min-width:18px;text-align:center;padding:6px 0}
.pager-nums-wide,.pager-nums-narrow{display:contents}
.pager-sp{display:none}
.pager-nums-narrow{display:none}
/* スマホも「新しい記事」「番号」「古い記事」を横一列に並べる(2026-11-14 本人)。
   幅が足りないので、番号は今の前後1つずつ、ボタンは「前へ」「次へ」(「新しい」「古い」は本人「微妙」) */
@media (max-width:520px){
  .pager{gap:6px}
  .pager-link{padding:6px 8px;white-space:nowrap;flex:none}
  .pager-pc{display:none}.pager-sp{display:inline}
  .pager-nums{flex-wrap:nowrap;gap:2px}
  .pager-nums-wide{display:none}
  .pager-nums-narrow{display:contents}
  .pager-num{min-width:24px;padding:6px 2px}
  .pager-gap{min-width:12px}
}

/* ── カード ─────────────────────────────────── */
.picks{margin:0 0 40px;padding:22px 0 6px;border-bottom:1px solid var(--rule)}
.picks-head{font-family:var(--mono);font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--ink-3);margin:0 0 18px;display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.picks-sub{font-family:inherit;font-size:12px;letter-spacing:0;text-transform:none;color:var(--ink-3)}
/* スマホは見出しが小さすぎて読みにくい(2026-11-14 本人) */
@media (max-width:520px){.picks-head{font-size:13px;letter-spacing:.12em;color:var(--ink-2)}}
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
.inline-media{margin:28px 0}
.inline-media-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;align-items:start}
.inline-media .embed{margin:0}
.inline-shot{margin:0;background:var(--surface);border:1px solid var(--rule);border-radius:6px;overflow:hidden}
.inline-shot img{display:block;width:100%;height:auto;max-height:520px;object-fit:contain;background:#fff}
.inline-shot figcaption{padding:9px 12px 10px;font-size:12.5px;line-height:1.7;color:var(--ink-3)}
.inline-credit{display:block;margin-top:2px;font-size:11px;letter-spacing:.02em}
.inline-clip video{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:contain;background:#000}
.inline-credit a{color:inherit}
@media (max-width:520px){.inline-media-grid{grid-template-columns:1fr}}
.pick-callout-bare span{font-family:inherit;font-size:12.5px;letter-spacing:0;text-transform:none}
@media(max-width:520px){.pick{grid-template-columns:72px 1fr}.pick-thumb img{height:48px}}
.lead{margin-bottom:8px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(268px,1fr));
  gap:1px;background:var(--rule);border-bottom:1px solid var(--rule)}
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

/* グリッドは auto-fill なので、記事数が列数の倍数でないと最終行に空きマスが
   できる。そこを次ページへの導線タイルで埋める（1枚だけなので全部の
   空きが必ず消えるわけではないが、何も無いより良い）。 */
.card-next{background:#14172e;color:#e9edf1;display:flex;flex-direction:column;
  align-items:flex-start;padding:22px 22px 24px;position:relative;overflow:hidden;
  transition:background .18s}
.card-next:hover{background:#1c2040}
/* 実物の空港表示にある「NEXT GATE」の掲示を模したブロック。案内板と同じ
   紺色にして、オレンジは数字とアイコンだけの控えめなアクセントに絞る。 */
.cn-tag{font-family:var(--mono);font-size:10px;letter-spacing:.24em;font-weight:600;
  color:#8990a0;margin-bottom:auto}
.cn-num{font-family:var(--disp);font-weight:700;font-size:56px;line-height:1;
  letter-spacing:-.02em;margin:18px 0 6px;color:var(--accent)}
.cn-num i{font-style:normal;font-size:20px;font-weight:600;color:#8990a0;margin-left:3px}
.cn-label{font-family:var(--disp);font-weight:700;font-size:16px;line-height:1.3;color:#e9edf1}
.cn-arrow{position:absolute;right:20px;bottom:18px;font-family:var(--disp);
  font-weight:700;font-size:26px;line-height:1;color:var(--accent);transition:transform .18s}
.card-next:hover .cn-arrow{transform:translateX(6px)}

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
/* 縦長の写真を 100% 幅＋contain で出すと、左右に白い帯が出ていた(2026-11-07 本人)。
   写真そのものの大きさで出し、帯を作らない。透過 PNG のために白地は写真の範囲だけに残す */
.article-hero img{display:block;width:auto;max-width:100%;height:auto;max-height:520px;margin:0 auto;background:#fff}
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
.jl-tabs{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin:0 0 28px}
.jl-tab{display:flex;flex-direction:column;gap:2px;padding:12px 14px;background:var(--surface);border:1px solid var(--rule);border-left:3px solid var(--accent);border-radius:2px}
.jl-tab b{font-family:var(--disp);font-size:22px;line-height:1.2;font-variant-numeric:tabular-nums}
.jl-tab span{font-size:12px;color:var(--ink-2)}
.jl-tab:hover{border-color:var(--ink-3)}
.jl-sec{margin:0 0 40px;scroll-margin-top:80px}
.jl-h{font-size:20px;margin:0 0 4px;display:flex;align-items:baseline;gap:10px}
.jl-h span{font-family:var(--mono);font-size:12px;color:var(--ink-3);font-weight:400}
.jl-desc{margin:0 0 16px;font-size:13px;color:var(--ink-2)}
.fx-jpy{color:var(--ink-3);font-size:.92em;white-space:nowrap}
.fx-note{font-size:12px;color:var(--ink-3);line-height:1.7;margin:-.6em 0 1.4em}

.ad-notice{max-width:var(--measure);margin:0 0 18px;padding:7px 11px;border:1px solid var(--rule-2);
  border-radius:3px;color:var(--ink-3);font-family:var(--mono);font-size:11px;letter-spacing:.03em}

/* 記事末の広告。本文の外に置き、罫線とラベルで「ここから先は広告」と
   分かるようにする。中身の高さは Google が決めるので min-height は持たせない。 */
.ad-slot{margin:44px 0 0;padding-top:14px;border-top:1px solid var(--rule)}
.ad-slot-label{margin:0 0 10px;font-family:var(--mono);font-size:10.5px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--ink-3)}
/* 広告在庫が無かったとき、AdSense は ins に data-ad-status="unfilled" を付ける。
   枠ごと畳まないと「広告」というラベルと罫線だけが残って、読者には
   何かが壊れているように見える。 */
.ad-slot:has(ins[data-ad-status="unfilled"]){display:none}
.alts{max-width:var(--measure);margin:44px 0 0;padding-top:24px;border-top:1px solid var(--rule)}
.alts h2{font-family:var(--mono);font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--ink-2);margin:0 0 16px;display:flex;align-items:center;gap:8px}
.alt-ad{background:var(--rule-2);color:var(--ink-2);padding:2px 6px;border-radius:2px;letter-spacing:.1em}
.alts ul{list-style:none;padding:0;margin:0}
.alts.gear{margin-top:32px}
.feature-hint{max-width:var(--measure);margin:28px 0 0;padding:14px 16px;border:1px solid var(--rule-2);border-radius:10px;background:var(--surface);color:var(--ink-2);font-size:14px;line-height:1.75}
.feature-hint a{color:var(--ink);font-weight:700}
.feature-hint-label{display:inline-block;margin-right:8px;padding:1px 8px;border-radius:999px;background:var(--accent);color:#fff;font-family:var(--mono);font-size:11px;letter-spacing:.12em}
.alt-item{margin:0 0 20px;display:flex;gap:16px;align-items:flex-start}
/* 写真は 11/7 に 64px→108px(本人「小さい」)。商品写真は白地が多いので白で受ける */
.alt-thumb{flex:none;display:block;width:140px;height:140px;border-radius:4px;overflow:hidden;
  background:#fff;border:1px solid var(--rule)}
.alt-thumb img{width:100%;height:100%;object-fit:contain;display:block;padding:4px;box-sizing:border-box}
@media (max-width:620px){.alt-thumb{width:112px;height:112px}}
/* 押す先のボタン(11/7 本人決定: 目立ちすぎない細い枠、サイトの等幅の字) */
.alt-cta{display:inline-flex;align-items:center;gap:6px;margin:10px 0 0;padding:7px 12px;border:1px solid var(--rule-2);
  border-radius:4px;font:500 12.5px/1 var(--mono);letter-spacing:.02em;color:var(--ink);text-decoration:none;
  transition:border-color .15s,color .15s}
.alt-cta:hover{border-color:var(--accent);color:var(--accent)}
.alt-cta span{color:var(--accent)}
/* 寄り道(記事の終わりの偶然の出会い。2026-11-08 モックB) */
.yr{max-width:var(--measure);margin:44px 0 0;padding:24px 0 0;border-top:1px solid var(--rule)}
.yr-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin:0 0 14px}
.yr-title{margin:0;font:700 15px/1.4 var(--sans);color:var(--ink)}
.yr-title small{display:block;margin-top:3px;font:400 12.5px/1.5 var(--sans);color:var(--ink-3)}
.yr-eyebrow{display:block;margin-bottom:6px;font:500 11px/1 var(--mono);letter-spacing:.08em;color:var(--accent)}
.yr-ad{margin-left:6px;padding:3px 5px;border:1px solid var(--rule-2);border-radius:3px;font:600 10.5px/1 var(--sans);color:var(--ink-3);vertical-align:2px}
.yr-shuffle{flex:none;display:inline-flex;align-items:center;gap:6px;padding:7px 11px;border:1px dashed var(--rule-2);border-radius:4px;background:none;font:500 12px/1 var(--mono);color:var(--ink-2);cursor:pointer;transition:border-color .15s,color .15s}
.yr-shuffle:hover{border-color:var(--accent);color:var(--accent)}
.yr-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.yr-card{display:flex;flex-direction:column;text-decoration:none;color:inherit}
.yr-img{display:block;aspect-ratio:1;background:#fff;border:1px solid var(--rule);border-radius:4px;overflow:hidden}
.yr-img img{width:100%;height:100%;object-fit:contain;padding:8px;box-sizing:border-box;display:block;transition:transform .3s}
.yr-card:hover .yr-img img{transform:scale(1.05)}
.yr-hook{display:block;margin:8px 0 0;font:600 13.5px/1.55 var(--sans);color:var(--ink)}
.yr-meta{display:block;margin:4px 0 0;font-size:11.5px;line-height:1.5;color:var(--ink-3)}
.yr-store{display:block;margin-top:auto;padding-top:8px;font:500 11.5px/1 var(--mono);color:var(--ink-2)}
.yr-card:hover .yr-store{color:var(--accent)}
.yr-in{animation:yrIn .25s ease-out}
@keyframes yrIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
@media (max-width:620px){.yr-grid{grid-template-columns:repeat(3,72%);overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:6px}.yr-card{scroll-snap-align:start}}
.alt-text{min-width:0}
.alt-item>a{font-size:15px;line-height:1.6}
.alt-why{margin:4px 0 0;color:var(--ink-2);font-size:13.5px;line-height:1.8}
/* 本国から直接買う導線。国内の代替品(.alts)と同じ骨格に乗せつつ、
   技適の判定を一行目の高さに置いて読み飛ばせないようにする。 */
.buy-item{margin:0 0 18px}
.buy-item>a{font-size:15px;line-height:1.6}
.buy-meta{margin:5px 0 0;display:flex;flex-wrap:wrap;align-items:center;gap:8px;
  font-family:var(--mono);font-size:11.5px;letter-spacing:.03em}
.buy-price{color:var(--ink)}
.buy-ship{color:var(--ink-3)}
.buy-giteki{border:1px solid var(--rule-2);border-radius:2px;padding:1px 6px;color:var(--ink-2)}
.buy-giteki.gi-ok{border-color:var(--cat);color:var(--cat)}
.buy-giteki.gi-warn{border-color:var(--warn);color:var(--warn)}
/* 技適未取得の警告。読み飛ばされると意味が無いので、左の罫線で
   本文とは別の種類の情報だと分かるようにする。 */
.buy-warn{margin:7px 0 0;padding-left:10px;border-left:2px solid var(--warn);
  color:var(--ink-2);font-size:13px;line-height:1.75}
.buy-note{margin:5px 0 0;color:var(--ink-2);font-size:13.5px;line-height:1.8}
.buy-coupon{margin:6px 0 0;padding:6px 10px;border:1px dashed var(--line,#ccc);border-radius:4px;font-size:13.5px;line-height:1.7}
.buy-coupon code{font-family:var(--mono,monospace);font-weight:700;letter-spacing:.06em;user-select:all}
.buy-caution{margin:14px 0 0;color:var(--ink-3);font-size:12.5px;line-height:1.85}
/* 日本上陸の続報。記事の冒頭に置く。本文(公開時点の記録)と取り違えないよう、
   左の太い罫線とバッジで「後から足した情報」だと一目で分かる形にする。 */
.jp-update{max-width:var(--measure);margin:22px 0 24px;padding:14px 16px 12px;
  background:var(--surface);border-left:3px solid var(--accent);border-radius:3px}
.jp-head{margin:0;display:flex;flex-wrap:wrap;align-items:center;gap:10px;
  font-family:var(--mono);font-size:11.5px;letter-spacing:.06em}
.jp-badge{background:var(--accent);color:#fff;padding:2px 7px;border-radius:2px;font-weight:600}
.jp-status{color:var(--ink);font-weight:600}
.jp-head time{color:var(--ink-3)}
.jp-summary{margin:10px 0 0;font-size:15px;line-height:1.85;color:var(--ink)}
.jp-update ul{list-style:none;padding:0;margin:12px 0 0}
.jp-update .buy-item{margin:0 0 12px}
.jp-src,.jp-note{margin:6px 0 0;font-size:12px;line-height:1.7;color:var(--ink-3)}
.meta-updated{color:var(--accent)}
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
.foot-meta{margin:0;display:flex;flex-wrap:wrap;gap:10px 22px;font-size:13px}
/* 折り返さないと、狭い幅でリンクが1文字ずつ縦に割れていた(2026-11-14 本人の指摘) */
.foot-meta a{white-space:nowrap}
.foot-social{display:none}
.foot-social-pc{display:contents}
.foot-meta a{color:var(--ink-2);border-bottom:1px solid transparent;padding-bottom:2px}
.foot-meta a:hover{color:var(--ink);border-bottom-color:var(--accent)}
.foot-copy{font-family:var(--mono);font-size:10.5px;color:var(--ink-3);margin:0;letter-spacing:.06em}

/* ── レスポンシブ ───────────────────────────── */
/* 案内板は狭くなるほど列を落とす。最後まで残すのは KEY と STATUS。
   「何の話か」と「今どうなっているか」が案内板の本体なので。 */
@media (max-width:1100px){
  .board-head,.board-row{grid-template-columns:64px 74px 44px minmax(0,1fr) 182px 20px}
  .b-title,.board-head span:nth-child(5){display:none}
  .b-what{display:block}
}
@media (max-width:900px){
  .nav-label{display:none}
  .board-head,.board-row{grid-template-columns:74px 44px minmax(0,1fr) 182px 20px}
  .b-flt,.board-head span:nth-child(1){display:none}
}
/* スマホ: 写真・製品名と一言・状態の3列にする(2026-11-05 本人了承)。
   それまでは記号の列だけで写真が1枚も無く、名前も「残りN日」も切れていた */
@media (max-width:620px){
  .board-head{display:none}
  .board-row{grid-template-columns:52px minmax(0,1fr) 92px;gap:11px;padding:9px 0}
  .b-flt,.b-from,.b-code,.b-arrow{display:none}
  .b-thumb{display:block;width:52px;height:52px;border-radius:4px;overflow:hidden;background:var(--raised)}
  .b-thumb img{width:100%;height:100%;object-fit:cover;display:block}
  .b-key{white-space:normal}
  .b-what{white-space:normal;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
  .st{letter-spacing:.04em;font-size:10px;gap:5px;flex-wrap:wrap;white-space:normal}
  .st em{margin-left:11px;padding-left:0;width:100%;font-size:11px}
  .board-lede{font-size:12px}
  .pop-list{grid-template-columns:1fr}
  .pop-item a{grid-template-columns:24px 84px minmax(0,1fr);gap:10px}
  .pop-img{width:84px;height:48px}
}
@media (max-width:820px){
  .card-featured{grid-template-columns:1fr;gap:14px}
  .card-featured .card-thumb{grid-row:auto}
  /* 1列にしたとき、見出し側が grid-column:2 のままだと見えない2列目が生まれ、
     写真の列が幅0に潰れて写真が消えていた(2026-11-14 本人「一部写真が出てない」) */
  .card-featured .card-meta,.card-featured .card-title,.card-featured .card-excerpt{grid-column:1;grid-row:auto}
}
@media (max-width:640px){
  .wrap{padding:0 18px}
  .hero{padding:30px 0 22px}
  .board{margin-bottom:48px}
  .article-wrap{padding-top:38px}
  .grid{grid-template-columns:1fr}
  .card-featured .card-thumb img{height:170px}
  .card-thumb img{height:150px}
  .foot-tag{margin-left:0;text-align:left;width:100%}
  .foot-board{flex-wrap:wrap}
  /* スマホは X と RSS を ONLINE の行の右端へ(2026-11-14 本人) */
  .foot-social{display:flex;gap:16px;margin-left:auto;font-family:var(--sans);font-size:13px;letter-spacing:0}
  .foot-social a{color:var(--ink-2)}
  .foot-social-pc{display:none}
}

/* ── 特集ページ ───────────────────────────────────────────── */
.nav-ft{--cat:#5fb0d9}
.feature-intro{max-width:70ch;margin:32px auto 40px}
.fp-updated{margin:14px 0 0;font-size:.78rem;color:var(--ink-3);
  font-family:var(--mono,ui-monospace,monospace);letter-spacing:.06em}

/* 特集の製品セクション。横並びのカードではなく、上から読む記事として組む */
.fp-list{max-width:760px;margin:0 auto 56px}
.pin-ft{display:flex;align-items:center;gap:20px;margin:0 0 28px;padding:16px 20px;border:1px solid var(--rule-2);
  border-left:3px solid var(--accent);border-radius:3px;background:var(--surface);color:var(--ink);text-decoration:none}
.pin-ft:hover{border-color:var(--accent)}
.pin-ft-text{flex:1;min-width:0;display:flex;flex-direction:column;gap:4px}
.pin-ft-eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.14em;color:var(--accent)}
.pin-ft-title{font-size:1.08rem;font-weight:700;line-height:1.45}
.pin-ft-go{font-size:.82rem;color:var(--accent);font-weight:600}
.pin-ft-imgs{display:flex;gap:6px;flex:0 0 auto;overflow:hidden;max-width:46%}
.pin-ft-imgs img{width:64px;height:64px;object-fit:contain;background:#fff;border-radius:4px;border:1px solid var(--rule);padding:3px;box-sizing:border-box;flex:none}
@media (max-width:620px){.pin-ft{flex-direction:column;align-items:stretch;gap:12px;padding:14px 16px}
  .pin-ft-imgs{max-width:100%}.pin-ft-imgs img{width:52px;height:52px}}
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
.fp-gallery{margin:0 0 22px}
.fp-gallery .fp-shot{margin:0 0 8px;background:#ecebe7}
.fp-gallery .fp-shot img{aspect-ratio:3/2;object-fit:contain}
.fp-gallery .fp-credit:empty{display:none}
.fp-thumbs{display:flex;gap:8px;overflow-x:auto;padding-bottom:2px}
.fp-thumb{flex:0 0 auto;width:84px;height:64px;padding:0;border:1px solid var(--line,rgba(255,255,255,.12));
  border-radius:3px;background:#ecebe7;cursor:pointer;overflow:hidden;opacity:.6}
.fp-thumb img{width:100%;height:100%;object-fit:contain;display:block}
.fp-thumb.on,.fp-thumb:hover{opacity:1;border-color:var(--ink-2)}
.fp-credit{position:absolute;right:0;bottom:0;font-size:.64rem;color:var(--ink-2);
  background:rgba(11,13,16,.82);padding:4px 9px;letter-spacing:.02em}
.fp-body{margin-bottom:24px}
.fp-body p{margin:0 0 1.1em;line-height:2;font-size:1rem;color:var(--ink-2)}
.fp-body p:last-child{margin-bottom:0}
.fp-body strong{color:var(--ink);font-weight:600}
.fp-box{margin:0 0 14px;background:var(--surface);border:1px solid var(--rule);
  border-left:3px solid var(--rule-2);border-radius:3px;padding:18px 20px}
.fp-ok .fp-box{border-left-color:#3f9e6a}
.fp-warn .fp-box{border-left-color:#d9a03f}
.fp-bad .fp-box{border-left-color:#c8503c}
.fp-cta{padding:0 0 16px;margin:0 0 16px;border-bottom:1px solid var(--rule-2);display:flex;gap:18px;align-items:flex-start}
.fp-cta:last-child{padding-bottom:0;margin-bottom:0;border-bottom:0}
.fp-cta-main{flex:1;min-width:0}
.fp-cta-img{flex:0 0 112px;height:112px;border-radius:6px;background:#fff;border:1px solid var(--rule);
  display:flex;align-items:center;justify-content:center;overflow:hidden}
.fp-cta-img img{width:100%;height:100%;object-fit:contain;padding:6px;box-sizing:border-box}
.fp-price{margin:0 0 12px;display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 10px}
.fp-price span{font-size:1.45rem;font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums;letter-spacing:.01em}
.fp-price small{font-size:.78rem;color:var(--ink-3);line-height:1.6}
.fp-buys{display:flex;flex-wrap:wrap;gap:10px}
a.fp-buy{display:inline-flex;flex-direction:column;justify-content:center;align-items:center;min-height:48px;
  min-width:210px;padding:8px 22px;border-radius:6px;border:1.5px solid var(--accent);color:var(--accent);
  background:transparent;font-weight:700;font-size:.95rem;line-height:1.3;text-decoration:none;text-align:center;
  transition:transform .12s,box-shadow .12s,background .12s}
a.fp-buy small{font-weight:400;font-size:.7rem;opacity:.85;margin-top:2px}
a.fp-buy-main{background:var(--accent);color:#1a1e24;box-shadow:0 2px 0 rgba(0,0,0,.18)}
a.fp-buy:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(255,107,61,.28)}
a.fp-buy:not(.fp-buy-main):hover{background:rgba(255,107,61,.08)}
.fp-cta-note{margin:10px 0 0;font-size:.72rem;color:var(--ink-3)}
.fp-meta{display:grid;grid-template-columns:auto 1fr;gap:10px 18px;margin:0;font-size:.88rem}
.fp-meta dt{color:var(--ink-3);white-space:nowrap}
.fp-meta dd{margin:0;color:var(--ink-2);line-height:1.85}
.fp-links{margin:0;display:flex;gap:18px;flex-wrap:wrap;font-size:.86rem}
.fp-src{color:var(--ink-3)}
@media(max-width:560px){
  .fp-name{font-size:1.28rem}
  .fp-meta{grid-template-columns:1fr;gap:4px 0}
  .fp-buys{flex-direction:column}
  .fp-cta-img{flex-basis:76px;height:76px}
  .fp-cta{gap:12px}
  a.fp-buy{width:100%;min-width:0}
  .fp-box{padding:16px}
  .fp-meta dt{margin-top:8px}
}

.fx{background:var(--surface);border:1px solid var(--rule);border-radius:3px;padding:22px 24px;margin-bottom:52px}
.fx-head{margin:0 0 8px;font-size:1rem}
.fx-lead{margin:0 0 14px;font-size:.86rem;color:var(--ink-3);line-height:1.8}
.fx-list{margin:0;padding-left:1.1em;font-size:.88rem;line-height:1.9;color:var(--ink-2)}
.fx-list li{margin-bottom:8px}
.fx-list strong{color:var(--ink)}

.fr-head{font-size:1rem;margin:0 0 16px}

.fi-grid{display:grid;gap:14px;margin-top:28px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}
.fi{display:block;background:var(--surface);border:1px solid var(--rule);border-radius:3px;
  padding:22px 24px;text-decoration:none;transition:border-color .15s}
.fi:hover{border-color:var(--accent)}
.fi-thumbs{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin:12px 0 12px}
.fi-thumbs img{display:block;width:100%;aspect-ratio:4/3;object-fit:contain;background:#fff;border:1px solid var(--rule);border-radius:2px;padding:4px;box-sizing:border-box}
.fi-eyebrow{margin:0 0 6px;font-size:.7rem;letter-spacing:.14em;color:var(--ink-3)}
.fi-title{margin:0 0 8px;font-size:1.12rem;line-height:1.4;color:var(--ink)}
.fi-lede{margin:0 0 12px;font-size:.86rem;line-height:1.8;color:var(--ink-2)}
.fi-count{margin:0;font-size:.74rem;color:var(--accent);letter-spacing:.06em}

@media(max-width:520px){
  .fi-grid{grid-template-columns:1fr}
}

/* ── 技適チェック一覧 ─────────────────────────────────────── */
[hidden]{display:none!important}
.gk{padding:26px 0 56px}
.gk-legend{margin:0 0 18px;display:grid;gap:10px;max-width:46em}
.gk-legend>div{display:grid;grid-template-columns:7.5em 1fr;gap:4px 14px;align-items:start}
.gk-legend dt{margin:0}
.gk-legend dd{margin:0;font-size:13px;line-height:1.8;color:var(--ink-2)}
.gk-legend dd strong{color:var(--ink);font-weight:700}
.gk-lead{margin:0 0 24px;max-width:46em;font-size:13px;line-height:1.8;color:var(--ink-2)}
.gk-lead a{color:var(--accent);border-bottom:1px solid color-mix(in srgb,var(--accent) 40%,transparent)}
/* 判定バッジ。.buy-giteki の見た目を借り、取得済みと対象外だけ色を足す */
.buy-giteki{display:inline-block;font-family:var(--mono);font-size:11.5px;letter-spacing:.03em;
  line-height:1.6;white-space:nowrap}
.buy-giteki.gk-ok{border-color:#3f9e6a;color:#2f7d54}
[data-theme="dark"] .buy-giteki.gk-ok{color:#6cc492}
.buy-giteki.gk-na{border-color:var(--rule-2);color:var(--ink-3)}
.gk-tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:0 0 18px}
.gk-tile{display:flex;flex-direction:column;gap:2px;padding:12px 14px;background:var(--surface);
  border:1px solid var(--rule);border-left:3px solid var(--rule-2);border-radius:3px;color:var(--ink)}
.gk-tile b{font-family:var(--disp);font-size:22px;line-height:1.2;font-weight:700;font-variant-numeric:tabular-nums}
.gk-tile span{font-size:12px;color:var(--ink-2)}
.gk-tile.gk-ok{border-left-color:#3f9e6a}
.gk-tile.gi-warn{border-left-color:var(--warn)}
.gk-tile.gk-all{border-left-color:var(--accent)}
.gk-tile:hover,.gk-tile[aria-pressed="true"]{border-color:var(--ink-3)}
.gk-tile[aria-pressed="true"]{background:var(--raised)}
.gk-filter{display:flex;flex-wrap:wrap;align-items:center;gap:10px 18px;margin:0 0 12px}
.gk-sel{font-size:12.5px;color:var(--ink-2);display:flex;align-items:center;gap:8px}
.gk-sel select{font:inherit;font-size:13px;color:var(--ink);background:var(--surface);
  border:1px solid var(--rule-2);border-radius:3px;padding:6px 10px;max-width:100%}
.gk-count{margin:0;font-family:var(--mono);font-size:11.5px;letter-spacing:.04em;color:var(--ink-3)}
.gk-table{width:100%;border-collapse:collapse;font-size:13.5px;font-variant-numeric:tabular-nums}
.gk-table th,.gk-table td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--rule);vertical-align:top}
.gk-table thead th{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;color:var(--ink-3);
  font-weight:600;border-bottom:1px solid var(--rule-2);white-space:nowrap}
.gk-table tbody tr:hover{background:var(--raised)}
.gk-prod{min-width:11em;font-weight:600}
.gk-prod a{display:flex;align-items:center;gap:12px;color:var(--ink)}
.gk-prod a span{border-bottom:1px solid var(--rule-2)}
.gk-prod a:hover span{border-bottom-color:var(--accent);color:var(--accent)}
.gk-thumb{flex:none;width:64px;height:48px;object-fit:contain;background:#fff;border:1px solid var(--rule);border-radius:2px;padding:2px;box-sizing:border-box}
.gk-note{display:block;margin-top:3px;font-size:12px;font-weight:400;line-height:1.7;color:var(--ink-3)}
.gk-empty{color:var(--ink-3)}
.gk-found{display:inline-block;margin-left:6px;font-family:var(--mono);font-size:10.5px;letter-spacing:.04em;
  padding:1px 6px;border-radius:2px;background:var(--accent);color:#fff;vertical-align:1px}
.gk-foundline{margin:-6px 0 18px;font-size:12.5px;color:var(--ink-3);display:flex;flex-wrap:wrap;gap:4px 14px;align-items:baseline}
.gk-foundline a{color:var(--ink);border-bottom:1px solid var(--rule-2)}
.gk-foundline a[aria-pressed="true"]{border-bottom-color:var(--accent);color:var(--accent)}
.gk-foundline b{font-variant-numeric:tabular-nums}
.gk-nums{font-family:var(--mono);font-size:12px;line-height:1.9}
.gk-num{display:inline-block;margin-right:10px;color:var(--ink);border-bottom:1px dotted var(--ink-3)}
.gk-num:hover{color:var(--accent);border-bottom-color:var(--accent)}
.gk-table time{font-family:var(--mono);font-size:12px;color:var(--ink-2);white-space:nowrap}
.gk-none{margin:20px 0;color:var(--ink-3);font-size:13.5px}
.gk-foot{margin:22px 0 0;font-size:12.5px;line-height:1.9;color:var(--ink-3)}
.gk-foot a{color:var(--ink-2);border-bottom:1px solid var(--rule-2);margin-left:.4em}
@media(max-width:620px){
  .gk{padding-top:20px}
  .gk-legend>div{grid-template-columns:1fr}
  .gk-tiles{grid-template-columns:repeat(2,minmax(0,1fr))}
  .gk-table,.gk-table tbody,.gk-table tr{display:block}
  .gk-table thead{display:none}
  .gk-table tr{padding:14px 0;border-bottom:1px solid var(--rule)}
  .gk-table tbody tr:hover{background:transparent}
  .gk-table td{display:block;position:relative;padding:2px 0 2px 5.6em;border:0;min-width:0}
  .gk-table td::before{content:attr(data-l);position:absolute;left:0;top:2px;
    font-size:11.5px;color:var(--ink-3);line-height:1.9}
  .gk-table .gk-prod{padding:0 0 8px;font-size:15px;line-height:1.5}
  .gk-table .gk-prod::before{content:none}
  .gk-table td.gk-empty{display:none}
  .gk-nums{line-height:1.8}
  .gk-num{overflow-wrap:anywhere}
}

/* ── 「日本で買える？使える？」の節の組み直し(2026-11-07、style_japan_section) ── */
.jp-verdict{max-width:var(--measure);margin:0 0 20px;padding:14px 16px 4px;background:var(--surface);
  border-left:3px solid var(--cat);border-radius:3px}
.jp-chips{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 10px}
.jp-chip{display:inline-flex;align-items:center;gap:6px;padding:3px 9px 3px 3px;font-size:12.5px;line-height:1.5;
  border:1px solid var(--rule-2);border-radius:999px;background:var(--bg);color:var(--ink);text-decoration:none}
.jp-chip b{font-family:var(--mono);font-size:11px;font-weight:600;padding:1px 7px;border-radius:999px;
  background:var(--ink-3);color:#fff}
.jp-chip-ok b{background:#2f8f5b}
.jp-chip-warn b{background:var(--warn)}
.jp-chip-na b{background:var(--ink-3)}
a.jp-chip-alert{border-color:var(--accent);color:var(--accent);font-weight:600}
a.jp-chip-alert b{background:var(--accent)}
a.jp-chip-alert:hover{background:color-mix(in srgb,var(--accent) 10%,var(--bg))}
.prose .jp-verdict-head{margin:0 0 6px;font-size:16.5px;line-height:1.7}
.prose .jp-verdict-text{margin:0 0 12px;font-size:14.5px;line-height:1.85;color:var(--ink-2)}
.jp-facts{max-width:var(--measure);margin:0 0 22px;border-top:1px solid var(--rule-2)}
.jp-fact{padding:12px 0 12px 14px;border-bottom:1px solid var(--rule);position:relative}
.jp-fact::before{content:"";position:absolute;left:0;top:17px;width:6px;height:6px;border-radius:50%;background:var(--cat)}
.jp-fact dt{font-weight:700;font-size:14px;line-height:1.6;margin:0 0 2px}
.jp-fact dt a{color:inherit}
.jp-fact dd{margin:0;font-size:14.5px;line-height:1.85}
.jp-rows{max-width:var(--measure);margin:0 0 22px;border-top:1px solid var(--rule-2)}
.prose .jp-fact > p{margin:0;font-size:14.5px;line-height:1.85}
.prose .jp-fact > p.jp-fact-h{margin:0 0 2px;font-size:14px;font-weight:700;line-height:1.6}
.prose .jp-foot{margin:0 0 18px;font-size:12.5px;line-height:1.8;color:var(--ink-3)}
.prose .jp-open-head{margin:0 0 8px;font-size:13.5px;font-weight:700;color:var(--ink-2)}
.prose ul.jp-open{list-style:none;padding:0;margin:0 0 22px;display:grid;gap:6px}
.prose ul.jp-open li{margin:0;padding:8px 12px 8px 38px;position:relative;background:var(--surface);
  border-radius:3px;font-size:14.5px;line-height:1.6}
.prose ul.jp-open li::before{content:"?";position:absolute;left:10px;top:50%;transform:translateY(-50%);
  width:18px;height:18px;border-radius:50%;border:1.5px solid var(--ink-3);color:var(--ink-3);
  font:600 11px/15px var(--mono);text-align:center}
.jp-next{max-width:var(--measure);margin:0 0 20px;padding:12px 16px 2px;border:1px solid var(--rule-2);border-radius:3px}
.prose .jp-next-head{margin:0 0 4px;font-size:12px;font-family:var(--mono);font-weight:600;letter-spacing:.06em;color:var(--cat)}
.prose .jp-next p{font-size:14.5px;line-height:1.85}

/* ── 日本上陸アラート(記事の「日本で買える？使える？」の節の末尾) ── */
.jp-alert{max-width:var(--measure);margin:22px 0 26px;padding:14px 16px 12px;
  background:var(--surface);border-left:3px solid var(--accent);border-radius:3px}
.jp-alert-text{margin:10px 0 0;font-size:14.5px;line-height:1.85;color:var(--ink)}
.jp-alert-form{display:flex;gap:8px;margin:12px 0 0;flex-wrap:wrap}
.jp-alert-form input[type=email]{flex:1 1 220px;min-width:0;padding:9px 11px;font-size:15px;
  border:1px solid var(--rule);border-radius:3px;background:var(--bg);color:var(--ink)}
.jp-alert-form input[type=email]:focus{outline:2px solid var(--accent);outline-offset:1px;border-color:var(--accent)}
.jp-alert-form button{flex:none;padding:9px 16px;font-size:14px;font-weight:600;
  background:var(--accent);color:#fff;border:0;border-radius:3px;cursor:pointer}
.jp-alert-form button:disabled{opacity:.6;cursor:default}
.jp-alert-hp{position:absolute;left:-9999px;width:1px;height:1px;opacity:0}
.videos-after .va-lead{margin:0 0 14px;font-size:13px;line-height:1.8;color:var(--ink-3)}
.videos-after figcaption .va-note{display:block;color:var(--ink);font-size:14px;line-height:1.7}
.videos-after figcaption .va-meta{display:block;font-size:12px;color:var(--ink-3);line-height:1.6;margin-top:2px}
.jp-buynow{max-width:var(--measure);margin:22px 0 0;padding:14px 16px 12px;
  background:var(--surface);border-left:3px solid var(--ink-3);border-radius:3px}
.jp-badge-buy{background:var(--ink)}
.jp-buynow-text{margin:10px 0 0;font-size:14.5px;line-height:1.85;color:var(--ink)}
.jp-buynow-link{display:inline-block;margin:8px 0 0;font-weight:600;font-size:14.5px}
.jp-alert-track{margin:8px 0 0;font-size:13px;line-height:1.8;color:var(--ink-2,var(--ink))}
.jp-alert-track a{margin-left:4px;white-space:nowrap}
.jp-alert-note{margin:8px 0 0;font-size:12px;line-height:1.7;color:var(--ink-3)}
.jp-alert-note a{color:var(--ink-3)}
.jp-alert-msg{margin:6px 0 0;font-size:13px;line-height:1.7;color:var(--accent);min-height:0}
.jp-alert-msg:empty{display:none}
"""


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#fbfaf8"/>
  <circle cx="32" cy="32" r="7" fill="#b4472b"/>
  <circle cx="32" cy="32" r="15" fill="none" stroke="#b4472b" stroke-width="3" stroke-opacity=".55"/>
  <circle cx="32" cy="32" r="23" fill="none" stroke="#b4472b" stroke-width="3" stroke-opacity=".25"/>
</svg>
"""


# ────────────────────────────── メイン ──────────────────────────────
CSS += HUB_CSS
# CSS の中身が変わったら読み直させる版(2026-11-14)。style.css は10分キャッシュされ、公開直後に
# 新しい HTML と古い CSS が組み合わさって崩れるため
CSS_VER = __import__("hashlib").md5(CSS.encode("utf-8")).hexdigest()[:8]


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
    # 同じ slug の記事が2本あると、後の記事が前の記事のページを黙って上書きする。
    # 毎朝の記事生成が書いた製品を見落とし、同じ製品を2回書いていた(2026-10-11 に5組
    # 見つかった)。ビルドを止めれば、検証を通らない記事は公開されない。
    seen_slugs: dict[str, str] = {}
    for p in posts:
        if p["slug"] in seen_slugs:
            sys.exit(f"✗ slug が重複しています: {p['slug']}\n"
                     f"  {seen_slugs[p['slug']]} と {p['date']} の「{p['title']}」。"
                     f"同じ製品なら新しいほうの記事を消す")
        seen_slugs[p["slug"]] = f"{p['date']} の「{p['title']}」"
    MERGED[:] = [p for p in posts if str(p.get("merged_into") or "").strip()]
    posts = [p for p in posts if not any(p is m for m in MERGED)]
    _live = {p["slug"] for p in posts}
    for m in MERGED:
        if str(m["merged_into"]).strip() not in _live:
            sys.exit(f"✗ merged_into の行き先がありません: {m['slug']} → {m['merged_into']}")
    if MERGED:
        print(f"■ 続報まとめ: {len(MERGED)}本を残す記事へ転送")
    features = []
    if FEATURES_DIR.exists():
        features = [f for f in (parse_feature(x)
                                for x in sorted(FEATURES_DIR.glob("*.md"))) if f]
        features.sort(key=lambda f: str(f.get("updated") or ""), reverse=True)
        # front matter に pin: true がある特集は一覧の先頭に固定する(2026-11-07 ブラックフライデーの特集。セール後に外す)
        features.sort(key=lambda f: not f.get("pin"))
    FEATURES_FOR_HINT[:] = features
    YORIMICHI[:] = build_yorimichi(site["site"], features)
    print(f"■ 寄り道の棚 {len(YORIMICHI)}件")
    LANDED_AFTER[0] = count_landed_after(posts)
    # 日付 → priority（front matter で 1 以上を指定するとその日の先頭に来る）→ slug
    posts.sort(key=lambda p: (p["date"], p.get("priority", 0), p["slug"]), reverse=True)
    # 便名は掲載が古い順の通し番号。既存記事の番号がずれないよう昇順で振る。
    for n, q in enumerate(sorted(posts, key=lambda x: (x["date"], x["slug"])), start=1):
        q["flight"] = f"GT {n:04d}"
    print(f"■ 記事 {len(posts)}本")
    TOPICS[:] = load_topics(posts)
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
    # トップページの装飾用画像。手描きのSVGでは実写的なシルエットは再現できないため、
    # 用意した透過PNGをそのままコピーする（リポジトリの assets/ に置いてある）。
    hero_plane_src = ROOT / "assets" / "hero-plane.png"
    if hero_plane_src.exists():
        shutil.copy2(hero_plane_src, PUBLIC / "assets" / "hero-plane.png")
    if CLIPS.exists():
        shutil.copytree(CLIPS, PUBLIC / "clips")

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

        # note の週まとめの見出し画像(scripts/note_weekly.py)。本人が note に
        # アップロードするので、文字とサイトの配色だけの自前の画像にしている。
        notes = 0
        for f in sorted((ROOT / "data" / "note").glob("*.md")):
            m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", f.read_text(encoding="utf-8"), re.S)
            fm = (yaml.safe_load(m.group(1)) or {}) if m else {}
            if fm.get("title") and fm.get("header_hook"):
                # 2026-11-01 からの形(5選を大きく＋主役の一言)。写真は TamakoStock が重ねる
                if ogp.render_note_header(str(fm["title"]), str(fm.get("label") or "WEEKLY"),
                                          str(fm["header_hook"]), str(fm.get("header_sub") or ""),
                                          site["site"]["title"], PUBLIC / "note" / f"{f.stem}.png"):
                    notes += 1
            elif fm.get("title") and ogp.render(str(fm["title"]), str(fm.get("label") or "WEEKLY"),
                                               site["site"]["title"], PUBLIC / "note" / f"{f.stem}.png",
                                               photo_credit="製品画像: 各メーカー公式サイト・クラウドファンディングページより"):
                notes += 1
            # X 記事の表紙(横長 5:2)。note と同じ週まとめを X 記事にも出す(2026-10-11 開始)
            # header_hook のある週は note と同じ形(写真は TamakoStock が X_SLOTS に重ねる。2026-11-01〜)
            if fm.get("header_hook"):
                ogp.render_note_header(str(fm["title"]), str(fm.get("label") or "WEEKLY"),
                                       str(fm["header_hook"]), str(fm.get("header_sub") or ""),
                                       site["site"]["title"], PUBLIC / "note" / f"{f.stem}-x.png", layout="x")
            elif fm.get("title"):
                ogp.render(str(fm["title"]), str(fm.get("label") or "WEEKLY"), site["site"]["title"],
                           PUBLIC / "note" / f"{f.stem}-x.png", size=(1500, 600))
        if notes:
            print(f"■ note の見出し画像 {notes}枚")

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
    (PUBLIC / "media.html").write_text(render_media(site, posts), encoding="utf-8")
    (PUBLIC / "jpn.html").write_text(render_domestic_cf(site, posts), encoding="utf-8")
    # 技適の解説は製品を並べる特集とは別物なので一覧には出さず、技適一覧から入る(2026-10-27 本人判断)
    (PUBLIC / "features.html").write_text(render_features_index(
        site, [f for f in features if f.get("slug") != GITEKI_FEATURE_SLUG]),
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
    (PUBLIC / GITEKI_PATH).mkdir(parents=True, exist_ok=True)
    (PUBLIC / GITEKI_PATH / "index.html").write_text(render_giteki(site, posts), encoding="utf-8")
    write_giteki_data(site, posts)
    write_landing_data(site, posts)
    (PUBLIC / "yorimichi.json").write_text(json.dumps(YORIMICHI, ensure_ascii=False, separators=(",", ":")),
                                           encoding="utf-8")
    gc = giteki_counts(posts)
    print(f"■ 技適の記録 {gc['記録']}本 / 取得済み {gc['取得済み']} / 確認できない {gc['確認できない']} "
          f"/ 対象外 {gc['対象外']} / 未記入 {gc['未記入']}")
    no_num = [p["slug"] for p in posts
              if p.get("giteki") and p["giteki"]["status"] == "取得済み" and not p["giteki"]["number"]]
    if no_num:
        print(f"  ! 取得済みなのに技適番号が空: {len(no_num)}本（番号を確認できたときだけ「取得済み」にする）")
        for slug in no_num[:5]:
            print(f"    {slug}")
    for p in posts:
        (PUBLIC / p["path"]).write_text(render_post(site, p, posts), encoding="utf-8")
    _by = {p["slug"]: p for p in posts}
    for m in MERGED:
        (PUBLIC / m["path"]).write_text(merged_redirect(site, m, _by[str(m["merged_into"]).strip()]), encoding="utf-8")
    if TOPICS:
        (PUBLIC / "topic").mkdir(parents=True, exist_ok=True)
        (PUBLIC / "topic" / "index.html").write_text(render_topics_index(site), encoding="utf-8")
        for t in TOPICS:
            (PUBLIC / t["path"]).write_text(render_topic(site, t), encoding="utf-8")
        print(f"■ 話題ページ {len(TOPICS)}本 (" + "・".join(f"{t['label']}{len(t['posts'])}" for t in TOPICS) + ")")
    write_weekly_data(site)
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

    # 見つからないページ(GitHub Pages は 404.html を出す)。リンクの後ろに「）。」などが
    # くっついて開けないことがよくある(2026-11-07)ので、.html や / より後ろの余計な文字を
    # 取ったアドレスへ移す。それでも無ければトップへの案内だけ出す。
    (PUBLIC / "404.html").write_text("""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>ページが見つかりません — Gadget Terminal</title>
<script>(function(){var p=decodeURIComponent(location.pathname),m=p.match(/^(.*?\\.html)./)||p.match(/^(\\/(?:posts|features)\\/[A-Za-z0-9._-]+?)[^A-Za-z0-9._\\/-].*$/);
if(m&&m[1]!==p){location.replace(m[1]+location.search+location.hash);}})();</script>
<style>body{margin:0;font-family:system-ui,sans-serif;background:#f6f5f1;color:#1d1d1f;display:grid;place-items:center;min-height:100vh;text-align:center;padding:16px}a{color:#0a5bd3}</style>
</head><body><main><h1>ページが見つかりません</h1><p>アドレスが変わったか、途中で切れている可能性があります。</p>
<p><a href="/">Gadget Terminal のトップへ</a></p></main></body></html>
""", encoding="utf-8")
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
