---
title: "「FREE-WILi 2」はRP2350×2・ICE40 FPGA・ESP32-C5を1台に集約したオープンソースのハッキング/セキュリティ研究用マルチツール、Founder Editionは400ドルでQ4 2026出荷予定"
seo_title: FREE-WILi 2は400ドルの多機能ハッキング端末
slug: free-wili-2-hacking-multitool
keyword: FREE-WILi 2
category: pc
date: 2026-09-23
kicker: 米ミシガン州トロイのIntrepid Control Systemsが、オープンソースのハッキング/セキュリティ研究向け携帯マルチツール「FREE-WILi 2」を自社ストアで公開した。RP2350を2基、ICE40 FPGA、Wi-Fi/Bluetooth対応のESP32-C5、Linuxが動くRaspberry Pi CM0を1台に集約し、Founder Editionの価格は400ドル、出荷は2026年第4四半期を予定する。
tags:
  - FREE-WILi 2
  - RP2350
  - Intrepid Control Systems
  - ハッキングツール
  - セキュリティ研究
x_hook: RP2350を2基、FPGA、Wi-Fi/Bluetoothチップ、そしてLinuxが動くRaspberry Pi CM0まで、5種類のプロセッサを手のひらサイズの端末1台に詰め込んだ。CAN FDやLoRa、125kHz RFIDにも対応し、価格は400ドルから。
origin: DTW デトロイト
embeds:
  - type: youtube
    id: Woj5an8Z4Bw
images:
  - url: "https://shop.freewili.com/cdn/shop/files/FREE-WILi2_Face_900x900_6fe2c847-3537-4b61-bf65-bf7d6491f60c.png"
    caption: 正面。3.5インチタッチスクリーンに「FREE WILi 2」のロゴ、上部にRGB LED7個、右側にホーム・チェック・×・保存ボタン、下部にコンテキストキー5個、左に方向パッドを配置する
    credit: FREE-WILi公式ストア(shop.freewili.com)
  - url: "https://shop.freewili.com/cdn/shop/files/FREE-WILi2_Back_900x900_d0832406-f039-4ed5-b2db-7d764241c012.png"
    caption: 背面のピンアウト表示。20ピン・10ピンコネクタの割り当て(CAN FD、IO、SPI、UART、I2Cなど)とURL・QRコード・シリアル番号が確認できる
    credit: FREE-WILi公式ストア(shop.freewili.com)
  - url: "https://shop.freewili.com/cdn/shop/files/FREE-WILi2_Top_900x900_3d9f8977-d677-4317-ab34-5cebff00e860.png"
    caption: 上端のインターフェース。USB Type-C、HDMI出力、右端に無線用アンテナコネクタが並ぶ
    credit: FREE-WILi公式ストア(shop.freewili.com)
buy:
  - name: FREE-WILi 2 Founder Edition(公式ストア)
    url: https://shop.freewili.com/products/free-wili-2
    price: 400ドル(掲載時点)
    giteki: 未取得
    note: 予約受付中で、出荷は2026年第4四半期を予定しているが、ハードウェア新製品であり日程が動く可能性がある。日本への発送対応は参照した情報源からは確認できていない。Wi-Fi・Bluetooth・LoRa・NFC/RFIDなど複数の無線モジュールを搭載しており、国内で無線機能を使うには技適の取得が前提になるが、掲載時点で取得の案内は確認できていない。
faq:
  - q: 日本で買えますか
    a: 公式ストアで予約注文自体は可能ですが、日本への発送に対応しているかは掲載時点の情報からは確認できていません。
  - q: 技適は取得していますか
    a: 掲載時点で確認できていません。Wi-Fi・Bluetooth・LoRa・NFC/RFIDなど複数の無線モジュールを搭載しており、国内でこれらを使うには技適の取得が前提になります。
  - q: いくらですか
    a: Founder Editionが400ドルです(掲載時点)。
  - q: いつ発売されますか
    a: 2026年第4四半期の出荷を予定していますが、確定した日程ではありません。
sources:
  - title: "FREE-WILI 2 (Founder Edition)"
    url: https://shop.freewili.com/products/free-wili-2
    publisher: FREE-WILi公式ストア
  - title: FREE-WILi 2 公式サイト
    url: https://freewili.com/
    publisher: FREE-WILi
  - title: "FREE-WILi 2 portable hacking multitool features two RP2350 MCUs, ESP32-C5, ICE40 FPGA, and Raspberry Pi CM0"
    url: https://www.cnx-software.com/2026/09/09/free-wili-2-portable-hacking-multitool-features-two-rp2350-mcus-esp32-c5-ice40-fpga-and-raspberry-pi-cm0/
    publisher: CNX Software
---

米ミシガン州トロイのIntrepid Control Systems(車載ネットワーク解析ツールで知られる企業)が、オープンソースのハッキング/セキュリティ研究向け携帯マルチツール「FREE-WILi 2」を自社ストアで公開した。前モデルの後継で、手のひらサイズの筐体に5種類のプロセッサを詰め込んだ構成が特徴だ。掲載時点でFounder Editionの価格は400ドル、出荷は2026年第4四半期を予定している。予約注文であり、新規ハードウェアである以上、日程が動く可能性はある。

## 中身はプロセッサ5種類

心臓部はRaspberry Pi RP2350を2基(いずれもデュアルコア、PIO搭載、8MB SRAM/16MBフラッシュ)。これにLattice製ICE40 FPGA(8MB SRAM付き)、Wi-Fi 2.4/5GHzとBluetooth LEを担当するESP32-C5、Linuxが動くRaspberry Pi CM0、LoRa専用のSTM32WLE5JCを組み合わせる。無線面ではMeshtastic対応のLoRaに加え、125kHzと13.56MHz(ST25R3916B)のNFC/RFID、CAN FD(8Mbit)まで備える。用途としては組み込み開発、セキュリティ研究・ペネトレーションテスト、技術教育、レトロゲーミングなどが想定されている。

3.5インチ・480×320のタッチスクリーンに加え、5方向D-パッド、A/B/X/Yに相当する4ボタン、5個のコンテキストキーを搭載。センサーは9軸IMU(BMI323)、磁気センサー(BMM350)、環境光センサー(OPT4001)、温湿度センサー(SHT40)、4マイクアレイと幅広い。バッテリーは3000mAhで、スリープ時の消費電流は60µAという。

## スペック(公式サイトより)

| 項目 | 内容 |
| --- | --- |
| メインCPU | RP2350×2(デュアルコア、PIO搭載) |
| FPGA | Lattice ICE40(8MB SRAM) |
| 無線MCU | ESP32-C5(Wi-Fi 2.4/5GHz、Bluetooth LE) |
| Linux | Raspberry Pi CM0 |
| LoRa | STM32WLE5JC(Meshtastic対応) |
| メモリ | RP2350ごとに8MB SRAM/16MBフラッシュ |
| ディスプレイ | 3.5インチ、480×320タッチスクリーン |
| センサー | 9軸IMU、磁気センサー、環境光センサー、温湿度センサー、4マイクアレイ |
| 通信 | Wi-Fi、Bluetooth LE、LoRa、NFC/RFID(125kHz+13.56MHz)、CAN FD(8Mbit) |
| インターフェース | USBホスト×3、20/10ピンコネクタ、DVI出力 |
| バッテリー | 3000mAh、スリープ時60µA |
| 価格(Founder Edition) | 400ドル(掲載時点) |

## 日本から見るとどうか

**技適は掲載時点で未確認。** FREE-WILi 2はWi-Fi・Bluetooth・LoRa・NFC/RFIDと複数の無線モジュールを搭載しており、国内でこれらを使うには技適の取得が前提になる。公式サイト・公式ストアのいずれにも日本の技術基準適合証明への言及は見当たらない。

**日本への発送も確認できていない。** 公式ストアはFounder Editionの予約を受け付けているが、参照した情報源には日本を含む国際発送の可否について明記が無かった。購入を検討する場合は、注文前に発送先の対応状況を直接確認する必要がある。

**用途面でも注意が要る。** FREE-WILi 2はNFC/RFIDの読み取りやCAN FDへのアクセスなど、セキュリティ研究・ペネトレーションテストを想定した機能を持つ。製造元は教育・研究用途を掲げているが、対象システムの所有者の許可なく通信を傍受・操作する行為は、国内でも不正アクセス禁止法などに抵触しうる。技適の有無にかかわらず、用途は許可された範囲にとどめる必要がある。

情報源は公式ストア、公式サイト、CNX Softwareの3件。価格・出荷時期はいずれも掲載時点の情報で、予約注文である以上、変更される可能性がある。
