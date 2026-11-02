---
title: Waveshare「UNO-Q-DSI-TOUCH-10.1A」、Arduino UNO Qに直接挿せる10.1インチ画面。スピーカーとカメラ端子まで付いて69.99ドル
slug: waveshare-uno-q-dsi-touch-10-1a
seo_title: Waveshare 10.1型UNO Q用画面は69.99ドル
x_hook: |
  マイコンボードが、裏から挿すだけでタブレットになる。
  Waveshareの「UNO-Q-DSI-TOUCH-10.1A」はArduino UNO Q専用の10.1インチ画面で、スピーカーとカメラ端子まで背面に載せた。
  ・1280×800のIPSタッチ
  ・公式ストアで69.99ドル
keyword: UNO Q用10.1型画面
category: pc
date: 2026-11-02
kicker: Waveshareが、Arduino UNO Q専用の10.1インチタッチ画面「UNO-Q-DSI-TOUCH-10.1A」を出した。ボードを背面のコネクタに挿すだけで使え、ステレオスピーカー、3.5mmジャック2つ、カメラ用のMIPI CSI端子2系統を備える。価格はWaveshare公式ストアで69.99ドル。
tags:
- Waveshare
- Arduino UNO Q
- タッチディスプレイ
- シングルボードコンピューター
- 電子工作
images:
- url: "https://www.waveshare.com/img/devkit/LCD/UNO-Q-DSI-TOUCH-10.1A/UNO-Q-DSI-TOUCH-10.1A-details-1.jpg"
  caption: 表面はArduino UNOのデスクトップを映した画面、背面は金属板に2つのスピーカーと、ボードを挿す基板。基板にはカメラ端子と3.5mmジャックが並ぶ
- url: "https://www.waveshare.com/media/catalog/product/cache/1/image/560x560/9df78eab33525d08d6e5fb8d27136e95/u/n/uno-q-dsi-touch-10.1a-1_1.jpg"
  caption: 正面。ベゼルの黒い縁のある横長の画面
credit: Waveshare 公式製品ページ
origin: SZX 深圳
giteki:
  status: 対象外
  number: []
  checked: 2026-11-02
  radio: ""
  note: "ディスプレイ本体に無線機能は無い。組み合わせるArduino UNO Q側は別に確認が要る"
sources:
- title: UNO Q gets a 10.1-inch touch display with integrated speakers, audio jacks, camera connectors
  url: https://www.cnx-software.com/2026/10/31/arduino-uno-q-gets-a-10-1-inch-touch-display-with-integrated-speakers-audio-jacks-camera-connectors/
  publisher: CNX Software
- title: UNO-Q-DSI-TOUCH-10.1A（Waveshare 公式製品ページ）
  url: https://www.waveshare.com/uno-q-dsi-touch-10.1a.htm
  publisher: Waveshare（公式）
faq:
- q: いくらですか
  a: CNX Softwareによると、Waveshare公式ストアで69.99ドル、AliExpressで80.09ドルです（掲載時点）。Arduino UNO Q本体を含むセットは、2GB/16GB版または4GB/32GB版で120ドルからとされています。
- q: どのボードで使えますか
  a: Arduino UNO Q専用です。Waveshareは、上位のVENTUNO Qには対応しないと明記しています。
- q: 日本で買えますか
  a: 国内の取扱店は、日本語で検索した範囲では確認できませんでした。Waveshare公式ストアとAliExpressで買えると報じられていますが、日本への発送条件は各ストアで確認が必要です。
- q: 技適は必要ですか
  a: この画面自体に無線機能はありません。UNO Q本体のWi-FiやBluetoothを使う場合の扱いは、本体側で確認する必要があります。
---

Waveshareが、Arduino UNO Q専用の10.1インチタッチ画面「UNO-Q-DSI-TOUCH-10.1A」を出した。CNX Softwareが2026年10月31日に報じた。

UNO QはMIPI DSIの信号を、背面の60ピンのコネクタ（JMEDIAとJMISC）から出している。これまで画面をつなぐには、公式の「Arduino UNO Media Carrier」のような拡張基板が実質必要だった。この製品は、そのコネクタを画面側に組み込み、UNO Qを挿すだけで使えるようにしたものだ。

## 主な仕様

- **画面：** 10.1インチのIPS、1280×800、60Hz。輝度300cd/m²、コントラスト800:1、視野角178°。強化ガラスで、光学ボンディング
- **タッチ：** 静電容量式のマルチタッチ。同時に読める点数はソフトウェア（OS）側の対応によるとされる
- **カメラ：** 22ピンのMIPI CSI端子が2系統（CAMERA0、CAMERA1）。対応するのはIMX219のカメラモジュールのみ
- **音：** ステレオスピーカー内蔵。3.5mmジャックは2つ（出力とマイク入力、出力のみ）
- **ほか：** RGB LED、金属製の背面板
- **電源：** UNO QのUSB-C経由で5V/3A。キャリア基板側のUSB-Cから5Vを補助給電する端子もある
- **大きさ：** 239×147×19.11mm（UNO Qの厚みは含まない）

Waveshareの説明では、初期状態は縦向きで、横向きにするにはソフトウェアの設定が要る。付属品は画面とUSB Type-A/Type-Cケーブル1本で、UNO Q本体とカメラは含まれない。

## 価格

- **Waveshare公式ストア：** 69.99ドル（掲載時点）
- **AliExpress：** 80.09ドル（掲載時点）
- **セット：** UNO Q本体（2GB/16GBまたは4GB/32GB）との組み合わせが120ドルから。CNX Softwareは、いずれAmazonの店にも並ぶ可能性がある、と書いている

## 注意点

対応はUNO Qのみ。同じ公式のMedia Carrierが対応するVENTUNO Q（価格が399ドルに上がったと報じられている）は、この画面の対象外だとWaveshareが明記している。CNX Softwareの記事は実機の評価ではなく仕様の紹介で、タッチの点数や画質は未確認だ。

## 日本で買える？使える？

**国内の取扱店は、掲載時点でまだ見つかっていない。ただし画面そのものは無線を持たないので、技適の心配は要らない。**

- **入手：** 公式ストアとAliExpressが販売先として挙がっている。日本への発送条件・送料・関税は各ストアで確認できる。
- **技適・PSE：** 画面自体は無線を持たず、技適の対象外と判断している。UNO Q本体のWi-FiやBluetoothを日本で使う場合は、本体側の技適の確認が要る。電源はUSB-Cの5Vで、ACアダプターは付属しない。
- **日本語：** 画面はOSの表示をそのまま出すだけで、日本語表示の可否はOS側に依存する。

日本上陸を待つうえで、まだ分かっていないのは、国内の取扱店が出るかどうかだ。

行動の目安：UNO Qで、配線なしに画面・音・カメラを足したいなら、公式ストアの69.99ドルが基準になる。日本向けの発送が確認できない場合は、公式のMedia Carrierなど、別の接続方法を探す手がある。国内の取扱いが始まったら追記する。
