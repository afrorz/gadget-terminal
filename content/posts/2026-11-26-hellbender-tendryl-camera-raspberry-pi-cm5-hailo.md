---
title: Hellbender Tendryl CameraはRaspberry Pi CM5とHailo-8を85mm角の箱に収めたエッジAIカメラ、599ドル
slug: hellbender-tendryl-camera-raspberry-pi-cm5-hailo
seo_title: Tendryl Cameraは599ドル、AI推論カメラの中身
x_hook: |
  カメラの箱の中で、Raspberry Pi 5相当のCPUとAIチップが動いている。
  米ピッツバーグ製の「Tendryl Camera」は、26TOPSのHailo-8とスピーカー、マイクまで85mm角に収めた。
  ・PoE+給電に対応
  ・RaspberryPi OSでそのまま開発できる
keyword: Tendryl Camera
category: pc
date: 2026-11-26
kicker: 米Hellbenderの「Tendryl Camera」は、Raspberry Pi CM5、26TOPSのAIアクセラレーターHailo-8、1,190万画素のカメラ、スピーカーとマイクを、85×82×58mmのファンレスの筐体に収めたエッジAIカメラ。価格は599ドルで、27WのUSB PDアダプター付き。
tags:
- Tendryl Camera
- Hellbender
- Raspberry Pi CM5
- Hailo-8
- エッジAI
giteki:
  status: 確認できない
  number: []
  checked: 2026-11-26
  radio: Wi-Fi 5, Bluetooth 5.0
  note: 型番が公表されておらず、総務省DBで特定できない
images:
- url: "https://hellbender.com/wp-content/uploads/2026/04/tendryl-render-square.png"
  caption: 本体のレンダリング。前面にレンズ、スピーカーの穴、マイク、本体の側面にHDMIとUSB-Cが3つ並ぶ
- url: "https://hellbender.com/wp-content/uploads/2026/04/tendryl-feature-diagram-2.png"
  caption: 各部の解説図。背面にはPoE+のコネクターと取り付け穴
credit: Hellbender 公式製品ページ
origin: PIT ピッツバーグ
sources:
- title: Tendryl Camera（Hellbender 公式製品ページ）
  url: https://hellbender.com/product/tendryl-camera/
  publisher: Hellbender（公式）
- title: Tendryl Camera ドキュメント
  url: https://hellbenderinc.github.io/hellbender-product-documentation/tendryl-cam/2.0/
  publisher: Hellbender（公式）
- title: "Compact Edge AI camera packs Raspberry Pi CM5, Hailo-8 NPU, 12MP sensor, speaker and microphone"
  url: https://www.cnx-software.com/2026/11/25/compact-tendryl-edge-ai-camera-packs-raspberry-pi-cm5-hailo-8-npu-12mp-sensor-speaker-and-microphone/
  publisher: CNX Software
alternatives:
  - name: Entaniya 組込みセット（Raspberry Pi AIカメラ＋マウントプレート）
    why: Sony IMX500を載せたRaspberry Pi AI Cameraに、三脚用の1/4-20ネジ穴つきマウントプレートを組み合わせた国内販売のセット。AI処理をカメラ側で行う試作を、本体を別に用意して今日から始められる。
    url: https://item.rakuten.co.jp/entaniya/185981193/
    merchant: rakuten
    image: "https://thumbnail.image.rakuten.co.jp/@0_mall/entaniya/cabinet/12456717/12628098/185981193.jpg"
faq:
- q: Tendryl Cameraはいくらですか
  a: 公式サイトでは599ドルで、27WのUSB PDアダプターと、標準画角または広角のカメラが付きます。送料や関税は別です。
- q: 何ができるカメラですか
  a: Raspberry Pi OSで動き、Hailo-8（26TOPS）で物体検出などの画像認識をカメラの中で処理できます。コンピュータービジョンの試作用の製品と説明されています。
- q: 日本で買えますか
  a: 日本の販売元は確認できていません。公式サイトで日本へ発送されるかは、購入手続きで確かめる必要があります。
- q: 技適は取得していますか
  a: 確認できていません。Wi-Fi 5とBluetooth 5.0を内蔵しますが、型番が公表されておらず、総務省のデータベースで特定できませんでした。
---

Tendryl Cameraは、米ピッツバーグのHellbenderが設計・組み立てするエッジAIカメラだ。Raspberry Pi CM5（4GB RAM・16GB eMMC）、26TOPSのHailo-8、Raspberry Pi Camera Module 3（約1,190万画素・オートフォーカス）、スピーカー、マイクを、85×82×58mm、415gの筐体に収める。価格は599ドル（掲載時点）。

製品として売られているもので、クラウドファンディングの募集ではない。ただ、取得できた情報は公式ページ、ドキュメント、CNX Softwareの記事だけで、実機のレビューは見つかっていない。

## カメラの中でAIまで動かす

筐体はファンレスで、金属のヒートシンクがそのまま外装になる。CM5はBroadcom BCM2712（Cortex-A76、4コア、2.4GHz）で、HDMIは最大4Kp60。有線LANはギガビットで、PoE+（15W以上が必要）から給電できる。USB-Cは3つあり、電源、データ、OSの書き込み用に分かれる。

画像認識は、Hailo-8がカメラの映像を受けて処理する。公式のドキュメントには、rpicamのコマンドやHailoのSDKを使う手順が載っている。CNX Softwareは、公開されているのはRaspberry Pi OSベースのファームウェアイメージだけで、GitHubのサンプルは少ないと書いている。

| 項目 | 内容 |
|---|---|
| SoC | Raspberry Pi CM5（BCM2712、メモリ4GB、eMMC 16GB） |
| AIアクセラレーター | Hailo-8（26TOPS） |
| カメラ | Camera Module 3。標準は水平66°×垂直41°、広角は水平102°×垂直67° |
| 無線 | Wi-Fi 5（2.4GHz/5GHz）、Bluetooth 5.0 |
| 有線 | ギガビットLAN（PoE+対応）、HDMI、USB-C×3 |
| センサー | 6軸IMU、温度・湿度・気圧 |
| 電源 | 5V/3A以上のUSB PD、またはPoE+ |
| 動作温度 | 推奨5〜35℃ |
| 取り付け | 1/4インチ-20の取り付け穴が2か所 |

CNX Softwareは類似品として、Sony IMX500を載せたArducamのAI Cameraキットを挙げる。ただし、あちらは別のAI処理チップを持たず、無線と音声もない。CM4を使うEDATECとArducamの製品もある。

## 日本で買える？使える？

**掲載時点で、日本の販売元は確認できていない。**「Tendryl Camera」を日本語で検索しても、国内の紹介は見つからなかった。公式サイトの購入手続きで日本へ発送されるか、送料や関税がいくらになるかは、実際に確かめる必要がある。

Wi-Fi 5とBluetooth 5.0を内蔵するため、日本で無線を使うなら技適が要る。型番が公表されておらず、総務省のデータベースでは特定できなかった。有線LANとPoE+だけで使えば無線は使わないが、無線機能を切れるかどうかは確認できていない。

同じ用途を今日から試したいなら、国内で買えるRaspberry Pi AI Cameraを使う方法がある。カメラ側でAI処理をするので、本体のRaspberry Piは別に用意する形になる。この記事は、日本向けの情報が出たら追記する。
