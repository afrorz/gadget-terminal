---
title: "Wiiリモコンの形をしたESP32-S3汎用リモコン「OpenMote」がCrowd Supplyで資金調達完了、Home Assistant連携を標準搭載"
seo_title: OpenMoteはWiiリモコン型リモコン、99ドルから
slug: openmote-esp32-s3-wiimote-remote
category: weird
date: 2026-09-20
kicker: ロサンゼルスのHat & Hammerが、Nintendo Wiiリモコンの形状を再利用したプログラマブル汎用リモコン「OpenMote」をCrowd Supplyで公開した。ESP32-S3を核にWi-Fi・Bluetooth・赤外線・6軸IMUを積み、Home Assistant連携を標準搭載する。掲載時点で目標額(US$1、達成条件はごく低く設定)に対しUS$94,980を支援者686人から集め、すでに資金調達は完了している。**クラウドファンディングであり、まだ製品ではない。**
tags:
- OpenMote
- ESP32-S3
- Wiiリモコン
- Home Assistant
- Crowd Supply
x_hook: 懐かしのWiiリモコンの中身が、ESP32-S3搭載のスマートホームリモコンに置き換わった。ボタン11個は自由に割り当て可能で、赤外線・Wi-Fi・Bluetoothを1台に詰め込みながら基板とファームウェアは出荷前にすべてオープンソース化される予定
deadline: "2026-10-30"
origin: LAX ロサンゼルス
images:
- url: "https://www.crowdsupply.com/img/d904/49ef64eb-aaa1-4682-8269-3394aa9ad904_aa-md.jpg"
  caption: 左から「Mod Your Own」用の基板2枚(1枚は電源・振動モーター搭載、もう1枚はOpenMoteロゴ入り)と、右端に実物のNintendo Wiiリモコン。同じ筐体に収まるサイズであることがわかる
- url: "https://www.crowdsupply.com/img/87aa/4c021ded-b226-41d2-8b4e-0f0e595d87aa_md-xl.jpg"
  caption: Wiiリモコン筐体とOpenMote基板の表裏を並べた仕様図。基板上にはESP32-S3-WROOM-1モジュールや各ボタンの割り当てが番号で示されている
credit: Hat & Hammer(Crowd Supplyプロジェクトページ)
buy:
  - name: OpenMote(Crowd Supply)
    url: https://www.crowdsupply.com/hat-and-hammer/openmote
    price: Ready To Go(完成品)99ドル、OpenMote Board(基板のみ、要Wiiリモコン筐体)59ドル、いずれも米国内送料込み(掲載時点)
    ships_jp: true
    giteki: 未取得
    note: クラウドファンディングであり、まだ製品ではない。Crowd Supplyのページでは「international calculated at checkout」として日本を含む海外発送に対応するが、送料は購入手続き時に確定する。適合表明はEU/UKのDeclaration of Conformityが用意されているのみで、日本の技適については言及が無く未取得として扱う。Wi-Fi・Bluetooth・ESP-NOWを使う無線機能は国内で無許可のまま利用すると電波法に抵触する。配送予定は2027年2月28日を予定しているが、クラウドファンディングのため確定した日程ではない。
alternatives:
  - name: Nature Remo nano
    why: 技適取得済みの国内メーカー製スマートリモコンで、Alexa/Google Home/Siriと連携し赤外線家電をまとめて操作できる。OpenMoteのようなボタン単体でのプログラマブル操作や6軸IMUによるジェスチャー入力は無いが、「スマホ経由で家中の家電をリモコン化する」という目的は今日から満たせる。
    url: https://www.amazon.co.jp/dp/B0C6V1CJB7
    merchant: amazon
faq:
  - q: 日本で買えますか
    a: Crowd Supplyの海外発送で購入自体は可能で、送料は購入手続き時に確定します。ただし技適は掲載時点で未取得です。
  - q: 技適は取得していますか
    a: 掲載時点で未取得です。EU/UKの適合表明は用意されていますが、日本の技術基準適合証明への言及はありません。Wi-Fi・Bluetoothなどの無線機能を国内で使うには技適取得が必要です。
  - q: いくらですか
    a: 完成品の「Ready To Go」が99ドル、基板のみの「OpenMote Board」が59ドルです(いずれも掲載時点、米国内送料込み)。
  - q: いつ届きますか
    a: 2027年2月28日の配送を予定していますが、クラウドファンディングのため確定した日程ではありません。
sources:
  - title: "OpenMote - An ESP32-S3 programmable universal remote in a Wiimote shell (Crowdfunding)"
    url: https://www.cnx-software.com/2026/09/19/openmote-an-esp32-s3-programmable-universal-remote-in-a-wiimote-shell/
    publisher: CNX Software
  - title: "OpenMote turns a Wiimote-style remote into an ESP32-S3 Home Assistant controller"
    url: https://linuxgizmos.com/openmote-turns-a-wiimote-style-remote-into-an-esp32-s3-home-assistant-controller/
    publisher: LinuxGizmos
  - title: "OpenMote"
    url: https://www.crowdsupply.com/hat-and-hammer/openmote
    publisher: Crowd Supply
---

ロサンゼルスのHat & Hammerが、Nintendo Wiiリモコンの筐体をそのまま流用したプログラマブル汎用リモコン「OpenMote」をCrowd Supplyで公開した。Crowd Supplyのプロジェクトページによれば、資金調達はすでに達成済みで、掲載時点で支援者686人からUS$94,980を集めている。募集は現地時間2026年10月29日午後5時(太平洋夏時間、日本時間換算で10月30日午前9時ごろ)まで続く。**クラウドファンディングであり、まだ製品ではない。**なお、キャンペーン終了後もCrowd Supplyのストアで継続販売される予定だという。

## 中身はESP32-S3、ボタンは全部プログラマブル

OpenMoteのハードウェアはESP32-S3-WROOM-1(デュアルコア240MHz、16MBフラッシュ、8MB PSRAM)が核。Wiiリモコンと同じ12個のボタン配置のうち11個が自由に割り当て可能なプログラマブルボタンで、残り1個は電源ボタンだ。6軸IMU(加速度計・ジャイロ)によるジェスチャー操作、940nm赤外線送信機と38kHz受信機による家電のリモコン機能、Wi-Fi 802.11 b/g/n・Bluetooth 5 LE・ESP-NOWでの無線通信を備える。オーディオ面ではMAX98357A搭載の3.2Wスピーカーとマイク、拡張用のQwiic/STEMMA QTコネクタ、ハプティックモーター、4個のインジケーターLEDも搭載する。バッテリーは1200mAhのリチウム電池。

ソフトウェア面では、出荷時にESPHomeファームウェアが書き込み済みで、Home Assistantと直接連携できる。物理ボタンやジェスチャーを部屋ごとの自動化・照明・メディア操作に割り当てられ、クラウドサービスに依存しない構成だ。Bluetoothゲームパッドとしても使える。CNX Softwareによれば、Hat & Hammerは配送開始前に回路図・基板データ・部品表・Arduinoライブラリ・Home Assistantファームウェアの完全なオープンソース化を予定している。

購入形態は完成品の「Ready To Go」(99ドル)と、手持ちのWiiリモコン筐体に組み込む基板のみの「Mod Your Own」(59ドル)の2種類。

## スペック

| 項目 | 内容 |
| --- | --- |
| プロセッサ | ESP32-S3-WROOM-1(デュアルコア240MHz) |
| メモリ | 16MBフラッシュ、8MB PSRAM |
| ボタン | 12個(11個プログラマブル、1個電源) |
| センサー | 6軸IMU(加速度計・ジャイロ) |
| 赤外線 | 940nm送信機、38kHz受信機 |
| 無線 | Wi-Fi 802.11 b/g/n、Bluetooth 5 LE、ESP-NOW |
| オーディオ | 3.2Wスピーカー(MAX98357A)、PDM MEMSマイク |
| バッテリー | 1200mAhリチウム |
| 価格 | Ready To Go 99ドル/OpenMote Board 59ドル(掲載時点) |

## 日本から見るとどうか

Crowd Supplyは日本を含む海外発送に対応しており、送料は購入手続き時に計算される。ただし技適については掲載時点で未取得だ。プロジェクトページで確認できる適合表明はEU/UKのDeclaration of Conformityのみで、日本の技術基準適合証明への言及は無い。OpenMoteはWi-Fi・Bluetooth・ESP-NOWのいずれも本体の中核機能であり、赤外線リモコンとしての最低限の利用に絞っても、電源を入れた時点でこれらの無線モジュールが動作する設計である可能性が高い。技適の無い無線機を国内で使うと電波法上の問題になるため、届いてもそのまま使うのは避けたほうがよい。

「スマホから家中の家電をまとめてリモコン化したい」という目的だけであれば、国内メーカー製のNature Remo nanoが技適取得済みで今日から使える代替になる。OpenMoteのような物理ボタンでの操作やIMUによるジェスチャー入力、オープンソースでの改造はできないが、赤外線家電をスマートスピーカーで操作するという体験自体は今すぐ試せる。

情報源はCNX Software、LinuxGizmos、Crowd Supplyプロジェクトページの3件で、複数媒体が同時に取り上げている。調達額・支援者数はいずれも取得時点の値で、キャンペーン終了までに変動する。
