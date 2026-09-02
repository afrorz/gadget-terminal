---
title: Seeed Studioの電子ペーパー付箋「reTerminal Sticky」が49.90ドルで予約開始、ファームウェア書き換えで電子書籍リーダーにもなる
seo_title: reTerminal Stickyが50ドルで予約開始
slug: seeed-reterminal-sticky
keyword: reTerminal Sticky
category: weird
date: 2026-09-03
kicker: 深圳のSeeed Studioが、3.97インチの電子ペーパーを使った小型ガジェット「reTerminal Sticky」の予約受付を自社ストアで始めた。標準ではWi-Fi経由で時計・天気・メモを表示する「デジタル付箋」として動作するが、ファームウェアを書き換えれば電子書籍リーダーにもなる。価格は49.90ドルで、出荷は2026年9月中旬を予定する。
tags:
- Seeed Studio
- reTerminal Sticky
- 電子ペーパー
- E Ink
- 自作ガジェット
x_hook: 冷蔵庫に貼る付箋が、ファームウェアを書き換えると電子書籍リーダーに変わる。
origin: SZX 深圳
images:
- url: "https://media-cdn.seeedstudio.com/media/catalog/product/1/0/100056818-gallery_img_1_1.jpg"
  caption: 壁面に複数台を並べた使用例。時計、公式ロゴ画面、天気、メモとそれぞれ違う内容を表示できる
- url: "https://media-cdn.seeedstudio.com/media/catalog/product/1/0/100056818-gallery_img_2_1.jpg"
  caption: ホーム画面のクローズアップ。Settings/Clock/Note/Weather/AI Usageのアイコンとバッテリー残量84%表示、下部にUSB-Cポートが見える
credit: Seeed Studio公式製品ページ
faq:
- q: 日本で買えますか
  a: 掲載時点でSeeed Studio公式ストアからの海外発送が前提で、国内正規代理店の取り扱いは確認できていません。
- q: いくらですか
  a: 49.90ドルです(10個以上のまとめ買いは47.90ドル、いずれも掲載時点)。
- q: いつ発売されますか
  a: 予約受付中で、出荷は2026年9月中旬を予定しています(掲載時点の案内)。
- q: 電子書籍リーダーとして使えますか
  a: 標準ファームウェアはメモ・時計・天気表示用ですが、コミュニティ製ファームウェア「CrossPoint Reader」に書き換えることで電子書籍リーダーとしても使えるとSeeed Studioは説明しています。
alternatives:
- name: SwitchBot スマートデイリーステーション(楽天市場)
  why: 同じ電子ペーパーで天気・予定・メモをまとめて表示するWi-Fi対応スマートディスプレイ。画面は7.5インチとより大きく、reTerminal Stickyのようなファームウェア書き換えはできないが、国内正規品として今日から購入・サポートを受けられる。
  url: https://item.rakuten.co.jp/switchbot/weather-station/
  merchant: rakuten
sources:
- title: 'Lilbits: More phone-sized E Ink gadgets'
  url: https://liliputing.com/lilbits-more-phone-sized-e-ink-gadgets/
  publisher: Liliputing
- title: reTerminal Sticky product page
  url: https://www.seeedstudio.com/reTerminal-Sticky-p-6861.html
  publisher: Seeed Studio
- title: CrossPoint Reader documentation
  url: https://www.seeedstudio.com/sticky/docs/en/playground-docs/crosspoint-reader/
  publisher: Seeed Studio
---

深圳のSeeed Studioが、手のひらサイズの電子ペーパーガジェット「reTerminal Sticky」の予約受付を自社ストアで開始した。同社のIoT端末シリーズ「reTerminal」の派生モデルで、名前の通り「付箋(Sticky note)」のように壁や冷蔵庫に貼って使うことを想定する。Wi-Fi経由でSeeedashアプリからリモートで表示内容を書き換えられ、時計・天気・メモといった情報を切り替えて表示できる。価格は49.90ドル、出荷は2026年9月中旬を予定する。

## スペック

| 項目 | 内容 |
| --- | --- |
| 画面 | 3.97インチ電子ペーパー、800×480、235ppi、4階調グレースケール |
| バッテリー | 750mAh |
| 接続 | Wi-Fi(2.4GHz)、USB-C(充電・データ) |
| 管理方法 | Seeedashアプリでのリモート表示更新 |
| ファームウェア | 標準ファームウェアに加え、コミュニティ製「CrossPoint Reader」への書き換えに対応 |
| 価格 | 49.90ドル(10個以上は47.90ドル、いずれも掲載時点) |
| 出荷予定 | 2026年9月中旬(予定) |
| 販売形態 | Seeed Studio公式ストアでの予約受付 |

標準状態では時計・天気予報・手書き風メモといった画面を切り替えて表示する「デジタル付箋」として使う設計だが、Seeed Studioはファームウェアの書き換えを前提としたオープンな設計を取っており、コミュニティが開発した電子書籍リーダー用ファームウェア「CrossPoint Reader」を書き込むことで、低消費電力の電子ペーパー端末として長文を読む用途にも転用できるとしている。

## 日本から見るとどうか

**掲載時点でSeeed Studio公式ストアからの海外発送が前提で、国内正規代理店の取り扱いは確認できていない。** Seeed Studio自体は開発ボードなどで日本の自作・電子工作コミュニティにもなじみのある企業だが、reTerminal Sticky個別の国内発送や日本語対応は参照した情報だけでは確認できなかった。

**Wi-Fi機器のため技適が論点になる。** 2.4GHz帯のWi-Fiを搭載しており、国内で電波を発する状態で使うには技適の取得が前提になる。掲載時点でreTerminal Stickyの技適取得状況は確認できていない。価格はドル建てで、円換算額は為替により変動する。

**似た使い方をすぐ試したいなら。** ファームウェア書き換えによる拡張性こそ無いが、電子ペーパーで天気やカレンダーをまとめて表示するという発想そのものは、国内正規品のSwitchBot スマートデイリーステーションで今日から体験できる。画面サイズは7.5インチとひとまわり大きく、価格帯も異なるため、用途に応じて選びたい。
