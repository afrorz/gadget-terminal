---
title: 韓国Soulart「Station」はマーカーレスの全身モーショントラッカー、Kickstarterで目標の158%を集め419ドルから2027年6月出荷予定
seo_title: Soulart Stationは419ドルの全身トラッカー
slug: soulart-station-motion-tracker
keyword: Soulart Station
category: weird
date: 2026-09-24
kicker: 韓国スタートアップのSoulartが、体にマーカーやセンサーを付けずに全身の動きを追える「Soulart Station」をKickstarterで公開した。ToFセンサーとNPUを内蔵し、PCのGPUやクラウド処理を使わずに23関節分の動きを認識する。価格は1台419ドルから、目標額の158%を集めて資金調達中だ。
tags:
  - Soulart Station
  - モーションキャプチャ
  - VTuber
  - Kickstarter
  - クラウドファンディング
x_hook: 体に何も装着せず、部屋の隅に置いた箱1台がNPUで骨格を読み取る。23関節分の動きを10ミリ秒未満で処理し、目標額30万ドルに対しすでに158%を集めた。出荷は2027年6月の予定。
origin: ICN ソウル
deadline: 2026-11-09
embeds:
  - type: youtube
    id: q6hMoRqJrEM
images:
  - url: "https://framerusercontent.com/images/kFxrGIrQQAKdZDO7aDKyu6Lg40.png?width=960&height=540"
    caption: Soulart Station本体の正面。上部にステータス用の光点、中央にToFセンサーとレンズ、下部に六角形のロゴを配置する
    credit: Soulart公式サイト(soul.art)
  - url: "https://framerusercontent.com/images/vQCDBVHvqCt7gC6MAmSbWNvAig.jpg"
    caption: 暗所に置かれた本体のイメージ。正面上部の光点だけが浮かび上がる
    credit: Soulart公式サイト(soul.art)
alternatives:
  - name: ソニー mocopi(Amazon.co.jp)
    why: 体に6個の小型センサーを装着するマーカー式のモーションキャプチャで、Soulart Stationのようなマーカーレスではないが、VTuber・VR用途で国内から今日購入でき、技適取得済みのソニー製品として使える。
    url: https://www.amazon.co.jp/Sony-QMSS1-USCXA-3D%E3%83%A2%E3%83%90%E3%82%A4%E3%83%AB%E3%83%A2%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3%E3%82%AD%E3%83%A3%E3%83%97%E3%83%81%E3%83%A3-VR%E3%81%A83D%E3%82%B3%E3%83%B3%E3%83%86%E3%83%B3%E3%83%84%E4%BD%9C%E6%88%90%E7%94%A8/dp/B0D9R3YVZ6
    merchant: amazon
faq:
  - q: 日本で買えますか
    a: Kickstarterでの支援という形になり、通常の販売ではありません。日本への発送に対応するか、送料がいくらになるかは掲載時点の情報源からは確認できていません。
  - q: 技適は取得していますか
    a: まだ製品ではなく出荷前の段階のため、技適の取得状況は確認できていません。無線機能の有無を含めた詳細スペックも掲載時点では未確認です。
  - q: いくらですか
    a: Kickstarterでの支援額は1台419ドルから、2台セットが799ドル、8台セットが2,850ドルです(いずれも掲載時点、送料別)。
  - q: いつ発売されますか
    a: Kickstarterのページでは2027年6月の出荷を予定しているとしていますが、クラウドファンディングであり確定した日程ではありません。
sources:
  - title: "Soulart Station: The First Markerless Tracker for You by Soulart"
    url: https://www.kickstarter.com/projects/soulart-corp/soulart-station-the-first-markerless-tracker-for-you
    publisher: Kickstarter(Kicktraq経由で集計値を確認)
  - title: Soulart Station – A markerless full-body motion tracker for VR and VTubers (Crowdfunding)
    url: https://www.cnx-software.com/2026/09/23/soulart-station-a-markerless-full-body-motion-tracker-for-vr-and-vtubers/
    publisher: CNX Software
  - title: Soulart(公式サイト)
    url: https://soul.art/
    publisher: Soulart Corp
---

**まだ製品ではない。** 韓国のスタートアップSoulartが、体にマーカーやセンサーを一切付けずに全身の動きを追跡できる「Soulart Station」をKickstarterで公開した。現在も資金調達中で、目標額30万ドルに対し掲載時点で47万4,451ドル(158%)を集め、支援者は371人。出荷は2027年6月を予定しているが、クラウドファンディングである以上、遅延や仕様変更は起こり得る。

## PCのGPUもクラウドも使わない

Soulart Stationは940nm帯のカスタムToF(Time of Flight)センサーと4K RGB/NIRカメラを内蔵し、最大120Hzで点群データを取得する。特徴は、この点群からの骨格推定をステーション内蔵のデュアルコアNPUだけで完結させる点で、PC側のGPUやクラウド処理を必要としないという。結果として23関節分の6自由度(6DoF)モーションデータを、ML処理の遅延10ミリ秒未満で出力できるとしている。ステーションを複数台設置すればToF同士の干渉を打ち消しながら追跡範囲を広げられ、想定用途はVRゲーム、VTuber配信、モーションキャプチャ制作など。出力形式はVMC・OSC・BVHに対応し、VTube Studio、Warudo、VBridger、Unity、Unreal Engine、Blender、Maya、MotionBuilder、ROS2との連携をうたう。対応OS/プラットフォームはWindows、Meta Quest、Android XR。

創業したのはKAIST(韓国科学技術院)の情報科学出身であるOh Hyuk-jae氏(CEO)とJeon Da-eum氏(COO)。Oh氏は兵役中に着想を得て開発を始めたとされ、Mashup Venturesからシード資金を調達している。

## スペック・価格(Kicktraq・CNX Softwareより)

| 項目 | 内容 |
| --- | --- |
| センサー | 940nm帯ToF、4K RGB/NIRカメラ |
| 処理 | オンボードのデュアルコアNPU(PC・クラウド不要) |
| 追跡性能 | 23関節・6DoF、ML遅延10ミリ秒未満、最大120Hz |
| 連携ソフト | VTube Studio、Warudo、VBridger、Unity、Unreal Engine、Blender、Maya、MotionBuilder、ROS2 |
| 対応OS | Windows、Meta Quest、Android XR |
| 価格(1台) | 419ドル(送料別、掲載時点) |
| 価格(2台セット) | 799ドル(送料別、掲載時点) |
| 価格(8台セット) | 2,850ドル(送料別、掲載時点) |
| 調達額 | 47万4,451ドル(目標30万ドルの158%、掲載時点) |
| 支援者数 | 371人(掲載時点) |
| 締切 | 2026年11月9日(掲載時点でキャンペーンは進行中) |
| 出荷予定 | 2027年6月 |

## 日本から見るとどうか

**まだ製品ではない。** Kickstarterでの支援は購入の確約ではなく、目標額を大きく上回っているとはいえ、開発中のハードウェアである以上、出荷までに仕様変更や遅延が起きる可能性は残る。調達額・支援者数は掲載時点の値で、締切の2026年11月9日まで変動する。

**技適・日本への発送はいずれも確認できていない。** Soulart StationはToFセンサーとカメラを使う機器で、無線での連携機能があるかどうかを含め、詳細な通信仕様は参照した情報源からは確認できなかった。Kickstarterでの発送は米国向けの送料しか案内されておらず、日本への発送可否や送料は掲載時点で不明。

**マーカー式でよければ、国内に技適取得済みの選択肢がある。** ソニーの「mocopi」は体に6個の小型センサーを装着するマーカー式のモーションキャプチャで、Soulart Stationが売りにする「マーカーレス」ではない。ただし同じVTuber・VR用途で国内から今日購入でき、日本語サポート・技適取得済みという点でリスクは小さい。マーカーレスの利点(装着の手間がない)を優先するか、確実に国内で使える製品を選ぶかは、用途次第で判断が分かれる。

情報源はKickstarter(集計値はKicktraq経由で確認)、CNX Software、Soulart公式サイトの3件。調達額・支援者数・締切はいずれも掲載時点の値。
