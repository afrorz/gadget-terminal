---
title: 携帯型ハッキング&開発ツール「FREE-WILi 2」、RP2350×2とFPGAを積み400ドルで予約開始
seo_title: FREE-WILi 2は400ドルから、技適は未確認
slug: free-wili-2-hacking-multitool
keyword: FREE-WILi 2
category: weird
date: 2026-09-10
kicker: 米ミシガン州のFREE-WILi LLCが、RP2350を2基・ESP32-C5・FPGA・Raspberry Pi CM0を1台にまとめた携帯型マルチツール「FREE-WILi 2」を400ドルの予約受付で発表した。Wi-Fi・Bluetooth・LoRa・サブGHz・NFC・IRなど幅広い無線機能を積み、出荷は2026年第4四半期を予定する。
tags:
- FREE-WILi 2
- ハッキングツール
- RP2350
- 組み込み開発
x_hook: 画面付きの手のひらサイズの筐体に、Wi-Fi・Bluetooth・LoRa・サブGHz・NFC・IRの無線機がまとめて詰め込まれている。価格は400ドル、出荷は2026年末を予定するが、Founders Editionはすでに売り切れている。
embeds:
- type: youtube
  id: ji2Gl1b63co
  caption: "ChiefGyk3Dによる紹介動画「Free Wili 2: The Open-Source Flipper Zero Alternative?」"
images:
- url: "https://freewili.com/assets/freewili-og.png"
  caption: 本体正面。3.5インチタッチディスプレイと14個の物理ボタン、上部にアンテナ端子とD-pad
- url: "https://freewili.com/assets/wili8.webp"
  caption: 開発中の実機がディスプレイに「HELLO WORLD」を表示しているベンチ写真
- url: "https://freewili.com/assets/freewili2-device.png"
  caption: 背面ラベル。20/10ピンの拡張ヘッダーとアンテナ端子の配置が分かる
credit: FREE-WiLi 公式サイト(freewili.com)
faq:
- q: 日本で買えますか
  a: 掲載時点でFounders Editionは売り切れており、購入手段がありません。公式サイトにも日本を含む国際発送に関する具体的な記載はなく、確認できていません。
- q: 技適は取得していますか
  a: 公式サイトに技術基準適合証明(技適)の記載は見当たらず、確認できていません。Wi-Fi・Bluetooth・LoRa・サブGHzなどの無線機能を国内で使うには技適の取得が前提になります。USB経由の有線接続であれば技適の対象外で使えます。
- q: いくらですか
  a: Founders Editionは400ドルでした(掲載時点、現在は売り切れ)。
- q: いつ発売されますか
  a: 出荷は2026年第4四半期を予定していますが、現在Founders Editionは売り切れており、次のロットの受付時期は確認できていません。
sources:
- title: "FREE-WILi 2 portable hacking multitool features two RP2350 MCUs, ESP32-C5, ICE40 FPGA, and Raspberry Pi CM0"
  url: https://www.cnx-software.com/2026/09/09/free-wili-2-portable-hacking-multitool-features-two-rp2350-mcus-esp32-c5-ice40-fpga-and-raspberry-pi-cm0/
  publisher: CNX Software
- title: "Flipper One Alternative? Free Wili 2 Multitool Packs Dual RP2350 Chips and FPGA"
  url: https://www.geeky-gadgets.com/free-wili-2-multitool/
  publisher: Geeky Gadgets
- title: "FREE-WILi 2 — The Open Electronics Multitool"
  url: https://freewili.com/
  publisher: FREE-WiLi
---

米ミシガン州トロイのFREE-WILi LLCが、携帯型のハードウェアハッキング・組み込み開発ツール「FREE-WILi 2」の予約受付を始めた。Founders Editionの価格は400ドルで、出荷は2026年第4四半期を予定する。掲載時点でFounders Editionはすでに売り切れており、次のロットの受付時期は確認できていない。

## RP2350×2とFPGA、Linuxまで1台に

本体には次のチップが詰め込まれている。

| チップ | 役割 |
|---|---|
| RP2350(1基目) | メインMCU。IOとスクリプティングを制御 |
| RP2350(2基目) | 3.5インチ480×320の静電容量式タッチディスプレイ、操作、音声、DVI出力を制御 |
| ESP32-C5 | 2.4/5GHz Wi-FiとBluetooth LEを担当 |
| ICE40UP5K FPGA | SPIスレーブエミュレーションなどの特殊機能用 |
| Raspberry Pi CM0 | Linux実行環境。Pythonスクリプティングに対応 |

無線機能はWi-Fi(2.4/5GHz)、Bluetooth LE、CC1101によるサブGHz無線とLoRa(Meshtastic対応)、NFC/125kHzRFID、IEEE 802.15.4(Zigbee/Thread)、IR送受信と幅広い。物理ボタンは5方向D-pad・A/B/X/Yの4個・アンダースクリーンキー5個の合計14個で、拡張用の「Orca」ヘッダーも備える。ソフト面ではUSB CLIとオンデバイスGUIに加え、Python・Rust・C/C++から制御できる「OneWili API」、リアルタイムスクリプティング用の「rThon」、ビジュアルプログラミングの「WiliBlocks」を用意する。公式サイトが挙げる用途例は、LoRaメッシュ通信、RFID実験、カスタムハードウェアの試作、セキュリティテスト、組み込み開発、レトロゲーム、環境モニタリング、CANバス診断などだ。

## 「Flipper Zeroの代替」と評される理由

Geeky GadgetsやYouTubeのレビューは、FREE-WILi 2を携帯型ハッキングツール「Flipper Zero」の代替として位置づけている。Flipper Zeroが1つのMCUで無線実験や信号解析に特化するのに対し、FREE-WILi 2はデュアルMCUに加えFPGAとLinux実行環境まで積むことで、より汎用的な組み込み開発・実験用のプラットフォームを目指している点が違いとされる。

## 日本から見るとどうか

FREE-WILi 2はWi-Fi・Bluetooth・LoRa・サブGHz・NFC/RFID・Zigbee/Thread・IRという極めて広い無線機能を1台に積んでいるが、公式サイト・CNX Software・Geeky Gadgetsのいずれにも技適(技術基準適合証明)に関する記載は見当たらず、確認できていない。技適の無い無線機を国内で電波を発射して使うのは、個人の実験目的であっても電波法違反にあたる。Flipper Zeroのような携帯型ハッキングツールは、個人輸入した本人が「実験用だから」と無線機能を有効化してしまいがちな点が国内では特に問題になりやすい。FREE-WILi 2はUSB接続だけでもLinuxのCLI操作やPythonスクリプティングができる設計のため、無線機能を使わない範囲であれば技適の対象外で使える可能性がある一方、この製品の主な売りである無線実験機能はほぼ使えなくなる。

なお、現在Founders Editionは売り切れており、公式サイトにも日本を含む国際発送についての具体的な記載は無い。今すぐ購入する手段自体が無い点も踏まえておきたい。
