#!/usr/bin/env python3
"""Kickstarter のプロジェクトを読む。リターン(価格・数量)・本文・FAQ・最新数値まで。

    python3 scripts/ks_fetch.py <Kickstarter のプロジェクトURL> [--json]
    python3 scripts/ks_fetch.py <URL> --no-cache --runner    # ランナー相当(全文取得を飛ばす)を再現

なぜこのスクリプトがあるか
  GitHub Actions のランナー(Microsoft AS8075)からは、Kickstarter のプロジェクトページ・
  /rewards・/faqs・/graph・oEmbed が Cloudflare の 403 で全滅する(2026-10-18 実測)。
  一方、自宅PCからは全部取れる。そこで次の順に試す。

    (a) data/kscache/<作り手>__<slug>.json が 72 時間以内ならそれを使う
        (自宅PCが毎晩 ks_prefetch.py で貯める。数値だけ stats.json で最新化する)
    (b) 全文取得: プロジェクトページ(埋め込みJSON: リターン・数値)+ /graph の GraphQL
        (本文・リスク・FAQ)。自宅PCでだけ通る。
    (c) 取れないとき(403 / "Just a moment"): ランナーから見える
        card.html(基本情報)・stats.json(数値)・posts.atom(更新)・Kicktraq に落とす。
        このとき partial: true、missing に story / rewards / faq が入る。

重要な実装メモ
  - **Python の urllib だと Cloudflare に 403 で弾かれる**(TLS指紋)。同じURLを curl は
    200 で取れる。なので HTTP は curl を子プロセスで呼ぶ(無ければ urllib にフォールバック)。
    さらに **Windows 標準の curl.exe(C:/Windows/System32)は HTTP/2 だと 403** になる
    (Git for Windows 同梱の curl は 200)。`--http1.1` を付ければどちらでも 200(2026-10-18 実測)。
  - ページ内の `window.current_project = "..."` は、HTML実体参照(&quot;)に加えて
    バックスラッシュが二重(JS文字列リテラル)になっている。unescape 後に `\\\\`→`\\` が要る。
  - 本文(story)・risks・FAQ はページ本体に無い。React が /graph から取っている。

取れなかった値は欠けたままにする。補完・推測はしない。
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

if sys.platform == "win32":  # Windows のコンソールは既定 cp932
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "data" / "kscache"
CACHE_MAX_AGE_H = 72

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
JST = dt.timezone(dt.timedelta(hours=9))
STORY_MAX = 12000
BS = chr(92)

STATE_JA = {"live": "募集中", "successful": "成功して終了", "failed": "未達で終了",
            "canceled": "中止", "suspended": "停止", "submitted": "審査中",
            "started": "準備中", "draft": "下書き", "purged": "削除済み"}


# ----------------------------------------------------------------- 共通
def now_jst() -> dt.datetime:
    return dt.datetime.now(JST).replace(microsecond=0)


def iso(ts) -> str | None:
    if not ts:
        return None
    return dt.datetime.fromtimestamp(int(ts), JST).isoformat()


def parse_iso(s: str | None) -> dt.datetime | None:
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(s)
    except ValueError:
        return None


def num(v):
    """'138668.0' / 138668.0 → 138668 (整数なら整数で)。"""
    if v is None or v == "":
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return int(f) if f == int(f) else round(f, 2)


KS_URL = re.compile(r"https?://(?:www\.)?kickstarter\.com/projects/([^/\s?#\"'<>)\]]+)/([^/\s?#\"'<>)\].,]+)", re.I)


def normalize_url(url: str) -> tuple[str, str, str]:
    """→ (creator, slug, 正規URL)。クエリ・ref・末尾のサブパスは捨てる。"""
    m = KS_URL.search(url.strip())
    if not m:
        raise ValueError(f"Kickstarter のプロジェクトURLではありません: {url}")
    creator, slug = m.group(1), m.group(2)
    return creator, slug, f"https://www.kickstarter.com/projects/{creator}/{slug}"


def cache_path(creator: str, slug: str) -> Path:
    return CACHE_DIR / f"{creator}__{slug}.json"


# ----------------------------------------------------------------- HTTP
class Http:
    """curl 経由の簡易クライアント。Cookie を保持し、リクエスト間に 1〜2 秒空ける。"""

    def __init__(self, gap=(1.0, 2.0)):
        self.curl = os.environ.get("KS_CURL") or shutil.which("curl")
        fd, self.jar = tempfile.mkstemp(prefix="ksjar_")
        os.close(fd)
        self.gap = gap
        self._last = 0.0

    def close(self):
        try:
            os.remove(self.jar)
        except OSError:
            pass

    def _wait(self):
        d = random.uniform(*self.gap) - (time.time() - self._last)
        if d > 0:
            time.sleep(d)

    def request(self, url, headers=None, post: str | None = None, timeout=25) -> tuple[int, str]:
        """→ (HTTPステータス, 本文)。通信失敗は (0, '')。"""
        self._wait()
        try:
            if self.curl:
                return self._curl(url, headers or {}, post, timeout)
            return self._urllib(url, headers or {}, post, timeout)
        finally:
            self._last = time.time()

    def _curl(self, url, headers, post, timeout):
        cmd = [self.curl, "-sS", "-L", "--compressed", "-4", "--http1.1", "-m", str(timeout),
               "-A", UA, "-H", "Accept-Language: en-US,en;q=0.9",
               "-b", self.jar, "-c", self.jar, "-w", "\n%{http_code}"]
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
        if post is not None:
            cmd += ["--data-binary", "@-"]
        cmd.append(url)
        kw = {}
        if sys.platform == "win32":
            kw["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
        try:
            p = subprocess.run(cmd, input=post.encode("utf-8") if post is not None else None,
                               capture_output=True, timeout=timeout + 10, **kw)
        except (subprocess.TimeoutExpired, OSError):
            return 0, ""
        out = p.stdout
        i = out.rfind(b"\n")
        try:
            status = int(out[i + 1:].strip() or 0)
        except ValueError:
            status = 0
        return status, out[:i].decode("utf-8", errors="replace")

    def _urllib(self, url, headers, post, timeout):
        h = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9", **headers}
        req = urllib.request.Request(url, data=post.encode("utf-8") if post is not None else None, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", errors="replace")
        except OSError:
            return 0, ""


def is_blocked(status: int, text: str) -> bool:
    return status in (403, 429, 503) or "Just a moment" in text[:4000] or "cf-challenge" in text[:4000]


def get_retry(http: Http, url, headers=None, post=None, retries=2) -> tuple[int, str]:
    """通信失敗・ブロック・5xx は 2 回までバックオフして再試行。404 などは再試行しない。"""
    status, text = 0, ""
    for i in range(retries + 1):
        status, text = http.request(url, headers, post)
        if status == 200 and not is_blocked(status, text):
            return status, text
        if status == 404:
            break
        if i < retries:
            time.sleep(3 * (i + 1) ** 2)  # 3秒, 12秒
    return status, text


# ----------------------------------------------------------------- 解析
def parse_current_project(page: str) -> dict | None:
    """ページ(project / card.html)の window.current_project を dict にする。"""
    m = re.search(r'window\.current_project\s*=\s*"(.*)";?[ \t]*$', page, re.M)
    if not m:
        return None
    s = html.unescape(m.group(1))
    for cand in (s.replace(BS + BS, BS), s):  # JS文字列リテラルの二重バックスラッシュを戻す
        try:
            d = json.loads(cand)
            if isinstance(d, dict):
                return d
        except ValueError:
            continue
    return None


def csrf_token(page: str) -> str | None:
    m = re.search(r'name="csrf-token"\s+content="([^"]+)"', page)
    return m.group(1) if m else None


class _Text(HTMLParser):
    """HTML → 行テキスト。見出しは '## '、リストは '- ' を付ける。画像URLも拾う。"""
    HEAD = {"h1", "h2", "h3", "h4", "h5", "h6"}
    BLOCK = {"p", "div", "section", "figure", "figcaption", "ul", "ol", "table", "tr", "blockquote",
             "br", "hr", "article", "header", "footer", "details", "summary"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines: list[str] = []
        self.images: list[str] = []
        self.buf: list[str] = []
        self.prefix = ""
        self.skip = 0

    def flush(self):
        line = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        if line:
            self.lines.append(self.prefix + line)
        self.buf = []
        self.prefix = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style"):
            self.skip += 1
        elif tag in self.HEAD:
            self.flush()
            self.prefix = "## "
        elif tag == "li":
            self.flush()
            self.prefix = "- "
        elif tag in self.BLOCK:
            self.flush()
        elif tag == "img":
            src = a.get("src") or a.get("data-src") or ""
            if src.startswith("//"):
                src = "https:" + src
            if src.startswith("http"):
                self.images.append(src)
            alt = (a.get("alt") or "").strip()
            if alt:
                self.flush()
                self.lines.append(f"[画像: {alt}]")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        elif tag in self.HEAD or tag == "li" or tag in self.BLOCK:
            self.flush()

    def handle_data(self, data):
        if not self.skip:
            self.buf.append(data)


def html_to_text(src: str) -> tuple[str, list[str]]:
    p = _Text()
    p.feed(src or "")
    p.flush()
    seen, imgs = set(), []
    for u in p.images:
        key = u.split("?")[0]
        if key not in seen:
            seen.add(key)
            imgs.append(u)
    return "\n".join(p.lines), imgs


def cap_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit]
    cut = cut[:cut.rfind("\n")] if "\n" in cut[limit // 2:] else cut
    return cut + "\n…(以下省略)"


def short(s: str | None, n: int) -> str | None:
    if not s:
        return None
    s = re.sub(r"[ \t]+", " ", s.replace("\r", "")).strip()
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s if len(s) <= n else s[:n].rstrip() + "…"


def base_fields(p: dict, creator: str, slug: str, canon: str) -> dict:
    """current_project の dict から基本項目を作る(リターン等は含めない)。"""
    cur = p.get("currency")
    goal, pledged = num(p.get("goal")), num(p.get("pledged"))
    out = {
        "url": canon, "creator_slug": creator, "slug": slug,
        "name": p.get("name"), "blurb": p.get("blurb"),
        "creator_name": (p.get("creator") or {}).get("name"),
        "location": (p.get("location") or {}).get("displayable_name"),
        "country": p.get("country"),
        "category": (p.get("category") or {}).get("name"),
        "category_slug": (p.get("category") or {}).get("slug"),
        "staff_pick": p.get("staff_pick"),
        "currency": cur, "goal": goal, "pledged": pledged,
        "usd_pledged": num(p.get("usd_pledged")),
        "backers": p.get("backers_count"),
        "percent_funded": round(pledged / goal * 100, 1) if goal and pledged is not None else None,
        "state": p.get("state"),
        "launched_at": iso(p.get("launched_at")), "deadline": iso(p.get("deadline")),
        "comments_count": p.get("comments_count"), "updates_count": p.get("updates_count"),
        "photo": ((p.get("photo") or {}).get("full") or "").split("?")[0] or None,
    }
    sites = ((p.get("creator") or {}).get("websites") or [])
    if sites:
        out["creator_websites"] = [w.get("url") for w in sites if w.get("url")]
    return out


def parse_rewards(p: dict) -> tuple[list[dict], list[dict]]:
    rewards = []
    for r in p.get("rewards") or []:
        if not r.get("id") or r.get("reward_type") == "no_reward":
            continue  # id 0 は「リターンなし」の支援枠
        items = []
        for ri in r.get("rewards_items") or []:
            nm = (ri.get("item") or {}).get("name")
            if nm:
                items.append(f"{nm} ×{ri.get('quantity') or 1}")
        desc = r.get("description") or r.get("reward")
        d = {
            "title": r.get("title") or r.get("title_for_backing_tier"),
            "minimum": num(r.get("minimum")), "currency": p.get("currency"),
            "limit": r.get("limit"), "remaining": r.get("remaining"),
            "backers": r.get("backers_count"), "available": r.get("available"),
            "estimated_delivery": (dt.datetime.fromtimestamp(int(r["estimated_delivery_on"]), JST).strftime("%Y-%m")
                                   if r.get("estimated_delivery_on") else None),
            "shipping": r.get("shipping_summary"),
            "items": items,
            "description": short(desc, 300),
        }
        rewards.append(d)
    addons = []
    for r in p.get("add_ons") or []:
        addons.append({"minimum": num(r.get("minimum")), "currency": p.get("currency"),
                       "description": short(r.get("reward") or r.get("description"), 160),
                       "limit": r.get("limit"), "remaining": r.get("remaining")})
    return rewards, addons


GQL = ("query Q($slug: String!) { project(slug: $slug) { story risks "
       "faqs { nodes { question answer } } } }")


def fetch_graph(http: Http, creator, slug, canon, token) -> dict | None:
    body = json.dumps({"query": GQL, "variables": {"slug": f"{creator}/{slug}"}})
    status, text = get_retry(http, "https://www.kickstarter.com/graph", post=body, retries=1, headers={
        "Content-Type": "application/json", "X-CSRF-Token": token or "", "Referer": canon,
        "Origin": "https://www.kickstarter.com", "Accept": "application/json"})
    if status != 200:
        return None
    try:
        return ((json.loads(text).get("data") or {}).get("project")) or None
    except ValueError:
        return None


def parse_faqs_html(page: str) -> list[dict]:
    """/faqs ページの <details> から Q/A を拾う(GraphQL が使えないとき用)。"""
    out = []
    for m in re.finditer(r'<details[^>]*id="project_faq_\d+".*?</details>', page, re.S):
        blk = m.group(0)
        q = re.search(r"<summary[^>]*>(.*?)<span", blk, re.S)
        a = re.search(r'kds-accordion__content">(.*?)<small', blk, re.S)
        if q and a:
            qt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", q.group(1)))).strip()
            at, _ = html_to_text(a.group(1))
            if qt and at:
                out.append({"q": qt, "a": at})
    return out


def parse_atom(xml: str, n=5) -> list[dict]:
    out = []
    for m in re.finditer(r"<entry>(.*?)</entry>", xml, re.S):
        e = m.group(1)

        def tag(t):
            x = re.search(rf"<{t}[^>]*>(.*?)</{t}>", e, re.S)
            return html.unescape(x.group(1)).strip() if x else ""
        link = re.search(r'<link[^>]*href="([^"]+)"', e)
        body, _ = html_to_text(tag("content"))
        if body.startswith("This post is for backers only"):
            body = ""  # 支援者限定の定型文は中身が無いので捨てる
        out.append({"title": tag("title"), "published": tag("published"),
                    "url": link.group(1) if link else None, "text": short(body, 600)})
        if len(out) >= n:
            break
    return out


def fetch_updates(http: Http, canon: str) -> list[dict] | None:
    status, text = http.request(canon + "/posts.atom")
    if status == 200 and "<feed" in text:
        return parse_atom(text)
    return None


def fetch_stats(http: Http, canon: str) -> dict | None:
    status, text = get_retry(http, canon + "/stats.json?v=1", retries=1)
    if status != 200:
        return None
    try:
        p = json.loads(text)["project"]
    except (ValueError, KeyError):
        return None
    return {"pledged": num(p.get("pledged")), "backers": p.get("backers_count"),
            "state": p.get("state"), "comments_count": p.get("comments_count")}


def apply_stats(d: dict, st: dict) -> None:
    d["pledged"], d["backers"], d["state"] = st["pledged"], st["backers"], st["state"]
    if st.get("comments_count") is not None:
        d["comments_count"] = st["comments_count"]
    if d.get("goal") and d.get("pledged") is not None:
        d["percent_funded"] = round(d["pledged"] / d["goal"] * 100, 1)
    d["live_numbers_at"] = now_jst().isoformat()


def fetch_kicktraq(http: Http, creator: str, slug: str) -> dict | None:
    status, text = http.request(f"https://www.kicktraq.com/projects/{creator}/{slug}/")
    if status != 200:
        return None
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text)))
    out = {}
    for key, pat in (("backers", r"Backers: ([\d,]+)"), ("avg_daily_pledges", r"Average Daily Pledges: ([^ ]+)"),
                     ("avg_per_backer", r"Average Pledge Per Backer: ([^ ]+)"),
                     ("funding", r"Funding: (.+?) Dates:"), ("dates", r"Dates: (.+?) Project By:")):
        m = re.search(pat, t)
        if m:
            out[key] = m.group(1).strip()
    return out or None


# ----------------------------------------------------------------- 取得本体
def fetch_full(creator: str, slug: str, http: Http | None = None) -> dict:
    """自宅PC向けの全文取得。ブロックされたら RuntimeError(blocked)。"""
    _, _, canon = normalize_url(f"https://www.kickstarter.com/projects/{creator}/{slug}")
    own = http is None
    http = http or Http()
    try:
        status, page = get_retry(http, canon)
        if status != 200 or is_blocked(status, page):
            raise RuntimeError(f"blocked:{status}" if is_blocked(status, page) else f"http:{status}")
        p = parse_current_project(page)
        if not p:
            raise RuntimeError("parse:current_project が見つからない")
        d = base_fields(p, creator, slug, canon)
        d["rewards"], d["add_ons"] = parse_rewards(p)
        missing = [] if d["rewards"] else ["rewards"]

        g = fetch_graph(http, creator, slug, canon, csrf_token(page))
        if g and g.get("story"):
            text, imgs = html_to_text(g["story"])
            d["story_text"] = cap_text(text, STORY_MAX)
            d["story_images"] = imgs[:40]
            risks, _ = html_to_text(g.get("risks") or "")
            d["risks"] = short(risks, 3000)
            nodes = ((g.get("faqs") or {}).get("nodes")) or []
            d["faq"] = [{"q": short(n.get("question"), 200), "a": short(n.get("answer"), 500)}
                        for n in nodes[:15] if n.get("question")]
        else:
            missing.append("story")
        if "faq" not in d:
            st, fp = get_retry(http, canon + "/faqs", retries=1)
            faqs = parse_faqs_html(fp) if st == 200 else []
            if faqs:
                d["faq"] = [{"q": short(f["q"], 200), "a": short(f["a"], 500)} for f in faqs[:15]]
            else:
                missing.append("faq")
        d["updates"] = fetch_updates(http, canon) or []
        d.update({"source": "home", "partial": bool(missing), "missing": missing,
                  "fetched_at": now_jst().isoformat(), "schema": 1})
        return d
    finally:
        if own:
            http.close()


def fetch_runner(creator: str, slug: str, http: Http | None = None) -> dict:
    """ランナー(403 になる環境)でも取れるエンドポイントだけで作る縮退版。"""
    _, _, canon = normalize_url(f"https://www.kickstarter.com/projects/{creator}/{slug}")
    own = http is None
    http = http or Http()
    try:
        d: dict = {"url": canon, "creator_slug": creator, "slug": slug}
        status, text = get_retry(http, canon + "/widget/card.html?v=2", retries=1)
        p = parse_current_project(text) if status == 200 else None
        if p:
            d.update(base_fields(p, creator, slug, canon))
        st = fetch_stats(http, canon)
        if st:
            apply_stats(d, st)
        d["updates"] = fetch_updates(http, canon) or []
        kt = fetch_kicktraq(http, creator, slug)
        if kt:
            d["kicktraq"] = kt
        if not p and not st:
            raise RuntimeError("blocked:カード・stats とも取得できない")
        d.update({"source": "runner", "partial": True, "missing": ["story", "rewards", "faq"],
                  "fetched_at": now_jst().isoformat(), "schema": 1})
        return d
    finally:
        if own:
            http.close()


def load_cache(creator, slug) -> dict | None:
    f = cache_path(creator, slug)
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def cache_age_h(d: dict) -> float | None:
    t = parse_iso(d.get("fetched_at"))
    return (now_jst() - t).total_seconds() / 3600 if t else None


def get_project(url: str, use_cache=True, runner=False) -> dict:
    creator, slug, canon = normalize_url(url)
    notes: list[str] = []
    if use_cache:
        c = load_cache(creator, slug)
        age = cache_age_h(c) if c else None
        if c and age is not None and age <= CACHE_MAX_AGE_H:
            http = Http()
            try:
                st = fetch_stats(http, canon)
            finally:
                http.close()
            if st:
                apply_stats(c, st)
            c["source"] = "cache"
            c["cache_age_h"] = round(age, 1)
            c["live_refreshed"] = bool(st)
            return c
        if c:
            notes.append(f"キャッシュは {age:.0f} 時間前のもので古いため使わなかった" if age is not None
                         else "キャッシュの取得時刻が読めないため使わなかった")
    http = Http()
    try:
        if not runner:
            try:
                d = fetch_full(creator, slug, http)
                d["notes"] = notes
                return d
            except RuntimeError as e:
                notes.append(f"全文取得に失敗({e})。ランナー用の縮退取得に切り替えた")
        d = fetch_runner(creator, slug, http)
        d["notes"] = notes + (["--runner 指定のため全文取得を飛ばした"] if runner else [])
        return d
    finally:
        http.close()


# ----------------------------------------------------------------- 表示
def money(v, cur) -> str:
    return "不明" if v is None else f"{v:,} {cur or ''}".strip()


def fmt_dt(s: str | None) -> str:
    t = parse_iso(s)
    return t.astimezone(JST).strftime("%Y-%m-%d %H:%M JST") if t else "不明"


def render(d: dict) -> str:
    L: list[str] = []
    cur = d.get("currency")
    src = d.get("source")
    fa = fmt_dt(d.get("fetched_at"))
    L.append(f"■ {d.get('name') or d.get('slug')}")
    L.append(f"URL: {d['url']}")
    if src == "cache":
        s = f"夜間先読みキャッシュ(全文取得: {fa})"
        s += f" / 数値は {fmt_dt(d.get('live_numbers_at'))} に stats.json で更新" if d.get("live_refreshed") \
            else " / 数値の更新はできなかった(キャッシュ時点の値)"
    elif src == "home":
        s = f"自宅PCから直接取得(全文)  取得: {fa}"
    else:
        s = f"ランナー用フォールバック(card.html + stats.json + posts.atom + Kicktraq)  取得: {fa}"
    L.append(f"source: {src} — {s}")
    L.append("掲載時点の目安: " + (fmt_dt(d.get("live_numbers_at")) if d.get("live_numbers_at") else fa)
             + "(記事には「◯月◯日時点」と書く)")
    for n in d.get("notes") or []:
        L.append(f"メモ: {n}")
    if d.get("partial"):
        L.append(f"partial: true / missing: {', '.join(d.get('missing') or [])}")
        L.append("  → 本文・リターン(価格)・FAQ が無い。スペックと価格はメーカー公式サイト・プレスリリース・"
                 "他の報道で確かめる。価格が確認できないなら候補から外す。")
    L.append("")
    st = d.get("state")
    L.append(f"状態: {STATE_JA.get(st, st)}  ({st})")
    L.append(f"作り手: {d.get('creator_name') or '不明'} / 所在地: {d.get('location') or '不明'} / 国: {d.get('country') or '不明'}")
    L.append(f"カテゴリ: {d.get('category') or '不明'}")
    L.append(f"通貨: {cur or '不明'}  ← 必ず確認。USD とは限らない")
    L.append(f"目標額: {money(d.get('goal'), cur)}")
    pf = d.get("percent_funded")
    L.append(f"調達額: {money(d.get('pledged'), cur)}" + (f"  (達成率 {pf:,.1f}%)" if pf is not None else ""))
    L.append(f"支援者数: {d.get('backers') if d.get('backers') is not None else '不明'}")
    L.append(f"開始: {fmt_dt(d.get('launched_at'))}")
    dl = parse_iso(d.get("deadline"))
    left = ""
    if dl and st == "live":
        h = (dl - now_jst()).total_seconds() / 3600
        left = f"  (残り約{h / 24:.1f}日)" if h > 0 else "  (締切時刻を過ぎている)"
    L.append(f"締切: {fmt_dt(d.get('deadline'))}{left}")
    if d.get("blurb"):
        L.append(f"キャッチ: {d['blurb']}")
    if d.get("creator_websites"):
        L.append("作り手サイト: " + ", ".join(d["creator_websites"]))
    if d.get("kicktraq"):
        kt = d["kicktraq"]
        L.append("Kicktraq: " + " / ".join(f"{k}={v}" for k, v in kt.items()))

    if d.get("rewards"):
        L.append("")
        L.append(f"━━ リターン({len(d['rewards'])}件・価格は{cur}建て) ━━")
        for i, r in enumerate(d["rewards"], 1):
            lim = ""
            if r.get("limit"):
                lim = f" / 限定{r['limit']}" + (f"(残り{r['remaining']})" if r.get("remaining") is not None else "")
            avail = "" if r.get("available") in (None, True) else " / 受付終了"
            L.append(f"{i}. {r.get('title')} — {money(r.get('minimum'), cur)}{lim}{avail}"
                     f" / 支援者{r.get('backers')}" + (f" / お届け予定 {r['estimated_delivery']}" if r.get("estimated_delivery") else "")
                     + (f" / 配送: {r['shipping']}" if r.get("shipping") else ""))
            if r.get("items"):
                L.append("   含まれるもの: " + ", ".join(r["items"]))
            if r.get("description"):
                L.append("   " + r["description"].replace("\n", " ⏎ "))
    if d.get("add_ons"):
        L.append("")
        L.append(f"━━ アドオン({len(d['add_ons'])}件) ━━")
        for a in d["add_ons"]:
            L.append(f"- {money(a.get('minimum'), cur)}: {(a.get('description') or '').replace(chr(10), ' ')}")
    if d.get("story_text"):
        L.append("")
        L.append("━━ 本文(プロジェクトのストーリー) ━━")
        L.append(d["story_text"])
    if d.get("story_images"):
        L.append("")
        L.append(f"━━ 本文中の画像URL({len(d['story_images'])}件。i.kickstarter.com) ━━")
        L += d["story_images"][:12]
        if len(d["story_images"]) > 12:
            L.append(f"…ほか{len(d['story_images']) - 12}件(--json で全部)")
    if d.get("risks"):
        L.append("")
        L.append("━━ リスクと課題(作り手の記述) ━━")
        L.append(d["risks"])
    if d.get("faq"):
        L.append("")
        L.append(f"━━ FAQ({len(d['faq'])}件) ━━")
        for f in d["faq"]:
            L.append(f"Q. {f['q']}")
            L.append(f"A. {(f['a'] or '').replace(chr(10), ' ')}")
    if d.get("updates"):
        L.append("")
        L.append("━━ 作り手の最新アップデート(新しい順) ━━")
        for u in d["updates"]:
            L.append(f"- [{u.get('published', '')[:10]}] {u.get('title')}")
            if u.get("text"):
                L.append("    " + u["text"].replace("\n", " ⏎ "))
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description="Kickstarter プロジェクトの読み取り")
    ap.add_argument("url")
    ap.add_argument("--json", action="store_true", help="JSON で出力する")
    ap.add_argument("--no-cache", action="store_true", help="キャッシュを見ない")
    ap.add_argument("--runner", action="store_true", help="全文取得を飛ばし、ランナー向けの縮退取得だけ行う(再現用)")
    ap.add_argument("--write-cache", action="store_true", help="全文取得できたら data/kscache に保存する")
    a = ap.parse_args()
    try:
        d = get_project(a.url, use_cache=not a.no_cache, runner=a.runner)
    except (ValueError, RuntimeError) as e:
        print(f"取得できませんでした: {e}", file=sys.stderr)
        return 1
    if a.write_cache and d.get("source") == "home" and not d.get("partial"):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path(d["creator_slug"], d["slug"]).write_text(
            json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(json.dumps(d, ensure_ascii=False, indent=1) if a.json else render(d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
