---
title: Banana Pi「BPI-M2C」は5Gモデム内蔵のUNISOC製スマホ用チップを積んだシングルボード、公式ストアで239ドル
seo_title: Banana Pi BPI-M2Cは239ドルの5G対応SBC
x_hook: |
  このラズパイ風ボードには、5Gモデムが最初から入っている。
  Banana Pi「BPI-M2C」はUNISOCのスマホ用チップを搭載し、NPUは8 TOPS。公式ストアの価格は239ドル（約3.7万円）。
slug: banana-pi-bpi-m2c-unisoc-5g-sbc
keyword: BPI-M2C
category: pc
date: 2026-11-28
kicker: Banana Piの新しいシングルボード「BPI-M2C」は、UNISOCのスマホ向けSoC「UIS7885」を載せ、5G・4G回線と8 TOPSのNPUを1枚にまとめている。4GBメモリと128GBのeMMCが付き、公式ストアで239ドルで受注中。
tags:
  - Banana Pi
  - BPI-M2C
  - UNISOC
  - シングルボードコンピューター
  - 5G
images:
  - url: "https://images-oss.2cshop.com/upload/customer_15823/upload/20261123/f68602c82ae87f0b9bdadbf06cf00d17.jpg"
    caption: 基板の表面。中央にUNISOC UIS7885、上部に40ピンのGPIO、右にUSBとLANが並ぶ
  - url: "https://docs.banana-pi.org/bpi-m2c/m2c_interface_en_261126.jpg"
    caption: 公式資料の端子配置図。表はHDMI・USB-C・LAN・アンテナ端子、裏はSIMスロットとmicroSD、カメラ・ディスプレイのコネクタ
credit: Banana Pi 公式ストア・公式ドキュメント
sources:
  - title: Banana Pi BPI-M2C SBC features UNISOC UIS7885 SoC with 5G cellular connectivity, 8 TOPS NPU
    url: https://www.cnx-software.com/2026/11/26/banana-pi-bpi-m2c-sbc-features-unisoc-uis7885-soc-with-5g-cellular-connectivity-8-tops-npu/
    publisher: CNX Software
  - title: BPI-M2C ドキュメント
    url: https://docs.banana-pi.org/en/BPI-M2C/BananaPi_BPI-M2C
    publisher: Banana Pi（公式ドキュメント）
  - title: Banana Pi BPI-M2C
    url: https://www.bpi-shop.com/products/banana-pi-bpi-m2c.html
    publisher: Banana Pi（公式ストア）
giteki:
  status: 確認できない
  number: []
  checked: 2026-11-28
  radio: 5G / 4G LTE / Wi-Fi 5 / Bluetooth / GNSS
  note: 総務省の技適データベースでBanana Pi（SINOVOIP）名義の登録が見つからない
alternatives:
  - name: Raspberry Pi 5（8GB）
    why: 国内で流通するシングルボードの定番で、技適取得済みのWi-Fi・Bluetoothを内蔵する。5G回線は無いが、OSとソフトの情報が多く、買ってすぐ使える。
    url: https://item.rakuten.co.jp/marutsuelec/2782704/
    merchant: rakuten
    image: "https://thumbnail.image.rakuten.co.jp/@0_mall/marutsuelec/cabinet/04881820/230620/2782704_2.jpg"
faq:
  - q: BPI-M2Cはいくらですか
    a: CNX Softwareによると、Banana Piの公式ストアで239ドルで受注中です。掲載時点の価格で、AliExpressの店舗ではまだ販売が始まっていません。
  - q: OSは用意されていますか
    a: CNX Softwareの時点では、UbuntuとYoctoのイメージとLinuxのBSPは未公開で、公式のGitHubにも該当するリポジトリは見つからなかったとされています。Androidについては記載がありません。
  - q: 日本で使えますか
    a: 日本の販売元は確認できていません。5G・4G回線とWi-Fi・Bluetoothを内蔵しますが、技適は確認できていません。有線LANだけで使う分には無線は関係しません。
  - q: 主な仕様を教えてください
    a: 8コアのUNISOC UIS7885（T820、6nm）、4GB LPDDR4X、128GB eMMC、microSD、HDMI出力、MIPIのカメラとディスプレイ端子、ギガビットLAN、USB 2.0×4、40ピンGPIOです。
---

Banana Piの「BPI-M2C」は、スマホ向けのSoC「UNISOC UIS7885」を載せたシングルボード。CNX Softwareは、UNISOCのモバイル向けチップを使ったSBCはこれまで見たことがないと書いている。

## 仕様

| 項目 | 内容 |
|---|---|
| SoC | UNISOC T820（UIS7885）、6nm、8コア（Cortex-A76×4＋A55×4、最大2.7GHz） |
| GPU・NPU | Arm Mali-G57、NPUは最大8 TOPS |
| メモリ・保存 | 4GB LPDDR4X、128GB eMMC、microSDスロット |
| 映像 | HDMI（最大1920×1080、DSI-HDMI変換チップ経由）、MIPI DSI（最大1280×800）、MIPI CSIカメラ端子 |
| 通信 | 5G・4G LTE・3G・2G（nano SIM）、デュアルバンドWi-Fi 5、Bluetooth、GNSS |
| 有線・拡張 | ギガビットLAN（外付けモジュールでPoE）、USB 2.0×4、40ピンGPIO、3.5mmジャック |
| 電源・大きさ | USB-Cの5V、85×56mm、60g |
| 価格 | 239ドル（公式ストア、掲載時点） |

アンテナ端子はU.FLが4つで、Wi-Fi・Bluetooth・GPS用が1つ、回線用が3つ。CNX SoftwareはRockchip RK3588に近い仕様で、性能も近いはずと見ている。違いは5Gモデムが内蔵されている点で、通信用のM.2モデムを別に付ける必要がない。

## 買う前に注意すること

OSの準備が整っていない。CNX Softwareによると、UbuntuとYoctoのイメージとLinuxのBSPは未公開で、公式のGitHubにも見つからなかった。モバイル向けのチップだが、Androidの記載もない。公式資料は公開されているものの、同媒体は「OSイメージとBSPが出てから買うのがよい」としている。UNISOCのイベントでは、Qtのデモが展示されたという。

また、ここで挙げた性能の見立てはCNX Softwareの推測で、公式の測定値ではない。この記事の仕様は主に1社の報道と公式資料によっている。

## 日本で買える？使える？

**日本の販売元は確認できておらず、Banana Piの公式ストアから海外発送で取り寄せる形になる。** 公式ストアが日本へ発送するかは、今回の資料では確かめられていない。

技適は、総務省のデータベースでBanana Pi名義の登録を確認できていない。5G・4G回線とWi-Fi、Bluetoothを内蔵するので、日本で電波を出して使うには技適の確認が要る。有線LANとHDMIだけで使うなら、無線は関係しない。5Gの対応バンドも資料からは読み取れておらず、日本の携帯会社の回線で使えるかは不明だ。

すぐに試したい人には、国内の販売店が扱うRaspberry Pi 5が手堅い。5G回線は無いが、技適済みで、OSやソフトの情報も多い。BPI-M2Cは、OSが出そろうのを待ってからでも遅くない。
