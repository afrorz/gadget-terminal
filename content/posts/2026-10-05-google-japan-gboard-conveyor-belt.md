---
title: "Google Japanの「Gboard くるくるバージョン」は、116個のキーがベルトで指先へ流れてくる。3Dプリントと基板データは公開済み"
seo_title: "Gboardくるくる版は116キーが動く、自作できる？"
x_hook: "Google Japanが10月1日に出した新しいGboardは、4本のベルトに並んだ116個のキーが手元へ流れてくる。製品としては売らず、3Dデータと基板、ファームを公開した。"
slug: google-japan-gboard-conveyor-belt
keyword: Gboardくるくる
category: weird
date: 2026-10-05
kicker: Google Japanが2026年10月1日に公開した「Gboard Conveyor Belt Version」（日本語名はくるくるバージョン）は、4本のコンベアベルトに計116個のキーを載せ、キーのほうが指へ動いてくるキーボード。販売はせず、3Dプリント用STL・基板・ファームウェアをGitHubで公開している。
tags: [Google, Gboard, キーボード, 3Dプリント, 自作, 変わり種]
origin: NRT 東京
images:
  - url: "https://raw.githubusercontent.com/google/mozc-devices/main/mozc-conveyorbelt/images/conveyorbelt.webp"
    caption: 完成形。青いフレームを立てかけ、白いキートップが縦に並ぶ。下端にローラーが見える
  - url: "https://raw.githubusercontent.com/google/mozc-devices/main/mozc-conveyorbelt/images/diy.webp"
    caption: 組み立て前の部品。キースイッチを並べたベルト4本、スプロケット、フレキ基板などが机に広がる
credit: Google Japan（GitHub google/mozc-devices）
embeds:
  - type: youtube
    id: DAn34l_YrUM
    caption: Google Japan公式の紹介動画「Gboard くるくるバージョン」
faq:
  - q: 買えますか
    a: 完成品の販売は報じられていません。Tom's Hardwareなどは販売予定なしと伝えており、公開されているのは3Dデータ・基板・ファームウェアです。自分で作る前提です。
  - q: 何個のキーがありますか
    a: ベルトは4本で、1本に29個、合計116個です。ビルドガイドの部品表でも、キースイッチとキーキャップは116個です。
  - q: 日本で部材は揃いますか
    a: ビルドガイドの部品表には、Amazon.co.jp、スイッチサイエンス、遊舎工房の商品ページが参照先として並んでいます。掲載時点で、国内で揃える前提の構成です。
  - q: Googleの公式製品ですか
    a: いいえ。リポジトリには「not an official Google product」と明記されています。
sources:
  - title: Gboard Conveyor Belt Version（README）
    url: https://github.com/google/mozc-devices/tree/main/mozc-conveyorbelt
    publisher: Google / GitHub
  - title: Build Guide
    url: https://github.com/google/mozc-devices/blob/main/mozc-conveyorbelt/buildguide.md
    publisher: Google / GitHub
  - title: Conveyor Belt GBoard Brings The Keys To You
    url: https://hackaday.com/2026/10/05/conveyor-belt-gboard-brings-the-keys-to-you/
    publisher: Hackaday
---

**Gboard Conveyor Belt Version** は、キーのほうが指へ動いてくるキーボードだ。4本のコンベアベルトに計116個のキーが載り、モーターでベルトが回る。手や腕を動かさず、目当てのキーが流れてくるのを待って押す設計になっている。Google Japanが2026年10月1日に公開した。日本語の動画タイトルは「Gboard くるくるバージョン」。

Googleの公式製品ではなく、報道によれば売る予定もない。リポジトリ（google/mozc-devices）に3Dプリント用のSTL、KiCadの基板データ、ファームウェアが置かれ、読者が自分で作る形をとっている。

## 仕組みと構成

| 項目 | 内容 |
| --- | --- |
| ベルト | 4本。1本に29個、計116個のキー |
| キースイッチ | Kailh Choc V1 ロープロファイル、116個 |
| 駆動 | DC6V N20 メタルギアモーター（150RPM）、モータードライバ DRV8833 |
| 制御 | ATOMS3 Lite |
| 3Dプリント部品 | 18種、合計157個。ベルトの1コマだけで116個 |
| 公開物 | STL、基板データ、ファームウェア（ビルド済みバイナリ付き） |

ファームウェアのビルド済みバイナリは、USBケーブルをつないだままブートスイッチを押して書き込む手順になっている。

実物の写真では、青いフレームを斜めに立てかけ、白いキートップが縦に流れる向きに並ぶ。机に平置きするキーボードとは別の形だ。

## 注意点

ビルドガイドは、基板まわりの資料を「Coming soon」としている。Bluetooth接続版も同じく「Coming soon」で、現時点で組めるのは、ベルトが動く「Moving Keys Edition」のほうだ。

Hackadayは、公開されたソースコードは完全ではないように見えると書いている。同誌はジョーク企画の可能性にも触れている。実際に打てる状態まで組めるかは、こちらでは確認できていない。

Google Japanは毎年10月1日に、風変わりなキーボードを公開してきた。Hackadayは過去の例として、帽子型と回転式の電話型を挙げている。

## 日本から見るとどうか

作るなら、日本のほうが有利な題材だ。ビルドガイドの部品表は、Amazon.co.jp、スイッチサイエンス（ATOMS3 Lite）、遊舎工房（Kailh Choc V1のスイッチとキーキャップ）の商品ページを参照先にしている。海外から取り寄せる前提ではない。

技適やPSEの扱いは、完成品を売らないため購入者の問題にはならない。自分で組む場合、使う基板が無線機能を持つなら、その電波の扱いは組み立てた人が確認する必要がある。ビルドガイドが書いているのは、ファームウェアをUSB経由で書き込む手順までで、無線部分についての記述は確認できていない。

次に取れる行動は2つ。3Dプリンターがあるなら、まずビルドガイドとSTLを見て、116個のベルト部品を印刷できるか確かめる。組み立てる気がないなら、公式動画で動きだけ見るのが早い。実用の入力装置としては、キーが流れてくるのを待つ分だけ遅くなるはずで、日常使いの代替品にはならない。
