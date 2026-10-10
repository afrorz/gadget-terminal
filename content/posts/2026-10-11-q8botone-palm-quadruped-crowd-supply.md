---
title: 配線ゼロの手のひらサイズ四足ロボット「Q8botOne」、基板が背骨になる構造でCrowd Supplyに登場、完成品は599ドル
slug: q8botone-palm-quadruped-crowd-supply
keyword: Q8botOne
category: weird
date: 2026-10-11
kicker: ZeroWire Roboticsの四足ロボット「Q8botOne」が、Crowd Supplyで募集を始めた。スマホ大の本体は内部に配線が無く、メイン基板そのものが背骨になる。価格は199〜599ドルで、完成品は599ドル。
seo_title: Q8botOneは599ドル、配線ゼロの四足ロボット
x_hook: 配線ゼロ、基板が背骨になる手のひらサイズの四足ロボット「Q8botOne」。8個のDYNAMIXELで走ってジャンプし、完成品は599ドル。
tags:
- Q8botOne
- ロボット
- 四足歩行
- Crowd Supply
- オープンソース
origin: SJC クパチーノ
deadline: 2026-11-19
faq:
- q: Q8botOneはいくらですか
  a: Crowd Supplyの掲載時点で、選択肢の価格帯は199〜599ドルです。完成品の価格は599ドルと比較表に書かれています。キット版は8個のDYNAMIXELアクチュエーターを別に買う必要があります。
- q: いつまで募集していますか
  a: Crowd Supplyの表示では、2026年11月19日（米太平洋時間の午後3時59分）までです。
- q: いつ届きますか
  a: 掲載時点で確認できたページには発送予定時期が書かれていません。クラウドファンディングの納期は遅れることがあります。
- q: 日本で買えますか
  a: 国内の取扱いは確認できていません。Crowd Supplyは世界中のバッカーへ配送するとしていますが、日本向けの送料や条件は確認していません。
images:
- url: https://www.crowdsupply.com/img/2500/c6641401-a2af-48c6-9dde-d99751042500_project-main.jpg
  caption: Q8botOneの本体。8個のアクチュエーターが並び、平行リンクの脚が四隅に付く
credit: ZeroWire Robotics / Crowd Supply プロジェクトページ
sources:
- title: Q8botOne（Crowd Supply プロジェクトページ）
  url: https://www.crowdsupply.com/zerowire-robotics/q8botone
  publisher: Crowd Supply（公式）
- title: Q8botOne – A palm-sized open-source quadruped robot with ESP32-C3, DYNAMIXEL smart actuators
  url: https://www.cnx-software.com/2026/10/08/q8botone-a-palm-sized-open-source-quadruped-robot-with-esp32-c3-dynamixel-smart-actuators/
  publisher: CNX Software
- title: A $599 Robot Dog That Fits on Your Desk and Works Like LEGO Technic
  url: https://www.yankodesign.com/2026/10/10/a-599-robot-dog-that-fits-on-your-desk-and-works-like-lego-technic/
  publisher: Yanko Design
---

ZeroWire Roboticsの「Q8botOne」は、スマートフォンほどの大きさの四足ロボットだ。Crowd Supplyで10月6日に募集が始まり、掲載時点では10,000ドルの目標に対して3,588ドル（36%）、支援者12人。募集は11月19日（米太平洋時間）まで。

**これはクラウドファンディング案件であり、まだ製品ではない。** 調達額と支援者数は取得時点の値で、毎日動く。支援は購入ではなく、納期の遅れや仕様変更が起きうる。公式ページには発送予定時期が書かれていない。

## 配線をなくした作り

内部のケーブルを使わず、8個のモーターモジュールと2本のバッテリーを、構造材を兼ねるメイン基板に直接差し込む。ロボットは直方体の胴に平行リンクの脚が付く形で、動物の見た目を真似ていない。

アクチュエーターは、ROBOTISの「DYNAMIXEL XL330-M077-T」を8個使う。一般的な教育用ロボットはPWMサーボを使うが、DYNAMIXELは関節ごとに通信で位置や速度、PIDゲインを読み書きできる。開発側は「高速で走り、ジャンプし、自重の2倍を運べる」と説明するが、これはメーカーの申告で、独立した検証は見当たらない。

| 項目 | 内容 |
| --- | --- |
| 大きさ・重さ | 120 × 70 × 70mm、250g |
| メインマイコン | ESP32-C3（基板とコントローラーの両方） |
| バッテリー | 14500のリチウムイオン2本 |
| 拡張 | Qwiic/STEMMA QTコネクタ、5V・3Aを出せるUARTポート、上面の取り付け穴 |
| 操作 | 付属コントローラー（Adafruit製ミニI2Cゲームパッドを使用）。PCにつなぐと無線ドングルになり、Xboxコントローラーも使える |

カメラとモーションセンサーは標準では付かない。

## 価格と選び方

選択肢の価格帯は199〜599ドル。完成品は599ドルで、キット版（シャーシ、バッテリー、リンク、コントローラーなどを含み、組み立てが必要）は8個のDYNAMIXELを別に買う前提になっている。キットの個別価格は、確認できた範囲では書かれていない。

プロジェクトページの比較表では、Petoi Bittle XとHiwonder MechDogが各399ドル、Unitree Go2 Proが2,800ドル以上とされている。これは開発側が作った表なので、そのまま客観的な比較とは受け取れない。製造はElecrowがPCBAと3D印刷を担当し、完成品の最終組み立てはカリフォルニア州クパチーノで行う。発送はMouser Electronicsが担う。部品（とくにDYNAMIXELとメイン基板のIC）の入手難がリスクとして書かれている。

## 日本から見るとどうか

**国内の取扱いは確認できていない。** 日本語でも検索したが、Q8botOneの国内記事や販売店は見つからなかった。Crowd Supplyは世界中のバッカーに配送するとしているが、日本の送料と関税は確認していない。

**技適が関わる。** ESP32-C3を無線に使う構成で、無線機器にあたる。総務省のデータベースには、Espressifの「ESP32-C3-MINI-1」モジュールが登録されている（認証番号201-210888）。ただしQ8botOneという製品としての認証は確認できず、どのモジュールを使うかも、ページから読めたのは基板の型番までだ。技適の有無を言い切れる材料は揃っていない。

**取れる行動。** 構造に興味があるだけなら、募集期間内に進捗を見守る。実際に支援するなら、完成品の599ドルに送料と関税が乗り、納期の遅れもありうると見込む。公開されている設計ファイル（PCB、ファームウェア、CAD）を読むだけでも勉強にはなる。国内の同じ用途の製品は見つけられなかったため、代替品は載せていない。
