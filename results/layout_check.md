# 编译、版面与内容核对

- `main_zh.pdf`：4 页；`main_en.pdf`：4 页。均为 Letter 纸型、IEEE Computer Society Transactions 双栏。
- 使用 Tectonic 0.17.0 的 XeTeX 路径编译，自动运行 BibTeX 并重编译。Overleaf 对应设置为 XeLaTeX。
- 最终两版逐页渲染核对；标题、摘要、正文、公式、算法行号、主表、两幅图及五条参考文献均可见，无裁切、重叠和越界。
- 最终日志无 overfull box、missing character 或未解析的正文引用与交叉引用。少量字体初始化回退、algorithm.sty 注释编码提示及 underfull 排版提示不影响页面可见内容。
- 西文字体显式使用 TeX Gyre Pagella / Heros，等宽字体使用 Latin Modern Mono；中文为 Fandol。
- 两版使用同一个 `.bib` 和同一组图片；主表由同一结果生成不同语言标签；计时数值共用生成的宏文件。
- 核对关键结果：名义 20% 预算下 86.86% / 25.30% / 87.06%；实际句数率 22.47%，滑动窗口词数率 25.25%，Top-k 词数率 28.25%。
- 百分点差异从未四舍五入的原始值计算：30% 和 50% 预算分别为 1.28 与 2.08 个百分点。
- 数据审计、算法核对与逐条结果随项目交付。上游原始数据通过下载器单独获取；编译论文不依赖下载数据。
- 中文 CID 字体的结构化文字提取依赖阅读器的 Adobe GB1 映射支持；源文件保留完整 Unicode 中文。
