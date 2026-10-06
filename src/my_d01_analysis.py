# -*- coding: utf-8 -*-
r"""我的 Day 1 分析脚本（已从 notebooks 移入 src，并修复 3 处问题）

注意开头那个 r：r + 三引号 表示「原始字符串」，里面的反斜杠不当作转义符。
不加 r 的话，下面的 Windows 路径里的 \A 会被 Python 3.12 报警：
    SyntaxWarning: invalid escape sequence '\A'
凡是文档里出现 Windows 路径，就用 r 开头。

修复记录：
  1. def plot_three(r: pd.Seriers  ->  pd.Series            （拼写错误）
  2. mu = float(r.mean)            ->  float(r.mean())      （漏括号，取到的是方法对象而非数值）
  3. sigma = float(r.std(off=1))   ->  float(r.std(ddof=1)) （参数名错，应为 ddof）
  4. 文件末尾补回 if __name__ == "__main__" 入口（之前被删掉，所以运行没任何反应）

运行：
    cd /d "E:\AI结果\量化"
    .venv\Scripts\python.exe src\my_d01_analysis.py

测试：
    $env:D01_MODULE="my_d01_analysis"
    .venv\Scripts\python.exe -m pytest src\test_d01_analysis.py -v
"""
import json
import math
import os
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

# 本文件在 项目/src/ 下时，两次 dirname 正好回到项目根目录：
#   第一次 dirname：E:\AI结果\量化\src      第二次：E:\AI结果\量化
# 注意：如果把文件移到更深一层（如 src/xxx/），这里就要多加一次 dirname
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "clean", "hs300.parquet")
SEED = 42
ANNUAL = 244


def log_returns(close: pd.Series) -> pd.Series:
    """对数收益：ln(P_t) - ln(P_{t-1})，第一个值为 NaN。"""
    return np.log(close.astype(float)).diff()


def annualized_stats(r: pd.Series, freq: int = ANNUAL) -> dict:
    """返回 {"年化收益": float, "年化波动": float}。"""
    r = r.dropna()
    nav = (1 + r).cumprod()
    years = len(r) / freq
    ann_ret = nav.iloc[-1] ** (1 / years) - 1
    ann_vol = r.std(ddof=1) * math.sqrt(freq)
    # 字典用「冒号」分隔键和值；用逗号会变成 set（集合），无法用 ["键"] 取值
    return {"年化收益": float(ann_ret), "年化波动": float(ann_vol)}


def max_drawdown(r: pd.Series) -> float:
    """最大回撤，返回负数。"""
    r = r.fillna(0)
    nav = (1 + r).cumprod()
    dd = nav / nav.cummax() - 1
    return float(dd.min())


def normal_cdf(x: float) -> float:
    """标准正态分布函数 Φ(x)。"""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def tail_ratio(r: pd.Series, k: float = 3.0) -> dict:
    """尾部概率对比：实际占比 vs 正态理论。"""
    r = r.dropna()
    z = (r - r.mean()) / r.std(ddof=1)
    actual = float((z.abs() > k).mean())
    theo = float(2 * (1 - normal_cdf(k)))
    return {"实际": actual, "正态理论": theo, "倍数": actual / theo if theo else float("nan")}


def load_close() -> pd.Series:
    """读本地 parquet，返回以日期为索引的收盘价。"""
    df = pd.read_parquet(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").set_index("date")["close"]


def setup_chinese_font() -> bool:
    """让 matplotlib 能显示中文。成功返回 True，找不到字体返回 False。"""
    import matplotlib
    from matplotlib import font_manager

    for name in ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC"]:
        try:
            font_manager.findfont(name, fallback_to_default=False)
            matplotlib.rcParams["font.sans-serif"] = [name]
            matplotlib.rcParams["axes.unicode_minus"] = False
            return True
        except Exception:  # noqa: BLE001
            continue
    return False


def plot_three(r: pd.Series, out_rel: str = "reports/figs/d01_mine.png") -> str:
    """三张图：分布 vs 正态、Q-Q、净值与历史高点。返回图片路径。

    每个参数的含义见《Matplotlib画图逐行注解.md》
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    mu = float(r.mean())            # 必须加 ()：不加取到的是"方法对象"，不是数值
    sigma = float(r.std(ddof=1))    # 参数名是 ddof，不是 off

    fake = np.random.default_rng(SEED).normal(mu, sigma, len(r))

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.4), dpi=130)

    # --- 图 1：收益分布 vs 正态 ---
    axes[0].hist(r, bins=120, density=True, alpha=0.75, label="HS300 日对数收益")
    xs = np.linspace(r.min(), r.max(), 400)
    pdf = np.exp(-((xs - mu) ** 2) / (2 * sigma ** 2)) / (sigma * math.sqrt(2 * math.pi))
    axes[0].plot(xs, pdf, "r-", lw=1.6, label="同均值方差正态")
    axes[0].set_yscale("log")
    axes[0].set_title("分布（对数纵轴）vs 正态")
    axes[0].legend(fontsize=8)

    # --- 图 2：Q-Q 图 ---
    axes[1].plot(fake, np.sort(r.values), ".", ms=1.5)
    lim = [min(fake.min(), r.min()), max(fake.max(), r.max())]
    axes[1].plot(lim, lim, "r--", lw=1)
    axes[1].set_title("Q-Q 图：两端偏离")

    # --- 图 3：净值与历史高点 ---
    nav = (1 + r).cumprod()
    axes[2].plot(nav.index, nav.values, lw=1.2, label="净值")
    axes[2].plot(nav.index, nav.cummax().values, ls="--", lw=0.8, color="grey", label="历史高点")
    axes[2].set_title("净值与历史高点")
    axes[2].legend(fontsize=8)

    fig.tight_layout()

    path = os.path.join(ROOT, out_rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    return path


def main() -> int:
    font_ok = setup_chinese_font()
    print("中文字体:", "已设置" if font_ok else "未找到，图内中文会变方框")

    close = load_close()
    r = log_returns(close).dropna()
    st = annualized_stats(r)
    res = {
        "样本天数": int(len(r)),
        "样本区间": f"{r.index.min():%Y-%m-%d} ~ {r.index.max():%Y-%m-%d}",
        "年化收益": round(st["年化收益"], 4),
        "年化波动": round(st["年化波动"], 4),
        "夏普(0利率)": round(st["年化收益"] / st["年化波动"], 3),
        "最大回撤": round(max_drawdown(r), 4),
        "偏度": round(float(r.skew()), 3),
        "峰度(原始)": round(float(r.kurt() + 3), 3),
        "日胜率": round(float((r > 0).mean()), 4),
        "|z|>3": {k: round(v, 6) for k, v in tail_ratio(r, 3).items()},
        "|z|>5": {k: round(v, 6) for k, v in tail_ratio(r, 5).items()},
        "可复现性": f"固定种子 SEED={SEED}",
    }

    print("=" * 58)
    for k, v in res.items():
        print(f"{k:14}: {v}")

    print("=" * 58)
    print("三句话结论（抄进 docs/d01.md）:")
    print(f"  1. 沪深300 日对数收益峰度 {res['峰度(原始)']}，正态应为 3 —— 尖峰肥尾。")
    print(f"  2. |z|>3 实际占比 {res['|z|>3']['实际']:.4%}，是正态理论 "
          f"{res['|z|>3']['正态理论']:.4%} 的 {res['|z|>3']['倍数']:.1f} 倍。")
    print("  3. 因此后续因子检验不能假设正态，要用 bootstrap 或稳健统计量。")

    fig = plot_three(r)
    out_dir = os.path.join(ROOT, "reports")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "d01_mine.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=2)

    print("图  ->", fig)
    print("数据->", os.path.join(out_dir, "d01_mine.json"))

    a = np.random.default_rng(SEED).normal(size=3)
    b = np.random.default_rng(SEED).normal(size=3)
    assert np.array_equal(a, b), "随机种子失效！"
    print("可复现性自检: 通过")
    return 0


# ===========================================================================
# 入口：让"直接运行这个文件"能触发 main()
#
# __name__ 是 Python 自动给每个文件设的变量：
#     直接运行本文件时      __name__ == "__main__"
#     被别的文件 import 时  __name__ == "my_d01_analysis"（模块名）
# 所以这个 if 的意思是"只有直接运行我才执行 main()"，
# 被 import 时不会偷偷跑一遍（否则 import 就会打印一大堆东西）。
#
# raise SystemExit(main()) 等价于两步：
#     code = main()           先跑主逻辑、拿到返回值
#     raise SystemExit(code)  把返回值当作进程退出码交给操作系统
# 好处：Windows 命令行里 echo %ERRORLEVEL% 能看到它（0 = 成功）。
# 详细对比见《Matplotlib画图逐行注解.md》最后一节。
# ===========================================================================
if __name__ == "__main__":
    raise SystemExit(main())
