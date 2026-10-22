---
title: Romuは15.5×12mmのUSB開発ボード。USB-Aポートに直接挿して、MicroPythonで動かす。Crowd Supplyで$40から
slug: romu-usb-rp2354a-board
seo_title: Romu、USB-Aに挿す超小型ボードは40ドル
x_hook: |
  開発ボードなのに、GPIOピンが1本も無い。
  Bitmerseの「Romu」は、USB-Aポートに直接挿す15.5×12mmの基板。Raspberry PiのRP2354Aを積み、挿してすぐMicroPythonを書ける。
  ・タッチボタンでパスキー認証やマクロ入力
  ・Crowd Supplyで40ドル（約6,000円）から
keyword: Romu
category: pc
date: 2026-10-18
kicker: Bitmerseが、Raspberry PiのマイコンRP2354Aを積んだ15.5×12mmのUSB開発ボード「Romu」をCrowd Supplyで募集中。USB Type-Aポートに直接挿して使い、MicroPythonが最初から入っている。リターンは40ドルから。
tags:
- Romu
- Bitmerse
- RP2354A
- マイコン
- Crowd Supply
- MicroPython
giteki:
  status: 対象外
  number: []
  checked: 2026-10-18
  radio: ""
  note: 無線機能は無く、USB 2.0のみ
images:
- url: "https://www.crowdsupply.com/img/639d/ee3a7df5-2cac-4ea6-9800-99e4ec8f639d_gallery-lg.jpg"
  caption: 基板の表面。中央にRP2354A、右上にキーホルダー用の穴と静電容量式のタッチボタン、右下にブートボタン
- url: "https://www.crowdsupply.com/img/8606/cf86e51c-15d9-4921-b375-660d021f8606_gallery-lg.jpg"
  caption: 各部の名称。タッチボタン、RGB LED、ブートボタン、SWDとUARTのテストポイント、12MHz水晶
- url: "https://www.crowdsupply.com/img/8b0a/13570feb-51c4-493f-b8b3-008cf6eb8b0a_gallery-lg.jpg"
  caption: USB Type-Aの端子側。25セント硬貨と並べた大きさ比較。黄色い3Dプリントの保護パーツが付く
credit: Bitmerse / Crowd Supply プロジェクトページ
sources:
- title: Romu（Crowd Supply プロジェクトページ）
  url: https://www.crowdsupply.com/bitmerse/romu
  publisher: Crowd Supply（公式）
- title: Romu - A Tiny Raspberry Pi RP2354A board for USB application development (Crowdfunding)
  url: https://www.cnx-software.com/2026/10/14/romu-tiny-raspberry-pi-rp2354a-usb-board/
  publisher: CNX Software
deadline: 2026-11-27
alternatives:
  - name: Raspberry Pi Pico 2（Pico 2 / 2H / 2W / 2WHの各型）
    why: Romuと同じRP2350系のRaspberry Pi純正ボードで、国内で今日買える。2Wは無線入りだが技適表示のある国内流通品が出回っている。
    url: https://item.rakuten.co.jp/nanairo-s/pi-pico2/
    merchant: rakuten
    image: "https://thumbnail.image.rakuten.co.jp/@0_mall/nanairo-s/cabinet/denshi/pi-pico/10.jpg"
faq:
- q: Romuとは何ですか
  a: USB Type-Aポートに直接挿す、15.5×12mmの開発ボードです。Raspberry PiのRP2354A（150MHzのデュアルコア）を積み、MicroPythonが最初から入っています。
- q: 日本で買えますか
  a: 掲載時点で、Crowd Supplyのページに日本向けの発送可否の記載は確認できていません。送料は米国が8ドル、国外が一律18ドルと書かれています。出資は購入ではなく、製品が届く保証はありません。
- q: 技適は必要ですか
  a: Romuには無線機能が無く、USB 2.0だけで動くため、技適の対象外です。
- q: いくらですか
  a: 掲載時点でRomu本体は40ドルです。リターン全体は40〜115ドルで、別売りの書き込み用ジグが選べます。
---

Bitmerseが、Raspberry PiのマイコンRP2354Aを積んだ超小型のUSB開発ボード「Romu」を、クラウドファンディングのCrowd Supplyで募集している。基板は15.5×12mmで、USB Type-Aポートに直接挿して使う。ケーブルもブレッドボードも書き込み機も要らず、MicroPythonが最初から入っている。

**まだ製品ではない。** 出資は購入ではなく、納期の遅れや仕様変更が起こりうる。以下の調達額は取得した時点（10月17日）の値で、目標5,000ドルに対し1,080ドル（22%）、支援者は12人だった。募集は2026年11月26日の午後4時（米国太平洋時間）まで。日本時間では27日の朝にあたる。

## 主な仕様

| 項目 | 内容 |
|---|---|
| マイコン | Raspberry Pi RP2354A。Arm Cortex-M33またはHazard3 RISC-Vのデュアルコア、150MHz |
| メモリ | SRAM 520KB、内蔵フラッシュ2MB |
| USB | USB 2.0 フルスピード、Type-Aの端子が基板そのもの |
| 入出力 | 静電容量式タッチボタン1つ、ブートボタン、RGB LED |
| 書き込み | USB DFU、またはSWDのテストポイント |
| サイズ | 15.5×12×1.65mm。3Dプリントの保護パーツが付属 |
| 電源 | USBの5Vから、基板上で3.3Vに降圧 |

## GPIOを捨てた開発ボード

多くの開発ボードは、できるだけ多くのGPIOを引き出すことを競う。Romuはそれをやめて、USBデバイスを作ることだけに絞っている。Crowd Supplyのページが挙げる用途は、ワンタッチのマクロキーボード、FIDO2/U2Fのセキュリティキー、USB MIDIコントローラー、USB HIDのカスタム機器など。デモ用のファームには、タッチ1回でキー入力のマクロを送る、パスキーでログインする、ウェブサイトを開く、という動作が入っている。

デバッグ用の端子は、基板が小さすぎて付けられない。代わりに、別売りの書き込み・デバッグ用ジグを使う。ジグはUSB Type-Cで接続し、標準の20ピンJTAGコネクタ（SWD）とUARTを出す。基板をジグに押し当てるだけで、はんだ付けは要らない。

## 同系統のボードとの比較

ページには、同じ「直接挿すUSB-Aボード」のTomu・Qomu・Somuとの比較表がある。CoreMarkは、Romuが615、Tomuが61.5、QomuとSomuが283.2。価格はRomuが40ドル、Tomuが25ドル、Qomuが49ドル、Somuが35ドル。これらの数字はBitmerse自身が載せたもので、第三者の検証は確認できていない。MicroPythonが最初から入っているのはRomuだけだと表にある。

## 日本で買える？使える？

無線機能が無いため、技適は不要。電波法の面で気にすることは無い。入手は、Crowd Supplyのページで日本向けの発送可否を確認できていない。送料の欄には米国8ドル・国外18ドルとあるが、日本が対象かは掲載時点で書かれていない。出荷はCrowd Supplyの物流パートナーであるMouser Electronics経由とされている。製造はElecrowが担当し、少量の試作はすでに作って試験済みだという。

回路図やPCBデータ、BOM、ケースのSTLは、出荷前にGitHubで公開すると約束されている。ただし掲載時点で、リポジトリの公開は確認できていない。

今日から同じ用途を試したいなら、国内で買えるRaspberry Pi Pico 2が代わりになる。RP2350系のマイコンで、MicroPythonも動く。USB-Aに挿せる小ささと、タッチボタンとRGB LEDが最初から付く点は無い。待つか、Pico 2で先に始めるかは、キーホルダーサイズにこだわるかで決まる。
