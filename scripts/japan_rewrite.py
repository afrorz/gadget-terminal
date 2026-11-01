"""過去記事の「日本で買える？使える？」の節を、期待を残す言い方に書き直す(1回きりの作業)。

    python scripts/japan_rewrite.py pick --n 20   # 今夜書き直す記事を出す(新しい記事から)
    python scripts/japan_rewrite.py check FILE... # 節の外を変えていないか・新しい数字が無いかを確かめる
    python scripts/japan_rewrite.py done FILE...  # 書き直し済みとして記録する
    python scripts/japan_rewrite.py status        # 残りの本数

なぜ(2026-11-01 本人): 記事の多くが「そのまま買って使うことはできない」「電波法違反となる」
「唯一の道」で締めていて、その製品が欲しくて来た読者の買う気を消していた。実際には GT が先に
書いた製品の何十本かが後から日本に来ている。言い方だけを変え、事実(周波数・技適の状況・価格)は変えない。

歯止め(check):
  - 節(見出しから次の ## の手前まで)の外が、git の HEAD と1文字でも違えば戻す
  - 節の中に、元のファイルのどこにも無い数字が出てきたら戻す(写し間違い・言い過ぎを止める)
  - 戻した記事は done にしないので、次の晩にもう一度選ばれる
日本上陸が確認済みの記事(上の「日本上陸」の枠が答えになっている)は対象外。
記録は data/japan_rewrite.json。{記事ファイル名: 書き直した日}。
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "content" / "posts"
STATE = ROOT / "data" / "japan_rewrite.json"
JST = timezone(timedelta(hours=9))
HEAD_RE = re.compile(r"^## 日本で買える？使える？[ \t]*$", re.M)
LANDED = ("発売済み", "予約受付中", "クラウドファンディング中")
NUM_RE = re.compile(r"\d+(?:[.,]\d+)*")

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def front_matter(text: str) -> dict:
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    return yaml.safe_load(m.group(1)) if m else {}


def split_section(text: str) -> tuple[str, str, str] | None:
    """(節の前, 節, 節の後)。節が無ければ None"""
    m = HEAD_RE.search(text)
    if not m:
        return None
    nxt = re.search(r"^## ", text[m.end():], re.M)
    end = m.end() + nxt.start() if nxt else len(text)
    return text[:m.start()], text[m.start():end], text[end:]


def load_state() -> dict:
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}


def targets() -> list[Path]:
    state = load_state()
    rows = []
    for p in POSTS.glob("*.md"):
        if p.name in state:
            continue
        text = p.read_text(encoding="utf-8")
        if not split_section(text):
            continue
        fm = front_matter(text)
        if str((fm.get("japan") or {}).get("status") or "") in LANDED:
            continue
        rows.append((str(fm.get("date") or ""), p))
    rows.sort(key=lambda x: x[0], reverse=True)  # 新しい記事から
    return [p for _, p in rows]


def head_text(path: Path) -> str | None:
    rel = path.resolve().relative_to(ROOT).as_posix()
    r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True)
    return r.stdout.decode("utf-8") if r.returncode == 0 else None


def check_one(path: Path) -> str:
    """問題があれば理由を返す。無ければ空文字"""
    old = head_text(path)
    if old is None:
        return "HEAD に無いファイル"
    new = path.read_text(encoding="utf-8")
    if old.replace("\r\n", "\n") == new.replace("\r\n", "\n"):
        return "変わっていない"
    so, sn = split_section(old.replace("\r\n", "\n")), split_section(new.replace("\r\n", "\n"))
    if not so or not sn:
        return "節の見出しが無くなった"
    if so[0] != sn[0]:
        return "節より前(front matter・本文)が変わっている"
    if so[2].strip() != sn[2].strip():
        return "節より後が変わっている"
    body = sn[1]
    if len(body.strip().splitlines()) < 3:
        return "節が短すぎる"
    extra = sorted({n for n in NUM_RE.findall(body) if n not in old})
    if extra:
        return "元の記事に無い数字: " + ", ".join(extra[:5])
    for bad in ("電波法違反となる", "唯一の安全な道", "唯一の道"):
        if bad in body:
            return f"「{bad}」が残っている"
    return ""


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("pick")
    sp.add_argument("--n", type=int, default=20)
    sc = sub.add_parser("check")
    sc.add_argument("files", nargs="+")
    sd = sub.add_parser("done")
    sd.add_argument("files", nargs="+")
    sub.add_parser("status")
    a = ap.parse_args(argv)

    if a.cmd == "pick":
        rows = targets()[:a.n]
        if not rows:
            print("書き直す記事はもうありません。")
        for p in rows:
            print(f"- {p.relative_to(ROOT).as_posix()}")
        return 0

    if a.cmd == "status":
        print(f"書き直し済み {len(load_state())}本 / 残り {len(targets())}本")
        return 0

    if a.cmd == "check":
        ok = 0
        for f in a.files:
            p = Path(f)
            why = check_one(p)
            if why:
                # 戻す。done にしないので次の晩にまた選ばれる
                subprocess.run(["git", "checkout", "--", p.resolve().relative_to(ROOT).as_posix()], cwd=ROOT)
                print(f"✗ 戻した: {p.name}({why})")
            else:
                ok += 1
                print(f"✓ {p.name}")
        print(f"通った {ok} / {len(a.files)} 本")
        return 0

    state = load_state()
    today = datetime.now(JST).date().isoformat()
    for f in a.files:
        state[Path(f).name] = today
    STATE.write_text(json.dumps(dict(sorted(state.items())), ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
    print(f"{len(a.files)} 本を記録しました(残り {len(targets())}本)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
