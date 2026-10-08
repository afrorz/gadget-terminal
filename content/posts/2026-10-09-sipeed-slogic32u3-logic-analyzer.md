---
title: Sipeed「SLogic32U3」、10Gbps USB 3.2接続で32チャンネル・最大1400MS/sのロジックアナライザがクラウドファンディングに
slug: sipeed-slogic32u3-logic-analyzer
seo_title: Sipeed SLogic32U3、32chで1400MS/sの仕様
x_hook: |
  59×51×13mmのアルミ筐体で、32chのロジックアナライザが1400MS/sまで出る。Sipeedの「SLogic32U3」は、USB 3.2 Gen2接続で波形をPCのメモリやディスクにそのまま流し込む。
  ・ブラウザだけで動くWebアプリ付き
  ・オプションでオシロスコープにもなる
keyword: SLogic32U3
category: pc
date: 2026-10-09
kicker: Sipeedが、USB 3.2 Gen2（10Gbps）で接続する32チャンネルのロジックアナライザ「SLogic32U3」をKickstarterで募集している。4チャンネルなら1400MS/s、32チャンネル同時でも200MS/sで、波形はPCのメモリやディスクにストリーミングする。
tags:
- Sipeed
- SLogic32U3
- ロジックアナライザ
- Kickstarter
- 電子工作
images:
- url: "https://wiki.sipeed.com/hardware/zh/logic_analyzer/slogic32u3/assets/DCIM/SLogic32U3-hero.jpg"
  caption: Raspberry Pi系のボードにプローブをつなぎ、USB-CでノートPCに接続した使用例。画面にはデコード結果が並ぶ
- url: "https://wiki.sipeed.com/hardware/zh/logic_analyzer/slogic32u3/assets/MISC/view-front-mini-hdmi.jpg"
  caption: 前面のMini-HDMI端子が4つ。1端子あたり8チャンネルを束ねる
credit: Sipeed 公式Wiki
sources:
- title: SLogic32U3 Introduction
  url: https://wiki.sipeed.com/hardware/en/logic_analyzer/slogic32u3/Introduction
  publisher: Sipeed（公式Wiki）
- title: Sipeed SLogic32U3 - A high-speed 10 Gbps USB 3.2 logic analyzer (Crowdfunding)
  url: https://www.cnx-software.com/2026/10/09/sipeed-slogic32u3-high-speed-10-gbps-usb-3-2-logic-analyzer/
  publisher: CNX Software
alternatives:
- name: ZEROPLUS ロジックアナライザ Logic Cube LAP-C(16032)
  why: 国内の電子部品通販で買えるUSB接続のロジックアナライザ。クラファンの完成を待たず、今日から使える
  url: https://item.rakuten.co.jp/marutsuelec/99620/
  merchant: rakuten
  image: "https://thumbnail.image.rakuten.co.jp/@0_mall/marutsuelec/cabinet/04881820/85_1/99620.jpg"
faq:
- q: SLogic32U3は何チャンネルで、どこまで速いですか
  a: 32チャンネルです。サンプリングレートは4チャンネルで1400MS/s、8チャンネルで800MS/s、16チャンネルで400MS/s、32チャンネルで200MS/sです。
- q: 10Gbpsは実際に出ますか
  a: 10GbpsはUSBの回線速度です。Sipeedは実効の連続ストリームを800MB/s（6.4Gbps）としています。
- q: どのソフトで使えますか
  a: 公式にはSLogicView、ngscopeclient、sigrok-cliに対応し、インストール不要のWebアプリ「SLogicWeb」もあります。
- q: 技適は必要ですか
  a: 公式仕様に無線機能の記載はなく、USB-Cのバスパワーで動く有線の計測機器です。技適の対象外と判断できます。
- q: 日本で買えますか
  a: 国内の取扱いは掲載時点で確認できていません。支援額・価格・締切・日本への発送可否も、取得できた資料では確認できていません。
---

Sipeedが、世界初のUSB 3.2 Gen2対応ロジックアナライザとうたう「SLogic32U3」のクラウドファンディングを始めた。2025年に出た3.2Gbps接続の「SLogic16U3」の後継機で、32チャンネル、最大1400MS/s、デジタル信号帯域350MHzという仕様だ。クラウドファンディングは製品の購入ではなく、出資である。この記事の時点で、支援額・価格・締切はプロジェクトページを読み込めず確認できていないため、書いていない。

## 何が速いのか

波形を本体に溜めずに、PCへそのまま流し込む設計になっている。本体には2GbitのDDR3があり、これを弾力的なバッファにして、実効800MB/s（6.4Gbps）でPCのメモリやディスクへストリーミングする。USBの回線速度は10Gbpsだが、実効値はそれより低い。キャプチャできる長さは本体のメモリではなく、PC側の空きで決まる。

| 項目 | 仕様（Sipeed公式Wikiの記載） |
|---|---|
| チャンネル | 32（Mini-HDMI端子4つ、各8チャンネル） |
| サンプリングレート | 1400MS/s（4ch）、800MS/s（8ch）、400MS/s（16ch）、200MS/s（32ch） |
| デジタル信号帯域 | 350MHz |
| 入力電圧 | 0〜10V、しきい値は0〜6Vで0.1V刻み |
| 入力インピーダンス | 100kΩ |
| 接続 | USB-C（USB 3.2 Gen2 / Gen1 / 2.0 HS） |
| 筐体 | CNCアルミ、59×51×13mm |
| 電源 | USBバスパワー、定格5V 65mA |
| オプション | 4チャンネルADCモジュール（8ビット、100MS/s、アナログ帯域10MHz、安全入力±15V） |

Wikiは、SD UHS-I、eMMC HS200、Octal-SPIなどの高速バスの観測に足りる帯域だと説明している。プローブは15cmの同軸シールドケーブルで、Mini-HDMI端子の1つが8チャンネルを束ねる。ADCモジュールを足すと、同じ本体がサンプリングオシロスコープになる。

## ソフトウェア

標準はSLogicViewで、ngscopeclientとsigrok-cliも使える。Webアプリ「SLogicWeb」はインストール不要で、ブラウザからキャプチャでき、Android端末でも動くとされている。ファームウェアは無線ではなく、オンラインで更新できる。

## 日本から見るとどうか

技適：SLogic32U3は有線のUSB機器で、公式仕様に無線機能の記載はない。技適の対象外と判断してよい。

入手：「SLogic32U3 国内 発売」で検索したが、国内の販売や取扱店は見つからなかった。Sipeedは前世代のSLogic16U3をAliExpressの公式ストアなどで売っており、今回も同様の経路が考えられるが、日本への発送可否は確認できていない。クラウドファンディングの出資は、遅延・仕様変更・未達のリスクがあり、納期は予定にすぎない。

代替：すぐ使いたいなら、国内の通販で買えるUSB接続のロジックアナライザがある。ただし、SLogic32U3のように32チャンネルを200MS/s以上で連続ストリーミングできる製品ではない。

向いている人：組み込み機器のバスを高速に観測したい電子工作・開発の人。数MHzのI2CやUARTを見る程度なら、ここまでの性能は要らない。出荷実績が積み上がり、価格と日本への発送条件が確定してから動くのが安全だ。
