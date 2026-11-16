# 高性价比人生指南 · 在线阅读页

一个单文件 HTML 阅读页，把开源书《高性价比人生指南》的全部 32 节、528 条建议
渲染成可搜索的页面。手机上打开就能看，不用装任何东西。

**在线阅读：** https://cdyforever.github.io/how-to-live-better/

## 装到手机（安卓，离线可用）

1. 手机 Chrome 打开上面的链接
2. 点右上角 ⋮ → 「安装应用」（旧版浏览器显示「添加到主屏幕」）
3. 桌面出现图标。之后**断网也能打开**，搜索、只看 A 级、切节全部照常

原理：`manifest.json` + `sw.js`（Service Worker）。打开页面时走**网络优先**——联网就拿当天最新内容，4 秒超时或断网则用本地缓存；正文和图标都缓存在手机上，所以离线不白屏。

> 注意：PWA 相关标签写在 `build.py` 里，不在 `index.html` 里。
> `index.html` 每天由 Actions 重新生成，直接手改会被覆盖。

## 这是什么

原书由 [eternity4719/HowToLiveBetter](https://github.com/eternity4719/HowToLiveBetter)
维护（Unlicense，公有领域），按「性价比」排序，每条写清花掉什么、换回什么、证据多硬，
只引期刊论文和官方文件。

本仓库不是原书的 fork，也不改动原书内容。它只做一件事：把原书正文渲染成一个
**自包含的单文件网页**，方便在手机和别人的电脑上直接打开。

## 页面特性

- **零外部资源**：没有 CDN、没有字体外链、不 fetch 任何数据，断网也能读
- 逐条卡片：建议标题、证据等级（A/B/C）、性价比档、成本标签
- **「说人话」高亮块**——原书里这一栏专门把统计量翻成日常说法，页面上做得最显眼
- 全站关键词搜索（结果高亮）、只看 A 级、只看说人话
- 左侧目录带性价比色点，滚动联动
- 手机端：搜索框独占一行、顶栏向下滚动后自动收成一行、回到顶部按钮
- 明暗主题切换
- 支持直接打印
- 可安装到手机主屏幕，断网可用（PWA）

## 本地使用

不用构建，双击 `index.html` 即可。

`file://` 协议下浏览器不允许注册 Service Worker，所以本地双击打开时没有离线缓存层——
但页面本身零外部依赖，照样能读。

## 文件清单

| 文件 | 作用 |
| --- | --- |
| `build.py` | 生成器，唯一需要维护的源码（含 PWA 标签注入） |
| `index.html` | 产物，每天由 Actions 重建，不要手改 |
| `manifest.json` | PWA 清单：名称、图标、standalone 显示 |
| `sw.js` | Service Worker：导航网络优先、静态资源缓存优先 |
| `icons/` | 主屏幕图标（192 / 512 / 512-maskable） |
| `scripts/make_icons.py` | 生成图标，改配色或图形后重跑即可 |

图标重新生成：`python3 scripts/make_icons.py`（需要 Pillow）。

## 重新生成

```bash
# 需要先有一份上游仓库的本地克隆
git clone --depth 1 https://github.com/eternity4719/HowToLiveBetter.git /tmp/upstream

# 全部节
python build.py all -o index.html --repo /tmp/upstream

# 只做某几节
python build.py 1 2 16 --repo /tmp/upstream
```

源目录也可以用环境变量 `HLTB_REPO` 指定。

统计口径（条目数、A/B/C 分级、性价比三档）与上游的 `tools/sync-stats.ps1`
和 `index.html` 保持一致，生成结果可与上游徽章逐项对照。

## 自动更新

`.github/workflows/rebuild.yml` 每天 06:00（北京时间）拉取上游重新生成，
内容有变化才提交。也可以去 Actions 页面手动触发。

## 授权

原书内容为 Unlicense（公有领域）。本仓库的构建脚本同样不作任何权利保留。
