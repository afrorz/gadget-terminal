---
title: Caimera「CAIM1」は、撮った瞬間に暗号署名を付ける試作カメラ。Noctuaのファンで冷やし、外装はPrusaのフィラメントで3Dプリント
slug: caimera-caim1-proof-camera
seo_title: CAIM1は撮影時に署名するカメラ、価格は？
x_hook: |
  このカメラは、撮った写真が本物だと署名する。
  Caimeraの試作機「CAIM1」は、4K動画も撮影した瞬間に暗号で署名。冷却はNoctuaのファン、外装は3Dプリントだ。
  ・Sony Eマウントにレンズ交換対応
keyword: CAIM1
category: weird
date: 2026-11-14
kicker: AI生成の画像があふれるなか、Caimeraが撮影した瞬間に写真と4K動画へ暗号署名を付ける試作カメラ「CAIM1」を公開した。署名チップはTropic SquareのTROPIC01、冷却ファンはNoctua製で、最初のロットは2027年初めを目標にしている。
tags:
- Caimera
- CAIM1
- 真正性
- 3Dプリント
- Noctua
giteki:
  status: 確認できない
  number: []
  checked: 2026-11-14
  radio:
  note: 試作段階で型番が公表されておらず、総務省DBで特定できない。無線機能の仕様も公式サイトに書かれていない
images:
- url: "https://caimera.one/optimized/nt_pr_iso_sensor_desktop.webp"
  caption: レンズを付けない状態の試作機。ベージュと茶色の外装に、シルバーのEマウントとセンサーが見える。「NOCTUA PRUSA」「004」の刻印入り
- url: "https://caimera.one/optimized/nt_pr_cracked_desktop.webp"
  caption: ZeissのEマウントレンズを付けた状態。上面にはシューと通気口が並ぶ
- url: "https://caimera.one/optimized/t01_integrate.webp"
  caption: 背面の4.3インチ画面と、署名を担うTROPIC01チップの拡大
credit: Caimera 公式サイト
sources:
- title: CAIM 1 | Prove You Were There（Caimera 公式サイト）
  url: https://caimera.one
  publisher: Caimera（公式）
- title: The CAIM1 3D Printed Camera puts a security chip behind your photos as proof against AI deepfakes
  url: https://www.yankodesign.com/2026/11/13/the-caim1-3d-printed-camera-puts-a-security-chip-behind-your-photos-as-proof-against-ai-deepfakes/
  publisher: Yanko Design
- title: ライカ コンテンツクレデンシャル（ライカカメラ日本語サイト）
  url: https://leica-camera.com/ja-JP/photography/content-credentials
  publisher: Leica Camera
alternatives:
  - name: Leica M11-P ブラックペイント
    why: 撮影時にContent Credentials（C2PA準拠の来歴情報）を付けられる市販のカメラ。CAIM1が目指す「撮影元の証明」を、国内正規品で今すぐ使える。ただし店頭は納期未定の表示があり、価格も高い。
    url: https://item.rakuten.co.jp/emedama/4548182202127/
    merchant: rakuten
    image: "https://thumbnail.image.rakuten.co.jp/@0_mall/emedama/cabinet/2127/4548182202127_1.jpg"
    picked: 2026-11-15
faq:
- q: CAIM1はいくらですか
  a: 価格は発表されていません。Yanko Designは、最初のロットを2027年初めに出荷する目標としており、価格は未公表と伝えています。
- q: CAIM1は買えますか
  a: 試作段階で、購入はできません。公式サイトに早期アクセスの登録欄があります。
- q: CAIM1は日本で使えますか
  a: 公式サイトには日本語表示がありますが、日本向けの販売や技適の情報は出ていません。無線機能の仕様も公開されていないため、確認できていません。
- q: 署名で何が証明できますか
  a: 公式サイトによれば、撮影の瞬間にハードウェアで暗号証明を作り、改ざんできない分散型のインフラに記録します。写っている出来事が実際に起きたかまでを保証するものではありません。
---

Caimeraが、撮影した写真と4K動画に、シャッターを切った瞬間に暗号署名を付けるカメラ「CAIM1」の試作機を公開した。名前は「Counter Artificial Intelligence Machine 1」の略で、AI生成ではなく実際に撮られたものだと示すことを目的にしている。Yanko Designによれば、最初のロットは2027年初めを目標とし、価格は未公表だ。製品ではなく試作機の段階にある。

## 署名の仕組み

公式サイトは、流れを4段階で説明する。撮影し、ハードウェアで証明を作り、不変の分散型インフラに記録し、誰でも検証できるようにする。署名を担うのは、チェコのTropic Squareが作る監査可能なセキュアエレメントTROPIC01。背面の4.3インチ画面の裏にあり、撮影から保存までを暗号化した経路に通すという。

珍しいのは、証明を紙で渡せる点だ。撮影した動画ごとに、検証用のアクセスコードを記した紙のレシートをその場で印刷できる。コードはウォレットにつながり、撮影した素材の証明を持ち歩ける。

## 3Dプリントの外装と、Noctuaのファン

センサーはマイクロフォーサーズで、4K動画に対応する。マウントはSony Eマウントが標準で、公式サイトはマイクロフォーサーズマウントも選べるとする。レンズは付属せず、手持ちのレンズを使う方式だ。Yanko Designは、Eマウントのフランジバックが18mm、マイクロフォーサーズが19.25mmと近いため、Eマウントのレンズでもセンサーを覆えると説明している。

4Kで撮りながら暗号証明を作ると熱がこもる。Yanko Designによれば、チームはPCファンで知られるNoctuaの40mmファン「NF-A4x10 5V PWM」をセンサーの背後に1基置き、前面の吸気口からの空気をセンサーとCPUのヒートシンクへ流している。外装はPrusa3Dのフィラメント「Prusament」のPETGで3Dプリントし、色はNoctuaのベージュと茶色だ。6月のニュルブルクリンクでは気温38度の中で動作を試し、同行のスマホが録画を止めるなか撮り続けたと伝えている。

## 日本で買える？使える？

**今は試作段階で、日本では買えない。製品化と日本向けの展開が見えてくるかどうかが鍵になる。**

国内の販売元は決まっていない。公式サイトには日本語の表示があり、早期アクセスの登録を受け付けている。製品化の際に日本向けの展開があるかは、掲載時点で明らかにされていない。

無線機能の仕様が公開されていないため、技適の判定もできない。Wi-FiやBluetoothを載せる場合、国内で使うには技適が必要になる。海外メーカーが日本発売に合わせて技適を取るのはよくあることで、Gadget Terminal が先に紹介した製品でも、公開後に日本で発売や予約が始まったものがいくつもある。市販が始まっても日本で使えるとは限らない点は、先に覚えておきたい。

日本上陸を待つうえで、掲載時点でまだ分かっていないのは次の3つ。

- 無線機能の仕様
- 技適を取るか
- 国内で正規に売られるか

撮影元の証明を今すぐ使いたい人には、ライカがM11-PでContent Credentialsに対応している。ライカの日本語サイトは、撮影情報を改ざんできない形で付けられると説明している。CAIM1は、第三者による検証も市販の製品としての実績もこれからだ。署名で証明できるのは機材が記録したことまでで、写った出来事の真実性までは保証しないとの指摘も、海外の報道では出ている。C2PAなど既存の規格との互換性は、掲載時点で確認できていない。日本向けの情報が出たら、この記事に追記する。
