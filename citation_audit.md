# 文献与数据来源核验

核验日期：2026-10-31，Asia/Shanghai。中英文版本共用同一个 `.bib`，均引用以下五项文献。

| 引用键 | 官方或作者来源 | 核验与正文用途 |
|---|---|---|
| `lin2025speechprune` | [IEEE 正式记录](https://ieeexplore.ieee.org/document/11209113)、[开放全文 v2](https://arxiv.org/html/2412.12009v2)、[作者项目页](https://speechprune.github.io/) | 已核对题名、作者、ICME 2025、DOI 10.1109/ICME59968.2025.11209113；全文第 III-B 节支持两阶段筛选描述，第 II 节支持 SPIRAL 数据来源。IEEE 直接打开时存在验证页，检索索引与作者项目页均可交叉核对发表信息。 |
| `chu2024qwen` | [arXiv 官方记录](https://arxiv.org/abs/2407.10759) | 核对题名、十二位作者、2024 年和 DOI 10.48550/arXiv.2407.10759；支持音频与文本指令联合分析背景，不引用其性能数字。 |
| `luo2026locality` | [arXiv 官方记录](https://arxiv.org/abs/2605.25179) 及[全文](https://arxiv.org/html/2605.25179v1) | 核对题名、三位作者、2026 年与 DOI 10.48550/arXiv.2605.25179；说明局部时间结构已有研究，效果依赖任务；明确为预印本。 |
| `radford2023whisper` | [PMLR 正式论文页](https://proceedings.mlr.press/v202/radford23a.html) | 核对题名、六位作者、ICML 2023、PMLR 202、28492–28518 页；作为语音识别背景。原文最初于 2022 年预印，本稿引用 2023 正式版本。所查正式页未给出 DOI，保留正式 URL。 |
| `manning2008ir` | [Cambridge DOI 落地页](https://doi.org/10.1017/CBO9780511809071)、[出版社前言与目录](https://assets.cambridge.org/97805218/65715/frontmatter/9780521865715_frontmatter.pdf)、[作者书籍网站](https://www-nlp.stanford.edu/IR-book/) | 核对三位作者、2008 年、出版社、ISBN 9780521865715、DOI；第 6 章为 TF-IDF 与向量空间背景。本稿明确写出所用平滑与归一化约定，算法证明独立给出。 |

## 数据快照

- 来源：[SPIRAL 作者仓库](https://github.com/linyueqian/SPIRAL_Dataset)。
- 文件：[data.jsonl](https://raw.githubusercontent.com/linyueqian/SPIRAL_Dataset/master/data.jsonl)。
- 文件大小：3,965,780 字节。
- SHA-256：`485225b9ef52c98298ceb06745c7acf022dcc7c6436c610a17dbd11e8022519f`。
- 实际解析 1,012 条记录、1,012 个唯一 ID。
- 数据来自原论文的生成与语音合成流程；本实验使用发布者转写，没有把它称为自然采集录音或 ASR 输出。
- 正文的检索率、分组结果与计时来自本次运行，不是从原论文性能表转抄。

## 核验范围

全部文献身份和正文所需论述均找到官方元数据、作者页面或开放全文支持；没有编造题名、卷期或 DOI。本文未执行付费相似度检查、全库撤稿监测或所有文献的全文逐句审计。正文使用概述，未长段转引来源文本。

IEEEtran 类与样式沿用已从 [CTAN](https://ctan.org/pkg/ieeetran?lang=en) 获取的未修改版本，源文件中保留许可证。当前确认的是样式基础和可编译性，不作期刊录用或正式投稿合规判断。
