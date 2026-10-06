# -*- coding: utf-8 -*-
r"""Day 1 教学版 · 统计分析（每一行都有注释，零基础可读）

开头那个 r 不要删：r + 三引号 是「原始字符串」，里面的反斜杠不当作转义符。
不加 r，下面的 Windows 路径会让 Python 3.12 报警：
    SyntaxWarning: invalid escape sequence '\A'

这个文件做四件事：
    1. 读本地数据 → 算日对数收益
    2. 算四个核心指标：年化收益、年化波动、最大回撤、尾部概率
    3. 画三张图（分布对比、Q-Q、净值与回撤）
    4. 打印三句话结论

运行：
    cd /d "E:\AI结果\量化"
    .venv\Scripts\python.exe src\d01_analysis_lesson.py

前置：先跑过一次 d01_data_lesson.py（否则读不到本地数据）
"""
# =============================================================================
# 【第 0 部分】导入包
# -----------------------------------------------------------------------------
# 标准库（Python 自带，无需安装）：os / sys / math / json
# 第三方库（需要 pip 安装）：numpy / pandas
# 画图库：matplotlib（我们只用它存图片，不弹窗）
# =============================================================================
import json                    # json：把结果存成 .json 文件（机器可读，便于对比两次运行）
import math                    # math：数学函数，这里用 sqrt(开方) 和 erf(误差函数)
import os                      # os：拼路径
import sys                     # sys：设输出编码

import numpy as np             # numpy：数值计算（对数、随机数、数组运算）
import pandas as pd            # pandas：表格与时间序列

# 同样把中文输出改成 UTF-8，避免 PowerShell 里显示乱码
sys.stdout.reconfigure(encoding="utf-8")


# =============================================================================
# 【第 1 部分】全局常量
# -----------------------------------------------------------------------------
# 常量用全大写命名，是"约定俗成的规范"，读到就知道不该改。
#
# SEED = 42
#   随机种子。凡是涉及随机数（比如生成模拟数据）都固定它，
#   这样同一个脚本跑两次结果完全一致 —— 这叫"可复现"，是量化研究的基本要求。
#   换成别的数字也行，但一旦固定就不要再改，否则历史结论对不上。
#
# ANNUAL = 244
#   A 股一年约 244 个交易日（美股用 252）。
#   年化波动 = 日波动 × √244 就用到它。
#   为什么是开方？因为波动（标准差）随时间按 √t 增长，不是按 t 线性增长。
# =============================================================================
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "clean", "hs300.parquet")
SEED = 42
ANNUAL = 244


# =============================================================================
# 【第 2 部分】四个核心函数（Day 1 真正要掌握的东西）
# =============================================================================

# -----------------------------------------------------------------------------
# 函数 1：对数收益
# -----------------------------------------------------------------------------
def log_returns(close: pd.Series) -> pd.Series:
    """输入收盘价序列，返回日对数收益序列。

    参数:
        close: 收盘价，pd.Series，索引是日期
    返回:
        对数收益，第一个值是 NaN（因为第一天没有"前一天"可比）

    公式: r_t = ln(P_t / P_{t-1}) = ln(P_t) - ln(P_{t-1})
    等价写法: np.log(close).diff()   ← 先取对数，再做一阶差分
    """
    # close.astype(float)
    #   把价格强转成浮点型。如果原始列是整数或字符串，不转会算出错或精度丢失。
    #
    # np.log(...)
    #   逐元素取自然对数。返回新的 Series，不改动原数据。
    #
    # .diff()
    #   一阶差分：每个位置减去上一位置的值。
    #   与 np.log 组合起来正好等于 ln(P_t / P_{t-1})。
    #   第一个位置没有"上一位置"，所以是 NaN（缺失值）。
    #
    # 为什么研究里用对数收益而不是 pct_change()（简单收益）？
    #   1) 多期可加：3 天的对数收益 = 3 天各自对数收益之和；
    #      简单收益必须连乘 (1+r1)(1+r2)(1+r3)-1，统计上难处理。
    #   2) 分布更接近对称，回归和统计推断的前提更容易满足。
    #   注意：组合层面的收益聚合（加权）仍要用简单收益，两者各有用途。
    return np.log(close.astype(float)).diff()


# -----------------------------------------------------------------------------
# 函数 2：年化收益与年化波动
# -----------------------------------------------------------------------------
def annualized_stats(r: pd.Series, freq: int = ANNUAL) -> dict:
    """输入日收益序列，返回 {"年化收益": 小数, "年化波动": 小数}。

    freq 默认 244（A 股交易日数），需要时可在调用处传 252。
    """
    # .dropna()
    #   丢掉缺失值。对数收益的第一个值是 NaN，不丢的话后面求和/连乘全会变 NaN。
    #   注意：这一步有副作用意识 —— 丢完之后样本少一天，年化时用的是新长度。
    r = r.dropna()

    # (1 + r).cumprod()
    #   先给每天收益加 1，得到"每日增长倍数"（涨 1% → 1.01），
    #   再 cumprod() 累积连乘，得到净值曲线（起点 1.0）。
    #   例：0.01, 0.02 → 1.01, 1.01×1.02 = 1.0302
    nav = (1 + r).cumprod()

    # len(r) / freq
    #   样本天数 ÷ 每年交易日数 = 样本跨越多少年（可以是小数，如 2.3 年）。
    #   后面算"几何年化"要用它当年数。
    years = len(r) / freq

    # nav.iloc[-1] ** (1 / years) - 1
    #   nav.iloc[-1]         取净值序列的最后一个值（iloc 按位置取，-1 表示倒数第一）
    #   ** (1 / years)       开"年数"次方，把总收益折算成每年的复合增长率
    #   - 1                  变回收益率形式
    #   这是"几何年化收益"，比"总收益/年数"的算术平均更准确。
    ann_ret = nav.iloc[-1] ** (1 / years) - 1

    # r.std(ddof=1)
    #   样本标准差。ddof=1 是"样本标准差"（除以 n-1），金融里默认用这个；
    #   ddof=0 是"总体标准差"（除以 n）。两者在小样本时差别明显。
    # math.sqrt(ANNUAL)
    #   年化因子 √244 ≈ 15.62。因为波动按 √时间 增长，
    #   所以日波动 × √244 = 年化波动。
    ann_vol = r.std(ddof=1) * math.sqrt(freq)

    # float(...) 把 numpy 的数值类型转成 Python 原生 float，
    # 这样后面 json.dump 才能序列化（numpy 类型不能直接存 JSON）。
    return {"年化收益": float(ann_ret), "年化波动": float(ann_vol)}


# -----------------------------------------------------------------------------
# 函数 3：最大回撤
# -----------------------------------------------------------------------------
def max_drawdown(r: pd.Series) -> float:
    """输入日收益，返回最大回撤（一个负数，例如 -0.7523 表示 -75.23%）。

    定义: 回撤_t = 净值_t / 历史最高净值_t - 1
          最大回撤 = 回撤序列里的最小值（最惨的那一刻）
    量化里它往往比夏普更重要：它回答"最坏情况下你要忍受多少亏损"。
    """
    # r.fillna(0)
    #   把缺失值当 0 收益处理。对净值曲线来说，缺失=没涨没跌，是合理假设。
    r = r.fillna(0)

    # 先算净值曲线，和函数 2 里一样
    nav = (1 + r).cumprod()

    # nav.cummax()
    #   累积最大值：每个位置记录"到目前为止见过的最高净值"。
    #   例：1.0, 1.5, 0.75 → cummax = 1.0, 1.5, 1.5
    #
    # nav / nav.cummax() - 1
    #   当前净值相对历史高点的跌幅，恒 ≤ 0。
    #   再 .min() 取最惨的一次，就是最大回撤。
    #
    # 关键理解：回撤的基准是"历史最高点"，不是"买入价"。
    #   所以 1 → 1.5 → 0.75 的回撤是 0.75/1.5 - 1 = -50%（不是 -25%）。
    dd = nav / nav.cummax() - 1
    return float(dd.min())


# -----------------------------------------------------------------------------
# 函数 4：尾部概率（判断"肥尾"）
# -----------------------------------------------------------------------------
def normal_cdf(x: float) -> float:
    """标准正态分布的累积分布函数 Φ(x) = P(Z ≤ x)。

    用 math.erf（误差函数）实现，不依赖 scipy：
        Φ(x) = 0.5 × (1 + erf(x / √2))
    自己实现一遍能彻底搞懂"正态假设"是怎么算出来的。
    """
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def tail_ratio(r: pd.Series, k: float = 3.0) -> dict:
    """比较"实际发生极端行情的频率"与"正态假设预测的频率"。

    参数:
        r: 日收益序列
        k: 阈值倍数，默认 3（即 3 倍标准差）
    返回:
        {"实际": 实际占比, "正态理论": 正态预测占比, "倍数": 实际/理论}
    """
    r = r.dropna()

    # (r - r.mean()) / r.std(ddof=1)
    #   标准化（z-score）：把收益变成"距离均值几个标准差"。
    #   这样不同量纲的数据可以公平比较，也是后续做因子的标准操作。
    z = (r - r.mean()) / r.std(ddof=1)

    # z.abs() 取绝对值（因为暴涨和暴跌都算极端）
    # .mean() 对布尔序列求均值 = 求 True 的比例 = 概率的经验估计
    actual = float((z.abs() > k).mean())

    # 正态分布下 P(|Z| > k) = 2 × (1 - Φ(k))，因为两侧对称
    # k=3 时约 0.0027（0.27%）
    theo = float(2 * (1 - normal_cdf(k)))

    # 倍数：实际是理论的几倍。远大于 1 就说明"肥尾"。
    # 加 if theo else nan 是防止除零（理论上 theo 不会为 0，但防御性写法是好习惯）。
    return {"实际": actual, "正态理论": theo, "倍数": actual / theo if theo else float("nan")}


# =============================================================================
# 【第 3 部分】读数据 + 画图
# =============================================================================

def load_close() -> pd.Series:
    """读取本地 parquet，返回以日期为索引的收盘价 Series。"""
    # pd.read_parquet(路径) 读 parquet 文件，比 read_csv 快且保留类型
    df = pd.read_parquet(DATA_PATH)

    # 保险起见再把 date 转成时间类型（parquet 里应该已经是了）
    df["date"] = pd.to_datetime(df["date"])

    # 链式操作：
    #   .sort_values("date")   按日期排序
    #   .set_index("date")     把 date 列变成索引（这样 r.index 就是日期，画图方便）
    #   ["close"]              只取收盘价这一列 → Series
    return df.sort_values("date").set_index("date")["close"]


def setup_chinese_font() -> bool:
    """让 matplotlib 能显示中文。成功返回 True，找不到字体返回 False。

    不设的话，图里所有中文会变成一个个方框（豆腐块）。
    """
    import matplotlib
    from matplotlib import font_manager

    # 按优先级尝试微软雅黑、黑体、思源黑体
    for name in ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC"]:
        try:
            # findfont(名字, fallback_to_default=False)
            #   找一个真实的字体文件；fallback_to_default=False 表示"找不到就报错"
            #   报错正好被 except 捕获，于是我们继续试下一个字体名
            font_manager.findfont(name, fallback_to_default=False)

            # 设置全局默认字体族
            matplotlib.rcParams["font.sans-serif"] = [name]
            # 让负号正常显示（否则 -0.05 的减号也会变方框）
            matplotlib.rcParams["axes.unicode_minus"] = False
            return True
        except Exception:      # 找不到这个字体就换下一个，不算错误
            continue
    return False


def plot_three(r: pd.Series, out_rel: str = "reports/figs/d01_lesson.png") -> str:
    """画三张图并保存，返回图片路径。"""
    # matplotlib.use("Agg") 必须在 import pyplot 之前调用。
    # Agg 是"只渲染到文件、不弹窗"的后端，脚本里必须用它，
    # 否则 plt.show() 会卡住或者在没有显示器的环境直接报错。
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # 用均值、标准差生成一组"同均值同方差的正态随机数"作为对照
    mu = float(r.mean())
    sigma = float(r.std(ddof=1))
    fake = np.random.default_rng(SEED).normal(mu, sigma, len(r))
    # np.random.default_rng(SEED) 是 numpy 新版推荐的随机数生成器（旧写法 np.random.seed 已不推荐）
    # .normal(均值, 标准差, 个数) 生成正态随机样本

    # subplots(1, 3) 表示 1 行 3 列的子图；figsize 是英寸；dpi 是清晰度
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.4), dpi=130)

    # --- 图 1：收益分布 vs 正态 ---
    # hist(数据, bins=箱子数, density=True 表示"画成概率密度"便于和理论曲线比)
    axes[0].hist(r, bins=120, density=True, alpha=0.75, label="HS300 日对数收益")
    # np.linspace(起点, 终点, 个数) 生成等间距的横坐标，用来画平滑曲线
    xs = np.linspace(r.min(), r.max(), 400)
    # 手写正态密度函数（不调 scipy，看清楚公式）
    pdf = np.exp(-((xs - mu) ** 2) / (2 * sigma ** 2)) / (sigma * math.sqrt(2 * math.pi))
    axes[0].plot(xs, pdf, "r-", lw=1.6, label="同均值方差正态")
    # 纵轴取对数：正态的尾部会衰减到 1e-5 量级，不取对数根本看不出尾部差异
    axes[0].set_yscale("log")
    axes[0].set_title("分布（对数纵轴）vs 正态")
    axes[0].legend(fontsize=8)      # 显示图例，字号调小一点

    # --- 图 2：Q-Q 图 ---
    # 横轴是正态分位数，纵轴是实际分位数。
    # 若数据真的正态，点会落在 45° 红线上；两端翘起 = 肥尾。
    axes[1].plot(fake, np.sort(r.values), ".", ms=1.5)
    lim = [min(fake.min(), r.min()), max(fake.max(), r.max())]
    axes[1].plot(lim, lim, "r--", lw=1)      # 参考线（虚线）
    axes[1].set_title("Q-Q 图：两端偏离")

    # --- 图 3：净值与历史高点 ---
    nav = (1 + r).cumprod()
    axes[2].plot(nav.index, nav.values, lw=1.2, label="净值")
    axes[2].plot(nav.index, nav.cummax().values, ls="--", lw=0.8, color="grey", label="历史高点")
    axes[2].set_title("净值与历史高点")
    axes[2].legend(fontsize=8)

    # tight_layout() 自动调整子图间距，避免标题/坐标轴被裁掉
    fig.tight_layout()

    path = os.path.join(ROOT, out_rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # savefig 存文件；plt.close(fig) 释放内存（批量画图时不关会越画越慢）
    fig.savefig(path)
    plt.close(fig)
    return path


# =============================================================================
# 【第 4 部分】主流程：把上面所有零件串起来并输出报告
# =============================================================================
def main() -> int:
    # 4.1 设置字体（顺便告诉用户成功没有）
    font_ok = setup_chinese_font()
    print("中文字体:", "已设置" if font_ok else "未找到，图内中文会变方框")

    # 4.2 读数据 → 算收益
    close = load_close()
    r = log_returns(close).dropna()      # dropna 丢掉第一个 NaN

    # 4.3 依次计算各项指标，装进一个 dict 方便统一输出和存盘
    st = annualized_stats(r)
    res = {
        "样本天数": int(len(r)),
        "样本区间": f"{r.index.min():%Y-%m-%d} ~ {r.index.max():%Y-%m-%d}",
        # round(x, 4) 保留 4 位小数，只是为了让打印好看，不影响内部计算
        "年化收益": round(st["年化收益"], 4),
        "年化波动": round(st["年化波动"], 4),
        # 夏普比率 = 超额收益 / 波动；这里无风险利率取 0
        "夏普(0利率)": round(st["年化收益"] / st["年化波动"], 3),
        "最大回撤": round(max_drawdown(r), 4),
        # .skew() 偏度：<0 左偏（暴跌比暴涨更极端）；正态应为 0
        "偏度": round(float(r.skew()), 3),
        # .kurt() 返回"超额峰度"（正态为 0），+3 才是通常说的峰度（正态为 3）
        "峰度(原始)": round(float(r.kurt() + 3), 3),
        # (r > 0).mean() 布尔序列求均值 = 上涨天数占比
        "日胜率": round(float((r > 0).mean()), 4),
        # 3 倍与 5 倍标准差的尾部概率对比（5 倍时正态几乎不可能发生）
        "|z|>3": {k: round(v, 6) for k, v in tail_ratio(r, 3).items()},
        "|z|>5": {k: round(v, 6) for k, v in tail_ratio(r, 5).items()},
        "可复现性": f"固定种子 SEED={SEED}",
    }

    # 4.4 打印报告
    print("=" * 58)
    for k, v in res.items():
        # f-string 的 {:12} 表示这个字段占 12 个字符宽度，左对齐 → 输出整齐
        print(f"{k:14}: {v}")

    # 4.5 输出"三句话结论"——这是研究报告的雏形
    print("=" * 58)
    print("三句话结论（抄进 docs/d01.md）:")
    print(f"  1. 沪深300 日对数收益峰度 {res['峰度(原始)']}，正态应为 3 —— 尖峰肥尾。")
    print(f"  2. |z|>3 实际占比 {res['|z|>3']['实际']:.4%}，是正态理论 "
          f"{res['|z|>3']['正态理论']:.4%} 的 {res['|z|>3']['倍数']:.1f} 倍。")
    print("  3. 因此后续因子检验不能假设正态，要用 bootstrap 或稳健统计量。")

    # 4.6 画图 + 存 JSON
    fig = plot_three(r)
    out_dir = os.path.join(ROOT, "reports")
    os.makedirs(out_dir, exist_ok=True)
    # open(路径, "w", encoding="utf-8") 写文本文件；
    # json.dump(对象, 文件, ensure_ascii=False 保留中文, indent=2 缩进美化)
    with open(os.path.join(out_dir, "d01_lesson.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=2)

    print("图  ->", fig)
    print("数据->", os.path.join(out_dir, "d01_lesson.json"))

    # 4.7 自检：同种子两次生成随机数必须一致（可复现性的最小验证）
    a = np.random.default_rng(SEED).normal(size=3)
    b = np.random.default_rng(SEED).normal(size=3)
    assert np.array_equal(a, b), "随机种子失效！"
    print("可复现性自检: 通过")
    return 0

main()
# 入口判断：直接运行本文件才执行 main()
if __name__ == "__main__":
    raise SystemExit(main())
