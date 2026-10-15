"""総務省「技術基準適合証明等を受けた機器の検索」を引く。

    python scripts/giteki.py --name Suunto            # 認証を受けた者の名称で
    python scripts/giteki.py --name Suunto --since 2026-01-01
    python scripts/giteki.py --model OW222            # 型式又は名称で

技適の有無を「国内で売っているから取っているはず」で書かないための道具。
一次ソースは総務省のデータベースで、ここに型式が出ていれば取得済みと言える。

**Web-API(giteki/list, giteki/num)は使わない。** 2026-09-27 時点で、仕様書に
載っている例のリクエストまで 403 を返した。代わりに電波利用ポータルの検索画面
(SearchServlet)を GET で呼ぶ。この画面は「特定無線設備の種別(RAD)」の指定が
必須で、無いと結果ではなく検索フォームが返る。種別の一覧は検索フォームから
毎回取り直す(制度改正で種別が増えても追随できるように)。
"""

import argparse
import functools
import html
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

BASE = "https://www.tele.soumu.go.jp/giteki/SearchServlet"
# 素の urllib の UA だと弾かれる。ブラウザ相当の UA を名乗る。
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
WAREKI = {"令和": 2018, "平成": 1988, "昭和": 1925}


def _get(url: str) -> str:
    """応答は Content-Type / meta ともに UTF-8(2026-10-15 実測)。デコードは正しい。

    以前「文字化けする」ように見えたのは、DB の値が全角英数(「Ｓｅｎｎｈｅｉｓｅｒ」)で、
    それを Windows の cp932 標準出力に流していたため。取り込み時に NFKC で半角へ
    正規化し(norm_text)、標準出力は main() で UTF-8 に固定する。
    """
    last = None
    for i in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
                m = re.search(r"charset=([\w-]+)", r.headers.get("Content-Type", ""))
            return raw.decode(m.group(1) if m else "utf-8", errors="replace")
        except OSError as e:   # URLError / 接続断 / タイムアウト
            last = e
            time.sleep(2 * (i + 1))
    raise last


def norm_text(s: str) -> str:
    """DB の全角英数・全角空白を半角に寄せる(NFKC)。空白は1つに畳む。"""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s)).strip()


@functools.lru_cache(maxsize=1)
def rad_codes() -> list[str]:
    form = _get(f"{BASE}?pageID=js01")
    codes = re.findall(r'name="RAD"[^>]*value="([0-9-]+)"|value="([0-9-]+)"[^>]*name="RAD"', form)
    return sorted({a or b for a, b in codes})


def to_iso(wareki: str) -> str:
    """「令和8年9月3日」→「2026-09-03」。読めなければ空文字。"""
    m = re.match(r"(令和|平成|昭和)(元|\d+)年(\d+)月(\d+)日", wareki)
    if not m:
        return ""
    y = 1 if m.group(2) == "元" else int(m.group(2))
    return f"{WAREKI[m.group(1)] + y:04d}-{int(m.group(3)):02d}-{int(m.group(4)):02d}"


def search(name: str | None = None, model: str | None = None,
           since: str | None = None) -> list[dict]:
    """名称(認証を受けた者・部分一致)か型式で引く。

    戻り値の各行: number / holder(登録者) / model(型式又は名称) / date(ISO) /
    kind(特定無線設備の種別の文言) / date_raw。文字列は NFKC で半角に正規化済み。
    since(YYYY-MM-DD)を渡すと、その日以降の認証だけに絞る。新しい順。
    """
    name, model = name or "", model or ""
    if not name and not model:
        raise ValueError("name か model のどちらかは必要")
    # 1ページ10件固定(DC は変えても効かなかった)。SC で開始位置を送ってめくる。
    params = [("pageID", "jk01"), ("NAM", name), ("FOM", model), ("SC", "1")]
    params += [("RAD", c) for c in rad_codes()]
    params += [("TEC", str(i)) for i in range(1, 8)]
    if since and re.match(r"\d{4}-\d{2}-\d{2}$", since):
        # 検索画面の「年月日 from」。サーバー側で絞るとページ数(=リクエスト数)が減る。
        # 結果は古い順に返るので、絞らないと大口の登録者は500件の打ち切りで新しい方が落ちる。
        y, mo, d = since.split("-")
        params += [("YAR_FROM", y), ("MON_FROM", str(int(mo))), ("DAY_FROM", str(int(d)))]
    out, sc = [], 1
    while True:
        q =[(k, (str(sc) if k == "SC" else v)) for k, v in params]
        page = _get(f"{BASE}?{urllib.parse.urlencode(q)}")
        rows = []
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S):
            cells = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", td))).strip()
                     for td in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
            # 結果行は「種類(アイコン)・名称・種別・型式・番号・年月日…」の並び。
            # 先頭のセルは空なので、年月日が和暦として読めるかで結果行を見分ける。
            if len(cells) >= 6 and to_iso(cells[5]):
                rows.append({"holder": norm_text(cells[1]), "kind": norm_text(cells[2]),
                             "model": norm_text(cells[3]), "number": norm_text(cells[4]),
                             "date": to_iso(cells[5]), "date_raw": cells[5]})
        out += rows
        total = re.search(r"([0-9,]+)\s*件中", page)
        total_n = int(total.group(1).replace(",", "")) if total else len(out)
        if not rows or sc + len(rows) > total_n or sc > 500:
            break  # 500件を超える名称は絞り込みが甘い。--model か --since で絞る
        sc += len(rows)
    # 同じ番号が重複して出ることがある(実測: Suunto OW222 が2行)
    seen, uniq = set(), []
    for r in out:
        if r["number"] not in seen:
            seen.add(r["number"])
            uniq.append(r)
    if since:
        uniq = [r for r in uniq if r["date"] >= since]
    uniq.sort(key=lambda r: r["date"], reverse=True)
    return uniq


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="", help="氏名又は名称(部分一致)")
    ap.add_argument("--model", default="", help="型式又は名称(部分一致)")
    ap.add_argument("--since", default="", help="この日付(YYYY-MM-DD)以降の認証だけ出す")
    a = ap.parse_args(argv)
    for st in (sys.stdout, sys.stderr):   # Windows の既定(cp932)だと Git Bash 等で化ける
        try:
            st.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    if not a.name and not a.model:
        ap.error("--name か --model のどちらかは必要")
    rows = search(a.name, a.model, a.since or None)
    for r in rows:
        print(f'{r["date"] or r["date_raw"]}  {r["number"]:<16} {r["model"]}  ({r["holder"]})')
    print(f"{len(rows)} 件", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
