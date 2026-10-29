---
title: LILYGO「T-Display K230」、RISC-VのLinux機に4.1インチAMOLEDとLoRaを載せた手のひらサイズの開発キット。単体98.79ドル、キーボード付きは別売
slug: lilygo-t-display-k230
seo_title: LILYGO T-Display K230は98.79ドル
x_hook: |
  キーボードを付けると、LoRaつきの小さなLinux機になる。
  LILYGO「T-Display K230」は4.1インチAMOLEDにRISC-VのK230を載せた開発機。キーボードは別売で、LTE-Mの版もある。
  ・本体のみ98.79ドル（約1万5千円）
keyword: T-Display K230
category: pc
date: 2026-10-30
kicker: 中国・深圳のLILYGOが、Canaan製のRISC-V SoC「Kendryte K230」を載せた手のひらサイズの開発キット「T-Display K230」を公式ストアで売っている。4.1インチのAMOLEDタッチ画面、LoRa、HDMI、Ethernet、2MPカメラを備え、基板のみ98.79ドル、ケース付きキットは約150ドル。
tags:
- LILYGO
- T-Display K230
- RISC-V
- LoRa
- 開発ボード
origin: SZX 深圳
giteki:
  status: 確認できない
  number: []
  checked: 2026-10-30
  radio: Wi-Fi 4 / Bluetooth LE / LoRa
  note: "型番の技適は確認できない。LoRaは868/915/923MHzと830〜940MHzの2種"
images:
- url: "https://lilygo.cc/cdn/shop/files/LILYGO-T-DISPLAY-K230-KIT_12.jpg?v=1785985215&width=1920"
  caption: ケース付きキットの表（ホーム画面）と裏。背面にカメラ、ファン、40ピンのGPIOヘッダが見える
- url: "https://lilygo.cc/cdn/shop/files/LILYGO-T-DISPLAY-K230-KIT_9.jpg?v=1785985214&width=1946"
  caption: カメラ部を持ち上げた状態。画面にはカメラ、LoRa、BLEなどのアプリのアイコンが並ぶ
- url: "https://lilygo.cc/cdn/shop/files/LILYGO-T-DISPLAY-K230-KIT_3.png?v=1785985214&width=1920"
  caption: 別売のバックライト付きQWERTYキーボード。表側（上）と背面（下）。背面に三脚ネジ用の穴とクリップがある
credit: LILYGO 公式製品ページ
sources:
- title: LILYGO T-Display K230 RISC-V AI dev kit features AMOLED, LoRa, and keyboard with optional LTE-M/NB-IoT cellular connectivity（CNX Software）
  url: https://www.cnx-software.com/2026/10/28/lilygo-t-display-k230-risc-v-ai-dev-kit-features-amoled-lora-and-an-optional-keyboard/
  publisher: CNX Software
- title: T-Display K230 Kit（LILYGO 公式ストア）
  url: https://lilygo.cc/products/t-display-k230-kit
  publisher: LILYGO（公式）
- title: T-Display K230（LILYGO Wiki）
  url: https://wiki.lilygo.cc/products/t-display-series/t-display-k230/
  publisher: LILYGO（公式）
faq:
- q: T-Display K230はいくらですか
  a: CNX Softwareによると、公式ストアでキットは約150ドル、基板のみは98.79ドル、別売キーボードは70.94ドル（nRF9151なし）または113.25ドル（あり）です。為替と在庫で変わります。
- q: 日本で買えますか
  a: 国内の販売店は確認できていません（掲載時点）。LILYGOの公式ストアやAliExpressで海外から買う形になります。
- q: 技適は取得していますか
  a: 確認できていません。Wi-Fi、Bluetooth LE、LoRaを備えるため、国内で電波を出す使い方をするなら事前に確認が必要です。
- q: 何のOSで動きますか
  a: Kendryte K230のLinux SDKとCanMV/RT-Smartのファームウェアが提供されています。新しいLinux版にはMeshtasticとLoRaWANの試験的な対応があります。
---

中国・深圳のLILYGOが、Canaan製のRISC-V SoC「Kendryte K230」を載せた開発キット「T-Display K230」を公式ストアで販売している。CNX Softwareが2026年10月28日に報じた。**製品として売られている**もので、クラウドファンディングではない。価格は為替と在庫で変わる。

## 何ができるのか

CNX Softwareが整理した主な仕様は次のとおり。

| 項目 | 内容 |
|---|---|
| SoC | Kendryte K230。64ビットRISC-Vの2コア（1.6GHzと800MHz）、AI用のKPU、2.5Dグラフィックス、H.264/H.265の動画処理を内蔵 |
| メモリ | 1GB LPDDR4。ストレージはmicroSD |
| 画面 | 4.1インチ、568×1232のAMOLEDタッチ |
| カメラ | 2MP、1080p。前面にも向けられる回転式 |
| 映像出力 | HDMI（1080p30） |
| 無線 | Wi-Fi 4、LoRa（SX1262で868/915/923MHz、またはLR2021で830〜940MHz）、Bluetooth LE（拡張基板のnRF52840） |
| 有線 | 10/100MbpsのEthernet、USB Type-C×3 |
| 拡張 | 40ピンのGPIOヘッダ、Qwiic、スピーカーとマイク、3.5mmヘッドホン端子 |
| 大きさ | 基板104×51×15.5mm。ケース付きは約110×58×30mm |

別売のキーボードは、バックライト付きのQWERTYで、21700電池を2本入れられる。標準版のほか、LTE-M、NB-IoT、GNSSのためのnRF9151を載せ、SIMスロットを持つ版もある。

ソフトウェアは、K230のLinux SDKとCanMV/RT-Smartのファームウェアが使え、LVGLで作った起動画面からカメラ、動画、音声、LoRa、Wi-Fi、電池残量のアプリを呼び出す。

## 価格

CNX Softwareの記載では、LILYGO公式ストアで次のとおり。

- キット（ケース付き）：約150ドル
- 基板のみ：98.79ドル
- キーボード：70.94ドル（nRF9151なし）、113.25ドル（あり）
- AliExpressではキットが約180ドル（SX1262とLR2021の両方の版）で、キーボードは133ドル

## 注意点

使い道は、遠隔監視や無線通信などの組み込み用途が中心で、普通のスマートフォンやパソコンの代わりにはならない。Wi-Fiは2.4GHzのみの「Wi-Fi 4」だ。レビューや実機での動作は確認していない。

## 日本で買える？使える？

- **国内販売：** 国内の販売店は確認できていない（掲載時点。「T-Display K230 国内 販売」で検索した）。LILYGO公式ストアとAliExpressから海外発送で買う形になる
- **技適：** 確認できていない。LoRaとWi-Fi、Bluetooth LEを内蔵するため、国内の屋外で電波を出す使い方は、技適の有無と周波数の確認が前提になる。LoRaは、版によって使える周波数帯が違う
- **電源：** USB Type-Cの5Vで動く。国内でそのまま使える
- **税金：** 公式ストアの価格には税が含まれていない。個人輸入では関税や消費税が別にかかる場合がある

行動の目安：RISC-VでLinuxを動かす遊びが目的なら、技適が不要な有線とディスプレイだけの使い方から始める。電波を出す使い方をするなら、国内の技適取得済みのモジュールを使った構成を選ぶほうが安全だ。
