# -*- coding: utf-8 -*-
"""Day 1 参考实现：把 4 个核心函数 + 画图串起来。

第 1 遍：照着这个敲，边敲边想每一步在做什么
第 2 遍：关掉这个文件，从空文件重写这 4 个函数
第 3 遍：用 pytest 自测（src/test_d01_analysis.py），全绿才算过关

运行：
    .venv\\Scripts\\python.exe src\\d01_analysis.py          # 出报告与图
    .venv\\Scripts\\python.exe -m pytest src\\test_d01_analysis.py -v
"""
from __future__ import annotations

import json
import math
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 42            # 固定随机种子：两次运行结果必须完全一致
ANNUAL = 244         # A 股每年约 244 个交易日


# ============================================================ 核心函数（要能手写）

def log_returns(close: pd.Series) -> pd.Series:
    """对数收益：ln(P_t / P_{t-1})。第一个值为 NaN。

    为什么研究里用对数收益：多期收益可以直接相加，做回归和统计更自然。
    """
    return np.log(close.astype(float)).diff()


def annualized_stats(r: pd.Series) -> dict:
    """年化收益与年化波动。

    年化收益 = 净值终值^(1/年数) - 1，年数 = 样本天数 / 244
    年化波动 = 日收益标准差 × sqrt(244)
    """
    r = r.dropna()
    nav = (1 + r).cumprod()                      # 净值曲线
    years = len(r) / ANNUAL
    ann_ret = nav.iloc[-1] ** (1 / years) - 1
    ann_vol = r.std(ddof=1) * math.sqrt(ANNUAL)
    return {"年化收益": float(ann_ret), "年化波动": float(ann_vol)}


def max_drawdown(r: pd.Series) -> float:
    """最大回撤：净值相对历史高点的最大跌幅，返回负数。

    回撤_t = 净值_t / 历史最高净值_t - 1
    量化里它比夏普更重要：它回答"最惨的时候你要忍受多少"。
    """
    r = r.fillna(0)
    nav = (1 + r).cumprod()
    dd = nav / nav.cummax() - 1
    return float(dd.min())


def normal_cdf(x: float) -> float:
    """标准正态分布函数，用 erf 实现（不依赖 scipy，方便理解）。"""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def tail_ratio(r: pd.Series, k: float = 3.0) -> dict:
    """比较 P(|z| > k) 的实际占比与正态理论值。

    把收益标准化成 z = (r - 均值) / 标准差 之后，
    正态分布下 P(|z| > 3) ≈ 0.27%；如果实际远大于它，就是肥尾。
    """
    r = r.dropna()
    z = (r - r.mean()) / r.std(ddof=1)
    actual = float((z.abs() > k).mean())
    theo = float(2 * (1 - normal_cdf(k)))
    return {"实际": actual, "正态理论": theo, "倍数": actual / theo if theo else float("nan")}


# ============================================================ 画图与报告

def setup_chinese_font() -> bool:
    """设置中文字体，否则图里中文会变成方框。成功返回 True。"""
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


def load_close() -> pd.Series:
    """读取本地已落盘的数据（先跑 d01_data.py）。"""
    path = os.path.join(ROOT, "data", "clean", "hs300.parquet")
    df = pd.read_parquet(path)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").set_index("date")["close"]


def plot(r: pd.Series, out: str = "reports/figs/d01_lecture.png") -> str:
    """三张图：分布 vs 正态、Q-Q、净值与回撤。"""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    mu, sigma = float(r.mean()), float(r.std(ddof=1))
    fake = np.random.default_rng(SEED).normal(mu, sigma, len(r))

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.4), dpi=130)

    axes[0].hist(r, bins=120, density=True, alpha=0.75, label="HS300 日对数收益")
    xs = np.linspace(r.min(), r.max(), 400)
    axes[0].plot(xs, np.exp(-((xs - mu) ** 2) / (2 * sigma ** 2)) / (sigma * math.sqrt(2 * math.pi)),
                 "r-", lw=1.6, label="同均值方差正态")
    axes[0].set_yscale("log")
    axes[0].set_title("分布（对数纵轴）vs 正态")
    axes[0].legend(fontsize=8)

    axes[1].plot(fake, np.sort(r.values), ".", ms=1.5)
    lim = [min(fake.min(), r.min()), max(fake.max(), r.max())]
    axes[1].plot(lim, lim, "r--", lw=1)
    axes[1].set_title("Q-Q 图：两端偏离")

    nav = (1 + r).cumprod()
    axes[2].plot(nav.index, nav.values, lw=1.2, label="净值")
    axes[2].plot(nav.index, nav.cummax().values, ls="--", lw=0.8, color="grey", label="历史高点")
    axes[2].set_title("净值与历史高点")
    axes[2].legend(fontsize=8)

    fig.tight_layout()
    path = os.path.join(ROOT, out)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    return path


def main() -> int:
    font_ok = setup_chinese_font()
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
        "|z|>3": {k: (round(v, 6) if isinstance(v, float) else v) for k, v in tail_ratio(r, 3).items()},
        "|z|>5": {k: (round(v, 6) if isinstance(v, float) else v) for k, v in tail_ratio(r, 5).items()},
        "中文字体": "已设置" if font_ok else "未找到（图内中文会变方框）",
        "可复现性": "固定种子 SEED=42",
    }

    print("=" * 58)
    for k, v in res.items():
        print(f"{k:12}: {v}")

    print("=" * 58)
    print("三句话结论（写进 docs/d01.md）：")
    print(f"  1. 沪深300 日对数收益的峰度是 {res['峰度(原始)']}，正态应为 3 —— 尖峰肥尾。")
    print(f"  2. |z|>3 的实际占比 {res['|z|>3']['实际']:.4%}，是正态理论 "
          f"{res['|z|>3']['正态理论']:.4%} 的 {res['|z|>3']['倍数']:.1f} 倍。")
    print("  3. 因此后续因子检验不能假设正态，要用 bootstrap 或稳健统计量。")

    fig = plot(r)
    out_dir = os.path.join(ROOT, "reports")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "d01_lecture.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=2)
    print("图 ->", fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
