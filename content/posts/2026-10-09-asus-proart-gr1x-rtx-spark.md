---
title: ASUS「ProArt GR1X」はNVIDIA RTX Spark搭載の1.1リットルミニPC、統合メモリ最大128GBで120BパラメータのLLMを動かす
slug: asus-proart-gr1x-rtx-spark
seo_title: ASUS ProArt GR1X、128GBメモリのミニPC
x_hook: |
  1.1リットルの箱1台で、1200億パラメータのLLMを本体だけで動かす。ASUSの「ProArt GR1X」は、NVIDIA RTX Sparkと最大128GBの統合メモリを150mm四方に収めたWindowsミニPC。
  ・CPUは20コア、GPUは6,144コア
  ・10GbE、Wi-Fi 7
  ・発売は年内の予定
keyword: ProArt GR1X
category: pc
date: 2026-10-09
kicker: ASUSが、NVIDIA RTX Spark Superchipを載せた1.1リットルのミニPC「ProArt GR1X」を発表した。統合メモリは64GBと128GB、本体は150×150×51mmで、128GB版は1200億パラメータのLLMを本体だけで動かせるとしている。発売は年内の予定。
tags:
- ASUS
- ProArt
- GR1X
- RTX Spark
- ミニPC
images:
- url: "https://dlcdnwebimgs.asus.com/files/media/202605/c3379200-8584-4929-b246-ac81e169d1ce/V3/img/design-main-dark.png"
  caption: ブラックモデル。前面は格子状の通気口で、右上に電源ボタン、上面にProArtのロゴ
- url: "https://dlcdnwebimgs.asus.com/files/media/202605/c3379200-8584-4929-b246-ac81e169d1ce/V3/img/design-main-light.png"
  caption: シルバーモデル。前面は同じ格子状の通気口
- url: "https://dlcdnwebimgs.asus.com/files/media/202605/c3379200-8584-4929-b246-ac81e169d1ce/V3/img/spec-main.png"
  caption: 背面の端子。左からセキュリティスロット、電源入力のUSB-C、USB-C 3つ、HDMI、10GbE
credit: ASUS 公式製品ページ
sources:
- title: ProArt GR1X Mini PC
  url: https://www.asus.com/displays-desktops/mini-pcs/proart-mini-pc-series/proart-gr1x-mini-pc/
  publisher: ASUS（公式）
- title: Asus launches ProArt GR1X Mini PC with Nvidia RTX Spark Superchip
  url: https://www.gizmochina.com/2026/10/08/asus-proart-gr1x-mini-pc-launched-specs-price/
  publisher: Gizmochina
alternatives:
- name: MINISFORUM MS-S1 Max
  why: Ryzen AI Max+ 395と128GBメモリを載せた、国内の楽天市場で買えるミニPC。大きなAIモデルを手元で動かす用途の現行品
  url: https://item.rakuten.co.jp/minisforum-minipc/ma-s1max/
  merchant: rakuten
  image: "https://thumbnail.image.rakuten.co.jp/@0_mall/minisforum-minipc/cabinet/13903623/imgrc0102308617.jpg"
faq:
- q: ProArt GR1Xの価格はいくらですか
  a: 掲載時点でASUSは価格を発表していません。64GBと128GBの2構成を、一部の販売店で売るとしています。
- q: いつ発売されますか
  a: 年内に発売される予定と報じられています。具体的な日付は発表されていません。
- q: 日本で買えますか
  a: 国内の発売・価格の発表は、掲載時点で確認できていません。ASUS公式ページには、発売通知の登録欄があります。
- q: 技適は取得していますか
  a: Wi-Fi 7とBluetooth 5.4を備えますが、技適の取得は掲載時点で確認できていません。国内で発売されるなら、取得した型番で売られる見込みです。
---

ASUSがProArt GR1Xを発表した。NVIDIA RTX Spark Superchipを使ったミニPCで、20コアのArm系CPU「Grace」と、6,144コアのBlackwell世代GPUを1つのチップにまとめている。メモリはCPUとGPUが共有するLPDDR5Xで、64GBと128GBの2構成。ASUSによると、128GB版は1200億パラメータのLLMを本体だけで動かせる。価格は未発表で、発売は年内の予定だ。

## 150mm四方に何が入っているか

| 項目 | 内容（ASUS公式ページ・Gizmochinaの記載） |
|---|---|
| チップ | NVIDIA RTX Spark Superchip（Grace CPU 20コア、Blackwell RTX GPU 6,144コア） |
| AI性能 | 最大1ペタフロップス（FP4） |
| メモリ | 64GB / 128GB、CPUとGPUの共有メモリ（LPDDR5X、NVLink-C2C接続） |
| 本体 | 150×150×51mm、約1.1リットル、1.48kg |
| 冷却 | ファン2基、ヒートパイプ4本、TDP 140W。24時間稼働を想定 |
| 端子（背面） | 10GbE、HDMI 2.1、USB-C 3つ（DisplayPort対応）、電源入力用USB-C |
| 無線 | Wi-Fi 7、Bluetooth 5.4 |
| ストレージ | M.2 PCIe 5.0 / 4.0 スロット2基 |
| 色 | ブラックとシルバー |

4Kモニターを最大4台つなげる。OSはWindowsで、ASUSは「Windowsの互換性を保ったまま」と説明している。CUDAに対応し、ComfyUIと、Nous Researchのオープンソースのエージェント「Hermes」との連携が用意されている。

## 何に使う機械か

共有メモリの大きさが売りだ。一般にGPUのメモリは、PC本体のメモリと分かれていて、大きなAIモデルが載らなくなる。GR1Xは128GBをCPUとGPUで共有するため、モデルの置き場を気にせずに済む、とASUSは説明している。ASUSの公式ページには、1,440pで100fps以上のゲームや、90GBの3Dシーンのレンダリングといった用途も並ぶ。これらはメーカーの数値で、実機での検証は編集部では確認していない。

## 日本から見るとどうか

入手：「ProArt GR1X 国内 発売」で検索したが、ASUS JAPANの発表や国内の価格は見つからなかった。ASUSの公式ページに発売通知の登録欄があるだけで、まだ発売前だ。海外での価格も発表されていない。

技適：Wi-Fi 7とBluetooth 5.4を備える。技適の取得は掲載時点で確認できていない。国内で売られる製品なら、技適を取った型番になるはずだが、並行輸入で個人が買う場合は、無線を使う前に技適の有無を確かめる必要がある。

電源：電源は背面のUSB-Cから入る方式で、ASUSの資料の範囲では、出力や付属品の詳細は確認できていない。

代替：同じ「共有メモリが大きいミニPC」なら、国内の楽天市場で買えるMINISFORUM MS-S1 Maxなどが現行品としてある。ただしチップの系統が違い、GR1XがGraceとBlackwellを使うのに対し、こちらはAMDだ。CUDAが必要な人は、GR1Xの価格と国内発売を待つ理由がある。
