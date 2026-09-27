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


def main() -> int:
    base_sha = sys.argv[1] if len(sys.argv) > 1 else None
    ingest_url = sys.argv[2] if len(sys.argv) > 2 else None
    token = sys.argv[3] if len(sys.argv) > 3 else None

    if not base_sha or not ingest_url or not token:
        print("使い方: notify_x.py <base_sha> <ingest_url> <token>")
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
        hook = str(j.get("x_hook") or "").strip() or str(j.get("summary") or "").split("。")[0] + "。"
        if not slug or not hook.strip("。"):
            continue
        articles.append({
            # アプリ側は id を英数字に限っているので、状況は英語の略号にする
            "id": f"{path.stem}-jp-{JAPAN_STATUS_ID.get(j['status'], 'update')}",
            "title": f"【日本上陸・{j['status']}】{fm.get('title') or ''}",
            "hook": hook,
            "hashtags": build_hashtags(fm.get("tags")),
            "url": f"{base_url}/posts/{slug}.html",
            "images": image_urls(fm),
            "ogImage": f"{base_url}/ogp/{slug}.png",
        })
    for path in files:
        fm = load_front_matter(path)
        slug = fm.get("slug")
        hook = fm.get("x_hook")
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
