#!/usr/bin/env python3
"""読まれている記事の「今すぐ買えるオススメガジェット」(alternatives)の見直し表を作る。

ガジェット好きは型落ちに目もくれないので、読まれている記事のこの欄は
3か月に1回、新しい製品に入れ替える(2026-11-07 本人)。全記事はやらない。

    python scripts/refresh_alts.py                # 上位20本の表を作る(リンクの生死も見る)
    python scripts/refresh_alts.py --top 30
    python scripts/refresh_alts.py --no-alive     # リンクを開かずに表だけ

**このスクリプトは書き換えない。** 表を data/alts-refresh/<日付>.md に書くだけ。
入れ替えは人(または Claude)が、後継機・新しい物が日本の正規品で売られているか、
記事との関係(why)が言えるかを確かめてから front matter を直す。
見る項目は「製品そのものが古くないか」(発売からの年数・後継機の有無)。記事を
出した日に選んだ物でも、製品が型落ちなら入れ替える(例: 2026年の記事に2022年の時計)。
見直した項目には、入れ替えても据え置いても `picked: YYYY-MM-DD` を付ける。
次の回は picked から80日たっていない項目を「見直し不要」にする。
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import re
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checklinks import alive  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
POPULAR = ROOT / "data" / "popular.json"
OUT_DIR = ROOT / "data" / "alts-refresh"
FRESH_DAYS = 80  # これより新しく選んだ項目は見直さない


def front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def find_post(slug: str) -> Path | None:
    hits = glob.glob(str(ROOT / "content" / "posts" / f"*-{slug}.md"))
    for h in hits:
        if str(front_matter(Path(h)).get("slug") or "") == slug:
            return Path(h)
    return Path(hits[0]) if hits else None


def main(argv: list[str]) -> int:
    top = 20
    if "--top" in argv:
        top = int(argv[argv.index("--top") + 1])
    check = "--no-alive" not in argv
    today = dt.date.today()

    pop = json.loads(POPULAR.read_text(encoding="utf-8"))
    slugs = [p["path"].removeprefix("/posts/").removesuffix(".html")
             for p in pop.get("paths", []) if p["path"].startswith("/posts/")]

    lines = [f"# オススメ欄の見直し表 {today}",
             "",
             f"元: data/popular.json(過去{pop.get('days', 30)}日、{pop.get('updated', '')} 時点)の上位{top}本。",
             f"「見直した日」は項目の picked。{FRESH_DAYS}日以内は見直し不要。判定は製品の発売年と後継機で人が下す。",
             ""]
    n_review = 0
    for rank, slug in enumerate(slugs[:top], 1):
        path = find_post(slug)
        if not path:
            lines += [f"## {rank}. {slug}", "", "記事ファイルが見つからない(特集など)", ""]
            continue
        fm = front_matter(path)
        alts = fm.get("alternatives") or []
        lines += [f"## {rank}. {fm.get('title', slug)}",
                  "",
                  f"`content/posts/{path.name}`(公開 {fm.get('date')})", ""]
        if not alts:
            lines += ["オススメ欄なし", ""]
            continue
        lines += ["| # | 製品 | 店 | 見直した日 | 経過 | リンク | 判定 |", "|---|---|---|---|---|---|---|"]
        for i, a in enumerate(alts):
            picked = str(a.get("picked") or "")
            try:
                age = (today - dt.date.fromisoformat(picked[:10])).days
            except ValueError:
                age = 9999  # 一度も見直していない
            status = "-"
            if check and a.get("url"):
                ok, msg = alive(str(a["url"]))
                status = {True: "OK", False: f"切れ({msg})", None: "不明"}[ok]
                time.sleep(1.0)
            need = age > FRESH_DAYS or status.startswith("切れ")
            n_review += need
            lines.append(f"| {i} | {a.get('name', '')} | {a.get('merchant', '')} | {picked} | "
                         f"{str(age) + '日' if picked else '未見直し'} | {status} | {'見直す' if need else '不要'} |")
        lines.append("")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{today}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\n見直す項目 {n_review}件 → {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
