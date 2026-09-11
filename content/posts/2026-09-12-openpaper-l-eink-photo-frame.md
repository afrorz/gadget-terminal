---
title: ベンダーのクラウドに繋がないオープンソースのカラー電子ペーパー額縁「OpenPaper L」、13.3インチで339ユーロ
seo_title: OpenPaper Lは339ユーロ、13.3インチE Ink
slug: openpaper-l-eink-photo-frame
keyword: OpenPaper L
category: weird
date: 2026-09-12
kicker: ドイツのpaperlesspaperが、オープンソースのカラー電子ペーパー(E Ink Spectra 6)を使った13.3インチのデジタル額縁「OpenPaper L」を339ユーロで発売した。メーカーのクラウドサーバーに接続しなくても動作するオフラインモードを備え、Home Assistantなどとの連携もできる。
tags:
- OpenPaper
- paperlesspaper
- E Ink
- 電子ペーパー
- オープンソース
x_hook: 電源を切っても表示が消えない額縁が、メーカーのクラウドに一切接続しなくても動くように作られている。単3電池4本で半年持つ13.3インチのカラー電子ペーパーに天気やGoogleカレンダーも映せるオープンソース仕様で、価格は339ユーロから。
images:
- url: "https://paperlesspaper.de/_next/image?url=%2F_next%2Fstatic%2Fmedia%2FIMG_5966-Bearbeitet-12b.ed282640.jpg&w=3840&q=75"
  caption: 自転車のイラストを表示した状態。木製フレームと白いマットが公式サイトに明記された素材と一致する
- url: "https://media.paperlesspaper.de/t/c_limit,w_868,h_1302,f_jpg,q_auto/paperlesspaper-website/IMG_5808-Bearbeitet.jpg"
  caption: 情報ダッシュボードとして使った状態。曜日・日付・その日の予定を表示している
- url: "https://media.paperlesspaper.de/t/c_limit,w_868,h_579,f_jpg,q_auto/paperlesspaper-website/IMG_5761-Bearbeitet.jpg"
  caption: 抽象画を表示した状態。木製フレームに壁掛けで設置している
credit: paperlesspaper 公式サイト
status: LANDED
status_note: 公式サイトで受注中、14日程度で発送(日本への配送可否は要確認)
faq:
- q: 日本で買えますか
  a: 公式サイト(paperlesspaper.de)は欧州向けの配送を中心に案内しており、日本への発送に対応しているかどうかは掲載時点で確認できていない。
- q: 技適は取得していますか
  a: Wi-Fi 6とBluetooth Low Energyを搭載しているが、日本の技術基準適合証明(技適)を取得しているかどうかは公式情報から確認できていない。
- q: いくらですか
  a: 掲載時点で339ユーロ(通常価格359ユーロから20ユーロの割引価格)。
- q: 電源はどうなっていますか
  a: 単3形電池4本(ニッケル水素充電池も使用可)またはUSB-C給電に対応する。1日1回の更新であれば、電池で約6か月動作するとしている。
sources:
- title: "13-inch eInk picture frame"
  url: https://paperlesspaper.de/en/openpaper-l
  publisher: paperlesspaper
- title: "OpenPaper L Launches as a 13.3-Inch Open-Source Color E-Ink Frame"
  url: https://linuxiac.com/openpaper-l-launches-as-a-13-3-inch-open-source-color-e-ink-frame/
  publisher: Linuxiac
---

ドイツのスタートアップpaperlesspaperが、13.3インチのカラー電子ペーパー額縁「OpenPaper L」を339ユーロ(通常359ユーロから20ユーロ割引の掲載時点価格)で発売した。オープンソースの小型モデル「Paper 7」の後継にあたる大型版で、メーカーのクラウドサーバーに一切接続しなくても動作するオフラインファームウェアを選べる点が最大の特徴だ。

## スペックと使い方

ディスプレイにはE Ink Spectra 6を採用し、解像度は1600×1200(150ppi)、表示エリアは200×268mm。フレームはナチュラルウッド・ブラック・ホワイトの3種類から選べ、反射を抑えるUV70ミュージアムガラスを使う。電源は単3形電池4本(ニッケル水素充電池も使用可)またはUSB-C給電に対応し、1日1回の更新であれば電池だけで約6か月動作するという。通信はWi-Fi 6とBluetooth Low Energyに対応し、スマートフォンアプリはAndroid 15以降・iOS 18以降で動く。

## クラウド不要のオープンソース仕様

一般的なデジタルフォトフレームの多くはメーカーのクラウドサービスを介して画像を配信するが、OpenPaper Lはオプションのオフラインファームウェアを使うことで、インターネット接続やpaperlesspaperのサーバーへの接続なしにローカルネットワーク上だけで完結させられる。画像はBluetooth経由か、ローカルURLからの取得で表示する仕組みだ。Home Assistant・Googleカレンダー・RSSフィード・天気・ウェブサイト・Immich(自前ホスト型の写真管理ソフト)との連携にも対応しており、単なる写真立てではなく簡易的な情報ダッシュボードとしても使える設計になっている。

## 日本から見るとどうか

OpenPaper Lが搭載するWi-Fi 6とBluetooth Low Energyのモジュールについて、日本の技術基準適合証明(技適)を取得しているかどうかは公式情報から確認できていない。ドイツの小規模スタートアップが欧州向けに展開している製品であるため、日本向けの認証を取得している可能性は高くないとみられる。配送についても、公式サイトの案内は欧州域内が中心で、日本への発送に対応するかどうかは明記されていない。購入を検討する場合は、事前に公式サイトへ問い合わせて配送可否と技適の扱いを確認する必要がある。

同じくE Ink Spectra 6パネルを使ったDIYキットとして、Raspberry Pi Pico向けの7.3インチ「Waveshare PhotoPainter」のような製品もあるが、これは組み立てが前提の小型キットであり、完成品として届く13.3インチのOpenPaper Lとは製品としての性格が異なる。国内で技適を取得した同等品は見当たらず、今すぐ国内で買える直接の代替品は無いのが実情だ。
