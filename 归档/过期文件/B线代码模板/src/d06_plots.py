# -*- coding: utf-8 -*-
"""Day 6 可视化：生成量化报告最常用的 6 张图。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "reports", "figs")


def set_font() -> str:
    """设置中文字体，避免图里中文变成方框。"""
    for name in ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC"]:
        try:
            font_manager.findfont(name, fallback_to_default=False)
            matplotlib.rcParams["font.sans-serif"] = [name]
            matplotlib.rcParams["axes.unicode_minus"] = False
            return name
        except Exception:  # noqa: BLE001
            continue
    return "(未找到中文字体，图内中文可能显示为方框)"


def save(fig, name: str) -> str:
    os.makedirs(FIG, exist_ok=True)
    path = os.path.join(FIG, name)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def main() -> None:
    print("使用字体:", set_font())
    df = pd.read_parquet(os.path.join(ROOT, "data", "clean", "hs300.parquet"))
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").set_index("date")
    r = np.log(df["close"]).diff().dropna()
    nav = (1 + r).cumprod()

    # 1) 净值 + 回撤
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), dpi=130, sharex=True,
                                   gridspec_kw={"height_ratios": [3, 1]})
    ax1.plot(nav.index, nav.values, lw=1.2, label="净值")
    ax1.plot(nav.index, nav.cummax().values, ls="--", lw=0.8, color="grey", label="历史高点")
    ax1.set_title("沪深300 净值与回撤")
    ax1.legend(fontsize=9)
    dd = nav / nav.cummax() - 1
    ax2.fill_between(dd.index, dd.values, 0, color="crimson", alpha=0.5)
    ax2.set_ylabel("回撤")
    print("保存:", save(fig, "d06_nav_drawdown.png"))

    # 2) 收益分布（对数纵轴）
    fig, ax = plt.subplots(figsize=(7, 4), dpi=130)
    ax.hist(r, bins=100, density=True, alpha=0.7)
    ax.set_yscale("log")
    ax.set_title("日对数收益分布（对数纵轴：才能看两端）")
    print("保存:", save(fig, "d06_return_hist.png"))

    # 3) 滚动波动率（波动聚集）
    fig, ax = plt.subplots(figsize=(10, 3.5), dpi=130)
    rv = r.rolling(20).std() * np.sqrt(244)
    ax.plot(rv.index, rv.values, lw=1)
    ax.set_title("滚动 20 日年化波动率")
    print("保存:", save(fig, "d06_rolling_vol.png"))

    # 4) 月度收益热力图
    monthly = r.resample("ME").apply(lambda s: (1 + s).prod() - 1)
    table = pd.DataFrame({"y": monthly.index.year, "m": monthly.index.month, "r": monthly.values})
    pivot = table.pivot(index="y", columns="m", values="r")
    fig, ax = plt.subplots(figsize=(11, 7), dpi=130)
    im = ax.imshow(pivot.values, cmap="RdYlGn", vmin=-0.15, vmax=0.15, aspect="auto")
    ax.set_xticks(range(12), labels=[f"{m}月" for m in range(1, 13)])
    ax.set_yticks(range(len(pivot)), labels=pivot.index)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            v = pivot.values[i, j]
            if v == v:
                ax.text(j, i, f"{v * 100:.0f}", ha="center", va="center", fontsize=7)
    ax.set_title("月度收益热力图（%）——深红格子就是灾难月")
    fig.colorbar(im, ax=ax, shrink=0.8)
    print("保存:", save(fig, "d06_monthly_heatmap.png"))

    # 5) 分层收益柱状图（因子研究的门面图）
    close = df["close"]
    mom = close / close.shift(20) - 1
    fwd = close.shift(-5) / close - 1
    panel = pd.DataFrame({"mom": mom, "fwd": fwd}).dropna()
    panel["q"] = pd.qcut(panel["mom"].rank(method="first"), 5,
                         labels=["Q1最弱", "Q2", "Q3", "Q4", "Q5最强"])
    grp = panel.groupby("q", observed=True)["fwd"].mean()
    fig, ax = plt.subplots(figsize=(7, 4), dpi=130)
    ax.bar(range(5), grp.values * 100)
    ax.set_xticks(range(5), labels=grp.index, rotation=15)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_ylabel("未来 5 日平均收益（%）")
    ax.set_title("按 20 日动量分层的未来收益（未扣成本）")
    print("保存:", save(fig, "d06_quantile_bar.png"))
    print("\n分层结果（注意：此时还没扣交易成本，只能看现象）:")
    print((grp * 100).round(4).to_string())


if __name__ == "__main__":
    main()
