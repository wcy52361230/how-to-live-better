#!/usr/bin/env python3
"""生成 PWA 图标（Android 添加到主屏幕用）。

产出：
  icons/icon-192.png            192×192  普通图标（自带圆角）
  icons/icon-512.png            512×512  普通图标（自带圆角）
  icons/icon-512-maskable.png   512×512  可遮罩图标（满底无圆角，图形收进安全区）

设计：深底 + 打开的书 + 绿色认证徽章。全部按比例绘制，
以 4× 超采样后 LANCZOS 缩小，保证小尺寸边缘干净。

用法：python3 scripts/make_icons.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "icons"

BG = (27, 27, 31, 255)          # 页面暗色主题底色 #1b1b1f
PAGE = (244, 244, 245, 255)     # 书页
LINE = (27, 27, 31, 62)         # 页内文字线（半透明深色）
BADGE = (74, 222, 128, 255)     # 认证徽章 #4ade80
CHECK = (16, 40, 26, 255)       # 对勾（深色，压在绿底上对比更强）

SS = 4  # 超采样倍数


def render(size: int, maskable: bool) -> Image.Image:
    """按尺寸绘制图标，返回 RGBA 图。"""
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 背景：普通图标带圆角，maskable 满底
    if maskable:
        d.rectangle([0, 0, s, s], fill=BG)
    else:
        d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.22), fill=BG)

    # maskable 时把内容缩到中心安全区，保证圆形裁切不切到图形
    # 安全区为直径 80% 的圆；本设计内容对角半径约 0.42，故取 0.95 刚好贴住
    k = 0.95 if maskable else 1.0

    def px(v: float) -> float:
        """把 0~1 的比例坐标换算成实际像素（含安全区缩放）。"""
        return s * (0.5 + (v - 0.5) * k)

    def box(x0, y0, x1, y1):
        return [px(x0), px(y0), px(x1), px(y1)]

    rpag = int(s * 0.035 * k)

    # 左右两页
    d.rounded_rectangle(box(0.155, 0.255, 0.484, 0.745), radius=rpag, fill=PAGE)
    d.rounded_rectangle(box(0.516, 0.255, 0.845, 0.745), radius=rpag, fill=PAGE)

    # 页内文字线：每页 3 行，长度递减更自然
    line_w = int(s * 0.018 * k)
    widths = [0.245, 0.245, 0.165]
    for i, w in enumerate(widths):
        y = 0.375 + i * 0.095
        d.rounded_rectangle(
            [px(0.195), px(y), px(0.195 + w * 0.0 + w), px(y) + line_w],
            radius=line_w // 2, fill=LINE,
        )
        # 右页对称，第三行让左右错开一点
        w2 = widths[i] if i < 2 else 0.245
        d.rounded_rectangle(
            [px(0.805 - w2), px(y), px(0.805), px(y) + line_w],
            radius=line_w // 2, fill=LINE,
        )

    # 右下角认证徽章
    cx, cy, r = px(0.755), px(0.752), s * 0.155 * k
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BADGE)
    # 徽章描一圈背景色，和书页分开
    d.ellipse([cx - r, cy - r, cx + r, cy + r],
              outline=BG, width=int(s * 0.012 * k))

    # 对勾
    cw = max(2, int(s * 0.048 * k))
    pts = [
        (cx - r * 0.44, cy + r * 0.02),
        (cx - r * 0.10, cy + r * 0.36),
        (cx + r * 0.48, cy - r * 0.34),
    ]
    d.line(pts, fill=CHECK, width=cw, joint="curve")
    for p in pts:
        d.ellipse([p[0] - cw / 2, p[1] - cw / 2, p[0] + cw / 2, p[1] + cw / 2],
                  fill=CHECK)

    return img.resize((size, size), Image.LANCZOS)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(192, False), (512, False), (512, True)]
    for size, maskable in jobs:
        name = "icon-%d%s.png" % (size, "-maskable" if maskable else "")
        path = OUT / name
        render(size, maskable).save(path, "PNG", optimize=True)
        print("写入 %s (%d 字节)" % (path.relative_to(OUT.parent),
                                  path.stat().st_size))


if __name__ == "__main__":
    main()
