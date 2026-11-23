---
title: Piccola CNCは設計から基板加工までオープンソースの卓上フライス盤。Kickstarterは開始12分で目標を達成
slug: piccola-cnc-open-source-desktop-mill
seo_title: Piccola CNCは1279ユーロから、卓上フライス盤
x_hook: |
  基板もアルミも削れる卓上フライスが、開始12分で目標額に届いた。
  ドイツ発の「Piccola CNC」はハードもファームもソフトも全部オープンソース。基板の高さをレーザーで測り、自動で補正する。
  ・加工範囲150×150×70mm
  ・基板、木、樹脂、アルミ、真ちゅうに対応
keyword: Piccola CNC
category: pc
date: 2026-11-24
kicker: 加工範囲150×150×70mmの卓上フライス盤「Piccola CNC」が、Kickstarterで募集中。基板、木、樹脂、アルミや真ちゅうまで削れて、制御基板からCAMまで全部オープンソース。支援は1,279ユーロから（付加価値税込み）。
tags:
- Piccola CNC
- InMachines
- CNC
- 基板加工
- オープンソースハードウェア
- Kickstarter
deadline: 2026-12-16
origin: HAM ハンブルク
giteki:
  status: 確認できない
  number: []
  checked: 2026-11-24
  radio: Wi-Fi
  note: 型番が公表されておらず、総務省DBで特定できない
images:
- url: "https://irp.cdn-website.com/11074afe/dms3rep/multi/opt/Intro_mobile_r-1920w.jpg"
  caption: 全面カバーつきの本体。手前のノートPCに基板加工の画面、本体の前に加工サンプルが並ぶ
- url: "https://irp.cdn-website.com/11074afe/dms3rep/multi/opt/IMG_1146.jpg-1920w.jpeg"
  caption: 木、アルミ、真ちゅう、樹脂で削り出した加工サンプル
credit: InMachines / Piccola CNC 公式サイト
clips:
- file: piccola-cnc-open-source-desktop-mill/alu.mp4
  caption: "アルミも真ちゅうも削る（木や樹脂にも対応）"
  credit: "InMachines 公式 YouTube"
  source: "https://www.youtube.com/watch?v=Nwl-WHoEikU"
- file: piccola-cnc-open-source-desktop-mill/pcb.mp4
  caption: "基板もその場で彫る（両面基板にも）"
  credit: "InMachines 公式 YouTube"
  source: "https://www.youtube.com/watch?v=Nwl-WHoEikU"
sources:
- title: "Piccola CNC: 100% Open Source Desktop Milling Machine（Kickstarter。金額・支援者数は2026年11月24日時点）"
  url: https://www.kickstarter.com/projects/inmachines/piccola-cnc
  publisher: Kickstarter（公式）
- title: Piccola CNC 公式サイト
  url: https://www.piccolacnc.com/
  publisher: InMachines（公式）
- title: "Piccola CNC – An open-source hardware desktop milling machine with PCB auto-leveling and integrated CAM (Crowdfunding)"
  url: https://www.cnx-software.com/2026/11/23/piccola-cnc-open-source-desktop-milling-machine-with-pcb-auto-leveling-and-integrated-cam/
  publisher: CNX Software
alternatives:
  - name: KitMill BS100 / 200（オリジナルマインド）
    why: 国内メーカーの卓上CNCフライス。樹脂・木材・アルミ・真ちゅうを削れ、基板加工は別売りアタッチメントで対応する。国内サポートと日本語の資料がある。税込248,000円から。
    url: https://www.originalmind.co.jp/products/kitmill_bs
    image: "https://cdn.originalmind.co.jp/assets/1000/034221/products-bs01.jpg"
faq:
- q: Piccola CNCはいくらですか
  a: 公式サイトの価格（付加価値税込み）は、Basicが1,279ユーロ、Proが1,679ユーロ、Ultimateが1,979ユーロのSuper Early Birdです。発売後の想定価格はそれぞれ1,499ユーロ、1,999ユーロ、2,499ユーロとされています。
- q: 何を削れますか
  a: 基板、木材、樹脂、アルミ、真ちゅう、銅などです。加工範囲は150×150×70mmです。
- q: 日本で買えますか
  a: 掲載時点で日本の販売元や日本への発送条件は確認できていません。Kickstarterの募集に日本から支援できるかは、支援ページでの確認が必要です。
- q: 技適は取得していますか
  a: 確認できていません。USB-CのほかWi-Fiを備えますが、型番が公表されておらず、総務省のデータベースで特定できませんでした。
---

Piccola CNCは、ドイツのInMachinesが出す卓上のフライス盤だ。加工範囲は150×150×70mmで、基板の試作から、木材・樹脂・アルミ・真ちゅう・銅の削り出しまで対応する。Kickstarterの調達額は2026年11月24日時点で119,646ユーロ、支援者は76人。目標の25,000ユーロを開始の12分で超え、募集は12月16日（日本時間2時）まで。

**これはクラウドファンディングの募集で、製品の購入ではない。** 納期の遅れや仕様の変更が起きる可能性がある。調達額と支援者数は取得時点の値で、毎日動く。作り手のInMachinesは、10年にわたりオープンソースの機械を作ってきたと書いている。支援者1人あたりの金額が大きいのは、1台1,000ユーロを超える機械だからだ。

## 全部オープンソースという売り

制御は、RP2350を2個載せた自社製コントローラーで、動作制御にはgrblHALを使う。センサーや安全監視は、別のスーパーバイザーファームウェアが担当する。ステッピングモータードライバーはソケット式で交換でき、microSDカードで加工ファイルやログを保存できる。外部からの制御や自動化のためのJSON APIも用意される。公式サイトは「90%ではなく100%オープンソース」とうたう。

接続はUSB-C、Wi-Fi、本体が作る単独のWi-Fiホットスポット。付属のソフトには、基板・2D・3D・回転軸の加工に使えるCAMが入っていて、別のCAMを買う必要がないという。公式の更新情報では、両面基板を加工する流れも公開されている。

## 3つのモデルと仕様

| | Basic | Pro | Ultimate |
|---|---|---|---|
| 価格（Super Early Bird、税込） | 1,279ユーロ | 1,679ユーロ | 1,979ユーロ |
| 発売後の想定価格 | 1,499ユーロ | 1,999ユーロ | 2,499ユーロ |
| スピンドル | 100W・24V ブラシ式 20,000rpm | 200W・48V ブラシ式 12,000rpm | 200W・48V ブラシレス 12,000rpm |
| 囲い・安全 | ― | 全面カバー、ドアのインターロック | 同左 |
| 基板の高さ測定 | 接触式 | 接触式 | レーザー式 |

共通の仕様は、移動速度が最大2,000mm/分、3軸ともベルト駆動の1204ボールねじ、理論上のステップ分解能2.5µm。繰り返し精度はメーカーの申告で、5mmの早送りで10µm未満、0.1mmの移動で2µm未満とされる。フレームは曲げ加工のアルミ板で、防振脚が付く。独立したハードウェアの非常停止回路があり、集じんキットは全モデルに付属する。

Ultimateはレーザーで基板の端や中心を探し、非接触で高さを測り、3Dスキャンもできる。レーザーセンサーは、BasicとProでは別売りの付属品になる。回転軸、真空テーブルとポンプ、最小量潤滑（MQL）、固定治具もオプションで用意される。

## 日本で買える？使える？

**掲載時点で、日本の販売元や日本向けの発送条件は確認できていない。**「Piccola CNC 国内」の日本語検索でも、紹介記事は見つからなかった。Kickstarterで日本から支援できるか、送料や関税がどうなるかは、支援ページで確認が必要だ。お届け予定の時期も、取得できた情報には書かれていなかった。

Wi-Fiを備えるため、日本で電波を出すなら技適が要る。型番が公表されておらず、総務省のデータベースで特定できなかった。USB-Cの有線で使う分には問題にならないが、電源（24V・48Vのスピンドルを動かす電源）の仕様も本文からは確認できていない。

今すぐ卓上CNCが欲しい人には、国内メーカーのKitMillのように、日本語の資料とサポートがある選択肢がある。待つなら、日本向けの販売元と技適の情報が出てから決めればよい。日本向けの情報が出たら、この記事に追記する。
