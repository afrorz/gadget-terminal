#!/usr/bin/env python3
"""TOP の「よく読まれている記事」の元データを作る(2026-11-05 本人了承)。

GA4 の閲覧の記録から、過去7日に読まれた記事を多い順に並べて
data/popular.json に書く(2026-11-21 本人了承で Cloudflare・30日から GA4・7日に変えた。
Cloudflare は約1割の抜き取りで10単位でしか動かず、30日では順位がほぼ変わらなかったため)。自宅PCの ks_prefetch.py が毎晩呼び、一緒に push する
(GitHub のランナーには Cloudflare の鍵を置いていないため)。

    python scripts/popular.py            # 取って書く
    python scripts/popular.py --print    # 書かずに表示だけ

GA4 は司令塔(cockpit\\collect.py)と同じく、gcloud のログインで係 cockpit-ga4 の名前を借りて読む(鍵ファイルなし)。
GA4 が読めない夜は、前と同じ Cloudflare(cockpit\\secrets\\cloudflare_token.txt)で数える。
build.py は並び順だけ使い、数は出さない。
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "popular.json"
TOKEN = Path(r"D:\MyDocument\ClaudeApp\cockpit\secrets\cloudflare_token.txt")
ACCOUNT = "3c00b0da715fa714950659b5e27ebba5"
HOST = "gadgetterminal.com"
DAYS = 7
GA4_PROPERTY = "561742941"  # GA4 プロパティ「Gadget Terminal」
GA4_SA = "cockpit-ga4@gadget-shorts-tts.iam.gserviceaccount.com"

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


def _post(url: str, body: dict, token: str) -> dict:
    req = urllib.request.Request(url, json.dumps(body).encode(),
                                 {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as res:
        return json.load(res)


def ga4_fetch() -> list[dict]:
    c = json.loads((Path(os.environ["APPDATA"]) / "gcloud" / "application_default_credentials.json").read_text(encoding="utf-8"))
    body = urllib.parse.urlencode({"client_id": c["client_id"], "client_secret": c["client_secret"],
                                   "refresh_token": c["refresh_token"], "grant_type": "refresh_token"}).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", body, timeout=30) as res:
        user = json.load(res)["access_token"]
    token = _post(f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{GA4_SA}:generateAccessToken",
                  {"scope": ["https://www.googleapis.com/auth/analytics.readonly"], "lifetime": "600s"}, user)["accessToken"]
    rep = _post(f"https://analyticsdata.googleapis.com/v1beta/properties/{GA4_PROPERTY}:runReport", {
        "dateRanges": [{"startDate": f"{DAYS}daysAgo", "endDate": "today"}],
        "dimensions": [{"name": "pagePath"}],
        "metrics": [{"name": "sessions"}, {"name": "screenPageViews"}],
        "dimensionFilter": {"filter": {"fieldName": "pagePath", "stringFilter": {"matchType": "BEGINS_WITH", "value": "/posts/"}}},
        "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}],
        "limit": 200}, token)
    total: dict[str, list[int]] = {}
    for r in rep.get("rows", []):
        path = r["dimensionValues"][0]["value"].split("?")[0]
        t = total.setdefault(path, [0, 0])
        t[0] += int(r["metricValues"][0]["value"])
        t[1] += int(r["metricValues"][1]["value"])
    ranked = sorted(total.items(), key=lambda kv: (kv[1][0], kv[1][1]), reverse=True)
    return [{"path": p, "visits": v, "views": c} for p, (v, c) in ranked[:20]]


def main() -> int:
    try:
        paths, source = ga4_fetch(), "GA4"
        if not paths:
            raise RuntimeError("GA4 の結果が0件")
    except Exception as e:  # GA4 が読めない夜は Cloudflare で数える
        print(f"GA4 が読めないので Cloudflare で数える: {e}", file=sys.stderr)
        paths, source = fetch(), "Cloudflare Web Analytics"
    data = {"updated": dt.date.today().isoformat(), "days": DAYS, "source": source,
            "paths": paths}
    if "--print" in sys.argv:
        print(json.dumps(data, ensure_ascii=False, indent=1))
        return 0
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"popular.json: {len(paths)}件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
