---
title: ANAVI I2C TPM 2.0、Raspberry Pi用のオープンソースTPMモジュール。Infineon SLB 9673搭載で20ドル、Crowd Supplyで募集中
slug: anavi-i2c-tpm-2-raspberry-pi-crowd-supply
seo_title: ANAVI I2C TPM 2.0は20ドル、日本で使える？
x_hook: |
  Raspberry Piに足りなかったのは、ディスク暗号の鍵を守る部品だった。
  ブルガリアのANAVIが作る「I2C TPM 2.0」は16.5×12.8mmの小さな基板で、Infineon製TPMチップを載せる。
  ・設計データはKiCadで公開
  ・20ドル（約3,000円）
keyword: ANAVI TPM 2.0
category: pc
date: 2026-11-20
kicker: オープンソースハードウェアのANAVIが、Raspberry Pi向けの「ANAVI I2C TPM 2.0」をCrowd Supplyで募集している。Infineon OPTIGA SLB 9673を載せた16.5×12.8mmの小型基板で、価格は20ドルから。出荷は2027年3月18日の予定。
tags:
- ANAVI
- Raspberry Pi
- TPM
- Crowd Supply
- オープンソースハードウェア
images:
- url: "https://anavi.technology/images/anavi-i2c-tpm-20.jpg"
  caption: ANAVI I2C TPM 2.0の基板。5ピンのI2Cヘッダー（3.3V・SDA・SCL・RST・GND）を持ち、表と裏、横向きと縦向きの2種類が並ぶ
credit: ANAVI Technology 公式サイト
giteki:
  status: 対象外
  number: []
  checked: 2026-11-20
  radio: ""
  note: 無線機能のない基板モジュール
sources:
- title: Raspberry Pi SBCs get an open-source hardware I2C TPM 2.0 security module (Crowdfunding)（CNX Software）
  url: https://www.cnx-software.com/2026/11/19/raspberry-pi-sbcs-get-an-open-source-hardware-i2c-tpm-2-0-security-module/
  publisher: CNX Software
- title: ANAVI Technology 公式サイト
  url: https://anavi.technology/
  publisher: ANAVI Technology（公式）
- title: anavi-i2c-tpm-2.0（GitHub）
  url: https://github.com/AnaviTechnology/anavi-i2c-tpm-2.0
  publisher: ANAVI Technology（公式）
faq:
- q: ANAVI I2C TPM 2.0はいくらですか
  a: Crowd Supplyでは横向きが20ドル、縦向きが21ドルです。送料は米国向けが8ドル、そのほかの地域は18ドルです。CNX Softwareが2026年11月19日に伝えた値で、募集ページの最新の状況は確認できていません。
- q: いつ届きますか
  a: 出荷は2027年3月18日に始まる予定です。クラウドファンディングの納期は遅れることがあります。
- q: 日本で買えますか
  a: 国内の販売店や代理店は確認できていません。Crowd Supplyでの募集に出資して入手します。送料は日本を含む米国以外の地域向けで18ドルとされています。
- q: 技適は必要ですか
  a: 無線機能のない基板モジュールなので、技適の対象外です。
---

ブルガリアのオープンソースハードウェア設計者、Leon ANAVIが「ANAVI I2C TPM 2.0」の募集をCrowd Supplyで始めた。Raspberry Pi用のセキュリティモジュールで、CNX Softwareが2026年11月19日に伝えた。**クラウドファンディングの案件で、まだ製品として出荷されたものではない。** 出資は購入ではなく、納期の遅れや仕様の変更が起きうる。

## 何ができるのか

載っているのはInfineonの「OPTIGA SLB 9673」というTPM 2.0チップ。ディスク暗号化の鍵の保管、暗号処理、ハードウェア乱数生成（TRNG）に使える。同じANAVIの前作は、SPI接続のSLB 9672を載せた「ANAVI TPM 2.0」で、今回はI2C接続の後継にあたる。

Raspberry Piの40ピンヘッダーに接続する5ピンのI2Cヘッダー（I2C、リセット、3.3V、GND）を持ち、すべてのRaspberry Piで使える。ほかの40ピン互換ボードにも「おそらく流用できる」とCNX Softwareは書いている。専用のソフトは要らない。Raspberry PiのLinuxカーネルに入っているデバイスツリーオーバーレイ（tpm-slb9673.dtbo）に対応していて、Raspberry Pi OSなどで追加の準備なしに動く。暗号化パーティションの作り方は、ANAVIがチュートリアルで公開している。

| 項目 | 内容 |
|---|---|
| TPMチップ | Infineon OPTIGA SLB 9673（TPM 2.0） |
| 仕様 | TCG TPM Library 1.59、PC Client PTP 1.05 |
| 大きさ | 16.5×12.8mm |
| 形状 | 横向きヘッダー版／縦向き（90度）ヘッダー版 |
| 設計データ | KiCad、CC BY-SA 4.0で公開 |
| OSHWA認証 | BG000154 |

## 価格と出荷

Crowd Supplyでの価格は、横向きが20ドル、縦向きが21ドル。送料は米国向けが8ドル、そのほかの地域は18ドルで、出荷は2027年3月18日に始まる予定とされる。価格と日程はCNX Softwareの記事の値で、Crowd Supplyの募集ページはこちらから読めなかったため、支援者数や調達額は確認できていない。独立したレビューも、今のところ見つかっていない。

実行者のLeon ANAVIは、2017年の赤外線pHAT以降、年に1枚ほどのペースでオープンソースの基板を作ってきた。今回の基板の裏面には「Made in Plovdiv, Bulgaria」と印字されている。

## 日本で買える？使える？

**国内の販売店や代理店は確認できていない。入手はCrowd Supplyでの出資になる。** 日本向けの送料は「米国以外」の18ドルとされるが、日本への発送可否はプロジェクトページで確かめてほしい。

無線機能のない基板なので、技適の対象外。電波法の心配はなく、届いたらそのままRaspberry Piに挿して使える。関税や消費税は別にかかる。

すぐに試したい人には、同じSLB 9673を載せたInfineon公式のRaspberry Pi向け評価ボード（OPTIGA TPM 9673 RPI EVAL）がある。国内ではマクニカやFarnellの日本語ページに掲載があるが、在庫と価格は確認できていない。同じ用途の手軽な国内販売品は、探した範囲では見つからなかった。
