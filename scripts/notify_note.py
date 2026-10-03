"""note の週まとめの下書き(data/note/<日付>.md)を TamakoStock へ送る。

    python scripts/notify_note.py data/note/2026-10-04.md <ingest_url> <token>

weekly-note.yml が下書きを push したあとに呼ぶ。TamakoStock の GT タブに
「note 週まとめ」として並び、本人がコピーして note に貼って公開する。

本文は Markdown と HTML の両方を送る。note の編集画面は HTML を貼ると
見出し・太字・リンクを引き継ぐので、手直しが少なくて済む。

送信に失敗しても下書き自体は GitHub に残っているので、exit 0 で警告だけ出す
(notify_x.py と同じ考え方)。
"""

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    if len(sys.argv) < 4:
        print("使い方: notify_note.py <下書き.md> <ingest_url> <token>")
        return 0
    path, url, token = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", text, re.S)
    if not m:
        print(f"⚠ {path.name}: front matter が読めません")
        return 0
    fm = yaml.safe_load(m.group(1)) or {}
    body = m.group(2).strip()
    site = yaml.safe_load((ROOT / "config" / "site.yaml").read_text(encoding="utf-8"))
    base = site["site"]["base_url"].rstrip("/")
    payload = {
        "id": path.stem,
        "title": fm.get("title") or "",
        "label": fm.get("label") or "",
        "hashtags": [str(h).lstrip("#") for h in (fm.get("hashtags") or [])],
        "markdown": body,
        "html": markdown.markdown(body, extensions=["sane_lists"]),
        # 製品の写真(1製品1枚)。note に本文を貼って写真が落ちたとき、GT タブから
        # 保存して差し込めるように、節の見出し・出典と組で送る。
        "images": [{"section": s, "url": u, "credit": c} for s, u, c in re.findall(
            r"(?m)^## (\d+\.[^\n]*)\n+!\[[^\]]*\]\(([^)\s]+)\)\n画像[:：]\s*([^\n]+)", body)],
        # build.py が public/note/<日付>.png に作る見出し画像
        "headerImage": f"{base}/note/{path.stem}.png",
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"note の下書きを送りました: {r.read().decode('utf-8')}")
    except urllib.error.URLError as e:
        print(f"⚠ TamakoStock への送信に失敗しました(下書きは data/note/ に残っています): {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
