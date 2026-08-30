#!/usr/bin/env python3
"""既存記事の代替品リンク（merchant: amazon）を、楽天市場の商品に差し替える候補を探す。

    python scripts/find_rakuten_alt.py                 # 対象を全部調べて候補一覧を出す
    python scripts/find_rakuten_alt.py --apply          # 一覧を見て良ければ front matter に書き込む

**書き換えは自動でしない。** 型番違い・別モデルを誤って選ぶと、読者に間違った
商品を勧めることになり記事の信頼に関わる。まず候補を出して人が確認し、
--apply を付けたときだけ、確認済みとして front matter を書き換える。

必要なもの:
  - config/site.yaml の site.rakuten_app_id （楽天ウェブサービスで無料発行）
  - config/secrets.local.yaml の rakuten_access_key （同じ画面の「アクセスキー」）
    このファイルは .gitignore 済み。GitHubには上がらない。
"""
from __future__ import annotations

import glob
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SEARCH_URL = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"
ORIGIN = "https://gadgetterminal.com"

# 転売・並行輸入・訳ありを名前から弾く。買ってよいと勧める記事なので、
# 迷ったら候補から外す方に倒す（本文の方針: 「読者へ不利な店を勧めるのは本末転倒」）。
NG_WORDS = ("中古", "アウトレット", "訳あり", "並行輸入", "海外直送", "ジャンク",
            "返品不可", "キズ", "汚れ", "B級品", "在庫処分")

# 「製品名」で検索すると、本体よりケースやフィルムの方がレビュー数を稼いでいて
# 上位に来ることが多い（実測: ANBERNIC RG35XX+ の代替品として保護フィルムが選ばれた、
# ASUS ROG Ally X が3記事とも保護ケースになった等）。読者に勧めたいのは本体であって
# 付属品ではないので、名前にこれらの語を含む商品は候補から外す。
ACCESSORY_WORDS = ("ケース", "カバー", "フィルム", "保護シート", "スキンシール",
                   "ステッカー", "ストラップ", "スタンド台", "レンズ保護", "液晶保護",
                   "収納", "ポーチ", "バッグ", "キャリング")

RATE_LIMIT_SEC = 1.2  # 予想QPS=1で申請したので、余裕を持たせて待つ


def clean_keyword(name: str) -> str:
    """商品検索に投げる語に整形する。

    front matter の name には「（Amazon.co.jp）」「(国内正規品)」のような
    Amazon時代の注記が付いている。検索語としては邪魔なので落とす。

    また、このAPIは1文字だけの単語（例: "X"）を含む keyword を
    "keyword is not valid" で拒否する（実測で確認済み）。"ROG Ally X" のような
    型番は日本語の型番表記でもよくあるので、前の単語にくっつけて "AllyX" にする。
    """
    name = re.sub(r"[（(][^）)]*[）)]", "", name)
    tokens = name.split()
    out: list[str] = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if len(t) == 1 and t.isalnum():
            if out:
                out[-1] += t
            elif i + 1 < len(tokens):
                tokens[i + 1] = t + tokens[i + 1]
        else:
            out.append(t)
        i += 1
    return " ".join(out).strip()


def search(app_id: str, access_key: str, keyword: str, hits: int = 10) -> list[dict]:
    params = {
        "applicationId": app_id,
        "accessKey": access_key,
        "keyword": keyword,
        "hits": hits,
        "sort": "standard",
        "format": "json",
    }
    url = SEARCH_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Origin": ORIGIN,
        "User-Agent": "GadgetTerminal-LinkTool/1.0 (+https://gadgetterminal.com/)",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        import json
        data = json.load(r)
    return [it["Item"] for it in data.get("Items", [])]


GENERATION_SUFFIX_RE = re.compile(r"^(2|3|4|5|6|ii|iii|iv|v)$", re.I)

# キーワードに無いのにこれが item 名に出てきたら、別バリエーションの疑いが強い。
# 実測: 「Qoobo」で検索して「Petit Qoobo（小型版）」が最多レビューで選ばれた。
VARIANT_WORDS = ("プチ", "petit", "ミニ", "mini", "ジュニア", "junior", "コンパクト")


def variant_mismatch(keyword: str, item_name: str) -> bool:
    """型番のすぐ後ろに新しい数字が続く（世代違い）か、キーワードに無い
    バリエーション語が入っている（別サイズ・別モデル）かを見る。

    実測: 「DJI Neo」で検索すると「DJI Neo 2」（別製品・別世代）が
    レビュー数トップで出てきた。次の単語が数字/ローマ数字だけなら弾く。
    """
    kw_low = keyword.lower()
    name_low = item_name.lower()
    kw_tokens = kw_low.split()
    name_tokens = re.split(r"[\s/／、,，]+", name_low)
    for i in range(len(name_tokens) - len(kw_tokens) + 1):
        if name_tokens[i:i + len(kw_tokens)] == kw_tokens:
            nxt = name_tokens[i + len(kw_tokens)] if i + len(kw_tokens) < len(name_tokens) else ""
            if GENERATION_SUFFIX_RE.match(nxt):
                return True
            break
    return any(w in name_low and w not in kw_low for w in VARIANT_WORDS)


def pick_best(items: list[dict], keyword: str) -> dict | None:
    """候補から一番良さそうな1件を選ぶ。付属品・別モデルしか無ければ「候補なし」を返す。

    NG_WORDS・ACCESSORY_WORDS を含むもの、世代/バリエーション違いの疑いがあるものを除外し、
    価格が極端に外れたもの（中央値の 0.4〜3倍を外れる＝転売やジャンク・型違いの疑いが強い）
    も除く。残りからレビュー件数が多い順に選ぶ。
    """
    clean = [it for it in items
             if not any(ng in it["itemName"] for ng in NG_WORDS)
             and not any(w in it["itemName"] for w in ACCESSORY_WORDS)
             and not variant_mismatch(keyword, it["itemName"])]
    if not clean:
        return None
    prices = sorted(it["itemPrice"] for it in clean)
    mid = prices[len(prices) // 2]
    in_range = [it for it in clean if mid * 0.4 <= it["itemPrice"] <= mid * 3] or clean
    in_range.sort(key=lambda it: it.get("reviewCount", 0), reverse=True)
    return in_range[0]


def targets(files: list[str]) -> list[tuple[Path, int, dict]]:
    """merchant: amazon の代替品を持つ (ファイル, 何番目か, 現在の値) を集める。"""
    out = []
    for f in files:
        p = Path(f)
        text = p.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not m:
            continue
        fm = yaml.safe_load(m.group(1)) or {}
        for idx, a in enumerate(fm.get("alternatives") or []):
            if str(a.get("merchant") or "") == "amazon":
                out.append((p, idx, a))
    return out


def apply_change(path: Path, idx: int, new_url: str, new_name: str) -> None:
    """front matter の alternatives[idx] だけを書き換える。本文には触らない。"""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fm = yaml.safe_load(m.group(1)) or {}
    alt = fm["alternatives"][idx]
    alt["url"] = new_url
    alt["merchant"] = "rakuten"
    alt["name"] = new_name
    new_fm = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    path.write_text(f"---\n{new_fm}---\n{text[m.end():]}", encoding="utf-8")


def main(argv: list[str]) -> int:
    apply = "--apply" in argv
    site = yaml.safe_load((ROOT / "config" / "site.yaml").read_text(encoding="utf-8"))["site"]
    secrets_path = ROOT / "config" / "secrets.local.yaml"
    if not secrets_path.exists():
        print("NG  config/secrets.local.yaml がありません。"
              "rakuten_access_key を書いたファイルを先に作ってください。")
        return 1
    secrets = yaml.safe_load(secrets_path.read_text(encoding="utf-8")) or {}
    app_id = str(site.get("rakuten_app_id") or "").strip()
    access_key = str(secrets.get("rakuten_access_key") or "").strip()
    if not app_id or not access_key:
        print("NG  rakuten_app_id または rakuten_access_key が空です。")
        return 1

    files = sorted(glob.glob(str(ROOT / "content" / "posts" / "*.md")))
    todo = targets(files)
    print(f"対象（merchant: amazon の代替品）: {todo and len(todo)}件\n")

    results = []
    for path, idx, alt in todo:
        kw = clean_keyword(str(alt["name"]))
        time.sleep(RATE_LIMIT_SEC)
        try:
            items = search(app_id, access_key, kw)
        except urllib.error.HTTPError as e:
            print(f"NG  {path.name}: 検索失敗 ({e.code}) keyword={kw!r}")
            continue
        best = pick_best(items, kw)
        print(f"■ {path.name}")
        print(f"   現在: {alt['name']}  ({alt['url']})")
        if not best:
            print("   → 楽天に妥当な候補が見つからず。merchant を外して素のリンクにすることを検討")
            results.append((path, idx, alt, None))
            continue
        print(f"   候補: {best['itemName'][:50]}  {best['itemPrice']}円"
              f"  レビュー{best.get('reviewCount', 0)}件  店舗:{best['shopName']}")
        print(f"   URL : {best['itemUrl']}")
        results.append((path, idx, alt, best))
        print()

    ok = sum(1 for *_, b in results if b)
    none = len(results) - ok
    print(f"\n候補あり {ok}件 / 候補なし {none}件")

    if not apply:
        print("\nこれは確認用の一覧です。書き換えるには --apply を付けて再実行してください。")
        return 0

    changed = 0
    for path, idx, alt, best in results:
        if not best:
            continue
        apply_change(path, idx, best["itemUrl"], best["itemName"])
        changed += 1
    print(f"\n{changed}件の front matter を書き換えました。"
          f"python scripts/checklinks.py と python scripts/build.py で確認してください。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
