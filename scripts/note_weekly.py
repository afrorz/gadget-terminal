#!/usr/bin/env python3
"""note に載せる「週のまとめ」の材料を集める。

    python scripts/note_weekly.py context              # 直近7日の記事一覧を出す(執筆の材料)
    python scripts/note_weekly.py context --date 2026-10-04
    python scripts/note_weekly.py check data/note/2026-10-04.md   # 下書きの検査

**なぜ note か。** note.com は検索に強く、この新しいドメインより Google で上に出やすい。
そこに週1本のまとめを置き、各製品からサイトの記事へ送る(2026-10-03 開始、
アカウントは https://note.com/gadgetterminal )。

**毎日の記事の転載はしない。** 同じ文章が2か所にあると、Google はどちらか一方しか
評価せず、新しいドメインのほうが負けやすい。まとめは「その週に何が出たか」を
見渡す別の読み物として書く。

note には投稿用の API が無い。下書きは data/note/<日付>.md に置き、本人が
TamakoStock の GT タブからコピーして貼り付ける。見出し画像は build.py が
public/note/<日付>.png に作る(文字とサイトの配色だけの自前の画像。製品写真は
note にアップロードする形になり、サイトの画像ルールの外に出るので使わない)。

**製品の写真は1製品1枚まで入れる**(2026-10-03 本人判断。「ガジェットがテーマなのに
写真が無いのは微妙」)。note では写真をアップロードする形になり、サイトの
「ホットリンクで引用」より一歩踏み込むので、次を守って引用の形を保つ:
サイトの記事で使っているメーカー公式・クラファンのページの写真だけ /
1製品1枚 / 直下に出典。check がこれを機械で確かめる。
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import yaml

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "content" / "posts"
NOTE_DIR = ROOT / "data" / "note"


def front_matter(text: str) -> dict:
    # 画像URLに "---" を含む記事があるので split では切らない(notify_x.py と同じ)
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def status_at(sha: str | None, f: Path) -> str | None:
    """sha の時点でのその記事の japan.status。sha が無い・記事が無かったなら None。"""
    if not sha:
        return None
    r = subprocess.run(["git", "show", f"{sha}:content/posts/{f.name}"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8")
    return ((front_matter(r.stdout).get("japan") or {}).get("status")) if r.returncode == 0 else None


IMAGE_EXT = re.compile(r"\.(jpe?g|png|gif|webp)$", re.I)


def first_image(fm: dict) -> dict | None:
    """note に入れる写真1枚と出典。build.py と同じ解決のしかた(images を正、旧 thumbnail を補う)。

    URL のパスにファイル名(.jpg 等)がある写真を優先する。note は貼り付けた本文の写真を
    自分のサーバーに取り込むが、拡張子の無い URL(Meta の lookaside.fbsbx.com/.../media/?...)
    は読み込み中のまま止まった(2026-10-03)。
    """
    cands = []
    for it in (fm.get("images") or []):
        it = {"url": it} if isinstance(it, str) else (it or {})
        url = str(it.get("url") or "").strip()
        if url:
            cands.append({"url": url, "credit": str(it.get("credit") or fm.get("credit")
                                                    or fm.get("thumbnail_credit") or "").strip()})
    if cands:
        from urllib.parse import urlparse
        return next((c for c in cands if IMAGE_EXT.search(urlparse(c["url"]).path)), cands[0])
    if fm.get("thumbnail"):
        return {"url": str(fm["thumbnail"]).strip(), "credit": str(fm.get("thumbnail_credit") or "").strip()}
    return None


def week_posts(today: date) -> list[dict]:
    """today の前日までの7日間に公開した記事と、その期間に日本上陸の状況が変わった記事。

    japan.checked は見回りのたびに更新されるので、それだけでは「今週動いた」と言えない
    (2026-10-03 の試運転で、状況の変わっていない続報が17本も拾われた)。週の始まりの
    時点の status と比べ、変わったものだけを日本上陸として扱う。
    git の履歴が要るので、Actions では checkout に fetch-depth: 0 を付けること。
    """
    start, end = today - timedelta(days=7), today - timedelta(days=1)
    r = subprocess.run(["git", "rev-list", "-1", f"--before={start}T00:00:00+09:00", "HEAD"],
                       cwd=ROOT, capture_output=True, text=True)
    start_sha = r.stdout.strip() or None
    site = yaml.safe_load((ROOT / "config" / "site.yaml").read_text(encoding="utf-8"))
    base = site["site"]["base_url"].rstrip("/")
    out = []
    for f in sorted(POSTS.glob("*.md")):
        fm = front_matter(f.read_text(encoding="utf-8"))
        d = fm.get("date")
        d = d if isinstance(d, date) else date.fromisoformat(str(d)) if d else None
        j = fm.get("japan") or {}
        jc = j.get("checked")
        jc = jc if isinstance(jc, date) else date.fromisoformat(str(jc)) if jc else None
        new = d is not None and start <= d <= end
        landed = (jc is not None and start <= jc <= end and bool(j.get("status"))
                  and j.get("status") != status_at(start_sha, f))
        if not (new or landed):
            continue
        out.append({
            "file": f.name, "new": new, "landed": landed, "date": str(d),
            "title": fm.get("title"), "keyword": fm.get("keyword"), "category": fm.get("category"),
            "kicker": fm.get("kicker"), "x_hook": fm.get("x_hook"), "image": first_image(fm),
            "url": f"{base}/posts/{fm.get('slug')}.html", "tags": fm.get("tags") or [],
            "japan": {k: j.get(k) for k in ("status", "summary") if j.get(k)} if j else None,
        })
    return out


def cmd_context(args) -> int:
    today = date.fromisoformat(args.date) if args.date else date.today()
    rows = week_posts(today)
    print(f"# {today - timedelta(days=7)} 〜 {today - timedelta(days=1)} の記事 {sum(r['new'] for r in rows)}本"
          f" / 日本上陸の続報 {sum(r['landed'] for r in rows)}本\n")
    for r in rows:
        mark = ("新着" if r["new"] else "") + ("・日本上陸" if r["landed"] else "")
        print(f"## [{mark}] {r['title']}")
        print(yaml.safe_dump({k: v for k, v in r.items() if k not in ("title", "new", "landed")},
                             allow_unicode=True, sort_keys=False, width=1000))
    return 0


# 煽り・否定の結論・円換算の混入を機械で拾う。全部を防げるわけではないが、
# 毎日の記事で実際に起きたもの(2026-09-30 の本人指摘など)は止める。
BANNED = [
    (re.compile(r"[!！](?!\[)"), "感嘆符"),  # 画像の書式 ![...] は除く
    (re.compile(r"約?[\d,]+円(相当|程度)"), "円換算らしき表記"),
    (re.compile(r"話題|衝撃|ヤバい|すごすぎ"), "煽りの語"),
]
NEGATIVE_IN_TITLE = re.compile(r"未発売|未発表|未確認|未定|買えない")


def cmd_check(args) -> int:
    p = Path(args.file)
    text = p.read_text(encoding="utf-8")
    fm = front_matter(text)
    body = text.split("\n---\n", 1)[1] if "\n---\n" in text else ""
    errors = []
    for key in ("title", "hashtags"):
        if not fm.get(key):
            errors.append(f"front matter に {key} がありません")
    title = str(fm.get("title") or "")
    if NEGATIVE_IN_TITLE.search(title):
        errors.append(f"タイトルに否定の結論があります: {title}")
    if len(body) < 1200:
        errors.append(f"本文が短すぎます({len(body)}字)。各製品の紹介が薄くなっていないか")
    for pat, label in BANNED:
        for m in pat.finditer(body):
            errors.append(f"{label}: …{body[max(0, m.start() - 15):m.end() + 15]}…")
    # 製品の写真: 「## 1.」〜「## 5.」の各節に1枚ずつ、出典つきで、記事で使っている写真だけ
    allowed = {}
    for f in POSTS.glob("*.md"):
        fm2 = front_matter(f.read_text(encoding="utf-8"))
        for it in (fm2.get("images") or []):
            it = {"url": it} if isinstance(it, str) else (it or {})
            if it.get("url"):
                allowed[str(it["url"]).strip()] = True
        if fm2.get("thumbnail"):
            allowed[str(fm2["thumbnail"]).strip()] = True
    sections = re.split(r"(?m)^## (?=\d+\.)", body)[1:]
    for sec in sections:
        name = sec.splitlines()[0][:40]
        sec = re.split(r"(?m)^## ", sec)[0]
        imgs = re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", sec)
        if len(imgs) != 1:
            errors.append(f"「{name}」の写真が {len(imgs)}枚です(1製品1枚)")
            continue
        if imgs[0] not in allowed:
            errors.append(f"「{name}」の写真が、サイトの記事で使っている写真ではありません: {imgs[0][:80]}")
        if not re.search(r"(?m)^画像[:：]\s*\S", sec):
            errors.append(f"「{name}」の写真の下に「画像: 出典」がありません")
    if not sections:
        errors.append("「## 1.」から始まる製品の節が見つかりません")

    links = re.findall(r"https://gadgetterminal\.com/posts/[\w.-]+\.html", body)
    if len(links) < 3:
        errors.append(f"サイトの記事へのリンクが {len(links)}本しかありません")
    for e in errors:
        print("NG ", e)
    print("OK  検査を通りました" if not errors else f"\n{len(errors)}件の問題があります")
    return 1 if errors else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("context"); c.add_argument("--date")
    k = sub.add_parser("check"); k.add_argument("file")
    args = ap.parse_args()
    return {"context": cmd_context, "check": cmd_check}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
