"""daily-article.yml が公開した新着記事を、X 投稿アプリ(x-poster)の
取り込み口(ingestGadgetPosts)へ送る。アプリの GT タブに「コピペで投稿できる
素材」として並び、本人が手動で X に投稿する。

新着の判定は「ワークフロー開始時点の HEAD」から「今の HEAD」までの間に
追加された content/posts/*.md の差分で行う。記事が1本も追加されなかった回
(3本揃っていて生成をスキップした日、画像なしで記事を削除した日など)は
何もせず終わる。

X への実際の投稿失敗はここでは起きない(ここは下書きを作るだけ)。
ここでの失敗は「サイト公開は成功したのに X への連携だけ落ちた」状態を
作るので、記事公開そのものを失敗扱いにはしない(exit 0 で警告するだけ)。
"""

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def changed_post_files(base_sha: str, diff_filter: str) -> list[Path]:
    import subprocess

    result = subprocess.run(
        ["git", "diff", "--name-only", f"--diff-filter={diff_filter}", base_sha, "HEAD",
         "--", "content/posts/*.md"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [ROOT / line for line in result.stdout.splitlines() if line.strip()]


def parse_front_matter(text: str) -> dict:
    # 画像URLに "---" を含む記事があるので、単純な split("---") では切らない
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    return yaml.safe_load(m.group(1)) if m else {}


def load_front_matter(path: Path) -> dict:
    return parse_front_matter(path.read_text(encoding="utf-8"))


def front_matter_at(sha: str, path: Path) -> dict:
    import subprocess

    rel = path.relative_to(ROOT).as_posix()
    r = subprocess.run(["git", "show", f"{sha}:{rel}"], cwd=ROOT, capture_output=True,
                       text=True, encoding="utf-8")
    return parse_front_matter(r.stdout) if r.returncode == 0 else {}


def japan_updates(base_sha: str) -> list[tuple[Path, dict]]:
    """この実行で「日本上陸」の続報が新しく付いた、または状況が変わった記事。

    確認日だけ更新した(状況は同じ)記事は投稿しない。同じ「予約受付中」を
    毎週流すと、読者には同じ話の繰り返しにしか見えない。
    """
    out = []
    for path in changed_post_files(base_sha, "M"):
        now = (load_front_matter(path).get("japan") or {})
        before = (front_matter_at(base_sha, path).get("japan") or {})
        if now.get("status") and now.get("status") != before.get("status"):
            out.append((path, now))
    return out


MAX_HASHTAGS = 2

JAPAN_STATUS_ID = {"発売予定": "announced", "クラウドファンディング中": "funding",
                   "予約受付中": "preorder", "発売済み": "released"}


def build_hashtags(tags) -> str:
    """記事の tags から先頭2件をハッシュタグ化する。

    スペースが入っているとハッシュタグがそこで切れてしまう(例: "Xsnap 7 Pro"
    は "#Xsnap" で終わる)ため、タグ内の空白は詰めて1トークンにする。
    """
    if not tags:
        return ""
    out = []
    for tag in tags[:MAX_HASHTAGS]:
        cleaned = "".join(str(tag).split())
        if cleaned:
            out.append(f"#{cleaned}")
    return " ".join(out)


MAX_IMAGES = 4  # X の1ポストに付けられる画像の上限


def image_urls(fm: dict) -> list[str]:
    """X に添付する候補画像。build.py と同じく images を正とし、旧 thumbnail を補う。"""
    urls = []
    for it in fm.get("images") or []:
        url = it if isinstance(it, str) else (it or {}).get("url")
        url = str(url or "").strip()
        if url and url not in urls:
            urls.append(url)
    if not urls and fm.get("thumbnail"):
        urls.append(str(fm["thumbnail"]).strip())
    return urls[:MAX_IMAGES]


def site_base_url() -> str:
    site = yaml.safe_load((ROOT / "config" / "site.yaml").read_text(encoding="utf-8"))
    return site["site"]["base_url"].rstrip("/")


# ── Threads 用の本文(2026-10-19) ──
# Threads のアカウントは「海外ガジェットの技適と日本での買い方を、確認できた事実で
# 答える」立場。X の x_hook をそのまま流さず、記事の front matter(giteki / japan /
# faq / alternatives)から決まった形で組み立てる。LLM は使わず、新しい事実も足さない。
THREADS_MAX_CHARS = 500
THREADS_LINK_LEAD = "日本から見るとどうか、国内で買える代わりの製品は記事にまとめています。"


def _one_line(text) -> str:
    return " ".join(str(text or "").split())


def _plain_ok(text: str) -> bool:
    """感嘆符と絵文字(BMP 外の文字)を含まない文だけを使う。"""
    return "！" not in text and "!" not in text and all(ord(c) <= 0xFFFF for c in text)


def first_sentence(text, limit: int) -> str:
    """最初の「。」までを1文として返す。limit を超える・使えない文は空文字。

    文の途中では切らない(読点で切ると意味が変わるため)。
    """
    t = _one_line(text)
    if not t:
        return ""
    end = t.find("。")
    sentence = t[: end + 1] if end >= 0 else t
    if len(sentence) > limit or not _plain_ok(sentence):
        return ""
    return sentence


def _md(value) -> str:
    """date / 'YYYY-MM-DD' を「M/D」にする。読めなければ空文字。"""
    if hasattr(value, "month") and hasattr(value, "day"):
        return f"{value.month}/{value.day}"
    m = re.match(r"^\d{4}-(\d{1,2})-(\d{1,2})", str(value or ""))
    return f"{int(m.group(1))}/{int(m.group(2))}" if m else ""


def threads_name(fm: dict) -> str:
    name = _one_line(fm.get("keyword"))
    if name:
        return name
    title = _one_line(fm.get("title"))
    cut = [i for i in (title.find("は"), title.find("、")) if i > 0]
    return title[: min(cut)] if cut else title


def _faq_answer(fm: dict, needles: tuple[str, ...]) -> str:
    for item in fm.get("faq") or []:
        q = str((item or {}).get("q") or "")
        if any(n in q for n in needles):
            return str((item or {}).get("a") or "")
    return ""


def giteki_line(fm: dict) -> str:
    g = fm.get("giteki")
    if not isinstance(g, dict) or not g.get("status"):
        s = first_sentence(_faq_answer(fm, ("技適",)), 80)
        return s
    status = str(g.get("status"))
    day = _md(g.get("checked"))
    when = f"（{day}時点）" if day else ""
    if status == "取得済み":
        numbers = [str(n).strip() for n in (g.get("number") or []) if str(n).strip()]
        if numbers:
            joined = "、".join(numbers)
            if g.get("found"):
                return f"公開後の再確認で、総務省のデータベースに技適番号 {joined} を確認{when}"
            return f"総務省のデータベースで技適番号 {joined} を確認{when}"
    elif status == "対象外":
        if "無線の記載なし" in str(g.get("note") or ""):
            return f"無線の記載が無く、対象外の見込み{when}"
        return f"無線を使わない製品で、技適の対象外{when}"
    elif status == "確認できない":
        return f"総務省のデータベースでは確認できていない{when}"
    return first_sentence(_faq_answer(fm, ("技適",)), 80)


def buy_line(fm: dict) -> str:
    j = fm.get("japan")
    if isinstance(j, dict) and j.get("status"):
        status = _one_line(j.get("status"))
        sentence = first_sentence(j.get("summary"), 90)
        return f"{status}。{sentence}" if sentence else status
    return first_sentence(_faq_answer(fm, ("日本で買え", "買えますか")), 90)


def clean_alternative_name(name) -> str:
    """代わりの製品名。楽天の商品名のように宣伝文句(【…】や「！」)や長い羅列が
    入っているものは使わず、空文字を返す(先頭の候補が使えなければ次の候補を見る)。"""
    t = _one_line(re.sub(r"【.*?】", " ", str(name or "")))
    if not t or len(t) > 60 or not _plain_ok(t):
        return ""
    return t


def threads_text(fm: dict, url: str = "") -> str:
    """Threads 用の本文(500字以内)。末尾は固定の誘導文。URL は呼び出し側が付ける。"""
    name = threads_name(fm)
    alt = ""
    for a in fm.get("alternatives") or []:
        alt = clean_alternative_name((a or {}).get("name") if isinstance(a, dict) else "")
        if alt:
            break

    def build(giteki: str, buy: str, alt_name: str) -> str:
        lines = [f"{name}は、日本で使える？", ""]
        if giteki:
            lines.append(f"技適：{giteki}")
        if buy:
            lines.append(f"日本で買う：{buy}")
        if alt_name:
            lines.append(f"今日買える代わり：{alt_name}")
        lines += ["", THREADS_LINK_LEAD]
        return "\n".join(lines)

    giteki = giteki_line(fm)
    buy = buy_line(fm)
    text = build(giteki, buy, alt)
    if len(text) > THREADS_MAX_CHARS and alt:
        # 代わりの製品名の補足(括弧書き)を落とす
        text = build(giteki, buy, re.sub(r"[（(].*?[）)]", "", alt).strip())
    if len(text) > THREADS_MAX_CHARS and "：" in buy.replace("。", "：", 1):
        # 日本の状況は文を落とし、状況だけにする
        status_only = buy.split("。")[0]
        text = build(giteki, status_only, alt)
    if len(text) > THREADS_MAX_CHARS:
        text = build(giteki, "", alt)
    return text


def preview(count: int) -> int:
    """送信せずに、新しい順に count 本ぶんの Threads 用本文を表示する(確認用)。"""
    base_url = site_base_url()
    files = sorted((ROOT / "content" / "posts").glob("*.md"), reverse=True)[:count]
    bad = 0
    for path in files:
        fm = load_front_matter(path)
        text = threads_text(fm, f"{base_url}/posts/{fm.get('slug')}.html")
        flags = []
        if len(text) > THREADS_MAX_CHARS:
            flags.append("500字超過")
        if "！" in text or "!" in text:
            flags.append("感嘆符あり")
        bad += bool(flags)
        print(f"===== {path.name}  ({len(text)}字) {' '.join(flags)}")
        print(text)
        print()
    print(f"{len(files)}本中、問題あり {bad}本")
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        return preview(int(sys.argv[2]) if len(sys.argv) > 2 else 8)

    base_sha = sys.argv[1] if len(sys.argv) > 1 else None
    ingest_url = sys.argv[2] if len(sys.argv) > 2 else None
    token = sys.argv[3] if len(sys.argv) > 3 else None

    if not base_sha or not ingest_url or not token:
        print("使い方: notify_x.py <base_sha> <ingest_url> <token>  /  notify_x.py --preview [本数]")
        return 0

    files = changed_post_files(base_sha, "A")
    updates = japan_updates(base_sha)
    if not files and not updates:
        print("新着記事も日本上陸の続報もなし。X への通知はスキップします。")
        return 0

    base_url = site_base_url()
    articles = []
    # 日本上陸の続報。記事と同じ素材の形で送り、アプリ側では新着と並んで出る。
    # id に状況を含めるので、「予約受付中」→「発売済み」と進めばそれぞれ1回ずつ届く。
    for path, j in updates:
        fm = load_front_matter(path)
        slug = fm.get("slug")
        # summary は記事の中で読む前提の文で、製品名が入っていない
        # (「日本ではヤンミン・ストアが…応援購入を受け付けている」だけでは
        # 何の話か分からない、と本人から指摘があった)。x_hook が無ければ
        # 製品名を必ず頭に付ける。
        hook = str(j.get("x_hook") or "").strip()
        if not hook:
            name = str(fm.get("keyword") or "").strip()
            first = str(j.get("summary") or "").split("。")[0]
            if not name or not first:
                print(f"⚠ {path.name}: x_hook も製品名も無いため続報の通知をスキップします")
                continue
            hook = f"「{name}」の日本上陸の続報。{first}。"
        if not slug:
            continue
        articles.append({
            # アプリ側は id を英数字に限っているので、状況は英語の略号にする
            "id": f"{path.stem}-jp-{JAPAN_STATUS_ID.get(j['status'], 'update')}",
            "title": f"【日本上陸・{j['status']}】{fm.get('title') or ''}",
            "hook": hook,
            "threadsText": threads_text(fm, f"{base_url}/posts/{slug}.html"),
            "hashtags": build_hashtags(fm.get("tags")),
            "url": f"{base_url}/posts/{slug}.html",
            "images": image_urls(fm),
            "ogImage": f"{base_url}/ogp/{slug}.png",
        })
    for path in files:
        fm = load_front_matter(path)
        slug = fm.get("slug")
        # 箇条書きの x_hook は YAML のブロック形式で書くので、末尾の改行を落とす
        hook = str(fm.get("x_hook") or "").strip()
        if not slug or not hook:
            print(f"⚠ {path.name}: slug または x_hook が無いためスキップします")
            continue
        # 投稿文は組み立てずに素材のまま送る。X へは本人がアプリから
        # コピペで手動投稿する(URL 付きの API 投稿は1件$0.20と割高なため、
        # 2026-09-27 に自動投稿をやめた)。
        articles.append({
            "id": path.stem,
            "title": fm.get("title") or "",
            "hook": hook,
            "threadsText": threads_text(fm, f"{base_url}/posts/{slug}.html"),
            "hashtags": build_hashtags(fm.get("tags")),
            "url": f"{base_url}/posts/{slug}.html",
            "images": image_urls(fm),
            "ogImage": f"{base_url}/ogp/{slug}.png",
        })

    if not articles:
        print("送れる記事がありませんでした。")
        return 0

    body = json.dumps({"articles": articles}).encode("utf-8")
    req = urllib.request.Request(
        ingest_url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"X 投稿の下書きを送信しました: {resp.read().decode('utf-8')}")
    except urllib.error.URLError as err:
        # サイト公開自体は成功しているので、ここで失敗させて記事の
        # コミット・公開を無かったことにはしない。
        print(f"⚠ X 投稿アプリへの送信に失敗しました(記事の公開は成功しています): {err}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
