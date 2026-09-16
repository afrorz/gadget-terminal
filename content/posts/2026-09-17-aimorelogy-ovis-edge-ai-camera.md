---
title: "AIMORELOGYの1.5TOPS AIカメラ「Ovis」がKickstarter始動、HK$460から低照度でもフルカラー撮影"
seo_title: AIMORELOGY Ovisは59ドルから、AI夜間カメラ
slug: aimorelogy-ovis-edge-ai-camera
keyword: AIMORELOGY Ovis
category: pc
date: 2026-09-17
origin: HKG 香港
deadline: "2026-11-09"
kicker: エッジAI開発の香港企業AIMORELOGYが、CVITEK製SoCを積んだオープンソースのAIカメラモジュール「Ovis」をKickstarterで公開した。低照度でもフルカラーの映像を1080p/30fpsで出力するAI-ISPと、1.5TOPSのオンボード推論を1枚に詰め込んでいる。
tags:
  - AIMORELOGY
  - Ovis
  - Kickstarter
  - エッジAI
  - カメラモジュール
x_hook: 暗所でもモノクロにならない防犯カメラ用チップを、20×20mmの基板に載せた。Kickstarterの目標はHK$30,000だが、掲載時点の支援はHK$4,928(16%)、支援者はまだ8人にとどまる。
faq:
  - q: 日本で買えますか
    a: 掲載時点でKickstarterでの支援受付のみです。日本への発送可否はキャンペーンページに明記がなく確認できていません。
  - q: 技適は必要ですか
    a: Standard Kit・CVBS Kitとも無線モジュールを搭載せず、USB・Ethernet・UARTの有線インターフェースのみで動作するため、この構成では技適の対象になりません。ただしプロジェクトオプションとしてWi-Fi拡張が案内されており、それを追加する場合は別途、技適の確認が必要です。
  - q: いくらですか
    a: Standard KitがHK$460(約59ドル、掲載時点の支援額)、CVBS出力基板を追加するCVBS Kitが約69ドルです。
  - q: いつ届きますか
    a: 2026年12月の発送を予定しています。クラウドファンディングのため、遅延や仕様変更が起きる可能性があります。
images:
  - url: "https://i.kickstarter.com/assets/055/025/853/cf9fc4460384d0ff7d1157486a17a041_original.png?fit=scale-down&origin=ugc&q=100&v=1788751444&width=680&sig=rQQWT8dAzHYQuhbDEqCZ1ocjoJKDhcW7RHTNTTzg0wM%3D"
    caption: Ovis本体(中央)と、人物・車両検知、ドローン視点でのFPVトラッキング、街頭での追跡、Webブラウザ上の設定画面(OVIS Web)といった活用イメージ
  - url: "https://i.kickstarter.com/assets/055/026/205/d12594f6b33fcb3321a5296301d843ea_original.jpg?fit=scale-down&origin=ugc&q=92&v=1788754964&width=680&sig=8ZB0dl%2FALmlQjftS8aYGELd0APIzXffuAWc8Lhj7bjY%3D"
    caption: Core基板・センサー基板・CVBS出力基板を分離したモジュール構成。プロジェクトに応じてWi-Fi・IMU・カスタムI/Oを組み合わせられる
  - url: "https://i.kickstarter.com/assets/055/025/863/90dd8c27e1d3d9ccfddf7cad20940bcd_original.jpg?fit=scale-down&origin=ugc&q=92&v=1788751561&width=680&sig=Gfw%2BuKcVUR%2FMjUtRojnnH3zhXezFJ%2FhHmj51HtE5INM%3D"
    caption: 低照度画質の比較。左がOvisのAI-BNR処理、右が従来型ISP。同じ暗さのシーンでも色と輪郭の残り方が異なる
credit: AIMORELOGY Kickstarterキャンペーンページ
sources:
  - title: "CVITEK CV1842H-P-based edge AI camera module offers night vision and AI-ISP support (Crowdfunding)"
    url: https://www.cnx-software.com/2026/09/16/cvitek-cv1842h-p-based-edge-ai-camera-module-offers-night-vision-and-ai-isp-support/
    publisher: CNX Software
  - title: "Ovis: Open-Source 1.5TOPS Edge AI Camera Module"
    url: https://www.kickstarter.com/projects/aimorelogy/ovis-open-source-15tops-edge-ai-camera-module
    publisher: Kickstarter
alternatives:
  - name: Raspberry Pi 公式 AI カメラ(IMX500搭載)
    why: 同じくセンサー上でAI推論を行うカメラモジュールで、国内Amazonから技適を気にせず今日から入手できる。Ovisのような低照度カラー補正(AI-ISP)機能は無いが、エッジAIカメラの入り口として使える。
    url: https://www.amazon.co.jp/RaspberryPi-AI-12MP%E3%80%81IMX500-%E3%82%BB%E3%83%B3%E3%82%B5%E3%83%BC%E3%80%81IMX500-78-3%C2%B0FOV%E3%80%81Pi5/dp/B0DSBTHNKT
    merchant: amazon
---

香港のエッジAI企業AIMORELOGYが、CVITEK(SOPHGO系列)製SoC「CV1842H-P」を搭載したAIカメラモジュール「Ovis」をKickstarterで公開した。Arm Cortex-A53とRISC-V C906のデュアルコアに1.5TOPSのNPUを組み合わせ、暗所でもモノクロにならずフルカラーのまま1080p/30fpsで映像を出力する「AI-ISP」処理をカメラ単体で完結させるのが売りだ。掲載時点の支援額はHK$4,928で、目標のHK$30,000に対し16.4%、支援者は8人にとどまる。募集は2026年11月9日まで。

## スペック

| 項目 | 内容 |
| --- | --- |
| SoC | CVITEK CV1842H-P |
| CPU | Arm Cortex-A53 @1.1GHz + RISC-V C906 @800MHz |
| NPU | 1.5TOPS(INT8、BF16対応) |
| AI-ISP | 1080p/30fpsのリアルタイム低照度カラー補正(AI-BNR) |
| 動画エンコード | H.265/H.264/MJPEG、最大8MP@25fps |
| メモリ/ストレージ | 256MB DDR3(SiP内蔵)/256MB SPI NAND |
| インターフェース | USB 2.0(UVC/NCM)、Ethernet 10/100Mbps、UART |
| 寸法 | Ovis Core基板 20×20×5.7mm、レンズ付きStandard Kit 28×28×31.7mm |
| ソフトウェア | Cortex-A53側Linux 5.10、RISC-V側RT-Thread、ブラウザ設定ツール「OVIS Web」 |
| 価格(支援額) | Standard Kit HK$460(約59ドル)、CVBS Kit 約69ドル |
| 発送予定 | 2026年12月(計画通りに進んだ場合) |

Core基板・センサー基板・オプションのCVBS出力基板をボード間コネクタで積み重ねるモジュール構造で、開発者が独自のキャリアボードを設計してWi-Fi・IMU・カスタムI/Oを追加できる余地も残す。AIMORELOGYはハードウェア設計図と回路図、構造データ、ソースコードの公開を予定しており、SDK自体は既にGitHubで公開済み。人物・車両検知や顔検知、姿勢推定、単一物体追跡といったAI機能を備え、YOLOv8nの動作手順も文書化されている。用途はドローン、ロボティクス、防犯・監視、組み込みカメラ製品と幅広いが、キャンペーンページには軍事・武力行使目的での使用を明確に禁じる条項がある。

## 日本から見るとどうか

**無線を積まなければ技適は関係ない。** Standard KitとCVBS KitはいずれもUSB・Ethernet・UARTの有線接続のみで、電波を発する部品を持たない。個人輸入して有線のまま使う分には、日本の電波法・技適の対象にはならない。ただし、プロジェクトオプションとして案内されているWi-Fi拡張を追加する場合は話が別で、技適未取得のモジュールを組み込んで国内で電波を発すれば電波法違反になる。この点は自分で構成を選ぶ段階できちんと確認する必要がある。

**CVITEK(SOPHGO)系のSoCは、日本のSBC愛好家にも土地勘がある。** 同社のチップはMilk-V DuoやDuo 256Mといった小型ボードにも使われており、国内でも一定のユーザーが触ったことがあるはずだ。ただしCV1842H-Pのパッケージ・ピン配置はCV1812H系と共通する一方、Milk-V Duo/Duo 256Mが使うCV1800B・SG2002とは異なるため、Duo用に設計した基板にそのまま載せ替えることはできない。SDKやソフトウェア資産の流用はできても、基板の互換性は無いと考えたほうがいい。

**日本の代理店はなく、クラウドファンディングという性質上、届く保証もない。** HK$4,928・支援者8人という掲載時点の数字が示す通り、このプロジェクトはまだ目標に遠く、成立するかどうか自体が確定していない。届いても発送は2026年12月予定で前後しうる。今すぐ同種のAIカメラを試したいなら、国内で正規に買えてサポートも受けやすいRaspberry Pi公式AIカメラのような選択肢から始めるほうが現実的だ。
