#!/usr/bin/env python3
"""TOP の「よく読まれている記事」の元データを作る(2026-11-05 本人了承)。

Cloudflare Web Analytics の閲覧の記録から、過去30日に読まれた記事を多い順に並べて
data/popular.json に書く。自宅PCの ks_prefetch.py が毎晩呼び、一緒に push する
(GitHub のランナーには Cloudflare の鍵を置いていないため)。

    python scripts/popular.py            # 取って書く
    python scripts/popular.py --print    # 書かずに表示だけ

鍵は司令塔と同じ cockpit\\secrets\\cloudflare_token.txt を読む(リポジトリには入れない)。
Cloudflare の数字は抜き取りで粗い(10回単位)ので、build.py は並び順だけ使い、数は出さない。
"""
from __future__ import annotations

import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "popular.json"
TOKEN = Path(r"D:\MyDocument\ClaudeApp\cockpit\secrets\cloudflare_token.txt")
ACCOUNT = "3c00b0da715fa714950659b5e27ebba5"
HOST = "gadgetterminal.com"
DAYS = 30

QUERY = """query($acct: String!, $from: Date!, $to: Date!, $host: String!) { viewer {
  accounts(filter: {accountTag: $acct}) {
    rumPageloadEventsAdaptiveGroups(limit: 200,
      filter: {date_geq: $from, date_leq: $to, requestHost: $host},
      orderBy: [sum_visits_DESC]) {
      count sum { visits } dimensions { requestPath }
    } } } }"""


def fetch() -> list[dict]:
    token = TOKEN.read_text(encoding="utf-8").strip()
    today = dt.date.today()
    body = {"query": QUERY, "variables": {
        "acct": ACCOUNT, "host": HOST,
        "from": (today - dt.timedelta(days=DAYS)).isoformat(), "to": today.isoformat()}}
    req = urllib.request.Request("https://api.cloudflare.com/client/v4/graphql",
                                 json.dumps(body).encode(),
                                 {"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.load(res)
    if data.get("errors"):
        raise RuntimeError("; ".join(e.get("message", "") for e in data["errors"])[:300])
    rows = data["data"]["viewer"]["accounts"][0]["rumPageloadEventsAdaptiveGroups"]
    total: dict[str, list[int]] = {}
    for g in rows:
        path = (g["dimensions"]["requestPath"] or "").split("?")[0]
        if not path.startswith("/posts/"):
            continue
        t = total.setdefault(path, [0, 0])
        t[0] += int(g["sum"]["visits"])
        t[1] += int(g["count"])
    # 外から来た人(訪問)が多い順、同じなら閲覧の多い順
    ranked = sorted(total.items(), key=lambda kv: (kv[1][0], kv[1][1]), reverse=True)
    return [{"path": p, "visits": v, "views": c} for p, (v, c) in ranked[:20]]


def main() -> int:
    paths = fetch()
    data = {"updated": dt.date.today().isoformat(), "days": DAYS, "source": "Cloudflare Web Analytics",
            "paths": paths}
    if "--print" in sys.argv:
        print(json.dumps(data, ensure_ascii=False, indent=1))
        return 0
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"popular.json: {len(paths)}件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
