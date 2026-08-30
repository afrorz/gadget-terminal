#!/usr/bin/env python3
"""代替品リンクが実際に収益になる形で書かれているかを確かめる。

    python scripts/checklinks.py                        # 全記事（棚卸し用）
    python scripts/checklinks.py content/posts/2026-08-29-*.md   # 公開前の門番
    python scripts/checklinks.py --check-alive           # リンクの生存も見る（遅い）

**この検査が存在する理由。** 2026-08-16〜28 の46記事で、代替品リンク20本すべてが
merchant: amazon で書かれていた。もしもアフィリエイトで提携できているのは楽天だけで、
moshimo_amazon は空。build.py はテンプレートが空なら黙って素のURLを返す仕様なので、
12日間ひとつも報酬が発生しないまま、どこにも警告が出なかった。
記事は正しく積み上がっているのに収益だけがゼロ、という壊れ方は目で気づけない。
だから機械が毎回見る。

画像（checkimages.py）が「読者に届くか」の門番なのに対し、これは
「書いた労力が収益につながる形になっているか」の門番。
"""
from __future__ import annotations

import glob
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import yaml

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# build.py の MERCHANT_HOSTS と同じ対応表。片方だけ直すと検査をすり抜けるので、
# 変更するときは必ず両方あわせる。
MERCHANT_HOSTS = {
    "amazon": ("amazon.co.jp",),
    "rakuten": ("rakuten.co.jp",),
    "yahoo": ("yahoo.co.jp", "paypaymall.yahoo.co.jp"),
}

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def live_merchants(aff: dict) -> set[str]:
    """いま実際に報酬が発生する merchant。テンプレートが入っているものだけ。"""
    out = set()
    for m in MERCHANT_HOSTS:
        t = str(aff.get(f"moshimo_{m}") or "").strip()
        if t and "{url}" in t:
            out.add(m)
    return out


def alive(url: str) -> tuple[bool | None, str]:
    """商品ページが生きているか。判定できないときは None を返す。

    Amazon と楽天はボット避けで 403 / 503 を返すことがある。これを NG に
    すると門番が誤爆して公開が止まるので、確認できない場合は素通しにする。
    """
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read(120_000).decode("utf-8", "ignore")
            code = r.status
    except urllib.error.HTTPError as e:
        if e.code in (403, 429, 503):
            return None, f"確認できず (HTTP {e.code}・ボット避け)"
        return False, f"HTTP {e.code}"
    except Exception as e:
        return None, f"確認できず ({type(e).__name__})"
    # 楽天は終了した商品でも 200 を返し、本文で知らせる。
    for ng in ("この商品は現在ご購入いただけません", "販売期間が終了",
               "ページが見つかりません", "現在お取り扱いできません"):
        if ng in body:
            return False, f"商品が終了している（{ng}）"
    return True, f"HTTP {code}"


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    check_alive = "--check-alive" in argv
    site = yaml.safe_load(Path("config/site.yaml").read_text(encoding="utf-8")) or {}
    # affiliate は site.yaml の site: 配下にある。build.py も site["site"] で読む。
    aff = (site.get("site") or {}).get("affiliate") or {}
    enabled = bool(aff.get("enabled"))
    live = live_merchants(aff)

    print(f"提携中の merchant: {', '.join(sorted(live)) or '(なし)'}"
          f"{'' if enabled else '  ※ affiliate.enabled が false のため全て素のリンク'}")
    if not live:
        print("NG  もしもアフィリエイトのテンプレートが1つも入っていません。"
              "config/site.yaml の affiliate を設定してください。")
        return 1

    files = sorted({f for pat in (args or ["content/posts/*.md"]) for f in glob.glob(pat)})
    if not files:
        print("対象の記事がありません:", " ".join(args))
        return 1

    dead_merchant, mismatch, no_money, gone = [], [], [], []
    money_links = plain_links = 0

    for f in files:
        text = Path(f).read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not m:
            continue
        meta = yaml.safe_load(m.group(1)) or {}
        name = Path(f).name
        alts = [x for x in (meta.get("alternatives") or []) if x.get("name") and x.get("url")]
        if not alts:
            continue

        earning = 0
        for x in alts:
            url = str(x["url"]).strip()
            merchant = str(x.get("merchant") or "").strip()
            label = f"{name}: {x['name']}"

            if not merchant:
                # merchant なしは「対応ストアではない」の意思表示。事故ではない。
                plain_links += 1
                print(f"--  {label}\n      merchant なし（素のリンク）")
                continue
            if merchant not in live:
                dead_merchant.append(label)
                print(f"NG  {label}\n      merchant={merchant} は未提携。"
                      f"報酬が発生しません → merchant を消すか {'/'.join(sorted(live))} に差し替える")
                continue
            host = urlparse(url).netloc.lower()
            hosts = MERCHANT_HOSTS[merchant]
            if not any(host == h or host.endswith("." + h) for h in hosts):
                mismatch.append(label)
                print(f"NG  {label}\n      merchant={merchant} だが URL は {host}")
                continue
            if check_alive:
                ok, why = alive(url)
                if ok is False:
                    gone.append(label)
                    print(f"NG  {label}\n      {why}\n      {url}")
                    continue
            earning += 1
            money_links += 1
            print(f"OK  {label}  ({merchant})")

        if earning == 0:
            no_money.append(name)
            print(f"△   {name}: 代替品が {len(alts)}件あるが、報酬になるリンクは0本")

    print(f"\n記事 {len(files)}本 / 収益リンク {money_links}本 / 素のリンク {plain_links}本"
          f" / 未提携 merchant {len(dead_merchant)}本 / ドメイン不一致 {len(mismatch)}本"
          f" / 終了した商品 {len(gone)}本 / 収益リンク0本の記事 {len(no_money)}本")

    if dead_merchant or mismatch or gone:
        print("\n公開できません。代替品を "
              f"{'/'.join(sorted(live))} の商品ページに差し替えてください。"
              "\n楽天に妥当な商品が無い場合は merchant を書かずに素のリンクにする。"
              "\n報酬のために転売価格や怪しい並行輸入を勧めてはいけません。")
        return 1
    if no_money:
        # 収益ゼロは事故ではなく編集判断のこともあるので、止めずに知らせるだけ。
        print("\n上の△は、楽天に妥当な商品が無かったのなら問題ありません。")
    print("\n書いたリンクは収益になる形になっています。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
