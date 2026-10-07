---
title: Minisforum「ESP4B」はPCIeスロット1本にM.2を4枚、OCuLinkと20Gbps Type-Cまで載せた拡張カード
slug: minisforum-esp4b-4-nvme-card
seo_title: Minisforum ESP4B、M.2を4枚挿せる拡張カード
x_hook: PCIeスロット1本でNVMe SSDを4枚挿せるMinisforumの拡張カード「ESP4B」は、OCuLinkで最大4台のSATA HDD、20Gbps出るType-Cまで同居。バイファケーション非対応のマザーでも使えるのが売りで、公式ストアは135.90ドル。
keyword: ESP4B
category: pc
date: 2026-10-08
kicker: Minisforumが、PCIe 4.0 x4接続でM.2 NVMe SSDを4枚、OCuLinkとUSB 3.2のType-Cを1枚に収めた拡張カード「ESP4B」を公式ストアで売り出した。セール価格は135.90ドル（通常169ドル）、出荷は10月下旬の見込み。
tags:
- Minisforum
- ESP4B
- NVMe
- OCuLink
- 拡張カード
faq:
- q: ESP4Bはいくらですか
  a: Minisforumの米国公式ストアでは、掲載時点でセール価格135.90ドル、通常価格169ドルです。
- q: M.2はすべてフル速度で使えますか
  a: 使えません。公式仕様では、SSD1とSSD2がPCIe 4.0 x4まで、SSD3とSSD4がPCIe 4.0 x2までです。4枚すべて挿すと全スロットがx2動作になります。
- q: 日本で買えますか
  a: 掲載時点で、日本のMinisforum取り扱い店や国内代理店による発売情報は確認できていません。米国公式ストアの出荷予定は10月下旬で、日本への発送可否はこちらでは確認できていません。
- q: 技適は必要ですか
  a: ESP4Bは無線機能を持たないPCIe拡張カードで、Wi-FiやBluetoothの仕様記載はありません。技適の対象にはならない製品です。
images:
- url: "https://store.minisforum.com/cdn/shop/files/MinisforumESP4B.png"
  caption: ESP4Bの外観。黒いカバーの上面に小型ファン、ブラケット側にOCuLinkとUSB Type-C
- url: "https://store.minisforum.com/cdn/shop/files/MinisforumESP4B-front.png"
  caption: ブラケット側の端子。左がOCuLink、右がUSB Type-C
- url: "https://store.minisforum.com/cdn/shop/files/MinisforumESP4B-Top.png"
  caption: 上から見た状態。PCIe x4のエッジコネクタとファンが見える
credit: Minisforum 公式ストア
sources:
- title: MINISFORUM ESP4B PCIe to 4 × NVMe M.2 Expansion Card
  url: https://store.minisforum.com/en-os/products/minisforum-esp4b-pcie-to-4-nvme-m-2-expansion-card
  publisher: Minisforum（公式）
- title: Minisforum Brings AMD B850 Chipset To Its AIC, Offering Support For 4x M.2 Ports, OCuLink And 20 Gbps Type-C Port
  url: https://wccftech.com/minisforum-brings-amd-b850-chipset-to-its-aic/
  publisher: Wccftech
- title: Minisforum puts AMD B850 chipset on $136 PCIe card with four M.2 slots
  url: https://videocardz.com/newz/minisforum-puts-amd-b850-chipset-on-136-pcie-card-with-four-m-2-slots
  publisher: VideoCardz
---

Minisforumが「ESP4B」を出した。ホストはPCIe 4.0 x4で、カード上にM.2 NVMe SSDのスロットを4つ、ブラケット側にOCuLinkポートを1つとUSB 3.2のType-C（最大20Gbps）を1つ備える。米国公式ストアの掲載時点の価格はセール価格135.90ドル、通常価格169ドルで、出荷予定は10月下旬とされている。

## 何ができるカードか

マザーボードのPCIeスロットが1本空いていれば、SSDを最大4枚増やせる。公式の説明では、マザーボード側のバイファケーション（スロットの分割）に頼らず、カード上のチップがレーンを振り分ける。Wccftechによれば、チップはAMD Promontory 21系で、同誌は「B850チップセットをカードに載せた」と表現している。一般にバイファケーションが使えないマザーでも複数のSSDを挿せる点が、この種のカードの価値になる。

OCuLinkポートには付属の専用ケーブルをつなぐと、SATA 3.0のHDDを最大4台使える。SATA HDDの電源ケーブルは別途用意する必要がある。

| 項目 | 仕様（公式ストアの記載） |
|---|---|
| ホスト接続 | PCIe 4.0 x4（x4以上のスロットに対応） |
| M.2スロット | 4つ（NVMe）。SSD1・SSD2はPCIe 4.0 x4まで、SSD3・SSD4はPCIe 4.0 x2まで |
| 4枚すべて挿した場合 | 全スロットがPCIe 4.0 x2動作 |
| OCuLink | 1ポート。専用ケーブルでSATA 3.0 HDDを最大4台 |
| USB | Type-C 1ポート、USB 3.2、最大20Gbps、5V/3A |
| 電力管理 | ASPM対応 |
| 寸法 | 69 × 168mm |
| 同梱品 | SATAデータケーブル、固定ストリップ、ネジ一式、マニュアル |

## 実測の報告

Wccftechが紹介したRedditユーザーの検証では、SSD2枚のときは各SSDがPCIe 4.0 x4で動き、Kingstonの Gen4 SSDで読み出し約6.1GB/sが出た。4枚すべて挿すとx2動作に切り替わり、読み出しは約3.3GB/sになったという。2011年製のDell OptiPlexや、ARMベースのMinisforum機でも認識したと報告されている。これは1人のユーザーの検証で、編集部では確認していない。

SSDを4枚挿した構成では1枚あたりの帯域が半分になるため、速度を取るなら2枚まで、容量を取るなら4枚、という使い分けになる。ホスト側が4.0 x4であることも前提で、古いPCIe 3.0スロットでは上限がその分下がる。

## 日本から見るとどうか

技適：ESP4Bは無線機能の無いPCIe拡張カードで、仕様にもWi-FiやBluetoothの記載は無い。技適の対象外と判断してよい。ACアダプターなどの電源機器は同梱されない。

入手：掲載時点で、国内代理店や日本の販売店によるESP4Bの発売情報は見つけられていない。「ESP4B 国内 発売」と「ESP4B Makuake」で検索したが、国内の記事や販売ページは出なかった。米国公式ストアには出荷予定が「10月下旬」と書かれているだけで、日本への発送可否や送料・関税はここでは確認できていない。購入前にストアで日本の住所を入れて確かめる必要がある。

価格：セール価格135.90ドルは掲載時点のもので、通常価格は169ドル。米国の公式ストアは2年保証をうたっているが、海外から買った場合に日本でその保証を受けられるかは確認できていない。

向いている人：空きPCIeスロットがあるデスクトップや自作のNAS機で、M.2を増やしたい人。一方、マザーのM.2が余っている人には不要で、バイファケーション対応のマザーなら安価な単純分割カードでも足りる。国内発売を待つか、Minisforumの国内取扱店の入荷を確かめてから動くのが安全だ。
