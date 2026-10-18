#!/usr/bin/env python3
"""Kickstarter の先読み。自宅PCで毎晩 02:00 に回し、data/kscache/ に貯めて push する。

    python scripts/ks_prefetch.py            # 通常(タスクスケジューラから)
    python scripts/ks_prefetch.py --no-git   # 取得だけ。pull / commit / push をしない
    python scripts/ks_prefetch.py --force    # 取得済み(6時間以内)でも取り直す
    python scripts/ks_prefetch.py --limit 5  # 全文取得の上限(既定 25)

なぜ必要か: GitHub Actions のランナーからは Kickstarter のページが 403(Cloudflare)で読めない。
自宅PCからは読める。夜のうちに読んでおき、リポジトリ経由でランナーへ渡す。
記事生成側は scripts/ks_fetch.py がこのキャッシュを読む。

対象(優先順):
  1. data/queue.md の「未処理」にある Kickstarter URL
  2. 最新のダイジェスト(data/digest/*.json と .md)に出てくる Kickstarter URL
  3. すでにキャッシュにあり、まだ募集中のもの。全文取得が 48 時間より古くなったら取り直す。
     それ以外は stats.json で数値だけ更新する(軽い)
  4. Kickstarter 自身の Technology カテゴリの一覧(discover)の上位 15 件(募集中のみ)

ログ: logs/ks_prefetch.log(gitignore)。部分的に失敗しても終了コードは 0。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import ks_fetch as K  # noqa: E402

LOG = ROOT / "logs" / "ks_prefetch.log"
QUEUE = ROOT / "data" / "queue.md"
DIGEST_DIR = ROOT / "data" / "digest"
MAX_FULL = 25
DISCOVER_TAKE = 15
FRESH_H = 6          # この時間以内に全文取得済みなら、再実行しても取り直さない
REFETCH_H = 48       # 募集中のキャッシュがこれより古くなったら全文を取り直す
KEEP_DAYS = 30       # 締切後、これを過ぎたキャッシュは消す
SKIP_CATEGORIES = {"Software", "Web", "Apps"}  # ガジェット媒体の対象外
EMAIL = "306337156+afrorz@users.noreply.github.com"
ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001


def log(msg: str) -> None:
    line = f"{K.now_jst().strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass
    print(line, flush=True)


def keep_awake(on: bool) -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(
            (ES_CONTINUOUS | ES_SYSTEM_REQUIRED) if on else ES_CONTINUOUS)
    except Exception as e:  # noqa: BLE001
        log(f"スリープ抑止の切り替えに失敗: {e}")


def find_git() -> str | None:
    g = shutil.which("git")
    if g:
        return g
    for p in (r"C:\Program Files\Git\cmd\git.exe", r"C:\Program Files\Git\bin\git.exe",
              r"C:\Program Files (x86)\Git\cmd\git.exe"):
        if Path(p).exists():
            return p
    return None


def git(*args, check=False) -> tuple[int, str]:
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    kw = {"creationflags": 0x08000000} if sys.platform == "win32" else {}
    p = subprocess.run([GIT, *args], cwd=ROOT, capture_output=True, env=env, timeout=300, **kw)
    out = (p.stdout + p.stderr).decode("utf-8", errors="replace").strip()
    return p.returncode, out


# ----------------------------------------------------------------- 対象の収集
def keyof(creator, slug):
    return (creator.lower(), slug.lower())


def urls_in(text: str):
    for m in K.KS_URL.finditer(text):
        yield m.group(1), m.group(2)


def from_queue() -> list[tuple[str, str]]:
    if not QUEUE.exists():
        return []
    text = QUEUE.read_text(encoding="utf-8")
    m = re.search(r"^## 未処理\s*$(.*?)(?=^## |\Z)", text, re.S | re.M)
    return list(urls_in(m.group(1))) if m else []


def from_digest() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    files = sorted(DIGEST_DIR.glob("*.json"))[-1:] + sorted(DIGEST_DIR.glob("*.md"))[-1:]
    for f in files:
        try:
            out += list(urls_in(f.read_text(encoding="utf-8")))
        except OSError:
            pass
    return out


def from_discover(http: K.Http) -> list[tuple[str, str]]:
    """Kickstarter の Technology(category_id=16)。募集中のガジェット系だけ上位から取る。"""
    out: list[tuple[str, str]] = []
    seen = set()
    for sort, page in (("magic", 1), ("newest", 1), ("magic", 2)):
        if len(out) >= DISCOVER_TAKE:
            break
        url = f"https://www.kickstarter.com/discover/advanced.json?category_id=16&sort={sort}&page={page}"
        status, text = K.get_retry(http, url, headers={"Accept": "application/json",
                                                       "X-Requested-With": "XMLHttpRequest"}, retries=1)
        if status != 200:
            log(f"discover 取得失敗 sort={sort} page={page} status={status}")
            continue
        try:
            projects = json.loads(text).get("projects") or []
        except ValueError:
            log(f"discover の応答がJSONでない sort={sort} page={page}")
            continue
        n0 = len(out)
        for p in projects:
            if p.get("state") != "live" or (p.get("category") or {}).get("name") in SKIP_CATEGORIES:
                continue
            web = ((p.get("urls") or {}).get("web") or {}).get("project", "")
            m = K.KS_URL.search(web)
            if not m:
                continue
            k = keyof(m.group(1), m.group(2))
            if k in seen:
                continue
            seen.add(k)
            out.append((m.group(1), m.group(2)))
            if len(out) >= DISCOVER_TAKE:
                break
        log(f"discover sort={sort} page={page}: 取得{len(projects)}件 / 採用+{len(out) - n0}")
    return out


def cached_live() -> dict[tuple[str, str], dict]:
    """キャッシュ済みで締切が未来のもの。"""
    res = {}
    for f in K.CACHE_DIR.glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        dl = K.parse_iso(d.get("deadline"))
        if dl and dl > K.now_jst() and d.get("creator_slug") and d.get("slug"):
            res[keyof(d["creator_slug"], d["slug"])] = d
    return res


# ----------------------------------------------------------------- 保存・掃除
def save(d: dict) -> None:
    K.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    K.cache_path(d["creator_slug"], d["slug"]).write_text(
        json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def cleanup() -> int:
    n = 0
    for f in K.CACHE_DIR.glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            age_h = K.cache_age_h(d)
            dl = K.parse_iso(d.get("deadline"))
            old = age_h is not None and age_h > KEEP_DAYS * 24
            gone = dl is not None and dl < K.now_jst()
        except (OSError, ValueError):
            old = (time.time() - f.stat().st_mtime) > KEEP_DAYS * 86400
            gone = True
        if old and gone:
            f.unlink()
            n += 1
    return n


# ----------------------------------------------------------------- git
def git_sync_start() -> None:
    rc, out = git("pull", "--rebase", "--autostash")
    log(f"git pull --rebase: rc={rc} {out.splitlines()[-1] if out else ''}")


def git_publish() -> None:
    rc, em = git("config", "--local", "user.email")
    if em.strip() != EMAIL:
        log(f"中止: リポジトリのgit user.email が想定と違う({em.strip()!r})。commit/push しない")
        return
    git("add", "-A", "data/kscache")
    rc, _ = git("diff", "--cached", "--quiet", "--", "data/kscache")
    if rc == 0:
        log("キャッシュに変更なし。commit しない")
        return
    msg = f"Kickstarter先読み {K.now_jst().strftime('%Y-%m-%d')}"
    rc, out = git("commit", "-m", msg, "--", "data/kscache")
    log(f"git commit: rc={rc} {out.splitlines()[0] if out else ''}")
    if rc != 0:
        return
    for attempt in (1, 2):
        rc, out = git("push")
        log(f"git push (試行{attempt}): rc={rc} {out.splitlines()[-1] if out else ''}")
        if rc == 0:
            return
        rc2, out2 = git("pull", "--rebase", "--autostash")
        log(f"git pull --rebase: rc={rc2} {out2.splitlines()[-1] if out2 else ''}")
        if rc2 != 0:
            return
    log("push に失敗した(次回の実行で一緒に送られる)")


# ----------------------------------------------------------------- 本体
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-git", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--limit", type=int, default=MAX_FULL)
    a = ap.parse_args()

    log(f"=== 開始 (python {sys.version.split()[0]}, repo {ROOT}) ===")
    keep_awake(True)
    http = K.Http()
    stats = {"full_ok": 0, "full_ng": 0, "numbers": 0, "skipped_fresh": 0, "deleted": 0}
    try:
        global GIT
        GIT = find_git()
        if not a.no_git:
            if GIT:
                git_sync_start()
            else:
                log("git が見つからない。pull/commit/push は行わない")
                a.no_git = True

        live = cached_live()
        order: list[tuple[str, str, str]] = []  # (creator, slug, 由来)
        seen = set()

        def add(items, why):
            n = 0
            for c, s in items:
                k = keyof(c, s)
                if k not in seen:
                    seen.add(k)
                    order.append((c, s, why))
                    n += 1
            log(f"対象 {why}: +{n}件")

        add(from_queue(), "queue")
        add(from_digest(), "digest")
        stale = [(d["creator_slug"], d["slug"]) for k, d in live.items()
                 if (K.cache_age_h(d) or 1e9) > REFETCH_H]
        add(stale, "キャッシュ(取り直し)")
        add(from_discover(http), "discover")

        todo = order[: a.limit]
        if len(order) > a.limit:
            log(f"上限{a.limit}件のため {len(order) - a.limit} 件は今夜は見送り")

        blocked_run = 0
        for c, s, why in todo:
            c0 = K.load_cache(c, s)
            if c0 and not a.force and (K.cache_age_h(c0) or 1e9) < FRESH_H:
                stats["skipped_fresh"] += 1
                log(f"skip(取得済み) {c}/{s}")
                continue
            try:
                d = K.fetch_full(c, s, http)
            except RuntimeError as e:
                stats["full_ng"] += 1
                log(f"NG [{why}] {c}/{s}: {e}")
                blocked_run = blocked_run + 1 if str(e).startswith("blocked") else 0
                if blocked_run >= 3:
                    log("連続でブロックされた。Cloudflare に止められた可能性があるので今夜は打ち切る")
                    break
                continue
            blocked_run = 0
            if d["state"] != "live" and not d.get("rewards"):
                log(f"注意 {c}/{s}: state={d['state']} リターンなし")
            save(d)
            stats["full_ok"] += 1
            log(f"OK [{why}] {c}/{s}: {d['name'][:40]!r} state={d['state']} rewards={len(d['rewards'])} "
                f"story={len(d.get('story_text') or '')}字 faq={len(d.get('faq') or [])}"
                + (f" partial={d['missing']}" if d["partial"] else ""))

        # 全文を取らなかった募集中のキャッシュは数値だけ更新する
        done = {keyof(c, s) for c, s, _ in todo}
        for k, d in live.items():
            if k in done:
                continue
            st = K.fetch_stats(http, d["url"])
            if st:
                K.apply_stats(d, st)
                save(d)
                stats["numbers"] += 1
            else:
                log(f"数値更新に失敗 {k[0]}/{k[1]}")

        stats["deleted"] = cleanup()
        size = sum(f.stat().st_size for f in K.CACHE_DIR.glob("*.json")) if K.CACHE_DIR.exists() else 0
        log(f"結果: 全文OK={stats['full_ok']} NG={stats['full_ng']} 取得済みskip={stats['skipped_fresh']} "
            f"数値のみ更新={stats['numbers']} 削除={stats['deleted']} / キャッシュ合計 "
            f"{len(list(K.CACHE_DIR.glob('*.json')))}件 {size // 1024}KB")

        if not a.no_git:
            git_publish()
    except Exception as e:  # noqa: BLE001  タスクとしては落とさない
        import traceback
        log("予期しないエラー: " + traceback.format_exc().replace("\n", " | "))
    finally:
        http.close()
        keep_awake(False)
        log("=== 終了 ===")
    return 0


GIT: str | None = None

if __name__ == "__main__":
    sys.exit(main())
