---
title: Radxa「Linkr」実機レビュー、USBメモリ大のIP KVMはHTTPS・2段階認証・Tailscaleに対応。59ドルから
slug: radxa-linkr-ip-kvm
seo_title: Radxa Linkrレビュー、59ドルのIP KVMの実力
x_hook: |
  サーバー用の遠隔操作装置が、USBメモリの大きさになった。
  Radxaの「Linkr」はHDMIに挿すだけで、遠くのPCのBIOS画面まで操作できる。2段階認証とTailscaleにも対応する。
  ・59ドルから
  ・1080p30と1440p60の映像
keyword: Radxa Linkr
category: pc
date: 2026-11-16
kicker: HDMI端子に挿してPCを遠隔操作できる、USBメモリ大のIP KVM「Radxa Linkr」を、CNX Softwareが実機で試した。HTTPS、2段階認証、Tailscaleに対応し、価格は59ドルから。共有クリップボードと仮想ドライブは未対応だった。
tags:
- Radxa Linkr
- IP KVM
- Tailscale
- 遠隔操作
- ホームラボ
giteki:
  status: 確認できない
  number: []
  checked: 2026-11-16
  radio: Wi-Fi（Ethernet、USBでも接続可）
  note: レビュー機は中国向け小売パッケージ（型番MV004）。日本向けの型番は確認できない
images:
- url: "https://radxa.com/linkr/kvm/overview/smooth-operation.webp"
  caption: Linkr の本体。HDMIコネクターが付いた細長い黒い筐体で、右の小さい画像は別の角度から見た姿
- url: "https://radxa.com/linkr/kvm/overview/link1.webp"
  caption: 接続図。操作する側のノートPCとLinkrをUSB-Cでつなぎ、対象のPCにはHDMIで映像を、USBでキーボードとマウスの入力を送る
- url: "https://radxa.com/linkr/kvm/overview/link2.webp"
  caption: ネットワーク経由の接続図。Linkr に有線LANをつなぎ、ルーター越しに遠くのノートPCから操作する
credit: Radxa 公式製品ページ
sources:
- title: "Radxa Linkr review – A compact IP KVM with HTTPS, 2FA authentication, and Tailscale support"
  url: https://www.cnx-software.com/2026/11/15/radxa-linkr-review-a-compact-ip-kvm-with-https-2fa-authentication-and-tailscale-support/
  publisher: CNX Software
- title: "Radxa Linkr – A USB drive-sized IP KVM with USB-C, Ethernet, and WiFi support"
  url: https://www.cnx-software.com/2026/08/30/radxa-linkr-a-usb-drive-sized-ip-kvm-with-usb-c-ethernet-and-wifi-support/
  publisher: CNX Software
- title: Radxa Linkr 製品ページ
  url: https://radxa.com/products/linkr/linkr/
  publisher: Radxa（公式）
alternatives:
  - name: GL.iNet Comet PoE（GL-RM1PE）
    why: 国内の通販で買える、Tailscale対応のIP KVM。Linkrより大きく高価だが、同じレビュアーはGL-RM1系を「より完成度が高い」と評価している。
    url: https://item.rakuten.co.jp/daily-store/gr-e9duis7x3e/
    merchant: rakuten
    image: "https://thumbnail.image.rakuten.co.jp/@0_mall/daily-store/cabinet/g/40/e9duis7x3e-6.jpg"
faq:
- q: Radxa Linkrはいくらですか
  a: CNX Softwareによると、AliExpress、Amazon、Arace、Allnetなどで59ドルからです。送料・税・手数料で販売先ごとに変わります。
- q: 何ができますか
  a: HDMIで対象PCの映像を取り込み、USBでキーボードとマウスの入力を送ります。ブラウザから操作でき、OSが起動する前のBIOS画面にも入れたとレビューにあります。
- q: 日本で買えますか
  a: 掲載時点で、日本の販売元や国内向けの案内は確認できていません。海外通販では購入できるとされています。
- q: 技適は取得していますか
  a: 掲載時点で確認できていません。レビュー機は中国向けの小売パッケージ（型番MV004）で、日本向けの型番は確認できません。
---

「Radxa Linkr」は、対象PCのHDMI端子に直接挿して使う、USBメモリ大のIP KVMだ。映像をHDMIで取り込み、キーボードとマウスの操作をUSBで送るため、遠くから別のPCの画面を見て操作できる。CNX Softwareが8月に仕様を紹介し、11月15日に実機での使用感を公開した。

## 接続と設定

Linkrは、USB、Ethernet、Wi-Fiのいずれでも使える。レビューでは、付属のUSB-C-Ethernetケーブルでスイッチにつなぎ、電源はUSB-Aから取り、HDMIはミニPCのHDMI端子に直接挿した。起動中のLEDは赤の点滅、準備完了で青の点灯になる。

専用アプリは不要で、ブラウザで操作する。初期設定はlinkr.nowのサイトに従う。レビュアーのFirefoxでは最初は機器が見つからず、設定の `security.mixed_content.block_active_content` を変更して通った。Chromeでは問題なく検出されたという。

## 映像と機能

- 映像：最大で1080p30と1440p60。コーデックはH.264、H.265、MJPEG。H.265はファームウェア1.6.0で追加され、レビューではChromeでは60fpsで動いたがFirefoxではエラーになった
- 安全面：HTTPS（自己署名証明書）、2段階認証、Tailscale経由のリモート接続に対応
- 音声：「仮想サウンドカード」を有効にするとHDMIの音声を取れた
- BIOS：再起動後にEscキーでBIOS画面に入れた

Tailscaleは無料アカウントで試され、スマートフォンのFirefoxから携帯回線経由でもつなげた。

## 気になった点

- 初期設定は暗号化されないHTTPで行われ、ユーザー名とパスワードのハッシュが通信に出る。気になる場合はUSB接続で設定するほうがよい
- ファームウェア1.0.0から1.6.0へのOTA更新は約1時間かかり、設定が消えた
- 共有クリップボードと仮想ドライブは、必要な「Linkrd」プラグインが入手できず試せなかった
- 画面の言語は英語と中国語のみ
- レビュアーは電源制御を含むGL.iNet Comet（GL-RM1）のほうが完成度は高いとしつつ、そちらは大きく高価だと書いている

セキュリティは設計の重点だが、レビュアー自身が第三者による監査は無いと断っている。

## 日本で買える？使える？

**日本の販売元や国内向けの案内は、掲載時点で確認できていない。** 海外では、AliExpress、Amazon、Arace、Allnetなどで59ドルからとされる。

注意したいのは、レビュー機が中国向けの小売パッケージ（型番MV004）だった点だ。Linkrは Wi-Fi を備えるため、日本で電波を出して使うには技適が要るが、今回は総務省のデータベースで確認できなかった。有線LANとUSBだけで使う分には電波を出さないが、Wi-Fiは国内で使える状態かどうか分からない。

ホームラボやミニPCの管理に今すぐ使いたいなら、国内の通販で買えるGL.iNetのIP KVMが選択肢になる。待つ場合は、日本向けの型番と技適の情報を見てから決めればよい。
