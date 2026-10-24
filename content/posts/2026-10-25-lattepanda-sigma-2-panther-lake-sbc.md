---
title: LattePanda「Sigma 2」、Core Ultra X7 358HとメモリLPDDR5X 64GBを3.5インチ基板に。10GbE2口、予約2,599ドル
slug: lattepanda-sigma-2-panther-lake-sbc
seo_title: LattePanda Sigma 2は2,599ドル、64GB基板
x_hook: |
  35B級のAIモデルを動かすという、3.5インチの基板。
  LattePanda「Sigma 2」は、Core Ultra X7と64GBメモリ、10GbE2口を載せたシングルボード。AI性能は最大180TOPS。
  ・Thunderbolt 4が2口、M.2は4スロット
keyword: Sigma 2
category: pc
date: 2026-10-25
kicker: DFRobotのLattePandaが、Intel Core Ultra X7 358H（Panther Lake）と64GBのLPDDR5Xを146×102mmの基板に載せたシングルボード「Sigma 2」の予約を始めた。Thunderbolt 4が2口、10GbEが2口、M.2が4スロットで、1TBのSSD込みの予約価格は2,599ドルだ。
tags:
- LattePanda
- Sigma 2
- Core Ultra X7
- Panther Lake
- シングルボードコンピューター
giteki:
  status: 対象外
  number: []
  checked: 2026-10-25
  radio: ""
  note: "公式の仕様に無線モジュールの記載が無い（Wi-Fi用のM.2 E-Keyスロットのみ）。無線機能を持たない基板として対象外と判断"
images:
- url: "https://dfimg.dfrobot.com/enshop/image/data/DFR1316/DFR1316_Main_01.jpg"
  caption: 冷却ファン付きの基板。手前に10GbEのRJ45が2口とUSB、奥にHDMIとUSB-C
- url: "https://dfimg.dfrobot.com/enshop/image/data/DFR1316/DFR1316_Back_03.jpg"
  caption: 裏面。M.2のM-Keyスロットが3つ（1つにSSDを装着）と、E-Keyスロット
- url: "https://dfimg.dfrobot.com/enshop/image/data/DFR1316/DFR1316_Dim_02.jpg"
  caption: 寸法は146×102mm。定規と並べた上面
credit: DFRobot 公式製品ページ
sources:
- title: LattePanda Sigma 2 - The Embeddable AI Single Board Server（DFRobot公式製品ページ。価格は2026年10月25日時点）
  url: https://www.dfrobot.com/product-3164.html
  publisher: DFRobot（公式）
alternatives:
  - name: GMKtec EVO-X2（Ryzen AI Max+ 395搭載ミニPC、128GB）
    why: ローカルLLM向けの大容量メモリを積んだ完成品のミニPCで、国内の通販で買える。基板ではなくケース付きなので、すぐ使い始められる。
    url: https://item.rakuten.co.jp/gmktecdirect/evo-x2/
    merchant: rakuten
    image: "https://thumbnail.image.rakuten.co.jp/@0_mall/gmktecdirect/cabinet/10289896/evo-x2/imgrc0127790539.jpg"
faq:
- q: LattePanda Sigma 2とは何ですか
  a: Intel Core Ultra X7 358H（Panther Lake）と64GBのメモリを載せた、3.5インチのシングルボードコンピューターです。ローカルのAI処理や組み込み用途を想定しています。
- q: いくらですか
  a: DFRobotの予約ページで2,599ドル、通常価格は2,799ドルと表示されています（2026年10月25日時点）。1TBのSSDと冷却ファン、電源アダプターが付きます。
- q: 無線は付いていますか
  a: 公式の仕様にWi-FiやBluetoothの記載はありません。無線LAN用のM.2 E-Keyスロットがあり、カードを足して使う想定とみられます。
- q: 日本で買えますか
  a: 日本向けの販売や国内の代理店は、掲載時点で確認できていません。日本語の紹介記事も見つかっていません。
---

DFRobotのLattePandaが、シングルボードコンピューター「Sigma 2」の予約を始めた。Intel Core Ultra X7 358H（Panther Lake）と、64GBのLPDDR5X-8533メモリを、146×102mmの3.5インチ基板に載せる。DFRobotの製品ページでは予約価格が2,599ドル、通常価格は2,799ドルと表示されている（2026年10月25日時点）。**予約受付の段階で、出荷時期は確認できていない。**

## 何が載っているか

| 項目 | 内容 |
|---|---|
| CPU | Core Ultra X7 358H、16コア16スレッド、最大4.8GHz |
| GPU | Intel Arc B390（12 Xeコア）、最大2.5GHz |
| AI性能 | CPU・GPU・NPUの合計で最大180TOPS（INT8）。内訳はGPU 122、NPU 50、CPU 8 |
| メモリ | 64GB LPDDR5X-8533（デュアルチャンネル、理論帯域136.5GB/s）。最大59GBをGPUに割り当て可 |
| ストレージ | WD SN7100 1TBを搭載（Ubuntuと各種ドライバー導入済み） |
| 映像 | HDMI 2.1、eDP 1.5、Thunderbolt 4経由のDisplayPort 2.1 |
| ネットワーク | 10GbEが2口 |
| USB | Thunderbolt 4が2口、USB 3.2 Gen 2のType-Aが2口、USB 2.0のType-Aが2口 |
| 拡張 | M.2 M-Keyが3スロット（PCIe 5.0 ×2、4.0 ×4、4.0 ×1）、M.2 E-Key、OCuLink（PCIe 4.0 ×2） |
| 補助チップ | RP2350（MicroPython導入済み。センサーやアクチュエーターの制御用） |
| OS | Windows 11、Ubuntu 24.04 LTS以降 |

電源はDC 15〜20V、またはUSB-C PDの20V。付属品には冷却ファン、金属の底板、RTC電池、電源アダプターとEU・US・UKのACケーブルが入る。

## 狙いはローカルAI

公式ページは、35Bクラスの量子化MoEモデルを基板上で動かせるとうたう。付属のSSDには、OpenVINO Model Server、OpenClaw、ローカルのAIモデルが入った状態で届く。Intel OpenVINO、Ollama、llama.cppに対応する。

前世代のSigmaとの比較は公式の自社テストの数字で、テキスト生成が約2倍、平均のDC入力電力は35Wから38Wに増え、アイドルは5Wから4.5Wに下がるとされる。第三者のレビューはまだ確認できておらず、これらは自社測定の値だ。

## 日本で買える？使える？

日本向けの販売や国内の代理店は、掲載時点で確認できていない。日本語の紹介記事も見つからなかった。購入は予約中のDFRobotの海外ストアが入口になるが、日本への送料、関税、保証の扱いは、ページから確認できなかった。

技適は、無線機能が基板に載っていないため対象外と判断している。仕様にWi-FiやBluetoothの記載はなく、無線LANを使うならM.2 E-Keyスロットに別のカードを足す形になる。その場合は、足したカード側の技適を確認する。

電源は付属のACアダプターで、ケーブルはEU・US・UK向けだ。日本向けの表示と、PSEの扱いは確認できていない。2,599ドルという価格と、出荷時期が決まっていない点を踏まえると、今すぐ試したい人には向かない。

同じ用途（ローカルLLMを手元で動かす）なら、国内の通販で買えるRyzen AI Max+ 395搭載のミニPCがある。GMKtecのEVO-X2は128GBメモリのモデルで、完成品として国内で買える。ただし基板形状ではなく筐体入りの完成品なので、組み込みや拡張が目的の人は、Sigma 2の出荷と日本への送り方が見えるまで待つことになる。
