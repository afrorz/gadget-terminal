"""日本上陸の見回り。公開済みの記事から、今日確認する分を選んで記録する。

    python scripts/followup.py pick            # 今日見る記事を選んで一覧を出す
    python scripts/followup.py pick --n 3      # 本数を変える
    python scripts/followup.py done FILE...    # 見終わった記事を記録する

この媒体は「海外で出たばかりで、まだ日本で買えない製品」を先に書く。
日本で検索されるのは上陸したとき(Makuake開始・国内発売)なので、そのとき記事が
「買えない」のままだと、先に書いた意味が無くなる。そこで毎日少しずつ過去記事を
見回り、上陸していれば front matter の japan に続報を書く(docs/PLAYBOOK.md)。

選び方:
- 公開から3日以内は見ない(公開時に調べたばかり)。180日を過ぎたものも見ない
- japan.status が「発売済み」のものは見ない(続報として完結している)
- それ以外(発売予定・予約受付中・クラファン中・未上陸)は、前回から7日空けて再訪する。
  予約受付中→発売済み、技適がデータベースに載った、といった変化を拾うため
- 一度も見ていないもの → 前回確認が古いもの、の順。同順なら新しい記事から
  (新しいほど上陸が近いことが多い)

記録は data/followup.json。{記事ファイル名: 最終確認日}。
"""

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "content" / "posts"
STATE = ROOT / "data" / "followup.json"
JST = timezone(timedelta(hours=9))

MIN_AGE_DAYS = 3
MAX_AGE_DAYS = 180
REVISIT_DAYS = 7
FINAL_STATUS = "発売済み"


def today() -> date:
    return datetime.now(JST).date()


def front_matter(path: Path) -> dict:
    # 画像URLに "---" を含む記事があるので、単純な split("---") では切らない
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", path.read_text(encoding="utf-8"), re.S)
    return yaml.safe_load(m.group(1)) if m else {}


def load_state() -> dict:
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}


def pick(n: int) -> list[tuple[Path, dict]]:
    state = load_state()
    t = today()
    cands = []
    for p in sorted(POSTS.glob("*.md")):
        fm = front_matter(p)
        try:
            d = date.fromisoformat(str(fm.get("date")))
        except ValueError:
            continue
        age = (t - d).days
        if not (MIN_AGE_DAYS <= age <= MAX_AGE_DAYS):
            continue
        if str((fm.get("japan") or {}).get("status") or "") == FINAL_STATUS:
            continue
        last = state.get(p.name)
        if last and (t - date.fromisoformat(last)).days < REVISIT_DAYS:
            continue
        # 未確認を先に、次に確認が古い順、同順なら新しい記事から
        cands.append(((last is not None, last or "", -d.toordinal()), p, fm))
    cands.sort(key=lambda x: x[0])
    return [(p, fm) for _, p, fm in cands[:n]]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("pick")
    sp.add_argument("--n", type=int, default=8)
    sd = sub.add_parser("done")
    sd.add_argument("files", nargs="+")
    a = ap.parse_args(argv)

    if a.cmd == "pick":
        rows = pick(a.n)
        if not rows:
            print("今日見る記事はありません。")
        for p, fm in rows:
            j = fm.get("japan") or {}
            now = f'{j.get("status")}({j.get("checked")}確認)' if j else "続報なし"
            print(f"- {p.relative_to(ROOT).as_posix()}")
            print(f"    製品: {fm.get('keyword') or ''} / 公開: {fm.get('date')} / 現在: {now}")
            print(f"    タイトル: {fm.get('title')}")
        return 0

    state = load_state()
    for f in a.files:
        state[Path(f).name] = today().isoformat()
    STATE.write_text(json.dumps(dict(sorted(state.items())), ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    print(f"{len(a.files)} 本を記録しました")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
