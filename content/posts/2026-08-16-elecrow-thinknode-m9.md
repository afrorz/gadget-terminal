---
title: Elecrow ThinkNode M9 — 電波が届かない場所で文字を送る、75ドルのQWERTY端末
seo_title: "ThinkNode M9は75ドル、日本で使える？"
slug: elecrow-thinknode-m9
keyword: ThinkNode M9
category: weird
date: 2026-08-16
kicker: BlackBerry の子孫のような見た目だが電話ではない。LoRa と MeshCore で、携帯圏外どうしを直接つなぐメッシュ通信端末。
x_hook: 基地局が無くても文字は届く。ただし日本の電波法上、そのままでは使えない。
tags: [LoRa, MeshCore, Meshtastic, ESP32, 変わり種]
giteki:
  status: 確認できない
  number: []
  checked: 2026-08-16
  radio: "LoRa / Wi-Fi 4 / Bluetooth 5.0"
  note: "日本向け920MHz帯モデルの有無が不明"
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
  a: そのままでは使えません。日本で免許不要のLoRaは920MHz帯（ARIB STD-T108）で、技術基準適合証明（技適）を取得した無線機である必要があります。海外向けは868MHz（EU）や915MHz（US）向けで出荷されることが多く、技適のない機器で電波を出せば電波法違反となります。
- q: 技適は取得していますか
  a: 掲載時点で、日本向け920MHz帯モデルの有無、技適取得の有無、国内正規流通の有無のいずれも確認できていません。
- q: いくらですか
  a: 約75ドルで、Elecrowで販売中です。フルキーボードとGPSを積んだ完成品としては安い部類に入ります。
- q: 1台だけ買えば使えますか
  a: 使えません。端末どうしが直接つながる方式なので、最低2台、実用的にはグループで導入するタイプの製品です。
sources:
  - title: "Elecrow ThinkNode M9 is a phone-like mesh communicator with a 2.4 inch screen, QWERTY keyboard, and LoRa"
    url: https://liliputing.com/elecrow-thinknode-m9-is-a-phone-like-mesh-communicator-with-a-2-4-inch-sccreen-qwerty-keyboard-and-lora/
    publisher: Liliputing
  - title: "ThinkNode M9 Meshcore Standalone Communicator"
    url: https://www.elecrow.com/thinknode-m9-meshcore-communication-terminal-with-full-keyboard-2-4inch-lcd-esp32-s3-lr1110-gps-2300mah.html
    publisher: Elecrow
---

**Elecrow ThinkNode M9** は、iPhone と Android ではなく BlackBerry と Palm Treo の側に進化した世界線から来たような端末だ。実際にはスマートフォンではない。通話機能はなく、携帯電話網も使わない。**LoRa** による長距離無線と **MeshCore** を使って、端末どうしが直接メッセージをやり取りする通信機である。

## スペック

| 項目 | 内容 |
|---|---|
| SoC | ESP32-S3R8 |
| 無線（メッシュ） | LoRa モジュール Semtech LR1110 |
| その他無線 | Wi-Fi 4（802.11n）、Bluetooth 5.0 |
| 測位 | GPS 受信機 |
| ディスプレイ | 2.4インチ LCD / 320×240（非タッチ） |
| 入力 | 37キー QWERTY ＋ 操作用ファンクションキー |
| バッテリー | 2,300mAh |
| 端子 | USB 2.0 Type-C（充電） |
| 音 | ブザー（スピーカーではない） |
| サイズ | 126 × 67 × 10mm |
| 重量 | 123g |
| 価格 | 約75ドル（Elecrow で販売中） |

近い立ち位置の製品としては LILYGO の T-Deck Pro シリーズがある。

## 何が面白いのか

この手のデバイスの本質は「インフラに依存せずに文字が届く」ことにある。基地局も、インターネットも、契約も要らない。端末どうしが中継し合ってメッシュを作り、ホップを重ねてメッセージを運ぶ。

**スマホと決定的に違うのは、通信が「圏内かどうか」ではなく「近くに仲間の端末があるかどうか」で決まる点だ。** だから単体で買っても意味がなく、最低2台、実用的にはグループで導入するタイプの製品になる。登山・キャンプ、イベント運営、アマチュア無線的な実験、災害時の備えといった文脈で使われている。

75ドルという価格は、フルキーボードと GPS を積んだ完成品としてはかなり安い。ESP32-S3 なので、ファームウェアを自分で書き換えて遊ぶ余地も大きい。

## 日本で買える？使える？

**今の海外版は、日本ではそのまま使えない。日本向けが出るかどうかが鍵になる。**

LoRa の周波数は国ごとに違う。日本で免許なしに使えるのは 920MHz 帯（ARIB STD-T108）で、**技術基準適合証明（技適）を取った無線機**に限られる。海外向けの LoRa 機は 868MHz（EU）や 915MHz（US）向けで出荷されることが多い。

ただ、これは「日本には来ない」という意味ではない。海外メーカーが日本発売に合わせて技適を取るのはよくあることで、Gadget Terminal が先に紹介した製品でも、公開後に日本で発売や予約が始まったものがいくつもある。

日本上陸を待つうえで、掲載時点でまだ分かっていないのは次の3つ。

- 日本向けの 920MHz 帯モデルが出るか
- 技適を取るか
- 国内で正規に売られるか

今すぐ国内で LoRa メッシュを試したいなら、技適を取った 920MHz 帯の製品を選ぶのが確実だ。ThinkNode M9 の日本向けが出たら、この記事に追記する。
