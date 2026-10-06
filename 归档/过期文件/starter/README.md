# Quant Starter · 第一个因子项目骨架

> 目标：**跑通一次完整的单因子研究流程**，而不是追求因子有效。
> 第一版跑出来「没用」是正常且有价值的 —— 交付物是一份说清楚为什么没用的研究笔记。

## 目录结构

```
starter/
├── requirements.txt          # 第一周只需装前 6 个包
├── README.md
├── src/
│   ├── 01_fetch_data.py      # 拉 A 股前复权日线 → data/daily.parquet
│   └── 02_first_factor.py    # 20 日动量：IC 分析 + 5 分组 + 净值图
├── data/                     # 运行后生成（已 gitignore 建议）
└── figs/                     # 运行后生成：ic_series.png / group_nav.png
```

## 快速开始

```bash
# 1) 建环境
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2) 拉数据（约 1 分钟）
python src/01_fetch_data.py

# 3) 跑第一个因子
python src/02_first_factor.py
```

输出：终端打印 IC 均值 / ICIR / t 统计量 / 分组收益，图片落在 `figs/`。

## 代码里已经处理好的四个坑（读代码时重点理解）

| 坑 | 处理方式 |
|---|---|
| 未来函数 | 未来收益用 `open[t+1]` 买入、`close[t+5]` 卖出，不用当日收盘价成交 |
| 极值主导排序 | 按交易日截面做 3σ winsorize + z-score |
| 忘记交易成本 | 调仓一次扣 30bp（双边千三，含佣金+印花税+冲击） |
| 随机切分验证集 | 本脚本只做全样本描述；做样本外时**必须按时间切分**并留 embargo |

## 下一步扩展清单（按顺序做）

1. **扩股票池**：30 只 → 沪深300 / 中证500（用 `ak.index_stock_cons("000300")` 取成分股）
2. **剔除样本**：ST、上市不足 60 日、当日停牌、一字涨停无法成交
3. **加因子**：价值（BP/EP）、波动率、换手率 → 建 4 因子表
4. **做中性化**：行业 + 市值中性（对因子值做截面回归取残差）
5. **稳健性检验**：换参数（10/20/60 日）、换股票池、换时间段，看结论是否还成立
6. **样本外切分**：按时间切 train/test，中间留 embargo（≥ 持有期）
7. **产物化**：把结果整理成 8–12 页 PDF 研究笔记，这就是你第一份能写进简历的作品

## 关于样本量的诚实说明

30 只蓝筹的 IC 与分组结果**没有统计意义**，只用于验证代码链路正确。
真正的结论必须建立在 ≥300 只股票 × ≥5 年 的样本上。
