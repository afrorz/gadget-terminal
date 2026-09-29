#!/usr/bin/env python3
"""
japan_launch.py — 海外メーカーのガジェットが「日本で発売された」知らせを拾う。

この媒体の本線は「海外で出て、まだ日本語記事が無い製品」だが、そういう製品を
日本語で検索する人は少ない。検索が増えるのは日本で発売されたときなので、
その瞬間の知らせも候補に入れる（2026-09-29 本人の判断）。

ソースは PR TIMES。海外メーカーの日本法人・国内代理店は発売の告知をここに
出すことが多い。robots.txt で RSS もサイトマップも禁止されていない（2026-09-29 確認）。

  sitemap-news.xml  全リリースが載るが、直近16時間ぶんしかない
  index.rdf         説明文付きだが、全体の一部(約200件)しか載らない

朝1回だと前日の午前(リリースがいちばん多い時間帯)を取りこぼすので、夕方にも
japan-launch.yml が回り、拾ったものを data/japan_launch.json に貯めておく。
翌朝の collect.py がそこから未出のものをダイジェストに載せる。

拾うのは次の3つをすべて満たすものだけ:
  1. 題名に発売の語がある（日本上陸・国内発売・販売開始・Makuake 等）
  2. ガジェットの語がある（crowdfunding.looks_tech と同じ網）
  3. 題名に英字の製品名・ブランド名がある（国内メーカーの定番品を落とす粗い網）
セール・クーポン・キャンペーンの告知は落とす。最終的な採否は記事生成側が判断する。

collect.py から呼ばれる。単体でも動く:
    python scripts/japan_launch.py
"""
from __future__ import annotations

import html
import json
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from crowdfunding import looks_tech
except Exception:  # 単体実行でも動くように
    def looks_tech(text: str) -> bool:
        return True

FEED = "https://prtimes.jp/index.rdf"
NEWS_SITEMAP = "https://prtimes.jp/sitemap-news.xml"
POOL = Path(__file__).resolve().parent.parent / "data" / "japan_launch.json"
KEEP_DAYS = 4
UA = "GadgetTerminalBot/1.0 (+https://gadgetterminal.com; contact: info@gadgetterminal.com)"

LAUNCH = re.compile(r"日本上陸|日本初|日本発売|日本市場|国内発売|国内正規|国内販売|国内初|"
                    r"日本国内|販売開始|発売開始|新発売|先行販売|予約開始|予約受付|"
                    r"Makuake|マクアケ|CAMPFIRE|GREEN FUNDING|応援購入")
# 値引きの告知は製品のニュースではない。PLAYBOOK「狙わない」の表と同じ扱い。
NOISE = re.compile(r"セール|OFF|オフ|割引|クーポン|キャンペーン|ポイント|プレゼント|"
                   r"半額|値下げ|最安|特価|記念価格|お得|期間限定")
LATIN = re.compile(r"[A-Za-z]{2,}")

_ITEM = re.compile(r"<item\b.*?</item>", re.S)


def _tag(block: str, name: str) -> str:
    m = re.search(rf"<{name}>(.*?)</{name}>", block, re.S)
    if not m:
        return ""
    return html.unescape(re.sub(r"<!\[CDATA\[|\]\]>", "", m.group(1))).strip()


def _fetch(url: str, timeout: int) -> str:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"  ! PR TIMES を取得できませんでした: {url} {type(e).__name__} {e}", file=sys.stderr)
        return ""


def _iso(date: str) -> str:
    try:
        return datetime.fromisoformat(date).astimezone(timezone.utc).isoformat()
    except ValueError:
        return datetime.now(timezone.utc).isoformat()


def _keep(title: str, desc: str = "") -> bool:
    if not LAUNCH.search(title) or NOISE.search(title):
        return False
    return bool(LATIN.search(title)) and looks_tech(f"{title} {desc}")


def _item(title: str, url: str, desc: str, date: str) -> dict:
    desc = " ".join(desc.split())  # 改行が入るとダイジェストの箇条書きが崩れる
    return {"title": title, "url": url, "summary": desc[:300], "published": _iso(date),
            "source": "PR TIMES", "source_id": "prtimes", "kind": "japan_launch"}


def fetch(timeout: int = 30) -> list[dict]:
    """条件に合うリリースを返す。取れなければ空リスト（収集全体は止めない）。"""
    found: dict[str, dict] = {}
    text = _fetch(FEED, timeout)
    for block in _ITEM.findall(text):
        title, url = _tag(block, "title"), _tag(block, "link")
        desc = re.sub(r"<[^>]+>", "", _tag(block, "description"))
        if title and url and _keep(title, desc):
            found[url] = _item(title, url, desc, _tag(block, "dc:date"))
    text = _fetch(NEWS_SITEMAP, timeout)
    for block in re.findall(r"<url>.*?</url>", text, re.S):
        title, url = _tag(block, "news:title"), _tag(block, "loc")
        if title and url and url not in found and _keep(title):
            found[url] = _item(title, url, "", _tag(block, "news:publication_date"))
    return sorted(found.values(), key=lambda x: x["published"], reverse=True)


def update_pool() -> list[dict]:
    """新しく拾ったものを data/japan_launch.json に足し、古いものを捨てて全件返す。"""
    pool = json.loads(POOL.read_text(encoding="utf-8")) if POOL.exists() else []
    by_url = {x["url"]: x for x in pool}
    for it in fetch():
        by_url.setdefault(it["url"], it)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=KEEP_DAYS)).isoformat()
    items = sorted((x for x in by_url.values() if x["published"] >= cutoff),
                   key=lambda x: x["published"], reverse=True)
    POOL.parent.mkdir(parents=True, exist_ok=True)
    POOL.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    return items


if __name__ == "__main__":
    items = update_pool() if "--save" in sys.argv else fetch()
    print(f"{len(items)}件")
    for it in items:
        print(f"- {it['published'][:10]} {it['title']}\n  {it['url']}")
