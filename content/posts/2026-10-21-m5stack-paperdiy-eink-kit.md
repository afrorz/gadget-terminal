---
title: M5Stack「PaperDIY」、4.7インチ電子ペーパー付きESP32-S3キットが25ドルから。電池は140mAh、タッチは無い
slug: m5stack-paperdiy-eink-kit
seo_title: M5Stack PaperDIYは25ドル、電子ペーパー開発キット
x_hook: |
  電池が140mAhしかない、4.7インチの画面。
  M5Stackの電子ペーパー開発キット「PaperDIY」。ESP32-S3を載せ、25ドルから。
  ・960×540、16階調のグレー
keyword: PaperDIY
category: pc
date: 2026-10-21
kicker: 中国・深圳のM5Stackが、4.7インチの電子ペーパーとESP32-S3を組み合わせた開発キット「PaperDIY」を公式ストアで売り出した。筐体なしの組み立てキットが25ドル、3Dプリント筐体付きの完成版が29.90ドルで、掲載時点では完成版が在庫切れになっている。
tags:
- M5Stack
- PaperDIY
- ESP32-S3
- 電子ペーパー
- 開発ボード
origin: SZX 深圳
giteki:
  status: 確認できない
  number: []
  checked: 2026-10-28
  radio: Wi-Fi 2.4GHz
  note: "PaperDIYの型式は総務省DBに無い。搭載モジュールの同系ESP32-S3-WROOM-1は登録があるが、基板としての扱いは言えない"
images:
- url: "https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1287/K159-PaperDIY-Assembly-Kit_main_pictures_01.webp"
  caption: 組み立てキットの中身。4.7インチの電子ペーパー、アクリルの押さえ板、140mAhの電池、ESP32-S3-WROOM-1を載せた基板。基板のmicroSDスロットとUSB Type-C、ボタン2つが読み取れる
- url: "https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1288/K159-B_PaperDIY_Complete_Kit_main_pictures_01.webp"
  caption: 完成版。白い3Dプリント（PLA）の筐体に収まり、画面にはピン配置とWi-Fiの検出結果が出ている。背面にはM2のネジ穴がある
- url: "https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1287/K159-PaperDIY-Assembly-Kit_main_pictures_03.webp"
  caption: 組み立てキットのパッケージ。段ボールの箱に電子ペーパーが載り、「3Dプリント筐体は含まれない」と印字されている
credit: M5Stack 公式製品ページ
sources:
- title: PaperDIY Assembly Kit（M5Stack公式ドキュメント。取得は2026年10月21日）
  url: https://docs.m5stack.com/en/products/sku/K159
  publisher: M5Stack（公式）
- title: PaperDIY Complete Kit（M5Stack公式ドキュメント）
  url: https://docs.m5stack.com/en/products/sku/K159-B
  publisher: M5Stack（公式）
- title: PaperDIY Assembly Kit (ESP32-S3)（M5Stack公式ストア。価格と在庫は2026年10月21日時点）
  url: https://shop.m5stack.com/products/paperdiy-assembly-kit-esp32-s3
  publisher: M5Stack（公式）
- title: "A modular smartphone with a de-Googled OS, a $25 E Ink Dev Kit, and a Cyberdeck that runs on power tool batteries: Liliputing News Roundup"
  url: https://liliputing.com/a-modular-smartphone-with-a-de-googled-os-a-25-e-ink-dev-kit-and-a-cyberdeck-that-runs-on-power-tool-batteries-liliputing-news-roundup/
  publisher: Liliputing
faq:
- q: PaperDIYはいくらですか
  a: M5Stackの公式ストアでは、筐体なしの組み立てキットが25ドル、3Dプリント筐体付きの完成版が29.90ドルです（2026年10月21日時点）。送料や関税は別です。
- q: 日本で買えますか
  a: 公式ストアでの購入が前提になります。国内の取扱店は、掲載時点で検索しても見つかりませんでした。国内ではスイッチサイエンスがM5Stack製品を扱っているので、入荷の有無は確かめる価値があります。
- q: 技適は取得していますか
  a: PaperDIYの型式は、総務省の技適データベースで見つかりませんでした。M5Stackの別製品（PaperMono、Paper Colorなど）には登録があります。PaperDIYを国内で電波を出して使うなら、登録の有無を先に確認してください。
- q: タッチ操作はできますか
  a: 公式の仕様欄にタッチパネルの記載はありません。入力は電源ボタンと2つのユーザーボタンです。
---

M5Stackが、4.7インチの電子ペーパーを載せたESP32-S3の開発キット「PaperDIY」を売り出した。2020年に出た同社の電子ペーパー端末M5Paperの流れをくむ後継という位置づけで、Liliputingは「25ドルの電子ペーパー開発キット」として紹介している。完成した端末ではなく、中身を自分で組んで使う基板とパネルのキットだ。

**価格は2種類。** 筐体なしの組み立てキット（K159）が25ドルで、3Dプリント筐体付きの完成版（K159-B）が29.90ドル。公式ストアの表示では、組み立てキットは購入でき、完成版は在庫切れになっている（2026年10月21日時点）。

## 何が入っているか

公式ドキュメントの仕様は次のとおり。

- 表示：4.7インチの電子ペーパー、960×540ピクセル、16階調のグレー
- マイコン：ESP32-S3-WROOM-1-N16R8（デュアルコア240MHz、フラッシュ16MB、PSRAM 8MB）
- 通信：2.4GHzのWi-Fi。Bluetoothは仕様欄に書かれていない
- 電池：3.7V・140mAhのリチウム電池
- 端子：USB Type-C、microSDスロット、0.5mmピッチ12ピンのFPC拡張が2つ、5Vパッド
- ボタン：電源ボタン1つとユーザーボタン2つ
- 大きさ：115.3×62.5×5.5mm、重さ26.4g（組み立てキット）

組み立てキットに含まれるのは、電子ペーパー、制御基板、電池、アクリルの押さえ板で、筐体は付かない。完成版は同じ中身にPLA製の3Dプリント筐体が最初から付き、筐体のデータは公開されているので、自分で刷り直したり形を変えたりできる。背面のM2ネジ穴に使うネジは、画面を押さないよう3mmより短いものを使う、と公式は注意している。

仕様欄には、タッチパネルやセンサーの記載が無い。M5Paperの発想で「タッチできる端末」を期待すると外れる。操作は3つのボタンで足りる用途、たとえば天気や予定を表示し続ける卓上の表示器や、電子ペーパーの試作に向く。電池が140mAhと小さいのは、電子ペーパーが表示を書き換えるときしか電力を使わないためで、常時点灯の画面を載せる端末とは設計の前提が違う。実際の電池持ちは公式に数字が無く、ここでは書けない。

## 日本で買える？使える？

買う手段は、M5Stackの公式ストア（shop.m5stack.com）が基本になる。国内の販売店では、掲載時点で検索しても見つからなかった。国内ではスイッチサイエンスがM5Stack製品を扱っており、4インチのカラー電子ペーパーを載せた「M5Paper Color」も同店で売られている。PaperDIYが入荷するかどうかは、同店の動き次第で、現時点では確認できていない。

**技適は確認できない。** 総務省の技適データベースに、PaperDIYの型式は載っていなかった（2026年10月21日に確認）。載っているのは別製品で、PaperMono（2026年8月）やPaper Color（2026年3月）がM5Stack名義で登録されている。搭載モジュールの同系ESP32-S3-WROOM-1もEspressif名義で登録があるが、基板ごとの扱いがどうなるかは、登録の有無から言い切れない。無線機能を日本で使うなら、技適の表示がある製品を選ぶのが確実だ。電波を出さず、ケーブルだけで画面を書き換える使い方なら、この問題は避けられる。

同じ「国内で買える電子ペーパー付きの開発ボード」を探したが、4.7インチのパネルまで付いた同種のキットは、楽天市場では見つからなかった。Seeed Studioの電子ペーパー用基板は国内の通販に出ているが、パネルが別売りで用途が少し違う。今すぐ試したいなら、国内の取扱店の入荷を待つか、25ドルに送料と関税を足して公式ストアから個人輸入するかの二択になる。
