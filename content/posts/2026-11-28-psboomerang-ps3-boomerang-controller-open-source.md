---
title: 2005年にSonyが見せたPS3の「ブーメラン型コントローラー」を、個人が動く実機にして設計ごと公開した
seo_title: PS3ブーメラン型コントローラーを実機化
x_hook: |
  Sonyが商品にしなかったコントローラーを、個人が作った。
  2005年のPS3発表時に見せた「ブーメラン型」を、polymattがBluetooth対応の実機に再現。設計図とファームウェアは公開されている。
slug: psboomerang-ps3-boomerang-controller-open-source
keyword: PSBoomerang
category: weird
date: 2026-11-28
kicker: 制作者のpolymattが、2005年のE3でSonyがPS3と並べて見せ、発売されなかったブーメラン型コントローラーを「PSBoomerang」として作り直した。基板・筐体・ファームウェアはGitHubで公開されている。
tags:
  - PS3
  - ゲームコントローラー
  - オープンソース
  - ESP32
  - 自作
images:
  - url: "https://raw.githubusercontent.com/thepolymatt/psboomerang/main/docs/images/hero_render.png"
    caption: 制作者が公開している完成形のレンダリング。銀色に塗装された三日月形で、左右にスティックとボタンが並ぶ
  - url: "https://raw.githubusercontent.com/thepolymatt/psboomerang/main/docs/images/hero_pcb.png"
    caption: 本体と同じ曲線の基板（v0.4）の設計画面。ボタン用の接点とマイコンの位置が見える
credit: polymatt GitHubリポジトリ（thepolymatt/psboomerang）
clips:
- file: psboomerang-ps3-boomerang-controller-open-source/hero.mp4
  caption: "Sonyの幻のコントローラー（PSBoomerang）"
  credit: "polymatt 公式 YouTube"
  source: "https://youtu.be/1w722lkhs_E"
sources:
  - title: Sony's Abandoned PS3 Boomerang controller finally reincarnates as a working gamepad 20 years later
    url: https://www.yankodesign.com/2026/11/27/sonys-abandoned-ps3-boomerang-controller-finally-reincarnates-as-a-working-gamepad-20-years-later/
    publisher: Yanko Design
  - title: PS3 Boomerang Controller Concept Flies Back Into Your Hands
    url: https://hackaday.com/2026/11/27/ps3-boomerang-controller-concept-flies-back-into-your-hands/
    publisher: Hackaday
  - title: thepolymatt/psboomerang
    url: https://github.com/thepolymatt/psboomerang
    publisher: GitHub（制作者のリポジトリ）
giteki:
  status: 確認できない
  number: []
  checked: 2026-11-28
  radio: Bluetooth LE
  note: 完成品として売られる製品ではない。マイコンのSeeed XIAO ESP32S3単体は総務省DBに登録がある（217-230892）が、組み上げた機器としての認証は無い
alternatives:
  - name: SONY DualSense ワイヤレスコントローラー（ホワイト）
    why: 国内向けの純正品で、PCやSteamにもUSB-C接続で使える。形は普通だが、今日から使える完成品のコントローラー。
    url: https://item.rakuten.co.jp/world-free-store/4948872414975/
    merchant: rakuten
    image: "https://thumbnail.image.rakuten.co.jp/@0_mall/world-free-store/cabinet/07084073/09702165/imgrc0089637697.jpg"
faq:
  - q: PSBoomerangは買えますか
    a: 完成品としての販売は確認できていません。設計データ（基板・筐体・ファームウェア・部品表）がGitHubで公開されていて、自分で作る前提のプロジェクトです。
  - q: PS3や最新の機種でも使えますか
    a: 制作者の説明では、PCとSteamでは無線またはUSB-Cで使え、PS3にはUSB-C接続で使えます。マイコンがBluetooth LEのみに対応するため、PS3や最近のゲーム機との無線接続はできません。
  - q: 日本で作れますか
    a: 設計データは公開されており、部品は一般的な電子部品です。ただし基板の製造発注やはんだ付けが必要で、気軽に組める製品ではありません。無線部分の技適については本文を参照してください。
---

2005年のE3で、SonyはPS3の試作機と一緒に、三日月のように大きく曲がったコントローラーを見せた。製品にはならなかったその形を、制作者のpolymattが動く機器として作り直した。名前は「PSBoomerang」。

## 何を作ったのか

当時の写真や特許の図面、手元のPS3本体を頼りに寸法を起こし、外装を3Dモデルにして作った。Yanko Designによると、DualShockのスティックは本体に収まらず、Joy-Con用の小型スティック（TMR方式）に替えている。ボタンの接点にはDualShock 3のゴム製パッドを使い、基板もこの形に合わせてKiCadで専用設計した。

制作者のリポジトリによる主な仕様は次のとおり。

| 項目 | 内容 |
|---|---|
| 接続 | Bluetooth LE（無線）、またはUSB-C（有線） |
| 認識 | SInput規格のゲームパッドとしてSteamやSDL3対応のゲームで使える |
| マイコン | Seeed XIAO ESP32-S3 |
| 入力 | 十字キー・フェイスボタン・中央ボタン（DualShock 3用ゴムパッド）、スティック2本（L3/R3クリック付き）、肩ボタン |
| 電池 | 内蔵のリチウムポリマー電池をUSB-Cで充電。容量は筐体に合わせて選ぶ |
| 表示 | RGB LED 2つ |
| 公開物 | 基板（KiCad）、筐体のSTL、ファームウェア、部品表 |

Yanko Designは電池を2,000mAh・約40時間と伝えているが、制作者のリポジトリには容量が筐体しだいと書かれており、この数字は制作者の試作機の値とみられる。

## できないこと

制作者自身が説明しているとおり、PS3や最近のゲーム機とは無線でつながらない。使っているマイコンがBluetooth LEにしか対応しておらず、PS3が使う従来のBluetoothや、新しい機種の認証の仕組みには対応できないためだ。PS3にはUSB-Cでの有線接続で使える。PCやSteamが主な使い道になる。

Yanko Designによると、肩ボタンの押し心地は普通のDualShockよりやや硬い。握りやすさを狙った機器ではなく、形の再現が目的のプロジェクトだ。

外装の塗装では、金属メッキだと電波を遮ってしまい、最終的に液体クロム塗料で銀色にしたとされる。

## 日本で買える？使える？

**完成品としては売られていないので、日本から買う方法は無い。** 作るなら、公開されている部品表の部品とPCBの製造、はんだ付け、3Dプリントが必要になる。部品表には一般的な電子部品が並び、販売元として海外の部品商社（LCSCやDigiKey）の品番も挙がっている。

無線の技適について。使うマイコンのSeeed XIAO ESP32S3は、総務省のデータベースに単体の登録（217-230892）がある。ただし、これは基板単体の話で、組み上げた機器としての認証ではない。国内で自作して使う場合の電波法上の扱いは、組み方や改造の有無で変わりうる。確信が持てないときは、有線（USB-C）だけで使うのが確実だ。

すぐに遊べる完成品のコントローラーが欲しいなら、国内で買える純正品のDualSenseがPCにも使える。ブーメランの形を味わうなら、リポジトリの写真と設計図を眺めるだけでも十分に楽しめる。
