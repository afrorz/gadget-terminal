#!/usr/bin/env python3
"""代替品(alternatives)を探すための、楽天市場の商品検索。

    python3 scripts/rakuten_search.py "Garmin Instinct"
    python3 scripts/rakuten_search.py "Amazfit Active" --hits 20

商品名・価格・店名・商品ページURL・商品画像URLを並べて出す。中古・並行輸入・
ケースやフィルムなどの付属品は名前で落とす。どれを載せるかは自分で選び、
画像は必ず /tmp に落として Read で開き、その型番の本体かを目で確かめること。

鍵は環境変数 RAKUTEN_ACCESS_KEY(GitHub Actions のシークレット)か、
手元なら config/secrets.local.yaml の rakuten_access_key から読む。
クラウドの記事生成で鍵が読めず代替品を毎回省いていた(2026-10 前半、
10月の記事のほぼすべてに代替品が無かった)ため、両方から読めるようにした。

注意: この API は1文字だけの単語(例: "Active 2" の "2")を含む検索語を
400 で拒否する。clean_keyword() で前の単語にくっつけて "Active2" にする。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from find_rakuten_alt import ACCESSORY_WORDS, NG_WORDS, clean_keyword, search  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent

# 交換バンドや互換品も本体より上に来やすい(実測: 「Amazfit Active 2」で交換ベルトが出た)
EXTRA_NG = ("交換", "互換", "替えベルト")


def credentials() -> tuple[str, str]:
    site = yaml.safe_load((ROOT / "config" / "site.yaml").read_text(encoding="utf-8"))["site"]
    app_id = str(site.get("rakuten_app_id") or "").strip()
    key = os.environ.get("RAKUTEN_ACCESS_KEY", "").strip()
    local = ROOT / "config" / "secrets.local.yaml"
    if not key and local.exists():
        key = str((yaml.safe_load(local.read_text(encoding="utf-8")) or {}).get("rakuten_access_key") or "").strip()
    return app_id, key


def main(argv: list[str]) -> int:
    hits = 15
    if "--hits" in argv:
        i = argv.index("--hits")
        hits = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 1
    app_id, key = credentials()
    if not app_id or not key:
        print("NG 楽天の鍵がありません(RAKUTEN_ACCESS_KEY か config/secrets.local.yaml)")
        return 1
    keyword = clean_keyword(" ".join(args))
    items = search(app_id, key, keyword, hits)
    shown = 0
    for it in items:
        name = str(it.get("itemName") or "")
        if any(w in name for w in NG_WORDS + ACCESSORY_WORDS + EXTRA_NG):
            continue
        imgs = [x["imageUrl"].split("?")[0] for x in (it.get("mediumImageUrls") or [])]
        print(f"- {it.get('itemPrice'):,}円 / {it.get('shopName', '')} / レビュー{it.get('reviewCount', 0)}件\n"
              f"  {name[:110]}\n"
              f"  url:   {str(it.get('itemUrl', '')).split('?')[0]}\n"
              f"  image: {imgs[0] if imgs else '(なし)'}")
        shown += 1
    print(f"\n検索語「{keyword}」: {len(items)}件中 {shown}件を表示")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
