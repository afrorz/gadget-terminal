---
title: 拡張式LEDティッカー「TickrCast」がKickstarter開始、ESP32-S3でスコア・天気・フライト情報を壁に表示
seo_title: TickrCastがKickstarter開始、99ドルから
slug: tickrcast-esp32-led-ticker
keyword: TickrCast
category: weird
date: 2026-09-04
kicker: 米オハイオ州のTickrCastが、ESP32-S3を積んだ拡張式LEDティッカーディスプレイをKickstarterで発売した。スマホを見なくてもスポーツの試合速報や天気、フライト情報を壁に流し続けられるとうたい、目標額5,000ドルを開始40分で達成した。
tags:
- TickrCast
- Kickstarter
- クラウドファンディング
- ESP32
- LEDディスプレイ
x_hook: LEDの電光掲示板を自室の壁に据え置く。スコアも天気もSNSの数字も、スマホを見ずに流しっぱなしにできるという。
deadline: 2026-10-01
embeds: []
images:
- url: "https://tickrcast.com/og-image.jpg"
  caption: 実機のLEDパネル。ロゴ「TickrCast / FOR THE OBSESSED」を表示した状態
- url: "https://tickrcast.com/media/hero-led-poster.png"
  caption: 表示例。eスポーツの決勝戦のスコアと開始時刻を流している
- url: "https://tickrcast.com/media/showcase/02-dashboard.webp"
  caption: 専用アプリの設定画面。明るさ・スクロール速度・プラグインのオンオフを切り替えられる
credit: TickrCast公式サイト
faq:
- q: 日本で買えますか
  a: Kickstarterでの海外発送が前提で、国内正規代理店の取り扱いは確認できていません。専用アプリも英語表記です。
- q: いくらですか
  a: Kickstarterの早期価格でパネル1枚の基本キットが99ドルから、標準の2枚組「Enthusiast」キットが159ドルからです(いずれも掲載時点)。8枚組は699ドル、10枚組は799ドルとされています。
- q: いつ届きますか
  a: 一般の配送予定は2027年2月とされています。ただし最初の50人分は3Dプリント筐体で先行出荷するとしており、正式な射出成形筐体は追加のストレッチゴールが達成された場合に切り替わる計画です。
- q: 何が新しいのですか
  a: ESP32-S3を積んだHUB75 LEDパネルをディジーチェーン(数珠つなぎ)で拡張でき、サーバー側でレンダリングしたスポーツスコア・天気・SNS指標・フライト情報などを常時表示できる点です。30種類以上のプラグインが用意され、サブスクリプションは不要とされています。
alternatives:
- name: Divoom Pixoo-Max ピクセルディスプレイ(楽天市場)
  why: 常時稼働のBluetooth接続LED表示デバイスとして国内から今日購入できる。TickrCastのようなスポーツ速報プラグインではなくドット絵やメッセージ表示が主用途だが、「ネット経由の情報を壁に表示する」という使い方自体は今すぐ試せる。
  url: https://item.rakuten.co.jp/netclickstore-r/4950537466338/
  merchant: rakuten
sources:
- title: TickrCast - An ESP32-S3 HUB75 LED ticker display with server-side rendering and OTA (Crowdfunding)
  url: https://www.cnx-software.com/2026/09/03/tickrcast-esp32-s3-hub75-led-ticker-display-with-server-side-rendering-and-ota/
  publisher: CNX Software
- title: 'TickrCast: The Expandable LED Ticker for the Obsessed by Joseph Capehart'
  url: http://www.kicktraq.com/projects/jcii/tickrcast-the-expandable-led-ticker-for-the-obsessed/
  publisher: Kicktraq
- title: TickrCast — Live scores and esports on your wall
  url: https://tickrcast.com/
  publisher: TickrCast公式サイト
---

米オハイオ州Findlayを拠点とする個人開発者Joseph Capehart氏が、ESP32-S3を核にした拡張式LEDティッカーディスプレイ「TickrCast」をKickstarterで発売した。キャンペーンは2026年9月1日開始、目標額5,000ドルに対して開始から40分足らずで到達し、Kicktraqの記録では掲載時点で9,609ドル(達成率192%)・支援者50人となっている。募集は10月1日まで。

## スペック

| 項目 | 内容 |
| --- | --- |
| コントローラ | ESP32-S3(専用基板)、Wi-Fi制御・Bluetooth LEで初期設定 |
| パネル方式 | HUB75、プラグアンドプレイでディジーチェーン拡張 |
| パネル1枚のサイズ | 約5.2×10.2インチ |
| 価格(早期価格) | 1枚キット99ドル/2枚組「Enthusiast」159ドル/8枚組699ドル/10枚組799ドル |
| 表示内容 | スポーツ速報・eスポーツ・天気・SNS指標・フライト情報など、30種類以上のプラグイン |
| 配送予定 | 一般ロットは2027年2月(予定)、先行50人分は数週間後 |
| 販売形態 | Kickstarter |

サーバー側で描画したコンテンツをパネルに送る方式で、専用アプリからプラグインのオン・オフや明るさ、スクロール速度を切り替えられる。パネルは最小構成の1〜2枚から始めて、公式には10枚以上への拡張も想定しているという。

## 「まだ製品ではない」ことに注意

TickrCastはKickstarterでの募集段階にあり、出資は購入の確約ではない。掲載している調達額・支援者数・達成率はKicktraqで確認した取得時点の値で、その後も変動する。配送予定の「2027年2月」もあくまで計画であり、クラウドファンディング案件に共通する遅延・仕様変更のリスクがある。

実際、TickrCast自身が最上位の10枚組について、テスト中に基板のグラウンド(接地)まわりの不具合を発見したと開示しており、10枚組の支援者にはまず8枚を先行出荷し、残り2枚は改良版基板の検証が済み次第の追加出荷になるとしている。開始直後からハードウェアの問題を公表している点は、クラウドファンディング特有のリスクが実際に起きた例として留意したい。

## 日本から見るとどうか

**技適の確認が取れていない。** TickrCastはWi-FiとBluetooth LEを内蔵する無線機器で、日本国内で使うには技術基準適合証明(技適)が必要になる。Kickstarter経由の個人輸入品が技適を取得しているかは掲載時点で確認できず、公式サイト・キャンペーンページにも記載が見当たらない。技適未取得の無線機を国内で使用すると電波法上の問題になり得るため、購入前に確認が必要な点として明記しておく。

**専用アプリは英語表記。** スクリーンショットで確認できた設定画面はすべて英語で、日本語化の予定は掲載時点で案内されていない。

**似た体験は国内でも今日から。** TickrCastのようなスポーツ速報特化のプラグイン基盤ではないが、ネット経由の情報を常時表示するアンビエントLEDデバイスとしてはDivoomのPixooシリーズが国内の楽天市場から購入できる。技適の懸念なく「壁に情報を表示し続ける」という体験を試したい場合の選択肢になる。
