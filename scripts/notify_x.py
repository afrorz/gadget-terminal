"""daily-article.yml が公開した新着記事を、X 自動投稿アプリ(x-poster)の
取り込み口(ingestGadgetPosts)へ送る。

新着の判定は「ワークフロー開始時点の HEAD」から「今の HEAD」までの間に
追加された content/posts/*.md の差分で行う。記事が1本も追加されなかった回
(3本揃っていて生成をスキップした日、画像なしで記事を削除した日など)は
何もせず終わる。

X への実際の投稿失敗はここでは起きない(ここは下書きを作るだけ)。
ここでの失敗は「サイト公開は成功したのに X への連携だけ落ちた」状態を
作るので、記事公開そのものを失敗扱いにはしない(exit 0 で警告するだけ)。
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def added_post_files(base_sha: str) -> list[Path]:
    import subprocess

    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=A", base_sha, "HEAD", "--", "content/posts/*.md"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [ROOT / line for line in result.stdout.splitlines() if line.strip()]


def load_front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    _, fm, _ = text.split("---", 2)
    return yaml.safe_load(fm)


MAX_HASHTAGS = 2


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


def compose_text(hook: str, url: str, hashtags: str) -> str:
    """1通で投稿する本文。hook → 改行1つ → ハッシュタグ → 改行2つ → URL
    (Xが自動でカード展開する)。

    以前はURLをリプライ側に分けていたが、運営判断で1通にまとめる方針に変更した
    (2026-09-05)。"""
    head = f"{hook}\n{hashtags}" if hashtags else hook
    return f"{head}\n\n{url}"


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

    files = added_post_files(base_sha)
    if not files:
        print("新着記事なし。X への通知はスキップします。")
        return 0

    base_url = site_base_url()
    articles = []
    for path in files:
        fm = load_front_matter(path)
        slug = fm.get("slug")
        hook = fm.get("x_hook")
        if not slug or not hook:
            print(f"⚠ {path.name}: slug または x_hook が無いためスキップします")
            continue
        url = f"{base_url}/posts/{slug}.html"
        hashtags = build_hashtags(fm.get("tags"))
        articles.append({
            "id": path.stem,
            "text": compose_text(hook, url, hashtags),
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
