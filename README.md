# 量化研究项目

北大金融数学方向 → 头部量化研究员的 90 天启动工程。
配合 `量化研究员启动计划.xlsx`（21 天逐日任务）与 `量化研究员启动手册-Day1起.md` 使用。

**新人从这里看** → [项目索引与聊天记录整理.md](docs/项目索引与聊天记录整理.md)

## 目录

```
src/            所有代码（脚本、工具库、测试）
data/raw/       原始数据（csv）
data/clean/     清洗后数据（parquet）
reports/        研究报告与图表
docs/           学习笔记、术语表、环境快照
资料库/          公开授权教材、讲义、论文（约 76 MB）
归档/           一次性脚本与过期文件（可整个删掉）
```

> `notebooks/` 已归档。探索性分析如果要做 `.ipynb`，再新建这个目录。

## 快速开始

> **本机环境约定（重要）**：本机有多个 Python（含 Anaconda、Python 3.11、DSH 自带 3.12），
> 为避免"装了却 import 不到"，本项目固定使用虚拟环境 `.venv`，
> 所有命令都显式调用它的解释器，不依赖 PATH。
> 环境说明见 [Python环境说明与清理记录.md](docs/Python环境说明与清理记录.md)，
> VS Code 报错排查见 [VSCode运行代码-排错手册.md](docs/VSCode运行代码-排错手册.md)。

```powershell
cd /d "E:\AI结果\量化"

# 环境自检（Python 版本、依赖、matplotlib 出图、数据源）
.venv\Scripts\python.exe src\check_env.py

# Day 1：拉取沪深300 并落盘（CSV + parquet）
.venv\Scripts\python.exe src\my_d01_data.py

# Day 1：分析并出图（统计量 + 正态性检验 + 三张图）
.venv\Scripts\python.exe src\my_d01_analysis.py

# Day 1：单测（14 项，检查 5 个核心函数写对没）
$env:D01_MODULE="my_d01_analysis"
.venv\Scripts\python.exe -m pytest src\test_d01_analysis.py -v
Remove-Item Env:\D01_MODULE

# 阶段验收：一次性检查 D1–D7 的全部产物
.venv\Scripts\python.exe src\d07_acceptance.py

# 装新包（永远用 python -m pip）
.venv\Scripts\python.exe -m pip install 包名
```

**不想敲命令**：双击根目录的 `运行-抓数据.bat` / `运行-做分析.bat` / `运行-全部测试.bat`。
**VS Code 用户**：打开要跑的文件按 `F5`（配置见 `.vscode/launch.json`）。

换电脑或环境损坏时重建（自动挑选解释器、装依赖、验证）：

```powershell
python src\make_venv.py            # 建 .venv
python src\make_venv.py --find     # 只列出本机可用解释器
python src\make_venv.py --clean    # 删掉重建
```

依赖版本留档在 [docs/requirements-lock.txt](docs/requirements-lock.txt)（精确到小版本的复现依据）。

## 已完成产出

| 文件 | 内容 |
|---|---|
| `docs/env.md` | Python 版本、依赖版本、数据源与区间快照 |
| `docs/d01.md` | Day 1 学习笔记：概念、数字、卡点、三句话结论 |
| `data/raw/hs300.csv`、`data/clean/hs300.parquet` | 沪深300 日线，2002-01-07 ~ 2026-09-30，6003 行 |
| `reports/d01_mine.json` | 你的 Day 1 指标留档 |
| `reports/figs/d01_mine.png` | 收益分布 vs 正态、Q-Q 图、净值与历史高点 |
| `src/my_d01_data.py`、`src/my_d01_analysis.py` | 你自己写的 Day 1 脚本（14/14 测试通过） |

## 工作约定

1. 所有随机过程固定种子（`np.random.default_rng(42)`），同脚本两次运行结果必须一致。
2. 先落盘再分析，不在 notebook 里现拉数据。
3. 每个研究结论都要写清：假设、数据、检验方式、成本假设、局限。
4. 每天收工提交 Git，commit message 写清"做了什么 + 卡在哪"。
