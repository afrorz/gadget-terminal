---
title: KickstarterでKVM機器初の大ヒットを飛ばしたJetKVMが、マッチ箱サイズの無線版「Mini W」を42ドルで発表
seo_title: JetKVM Mini Wは42ドル、10月26日発売
slug: jetkvm-mini-w-wireless-kvm
category: pc
date: 2026-09-21
kicker: KVM over IP機器「JetKVM」の開発元が、42×42×23mmのマッチ箱サイズに小型化した新モデル「JetKVM Mini」シリーズを発表した。有線(Ethernet)版のMiniは1個39ドル・3個パック33ドル/個、無線(Wi-Fi)版のMini Wは1個42ドル・3個パック36ドル/個(いずれも掲載時点)。発売は2026年10月26日を予定する。
tags:
- JetKVM
- KVM over IP
- ESP32-P4X
- リモート管理
- オープンソース
x_hook: 遠隔からPCのBIOS画面まで操作できるKVM機器が、マッチ箱サイズで42ドルまで下がった。無線版はWi-Fi 6を積むが、技適の取得状況は公式サイトに記載が無く未確認だ
images:
- url: "https://jetkvm.com/assets/jetkvm_mini_w_angle-Jauzu1Hr.webp"
  caption: JetKVM Mini Wの斜め上からの外観。天面のディスプレイにIPアドレスと接続中のWi-Fi名、USB・HDMIの接続状態が表示されている
- url: "https://jetkvm.com/assets/jetkvm_mini_w_back-CyYmvkRp.webp"
  caption: 背面のポート部。USB-C(電源または映像取り込み用と思われる端子)が2つとHDMI入力を1つ備える
- url: "https://jetkvm.com/assets/jetkvm_mini_w_front-DXNRbRZi.webp"
  caption: 正面からの外観。手のひらに収まる立方体に近い筐体で、天面のディスプレイに稼働状況が表示される
credit: JetKVM 公式サイト(jetkvm.com)
buy:
- name: JetKVM Mini W(無線版)
  url: https://jetkvm.com/products/jetkvm-mini-w
  price: 1個42ドル、3個パック36ドル/個(いずれも掲載時点、2026年10月26日発売予定)
  ships_jp: false
  giteki: 未取得
  note: 国際発送に日本が含まれるかどうかは公式サイト上に明記が無く、購入前に個別確認が必要。Wi-Fi(IEEE 802.11ax、2.4/5GHz)とBluetooth LEを搭載するため、国内で無線機能を使うには技適が必要だが、取得状況についての記載は見当たらない。
- name: JetKVM Mini(有線版)
  url: https://jetkvm.com/products/jetkvm-mini
  price: 1個39ドル、3個パック33ドル/個(いずれも掲載時点、2026年10月26日発売予定)
  ships_jp: false
  giteki: 対象外
  note: Ethernet接続のみで無線モジュールを搭載しないモデル。無線機能自体が無いため技適の対象外になる。国際発送に日本が含まれるかは公式サイト上に明記が無く、購入前に個別確認が必要。
faq:
- q: 日本で買えますか
  a: 公式サイトから直接注文できますが、日本への国際発送に対応するかどうかは掲載時点でページ上に明記されておらず、確認できていません。発売は2026年10月26日の予定です。
- q: 技適は取得していますか
  a: 無線版のMini Wは確認できていません。Wi-Fi 6・Bluetooth LEを搭載するため、国内で無線機能を使うには技適の取得が必要です。有線版のMiniは無線モジュール自体を搭載しないため、技適の対象外です。
- q: いくらですか
  a: 有線版のMiniは1個39ドル・3個パック33ドル/個、無線版のMini Wは1個42ドル・3個パック36ドル/個です(いずれも掲載時点)。円換算は為替により変動するため記載していません。
- q: 前作のJetKVMとは何が違いますか
  a: 初代JetKVMはEthernetポートを備えた据え置きサイズの筐体でしたが、Miniシリーズは42×42×23mmまで小型化し、無線版のMini Wでは新たにWi-Fi接続に対応しました。ファームウェアは初代同様オープンソースです。
sources:
- title: "This $42 box gives you remote access even if Windows is dead"
  url: https://newatlas.com/computers/jetkvm-mini-remote-access/
  publisher: New Atlas
- title: "Introducing JetKVM Mini"
  url: https://jetkvm.com/blog/introducing-jetkvm-mini
  publisher: JetKVM
- title: JetKVM Mini W 公式製品ページ
  url: https://jetkvm.com/products/jetkvm-mini-w
  publisher: JetKVM
- title: "JetKVM Kickstarter: $4.37M for an Open-Source KVM-over-IP Device"
  url: https://www.itechguides.com/tens-of-thousands-of-backers-pledged-more-than-4-million-to-open-source-kvm-over-ip-project-on-kickstarter/
  publisher: iTechGuides
---

KVM over IP機器「JetKVM」の開発元が、新モデル「JetKVM Mini」シリーズを発表した。42×42×23mmとマッチ箱サイズに小型化し、有線(Ethernet)版の「Mini」は1個39ドル・3個パック33ドル/個、無線(Wi-Fi)版の「Mini W」は1個42ドル・3個パック36ドル/個で、発売は**2026年10月26日**を予定する(価格はいずれも掲載時点)。

KVM over IPは、対象のPCにHDMIとUSBで接続し、ネットワーク経由でキーボード・マウス・画面をリモート操作できるようにする機器だ。OSが起動しない状態やBIOS画面の操作もできるため、リモートでのサーバー管理やトラブル対応によく使われる。

## 仕様とMini/Mini Wの違い

| 項目 | Mini(有線) | Mini W(無線) |
|---|---|---|
| 価格(1個/3個パック) | 39ドル/33ドル | 42ドル/36ドル |
| 接続方式 | RJ45 Ethernet | Wi-Fi(IEEE 802.11ax、2.4/5GHz) |
| Bluetooth | 非搭載 | Bluetooth LE対応 |
| プロセッサ | ESP32-P4X(H.264ハードウェアエンコーダ搭載) | 同左 |
| ネイティブ映像解像度 | 1080p/30fpsまたは720p/60fps | 同左 |
| USB規格 | USB 2.0 High Speed(480Mbps)+ Full Speed(12Mbps) | 同左 |
| サイズ | 42×42×23mm | 同左 |
| オープンソース | ファームウェアはオープンソース | 同左 |

公式ブログによれば、JetKVM独自のクラウドサービス「JetKVM OS Services」を使うことで最大4K相当の解像度にも対応するという。ストレージはmicroSDカードスロットを備える(カードは別売)。

## 前作は5万ドルの目標に対し数百万ドルを集めた実績

JetKVMの初代モデルは2024年にKickstarterでクラウドファンディングを実施し、目標額5万ドルに対して数万人の支援者から数百万ドル規模の資金を集めたと報じられている(iTechGuidesの報道では支援者数万人・調達額437万ドルとされるが、集計時点によって数字にばらつきがあり、正確な最終値は本メディアでは確認できていない)。今回のMiniシリーズはクラウドファンディングではなく、公式サイトでの通常の予約注文という形をとっている。

## 日本から見るとどうか

無線版のMini Wは**Wi-Fi 6(IEEE 802.11ax)とBluetooth LEを搭載しており、国内で無線機能を使うには技適の取得が必要**になる。公式サイト・公式ブログのいずれにも技適についての記載はなく、取得状況は確認できていない。一方、有線版のMiniは無線モジュールを搭載しないため、**技適はそもそも対象外**だ。日本国内で技適の心配なく使いたい場合は、無線版ではなく有線版のMiniを選ぶのが無難だろう。

日本への国際発送に対応するかどうかも、公式サイト上には明記がなく確認できていない。初代JetKVMはKickstarterのBackerKit経由で世界各国に発送された実績があるが、今回のMiniシリーズが同様に日本へ届くかは購入前に個別に確認する必要がある。価格・発売日は2026年10月26日発売という発表段階の情報で、いずれも掲載時点の値である。
