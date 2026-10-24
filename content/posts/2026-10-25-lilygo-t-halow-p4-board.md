---
title: LILYGO「T-Halow P4」、ESP32-P4にWi-Fi HaLowを載せたM.2サイズの開発ボード。26.57ドルで920MHz版もある
slug: lilygo-t-halow-p4-board
seo_title: LILYGO T-Halow P4は26.57ドル、920MHz版も
x_hook: |
  数百メートル先まで届く無線を、SSDのサイズに詰めた基板。
  LILYGO「T-Halow P4」は、ESP32-P4とWi-Fi HaLowを80×22mmに載せた開発ボード。日本の帯域に合う920MHz版もある。
  ・カメラとAMOLEDの端子つき
keyword: T-Halow P4
category: pc
date: 2026-10-25
kicker: 中国・深圳のLILYGOが、ESP32-P4とWi-Fi HaLow（802.11ah）モジュールを載せた開発ボード「T-Halow P4」を公式ストアで売っている。80×22mmのM.2 2280サイズの基板に、Wi-Fi 6とBluetooth LE用のESP32-C6、カメラとAMOLEDの端子を載せ、価格は26.57ドル。周波数は915MHz・868MHz・920MHzの3種類から選べる。
tags:
- LILYGO
- T-Halow P4
- ESP32-P4
- Wi-Fi HaLow
- 開発ボード
giteki:
  status: 確認できない
  number: []
  checked: 2026-10-25
  radio: Wi-Fi HaLow / Wi-Fi 6 / Bluetooth LE
  note: "総務省DBに「T-Halow」(211-241018、Shenzhen Xin Yuan Electronic Technology)があるが、このボードの各版との対応は確認できない"
images:
- url: "https://lilygo.cc/cdn/shop/files/T-Halow-P4-LILYGO_8.jpg"
  caption: 基板の表裏。表にHaLowモジュールとESP32-C6、ESP32-P4、USB-C。裏にカメラとAMOLEDのコネクタ
- url: "https://lilygo.cc/cdn/shop/files/T-Halow-P4-LILYGO_6.jpg"
  caption: SMAコネクタ付きの外付けアンテナをつないだ状態
- url: "https://lilygo.cc/cdn/shop/files/T-Halow-P4-LILYGO_7.jpg"
  caption: 寸法は長さ80mm、幅22mm、厚さ5mm
credit: LILYGO 公式製品ページ
sources:
- title: T-Halow P4（LILYGO公式ストア。価格・版は2026年10月25日時点）
  url: https://lilygo.cc/products/t-halow-p4
  publisher: LILYGO（公式）
- title: LILYGO T-Halow-P4（公式ウィキ）
  url: https://wiki.lilygo.cc/get_started/en/High_speed/T-Halow-P4/T-Halow-P4.html
  publisher: LILYGO（公式）
alternatives:
  - name: M5Stack Tab5（ESP32-P4搭載のIoTコントローラー）
    why: 同じESP32-P4とESP32-C6の組み合わせを、5インチのタッチ画面とカメラ付きの完成品として国内で買える。HaLowは載らないが、P4の開発は今日から始められる。
    url: https://item.rakuten.co.jp/zmart-shop/3458/
    merchant: rakuten
    image: "https://thumbnail.image.rakuten.co.jp/@0_mall/zmart-shop/cabinet/25/3458-1.jpg"
faq:
- q: T-Halow P4とは何ですか
  a: LILYGOが売るESP32-P4搭載の開発ボードです。Wi-Fi HaLow（802.11ah）モジュールとESP32-C6を載せ、カメラとAMOLEDの端子があります。
- q: いくらですか
  a: LILYGO公式ストアで26.57ドルです。カメラモジュール（OV2710）を足す選択肢もあります（2026年10月25日時点）。
- q: 日本の周波数に合いますか
  a: 920MHzの版（型番H777-01）が用意されています。ただし技適は確認できていません。
- q: 日本で買えますか
  a: 日本語の販売ページは見つかっていません。公式ストアから国際配送で買えますが、掲載時点でページに在庫切れの表示がありました。
---

中国・深圳のLILYGOが、ESP32-P4とWi-Fi HaLowを載せた開発ボード「T-Halow P4」を公式ストアで売っている。価格は26.57ドル。HaLowは、省電力で遠くまで届くことを狙った802.11ahの規格で、Wi-Fiの2.4GHz・5GHzより低いサブGHz帯を使う。掲載時点で、ストアのページには在庫切れの表示が出ていた。

## 載っているもの

| 項目 | 内容 |
|---|---|
| メインのチップ | ESP32-P4（フラッシュ16MB、PSRAM 8MB） |
| 無線 | ESP32-C6でWi-Fi 6とBluetooth LE、HaLowモジュールでサブGHz |
| 映像 | MIPIのカメラとディスプレイ（AMOLED）の端子。H.264 1080P/30fpsに対応 |
| 開発環境 | Arduino IDE、VS Code、ESP-IDF |
| 寸法 | 80×22×5mm（M.2 2280サイズ） |
| 端子 | USB-C、SMAのアンテナ端子 |

HaLowのモジュールは3つの版から選ぶ。915MHz版、868MHz版、920MHz版で、カメラモジュール（OV2710）も別に付けられる。ストアのページは、先代のT-Halow（ESP32-S3ベース）と同じATコマンドを使うとしている。製造元のLILYGOは中国・深圳の会社で、開発者向けの基板を多く出している。

M.2 2280のサイズと金色の端子の形をしているが、PCのM.2スロットに挿して使えるとはストアのページに書かれていない。USB-Cで給電し、基板上のピンで拡張する開発ボードとして読むのが無難だ。

## 日本で買える？使える？

日本語の販売ページや紹介記事は、掲載時点で見つかっていない。LILYGO公式ストアは国際配送で、DHLやFedExなら7〜10営業日、通常便なら10〜25営業日とされる。日本向けの正規代理店は確認できていない。

**注目点は920MHz版があること。** 日本のHaLowは920MHz帯を使うため、日本で使うなら合うのはこの版になる。一方、915MHzと868MHzは日本の帯域に合わず、技適がない状態で電波を出せば電波法違反になる。

技適については、総務省のデータベースに「T-Halow」という型式の認証が1件ある（番号211-241018、申請者はShenzhen Xin Yuan Electronic Technology）。ただし、このボードの3つの版がその認証と同じ物かは確認できない。基板上のモジュールには、日本の技適マークのような表示がある写真もあるが、915MHz版の写真とみられ、番号の読み取りも確かではない。ボードに載るESP32-C6のWi-Fi 6とBluetoothも、国内で使うなら別の確認が要る。

届いたらすぐ電波を出す前に、使う版と技適の対応を確かめるのが先だ。ESP32-P4そのものを国内で試したいなら、M5StackのTab5のように国内の店で買える完成品がある。ただしHaLowは載っていない。HaLowの実験をしたい人は、920MHz版の購入前に技適の確認を取りたい。
