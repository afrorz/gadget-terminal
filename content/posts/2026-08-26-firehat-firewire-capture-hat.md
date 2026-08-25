---
title: "MiniDVカメラの映像をRaspberry Piで直接録画するオープンソースHAT「Firehat」、Crowd Supplyで目標の141%を調達"
seo_title: "Firehat、Pi5用FireWireキャプチャが79ドル"
slug: firehat-firewire-capture-hat
keyword: Firehat
category: weird
date: 2026-08-26
kicker: Computer Equipment Groupが、Raspberry Pi 5やRadxa ROCK 2Fなど対応SBC向けにFireWire（IEEE 1394／i.LINK）経由でDV・HDV映像を直接キャプチャできるオープンソースHAT「Firehat」をCrowd Supplyで公開した。目標7,500ドルに対し、開始から141%にあたる1万621ドルを集めている。価格は79ドルから。
tags: [Firehat, Raspberry Pi, FireWire, クラウドファンディング, Crowd Supply, オープンソースハードウェア]
x_hook: MiniDVカメラの映像を、Raspberry Piがそのまま録画する。基板1枚で調達目標の141%。
embeds:
  - type: youtube
    id: xYHg6bqzR0Q
    caption: Crowd Supply公式によるFirehatのOLEDメニュー画面デモ
faq:
  - q: 日本で買えますか
    a: Crowd Supply経由での海外発送が前提。米国外への配送は送料+12ドルで、国内正規代理店の取り扱いは確認できていない。
  - q: 技適は必要ですか
    a: FireWire（IEEE 1394）は有線接続のみで無線機能を持たないため、Firehat自体は技適の対象外。ただし組み合わせるRaspberry Pi等ホスト機のWi-Fi／Bluetoothを使う場合は、そのホスト機側の技適取得状況が別途関わる。
  - q: いくらですか
    a: Crowd Supplyでの支援価格は79ドルから（2026年8月26日時点）。目標7,500ドルに対し141%にあたる1万621ドル、支援者82人を集めている。
  - q: いつ届きますか
    a: Crowd Supplyのクラウドファンディングのため、配送は「予定」であり確定ではない。プロジェクトページ上の配送予定は2027年2月3日から。
images:
  - url: "https://www.crowdsupply.com/img/1635/a0e800ea-ff66-41a8-9313-e4f6fcf61635_aa-md.jpg"
    caption: 基板単体。左端がFireWire（6ピン）ポート、中央がOLED画面
  - url: "https://www.crowdsupply.com/img/679d/a08bb9ee-dfe0-4a71-8fef-aa8327ab679d_md-xl.jpg"
    caption: Sony製DVカムコーダーとFireWireケーブルで接続し、録画中の状態。画面に録画時間を表示
  - url: "https://www.crowdsupply.com/img/83b3/6f6ab859-6820-495c-85bf-6771d1df83b3_md-xl.jpg"
    caption: 基板の真上からの写真。ボタン3個とブザーを備える
credit: Computer Equipment Group Crowd Supplyプロジェクトページ
sources:
  - title: "Firehat is an open-source FireWire DV capture HAT for SBCs with Raspberry Pi PCIe FFC connector (Crowdfunding)"
    url: https://www.cnx-software.com/2026/08/25/firehat-open-source-firewire-dv-capture-hat-pcie-sbc-raspberry-pi-5-radxa-rock-2f/
    publisher: CNX Software
  - title: "Firehat"
    url: https://www.crowdsupply.com/computer-equipment-group/firehat
    publisher: Crowd Supply
---

Computer Equipment Groupが、Raspberry Pi 5やRadxa ROCK 2FなどPCIe対応SBC向けのFireWireキャプチャボード「Firehat」をCrowd Supplyで公開した。VIA VT6315N IEEE 1394コントローラーと6ピンFireWireポートを備え、MiniDVやDigital8、DVCAM、DVCPRO、HDVといったテープ規格のカムコーダーから、映像を圧縮・変換せずに元のDV／HDVストリームのままストレージへ記録できる。価格は79ドルから、目標額7,500ドルに対し2026年8月26日時点で1万621ドル（141%）、支援者82人を集めている。

## スペック

| 項目 | 内容 |
| --- | --- |
| コントローラー | VIA VT6315N（IEEE 1394） |
| ポート | 6ピンFireWire／i.LINK／DV |
| ホスト接続 | PCIe 2.0 x1（FPCコネクタ経由） |
| 対応SBC | Raspberry Pi 5、Radxa ROCK 2F、その他PCIe FFC対応SBC |
| 画面 | 1.3インチ モノクロOLED |
| 入力 | タクタイルボタン×3、SK6812 RGB LED×3、PWM制御ブザー |
| 拡張 | 40ピン 2.54mm GPIOヘッダー |
| サイズ | 56×70×12mm |
| 重量 | 25g |
| ライセンス | ハードウェア：CERN OHL-S、ソフトウェア：GPL |
| 価格 | 79ドルから |
| 調達状況 | 目標7,500ドルに対し1万621ドル（141%）、支援者82人 |
| 募集終了 | 2026年10月8日（米太平洋時間17:00） |
| 配送予定 | 2027年2月3日から |

出典はCNX SoftwareとCrowd Supplyのプロジェクトページ。調達額・支援者数・残り日数は2026年8月26日時点の値で、募集期間中は変動する。

## なぜ今FireWireなのか

DVは単なる過去の遺物ではなく、インターレース特有の動きや小型センサーのハイライト、90年代後半〜2000年代前半のカムコーダーに特有の圧縮感を「味」として今も使う映像作家やスケーター、ミュージシャンが存在する。従来この映像を取り込むには、FireWireポートを持つ古いMacBookや生産終了済みのキャプチャカードに頼るしかなく、ハードウェアの故障や環境の陳腐化が課題だった。Firehatはこの1ポートのためだけに古いパソコン一式を維持する代わりに、小型のSBCを使った専用キャプチャ機を組めるようにする。ハードウェア設計（KiCadデータ、基板図、3Dモデル）はCERN OHL-Sで、ソフトウェアはGPLで公開されるオープンハードウェアプロジェクトでもある。

## 日本から見るとどうか

**これはまだ製品ではない。** Crowd Supplyでの支援は購入の確約ではなく、141%という調達額も2026年8月26日時点のスナップショットにすぎない。配送予定の2027年2月3日は「予定」であり、開発・製造の遅延は珍しくない。

**技適は基本的に関係ないが、輸入と言語の壁は残る。** FireWireは無線を使わない有線規格なので、Firehat本体に技適の取得・未取得という論点自体が生じない。一方でCrowd Supply経由の海外発送が前提となり、日本語のマニュアルやサポートは期待しにくい。組み合わせるRaspberry Pi自体は国内で技適取得済みの製品が流通しているため、SBC側の心配は少ない。

**日本にはDVカムコーダーの中古市場が厚いという追い風がある。** ソニーのHandycamやキヤノン、JVCなど、日本メーカー製のMiniDV・HDVカムコーダーは国内の中古市場に数多く出回っている。古いテープ資産のデジタル化ニーズがある人にとっては、海外の小規模クラウドファンディングとはいえ実用上の接点は見出しやすい製品と言える。ただし基板単体の製品であり、SBC・ケーブル・ストレージ・組み立ての知識を自分で用意する前提であることは踏まえておきたい。
