"""
02 · 第一个因子：20 日动量

用法:
    python src/02_first_factor.py

前置:
    先跑 src/01_fetch_data.py 生成 data/daily.parquet

这一步要产出的四张表/图:
    1) IC 序列 + ICIR + t 统计量
    2) 5 分组平均收益（检验单调性）
    3) 分组累计净值曲线
    4) 多空组合（第5组 - 第1组）净值

关键防坑点（代码里已处理，务必理解为什么）:
    - 未来收益用 open[t+1] 买入、close[t+5] 卖出，而不是 close[t] -> close[t+5]。
      用当日收盘价成交 = 未来函数，回测再漂亮也是幻觉。
    - 因子做截面 winsorize + z-score，避免极值主导排序。
    - 样本外必须按「时间」切分，不能随机切分。
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figs"
FIG_DIR.mkdir(exist_ok=True)

LOOKBACK = 20      # 动量回看窗口（交易日）
HOLD = 5           # 持有期（交易日）
N_GROUPS = 5       # 分组数
COST_BPS = 30      # 双边成本 30bp ≈ 千三（佣金+印花税+冲击），调仓一次扣一次


# ---------------------------------------------------------------- 数据
def load_prices() -> pd.DataFrame:
    pq, csv = ROOT / "data" / "daily.parquet", ROOT / "data" / "daily.csv"
    if pq.exists():
        df = pd.read_parquet(pq)
    elif csv.exists():
        df = pd.read_csv(csv, parse_dates=["date"])
    else:
        raise SystemExit("找不到数据，请先运行 src/01_fetch_data.py")
    return df.sort_values(["date", "code"]).reset_index(drop=True)


# ---------------------------------------------------------------- 因子与收益
def build(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("code", group_keys=False)

    # 因子：过去 LOOKBACK 日收益率（t 日收盘可得，无未来信息）
    df["mom20"] = g["close"].apply(lambda s: s / s.shift(LOOKBACK) - 1)

    # 未来收益：t+1 开盘买，t+1+HOLD-1 收盘卖
    # shift(-k) 把「未来」搬到当前行，用于对齐；建模时它是 y，不是 X
    df["fwd_open"] = g["open"].apply(lambda s: s.shift(-1))
    df["fwd_close"] = g["close"].apply(lambda s: s.shift(-(1 + HOLD - 1)))
    df["fwd_ret"] = df["fwd_close"] / df["fwd_open"] - 1

    return df


def winsorize_zscore(s: pd.Series, n_sigma: float = 3.0) -> pd.Series:
    """截面去极值 + 标准化。按交易日分组做，避免用到全样本信息。"""
    mu, sd = s.mean(), s.std()
    lo, hi = mu - n_sigma * sd, mu + n_sigma * sd
    s = s.clip(lo, hi)
    sd2 = s.std()
    return (s - s.mean()) / sd2 if sd2 and not np.isnan(sd2) else s * 0.0


# ---------------------------------------------------------------- 评估
def ic_analysis(df: pd.DataFrame) -> pd.DataFrame:
    def _ic(sub: pd.DataFrame) -> float:
        x, y = sub["mom20_z"], sub["fwd_ret"]
        mask = x.notna() & y.notna()
        if mask.sum() < 5:
            return np.nan
        return stats.spearmanr(x[mask], y[mask]).statistic

    ic = (
        df.dropna(subset=["mom20_z", "fwd_ret"])
          .groupby("date", group_keys=True)[["mom20_z", "fwd_ret"]]
          .apply(_ic)
          .rename("IC")
          .to_frame()
          .dropna()
    )
    ic.index = pd.to_datetime(ic.index)
    return ic


def group_analysis(df: pd.DataFrame):
    """分组收益 + 多空净值。返回 (分组平均收益表, 累计净值表, 多空累计)"""
    d = df.dropna(subset=["mom20_z", "fwd_ret"]).copy()
    d["grp"] = d.groupby("date")["mom20_z"].transform(
        lambda s: pd.qcut(s.rank(method="first"), N_GROUPS, labels=False) + 1
    )

    grp_ret = (
        d.groupby(["date", "grp"])["fwd_ret"].mean()
         .unstack("grp")
         .sort_index()
    )
    # 每 HOLD 期调仓一次，成本按调仓次数扣
    grp_ret = grp_ret.iloc[::HOLD] - COST_BPS / 10_000
    nav = (1 + grp_ret).cumprod()
    long_short = nav[N_GROUPS] - nav[1] + 1  # 相对净值口径
    return grp_ret, nav, long_short


# ---------------------------------------------------------------- 输出
def main() -> None:
    df = build(load_prices())
    df["mom20_z"] = (
        df.dropna(subset=["mom20"])
          .groupby("date")["mom20"]
          .transform(winsorize_zscore)
    )
    df["mom20_z"] = df["mom20_z"].reindex(df.index)

    ic = ic_analysis(df)
    icir = ic["IC"].mean() / ic["IC"].std()
    t_stat = ic["IC"].mean() / (ic["IC"].std() / np.sqrt(len(ic)))

    print("\n" + "=" * 56)
    print(f"20 日动量因子 · 持有 {HOLD} 日 · 股票池 {df['code'].nunique()} 只")
    print("-" * 56)
    print(f"IC 均值      : {ic['IC'].mean(): .4f}")
    print(f"IC 标准差    : {ic['IC'].std(): .4f}")
    print(f"ICIR         : {icir: .4f}")
    print(f"IC t 统计量  : {t_stat: .4f}")
    print(f"IC > 0 占比  : {(ic['IC'] > 0).mean(): .2%}")
    print(f"样本期       : {ic.index.min().date()} ~ {ic.index.max().date()}")
    print("=" * 56)

    grp_ret, nav, ls = group_analysis(df)
    print("\n分组平均未来收益（%）：")
    print((grp_ret.mean() * 100).round(3).to_string())
    print(f"\n多空组合累计（相对净值口径）: {ls.iloc[-1]: .4f}")

    # --- 图1：IC 序列
    fig, ax = plt.subplots(figsize=(11, 3.6))
    ax.bar(ic.index, ic["IC"], width=3, color="#22D3EE", alpha=.85)
    ax.axhline(ic["IC"].mean(), color="#F59E0B", lw=1.2,
               label=f"mean IC = {ic['IC'].mean():.4f}")
    ax.axhline(0, color="#52525B", lw=.8)
    ax.set_title(f"Rank IC · momentum_{LOOKBACK} · holding {HOLD}d", color="#FAFAFA")
    ax.legend(facecolor="#141417", labelcolor="#FAFAFA", framealpha=0)
    ax.set_facecolor("#0A0A0B"); fig.patch.set_facecolor("#0A0A0B")
    ax.tick_params(colors="#A1A1AA"); ax.spines[:].set_color("#27272A")
    fig.tight_layout(); fig.savefig(FIG_DIR / "ic_series.png", dpi=140); plt.close(fig)

    # --- 图2：分组净值
    fig, ax = plt.subplots(figsize=(11, 4.2))
    for c in nav.columns:
        ax.plot(nav.index, nav[c], lw=1.4, label=f"G{int(c)}")
    ax.plot(ls.index, ls, lw=2.2, color="#F59E0B", ls="--", label="G5 - G1")
    ax.set_title(f"Group NAV · {N_GROUPS} quantile groups (cost {COST_BPS}bp)", color="#FAFAFA")
    ax.legend(facecolor="#141417", labelcolor="#FAFAFA", framealpha=0, ncol=3)
    ax.set_facecolor("#0A0A0B"); fig.patch.set_facecolor("#0A0A0B")
    ax.tick_params(colors="#A1A1AA"); ax.spines[:].set_color("#27272A")
    fig.tight_layout(); fig.savefig(FIG_DIR / "group_nav.png", dpi=140); plt.close(fig)

    print(f"\n图片已保存到: {FIG_DIR}")
    print("\n⚠ 本次只用 30 只蓝筹做流程演示，样本太小，IC 与分组结论都不具统计意义。")
    print("   下一步：把股票池扩到沪深300 / 中证500，重跑后再判断因子是否有效。")


if __name__ == "__main__":
    main()
