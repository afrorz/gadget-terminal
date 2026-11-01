"""クラファン記事に、公開後に出た YouTube の実機動画を足す(2026-11-01 本人の提案)。

    python scripts/cf_videos.py pick --n 6                    # 今日見るクラファン記事
    python scripts/cf_videos.py add FILE --id VIDEO_ID --note "何が分かる動画か"
    python scripts/cf_videos.py done FILE...                  # 見終わった記事を記録(足さなかった記事も)

なぜ: Kickstarter などは出資から出荷まで数か月〜1年かかり、その間に YouTube で実機の
レビュー・開封・出資者への到着報告が出る。記事は公開時点の情報(キャンペーンの宣伝動画)のままなので、
「本当に届くのか」「実物はどうか」を知りたい読者に、後から出た動画を見せる。

歯止め(add がすべて機械で確かめる。Claude は動画 ID と日本語の一言だけを渡す):
  - 動画が実在するか、題名とチャンネル名は YouTube の oEmbed から取る(書き写しの誤りや捏造を防ぐ)
  - 公開日は動画のページの uploadDate から取り、記事の公開日の 60 日より前なら足さない(前の版の製品のことが多い)
  - 記事の embeds・videos_after に同じ動画があれば足さない。1記事 4 本まで
足すと front matter の末尾に videos_after を書き、modified を今日にする(本文は触らない)。
記録は data/cf_videos.json。{記事ファイル名: 最終確認日}。
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "content" / "posts"
STATE = ROOT / "data" / "cf_videos.json"
JST = timezone(timedelta(hours=9))
CF_DOMAINS = ("kickstarter.com", "indiegogo.com", "crowdsupply.com", "backerkit.com", "gamefound.com")
MIN_AGE_DAYS = 14
MAX_AGE_DAYS = 365
REVISIT_DAYS = 14
MAX_VIDEOS = 4
# 記事より少し前に出たレビューも、記事に入っていなければ役に立つ。ただし古すぎるものは前の版の製品のことが多い
OLDEST_BEFORE_DAYS = 60
ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
UA = "Mozilla/5.0 (compatible; GadgetTerminal-cf-videos/1.0; +https://gadgetterminal.com)"

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def today() -> date:
    return datetime.now(JST).date()


def split_fm(text: str) -> tuple[str, str] | None:
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    return (m.group(1), text[m.end():]) if m else None


def is_cf(fm: dict) -> bool:
    urls = " ".join(str(s.get("url", "")) for s in (fm.get("sources") or []) if isinstance(s, dict))
    return any(d in urls for d in CF_DOMAINS)


def load_state() -> dict:
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}


def pick(n: int) -> list[tuple[Path, dict]]:
    state, t, rows = load_state(), today(), []
    for p in POSTS.glob("*.md"):
        sp = split_fm(p.read_text(encoding="utf-8"))
        if not sp:
            continue
        fm = yaml.safe_load(sp[0]) or {}
        if not is_cf(fm):
            continue
        try:
            d = date.fromisoformat(str(fm.get("date")))
        except ValueError:
            continue
        if not (MIN_AGE_DAYS <= (t - d).days <= MAX_AGE_DAYS):
            continue
        if len(fm.get("videos_after") or []) >= MAX_VIDEOS:
            continue
        last = state.get(p.name)
        if last and (t - date.fromisoformat(last)).days < REVISIT_DAYS:
            continue
        rows.append(((last is not None, last or "", -d.toordinal()), p, fm))
    rows.sort(key=lambda x: x[0])
    return [(p, fm) for _, p, fm in rows[:n]]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "replace")


def video_info_api(vid: str, key: str) -> dict:
    """YouTube Data API(videos.list、1回1ユニット)。無い・非公開なら例外"""
    url = ("https://www.googleapis.com/youtube/v3/videos?part=snippet&id="
           + urllib.parse.quote(vid) + "&key=" + urllib.parse.quote(key))
    items = json.loads(fetch(url)).get("items") or []
    if not items:
        raise ValueError("動画が見つからない(削除・非公開)")
    sn = items[0]["snippet"]
    return {"title": sn["title"], "channel": sn["channelTitle"], "published": sn["publishedAt"][:10]}


def video_info(vid: str) -> dict:
    """題名・チャンネル・公開日。取れなければ例外

    GitHub Actions の実行サーバーから動画ページを読むと、YouTube がロボット確認の
    ページを返して公開日が読めない(2026-11-02 の初回の定時実行で全滅)。環境変数
    YOUTUBE_API_KEY があれば公式 API で取る。無ければ(手元のパソコン)従来どおり
    oEmbed で題名・チャンネル、動画のページで公開日。"""
    key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if key:
        return video_info_api(vid, key)
    watch = f"https://www.youtube.com/watch?v={vid}"
    o = json.loads(fetch("https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(watch, safe="")))
    page = fetch(watch)
    m = re.search(r'"uploadDate":"(\d{4}-\d{2}-\d{2})', page) or \
        re.search(r'itemprop="(?:uploadDate|datePublished)" content="(\d{4}-\d{2}-\d{2})', page)
    if not m:
        raise ValueError("公開日が読めない")
    return {"title": o["title"], "channel": o["author_name"], "published": m.group(1)}


def q(s: str) -> str:
    return json.dumps(str(s), ensure_ascii=False)  # YAML でも読めるダブルクォート文字列


def add(path: Path, vid: str, note: str) -> str:
    """足せたら空文字、だめなら理由"""
    if not ID_RE.match(vid):
        return "動画 ID の形が違う(11文字)"
    note = note.strip()
    if not note or len(note) > 80:
        return "note は1〜80文字の日本語で"
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    sp = split_fm(text)
    if not sp:
        return "front matter が無い"
    fm_text, body = sp
    fm = yaml.safe_load(fm_text) or {}
    have = {str(e.get("id")) for e in (fm.get("embeds") or []) if e.get("type") == "youtube"}
    have |= {str(e.get("id")) for e in (fm.get("videos_after") or [])}
    if vid in have:
        return "この記事にもう入っている動画"
    if len(fm.get("videos_after") or []) >= MAX_VIDEOS:
        return f"1記事 {MAX_VIDEOS} 本まで"
    try:
        info = video_info(vid)
    except Exception as e:  # noqa: BLE001
        return f"YouTube で確かめられない({e})"
    oldest = (date.fromisoformat(str(fm.get("date"))) - timedelta(days=OLDEST_BEFORE_DAYS)).isoformat()
    if info["published"] < oldest:
        return f"古すぎる動画({info['published']})。記事の公開日 {fm.get('date')} の {OLDEST_BEFORE_DAYS} 日前より前は、別の版の製品のことが多い"

    item = (f"  - id: {vid}\n    title: {q(info['title'])}\n    channel: {q(info['channel'])}\n"
            f"    published: {info['published']}\n    added: {today().isoformat()}\n    note: {q(note)}")
    lines = fm_text.split("\n")
    # modified を今日に(あれば置き換え、無ければ videos_after の前に足す)
    lines = [ln for ln in lines if not ln.startswith("modified:")]
    mod = f"modified: {today().isoformat()}"
    if any(ln.startswith("videos_after:") for ln in lines):
        # videos_after は常に front matter の最後に置いているので、末尾に足せばよい
        i = next(i for i, ln in enumerate(lines) if ln.startswith("videos_after:"))
        lines.insert(i, mod)
        lines.append(item)
    else:
        lines += [mod, "videos_after:", item]
    new_fm = "\n".join(lines)
    check = yaml.safe_load(new_fm)
    if [e["id"] for e in check.get("videos_after") or []][-1] != vid:
        return "front matter を正しく書けなかった"
    path.write_text(f"---\n{new_fm}\n---\n{body}", encoding="utf-8", newline="\n")
    return ""


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("pick")
    sp.add_argument("--n", type=int, default=6)
    sa = sub.add_parser("add")
    sa.add_argument("file")
    sa.add_argument("--id", required=True)
    sa.add_argument("--note", required=True)
    sd = sub.add_parser("done")
    sd.add_argument("files", nargs="+")
    a = ap.parse_args(argv)

    if a.cmd == "pick":
        rows = pick(a.n)
        if not rows:
            print("今日見る記事はありません。")
        for p, fm in rows:
            urls = [str(s.get("url")) for s in (fm.get("sources") or [])
                    if isinstance(s, dict) and any(d in str(s.get("url")) for d in CF_DOMAINS)]
            got = [str(e.get("id")) for e in (fm.get("embeds") or []) if e.get("type") == "youtube"]
            got += [str(e.get("id")) for e in (fm.get("videos_after") or [])]
            print(f"- {p.relative_to(ROOT).as_posix()}")
            print(f"    製品: {fm.get('keyword') or ''} / 公開: {fm.get('date')} / 入っている動画: {', '.join(got) or 'なし'}")
            print(f"    クラファン: {urls[0] if urls else ''}")
            print(f"    タイトル: {fm.get('title')}")
        return 0

    if a.cmd == "add":
        why = add(Path(a.file), a.id.strip(), a.note)
        print(f"✗ 足さなかった: {a.id}({why})" if why else f"✓ 足した: {a.id} → {Path(a.file).name}")
        return 1 if why else 0

    state = load_state()
    for f in a.files:
        state[Path(f).name] = today().isoformat()
    STATE.write_text(json.dumps(dict(sorted(state.items())), ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    print(f"{len(a.files)} 本を記録しました")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
