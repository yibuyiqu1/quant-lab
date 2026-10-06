# Day 2 · B线：pandas 数据结构与选择

> 时长 1.5h + 复盘 0.5h｜对应 `量化研究员启动计划.xlsx` 的「1-21天启动营」第 2 天
> 素材：[../src/day2_practice.py](../src/day2_practice.py)（练习）、[../src/day2_answers.py](../src/day2_answers.py)（答案）、[../src/test_day2.py](../src/test_day2.py)（测试）

---

## 一、今日目标

**一句话**：把 pandas 从"能看懂"变成"能熟练操作时间序列"，并掌握因子研究的核心操作 `groupby + transform`。

**为什么今天学这个**：Day 1 你已经算出了收益和指标，但那是在**一条**序列上。
真实量化研究面对的是**面板数据**（多只股票 × 多个日期），必须用分组操作。
今天学的 `groupby + transform` 就是"每个交易日做一次横截面标准化"，这是所有因子研究的第一个动作。

---

## 二、执行步骤（照顺序做，约 90 分钟）

| 步骤 | 做什么 | 时间 |
|---|---|---|
| 1 | 打开 [../src/day2_practice.py](../src/day2_practice.py)，读一遍函数签名和注释，**先不写** | 10 min |
| 2 | 按顺序实现第 0–5 题（每题写完先单独 print 验证） | 50 min |
| 3 | 跑 `python src/day2_practice.py`，对照注释里的"预期" | 10 min |
| 4 | 跑测试 `pytest src/test_day2.py -v`，红了先看测试名再改 | 10 min |
| 5 | 卡住的题看 [../src/day2_answers.py](../src/day2_answers.py)，**看懂后关掉重写一遍** | 10 min |

**最后一步（重要）**：`day2_answers.py` 里有个函数 `demo_agg_vs_transform()`，跑它一次。
它用 3 行数据把 `agg` 与 `transform` 的区别打印出来，看一眼就懂。

---

## 三、今日知识点清单（对应 6 道练习）

| 题 | 知识点 | 关键函数 | 为什么重要 |
|---|---|---|---|
| 0 | 读数据与日期索引 | `read_parquet` / `to_datetime` / `sort_values` / `set_index` | 索引不对，后面全错 |
| 1 | 派生列（向量化） | `shift` / `diff` / `rolling().mean()` / `rolling().std()` | 因子与指标都是这么造出来的 |
| 2 | 布尔筛选 | `(z.abs() > k).sum()` | 数极端值个数/占比 |
| 3 | 时间分组与重采样 | `groupby(index.year)` / `resample("ME")` | 分年、分月的稳健性检验 |
| 4 | **横截面标准化** | **`groupby().transform()`** / `rank(pct=True)` | **因子研究第一动作** |
| 5 | 分组聚合 | `groupby().agg([...])` | 统计各组的分布特征 |

---

## 四、必须记住的三条

### 1. `transform` vs `agg`（今天最重要）

```
agg       -> 每组压缩成一个值，结果长度 = 组数
transform -> 每组返回等长序列，结果长度 = 原表

横截面标准化必须用 transform（因为要把标准化后的值填回每一行）
```

**用 3 行数据看最清楚**：

```
原始：            agg 结果：          transform 结果：
D1  1.0           date  mean  std     date  factor      z
D1  2.0           D1     2.0  1.0     D1     1.0   -1.2247
D1  3.0           D2    20.0 10.0     D1     2.0    0.0000
D2 10.0                               D1     3.0    1.2247
D2 20.0                               D2    10.0   -1.2247
D2 30.0                               ...
```

### 2. `ddof` 决定校验时看到的数字

标准化公式 $z=(x-\mu)/\sigma$ 里的 $\sigma$ 是**总体**标准差，对应 `std(ddof=0)`。
如果你用 pandas 默认的 `.std()`（即 `ddof=1`），然后去校验"z 的标准差是不是 1"，
会得到 $\sqrt{3/2}\approx1.2247$ 而不是 1 —— **不是代码错了，是校验用了不同的 ddof**。

### 3. `reset_index(drop=True)` 会丢掉日期索引

题 3 需要 `r.index.year`，所以必须**先把 date 设为索引**。
这就是答案脚本 `main()` 里踩到的坑——它一开始报 `'Index' object has no attribute 'year'`。

---

## 五、预期输出（用来自查）

```
[0] 行数 6003，区间 2002-01-04 ~ 2026-09-30

[1] 派生列（最后 3 行）:
      date    close       ret   log_ret     amp       ma20    vol20
2026-09-28 4340.755 -0.022164 -0.022413 100.247 4520.46430 0.008395
2026-09-29 4345.209  0.001026  0.001026  34.773 4506.47045 0.008315
2026-09-30 4357.616  0.002855  0.002851  26.735 4493.77930 0.008420

[2] |z|>3 的天数: 107   |z|>5: 15
    占全部 6002 天的比例: 1.7827%（正态理论 0.27%）

[3] 按年年化波动（最后 3 年）:
2024    0.2089
2025    0.1514
2026    0.1865

[3] 最近 3 个月收益率:
2026-07-31   -0.0786
2026-08-31    0.0080
2026-09-30   -0.0578

[4] 每日横截面 z 的统计（应 mean≈0、std=1）:
            mean  std(ddof=0)
2026-09-30   0.0          1.0

[5] 每只股票的 factor 统计（前 3 行）:
       mean    std
S00  -0.008  1.003
S01   0.084  1.007
S02   0.219  1.000
```

**对照要点**：
- `|z|>3` 应为 **107 天**（这个数字 Day 1 已经验证过，能对上说明你的标准化写对了）
- 每日 z 的 `std(ddof=0)` 必须**正好等于 1**
- `code_stats` 的 mean 应随股票编号递增（造数据时第 i 只均值设为 `i*0.1`）

---

## 六、六道练习（自己做，答案在 src/day2_answers.py）

### 练习 0：读数据
`load_index()` → 返回以日期为索引的 close 序列（升序）。
**要点**：四步顺序不能变——读文件 → 转日期 → 排序 → 设索引。

### 练习 1：派生 5 列
`add_features(df)` → 新增 `ret / log_ret / amp / ma20 / vol20`，且**不改动传入的 df**。
**要点**：第一行 `df.copy()`；全部向量化，不许写 for。

### 练习 2：数极端值
`count_extreme(r, k)` → 返回 |标准化收益| > k 的**天数**。
**要点**：取绝对值（暴涨也算极端）；返回 `int` 不是 numpy 类型。

### 练习 3：时间分组（两个函数）
`yearly_vol(r)` → 按年算**年化**波动，索引是年份。
`monthly_return(close)` → 按月算收益率。

**两个坑**：
- 分年要用 `groupby(index.year)`，**不能** `resample("YE").std()`（那样每组只剩 1 个点）
- 得到日标准差后要乘 $\sqrt{244}$ 才是年化

### 练习 4：横截面标准化（重点）
`cs_zscore(panel)` → 每个交易日内做 z-score，新增列 `z`。
`rank_pct(panel)` → 每个交易日内算百分位排名。

**要点**：`groupby("date")["factor"].transform(lambda s: (s - s.mean()) / s.std(ddof=0))`

### 练习 5：分组聚合
`code_stats(panel)` → 按 code 分组，返回 mean 与 std 两列。

---

## 七、验收标准（3 条全过）

```powershell
cd /d "E:\AI结果\量化"

# 1) 脚本能跑，数字与第五节一致
.venv\Scripts\python.exe src\day2_practice.py

# 2) 测试全绿（14 项）
.venv\Scripts\python.exe -m pytest src\test_day2.py -v

# 3) 能口头回答下面 3 个问题
```

**三个自查问题**：
1. `df["ret"].shift(1)` 在干什么？→ 把昨天的收益对齐到今天（用于构造"用昨天信息预测今天"）
2. 为什么横截面标准化必须用 `transform` 而不能用 `agg`？→ 要填回每一行，长度必须相等
3. 分年算波动为什么不能直接 `resample("YE").std()`？→ 每年只剩 1 个点，标准差是 NaN

---

## 八、常见报错对照

| 报错 | 原因 | 解决 |
|---|---|---|
| `AttributeError: 'Index' object has no attribute 'year'` | 索引不是日期（被 `reset_index` 丢了） | 先 `set_index("date")` |
| `TypeError: 'set' object is not subscriptable` | 字典写成 `{键, 值}`（Day 1 踩过） | 用冒号 `{键: 值}` |
| `pandas.errors.InvalidIndexError` 或结果长度不对 | 用了 `agg` 却想回填 | 改用 `transform` |
| `KeyError: 'factor'` | 先选了列又选一次 | `groupby("code")["factor"]` 之后直接 `.agg(...)` |
| 标准化后 std = 1.2247 | 校验用了 `ddof=1` | 校验时写 `std(ddof=0)` |
| `FutureWarning: 'M' is deprecated` | 旧版重采样代码 | 用 `"ME"`（month end） |
| `SettingWithCopyWarning` | 对切片直接赋值 | 先 `.copy()` |

---

## 九、今日交付物

| 交付 | 位置 |
|---|---|
| 自己的练习实现 | `src/day2_practice.py` |
| 测试通过截图/输出 | 终端（14 passed） |
| 学习笔记 | `docs/d02.md`（**自己写**，照 `docs/d01.md` 的格式） |
| Git 提交 | `git commit -m "d02: pandas 数据结构与横截面标准化"` |

**写 `docs/d02.md` 时至少回答**：
1. `transform` 和 `agg` 的区别，各举一个使用场景
2. 为什么分年波动要 `groupby(index.year)` 而不是 `resample`
3. 横截面标准化在因子研究里解决什么问题（提示：不同股票的量纲/量级不同）
4. 今天卡住的点，以及怎么解决的
