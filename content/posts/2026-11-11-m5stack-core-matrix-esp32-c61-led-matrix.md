---
title: M5Stack Core Matrix、16×16の白色LEDを前面に並べたESP32-C61コントローラー。29.99ドル
slug: m5stack-core-matrix-esp32-c61-led-matrix
seo_title: Core Matrixは29.99ドル、日本で使える？
x_hook: |
  画面の無いマイコンが、256個のLEDで文字を出す。
  M5Stackの「Core Matrix」は、前面に16×16の白色LEDを並べたWi-Fi 6対応のIoTコントローラー。
  ・ESP32-C61、IMU・ブザー・microSD内蔵
  ・29.99ドル（約4,500円）
keyword: Core Matrix
category: pc
date: 2026-11-11
modified: 2026-11-11
kicker: M5Stackが、前面に16×16の白色LEDマトリクスを備えたESP32-C61搭載のIoTコントローラー「Core Matrix」を出した。2.4GHzのWi-Fi 6対応で、価格は29.99ドル（送料・税別）だ。
tags:
- M5Stack
- Core Matrix
- ESP32-C61
- マイコン
- IoT
giteki:
  status: 確認できない
  number: []
  checked: 2026-11-11
  radio: Wi-Fi 6（2.4GHz）/ Bluetooth LE 5.0
  note: 公式の製品写真の裏面ラベルに技適マークと番号の記載が見えるが、総務省DBでは本機を確認できなかった
images:
- url: "https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1274/C158_CoreMatrix_main_pictures_01.webp"
  caption: 各部の名称図。前面の16×16白色LED、USB-C、microSD、3つのボタンの位置が分かる
- url: "https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1274/C158_CoreMatrix_main_pictures_02.webp"
  caption: 前面から。黒い筐体に256個の白色LEDが並ぶ
- url: "https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1274/C158_CoreMatrix_main_pictures_04.webp"
  caption: 裏面。基板の端子配置と、型式・認証マークを印刷したラベルが見える
credit: M5Stack 公式ドキュメント
clips:
- file: m5stack-core-matrix-esp32-c61-led-matrix/scroll.mp4
  caption: "白い光の粒で文字やアイコン（16×16の白色LED）"
  credit: "M5Stack 公式 YouTube"
  source: "https://www.youtube.com/watch?v=u_HbVF10zYI"
- file: m5stack-core-matrix-esp32-c61-led-matrix/tilt.mp4
  caption: "傾けると表示が動く（6軸センサー内蔵）"
  credit: "M5Stack 公式 YouTube"
  source: "https://www.youtube.com/watch?v=u_HbVF10zYI"
- file: m5stack-core-matrix-esp32-c61-led-matrix/bars.mp4
  caption: "センサーをつないで表示（M5-BusとGroveの端子）"
  credit: "M5Stack 公式 YouTube"
  source: "https://www.youtube.com/watch?v=u_HbVF10zYI"
sources:
- title: CoreMatrix（公式ドキュメント）
  url: https://docs.m5stack.com/en/core/CoreMatrix
  publisher: M5Stack
- title: M5Stack Core Matrix ESP32-C61 IoT controller features 16×16 LED matrix, WiFi 6, and 6-axis IMU
  url: https://www.cnx-software.com/2026/11/09/m5stack-core-matrix-esp32-c61-iot-controller-features-16x16-led-matrix-wifi-6-and-6-axis-imu/
  publisher: CNX Software
alternatives:
  - name: M5Stack ATOM Matrix v1.1
    why: 同じM5Stackの5×5 RGB LED版。国内の電子部品店で買え、技適番号（211-260311）を総務省DBで確認済み。
    url: https://item.rakuten.co.jp/marutsuelec/3790989/
    merchant: rakuten
    image: "https://thumbnail.image.rakuten.co.jp/@0_mall/marutsuelec/cabinet/04881820/260723/3790989_2.jpg"
faq:
- q: 日本で買えますか
  a: CNX Softwareによると、AliExpressとM5Stackの公式ストアで買えます。国内の販売店での取り扱いは、掲載時点で確認できていません。
- q: 技適は取得していますか
  a: 確認できていません。公式の製品写真のラベルに技適マークが見えますが、総務省のデータベースでは本機を見つけられませんでした。
- q: いくらですか
  a: CNX Softwareによると29.99ドルで、送料と税は別です（掲載時点）。
- q: 何でプログラムしますか
  a: Arduino IDEと、M5Stackのビジュアルプログラミング環境UIFlow2に対応します。
---

M5Stackの「Core Matrix」は、前面全体に16×16の白色LEDを並べたIoTコントローラーだ。CNX Softwareによると、AliExpressとM5Stackの公式ストアで29.99ドル（送料・税別）で買える。2022年ごろからある小型の「ATOM Matrix」（5×5のRGB LED）の後継にあたる位置づけで、LEDは白の単色になった代わりに256個へ増えた。

## 何ができるのか

前面のLEDには、アイコンや簡単なアニメーション、機器の状態表示、通知などを出せる。モノクロなので、画像や文字を精細に見せる用途ではない。本体には6軸センサー（BMI270）があり、傾けたり動かしたりする操作にも反応できる。

M5-BusとGroveの端子があるため、M5Stackのモジュールやセンサーをつなげられる。電池は付属しないが、USB-C給電のほか、外部の3.7Vバッテリーでも動く。

## 主な仕様

| 項目 | 内容 |
|---|---|
| SoC | ESP32-C61HR8（RISC-V単一コア、最大160MHz） |
| メモリ | SRAM 320KB、PSRAM 8MB、フラッシュ 16MB |
| 無線 | 2.4GHz Wi-Fi 6、Bluetooth LE 5.0 |
| 表示 | 16×16 白色LED（TM1680で駆動） |
| センサー・入力 | 6軸IMU、ボタン3つ＋電源ボタン、パッシブブザー |
| 記憶 | microSDスロット |
| 拡張 | M5-Bus、Grove（HY2.0-4P）、USB拡張端子 |
| サイズ・重さ | 54×54×11.6mm、28.9g |
| 価格 | 29.99ドル（掲載時点、送料・税別） |

パッケージの中身は本体と2.0mmの六角レンチだ。プログラムはArduino IDEか、ブロックで組むUIFlow2で書ける。

## 日本で買える？使える？

M5Stack製品は国内の電子部品店でも広く売られているが、Core Matrixを扱う国内の店は掲載時点で見つかっていない。海外のストアから買う場合は、Wi-Fi 6とBluetoothを内蔵するため技適が問題になる。

公式の製品写真の裏面ラベルには、技適マークと番号が印刷されているように見える。ただし、総務省の電波利用ホームページで検索しても、本機の登録は確認できなかった。登録が反映されていないだけの可能性もあり、この点は断定できない。

国内で今すぐ使える物を求めるなら、技適を確認できているATOM Matrix v1.1が国内の店で買える。LEDは5×5のRGBと小さいが、状態表示の用途なら足りる。Core Matrixの国内取り扱いを待つのが無難だ。
