---
title: WavKong「V2700」、基地局用の歪み補正をWi-Fiに持ち込んだ独自チップ「RPU」搭載のWi-Fi 6ルーター。Kickstarterで1,074人が支援し、希望価格399ドルで一般販売へ
slug: wavkong-v2700-rpu-wifi6-router
seo_title: WavKong V2700は399ドル、技適は？
x_hook: |
  メッシュを増やさず、ルーターの電波そのものを磨く。
  WavKong「V2700」は携帯基地局の歪み補正を5GHz帯に持ち込んだWi-Fi 6ルーター。独自チップ「RPU」を載せる。
  ・Kickstarterで1,074人が支援
  ・希望価格399ドル（約6万円）
keyword: WavKong V2700
category: pc
date: 2026-10-31
kicker: 米国発のWavKongが、基地局用のデジタル歪み補正（DPD）を5GHz帯に持ち込んだ独自チップ「RPU」を載せたWi-Fi 6ルーター「V2700」を、Kickstarterの出荷完了を受けて一般販売に移した。希望価格は399ドルで、1台で最大約15,000平方フィートをカバーするとメーカーはうたう。
tags:
- WavKong
- V2700
- Wi-Fi 6
- ルーター
- Kickstarter
origin: HKG 香港
giteki:
  status: 確認できない
  number: []
  checked: 2026-10-31
  radio: Wi-Fi 6（2.4GHz / 5GHz）
  note: "総務省DBで登録者名「WavKong」を検索したが該当なし。型番での登録は未確認"
images:
- url: "https://www.wavkong.com/cdn/shop/files/4-_-2_fcbf8072-163e-42a9-9aab-8675b6e68106.png?v=1785209981"
  caption: V2700の正面。黒い縦長の筐体で、中央にRPUのロゴ、下部にWavKongのロゴと4つのLED（Sys、2.4GHz、5GHz、Mesh）が並ぶ
credit: WavKong 公式製品ページ
sources:
- title: WavKong V2700 Takes a Signal-First Approach to Whole-Home Wi-Fi（TechPowerUp、プレスリリース）
  url: https://www.techpowerup.com/354314/wavkong-v2700-takes-a-signal-first-approach-to-whole-home-wi-fi
  publisher: TechPowerUp
- title: V2700 Long Range Wi-Fi Router for Large Homes（WavKong 公式製品ページ）
  url: https://www.wavkong.com/products/v2700-long-range-wifi-router-for-large-homes
  publisher: WavKong（公式）
alternatives:
  - name: TP-Link Archer AX3000
    why: 同じAX3000クラスのWi-Fi 6ルーターで、国内の公式店で買える。EasyMesh対応で、足りなければ同社製品でノードを足せる。
    url: https://item.rakuten.co.jp/tplinkdirect/4895252502688/
    merchant: rakuten
    image: "https://thumbnail.image.rakuten.co.jp/@0_mall/tplinkdirect/cabinet/06321509/archer-ax3000.jpg"
faq:
- q: V2700はいくらですか
  a: 希望価格は399ドルです（TechPowerUpの編集注による）。公式ストアの掲載時点の販売価格も399ドルで、通常価格は539ドルと表示されています。
- q: 日本で買えますか
  a: 掲載時点で、国内の販売店や日本向けの案内は確認できていません。公式サイトは「supported markets」へ発送するとしていますが、日本が含まれるかは確認できていません。
- q: 技適は取得していますか
  a: 確認できていません。総務省の技適データベースで登録者名「WavKong」を検索しましたが、該当はありませんでした。国内で電波を出す使い方をするなら、事前の確認が必要です。
- q: 1台でどのくらいの範囲をカバーできますか
  a: メーカーの社内テストでは、米国カリフォルニアの平屋の木造住宅で、屋内外あわせて最大約15,000平方フィートでした。壁材や配置で変わる、メーカーの主張です。
---

米国のWavKongが、独自の無線処理チップ「RPU」を載せたWi-Fi 6ルーター「V2700」を一般販売に移した。TechPowerUpが2026年10月30日にプレスリリースを載せた。Kickstarterで支援を募ったのち、2026年9月29日に出荷を完了している。**Kickstarter分の出荷は終わっており、現在は公式サイトで購入できる製品である。** 以下の性能値はメーカーの社内テストか利用者の報告による。

## 何が違うのか

多くの家庭用ルーターは、電波の増幅時にひずみが出て、遠くで速度が落ちる。WavKongはこの歪みを、携帯基地局や衛星通信で使われるデジタルプリディストーション（DPD）で、送信前に補正する。それを5GHz帯の送信経路に入れた専用チップがRPU（Radio Processing Unit）で、開発に6年かけたという。160MHz幅・1024-QAMでの試験では、信号品質の指標EVMが約−29.3dBから−41.2dBへ、12dB以上改善したとされる。

メーカーが挙げる実測は次のとおり。いずれも条件つきの値で、第三者の検証ではない。

- カリフォルニアの平屋の木造住宅の離れた庭で、V2700は123Mbps、比較したメッシュ構成は4.2Mbps
- 技術系クリエイターのJeff Springer氏の比較では、V2700 1台が3台構成のメッシュのうち2地点で上回り、残り2地点では下回った
- オーストラリアの利用者は、ルーター＋メッシュ2台から切り替えて5GHzの下りが約250Mbpsから500Mbps超になったと報告

## 主な仕様

| 項目 | 内容 |
|---|---|
| 規格 | Wi-Fi 6（AX3000）、チャネル幅は最大160MHz、WPA3 |
| SoC | MediaTek MT7981 |
| メモリ | RAM 256MB、フラッシュ128MB |
| アンテナ | 2.4GHz×2、5GHz×2 |
| 有線ポート | ギガビットのWAN×1、LAN×3 |
| 使い方 | ルーターまたはアクセスポイント。2台でメッシュも組める |
| 電源 | 12V/4A、100〜240V |
| 保証 | 1年 |

## 支援と価格

Kickstarterは2026年4月22日に始まり、支援者1,074人から3,272,087香港ドル（40万米ドル超）を集めた。希望価格は399ドル。公式ストアでは掲載時点で399ドルの販売価格に通常価格539ドルが併記されている。

## 日本で買える？使える？

- **買えるか：** 国内の販売店は確認できていない。日本語でも検索したが、国内での正規販売の案内は見つからなかった（掲載時点）。公式サイトは「supported markets」へ発送するとしており、日本が含まれるかは分からない
- **技適：** 確認できていない。総務省のデータベースを登録者名「WavKong」で検索したが該当は無かった。Wi-Fiルーターは電波を出す機器なので、国内で使うには技適が要る。技適の無い機器を国内で使うと電波法に触れる
- **仕様の注意：** 試験は米国の住宅での結果で、日本の住宅や5GHz帯のチャネル規制に合わせた値ではない。出力の上限は国ごとに違い、海外仕様のまま国内で同じ性能が出るとは限らない
- **取れる行動：** 技適が確認できるまでは様子を見るのが安全。今すぐ広い家のWi-Fiを直したいなら、国内正規品のWi-Fi 6ルーターに、EasyMeshなどでノードを足す方法がある
