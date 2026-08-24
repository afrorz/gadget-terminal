# 記事にしたいネタの置き場

思いついた製品の URL をここに書いておくと、**毎晩 23:00 の自動実行が
自分でネタを探す前に、ここを上から消化します。**

## 書き方

`## 未処理` の下に `- ` で始まる行として URL を足すだけです。
スマホの GitHub アプリからでも編集できます。

    - https://www.kickstarter.com/projects/xxxx/yyyy
    - https://example.com/product  ← 一言メモを書いてもいい

URL の後ろに書いたメモは、記事の切り口の指示として読まれます。
「日本での入手性を厚めに」のような注文があれば書いてください。

## 「編集部ピックアップ」になります

**ここから書かれた記事は、トップページの「編集部ピックアップ」に載ります。**
自動で選ばれた記事と区別するためで、front matter に `pick: true` が付きます。

さらに、`> ` で始まる行を足すと、**その文がそのまま記事に載ります。**

    - https://example.com/product
      > フレットが光って運指を教えるという発想が面白い。

この一文は要約も改変もされません。**あなたが書いた文章がそのまま出ます。**

短くていいので書く価値があります。この媒体で唯一、人間が書いた部分になるためです。
競合は実名のライターが実機を触って書いており、そこが向こうの強みです。
こちらが同じ土俵に立てる最小の形が、この一文です。

## 日付を指定する

行の先頭に `[YYYY-MM-DD]` を付けると、**その日まで書かれません。**

    - [2026-08-24] https://example.com/product

発売日や締切に合わせたいとき、あるいは今日の3本に割り込ませたくないときに使います。
日付を付けない行は、次の実行で普通に消化されます。

## ルール

- 1回の実行で消化するのは最大3本（1日の記事数と同じ）
- 記事になった行は `## 処理済み` に移動します。**手で消さなくていい**
- 記事にできなかった場合（元記事が消えている等）は `## 保留` に理由付きで移ります
- 3本を超えて積んでも消えません。翌日以降に持ち越されます

## 今すぐ書かせたいとき

Actions タブ →「毎朝の記事下書きを作って公開」→ Run workflow →
`url` 欄に URL を貼って実行すると、その場で記事になります。

ただし**これは Claude の利用枠を即座に消費します。**
昼間にローカルで作業しているときは、ここに積んで夜に回すほうが安全です。

---

## 未処理

## 処理済み

- 2026-08-24 https://www.makuake.com/project/calorc1/ → content/posts/2026-08-24-calor-c1-makuake.md
- 2026-08-23 https://www.indiegogo.com/projects/hoverair/versa-this-pocket-camera-can-fly → content/posts/2026-08-23-hoverair-versa-indiegogo.md
- 2026-08-23 https://www.kickstarter.com/projects/litejam/litejam-neo-a1-the-worlds-first-rgb-acoustic-guitar → content/posts/2026-08-23-litejam-neo-acoustic-a1.md

## 保留

- https://www.kickstarter.com/projects/nimbopearl/nimbo-x1-worlds-lightest-sic-color-display-ar-glasses — KickstarterのページがCloudflareのボット対策で終始403を返し、curl（ブラウザUA）・WebFetch・r.jina.ai経由のいずれでも本文を取得できず。数値（調達額・支援者数など）の裏取りができないため見送り。次回実行時に取得できれば再挑戦する。
