"""技適の週次の再確認。「確認できない」の記事を、総務省のデータベースで引き直す。

    python scripts/giteki_recheck.py candidates     # 候補を出す(JSON + 読みやすい要約)
    python scripts/giteki_recheck.py mark-checked   # 引いた製品の確認日(giteki.checked)を今日にする
    python scripts/giteki_recheck.py apply <記事> --number 219-259442 --model "B6 Pro"
    python scripts/giteki_recheck.py add-maker Bigme "Bigme Cloud Literacy Technology" --note "..."
    python scripts/giteki_recheck.py add-unresolved Foo --note "調べたが登録者名を特定できず"

なぜ要るか: 技適の登録は製品の発表より数週間〜数か月遅れることが多い。公開時点で
「確認できない」だった記事が、後から取得済みになる。総務省のデータベースは
メーカー名ではなく**登録者名**(例: Sennheiser の MTW5 は Sonova Consumer Hearing GmbH、
Bigme は Bigme Cloud Literacy Technology)で引くので、ブランド→登録者名の対応を
data/giteki_makers.yaml に貯めておき、対応のあるブランドだけ機械的に引く。

このスクリプトは候補を出すだけ。「その製品か」の判断(型番の突き合わせ)は人間かエージェントがする。
番号を捏造しないこと。モジュール(ESP32 など)の認証は製品の認証ではない。
"""

import argparse
import json
import re
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import giteki  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "content" / "posts"
MAKERS = ROOT / "data" / "giteki_makers.yaml"
RUN_STATE = Path(tempfile.gettempdir()) / "giteki_recheck_run.json"   # candidates → mark-checked の受け渡し
JST = timezone(timedelta(hours=9))
THROTTLE = 1.5          # DB への問い合わせの間隔(秒)
LOOKBACK_DAYS = 365     # 記事の日付の何日前までの登録を候補にするか(公開前に登録済みのこともある)
UNRESOLVED_SKIP_DAYS = 60   # 調べて特定できなかったブランドは、この日数のあいだ再調査しない
MAX_OTHER_HITS = 12     # 型番が合わない登録は、1製品あたりこの件数までしか出さない

MAKERS_HEADER = """# ブランド → 総務省DB上の登録者名(giteki.py --name で引ける名前)の対応表。
# scripts/giteki_recheck.py が読む。DB に載っている表記のまま、部分一致で引ける短さで書く
# (例: 「Bigme Cloud Literacy Technology」。末尾の Co., Ltd. は不要)。
#
# brands:
#   <記事の題名・keyword に現れるブランド名>:      # 大文字小文字は区別しない
#     registrants: [登録者名, ...]                  # 確認済みのものだけ。推測で書かない
#     aliases: [別名, ...]                          # 任意。記事側の別表記(製品シリーズ名など)
#     note: 任意のメモ(根拠・注意)
# unresolved:    調べたが登録者名を特定できなかったブランド。60日は再調査しない
#   <ブランド>: {tried: YYYY-MM-DD, note: ...}
"""


# ────────────────────────────── 記事の読み書き ──────────────────────────────
def today() -> str:
    return datetime.now(JST).strftime("%Y-%m-%d")


def read_text(path: Path) -> str:
    with open(path, encoding="utf-8", newline="") as fh:   # 改行コードを変えない
        return fh.read()


def write_text(path: Path, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def front_matter(text: str) -> dict:
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def load_posts() -> list[dict]:
    out = []
    for path in sorted(POSTS.glob("*.md")):
        text = read_text(path)
        fm = front_matter(text)
        if fm.get("draft"):
            continue
        out.append({"path": path, "slug": fm.get("slug") or path.stem, "fm": fm,
                    "date": str(fm.get("date") or "")[:10]})
    return out


def edit_giteki_block(text: str, updates: dict[str, str]) -> str:
    """front matter の giteki: ブロックだけを書き換える。

    updates は {キー: 行の値(YAMLとして書く文字列)}。既にあるキーはその行だけ置換、
    無いキーはブロックの末尾に足す。他の行・改行コード(LF/CRLF)・引用符の流儀には触らない。
    """
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(nl)
    # front matter の範囲
    if not lines or lines[0] != "---":
        raise ValueError("front matter がない")
    end = next(i for i in range(1, len(lines)) if lines[i] == "---")
    start = next((i for i in range(1, end) if re.match(r"^giteki:\s*$", lines[i])), None)
    if start is None:
        raise ValueError("giteki ブロックがない(インライン形式は未対応)")
    stop = start + 1
    while stop < end and (lines[stop].startswith((" ", "\t")) or lines[stop] == ""):
        stop += 1
    # 末尾の空行はブロックに含めない
    while stop > start + 1 and lines[stop - 1] == "":
        stop -= 1
    for key, val in updates.items():
        pat = re.compile(rf"^(\s+){re.escape(key)}:")
        idx = next((i for i in range(start + 1, stop) if pat.match(lines[i])), None)
        if idx is not None:
            lines[idx] = f"{pat.match(lines[idx]).group(1)}{key}: {val}"
        else:
            lines.insert(stop, f"  {key}: {val}")
            stop += 1
    return nl.join(lines)


def yq(s: str) -> str:
    """YAML のダブルクォート文字列にする。"""
    return json.dumps(s, ensure_ascii=False)


# ────────────────────────────── 対応表 ──────────────────────────────
def load_makers() -> dict:
    if not MAKERS.exists():
        return {"brands": {}, "unresolved": {}}
    d = yaml.safe_load(MAKERS.read_text(encoding="utf-8")) or {}
    brands = {}
    for k, v in (d.get("brands") or {}).items():
        if isinstance(v, list):
            v = {"registrants": v}
        v = dict(v or {})
        v["registrants"] = [str(x).strip() for x in (v.get("registrants") or []) if str(x).strip()]
        v["aliases"] = [str(x).strip() for x in (v.get("aliases") or []) if str(x).strip()]
        brands[str(k)] = v
    return {"brands": brands, "unresolved": d.get("unresolved") or {}}


def save_makers(d: dict) -> None:
    brands = {k: {kk: vv for kk, vv in v.items() if vv} for k, v in d["brands"].items()}
    body = yaml.safe_dump({"brands": brands, "unresolved": d["unresolved"]},
                          allow_unicode=True, sort_keys=True, default_flow_style=False, width=100)
    MAKERS.write_text(MAKERS_HEADER + "\n" + body, encoding="utf-8")


def _word_re(term: str) -> re.Pattern:
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])", re.I)


def brand_of(post: dict, makers: dict) -> tuple[str | None, str]:
    """(対応表のキー or None, 未対応のときのブランド推定)。

    1) front matter の giteki.maker  2) 対応表のキー/別名が keyword・題名に現れる
    未対応なら、題名の先頭の語を推定ブランドにする(エージェントが登録者名を探す手がかり)。
    """
    fm = post["fm"]
    g = fm.get("giteki") or {}
    keys = makers["brands"]
    maker = str(g.get("maker") or "").strip()
    if maker:
        for k in keys:
            if k.lower() == maker.lower():
                return k, k
        return None, maker
    # 題名は冒頭(「 や は・が の手前)だけ見る。本文中に競合他社名が並ぶ題名(Googlebook の
    # 「Acer・ASUS・Dell…が発売」)で、別ブランドに誤って対応づけないため。
    title_head = re.split(r"[「『、，,—]|[はがを]", str(fm.get("title") or ""), maxsplit=1)[0]
    hay = f'{fm.get("keyword") or ""} {title_head} {post["slug"]}'
    for k, v in keys.items():
        if any(_word_re(t).search(hay) for t in [k] + v["aliases"]):
            return k, k
    title = str(fm.get("title") or "")
    first = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9\-+.]*)", title)
    if first:
        return None, first.group(1)
    kw = str(fm.get("keyword") or "").split()
    return None, (kw[0] if kw else "")


def product_name(fm: dict) -> str:
    kw = str(fm.get("keyword") or "").strip()
    if kw:
        return kw
    title = str(fm.get("title") or "")
    m = re.search(r"[「『]([^」』]+)[」』]", title)
    return m.group(1) if m else re.split(r"\s+[—-]\s+", title)[0]


def model_tokens(name: str, brand: str) -> list[str]:
    """型番の手がかりになる語(数字を含む語を優先)。ブランド名そのものは除く。"""
    brand_toks = {t.lower() for t in re.split(r"[^A-Za-z0-9]+", brand) if t}
    toks = [t for t in re.split(r"[^A-Za-z0-9]+", name) if len(t) >= 2 and t.lower() not in brand_toks]
    strong = [t for t in toks if re.search(r"\d", t)]
    return strong or toks


def hit_match(hit: dict, tokens: list[str]) -> list[str]:
    """DB の型式欄に現れた手がかりの語。全部そろえば有力、一部なら参考。"""
    have = {t.lower() for t in re.split(r"[^A-Za-z0-9]+", hit["model"])}
    return [t for t in tokens if t.lower() in have]


# ────────────────────────────── candidates ──────────────────────────────
class Querier:
    """DB への問い合わせ。同じ(名前, since)は1回だけ。間隔をあける。"""

    def __init__(self):
        self.cache: dict[tuple[str, str], list[dict] | None] = {}
        self.last = 0.0
        self.calls = 0

    def search(self, name: str, since: str) -> list[dict] | None:
        key = (name.lower(), since)
        if key not in self.cache:
            wait = THROTTLE - (time.time() - self.last)
            if wait > 0:
                time.sleep(wait)
            try:
                self.cache[key] = giteki.search(name=name, since=since)
            except Exception as e:   # 一時的な失敗は、その製品を「引いた」ことにしない
                print(f"! DB の問い合わせに失敗: {name}: {e}", file=sys.stderr)
                self.cache[key] = None
            self.last = time.time()
            self.calls += 1
        return self.cache[key]


def cmd_candidates(a) -> int:
    makers = load_makers()
    posts = load_posts()
    targets = []
    for p in posts:
        g = p["fm"].get("giteki") or {}
        if g.get("status") != "確認できない" or not str(g.get("radio") or "").strip():
            continue
        targets.append(p)
    targets.sort(key=lambda p: p["date"], reverse=True)   # 新しい順

    by_brand: dict[str, list[dict]] = {}
    unmapped: dict[str, list[dict]] = {}
    for p in targets:
        key, guess = brand_of(p, makers)
        (by_brand if key else unmapped).setdefault(key or guess or "(不明)", []).append(p)

    q = Querier()
    products, queried = [], []
    for brand, ps in by_brand.items():
        regs = makers["brands"][brand]["registrants"]
        if not regs:
            for p in ps:
                unmapped.setdefault(brand, []).append(p)
            continue
        earliest = min(p["date"] for p in ps)
        since_all = (datetime.strptime(earliest, "%Y-%m-%d") - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")
        rows, failed = [], False
        for reg in regs:
            r = q.search(reg, since_all)
            if r is None:
                failed = True
            else:
                rows += r
        for p in ps:
            fm = p["fm"]
            since = (datetime.strptime(p["date"], "%Y-%m-%d") - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")
            name = product_name(fm)
            toks = model_tokens(name, brand)
            seen, hits, others = set(), [], []
            for r in rows:
                if r["date"] < since or r["number"] in seen:
                    continue
                seen.add(r["number"])
                matched = hit_match(r, toks)
                item = {"number": r["number"], "registrant": r["holder"], "model": r["model"],
                        "date": r["date"], "kind": r["kind"], "matched_tokens": matched}
                (hits if toks and len(matched) == len(toks) else others).append(item)
            partial = [o for o in others if o["matched_tokens"]]
            rest = [o for o in others if not o["matched_tokens"]]
            products.append({
                "file": f"content/posts/{p['path'].name}", "slug": p["slug"], "date": p["date"],
                "product": name, "brand": brand, "radio": fm["giteki"].get("radio"),
                "title": fm.get("title"), "tokens": toks, "queried": not failed,
                "hits": hits,                       # 型番の手がかりが全部そろった登録(有力)
                "partial_hits": partial,            # 一部だけ合う登録(参考)
                "other_hits": rest[:MAX_OTHER_HITS],
                "other_hits_total": len(rest),
            })
            if not failed:
                queried.append(p["slug"])

    # 未対応ブランド(新しい記事の順)。調べて特定できなかった直近のものは除く
    skip_before = (datetime.now(JST) - timedelta(days=UNRESOLVED_SKIP_DAYS)).strftime("%Y-%m-%d")
    unmapped_out, skipped = [], []
    for brand, ps in sorted(unmapped.items(), key=lambda kv: max(p["date"] for p in kv[1]), reverse=True):
        un = makers["unresolved"].get(brand) or makers["unresolved"].get(brand.lower()) or {}
        entry = {"brand_guess": brand,
                 "products": [{"file": f"content/posts/{p['path'].name}", "date": p["date"],
                               "product": product_name(p["fm"]), "radio": p["fm"]["giteki"].get("radio"),
                               "title": p["fm"].get("title")} for p in ps]}
        if un and str(un.get("tried") or "") >= skip_before:
            entry["unresolved"] = un
            skipped.append(entry)
        else:
            unmapped_out.append(entry)

    result = {"today": today(), "targets": len(targets), "db_calls": q.calls,
              "products": products, "unmapped": unmapped_out, "unmapped_recently_failed": skipped}
    RUN_STATE.write_text(json.dumps({"date": today(), "queried": queried}, ensure_ascii=False), encoding="utf-8")
    if a.json_out:
        write_text(Path(a.json_out), json.dumps(result, ensure_ascii=False, indent=1))
    # 標準出力: 読みやすい要約 + JSON。JSON は判断に要る分だけ(型番が合わない登録は --full のとき)
    print_summary(result, sys.stdout)
    slim = dict(result)
    if not a.full:
        slim["products"] = [{k: v for k, v in p.items() if k not in ("other_hits", "title", "tokens")}
                            for p in result["products"]]
    print("--- JSON ---")
    print(json.dumps(slim, ensure_ascii=False, indent=1))
    return 0


def print_summary(r: dict, out) -> None:
    print("\n" + "=" * 60, file=out)
    print(f"技適の再確認 {r['today']}: 対象(確認できない・無線あり) {r['targets']} 本 / DB問い合わせ {r['db_calls']} 回", file=out)
    prods = r["products"]
    with_hits = [p for p in prods if p["hits"]]
    print(f"\n[対応表あり] {len(prods)} 本 / 型番がそろった候補あり {len(with_hits)} 本", file=out)
    for p in prods:
        if not p["queried"]:
            print(f"  ? {p['product']} ({p['slug']}): 問い合わせ失敗", file=out)
            continue
        if p["hits"]:
            print(f"  * {p['product']} ({p['date']}) {p['file']}", file=out)
            for h in p["hits"]:
                print(f"      {h['number']}  {h['model'][:70]}  [{h['registrant']}] {h['date']}", file=out)
        elif p["partial_hits"]:
            print(f"  ~ {p['product']} ({p['date']}): 一部だけ合う登録 {len(p['partial_hits'])} 件", file=out)
            for h in p["partial_hits"][:3]:
                print(f"      {h['number']}  {h['model'][:70]}  [{h['registrant']}] {h['date']}", file=out)
        else:
            print(f"  - {p['product']} ({p['date']}): 登録なし(同じ登録者の他の登録 {p['other_hits_total']} 件)", file=out)
    print(f"\n[対応表なし] {len(r['unmapped'])} ブランド (新しい記事の順)", file=out)
    for u_ in r["unmapped"]:
        names = ", ".join(x["product"] for x in u_["products"][:3])
        print(f"  {u_['brand_guess']}: {len(u_['products'])} 本 ({u_['products'][0]['date']}〜) {names}", file=out)
    if r["unmapped_recently_failed"]:
        print(f"\n[登録者名を調べたが特定できず、{UNRESOLVED_SKIP_DAYS}日以内なので除外] "
              + ", ".join(x["brand_guess"] for x in r["unmapped_recently_failed"]), file=out)


# ────────────────────────────── mark-checked / apply ──────────────────────────────
def find_post(arg: str) -> Path:
    p = Path(arg)
    if p.exists():
        return p.resolve()
    for cand in (ROOT / arg, POSTS / arg, POSTS / f"{arg}.md"):
        if cand.exists():
            return cand
    hits = [x for x in POSTS.glob("*.md") if arg in x.name]
    if len(hits) == 1:
        return hits[0]
    raise SystemExit(f"記事が特定できません: {arg}")


def cmd_mark_checked(a) -> int:
    if a.slugs:
        slugs = set(a.slugs)
    elif RUN_STATE.exists():
        st = json.loads(RUN_STATE.read_text(encoding="utf-8"))
        slugs = set(st.get("queried") or [])
        if st.get("date") != today():
            print(f"! 直近の candidates は {st.get('date')} のもの(今日ではない)", file=sys.stderr)
    else:
        raise SystemExit("先に candidates を実行してください(引いた製品の記録がありません)")
    t, n = today(), 0
    for p in load_posts():
        g = p["fm"].get("giteki") or {}
        if p["slug"] not in slugs or g.get("status") != "確認できない":
            continue
        text = read_text(p["path"])
        new = edit_giteki_block(text, {"checked": t}) if str(g.get("checked")) != t else text
        if new != text:
            write_text(p["path"], new)
            n += 1
    print(f"確認日を {t} にした記事: {n} 本(対象 {len(slugs)} 本)")
    return 0


def cmd_apply(a) -> int:
    path = find_post(a.post)
    text = read_text(path)
    fm = front_matter(text)
    g = fm.get("giteki") or {}
    if g.get("status") == "取得済み" and g.get("number") and not a.force:
        raise SystemExit(f"既に取得済みです: {path.name} {g.get('number')}(上書きするなら --force)")
    nums = [n.strip() for n in a.number if n.strip()]
    if not nums or not all(re.match(r"^\d{3}-[A-Za-z0-9]{6}$", n) for n in nums):
        raise SystemExit(f"技適番号の形式が不正です(例: 219-259442): {nums}")
    t = a.date or today()
    note = a.note or f"型番{a.model}で登録({t} 再確認)"
    new = edit_giteki_block(text, {
        "status": "取得済み",
        "number": "[" + ", ".join(yq(n) for n in nums) + "]",
        "checked": t,
        "found": t,
        "note": yq(note),
    })
    write_text(path, new)
    print(f"取得済みに更新: {path.name} {nums} / {note}")
    return 0


def cmd_add_maker(a) -> int:
    d = load_makers()
    cur = d["brands"].get(a.brand) or {"registrants": [], "aliases": []}
    for r in a.registrant:
        if r not in cur["registrants"]:
            cur["registrants"].append(r)
    for al in a.alias or []:
        if al not in cur["aliases"]:
            cur["aliases"].append(al)
    if a.note:
        cur["note"] = a.note
    cur = {k: v for k, v in cur.items() if v}
    d["brands"][a.brand] = cur
    d["unresolved"].pop(a.brand, None)
    save_makers(d)
    print(f"対応表に追加: {a.brand} → {cur['registrants']}")
    return 0


def cmd_add_unresolved(a) -> int:
    d = load_makers()
    d["unresolved"][a.brand] = {"tried": today(), "note": a.note or ""}
    save_makers(d)
    print(f"未特定として記録: {a.brand}({UNRESOLVED_SKIP_DAYS}日は再調査しない)")
    return 0


def main(argv: list[str]) -> int:
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("candidates", help="確認できない記事ごとに、DB の候補を出す")
    c.add_argument("--json-out", help="完全な JSON をこのファイルにも書く")
    c.add_argument("--full", action="store_true", help="標準出力の JSON に型番が合わない登録も含める")
    c.set_defaults(fn=cmd_candidates)
    m = sub.add_parser("mark-checked", help="直近の candidates で引けた製品の giteki.checked を今日にする")
    m.add_argument("slugs", nargs="*", help="省略時は candidates が記録した引けた製品すべて")
    m.set_defaults(fn=cmd_mark_checked)
    ap_ = sub.add_parser("apply", help="見つかった登録を記事に反映(取得済み・番号・found・note)")
    ap_.add_argument("post", help="記事のファイル名・スラッグの一部・パス")
    ap_.add_argument("--number", nargs="+", required=True, help="技適番号(例: 219-259442)")
    ap_.add_argument("--model", required=True, help="DB 上の型式(note に使う)")
    ap_.add_argument("--note", help="note を自分で書く場合")
    ap_.add_argument("--date", help="確認日(省略時は今日 JST)")
    ap_.add_argument("--force", action="store_true", help="取得済みの記事でも上書きする")
    ap_.set_defaults(fn=cmd_apply)
    am = sub.add_parser("add-maker", help="data/giteki_makers.yaml に登録者名を足す")
    am.add_argument("brand")
    am.add_argument("registrant", nargs="+")
    am.add_argument("--alias", nargs="*")
    am.add_argument("--note")
    am.set_defaults(fn=cmd_add_maker)
    au = sub.add_parser("add-unresolved", help="登録者名を特定できなかったブランドを記録(60日は再調査しない)")
    au.add_argument("brand")
    au.add_argument("--note")
    au.set_defaults(fn=cmd_add_unresolved)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
