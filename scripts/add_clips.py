"""記事に、メーカー公式 YouTube 動画の短い切り出し(動く映像)を足す(2026-11-04 本人了承)。

毎朝の動画づくり(shorts\\gadget-shorts の朝のタスク)が切った3秒・音なしの映像を、記事用に小さく作り直して
content/clips/<slug>/ に置き、記事の front matter に clips を書く。表示は build.py の inline_clip。

「画像をダウンロードして自社サーバーに置かない」の唯一の例外。置いてよいのは:
  - メーカー自身の公式チャンネルの動画から、1カット3秒まで・音なし・1記事3カットまで
  - 出典(チャンネル名と元の動画の URL)を必ず書く
ほかの人の動画・画像は今までどおり置かない。

使い方: python scripts/add_clips.py <記事の slug> [--shorts <gadget-shorts の slug>]
  gadget-shorts の videos\\<slug>\\wide.json で photo が .mp4 の場面を拾う(文字はその場面の見出し)。
  もう clips がある記事は何もしない(やり直すときは front matter の clips を消してから)。
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "content" / "posts"
CLIPS = ROOT / "content" / "clips"
SHORTS = Path(r"D:\MyDocument\ClaudeApp\shorts\gadget-shorts")
MAX_CLIPS = 3


def ffmpeg() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:  # GT の Python に無ければ、動画づくりの仮想環境の物を使う
        found = sorted((SHORTS / ".venv" / "Lib" / "site-packages" / "imageio_ffmpeg" / "binaries").glob("ffmpeg*.exe"))
        if not found:
            sys.exit("ffmpeg が見つかりません(pip install imageio-ffmpeg)")
        return str(found[0])


def q(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)  # YAML のダブルクォート文字列として使える


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--shorts", help="gadget-shorts 側の slug(記事と同じなら省略)")
    a = ap.parse_args()
    post = next(POSTS.glob(f"*-{a.slug}.md"), None)
    if not post:
        sys.exit(f"記事がありません: {a.slug}")
    text = post.read_text(encoding="utf-8")
    fm_end = text.index("\n---", 3)
    fm = text[:fm_end]
    if re.search(r"^clips:", fm, re.M):
        print(f"もう映像があります: {post.name}")
        return
    sslug = a.shorts or a.slug
    w = json.loads((SHORTS / "videos" / sslug / "wide.json").read_text(encoding="utf-8"))
    credit_m = re.search(r"映像：([^／/]+)", w.get("imageCredit") or "")
    credit = credit_m.group(1).strip() if credit_m else "メーカー公式 YouTube"
    picks = []
    for s in w.get("slides") or []:
        photo = str(s.get("photo") or "")
        if not photo.lower().endswith(".mp4") or photo in [p[0] for p in picks]:
            continue
        name = Path(photo).name
        src_note = str((w.get("images") or {}).get(name) or "")
        url = src_note.split()[0] if src_note.startswith("http") else ""
        if "youtube.com" not in url and "youtu.be" not in url:
            print(f"飛ばす(元の動画の URL が書かれていない): {name}")
            continue
        texts = s.get("texts") or []
        caption = str(texts[0]).replace("\n", "") if texts else ""
        if len(texts) > 1:
            caption += f"（{texts[1]}）"
        picks.append((photo, name, url, caption))
    picks = picks[:MAX_CLIPS]
    if not picks:
        print(f"映像の場面がありません: videos\\{sslug}\\wide.json")
        return

    out_dir = CLIPS / a.slug
    out_dir.mkdir(parents=True, exist_ok=True)
    ff = ffmpeg()
    lines = ["clips:"]
    for photo, name, url, caption in picks:
        src = SHORTS / "public" / "videos" / sslug / photo
        dst = out_dir / name
        # 記事の幅には 960px で足りる。1カット 100〜200KB(写真1枚と同じくらい)
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(src), "-an", "-vf", "scale=960:-2",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "30", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", str(dst)], check=True)
        # 読み込む前に出す止めた絵(1コマ目)。枠の大きさが先に決まり、ページがずれない
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(dst), "-frames:v", "1", "-q:v", "5",
                        str(dst.with_suffix(".jpg"))], check=True)
        print(f"置きました: {dst.relative_to(ROOT)}({dst.stat().st_size // 1024}KB)")
        lines += [f"- file: {a.slug}/{name}", f"  caption: {q(caption)}", f"  credit: {q(credit)}",
                  f"  source: {q(url)}"]
    # clips は sources の前に置く(videos_after は末尾に置く決まりなので、そこを避ける)
    m = re.search(r"^sources:", fm, re.M)
    at = m.start() if m else fm_end + 1
    text = text[:at] + "\n".join(lines) + "\n" + text[at:]
    post.write_text(text, encoding="utf-8")
    print(f"記事に {len(picks)} カット足しました: {post.name}")


if __name__ == "__main__":
    main()
