---
title: Elecrow ThinkNode M9 — 電波が届かない場所で文字を送る、75ドルのQWERTY端末
seo_title: "ThinkNode M9は75ドル、Meshtastic版も。日本で使える？"
slug: elecrow-thinknode-m9
keyword: ThinkNode M9
category: weird
date: 2026-08-16
modified: 2026-11-23
kicker: BlackBerry の子孫のような見た目だが電話ではない。LoRa と MeshCore で、携帯圏外どうしを直接つなぐメッシュ通信端末。
x_hook: 基地局が無くても文字は届く。ただし日本の電波法上、そのままでは使えない。
tags: [LoRa, MeshCore, Meshtastic, ESP32, 変わり種]
giteki:
  status: 確認できない
  number: []
  checked: 2026-11-23
  radio: "LoRa / Wi-Fi 4 / Bluetooth 5.0"
  note: "総務省DBで「ThinkNode」「Elecrow」「エレクロウ」と型番「TNM9」「LMM15409D」「LMM16509D」を引いて該当なし（2026-11-23）。販売中は868MHz・915MHz版のみ"
embeds:
  - type: youtube
    id: l7ITJTsp9CY
    caption: ThinkNode M9 の実機レビュー。QWERTYキーと画面の大きさが分かる（andy kirby）
images:
  - url: "https://www.elecrow.com/media/wysiwyg/products/2026/LMM16509D/ThinkNode_M9_all-in-one_terminal_1.jpg"
    caption: 本体正面。2.4インチカラーLCDとMeshCoreのメニュー画面を表示した状態
  - url: "https://www.elecrow.com/media/wysiwyg/products/2026/LMM16509D/ThinkNode_M9_with_retro_keyboard_and_display.jpg"
    caption: レトロ調のQWERTYキーボード全体
  - url: "https://www.elecrow.com/media/wysiwyg/products/2026/LMM16509D/ThinkNode_M9_with_GPS_function_and_2300mah_battery.jpg"
    caption: 内部構造。LoRa用・Wi-Fi/BT用の2本のアンテナと2,300mAhバッテリーが分かる分解図
credit: Elecrow 公式製品ページ
faq:
- q: 日本で使えますか
  a: いま売られている海外版は、日本でそのまま電波を出すことはできません。日本で免許不要のLoRaは920MHz帯（ARIB STD-T108）で、技術基準適合証明（技適）を取得した無線機である必要があります。Elecrowが売っているのは868MHz（欧州）と915MHz（米国）の版だけです。日本向けの版と技適が出れば使えるようになります。
- q: 技適は取得していますか
  a: 掲載時点では確認できていません。2026年11月23日に総務省の技適データベースを「ThinkNode」「Elecrow」と型番で引き直しても見つかりませんでした。米国向けのFCC ID（2BDNA-TNM9）はユーザーマニュアルに載っています。
- q: いくらですか
  a: Elecrowの直販で74.90ドルからです（2026年11月23日時点）。MeshCore版とMeshtastic版のどちらも同じ価格で、送料は別です。米国や豪州の販売店では、89ドルや109ドルで売られている例もあります。
- q: Meshtastic版はありますか
  a: あります。公開時点では「準備中」でしたが、その後Elecrowが「ThinkNode M9 Meshtastic」（型番LMM15409D）を出しました。MeshCore版とMeshtastic版は別の製品で、1台で使えるのはどちらか一方です。Meshtasticの公式ドキュメントにも対応機種として載っています。
- q: 日本のAmazonで買えますか
  a: 2026年11月23日時点で、Amazon.co.jpや国内の電子部品店での取り扱いは見つかりませんでした。Elecrowの直販サイトは円表示に切り替えられますが、届くのは868MHzか915MHzの版です。
- q: 1台だけ買えば使えますか
  a: 使えません。端末どうしが直接つながる方式なので、最低2台、実用的にはグループで導入するタイプの製品です。
sources:
  - title: "Elecrow ThinkNode M9 is a phone-like mesh communicator with a 2.4 inch screen, QWERTY keyboard, and LoRa"
    url: https://liliputing.com/elecrow-thinknode-m9-is-a-phone-like-mesh-communicator-with-a-2-4-inch-sccreen-qwerty-keyboard-and-lora/
    publisher: Liliputing
  - title: "ThinkNode M9 Meshtastic Communication Terminal with Full Keyboard"
    url: https://www.elecrow.com/thinknode-m9-meshtastic-communication-terminal-with-full-keyboard-2-4inch-lcd.html
    publisher: Elecrow
  - title: "ThinkNode M9 Selection Guide"
    url: https://www.elecrow.com/blog/thinknode-m9-product-selection-and-overview.html
    publisher: Elecrow
  - title: "ThinkNode Series"
    url: https://meshtastic.org/docs/hardware/devices/elecrow/thinknode/
    publisher: Meshtastic
  - title: "ThinkNode M9 for Meshtastic User Manual"
    url: https://www.elecrow.com/download/product/LMM15409D/ThinkNode_M9_for_Meshtastic_User_Manual.pdf
    publisher: Elecrow
  - title: "ThinkNode M9 Meshcore Standalone Communicator"
    url: https://www.elecrow.com/thinknode-m9-meshcore-communication-terminal-with-full-keyboard-2-4inch-lcd-esp32-s3-lr1110-gps-2300mah.html
    publisher: Elecrow
---

**Elecrow ThinkNode M9** は、iPhone と Android ではなく BlackBerry と Palm Treo の側に進化した世界線から来たような端末だ。実際にはスマートフォンではない。通話機能はなく、携帯電話網も使わない。**LoRa** による長距離無線と **MeshCore** を使って、端末どうしが直接メッセージをやり取りする通信機である。

## 11月23日の追記：Meshtastic版が出た

公開から3か月で分かったことをまとめる。

- **Meshtastic版が出た。** 公開時点のElecrowの販売ページは、Meshtastic版を「予定しているが、まだ無い」としていた。いまは「ThinkNode M9 Meshtastic」（型番LMM15409D）が別の製品として売られていて、Meshtasticのファームウェアを書き込んだ状態で届く。MeshCore版（型番LMM16509D）と見た目は同じだが、1台で使えるのはどちらか一方。Elecrowは、先にファームウェアの種類を、次に周波数を選ぶよう案内している
- **Meshtasticの公式ドキュメントに載った。** 対応機種の一覧に「ThinkNode M9」の項目ができ、専用のファームウェアと、画面で操作するMeshtastic UI版のファームウェアの2つが用意されている。Elecrowのwikiは、ほかのESP32-S3向けのファームウェアはピンの割り当てが違うので、M9専用の物だけを入れるよう注意している
- **価格は据え置き。** Elecrowの直販は、MeshCore版・Meshtastic版とも74.90ドルから（11月23日時点）。米国の販売店では89ドル、豪州では109ドルで売られている例がある
- **周波数は868MHzと915MHzの2つ。** Elecrowによれば、周波数ごとに無線まわりの部品が違い、設定で切り替える物ではない。日本の920MHz帯の版は、11月23日時点で出ていない
- **仕様が少し詳しくなった。** Meshtasticのドキュメントでは、記憶領域16GB、測位はGPS・BeiDou・Galileo・GLONASS、方位センサーも積む。Elecrowは、待ち受けで2〜3日もつとマニュアルを引いて説明している
- **販売ページは「12月上旬に出荷予定」と表示している。** 「在庫あり」の表示と並んでいて、注文してから届くまでの時期は、注文時に確かめたほうがいい

## スペック

| 項目 | 内容 |
|---|---|
| SoC | ESP32-S3R8 |
| 無線（メッシュ） | LoRa モジュール Semtech LR1110 |
| その他無線 | Wi-Fi 4（802.11n）、Bluetooth 5.0 |
| 測位 | GPS・BeiDou・Galileo・GLONASS（Meshtasticのドキュメントによる） |
| ディスプレイ | 2.4インチ LCD / 320×240（非タッチ） |
| 入力 | 37キー QWERTY ＋ 操作用ファンクションキー |
| バッテリー | 2,300mAh |
| 記憶領域 | 16GB（Meshtasticのドキュメントによる） |
| 端子 | USB 2.0 Type-C（充電） |
| 音 | ブザー（スピーカーではない） |
| サイズ | 126 × 67 × 10mm |
| 重量 | 123g |
| 周波数 | 868MHz（欧州）／915MHz（米国）の2つの版 |
| ファームウェア | MeshCore版／Meshtastic版（別の製品として販売） |
| 価格 | 74.90ドルから（Elecrow、掲載時点） |

近い立ち位置の製品としては LILYGO の T-Deck Pro シリーズがある。

## 何が面白いのか

この手のデバイスの本質は「インフラに依存せずに文字が届く」ことにある。基地局も、インターネットも、契約も要らない。端末どうしが中継し合ってメッシュを作り、ホップを重ねてメッセージを運ぶ。

**スマホと決定的に違うのは、通信が「圏内かどうか」ではなく「近くに仲間の端末があるかどうか」で決まる点だ。** だから単体で買っても意味がなく、最低2台、実用的にはグループで導入するタイプの製品になる。登山・キャンプ、イベント運営、アマチュア無線的な実験、災害時の備えといった文脈で使われている。

75ドルという価格は、フルキーボードと GPS を積んだ完成品としてはかなり安い。ESP32-S3 なので、ファームウェアを自分で書き換えて遊ぶ余地も大きい。

## 日本で買える？使える？

**今の海外版は、日本ではそのまま使えない。日本向けが出るかどうかが鍵になる。**

LoRa の周波数は国ごとに違う。日本で免許なしに使えるのは 920MHz 帯（ARIB STD-T108）で、**技術基準適合証明（技適）を取った無線機**に限られる。海外向けの LoRa 機は 868MHz（EU）や 915MHz（US）向けで出荷されることが多い。

ただ、これは「日本には来ない」という意味ではない。海外メーカーが日本発売に合わせて技適を取るのはよくあることで、Gadget Terminal が先に紹介した製品でも、公開後に日本で発売や予約が始まったものがいくつもある。

11月23日に見直した時点でも、日本の読者にとっての状況は大きくは変わっていない。Elecrowが売っているのは868MHzと915MHzの版で、総務省の技適データベースを「ThinkNode」「Elecrow」と型番で引いても見つからなかった。Amazon.co.jpや国内の電子部品店での取り扱いも見つからない。一方で、Meshtastic版が出たことで、MeshCore版とは別に、Meshtasticの端末とやり取りできる版も選べるようになった。日本向けの版が出たときに、選ぶ理由がひとつ増えたことになる。

日本上陸を待つうえで、まだ分かっていないのは次の3つ。

- 日本向けの 920MHz 帯モデルが出るか
- 技適を取るか
- 国内で正規に売られるか

今すぐ国内で LoRa メッシュを試したいなら、技適を取った 920MHz 帯の製品を選ぶのが確実だ。ThinkNode M9 の日本向けが出たら、この記事に追記する。
