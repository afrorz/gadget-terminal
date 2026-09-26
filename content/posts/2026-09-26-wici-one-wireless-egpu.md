---
title: Wici Oneはケーブル無しでRTX 5090をWi-Fi 7越しに共有する無線eGPU、早期予約1,999ドルから
seo_title: Wici Oneは無線eGPU、1,999ドルから
slug: wici-one-wireless-egpu
keyword: Wici One
category: pc
date: 2026-09-26
kicker: 米カリフォルニア州パロアルトのスタートアップWiciが、ケーブルを使わずWi-Fi 7経由で外部GPUを利用する「Wici One」を発表した。RTX 5060 Ti搭載モデルは早期登録価格1,999ドル(通常2,599ドル)、出荷は2026年第4四半期を見込むという。
tags:
  - Wici One
  - eGPU
  - Wi-Fi 7
  - RTX 5090
  - RTX 5060 Ti
x_hook: ケーブルを1本も挿さずにRTX 5090がまるごと共有できるという箱が出た。ただしWi-Fi 7の理論値46.1Gbpsのうち実際に出るのは11.5Gbpsで、遅延の数値は公表されていない
origin: SJC サンノゼ
status: SCHEDULED
status_note: 出荷は2026年Q4を予定
images:
  - url: "https://wici.ai/images/product/hero-wici-one.webp"
    caption: 波状のアルミ外装とパンチング仕上げのグリルを持つWici One本体。上面に「WiCi」のロゴが刻印されている
  - url: "https://wici.ai/images/product/product-external.webp"
    caption: 正面から見たWici One。左側は波状のアルミパネル、右側は通気用のパンチンググリル
  - url: "https://wici.ai/images/product/product-xray-io.webp"
    caption: 内部透視図。USBポート群と基板、冷却ファンの配置が確認できる
  - url: "https://wici.ai/images/product/explode-view-3.webp"
    caption: 分解図。電源ユニット、マザーボード、GPU、冷却ファンが積層構造で収まっている様子がわかる
credit: Wici公式サイト(wici.ai)
faq:
  - q: 日本で買えますか
    a: 公式サイトに国際発送や対象国の記載が無く、日本への発送は掲載時点で確認できていません。購入は現在ニュースレター登録・先行登録の段階です。
  - q: 技適は取得していますか
    a: 公式発表に技適に関する記載は無く、掲載時点で未確認です。Wi-Fi 7が製品の中核機能であり、有線での代替接続手段は公開資料で確認できていません。
  - q: いくらですか
    a: RTX 5060 Ti搭載モデルが早期登録価格1,999ドル、通常予定価格2,599ドルです(いずれも掲載時点)。RTX 5090搭載モデルの価格は未発表です。
  - q: いつ発売されますか
    a: 公式FAQによれば出荷開始は2026年第4四半期を見込むとしていますが、確定した日程ではありません。
sources:
  - title: "Wici Wireless eGPU Promises RTX 5060 Ti and 5090 Performance Over Wi-Fi 7"
    url: https://www.techpowerup.com/353099/wici-wireless-egpu-promises-rtx-5060-ti-and-5090-performance-over-wi-fi-7
    publisher: TechPowerUp
  - title: "WiCi One: Untethered GPU power for your personal AI"
    url: https://wici.ai/wici-one
    publisher: Wici
---

米カリフォルニア州パロアルトのスタートアップWiciが、Wi-Fi 7経由でGPUを共有する「Wici One」を発表した。Thunderbolt 5やOCuLink、MCIO 8iなどケーブル接続のeGPUが相次ぐなか、ケーブルを一切使わずノートPCやタブレットからGPUにアクセスする点が特徴だ。RTX 5060 Ti搭載モデルは早期登録価格1,999ドル(通常予定価格2,599ドル)で、出荷は2026年第4四半期を見込むという。

## 構成はGPUだけでなく「小さなPCまるごと」

Wici Oneは単なるGPUボックスではない。CPU・ストレージまで内蔵した独立したプラットフォームで、RAMの仕様は公開されていないことから、処理はGPU側のVRAMに依存する設計とみられる。ラインアップは2構成で、価格・スペックが公表されているのはRTX 5060 Ti搭載モデルのみだ。

| 項目 | RTX 5060 Tiモデル | RTX 5090モデル |
| --- | --- | --- |
| GPU | GeForce RTX 5060 Ti(16GB GDDR7) | GeForce RTX 5090(32GB GDDR7) |
| CPU | Intel Core 3 100U | Intel Core Ultra 7 255H |
| ストレージ | NVMe 1TB | NVMe 4TB |
| 価格 | 早期登録1,999ドル/通常予定2,599ドル | 未発表 |

通信はWi-Fi 7を採用し、4×4 MIMO・320MHz幅・4096-QAMという構成。TechPowerUpによれば、Wi-Fi 7の理論上の最大速度は約46.1Gbpsだが、この構成の実効速度は最大でも11.5Gbpsにとどまり、しかもごく短距離・低干渉の環境でしか出ないとみられるという。レイテンシに関する具体的な数値はWici側から公表されていない。

## 用途はゲームよりもAI・レンダリング

Wiciはゲーミング性能として、RTX 5060 Tiモデルで『サイバーパンク2077』が4K・Ultraプリセット・DLSS4使用時に80fps、『Black Myth: Wukong』が4K・Cinematicプリセットで60fpsに達すると主張する。ただし遅延に敏感なゲーミング用途は同社の主眼ではなく、想定される主な用途はローカルのAIワークロードとGPUアクセラレーションによる3Dレンダリングだとしている。手元の端末からジョブをWici One側のGPUへネットワーク越しに送り、処理を完了させてから結果だけを返す、という動作イメージだ。

## 日本から見るとどうか

公式サイトには国際発送や対象国についての記載が無く、日本への発送が可能かどうかは掲載時点で確認できていない。購入導線も現時点では一般販売ではなく、ニュースレター登録と「パイオニアプラン」への申し込み(上位10件のアイデアは製品を無償提供)という先行登録の段階にとどまる。

技適についても公式発表に記載は無い。Wi-Fi 7がWici Oneの通信手段のすべてであり、有線接続に切り替えられる代替手段は公開資料からは見当たらない。仮に技適未取得のまま日本国内でWi-Fi機能を有効にすれば電波法違反となる可能性があるが、この製品は無線接続そのものが売りであるため、有線運用による回避策も期待しにくい。加えてWiciは今回が初の製品発表とみられる新興企業で、量産・出荷の実績はまだ無い。価格は米ドル表記のままで、掲載時点のものである。

情報源はTechPowerUpとWici公式サイト(wici.ai)の2件。価格・出荷時期はいずれも掲載時点の情報で、正式発売までに変更される可能性がある。
