#!/usr/bin/env python3
"""把一张实物照片压缩后转成可直接贴进报告的 <figure class="figure photo"> 片段。

报告是单文件交付，照片必须内嵌为 data URI；外链和相对路径换台机器就裂图。

用法：
    python3 scripts/embed_photo.py <图片路径> --caption "折弯机：把平板压出角度" \
        --source "XX 公司官网产品页" --url "https://..." [--width 1200] [--quality 78]

输出片段里的图号写成「图 N」，贴进报告后按全文出现顺序改成实际编号。
依赖 Pillow；没有就 pip install pillow。
"""
import argparse, base64, html, io, sys

try:
    from PIL import Image
except ImportError:
    sys.exit("需要 Pillow：pip install pillow")

MAX_KB = 300


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--caption", required=True, help="图注：这张图让读者看懂什么")
    ap.add_argument("--source", required=True, help="来源名称，如「XX 公司官网产品页」")
    ap.add_argument("--url", default="", help="来源网址")
    ap.add_argument("--width", type=int, default=1200)
    ap.add_argument("--quality", type=int, default=78)
    a = ap.parse_args()

    im = Image.open(a.image)
    if im.mode not in ("RGB", "L"):
        bg = Image.new("RGB", im.size, (255, 255, 255))
        im = im.convert("RGBA")
        bg.paste(im, mask=im.split()[-1])
        im = bg
    if im.width > a.width:
        im = im.resize((a.width, round(im.height * a.width / im.width)), Image.LANCZOS)

    q = a.quality
    while True:
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
        if buf.tell() <= MAX_KB * 1024 or q <= 50:
            break
        q -= 7
    b64 = base64.b64encode(buf.getvalue()).decode()

    src = html.escape(a.source)
    if a.url:
        src = f'<a href="{html.escape(a.url, quote=True)}">{src}</a>'
    cap = html.escape(a.caption)
    print(
        f'<figure class="figure photo">\n'
        f'  <div class="fig-frame"><img alt="{cap}" src="data:image/jpeg;base64,{b64}"></div>\n'
        f'  <figcaption><b>图 N</b>　{cap}<span class="src">图片来源：{src}</span></figcaption>\n'
        f'</figure>'
    )
    print(f"[embed_photo] {im.width}×{im.height}，{buf.tell() // 1024} KB，JPEG q={q}", file=sys.stderr)


if __name__ == "__main__":
    main()
