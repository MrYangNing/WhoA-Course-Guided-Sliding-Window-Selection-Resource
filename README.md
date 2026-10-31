# 转写引导的滑动窗口片段选择 / Transcript-Guided Sliding-Window Selection

本项目包含同一篇课程论文的完整中文和英文版本，使用同一组算法、实验、图表及参考文献。两版均已编译为四页 IEEE Computer Society Transactions 双栏格式。

## Overleaf 使用

1. 将 `speech_window_paper_overleaf.zip` 上传为新项目。
2. 中文版主文件选择 `main_zh.tex`；英文版主文件选择 `main_en.tex`。
3. 编译器选择 **XeLaTeX**，点击 Recompile。引用由 Overleaf 自动调用 BibTeX 生成。
4. 替换作者姓名；按课程要求补充学号、单位和班级。

两份 PDF 是已编译的阅读版本。IEEEtran 类、参考文献样式和图表均已包含，编译论文无需运行实验、下载数据或安装 Python。版式沿用上一版所选的 IEEE/TPAMI 相关双栏基础；当前内容是课程论文，不代表正式投稿或期刊录用评估。

## 内容与实验范围

研究流程为：参考转写 → TF-IDF 句子相关分数 → 固定句数滑动窗口 → 关键跨度命中率。

- 使用全部 1,012 条公开 SPIRAL 标注：350 条讲座、324 条会议、338 条日常对话。
- 比较开头裁剪、随机连续窗口、分数 Top-k 与滑动窗口。
- 预算为句子数，名义比例为 10%、20%、30%、50%，实际使用向上取整。
- 名义 20% 预算下，滑动窗口完整关键跨度命中率 86.86%，随机窗口 25.30%，Top-k 87.06%。
- 本实验使用发布者提供的转写，不运行 ASR、音频大模型或语音问答。关键跨度命中率不是问答准确率，句数预算不是秒数预算。
- 全部数字由脚本执行产生。原文 SpeechPrune 的模型性能没有写作本项目实验结果。

## 文件

| 文件 | 用途 |
|---|---|
| `main_zh.tex` / `main_en.tex` | 独立中英文论文主文件 |
| `main_zh.pdf` / `main_en.pdf` | 四页阅读版本 |
| `references.bib` | 五项已核验文献 |
| `IEEEtran.cls` / `IEEEtran.bst` | 未修改的 IEEE 官方样式，保留源许可证信息 |
| `figures/` | 论文图表的 PDF 和 PNG |
| `experiment.py` | 数据处理、打分、四种选择方法、核对、计时及绘图 |
| `fetch_data.py` | 下载公开标注并核对 SHA-256 |
| `beginner_demo.py` | 独立可运行的滑动窗口小例子，无外部依赖 |
| `初学者阅读说明.md` | 从简单例子理解论文与实验 |
| `citation_audit.md` | 文献核验来源及边界 |
| `research_record.md` | 研究配置与证据记录 |
| `results/raw.csv` | 16,192 行逐记录、逐预算、逐方法结果 |
| `results/summary.csv` | 整体及场景分组汇总 |
| `results/annotation_audit.csv` | 全部标注的区间与文本关系核对 |
| `results/verification.json` | 数据快照、正确性检查及环境信息 |
| `results/timing.csv` | 独立窗口搜索计时 |

## 运行最简单的例子

```text
python beginner_demo.py
```

输入六个分数、保留三项，输出最佳开始位置 3（从 1 开始计数）、窗口 `[8, 9, 7]`、总分 24。

## 重建实验

```text
python -m pip install -r requirements.txt
python fetch_data.py
python experiment.py
```

数据来源：[SPIRAL 官方仓库](https://github.com/linyueqian/SPIRAL_Dataset)。压缩包提供下载器和结果，不重复打包上游原始标注。下载器核对论文所用快照的 SHA-256，若上游内容变化会停止并报告，避免无提示地改变实验数据。

脚本使用问题文本打分。选项、正确答案、原始关键句和关键位置不参与 TF-IDF 构建或窗口选择，仅在独立的评价阶段读取标签。随机窗口通过枚举所有合法开始位置计算精确期望，不需要反复随机抽样。所有结果按全量数据报告，未筛选有利样本。

重新运行会覆盖实验结果和图表。计时因机器负载而变化，论文通过 `results/timing_values.tex` 自动读取计时数字；重新编译后，中英文计时保持一致。

## 提交前

先阅读初学者说明，再核对算法、预算单位及指标含义。填写作者信息，并按课程要求复核和呈现辅助工具使用说明。若课程要求端到端语音模型实验，需要补充音频模型推理与对应问答结果；当前稿已清楚界定为转写检索实验。
