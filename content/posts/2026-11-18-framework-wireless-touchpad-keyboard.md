---
title: Framework「Wireless Touchpad Keyboard」は99ドル、タッチパッド付き75%キーボードで電池は交換式・CADも公開
slug: framework-wireless-touchpad-keyboard
seo_title: Framework新キーボードは99ドル、タッチパッド付き
x_hook: |
  ソファ用キーボードに、ここまで中身を公開するメーカーは珍しい。
  Frameworkの「Wireless Touchpad Keyboard」は、基板の回路図とケースのCADまで公開。電池は交換式で、99ドル（約1.5万円）。
  ・ZMKファームウェアで配列を書き換え可能
  ・1,200mAhで約1か月
keyword: Framework Keyboard
category: pc
date: 2026-11-18
kicker: Framework が、タッチパッド一体のワイヤレスキーボード「Wireless Touchpad Keyboard」を正式発表した。価格は99ドルで、出荷は2027年第1四半期の予定。電池は交換式で、ケースのCADと制御基板の回路図も公開される。
tags:
- Framework
- ワイヤレスキーボード
- タッチパッド
- ZMK
- オープンソース
giteki:
  status: 確認できない
  number: []
  checked: 2026-11-18
  radio: Bluetooth 6.0 / 2.4GHz ドングル
  note: 日本向けの型番・技適番号は公表されていない
images:
- url: "https://us1.discourse-cdn.com/flex001/uploads/framework3/original/3X/f/c/fcdf62cf2b638f1b90c3e7a154a39d293cc71e2e.jpeg"
  caption: 本体を真上から見たところ。右側に縦長のタッチパッド、右上に4つのペアリング表示とリンクボタンがある（US配列）
- url: "https://images.frame.work/frameworkmarketplace/virsvEBHQ8RHNfH2_fw-wireless-keyboard_family_overview_hero.jpg"
  caption: 居間のテーブルで、テレビ画面を前にゲームパッドと並べて使う想定のイメージ
credit: Framework 公式ストア・公式コミュニティ
sources:
- title: Framework Launches Customizable Slim Wireless Touchpad Keyboard With Open-Source CAD Files
  url: https://www.techpowerup.com/354946/framework-launches-customizable-slim-wireless-touchpad-keyboard-with-open-source-cad-files
  publisher: TechPowerUp
- title: Framework Wireless Touchpad Keyboard
  url: https://frame.work/products/framework-wireless-touchpad-keyboard
  publisher: Framework（公式）
- title: Previewing the Framework Wireless Touchpad Keyboard
  url: https://community.frame.work/t/previewing-the-framework-wireless-touchpad-keyboard/81953
  publisher: Framework Community（公式）
alternatives:
  - name: サンワダイレクト タッチパッド付きワイヤレスキーボード（400-SKB071）
    why: タッチパッド一体のBluetoothキーボードを国内の通販で今日から買える。Frameworkの出荷（2027年第1四半期予定）を待たずに、居間での操作用途を試せる。
    url: https://item.rakuten.co.jp/sanwadirect/400-skb071/
    merchant: rakuten
    image: "https://thumbnail.image.rakuten.co.jp/@0_mall/sanwadirect/cabinet/4/400-skb071.jpg"
faq:
- q: Framework Wireless Touchpad Keyboardはいくらですか
  a: Framework の公式ストアで99ドル（税・関税別）です。予約金は50ドルで、残りは出荷前に請求されます。掲載時点の情報です。
- q: いつ届きますか
  a: 出荷は2027年第1四半期の予定です。掲載時点で複数のバッチが完売しており、予約できるバッチも出荷は第1四半期と表示されています。
- q: 日本で買えますか
  a: 掲載時点で、日本向けの販売や配送を示す公式の案内は確認できていません。購入前に Framework の公式ストアで配送先に日本が含まれるかを確かめる必要があります。
- q: 技適は取得していますか
  a: 掲載時点で、技適の取得は確認できていません。Bluetoothと2.4GHzの無線を使うため、国内で使うには型番ごとの技適の確認が要ります。
---

Framework が、タッチパッドを右側に組み込んだコンパクトなワイヤレスキーボード「Wireless Touchpad Keyboard」を正式発表した。価格は99ドルで、公式ストアで予約を受け付けている。出荷は2027年第1四半期の予定だ。TechPowerUp によると、予約のバッチは複数が完売している。4月に公式コミュニティで先行紹介された製品で、今回は価格と出荷時期が確定した形になる。

## どんなキーボードか

Framework は、Framework Desktop やノートPCをワークステーションに据えた状態や、居間のソファでのゲーム用途を想定している。公式は、これまで居間用キーボードとして選択肢が乏しかったことが開発のきっかけだと説明している。TechPowerUp は、比較対象としてロジクールの「K400 Plus」（35ドル）を挙げている。

| 項目 | 内容 |
|---|---|
| キー | シザースイッチ、キーストローク1.5mm、キーピッチ19mm |
| タッチパッド | 縦長・クリック式、Windows Precision対応、物理ボタンなし |
| 接続 | Bluetooth 6.0、USB-A ドングル、有線USB-C。無線は4台まで登録 |
| 電池 | 1,200mAh・交換式。公式は「使用で1か月以上、待機で1年以上」 |
| 寸法 | 357 × 118.65mm、厚さ9.74〜16.91mm |
| 重量 | 484.9g（TechPowerUp） |
| 価格 | 99ドル（税・関税別） |

ファームウェアはオープンソースのZMKで、配列の書き換えができる。タッチパッドの寸法は、公式の告知文では68.8 × 85.6mm、ストアページでは69.79 × 85.6mmと表記が揺れている。

## 中身が公開される

Framework は、ケース表面のCADを公開し、3Dプリントのマウントやアクセサリーを作りやすくしている。Nordic nRF54LM20A を載せた制御基板の回路図も公開され、同基板は単体でもマーケットプレイスで販売される見込みだ。TechPowerUp は、この基板を土台に自作キーボードを組めると伝えている。

USB-Aアダプター用の拡張カードも計画されている。ドングルがFrameworkのノートPCの側面にぴったり収まるようになる。製造はノートPC向けのキーボードを手がけてきたLite-Onだ。

## 日本で買える？使える？

**掲載時点で、日本向けの販売や配送を示す公式の案内は確認できていない。** ストアページには配送対象国の記載がなく、日本語配列の用意も確認できない（掲載のモデルはUS配列）。日本で使うには、日本向けの販売開始と技適の整理が必要になる。技適は確認できていない。国内で使うなら、型番が確定し、技適番号が公表されたあとが現実的だ。

出荷は2027年第1四半期予定なので、待てる人は Framework のストアで配送先に日本が含まれるかを確認し、予約金の50ドルを払う前に判断するとよい。今すぐ居間用のタッチパッド付きキーボードが要る人は、国内の通販にある製品で足りる。ただし電池交換や配列の書き換えまで求めるなら、これと同じ組み合わせの製品は見当たらない。
