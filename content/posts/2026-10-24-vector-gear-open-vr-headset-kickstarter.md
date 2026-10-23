---
title: Vector Gear、Snapdragon 8cx Gen 3とRK3588Sの2チップ構成で改造も前提のスタンドアロンVR。Kickstarterで980ドルから
slug: vector-gear-open-vr-headset-kickstarter
seo_title: Vector Gearは980ドル、改造前提のVR
x_hook: |
  VRヘッドセットなのに、レンズの設計まで公開すると言っている。
  Kickstarterの「Vector Gear」は、ノートPC向けのチップとトラッキング専用チップを積んだスタンドアロン機。目と口の動きも追う。
  ・980ドルから、届くのは2027年5月予定
keyword: Vector Gear
category: pc
date: 2026-10-24
kicker: Walker Industriesが、スタンドアロンのVR/MRヘッドセット「Vector Gear」をKickstarterで募集している。片目2160×2160の液晶、視線と表情の追跡、85Whのシリコン電池を持ち、ソフトとハードを順に公開していく方針だ。980ドルから。
tags:
- Vector Gear
- VRヘッドセット
- オープンソース
- Kickstarter
- アイトラッキング
origin: HKD 函館
deadline: 2026-12-17
giteki:
  status: 確認できない
  number: []
  checked: 2026-10-24
  radio: Wi-Fi（PCストリーミング用アダプターは計画段階）
  note: "無線の仕様と型式が未公表で、総務省DBで特定できない"
images:
- url: "https://i.kickstarter.com/assets/054/932/566/ea55e335ee4969b8bec17deceb1cdd78_original.png?fit=scale-down&origin=ugc&q=100&v=1788057579&width=700&sig=GPkQpcoLiPpb%2BCBWBPN64jtk4PfGvsqzVl%2FtRzERAxg%3D"
  caption: 試作機の外観。左は前面で、黒いバンドと黄色のカメラ枠があり、右は内側のレンズ。樹脂は3Dプリント
- url: "https://i.kickstarter.com/assets/054/932/496/16de80c516e803192c3232dcffe17036_original.png?fit=scale-down&origin=ugc&q=100&v=1788056721&width=700&sig=HblCIE%2Bkz35%2FZT%2BTaqxLLFzmExmyL9e6eSAduFulSwo%3D"
  caption: 基板のレンダリングと、レンズユニット、機構部品の試作写真を並べた4枚組
credit: Vector Gear Kickstarterプロジェクトページ（Walker Industries）
sources:
- title: "The Vector Gear - Standalone, Open Headset In One Design（Kickstarterプロジェクトページ。数値は2026年10月24日朝時点）"
  url: https://www.kickstarter.com/projects/walkerindustries/the-vector-gear
  publisher: Walker Industries（公式）
alternatives:
  - name: Meta Quest 3 512GB（スタンドアロン型VRヘッドセット）
    why: 国内の公式ストアで買える、今日から使えるスタンドアロンVR。技適の取得も気にしなくてよい。
    url: https://item.rakuten.co.jp/meta/9089224147192/
    merchant: rakuten
    image: "https://thumbnail.image.rakuten.co.jp/@0_mall/meta/cabinet/12062899/imgrc0095963311.jpg"
faq:
- q: Vector Gearとは何ですか
  a: Walker IndustriesがKickstarterで募集しているスタンドアロンのVR/MRヘッドセットです。片目2160×2160の液晶、視線と表情の追跡、Steam Frame風のコントローラーを備え、ソフトとハードを順に公開していくと説明しています。
- q: いくらですか
  a: Vector Gear本体は980ドル、自作キット版は940ドルです。PC向けに絞った下位機種「Andromeda」は650ドルからです（2026年10月24日時点、米ドル建て）。
- q: いつ届きますか
  a: 本体のお届け予定は2027年5月です。募集の締切は2026年12月17日です。
- q: 日本で使えますか
  a: 無線の仕様と技適は確認できていません。配送先は「世界中どこでも」と表示されていますが、日本向けの送料と関税は確認できていません。
---

Walker Industriesは、スタンドアロン型のVR/MRヘッドセット「Vector Gear」をKickstarterで募集している。プロジェクトページでは、作り手の所在地が北海道函館市と表示されている。目標額は150,000ドルで、2026年10月24日朝の時点で調達額は35,250ドル（23.5%）、支援者は44人。締切は12月17日だ。

**まだ製品ではない。** 出資は購入ではなく、遅れる、仕様が変わる、届かないことがある。ページには試作機の写真が載っており、作り手は「最終品は3Dプリントではなく射出成形で作る」と書いている。調達額と支援者数は取得時点の値で、毎日動く。

## 仕様

ページに書かれた主な仕様は次のとおり。

| 項目 | 内容 |
|---|---|
| 表示 | 片目2160×2160、90Hz、液晶。2枚のフレネルレンズを重ねた疑似パンケーク光学系。自動IPD調整 |
| メインのチップ | Qualcomm Snapdragon 8cx Gen 3（RAM 8GB） |
| 補助チップ | RK3588S（RAM 8GB）。トラッキングとセンサー処理、開発者向けの計算に使う |
| 保存 | NVMe SSD 500GB／1TB |
| 追跡 | 内側からの位置追跡（白黒カメラ2基）、視線追跡カメラ2基、口の追跡カメラ1基、カラーのパススルーカメラ2基 |
| 電池 | 85Whのシリコン電池、USB-C PD充電 |
| ソフト | Arch系のXR用OS「YuukOS」と空間UIの「XRUIOS」、x86エミュレーションのFEX、Proton |

重さ、視野角、実際の電池持続時間は、ページから確認できなかった。電池は「開発中（WIP）」と書かれた項目もある。

## 価格

Kickstarterの支援額は米ドル建てで、次のとおり。

- Vector Gear（500GB）: 980ドル。自作キット版は940ドル
- Andromeda 1600×1600（PCVR向けの下位機種）: 650ドル。自作キット版は610ドル
- Andromeda 2560×2560（OLED、パンケーク光学系）: 1,250ドル。自作キット版は1,200ドル
- コントローラー2本のみ: 230ドル

お届け予定は2027年4〜5月だ。割引はほとんど付けられなかった、と作り手自身が書いている。Kickstarterの手数料8%を引くと、製造費が足りなくなるという理由だ。

## 気になる点

作り手が最大のリスクとして挙げているのは基板の設計だ。ミスがあれば本体が起動しない。そのため調達額の一部を、同じチップを扱った会社による品質確認に充てる予定だという。ページの謝辞に並ぶのは少人数の開発者で、「大学生のアルバイトと奨学金の返還、コンテストの賞金で作ってきた」とも書かれている。過去に量産した製品の実績は、ページから確認できなかった。

差別化の中心は「所有する自由」だ。ソフトとハードをソースが読める形か、完全なオープンソースで出し、順にハードの資料、最後にレンズの設計まで公開していくという。ただし公開は製品の発売後に進める計画で、今回の募集時点で公開されているわけではない。

## 日本で買える？使える？

配送先は「世界中どこでも」と表示されているが、日本向けの送料と関税は確認できていない。日本の代理店や国内の予約開始は、掲載時点で見つかっていない。

無線の仕様は、ページでは「PCストリーミング用のWi-Fi 6Eアダプターを計画中」とあるだけだ。本体が持つ無線の種類と型式が決まっておらず、総務省のデータベースでも特定できない。技適が無い無線機を日本で電波を出して使うと電波法違反になるため、届いてからそのまま使える保証は現時点でない。

届くのは約半年後で、基板が完成するかどうかもこれからだ。VRを今日から使いたいなら、国内の公式ストアで買えるMeta Quest 3がある。Vector Gearは、技適の見通しと、基板の検証結果が出てから考えるのが無難だ。
