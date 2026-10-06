# Python 包速查表（量化方向）

> 用法：先看"这个包是干嘛的"，再看"Day 1 实际用到哪几个函数"。
> **安装铁律**：永远用 `python -m pip`，并用项目 `.venv` 里的解释器：
> ```powershell
> cd /d "E:\AI结果\量化"
> .venv\Scripts\python.exe -m pip install 包名
> ```

---

## 一、Day 1 用到的 6 个包（按文件里的出现顺序）

### 1. `os` — 操作系统接口｜Python 自带，无需安装

**干嘛的**：拼路径、建目录、遍历文件。量化项目里所有"文件在哪"的问题都靠它。

**Day 1 用到的 2 个函数**：

| 写法 | 作用 | 例子 |
|---|---|---|
| `os.path.dirname(os.path.abspath(__file__))` | 算出文件所在目录（连用两次得到项目根目录） | 得到 `E:\AI结果\量化` |
| `os.path.join(ROOT, "data", "raw", "hs300.csv")` | **跨平台**拼路径（Windows 用 `\`，Linux 用 `/`，它自动处理） | `E:\AI结果\量化\data\raw\hs300.csv` |
| `os.makedirs(目录, exist_ok=True)` | 建目录，多层一起建；已存在也不报错 | 建出 `data/raw` |

**新手最常犯的错**：把路径写成 `"data\raw\hs300.csv"`——这是**相对路径**，取决于你在哪个目录敲命令，换个目录就找不到文件。一律用 `ROOT` 拼绝对路径。

---

### 2. `sys` — 解释器设置｜Python 自带

**干嘛的**：控制解释器行为。Day 1 只用一个功能：把输出编码改成 UTF-8。

| 写法 | 作用 |
|---|---|
| `sys.stdout.reconfigure(encoding="utf-8")` | 让 `print` 的中文在 PowerShell 里不乱码（Windows 默认 GBK，中文会变"锟斤拷"） |
| `sys.executable` | 当前运行的 Python 路径（排查"装了却没有"时第一句就查它） |

---

### 3. `pandas` — 表格与时间序列｜**量化最核心的包**

**干嘛的**：处理带行列标签的二维表。所有行情数据、因子、回测结果都是 pandas 对象。

**两个核心数据结构**：

- `Series`：一列数据（比如一列收盘价），带索引
- `DataFrame`：一张表（多列），带行索引和列名

**Day 1 用到的函数（每个都对应代码里的一行）**：

| 写法 | 作用 | 备注 |
|---|---|---|
| `pd.read_parquet(路径)` | 读 parquet 文件 | 比 `read_csv` 快 5-10 倍且保留类型 |
| `df.to_csv(路径, index=False, encoding="utf-8-sig")` | 存 CSV | `index=False` 否则多一列无名行号；`utf-8-sig` 让 Excel 打开中文不乱码 |
| `df.to_parquet(路径, index=False)` | 存 parquet | 需要 pyarrow |
| `pd.to_datetime(df["date"])` | 文本 → 日期类型 | **必须转**，否则无法按月汇总、无法正确比较大小 |
| `df.sort_values("date")` | 按某列排序 | |
| `df.reset_index(drop=True)` | 重排行号 0,1,2… | 不加 `drop=True` 会把旧行号变成新列 |
| `df.set_index("date")` | 把某列设为索引 | 之后 `r.index` 就是日期，画图方便 |
| `df.shape` | 形状 `(行数, 列数)` | 拿到新数据第一件事 |
| `df.dtypes` | 每列的数据类型 | 第二件事，看日期有没有被读成文本 |
| `df.head(3)` / `df.tail(3)` | 前 / 后 3 行 | 第三件事，肉眼确认数据对不对 |
| `df.isna().sum()` | 每列缺失值个数 | 数据体检必查 |
| `df["date"].duplicated().sum()` | 重复值个数 | 数据体检必查 |
| `df[col].astype(float)` | 强制转成浮点 | 防止整数除法或字符串运算报错 |
| `np.log(s).diff()` | 对数收益 | 先 log 再差分 |
| `(1 + r).cumprod()` | 净值曲线 | 累积连乘 |
| `nav.cummax()` | 累积最大值（历史高点） | 算回撤用 |
| `r.dropna()` | 丢掉缺失值 | 差分/滚动的第一行必是 NaN |
| `r.fillna(0)` | 缺失填 0 | 净值计算里"缺失=没涨没跌" |
| `r.std(ddof=1)` | 样本标准差 | 金融默认 `ddof=1`（除 n−1） |
| `r.mean()` / `r.min()` / `r.max()` | 均值 / 最小 / 最大 | |
| `r.skew()` | 偏度（正态为 0） | 负值 = 左偏，暴跌比暴涨极端 |
| `r.kurt()` | **超额**峰度（正态为 0） | `+3` 才是通常说的峰度（正态为 3） |
| `(r > 0).mean()` | 布尔求均值 = 占比 | 求"上涨天数占比"这类比例的标准技巧 |
| `df.iloc[-1]` | 按**位置**取（−1 = 最后一个） | 与按**标签**取的 `.loc` 相对 |
| `s.rolling(20).mean()` | 20 期滚动均值（均线） | 前 19 行是 NaN |
| `s.shift(1)` | 向上平移一行（昨天的值） | 时序对齐的核心 |
| `s.pct_change()` | 简单收益率 | 与对数收益的区别见下 |

**对数收益 vs 简单收益（一定要分清）**：

```python
r_log = np.log(close).diff()        # 对数收益：多期可加，统计建模用这个
r_sim = close.pct_change()          # 简单收益：组合加权聚合用这个
```

数值例子（100 → 110）：对数收益 0.0953，简单收益 0.10。

---

### 4. `numpy` — 数值计算｜科学计算的底座

**干嘛的**：数组运算、随机数、数学函数。pandas 处理"表格"，numpy 处理"数字"。

**Day 1 用到的**：

| 写法 | 作用 |
|---|---|
| `np.log(s)` | 逐元素取自然对数 |
| `np.linspace(0, 1, 400)` | 生成 400 个等间距点（画平滑曲线的横轴） |
| `np.exp(x)` | 逐元素指数 |
| `np.sort(x)` | 排序（画 Q-Q 图要排序） |
| `x.abs()` | 取绝对值 |
| `np.array_equal(a, b)` | 判断两个数组是否完全相等（自检可复现性） |
| `np.random.default_rng(42)` | **新版**随机数生成器（旧写法 `np.random.seed` 已不推荐） |
| `rng.normal(均值, 标准差, 个数)` | 生成正态随机样本 |
| `rng.uniform(0, 1, 个数)` | 生成均匀分布样本 |
| `rng.standard_t(自由度, 个数)` | 生成 t 分布样本（做肥尾对照） |

**为什么要固定种子**：`np.random.default_rng(42)` 里那个 42 是种子。同一个种子每次生成的随机数完全一样 → 结果可复现。不固定的话，每次跑结果都不同，你的研究结论就无法被验证。

---

### 5. `akshare` — 中国金融数据接口｜需要联网

**干嘛的**：免费抓 A 股行情、指数、财务、宏观数据，**不需要注册**。

| 写法 | 取什么数据 |
|---|---|
| `ak.stock_zh_index_daily(symbol="sh000300")` | 指数日线（沪深300） |
| `ak.stock_zh_a_hist(symbol="000001", period="daily", adjust="hfq")` | 个股日线（平安银行，后复权） |
| `ak.stock_zh_a_spot_em()` | 全市场实时快照 |
| `ak.index_stock_cons(symbol="000300")` | 指数成分股名单 |

**指数代码规则**：前缀 `sh`（上交所）/ `sz`（深交所）+ 6 位代码。
`sh000001` 上证指数｜`sh000300` 沪深300｜`sh000905` 中证500｜`sz399006` 创业板指

**返回列固定为**：`date / open / high / low / close / volume`
**注意**：`date` 是**文本**类型，必须 `pd.to_datetime` 转换。

---

### 6. `matplotlib` — 画图｜报告的门面

**干嘛的**：画折线图、直方图、热力图。量化报告的结论 80% 靠图传达。

**Day 1 用到的**：

| 写法 | 作用 |
|---|---|
| `matplotlib.use("Agg")` | 设成"只存文件不弹窗"（必须在 `import pyplot` **之前**） |
| `plt.subplots(1, 3, figsize=(16,4), dpi=130)` | 1 行 3 列的子图画布 |
| `ax.hist(数据, bins=120, density=True, alpha=0.75)` | 直方图；`density` 画成概率密度，`alpha` 透明度 |
| `ax.plot(x, y, "r-", lw=1.6, label="净值")` | 折线图；`"r-"` 红色实线 |
| `ax.set_yscale("log")` | 纵轴取对数（看尾部必须有） |
| `ax.set_title() / set_xticks() / set_ylabel()` | 标题 / 刻度 / 轴标签 |
| `ax.legend(fontsize=8)` | 显示图例 |
| `fig.tight_layout()` | 自动调间距，防止标题被裁 |
| `fig.savefig(路径, dpi=130)` | 存图片 |
| `plt.close(fig)` | 释放内存（不关会越画越慢） |
| `plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]` | 设中文字体，否则中文变方框 |

---

## 二、后面 90 天会用到的包（现在不用装，用到再装）

| 包 | 一句话作用 | 大概什么时候用 |
|---|---|---|
| `pyarrow` | parquet 读写引擎（pandas 存 parquet 的依赖） | **Day 1 就需要，已装** |
| `scipy` | 统计检验、优化、插值（`stats.norm`、`stats.jarque_bera`） | D5 描述统计、D10 回归 |
| `statsmodels` | 计量经济学（OLS、ADF 平稳性检验、GARCH） | D11 回归诊断、D12 时间序列 |
| `scikit-learn` | 机器学习（回归、树模型、交叉验证） | D13 岭回归、D14 交叉验证 |
| `baostock` | A 股数据（含复权因子，比 akshare 更适合回测） | D3 数据质量、D16 回测 |
| `pytest` | 单元测试框架（自动验收你的代码） | D7 开始每天用 |
| `jupyterlab` | 交互式笔记本（边写边看中间结果） | 探索性分析时 |
| `seaborn` | 基于 matplotlib 的统计图（更好看、更省代码） | D6 可视化进阶 |
| `polars` | 超快数据框（比 pandas 快，语法不同） | 处理亿级 tick 数据时 |
| `numba` | 把 Python 函数编译成机器码（提速几十倍） | 回测循环优化时 |
| `torch` | 深度学习框架 | D43 之后的 ML 阶段 |
| `tushare` | 另一套金融数据接口（需要积分） | akshare 不够用时 |

---

## 三、包管理命令速查

```powershell
# 用项目虚拟环境（推荐，本项目固定用法）
cd /d "E:\AI结果\量化"
.venv\Scripts\python.exe -m pip install 包名          # 装
.venv\Scripts\python.exe -m pip install -r requirements.txt   # 按清单批量装
.venv\Scripts\python.exe -m pip list                  # 看装了哪些
.venv\Scripts\python.exe -m pip show 包名              # 看某个包的版本与位置
.venv\Scripts\python.exe -m pip freeze > docs\requirements-lock.txt  # 导出精确版本

# 检查某个包能不能 import（最可靠的"装没装"判断）
.venv\Scripts\python.exe -c "import importlib.util as u; print(bool(u.find_spec('pyarrow')))"
```

**装包出错时的排查顺序**：

1. 是不是网络问题 → 换国内镜像：
   `.venv\Scripts\python.exe -m pip install 包名 -i https://pypi.tuna.tsinghua.edu.cn/simple`
2. 是不是装到了别的 Python → `python -m pip -V` 看目标路径
3. 是不是版本冲突 → 报错里会有 `incompatible` 字样，按提示装指定版本：
   `.venv\Scripts\python.exe -m pip install "包名==1.2.3"`

---

## 四、Day 1 完整命令序列（从零到出图）

```powershell
cd /d "E:\AI结果\量化"

# 1) 环境自检（确认 10 个包齐全、matplotlib 能出图、数据源可用）
.venv\Scripts\python.exe src\check_env.py

# 2) 抓数据（教学版，逐行注释）
.venv\Scripts\python.exe src\d01_data_lesson.py

# 3) 统计分析 + 出图 + 打印三句话结论
.venv\Scripts\python.exe src\d01_analysis_lesson.py

# 4) 自己重写 4 个核心函数后，用测试验收
.venv\Scripts\python.exe -m pytest src\test_d01_analysis.py -v
```

**产物检查清单**：

- [ ] `data/raw/hs300.csv`（Excel 能打开，6003 行）
- [ ] `data/clean/hs300.parquet`（分析用）
- [ ] `reports/figs/d01_lesson.png`（三张图，中文正常）
- [ ] `reports/d01_lesson.json`（指标留档）
- [ ] 控制台最后一行出现 `可复现性自检: 通过`
