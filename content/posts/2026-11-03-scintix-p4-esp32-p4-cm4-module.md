---
title: RELOC「SCINTIX P4」、Raspberry Pi CM4/CM5の差し込み口で動くESP32-P4モジュール。Linuxではなく、ファームウェアで動く
slug: scintix-p4-esp32-p4-cm4-module
seo_title: SCINTIX P4、CM4形状のESP32-P4モジュール
x_hook: |
  Raspberry Piのスロットに挿して、Linuxが動かないボード。
  イタリアRELOCの「SCINTIX P4」は、CM4/CM5の形でESP32-P4を載せ、Wi-Fi 6とEthernetも持つ。
  ・RISC-V 400MHz×2コア
  ・ESP-IDFとArduinoで開発
keyword: SCINTIX P4
category: pc
date: 2026-11-03
kicker: イタリアのRELOCが、Espressif製のESP32-P4をRaspberry Pi CM4/CM5と同じ55×40mmの基板に載せた「SCINTIX P4」を公開した。CM4/CM5用のキャリアボードに挿して使えるが、動かすのはLinuxではなく、ESP-IDFなどで書いたファームウェアになる。
tags:
- SCINTIX P4
- ESP32-P4
- RISC-V
- Raspberry Pi CM4
- 電子工作
giteki:
  status: 確認できない
  number: []
  checked: 2026-11-03
  radio: Wi-Fi 6 / Bluetooth 5 LE / IEEE 802.15.4
  note: "モジュールとしての技適は確認できていない。載せているESP32-C6はチップ単体"
images:
- url: "https://www.reloc.it/wp-content/uploads/2026/03/prod_rm-cmp4_v2.jpg"
  caption: 基板の上面。中央にESP32-P4、上部に無線用のアンテナ付きモジュール、下側にUSB Type-Cコネクタ。CM4形状の基板
credit: RELOC 公式製品ページ
sources:
- title: SCINTIX P4（RELOC 公式製品ページ）
  url: https://www.reloc.it/products/rm-cmp4/
  publisher: RELOC（公式）
- title: RISC-V compute module brings ESP32-P4 to Raspberry Pi CM4/CM5 carriers
  url: https://linuxgizmos.com/risc-v-compute-module-brings-esp32-p4-to-raspberry-pi-cm4-cm5-carriers/
  publisher: LinuxGizmos
- title: SCINTIX P4 ESP32-P4 Compute Module works with (some) Raspberry Pi CM4/CM5 carrier boards
  url: https://www.cnx-software.com/2026/06/17/scintix-p4-esp32-p4-compute-module-raspberry-pi-cm4-cm5-carrier-boards/
  publisher: CNX Software
alternatives:
  - name: M5Stack Tab5 IoT開発キット（ESP32-P4）
    why: 同じESP32-P4を、5インチのタッチ画面・カメラ・バッテリースロット付きで国内の販売店から買える。ESP-IDFでの試作を今日から始められる。
    url: https://item.rakuten.co.jp/zmart-shop/3458/
    merchant: rakuten
    image: "https://thumbnail.image.rakuten.co.jp/@0_mall/zmart-shop/cabinet/25/3458-1.jpg"
faq:
- q: SCINTIX P4でLinuxは動きますか
  a: 動きません。LinuxGizmosによると、ベアメタルまたはRTOSのファームウェアで動かすモジュールで、開発はESP-IDF、Arduino、PlatformIOで行います。
- q: Raspberry PiのどのボードにでもCM4用の差し込み口で使えますか
  a: 形とコネクタは合いますが、使える周辺機能はキャリアボード側の配線に依存します。RELOCが互換を記載しているのは、公式のCM4/CM5 IOボードと、一部のサードパーティ製ボードです。
- q: 価格はいくらですか
  a: 掲載時点で、クラウドファンディングの価格や出荷日は発表されていません。RELOCの製品ページには「価格は問い合わせ」とあります。
- q: 日本で使えますか
  a: 掲載時点で日本の販売元は確認できていません。無線を使う用途では技適が必要になります。
---

イタリアのRELOCが、Espressif製のマイコン「ESP32-P4」を、Raspberry Pi CM4/CM5と同じ55×40mmの基板に載せたコンピュートモジュール「SCINTIX P4」を公開した。2026年11月3日時点で、価格と出荷日は発表されていない。

**製品の扱いは、掲載時点でまだ流動的だ。** RELOCの製品ページには「Contact us for pricing」とある一方、同じページにはCrowd Supplyでの近日公開（プレローンチ）の案内もある。クラウドファンディングが始まるまでは、購入手段は問い合わせになる。

## どんなモジュールか

見た目と端子はRaspberry Pi Compute Module 4のものだが、中身はまったく別の系統だ。LinuxGizmosとRELOCの資料による仕様は次のとおり。

- **メイン：** ESP32-P4NRW32X。最大400MHzのRISC-V 32ビットCPUが2コアで、AI向けの命令拡張と単精度の浮動小数点演算ユニットを持つ。別に最大40MHzの低消費電力コアがある
- **メモリ：** 32MBのPSRAMと32MBのNORフラッシュ
- **無線：** 別チップのESP32-C6が担当する。2.4GHzのWi-Fi 6、Bluetooth 5 LE、Thread/Zigbee向けのIEEE 802.15.4
- **有線：** 10/100MbpsのEthernet PHY。RELOCの試験では、UDPで上り約73Mbps、下り約79Mbps
- **画面・カメラ：** 2レーンのMIPI-DSIとMIPI-CSI。H.264とJPEGのハードウェアコーデックを持つ
- **USB：** 電源とプログラミング用のUSB Type-Cを基板に搭載。USB 2.0 OTGの信号はキャリアボードへ出す
- **大きさ：** 55×40×5mm、プログラミング用コネクタを含めて約8mm。重さ8.2g。動作温度は-20〜70℃
- **電源：** CM4/CM5のコネクタからの5V、またはUSB Type-C

## 何が面白いのか

Raspberry Pi CM4/CM5用に作られた入出力ボードやディスプレイ付きボードを、そのまま試作の土台に使える点だ。ただしCM4/CM5の中身はArm CPUでLinuxが動くのに対し、ESP32-P4は**Linuxを動かさない**。ベアメタルかRTOSでファームウェアを書く。RELOCはESP-IDF 6.0.1の手順と、USB書き込み、Ethernet、Wi-Fiのサンプルを公開している。

互換にも限りがある。ESP32-P4にはHDMIやPCIeがないため、それらに頼るキャリアボードの機能は使えない。CNX Softwareは、標準の40ピンヘッダ側のI2Cの割り当ても、ESP32-P4の別のGPIOで読み替える必要があると伝えている。RELOCが互換を記載しているのは、公式のCM4/CM5 IOボードのほか、CM4-DUAL-ETH-MINI、一部のWaveshare製ボードなどだ。

## 価格と注意点

- **価格：** 未発表。RELOCは問い合わせを案内している
- **注意：** Raspberry Piの感覚で買うと、Linuxが動かず、HDMIも使えない。画面を使うならMIPI-DSIのパネルをキャリアボードで接続する形になる
- **注意：** 回路図、部品表、ピン配置図、機構モデル、KiCadライブラリは「公開予定」とされ、掲載時点でそろってはいない。ファームウェアのサンプルはGitHubにある

## 日本で買える？使える？

**日本の販売元は、掲載時点で確認できていない。** 日本語で製品名を調べた範囲では、国内の紹介記事も見つからなかった。

- **入手：** RELOCは製品ページで問い合わせを案内している。Crowd Supplyでの募集が始まれば、そこから買うことになる見込みだが、日本への発送は発表されていない
- **技適：** Wi-Fi 6、Bluetooth 5 LE、802.15.4の電波を出す。モジュールとしての技適は確認できていない。無線を使う機器に組み込んで日本で使うなら、技適の取得が要る。試作として有線だけで使う場合はこの点は関係しない
- **日本語：** ハードウェアの開発向けで、日本語対応は問題になる場面が少ない。資料は英語

行動の目安：ESP32-P4を試したいだけなら、国内の販売店で開発キットが手に入る。CM4/CM5の入出力ボードを持っていて、そのまま差し替えたい人は、Crowd Supplyの募集開始を待ち、価格と配送先を確認してからでよい。日本向けの情報が出たら追記する。
