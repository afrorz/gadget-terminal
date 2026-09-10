---
title: Seeed Studio、ファームウェアを書き換えられる50ドルの電子ペーパー端末「reTerminal Sticky」
seo_title: reTerminal Stickyは50ドル、技適は未確認
keyword: reTerminal Sticky
slug: seeed-reterminal-sticky
category: pc
date: 2026-09-11
kicker: Seeed Studioが、磁石で冷蔵庫などに貼り付けられる3.97インチ電子ペーパー端末「reTerminal Sticky」を49.90ドルで予約受付中。ESP32-S3を搭載し、有志が公開する複数のオープンソースファームウェアを書き込んで挙動を変えられる。
tags:
- Seeed Studio
- reTerminal Sticky
- ESP32
- 電子ペーパー
- 変わり種
x_hook: 本体価格49.90ドルの電子ペーパー端末に、天気表示・電卓・カードゲームのライフカウンターなど有志製のファームウェアを自由に書き込める。Wi-FiとBluetoothを積むが、技適に関する記載はどこにも見当たらない。
images:
- url: "https://www.seeedstudio.com/sticky/playground-registry/sticky-voice-companion/assets/preview.webp"
  caption: 天気・時刻・室内の温湿度を表示する「Voice Companion」ファームウェアを書き込んだ状態
- url: "https://www.seeedstudio.com/sticky/playground-registry/sticky-calculator/assets/preview.webp"
  caption: レトロな電卓アプリ「Datamath」を模したファームウェアの例。タッチ操作で計算できる
- url: "https://www.seeedstudio.com/sticky/playground-registry/sticky-lotus/assets/sticky-lotus.webp"
  caption: カードゲーム用のライフカウンター表示。有志によるオープンソースファームウェアの一つ
credit: Seeed Studio 公式製品ページ
faq:
- q: 日本で買えますか
  a: Seeed Studioの公式サイトから予約注文できますが、発送元は中国倉庫で、日本への発送可否は商品ページに明記されていません。掲載時点で日本の代理店での取り扱いは確認できていません。
- q: 技適は取得していますか
  a: reTerminal StickyはWi-Fi 4とBluetooth 5.0を搭載していますが、公式製品ページや仕様ドキュメントに技適・FCC・CEなどの認証に関する記載は見当たらず、掲載時点で確認できていません。日本国内で電波を出して使うには技適の取得が前提になります。
- q: いくらですか
  a: 49.90ドル(10個以上購入で47.90ドル)です(掲載時点)。
- q: ファームウェアは自分で作れますか
  a: Seeed Studioは「Playground」としてオープンソースのファームウェア集を公開しており、電卓・2048ゲーム・音声アシスタント・カードゲーム用カウンターなど複数の作例が既に配布されています。ESP32-S3向けの開発環境があれば、独自のファームウェアを書き込むこともできます。
sources:
- title: "reTerminal Sticky is a $50 E Ink gadget with flashable firmware that can be a refrigerator sign or a pocket-sized eReader"
  url: https://liliputing.com/reterminal-sticky-is-a-50-e-ink-gadget-with-flashable-firmware-that-can-be-a-refrigerator-sign-or-a-pocket-sized-ereade/
  publisher: Liliputing
- title: "reTerminal Sticky"
  url: https://www.seeedstudio.com/reTerminal-Sticky-p-6861.html
  publisher: Seeed Studio
- title: "reTerminal Sticky — The note your family can see"
  url: https://www.seeedstudio.com/sticky/
  publisher: Seeed Studio
---

深圳のメーカーSeeed Studioが、磁石で冷蔵庫やホワイトボードに貼り付けられる電子ペーパー端末「reTerminal Sticky」を49.90ドルで予約受付中だ。**特徴は、ファームウェアを書き換えることで挙動を変えられる点にある。** 天気表示・伝言板・電子書籍リーダーなど、有志が公開するオープンソースファームウェアを書き込んで使う設計で、Seeed Studio自身が「Playground」としてその一覧を公開している。

## 3.97インチの電子ペーパーにESP32-S3

本体は106×65.5×7.3mm、重さ70g。3.97インチの電子ペーパータッチスクリーン(800×480、235ppi、4階調グレースケール)を搭載し、マイコンはESP32-S3R8。750mAhバッテリーをUSB-Cで充電し、microSDカードにも対応する。通信はWi-Fi 4とBluetooth 5.0。温湿度センサー・6軸IMU・マイク・スピーカー・物理ボタン3個を備え、背面には固定用のマグネットが内蔵されている。

配布されているファームウェアには、TRMNLのような情報ダッシュボード、Crosspointによる電子書籍リーダー、ESPHome/OpenDisplayによるHome Assistant連携のほか、レトロ電卓や2048ゲーム、トレーディングカードゲーム用のライフカウンターといった遊び用のものまである。マイクとAIボイスボタンを使い、音声メモをそのまま電子ペーパーに表示する機能も持つ。

## 日本から見るとどうか

reTerminal StickyはWi-FiとBluetoothを内蔵する無線機器だが、公式製品ページにも仕様ドキュメントにも、技適はもちろんFCCやCEを含めた認証についての記載が見当たらない。日本国内で電波を出して使うには技適の取得が前提になるため、この点が確認できないまま個人輸入で使うのはリスクがある。発送元も「China Warehouse」とだけ記載されており、日本への発送に対応しているかどうかも商品ページからは読み取れない。Seeed Studioは国内でSwitch Scienceなどの代理店を通じて技適取得済みの製品を扱ってきた実績があるが、reTerminal Sticky自体がその対象になるかは掲載時点で不明だ。ESP32-S3という汎用性の高いチップを積んでいるだけに、技適の扱いは購入前に必ず確認したい。

なお、この製品はKickstarterやIndiegogoのようなクラウドファンディングではなく、Seeed Studio自身による直接予約販売である点も補足しておく。
