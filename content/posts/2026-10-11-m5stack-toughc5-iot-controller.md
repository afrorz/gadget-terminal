---
title: M5Stack「ToughC5」は5GHz対応Wi-Fi 6とZigbee/Threadを載せた防水IoTコントローラー、2インチ画面で49.90ドル
slug: m5stack-toughc5-iot-controller
keyword: M5Stack ToughC5
category: pc
date: 2026-10-11
kicker: M5Stackが屋外向けのIoTコントローラー「ToughC5」を公式ストアで売り出した。ESP32-C5を載せ、2.4/5GHzのWi-Fi 6、BLE 5、Zigbee/Threadに対応する。価格は49.90ドル。
seo_title: M5Stack ToughC5は49.90ドル、5GHz対応
x_hook: 5GHz対応のWi-Fi 6とZigbee/Threadを載せた、2インチ画面つきの屋外IoTコントローラー。M5Stack「ToughC5」が49.90ドル。
tags:
- M5Stack
- ESP32-C5
- IoT
- Wi-Fi 6
- Zigbee
faq:
- q: M5Stack ToughC5はいくらですか
  a: M5Stack公式ストアの掲載時点で49.90ドルです。送料と税は別です。
- q: 旧モデルのToughと何が違いますか
  a: 公式の比較表では、ToughC5は2.4/5GHzのWi-Fi 6とZigbee/Threadに対応し、SoCがESP32-C5になりました。一方、旧Toughにある1Wスピーカーはなくなり、パッシブブザーになっています。
- q: 日本で買えますか
  a: ToughC5の国内取扱いは掲載時点で確認できていません。旧モデルのM5Stack Toughは、楽天市場の販売店などで国内向けに売られています。
- q: 技適は取得していますか
  a: ToughC5の技適は確認できていません。総務省のデータベースにはM5Toughの登録（211-210316）がありますが、ToughC5は別の無線構成です。
images:
- url: https://cdn.shopify.com/s/files/1/0056/7689/2250/files/K162_M5Stack_ToughC5_IoT_Dev_Kit_ESP32-C5_1.webp?v=1791514760
  caption: 屋外で水がかかる状態のToughC5。画面に温湿度の表示が出ている
- url: https://cdn.shopify.com/s/files/1/0056/7689/2250/files/K162_M5Stack_ToughC5_IoT_Dev_Kit_ESP32-C5_5.webp?v=1791514760
  caption: 本体と付属品。拡張基板、防水用Oリング、六角レンチ、配線が付く
credit: M5Stack 公式ストア
alternatives:
- name: M5Stack Tough ESP32 IoT開発キット（旧モデル）
  why: 同じ防水筐体の旧モデルで、国内の楽天市場で売られている。技適は総務省のデータベースにM5Toughとして登録がある。2.4GHzのWi-Fiで足りる用途なら今日から試せる。
  url: https://item.rakuten.co.jp/marutsuelec/2229251/
  merchant: rakuten
  image: https://thumbnail.image.rakuten.co.jp/@0_mall/marutsuelec/cabinet/04881820/230620/2229251_2.jpg
sources:
- title: M5Stack ToughC5 IoT Dev Kit (ESP32-C5)（公式ストア）
  url: https://shop.m5stack.com/products/m5stack-toughc5-iot-dev-kit-esp32-c5
  publisher: M5Stack（公式）
- title: M5Stack ToughC5 weatherproof ESP32-C5 IoT controller offers dual-band Wi-Fi 6, BLE 5, and Zigbee/Thread
  url: https://www.cnx-software.com/2026/10/10/m5stack-toughc5-weatherproof-esp32-c5-iot-controller-offers-dual-band-wi-fi-6-ble-5-and-zigbee-thread/
  publisher: CNX Software
---

M5Stackが、屋外で使うIoTコントローラー「ToughC5」を公式ストアに載せた。ESP32-C5を中核に、2.4GHzと5GHzのWi-Fi 6、BLE 5、IEEE 802.15.4（Zigbee、Thread）に対応する。価格は49.90ドルで、ストアの掲載時点では購入できる表示になっている。

## 仕様

公式ページの主な仕様は次のとおり。

| 項目 | 内容 |
| --- | --- |
| SoC | ESP32-C5HR8（RISC-V 32bit、最大240MHz） |
| メモリ | Flash 16MB、PSRAM 8MB |
| 無線 | 2.4/5GHzデュアルバンドWi-Fi 6、BLE 5、Zigbee/Thread |
| 画面 | 2.0インチ IPS 320×240、静電容量タッチ、最大輝度853nit |
| 入力電圧 | USB 5V、RS485側 6〜24V、バッテリー 3.7V |
| 拡張 | HY2.0-4P×4（RS485/I2C/GPIO/UART）、M12ケーブル穴×2、microSD |
| 大きさ・重さ | 75.9 × 58.0 × 42.5mm、119g |

筐体はPC+ABSにUV対策の粉を混ぜた素材で、屋外の紫外線劣化に耐えるとされている。防塵・防滴の仕様で、水没には対応しない（公式画像にも「浸水からの保護なし」と注記がある）。内蔵のRTC（RX8130CE）と、電源管理（M5PM1とM5IOE1）を備え、低消費電力のスリープ復帰ができる。

## 旧Toughとの違い

公式の比較表で、旧モデルの「Tough」と並べると差は次のようになる。

| 項目 | ToughC5 | Tough |
| --- | --- | --- |
| SoC | ESP32-C5（RISC-V、単コア） | ESP32（Xtensa、2コア） |
| 無線 | 2.4/5GHzのWi-Fi 6、Zigbee/Thread | 2.4GHzのWi-Fi |
| PSRAM | 8MB（Octal） | 8MB（Quad） |
| 音 | パッシブブザー | 1Wスピーカー |
| アンテナ | FPC（2.4/5GHz） | 3D |

画面サイズと解像度、フラッシュ容量は同じ。音を出す機能は後退している。

## 日本から見るとどうか

**ToughC5の国内取扱いは確認できていない。** 日本語でも検索したが、国内の発売告知は見つからなかった。旧モデルのM5Stack Toughは、楽天市場の販売店で国内向けに売られている。

**技適は未確認。** 総務省のデータベースで型番を引いたが、ToughC5の登録は見つからなかった。M5Toughには登録（211-210316）があるものの、ToughC5は無線構成が違う。Espressifの「ESP32-C5-WROOM-1」モジュールは登録されている（020-250079）が、ToughC5が積むのは「ESP32-C5HR8」というコアモジュールで、同じ認証が使えるかは確認できない。

**5GHz帯は屋外で注意が要る。** 日本では5GHz帯のうちW52・W53（5.2/5.3GHz）は屋内での使用に限られる。屋外向けの製品でも、5GHzで使えるのは屋外利用が認められる帯域に限られる。実際の設定は電波法の区分を確認したうえで行う必要がある。

**取れる行動。** 5GHzやZigbee/Threadが必要でなければ、国内で買える旧Toughで足りる。ToughC5が欲しい場合は、国内の取扱いが出るのを待つか、海外ストアから個人輸入する際に技適が無い前提で、有線と屋内の用途にとどめる。
