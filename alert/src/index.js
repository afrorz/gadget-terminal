/**
 * 日本上陸アラート(alert.gadgetterminal.com)。
 *
 * なぜ要るか(2026-11-01 本人決定):
 *   GT の記事の 86% は「海外で出たばかりで、まだ日本で買えない製品」。読者はその製品が欲しくて
 *   来るので、「技適が確認できない=今は無理」で終わると買う気が消える。代わりの品は「ふーん」で
 *   終わる。そこで買う気を消さずに預かり、日本で買えるようになった時に1通だけ知らせ、
 *   その時に初めて「製品そのものを買うリンク」のある記事へ送る。
 *
 * 流れ:
 *   1. 記事の「日本で買える？使える？」の節にある欄から POST /subscribe (email, slug)
 *   2. 確認メールを送る(Resend)。リンク GET /confirm?t=TOKEN で登録完了(二段階にして、
 *      他人のアドレスを勝手に登録されるのを防ぐ)
 *   3. 毎朝 cron がサイトの landing.json(build.py が出す)を読み、landed が true になった
 *      記事の登録者に1通ずつ送り、notified に記録する(1記事1回)
 *   4. GET /unsubscribe?t=TOKEN で解除
 *
 * メールには紹介リンクを入れない(Amazon アソシエイトはメール内のリンクを禁じている)。
 * 記事の「日本上陸」の枠へ送る。
 *
 * 週1メール(2026-11-10 本人了承):
 *   記事の終わりの欄から slug="weekly" で登録する(同じ表・同じ確認の流れ)。毎週日曜 10:00 JST の cron が
 *   サイトの weekly.json(build.py が note の週まとめから作る)を読み、登録者に1通ずつ送る。
 *   同じ週は2回送らない(notified に "weekly-<日付>" を記録)。weekly.json が古ければ送らない。
 *
 * 環境: DB(D1)、RESEND_API_KEY(秘密)、SITE、FROM、ALLOW_ORIGINS(vars)
 */

const EMAIL_RE = /^[^\s@]{1,64}@[^\s@]{1,255}\.[^\s@]{2,}$/;
const SLUG_RE = /^[a-z0-9][a-z0-9-]{1,120}$/;
const MAX_PER_IP_PER_HOUR = 10;
const WEEKLY = "weekly";
const WEEKLY_CRON = "0 1 * * 0";
const WEEKLY_ITEM = { title: "週1回の海外ガジェット5選", landed: false };

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";
    const cors = corsHeaders(env, origin);
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    try {
      if (url.pathname === "/subscribe" && request.method === "POST") return await subscribe(request, env, cors);
      if (url.pathname === "/confirm" && request.method === "GET") return await confirm(url, env);
      if (url.pathname === "/unsubscribe" && request.method === "GET") return await unsubscribe(url, env);
      if (url.pathname === "/pending" && request.method === "GET") return await pending(env);
      if (url.pathname === "/" || url.pathname === "/health") return new Response("gt-alert ok", { headers: { "content-type": "text/plain; charset=utf-8" } });
      return new Response("not found", { status: 404 });
    } catch (e) {
      console.error("fetch error", e && e.stack || e);
      return page("エラー", "処理できませんでした。時間をおいてもう一度お試しください。", env, 500);
    }
  },

  async scheduled(event, env, ctx) {
    if (event.cron === WEEKLY_CRON) ctx.waitUntil(sendWeekly(env));
    else ctx.waitUntil(notifyLanded(env));
  },
};

function corsHeaders(env, origin) {
  const allowed = String(env.ALLOW_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean);
  const h = { "Vary": "Origin" };
  if (allowed.includes(origin)) {
    h["Access-Control-Allow-Origin"] = origin;
    h["Access-Control-Allow-Methods"] = "POST, OPTIONS";
    h["Access-Control-Allow-Headers"] = "Content-Type";
  }
  return h;
}

function now() { return new Date().toISOString(); }

function token() {
  const b = new Uint8Array(24);
  crypto.getRandomValues(b);
  return Array.from(b, (x) => x.toString(16).padStart(2, "0")).join("");
}

async function sha256(s) {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return Array.from(new Uint8Array(d), (x) => x.toString(16).padStart(2, "0")).join("").slice(0, 32);
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

/** サイトのフォントと色に近い、最小限のページ。記事へ戻るリンクつき */
function page(title, body, env, status = 200, backUrl = "") {
  const back = backUrl || env.SITE;
  const html = `<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>${esc(title)} — Gadget Terminal</title>
<style>body{margin:0;font-family:system-ui,-apple-system,"Hiragino Sans","Noto Sans JP",sans-serif;background:#f7f7f5;color:#1a1a1a}
main{max-width:560px;margin:12vh auto;padding:28px 24px;background:#fff;border-left:3px solid #d8452e;border-radius:3px}
h1{font-size:20px;margin:0 0 14px}p{font-size:15px;line-height:1.9;margin:0 0 12px}a{color:#d8452e}
.k{font-family:ui-monospace,Menlo,monospace;font-size:11px;letter-spacing:.12em;color:#777;margin:0 0 10px}</style></head>
<body><main><p class="k">GADGET TERMINAL / 日本上陸アラート</p><h1>${esc(title)}</h1>${body}
<p><a href="${esc(back)}">${backUrl ? "記事に戻る" : "Gadget Terminal へ"}</a></p></main></body></html>`;
  return new Response(html, { status, headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" } });
}

/** build.py が書き出す landing.json。slug → {title, url, status, landed, summary} */
async function loadLanding(env) {
  const r = await fetch(`${env.SITE}/landing.json`, { headers: { "accept": "application/json" }, cf: { cacheTtl: 300 } });
  if (!r.ok) throw new Error(`landing.json ${r.status}`);
  const data = await r.json();
  const map = new Map();
  for (const it of data.items || []) map.set(it.slug, it);
  return map;
}

async function readInput(request) {
  const ct = request.headers.get("content-type") || "";
  if (ct.includes("application/json")) return await request.json();
  const form = await request.formData();
  return Object.fromEntries(form.entries());
}

function wantsJson(request) {
  const accept = request.headers.get("accept") || "";
  const ct = request.headers.get("content-type") || "";
  return ct.includes("application/json") || accept.includes("application/json");
}

async function subscribe(request, env, cors) {
  const input = await readInput(request);
  const asJson = wantsJson(request);
  const reply = (status, obj, humanTitle, humanBody, backUrl) => asJson
    ? new Response(JSON.stringify(obj), { status, headers: { ...cors, "content-type": "application/json; charset=utf-8" } })
    : page(humanTitle, humanBody, env, status, backUrl);

  // ボットよけ。見えない欄に何か入っていたら、成功したふりをして捨てる
  if (String(input.website || "").trim()) return reply(200, { ok: true }, "受け付けました", "<p>確認メールをお送りしました。</p>");

  const email = String(input.email || "").trim().toLowerCase();
  const slug = String(input.slug || "").trim();
  if (!EMAIL_RE.test(email)) return reply(400, { ok: false, error: "メールアドレスの形が違います" }, "登録できません", "<p>メールアドレスの形が違います。</p>");
  if (!SLUG_RE.test(slug)) return reply(400, { ok: false, error: "記事が分かりません" }, "登録できません", "<p>どの記事か分かりませんでした。</p>");

  const isWeekly = slug === WEEKLY;
  const item = isWeekly ? { ...WEEKLY_ITEM, url: env.SITE } : (await loadLanding(env)).get(slug);
  if (!item) return reply(404, { ok: false, error: "その記事は見つかりません" }, "登録できません", "<p>その記事は見つかりませんでした。</p>");
  const backUrl = item.url;
  if (item.landed) return reply(200, { ok: true, landed: true, message: "この製品はすでに日本で買えます。記事の「日本上陸」の枠をご覧ください" },
    "もう日本で買えます", `<p>「${esc(item.title)}」はすでに日本で買えます。記事の「日本上陸」の枠に買える場所をまとめています。</p>`, backUrl);

  // 同じ IP から1時間に何件も来たら止める(アドレスそのものは保存しない)
  const ip = request.headers.get("CF-Connecting-IP") || "";
  const ipHash = ip ? await sha256(ip + "|" + slugSalt(env)) : null;
  if (ipHash) {
    const since = new Date(Date.now() - 3600_000).toISOString();
    const { c } = await env.DB.prepare("SELECT COUNT(*) AS c FROM subscriptions WHERE ip_hash = ? AND created_at > ?").bind(ipHash, since).first();
    if (c >= MAX_PER_IP_PER_HOUR) return reply(429, { ok: false, error: "しばらく待ってからお試しください" }, "登録できません", "<p>短い時間に登録が多すぎます。しばらく待ってからお試しください。</p>", backUrl);
  }

  const existing = await env.DB.prepare("SELECT token, confirmed_at, unsubscribed_at FROM subscriptions WHERE email = ? AND slug = ?").bind(email, slug).first();
  let tok;
  if (existing && existing.confirmed_at && !existing.unsubscribed_at) {
    return reply(200, { ok: true, already: true, message: "このアドレスはすでに登録済みです" },
      "登録済みです", `<p>このメールアドレスは「${esc(item.title)}」${isWeekly ? "のメール" : "の上陸アラート"}に登録済みです。</p>`, backUrl);
  }
  if (existing) {
    // 未確認のまま、または解除後の再登録。トークンを作り直して確認メールを送り直す
    tok = token();
    await env.DB.prepare("UPDATE subscriptions SET token = ?, created_at = ?, confirmed_at = NULL, unsubscribed_at = NULL, notified_at = NULL, ip_hash = ? WHERE email = ? AND slug = ?")
      .bind(tok, now(), ipHash, email, slug).run();
  } else {
    tok = token();
    await env.DB.prepare("INSERT INTO subscriptions (email, slug, token, ip_hash, created_at) VALUES (?, ?, ?, ?, ?)")
      .bind(email, slug, tok, ipHash, now()).run();
  }

  const confirmUrl = `${selfOrigin(request)}/confirm?t=${tok}`;
  if (isWeekly) {
    await sendMail(env, {
      to: email,
      subject: "【Gadget Terminal】週1回のメール、登録を確認してください",
      text: [
        "このメールアドレスで、Gadget Terminal の週1回のメール(毎週日曜の朝、その週の海外ガジェット5選と日本に来た製品)の登録を受け付けました。",
        "",
        "下のリンクを開くと登録が完了します。",
        confirmUrl,
        "",
        "心当たりがなければ、このメールは無視してください。登録は完了しません。",
        "",
        `Gadget Terminal ${env.SITE}/`,
      ].join("\n"),
    });
    return reply(200, { ok: true, message: "確認メールを送りました。メールのリンクを開くと登録が完了します" },
      "確認メールを送りました", `<p>${esc(email)} に確認メールを送りました。メールのリンクを開くと、週1回のメールの登録が完了します。</p><p>届かないときは、迷惑メールの欄もご確認ください。</p>`, backUrl);
  }
  await sendMail(env, {
    to: email,
    subject: `【Gadget Terminal】「${item.title}」の日本上陸アラート、登録を確認してください`,
    text: [
      `このメールアドレスで、「${item.title}」が日本で買えるようになったときに1通だけお知らせする登録を受け付けました。`,
      ``,
      `下のリンクを開くと登録が完了します。`,
      confirmUrl,
      ``,
      `心当たりがなければ、このメールは無視してください。登録は完了しません。`,
      ``,
      `記事: ${item.url}`,
      `Gadget Terminal ${env.SITE}/`,
    ].join("\n"),
  });

  return reply(200, { ok: true, message: "確認メールを送りました。メールのリンクを開くと登録が完了します" },
    "確認メールを送りました", `<p>${esc(email)} に確認メールを送りました。メールのリンクを開くと、「${esc(item.title)}」の上陸アラートの登録が完了します。</p><p>届かないときは、迷惑メールの欄もご確認ください。</p>`, backUrl);
}

function slugSalt(env) { return env.FROM || "gt"; }

function selfOrigin(request) { return new URL(request.url).origin; }

async function confirm(url, env) {
  const t = url.searchParams.get("t") || "";
  if (!/^[0-9a-f]{48}$/.test(t)) return page("リンクが正しくありません", "<p>確認のリンクが壊れています。記事からもう一度登録してください。</p>", env, 400);
  const row = await env.DB.prepare("SELECT slug, confirmed_at, unsubscribed_at FROM subscriptions WHERE token = ?").bind(t).first();
  if (!row) return page("リンクが正しくありません", "<p>この確認リンクは使えません。記事からもう一度登録してください。</p>", env, 404);
  if (!row.confirmed_at || row.unsubscribed_at) {
    await env.DB.prepare("UPDATE subscriptions SET confirmed_at = ?, unsubscribed_at = NULL WHERE token = ?").bind(now(), t).run();
  }
  const unsub = `${url.origin}/unsubscribe?t=${t}`;
  if (row.slug === WEEKLY) {
    return page("登録しました", `<p>毎週日曜の朝に、その週の海外ガジェット5選と、日本で買えるようになった製品を1通お届けします。</p>
<p>解除はいつでもできます: <a href="${esc(unsub)}">登録を解除する</a></p>`, env, 200);
  }
  const landing = await loadLanding(env);
  const item = landing.get(row.slug);
  const title = item ? item.title : row.slug;
  const backUrl = item ? item.url : "";
  return page("登録しました", `<p>「${esc(title)}」が日本で買えるようになったら、このメールアドレスに1通だけお知らせします。</p>
<p>それまでメールは送りません。解除はいつでもできます: <a href="${esc(unsub)}">登録を解除する</a></p>`, env, 200, backUrl);
}

async function unsubscribe(url, env) {
  const t = url.searchParams.get("t") || "";
  if (!/^[0-9a-f]{48}$/.test(t)) return page("リンクが正しくありません", "<p>解除のリンクが壊れています。</p>", env, 400);
  const row = await env.DB.prepare("SELECT slug FROM subscriptions WHERE token = ?").bind(t).first();
  if (!row) return page("解除済みです", "<p>この登録はすでに無いか、解除済みです。</p>", env, 200);
  await env.DB.prepare("UPDATE subscriptions SET unsubscribed_at = ? WHERE token = ?").bind(now(), t).run();
  if (row.slug === WEEKLY) return page("解除しました", "<p>週1回のメールを解除しました。今後このメールアドレスには届きません。</p>", env, 200);
  return page("解除しました", "<p>この製品の上陸アラートを解除しました。今後このメールアドレスにはお知らせを送りません。</p>", env, 200);
}

/**
 * 登録者が待っている記事の slug 一覧(メールは出さない)。
 * 過去記事の見回り(scripts/followup.py)が毎日これを読み、登録のある記事は 7 日おきでなく
 * 毎日見る(2026-11-01 本人決定)。1日8本の枠とは別に足すので Claude の利用枠はほぼ増えない。
 */
async function pending(env) {
  const rows = (await env.DB.prepare(
    "SELECT DISTINCT s.slug FROM subscriptions s LEFT JOIN notified n ON n.slug = s.slug " +
    "WHERE s.slug != 'weekly' AND s.confirmed_at IS NOT NULL AND s.unsubscribed_at IS NULL AND s.notified_at IS NULL AND n.slug IS NULL ORDER BY s.slug"
  ).all()).results;
  return new Response(JSON.stringify({ slugs: rows.map((r) => r.slug) }), {
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "public, max-age=300" },
  });
}

/** 毎朝: landed になった記事の登録者に1通ずつ送る(記事ごとに1回だけ) */
async function notifyLanded(env) {
  const landing = await loadLanding(env);
  const done = new Set((await env.DB.prepare("SELECT slug FROM notified").all()).results.map((r) => r.slug));
  let sentTotal = 0;
  for (const item of landing.values()) {
    if (!item.landed || done.has(item.slug)) continue;
    const subs = (await env.DB.prepare(
      "SELECT email, token FROM subscriptions WHERE slug = ? AND confirmed_at IS NOT NULL AND unsubscribed_at IS NULL AND notified_at IS NULL"
    ).bind(item.slug).all()).results;
    let sent = 0;
    for (const s of subs) {
      try {
        await sendMail(env, {
          to: s.email,
          subject: `【Gadget Terminal】「${item.title}」が日本で買えるようになりました`,
          text: [
            `登録いただいた「${item.title}」の日本上陸をお知らせします。`,
            ``,
            `状態: ${item.status}`,
            item.summary ? item.summary : "",
            ``,
            `買える場所と値段は、記事の「日本上陸」の枠にまとめています。`,
            `${item.url}?utm_source=alert&utm_medium=email`,
            ``,
            `このお知らせは、この製品について1回だけです。`,
            `登録の解除: ${env.ALERT_ORIGIN}/unsubscribe?t=${s.token}`,
            ``,
            `Gadget Terminal ${env.SITE}/`,
          ].filter((l) => l !== null).join("\n"),
        });
        await env.DB.prepare("UPDATE subscriptions SET notified_at = ? WHERE token = ?").bind(now(), s.token).run();
        sent++;
      } catch (e) {
        console.error("send failed", item.slug, e && e.message);
      }
    }
    await env.DB.prepare("INSERT OR REPLACE INTO notified (slug, status, sent_at, sent_count) VALUES (?, ?, ?, ?)")
      .bind(item.slug, item.status, now(), sent).run();
    sentTotal += sent;
    console.log(`landed: ${item.slug} (${item.status}) → ${sent} 通`);
  }
  console.log(`notifyLanded: ${sentTotal} 通`);
}

/** 毎週日曜: weekly.json の5本と今週の日本上陸を、週1メールの登録者に送る(同じ週は1回だけ) */
async function sendWeekly(env) {
  const r = await fetch(`${env.SITE}/weekly.json`, { headers: { "accept": "application/json" }, cf: { cacheTtl: 300 } });
  if (!r.ok) throw new Error(`weekly.json ${r.status}`);
  const w = await r.json();
  const ageDays = (Date.now() - Date.parse(`${w.date}T00:00:00+09:00`)) / 86400_000;
  if (!(w.items || []).length || !(ageDays >= -1 && ageDays <= 3)) {
    console.log(`sendWeekly: weekly.json が今週の物でない(${w.date})。送らない`);
    return;
  }
  const key = `weekly-${w.date}`;
  if (await env.DB.prepare("SELECT slug FROM notified WHERE slug = ?").bind(key).first()) {
    console.log(`sendWeekly: ${key} は送信済み`);
    return;
  }
  const subs = (await env.DB.prepare(
    "SELECT email, token FROM subscriptions WHERE slug = ? AND confirmed_at IS NOT NULL AND unsubscribed_at IS NULL"
  ).bind(WEEKLY).all()).results;
  // メールには紹介リンクを入れない(記事へ送るだけ)。どこから来たかは utm で数える
  const tag = (u) => u ? `${u}${u.includes("?") ? "&" : "?"}utm_source=weekly&utm_medium=email` : env.SITE;
  const title = w.title || "今週の海外ガジェット5選";
  const row = (x) => `<tr><td style="padding:14px 0;border-top:1px solid #eee;vertical-align:top;width:104px">${x.image ? `<img src="${esc(x.image)}" width="96" height="96" alt="" style="width:96px;height:96px;object-fit:contain;background:#fff;border:1px solid #eee;border-radius:4px">` : ""}</td>
<td style="padding:14px 0 14px 12px;border-top:1px solid #eee;vertical-align:top"><a href="${esc(tag(x.url))}" style="font-weight:700;font-size:15px;color:#1a1a1a;text-decoration:none">${esc(x.title)}</a>
<p style="margin:6px 0 0;font-size:13.5px;line-height:1.7;color:#555">${esc(x.text)}</p></td></tr>`;
  let sent = 0;
  for (const s of subs) {
    const unsub = `${env.ALERT_ORIGIN}/unsubscribe?t=${s.token}`;
    const text = [
      title, "", w.lead || "", "",
      ...w.items.flatMap((x, i) => [`${i + 1}. ${x.title}`, x.text, tag(x.url), ""]),
      ...((w.landed || []).length ? ["― 今週の日本上陸 ―", "", ...w.landed.flatMap((x) => [x.title, x.text, tag(x.url), ""])] : []),
      "このメールは週1回だけ届きます。", `配信の停止: ${unsub}`, "", `Gadget Terminal ${env.SITE}/`,
    ].join("\n");
    const html = `<!doctype html><html lang="ja"><body style="margin:0;background:#f7f7f5"><div style="max-width:600px;margin:0 auto;padding:24px 20px;background:#fff;font-family:system-ui,-apple-system,'Hiragino Sans','Noto Sans JP',sans-serif;color:#1a1a1a">
<p style="margin:0 0 6px;font:600 11px/1 ui-monospace,Menlo,monospace;letter-spacing:.12em;color:#d8452e">GADGET TERMINAL / WEEKLY</p>
<h1 style="margin:0 0 8px;font-size:20px;line-height:1.4">${esc(title)}</h1>
<p style="margin:0 0 10px;font-size:14px;line-height:1.8;color:#555">${esc(w.lead || "")}</p>
<table role="presentation" style="width:100%;border-collapse:collapse">${w.items.map(row).join("")}</table>
${(w.landed || []).length ? `<p style="margin:22px 0 4px;font:700 12px/1 ui-monospace,Menlo,monospace;letter-spacing:.08em;color:#d8452e">今週の日本上陸</p><table role="presentation" style="width:100%;border-collapse:collapse">${w.landed.map(row).join("")}</table>` : ""}
<p style="margin:24px 0 0;font-size:12px;line-height:1.7;color:#888">このメールは週1回だけ届きます。<a href="${esc(unsub)}" style="color:#888">配信の停止</a><br>Gadget Terminal <a href="${esc(env.SITE)}/" style="color:#888">${esc(env.SITE)}</a></p>
</div></body></html>`;
    try {
      await sendMail(env, { to: s.email, subject: `【Gadget Terminal】${title}`, text, html });
      sent++;
    } catch (e) {
      console.error("weekly send failed", e && e.message);
    }
  }
  await env.DB.prepare("INSERT OR REPLACE INTO notified (slug, status, sent_at, sent_count) VALUES (?, ?, ?, ?)")
    .bind(key, "weekly", now(), sent).run();
  console.log(`sendWeekly: ${key} → ${sent} 通`);
}

async function sendMail(env, { to, subject, text, html }) {
  if (!env.RESEND_API_KEY) throw new Error("RESEND_API_KEY が無い");
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { "Authorization": `Bearer ${env.RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify(html ? { from: env.FROM, to: [to], subject, text, html } : { from: env.FROM, to: [to], subject, text }),
  });
  if (!r.ok) throw new Error(`resend ${r.status}: ${(await r.text()).slice(0, 200)}`);
}
