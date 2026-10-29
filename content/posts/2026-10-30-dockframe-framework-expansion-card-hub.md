---
title: HW Media Lab「DockFrame」、Frameworkの拡張カードを差して使うUSB-Cハブ。テスター・電源・ブレッドボードのカードもあり、Crowd Supplyで119ドルから
slug: dockframe-framework-expansion-card-hub
seo_title: DockFrameは119ドル、拡張カード式ハブ
x_hook: |
  ノートPCの拡張カードを、机の上に差せる箱がある。
  「DockFrame」はFrameworkの拡張カード用スロットを持つUSB-Cハブ。テスターや可変電源のカードまで用意された。
  ・Crowd Supplyで119ドルから
keyword: DockFrame
category: pc
date: 2026-10-30
kicker: 米ワイオミング州のHW Media Labが、Frameworkの拡張カード規格に合わせたモジュール式USB-Cハブ「DockFrame」をCrowd Supplyで募集している。ハブに差すだけでなく、マルチメーター、0.8〜20Vの可変電源、ブレッドボード用の専用カードも用意し、支援価格は119〜399ドル。
tags:
- DockFrame
- HW Media Lab
- Framework
- USB-Cハブ
- Crowd Supply
origin: SHR ワイオミング
deadline: 2027-01-15
giteki:
  status: 確認できない
  number: []
  checked: 2026-10-30
  radio: Wi-Fi（2.4GHz）/ Bluetooth LE
  note: "計測カードにESP32-S3搭載。技適の記載は公式ページに無い"
images:
- url: "https://www.crowdsupply.com/img/d3d2/823a0b51-49ad-4d85-9ac6-a9c491e4d3d2_project-main.jpg"
  caption: 試作機の天面。レゴ互換のスタッド付きで、タイルを貼って飾れる。下部のコネクタには計測用のバナナジャックが刺さっている
credit: HW Media Lab / Crowd Supply（DockFrame プロジェクトページ）
sources:
- title: DockFrame（Crowd Supply。金額・支援者数は2026年10月30日時点）
  url: https://www.crowdsupply.com/hw-media-lab/dockframe
  publisher: Crowd Supply（公式）
- title: "Intel Moon Lake could replace Intel N100/N150, crowdfunding begins for a USB dock made of Framework Expansion cards...（Liliputing）"
  url: https://liliputing.com/intel-moon-lake-could-replace-intel-n100-n150-crowdfunding-begins-for-a-usb-dock-made-of-framework-expansion-cards-and-tuxedo-launches-a-linux-mini-pc-with-intel-panther-lake-liliputing-news-roundu/
  publisher: Liliputing
alternatives:
  - name: UGREEN Revodok 10-in-1 USB-Cドッキングステーション
    why: HDMI2系統・LAN・100W PD給電まで入った10ポートの国内流通品。拡張カードを持っていなくても、机の上のポートを今日から増やせる。
    url: https://item.rakuten.co.jp/ugreen-gear/45366/
    merchant: rakuten
    image: "https://thumbnail.image.rakuten.co.jp/@0_mall/ugreen-gear/cabinet/10122288/45366.jpg"
faq:
- q: DockFrameはいくらですか
  a: Crowd Supplyの支援価格は119〜399ドルです（2026年10月30日時点）。ハブとミニハブカードの組は219ドル、ハブと3種のツールカードは369ドル、全部入りは399ドルで、いずれも送料込みと案内されています。
- q: 日本で買えますか
  a: 国内の販売は確認できていません（掲載時点）。Crowd Supplyは世界各国への無料配送を掲げていますが、日本向けの扱いは公式ページの範囲では確認できていません。
- q: 技適は取得していますか
  a: 公式ページに日本の技適の記載は確認できていません。計測カードにWi-FiとBluetooth LE（ESP32-S3）が載るため、無線機能のあるカードは国内で使う前に確認が必要です。
- q: いつ届きますか
  a: Crowd Supplyの表示では、現時点の注文は2027年6月8日出荷の予定です。製造方法や認証書類が確定していないため、遅れる可能性があります。
---

米ワイオミング州のHW Media Labが、Frameworkのノートパソコン用「拡張カード」を差して使うUSB-Cハブ「DockFrame」をCrowd Supplyで募集している。2026年10月30日時点で、支援額は1,623ドル、支援者は6人。目標額は5万ドルで、締切は2027年1月15日（日本時間で同日21時49分）だ。

**これはクラウドファンディングの募集で、製品の購入ではない。** 金額と支援者数は取得時点の値で、日々動く。メーカーは試作段階の写真を使っており、筐体の製法と色はまだ決まっていないと公式ページに書いている。

## 何ができるのか

Frameworkのノートや「Framework Desktop」では、USB-CやHDMI、SSDなどの拡張カードを差し替えて使う。DockFrameは、その拡張カードを机の上のハブに差して使うための箱だ。手元に余っているカードの置き場にもなり、Framework以外のUSB-Cが付いたパソコンにも使えると公式ページは説明している。

ハブ本体のUSB-Cコネクタは合計7つ。内訳は、カードを差す5か所、パソコンにつなぐ上流側1か所、別系統の給電入力（Supercharger）1か所で、7つすべてがデータ通信に使えるわけではない。

- **上流側：** 最大10Gbps。パソコンを最大60Wで充電できる
- **カード側のPD入力：** 最大100WのUSB PD入力に対応。充電器とカードは同じ位置に同時には差せない
- **カード側のDataポート（2つ）：** それぞれ最大10Gbps、出力7.5W
- **カード側のUSB/DisplayPort：** USBは最大10Gbps、DisplayPort Alt Modeで4K・60Hzまで。映像とデータを同時に使った場合の性能は検証中
- **Supercharger：** USB PD 3.1 EPRの入力から、絶縁した1対1の出力を最大240W取り出せる。パソコンの充電には足されない

天面にはレゴ互換のスタッドがあり、積み重ねたりタイルを貼ったりできる。

### 専用のツールカード

ハブに差すだけでなく、HW Media Labが作る専用カードが4種ある。

| カード | 内容 |
|---|---|
| Multimeter | 直流±60V・2Aまで、交流60Vピーク・2Aピーク、抵抗・静電容量・インダクタンスも測る。USBと測定回路を機能的に絶縁。商用電源と測定カテゴリの定格は無い |
| Power Supply | 0.8〜20Vの可変出力、最大3A。USB PD入力は最大100W。連続出力は温度で制限される |
| BreadBoard | 取り外せるXIAO ESP32-C5を載せた、ブレッドボード用のUSB-Cカード |
| Mini Hub | USB 3.0のポート2つ。上流は5Gbps共有 |

MultimeterとPower Supplyは、ESP32-S3を載せ、ブラウザのアプリからUSBまたはBluetooth LEで操作する。Power SupplyはWi-Fi経由でも操作できる。専用アプリのインストールは不要で、波形のグラフ表示とCSV出力ができる。

## 支援のコース

| コース | 内容 | 価格 |
|---|---|---|
| User Kit | ハブ、Mini Hubカード、ケーブル | 219ドル |
| Maker Kit | ハブ、Multimeter・Power Supply・BreadBoardの3カード、XIAO ESP32-C5 | 369ドル |
| Full Kit | ハブと4種のカード全部 | 399ドル |
| ハブのみ | カードは別途 | 掲載ページの価格帯は119〜399ドル（ハブ単体の価格は確認できていない） |

送料は世界無料で価格に含まれ、Crowd Supplyの米テキサス州の倉庫からMouser Electronicsが発送する。初回の生産は全8種類で合計200個で、需要に応じて増やす予定とされる。

## 注意点

公式ページに書かれているリスクがそのまま注意点になる。筐体の製造方法が未確定で、試作品の確認が済んでいないこと。EU・UK向けの適合宣言書は、署名前の確認用の写しであること。ファームウェアは初期で不具合がありうること。製造は中国で、米中間の関税が変わる可能性にも触れている。設計ファイルは、募集終了後にGitHubで公開する予定で、現時点では非公開だ。

測定カードは「機能的な絶縁」までで、商用電源に接続してはいけないと明記されている。家庭のコンセントの計測には使えない。

## 日本で買える？使える？

- **国内販売：** 国内の取り扱いや日本語の募集は確認できていない（掲載時点。「DockFrame 国内」「Makuake」で検索した）
- **日本への発送：** Crowd Supplyは世界各国への無料配送を掲げるが、日本が対象かどうかは、確認できた範囲では分からない
- **技適：** 無線を持つのは計測カード（Wi-Fi・Bluetooth LE）。技適の記載は公式ページに無く、確認できていない。ハブ本体とMini Hubカードに無線は無い
- **電源：** USB PDで動く機器で、国内の充電器でそのまま使える
- **Frameworkの拡張カード：** カードを持っていなくても、ハブとMini Hubだけで使える

行動の目安：手持ちの拡張カードを机で使いたい人、小さな計測器をまとめて欲しい人は、日本向け発送の可否と技適の扱いが出るのを待つ。ポートを増やすだけなら、国内で買えるドッキングステーションで足りる。
