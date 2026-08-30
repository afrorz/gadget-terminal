---
title: MNT Research「MNT Station」はCPU/FPGAモジュールを差し替えられるオープンハードウェアPC、Crowd Supplyで9月25日まで支援受付
seo_title: MNT Station、モジュール式オープンPCが299ドル
slug: mnt-station-crowdsupply
keyword: MNT Station
category: pc
date: 2026-08-29
kicker: ベルリンのMNT Researchが、オープンソースの「MNT Reformマザーボード」を土台にしたモジュール式デスクトップ/サーバー筐体「MNT Station」をCrowd Supplyで公開した。Rockchip RK3588やNXP i.MX 8M Plus、AMD/Xilinx Kintex-7 FPGAなど10種類以上のCPU/FPGAモジュールから選んで組み込める。筐体は299ドルから、2026年9月25日まで支援を受け付けている。
tags:
- MNT Research
- MNT Station
- オープンハードウェア
- Crowd Supply
- ミニPC
- 自作PC
x_hook: CPUボードを丸ごと差し替えられるPC。名目上の目標額はわずか1ドル、実質フレキシブル方式の調達。
origin: BER ベルリン
deadline: 2026-09-25
faq:
- q: 日本で買えますか
  a: Crowd Supply経由の海外発送が前提で、日本向けの正規代理店は確認できていません。Crowd Supplyはフルフィルメントパートナーの Mouser Electronics を通じて世界へ配送するとしています。
- q: 技適は必要ですか
  a: 本体基板にはWi-Fi/Bluetooth用のmini PCIeカード(実機写真ではWLE200NXと確認できる型番のモジュール)が組み込まれており、このモジュール自体が日本の技適を取得しているかどうかが焦点になります。MNT Station自体が技適取得済みという記載は確認できていません。
- q: いくらですか
  a: ケースが299ドルから、MNT Reform Mainboard 3.0が429ドル、RCORE RK3588モジュールが899ドル(2026年8月29日時点)。組み合わせにより総額は変動します。
- q: いつ届きますか
  a: Crowd Supplyでの支援受付は2026年9月25日まで。発送予定は2027年1月下旬で、確定した納期ではありません。
images:
- url: https://www.crowdsupply.com/img/837c/54b53322-0d50-4afa-80cf-3256a29f837c_gallery-lg.jpg
  caption: 3色のケースを重ねたところ。背面にEthernet・USB-C等のポートが並ぶ
- url: https://www.crowdsupply.com/img/18df/19cf8eed-f8ac-4ee6-a0eb-9d722efe18df_gallery-lg.jpg
  caption: 黒ケースの背面。Wi-Fi用アンテナ2本とUSB-C給電ケーブルを接続した状態
- url: https://www.crowdsupply.com/img/2c9a/ef5d1edd-42fa-45eb-a3f0-90d890cc2c9a_gallery-lg.jpg
  caption: 内部基板。MNT Reformマザーボードに CPU/FPGA モジュールを1枚差し込んで使う
- url: https://www.crowdsupply.com/img/646d/2baa76d1-cf86-43c4-b037-a0b43d59646d_gallery-lg.jpg
  caption: 空のケースシェル。上下2分割でモジュールへのアクセスが容易な構造
credit: MNT Research Crowd Supplyプロジェクトページ
alternatives:
- name: 【送料無料】GeeekPi N07 ミニタワー NVMe NAS キット Raspberry Pi 5 用、N07 M.2 NVMe SSD Pip PCIe ペリフェラルボード底部付き、M.2 Key-M NVMe SSD 2230/2242/2260/2280 をサポート
  why: 同じくRaspberry Pi 5をベースにNAS/サーバー用途へ組めるキットで、Amazon.co.jpから今日届く。CPUモジュールを差し替えられる自由度はMNT Stationに劣るが、実用のホームサーバー構築ならすぐ試せる。
  url: https://item.rakuten.co.jp/slife/b0ddwlbpsy/?rafcid=wsc_i_is_426d0238-4559-4562-84cd-0ebadd9809ff
  merchant: rakuten
sources:
- title: MNT Station fanless, modular open-hardware computer supports a choice of 10+ Arm CPU or FPGA modules
  url: https://www.cnx-software.com/2026/08/24/mnt-station-fanless-modular-open-hardware-computer-supports-a-choice-of-10-arm-cpu-or-fpga-modules/
  publisher: CNX Software
- title: MNT Station
  url: https://www.crowdsupply.com/mnt-research/mnt-station
  publisher: Crowd Supply
---

MNT ResearchはオープンソースのハックしやすいノートPC「MNT Reform」を長年手がけてきたベルリンのチームである。MNT Stationはそのマザーボード規格をそのままデスクトップ・サーバー用途に転用する筐体で、既存のMNT Reformマザーボードを流用したい人にも、FPGAベースのマシンを一から組みたい人にも対応する。200ピンのモジュールコネクタにCPU/FPGAボードを1枚差し込むだけで、用途に応じて中身を丸ごと入れ替えられるのが最大の特徴だ。

## スペック

| 項目 | 内容 |
| --- | --- |
| 対応CPU/FPGAモジュール | Rockchip RK3588、NXP Layerscape LS1028A、NXP i.MX 8M Plus/8MQ、Raspberry Pi CM4、Amlogic A311D、Rockchip RK3566、AMD/Xilinx Kintex-7 FPGA、Qualcomm QCS6490/QCS8550(開発中) |
| メモリ | 最大32GB LPDDR4(モジュール依存) |
| ストレージ | M.2 NVMe、mPCIe、eMMC(最大256GB)、MicroSD |
| 拡張 | USB 3 Type-A×3、USB Type-C、Gigabit Ethernet、Wi-Fi/Bluetoothモジュール |
| 電源 | USB Type-C PD(65〜100W推奨)、消費電力目安約20W |
| ケース価格 | 299ドルから |
| MNT Reform Mainboard 3.0 | 429ドル |
| RCORE RK3588モジュール | 899ドル |
| 調達状況(2026年8月29日時点) | 目標1ドル(フレキシブルファンディング)に対し9,099ドル、支援者11人 |
| 募集終了 | 2026年9月25日 |
| 発送予定 | 2027年1月下旬 |

Crowd Supplyのこのプロジェクトは目標額を名目上1ドルに設定するフレキシブルファンディング方式で、達成率の数字自体には実質的な意味がない。支援者数・調達額は取得時点の値であり、募集終了までさらに動く。

## 日本から見るとどうか

**これはまだ製品ではない。** Crowd Supplyでの支援は購入の確約ではなく、発送予定の2027年1月下旬も「予定」にすぎない。MNT Researchは過去にMNT Reformノートを実際に出荷してきた実績があるため、完全な初挑戦のプロジェクトよりは信頼材料があるとはいえ、遅延のリスクはクラウドファンディング全般に共通する。

**技適は基板に載る無線モジュール次第。** 実機写真では2本のアンテナとmini PCIeのWi-Fiカードが確認でき、この種の無線モジュールは通常、技適を取得したものと未取得のものが混在する。MNT Station自体、あるいは付属するWi-Fiモジュールが日本の技適を取得しているという記載は確認できておらず、国内で無線機能を有効にして使う場合はこの点を輸入前に確認する必要がある。有線のみで使う分には論点にならない。

**「CPUを差し替えられる」という発想自体が、国内の完成品PC市場にはほぼ無い。** 日本国内でミニPCやNASを買う場合、多くは完成品としてCPU・メモリ構成が固定されている。MNT Stationのように後からCPU/FPGAモジュールだけ入れ替えて延命できる製品は選択肢が乏しく、オープンハードウェアの自由度を求める層には希少な存在といえる。一方で今すぐ実用のNAS・サーバーが欲しいだけなら、Raspberry Pi 5をベースにした国内で今日買えるキットのほうが手堅い。
