---
title: HackerGadgets「RTL-SDR/LoRa/GPS/RTC HAT」、ラズパイ1枚にSDR受信機とLoRaとGPSを載せて84.90ドルから
slug: hackergadgets-rtl-sdr-lora-gps-rtc-pi-hat
seo_title: ラズパイ用SDR・LoRa・GPS HATは84.90ドル
x_hook: |
  電波を聞いて、送って、位置まで知る基板。
  HackerGadgetsのラズパイ用HATは、RTL-SDR受信機とLoRa送受信、GPS、時計を1枚に載せている。
  ・100kHz〜1.74GHzを受信
  ・Meshtastic用のSX1262を搭載
keyword: SDR・LoRa HAT
category: pc
date: 2026-11-23
kicker: 中国・広州のHackerGadgetsが、Raspberry Pi用のHAT「RTL-SDR/LoRa/GPS/RTC HAT」を売っている。RTL-SDR受信機、SX1262のLoRa送受信、GPS、時計のICを1枚に載せ、価格は公式ストアで84.90ドルから。
tags:
- HackerGadgets
- Raspberry Pi
- RTL-SDR
- LoRa
- Meshtastic
images:
- url: "https://cdn.shopify.com/s/files/1/2067/9757/files/RPI-AIO-SMA_TOP.png?v=1786962615"
  caption: SMA版の表面。右側にSDR・GPS・LoRaの3つのSMAコネクターが並び、USB-Cポートと設定用のDIPスイッチ、ボタン電池が載る
- url: "https://cdn.shopify.com/s/files/1/2067/9757/files/RPI-AIO-IPEX_45_degree_d699c9e4-0454-4572-9618-78b543bc9ffd.png?v=1786963034"
  caption: U.FL版をRaspberry Piに重ねた状態。ケーブルで本体のUSBとつなぐ
- url: "https://cdn.shopify.com/s/files/1/2067/9757/files/RPI-AIO-SMA_With_antenna_Full_Kit.png?v=1787215349"
  caption: アンテナ付きのキット。3本のアンテナ、スペーサー、ネジ、USBケーブルが同梱される
credit: HackerGadgets 公式ストア
giteki:
  status: 確認できない
  number: []
  checked: 2026-11-23
  radio: LoRa（860〜960MHz）、GNSS・SDRは受信専用
  note: 総務省DBでHackerGadgetsの登録は見つからなかった
sources:
- title: 4-in-1 Raspberry Pi HAT combines RTL-SDR, LoRa, GPS, and RTC（CNX Software）
  url: https://www.cnx-software.com/2026/11/22/4-in-1-raspberry-pi-hat-combines-rtl-sdr-lora-gps-and-rtc/
  publisher: CNX Software
- title: RTL-SDR/LoRa/GPS/RTC hat for Raspberry Pi（HackerGadgets 公式ストア）
  url: https://hackergadgets.com/products/rtl-sdr-lora-gps-rtc-hat-for-raspberry-pi
  publisher: HackerGadgets（公式）
alternatives:
  - name: RTL-SDR V4（アンテナ付き SDR受信機）
    why: 国内の楽天市場で買える、受信専用のUSB型SDR。HATのSDR部分と同じ系統のRTL2832Uを使い、電波を送らないので送信の技適を気にせず試せる。LoRaやGPSは付かない。
    url: https://item.rakuten.co.jp/zmart-shop/3406/
    merchant: rakuten
    image: "https://thumbnail.image.rakuten.co.jp/@0_mall/zmart-shop/cabinet/25/3406-1.jpg"
faq:
- q: いくらですか
  a: 公式ストアでは、基板のみが84.90ドル、アンテナ3本付きが108.50ドルです（掲載時点）。SMA版とU.FL版があり、どちらも同じ価格です。
- q: どのRaspberry Piで使えますか
  a: Raspberry Pi 3B・4B・5にそのまま載せられます。Raspberry Pi ZeroとZero 2 Wは、40ピンのヘッダーがあれば載せられますが、高さと電源容量の確認が必要です。
- q: 日本で技適は取得していますか
  a: 確認できていません。総務省のデータベースにHackerGadgetsの登録は見つかりませんでした。LoRaは電波を送る機能です。
- q: 日本へ発送されますか
  a: 公式ストアの日本への発送条件は確認できていません。
---

中国・広州のHackerGadgetsが、Raspberry Pi用のHAT「RTL-SDR/LoRa/GPS/RTC HAT」を公式ストアで売っている。CNX Softwareが2026年11月22日に紹介した。SDR受信機、LoRa送受信、GPS、時計の4つを1枚の基板に載せたもので、価格は基板のみで84.90ドル、アンテナ3本付きで108.50ドル（掲載時点、SMA版もU.FL版も同じ）。

## 何が載っているのか

- **SDR受信機**: RealtekのRTL2832UとRafael MicroのR860の組み合わせ。受信範囲は100kHz〜1.74GHz。HF直接サンプリングは100kHz〜28.8MHzで、アンテナ給電（バイアスT）と温度補償水晶（TCXO）も付く
- **LoRa**: SemtechのSX1262で、860〜960MHz帯、最大出力は22dBm。Meshtasticのファームウェアが最初から使える
- **GNSS**: GPSとBeidou、またはGPSとGLONASSをDIPスイッチで切り替える。PPS出力、アクティブ・パッシブどちらのアンテナにも対応
- **RTC**: NXPのPCF85063A。充電式の3Vボタン電池で、ラズパイの電源が切れても時刻を保つ

| 項目 | 内容 |
|---|---|
| 対応 | Raspberry Pi 3B / 4B / 5（Zero系は40ピンのヘッダーがあれば可） |
| 接続 | 40ピンのGPIO（LoRaはSPI、GNSSはUART、RTCはI2C）。SDRはUSB-CかHAT内部のUSBコネクター |
| 電源 | GPIOから5V。Raspberry Pi 5は5V/5A、Pi 4は5V/3Aを推奨 |
| 形状 | Raspberry Pi HAT+の大きさ |
| 価格 | 84.90ドル（基板のみ）／108.50ドル（アンテナ付き）。掲載時点 |

使い方は、HATをGPIOヘッダーに差してネジで固定し、アンテナ3本と内部USBケーブルをつなぐ。ソフトはRaspberry Pi OSの64ビットが勧められ、I2C・SPI・UARTを有効にする設定の変更が必要になる。用途としては、SDR++やGQRXによる電波の観測、ADS-Bや気象衛星NOAAの受信、Meshtasticでのメッシュ通信、LoRaのIoTノード、ラジオゾンデの受信などが挙げられている。

CNX Softwareは、似た先行例としてCaribouLiteを挙げている。CaribouLiteは30MHz〜6GHzと受信範囲が広いが、Raspberry Pi 5には対応しない。この記事は、CNX Softwareの紹介と公式ストアの情報による。実機を使った独立したレビューは、掲載時点で見つかっていない。

## 日本で買える？使える？

**国内の取扱店は確認できておらず、入口は公式ストア（海外）です。** 日本への発送条件も、確認できていません。

使う前に押さえたい点は、電波を出す部分と出さない部分で扱いが違うことです。SDRとGPSは受信専用なので、電波を出しません。一方、LoRaは送信する機能で、日本で使うなら技適を取得した機器が前提になります。総務省のデータベースで検索しましたが、HackerGadgetsの登録は見つかりませんでした。また、日本のLoRaは920MHz帯が使われるため、860〜960MHzに対応するこの基板でも、日本で使える周波数と出力は別に確かめる必要があります。

そこで、国内で今すぐ試すなら、受信専用の部分だけを先に楽しむ手があります。USB型のRTL-SDRは国内でも買え、電波を送らないので、送信の技適を気にせずに電波の観測から始められます。LoRaやGPSまで1枚でそろえたい人は、日本向けの周波数に対応して技適を取得したモジュールを使う基板を探すことになります。
