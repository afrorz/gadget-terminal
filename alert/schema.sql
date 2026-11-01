-- 日本上陸アラートの表。npx wrangler d1 execute gt-alert --remote --file schema.sql
-- 登録。1行 = メールアドレス × 記事(slug)。token は確認・解除のリンクに使う
CREATE TABLE IF NOT EXISTS subscriptions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL,
  slug TEXT NOT NULL,
  token TEXT NOT NULL UNIQUE,
  ip_hash TEXT,
  created_at TEXT NOT NULL,
  confirmed_at TEXT,
  unsubscribed_at TEXT,
  notified_at TEXT,
  UNIQUE (email, slug)
);
CREATE INDEX IF NOT EXISTS idx_subs_slug ON subscriptions (slug);
CREATE INDEX IF NOT EXISTS idx_subs_created ON subscriptions (created_at);

-- 上陸を知らせ終えた記事。1記事1回だけ送る
CREATE TABLE IF NOT EXISTS notified (
  slug TEXT PRIMARY KEY,
  status TEXT NOT NULL,
  sent_at TEXT NOT NULL,
  sent_count INTEGER NOT NULL DEFAULT 0
);
