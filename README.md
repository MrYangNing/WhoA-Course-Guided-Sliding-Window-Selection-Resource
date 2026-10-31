# 转写引导的滑动窗口片段选择：实验代码与结果

本仓库提供实验部分：数据获取、句子打分、窗口选择、结果核对与计时。

## 实验流程

1. `fetch_data.py` 下载公开 SPIRAL 标注并校验 SHA-256。
2. `experiment.py` 在每条记录的参考转写上计算 TF-IDF 句子相关分数。
3. 在固定句数预算下比较四种片段选择方法：
   - 开头裁剪（first）
   - 随机连续窗口（random，枚举全部合法起点取精确期望）
   - 分数 Top-k（topk）
   - 滑动窗口（sliding，最早出现的最大和连续窗口）
4. 输出逐条结果、汇总、标注核对、正确性检查与计时。

关键句标注、选项和答案只在评价阶段读取，不参与 TF-IDF 构建或窗口选择。

## 数据

- 来源：[SPIRAL 作者仓库](https://github.com/linyueqian/SPIRAL_Dataset)
- 文件：`data/spiral_data.jsonl`，3,965,780 字节
- SHA-256：`485225b9ef52c98298ceb06745c7acf022dcc7c6436c610a17dbd11e8022519f`
- 规模：1,012 条记录（350 讲座、324 会议、338 日常对话）
- 仓库内已包含该快照；`fetch_data.py` 用于重新下载并核对同一版本，上游变化时会报错停止。
- 数据中的 `.jsonl` 以 `-text` 保存，检出后字节不变，SHA-256 可直接复核。

## 复现

```text
python -m pip install -r requirements.txt
python experiment.py
```

环境与结果记录一致：Python 3.13.15、numpy 2.5.3、matplotlib 3.11.2。

若需重新获取数据：

```text
python fetch_data.py
```

运行 `experiment.py` 会覆盖 `results/` 和 `figures/` 下的文件。计时受机器负载影响，数字会变化。

最简单的算法例子（无外部依赖）：

```text
python beginner_demo.py
```

输入六个分数、保留三项，输出最佳起始位置 3、窗口 `[8, 9, 7]`、总和 24。

## 主要结果

名义 20% 句数预算下的完整关键跨度命中率（全部 1,012 条）：

| 方法 | 命中率 |
|---|---|
| 开头裁剪 | 11.07% |
| 随机连续窗口 | 25.30% |
| 分数 Top-k | 87.06% |
| 滑动窗口 | 86.86% |

其他 Setting：

- 10%：滑动窗口 80.04%，Top-k 80.34%
- 30%：滑动窗口 91.01%，Top-k 89.72%
- 50%：滑动窗口 96.44%，Top-k 94.37%
- 实际保留句数率（名义 20%）：22.47%；滑动窗口保留词数率 25.25%，Top-k 为 28.25%。

指标定义：完整关键跨度命中指选中集合覆盖全部关键句；它不是问答准确率，句数预算也不是秒数预算。

## 文件

| 文件 | 用途 |
|---|---|
| `experiment.py` | 打分、四种选择方法、核对、计时与绘图 |
| `fetch_data.py` | 下载公开标注并核对 SHA-256 |
| `beginner_demo.py` | 无依赖的滑动窗口小例子 |
| `requirements.txt` | numpy 与 matplotlib 版本 |
| `data/spiral_data.jsonl` | SPIRAL 数据快照 |
| `figures/` | 实验生成的 PDF 和 PNG 图 |
| `results/raw.csv` | 16,192 行逐记录、逐预算、逐方法结果 |
| `results/summary.csv` | 整体及场景分组汇总 |
| `results/annotation_audit.csv` | 全部标注的区间与文本关系核对 |
| `results/verification.json` | 数据快照、正确性检查及环境信息 |
| `results/timing.csv` | 独立窗口搜索计时 |
| `results/run_output.txt` | 一次完整运行的输出记录 |

## 范围说明

本实验使用发布者提供的转写，不运行 ASR、音频大模型或语音问答。
关键跨度命中率衡量证据保留，不代表端到端问答性能，也未与 SpeechPrune 的音频模型结果作同类比较。
