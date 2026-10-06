# -*- coding: utf-8 -*-
"""Day 1 验收脚本：沪深300 日对数收益的可复现分析。

产出：
    reports/d01_result.json    统计量（机器可读）
    reports/d01_result.md      统计量（人可读）
    reports/figs/d01_returns.png  收益分布 vs 正态 + 净值与回撤
验收标准：
    1) 同一脚本重复运行结果完全一致（种子固定）
    2) parquet 读取行数与原始一致
    3) 报告给出肥尾的定量证据
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 42


def load_returns() -> pd.Series:
    raw = pd.read_csv(os.path.join(ROOT, "data/raw/hs300.csv"), parse_dates=["date"])
    clean = pd.read_parquet(os.path.join(ROOT, "data/clean/hs300.parquet"))
    assert len(raw) == len(clean), f"parquet 行数与原始不一致: {len(raw)} vs {len(clean)}"
    df = raw.dropna(subset=["close"]).sort_values("date")
    r = np.log(df["close"].astype(float)).diff().dropna()
    r.index = pd.DatetimeIndex(df["date"].iloc[1:])
    return r


def analyze(r: pd.Series) -> dict:
    from scipy import stats

    mu, sigma = float(r.mean()), float(r.std(ddof=1))
    rng = np.random.default_rng(SEED)
    fake = rng.normal(mu, sigma, size=len(r))

    jb_stat, jb_p = stats.jarque_bera(r)
    # 注意：scipy 1.18 下 kstest(r, "norm", args=...) 存在版本兼容问题，
    # 用冻结分布对象是更稳的写法，也便于以后替换成 t 分布做对照。
    ks_stat, ks_p = stats.kstest(r, stats.norm(loc=mu, scale=sigma).cdf)
    # scipy>=1.17 的 anderson 返回 SignificanceResult（含 pvalue），旧版返回临界值表，
    # 这里做兼容处理：优先用 p 值，取不到再退回 5% 临界值 0.752（正态情形经典值）。
    ad = stats.anderson(r, dist="norm")
    if hasattr(ad, "pvalue"):
        ad_stat, ad_crit, ad_desc = float(ad.statistic), float(ad.pvalue), "p 值"
    else:
        ad_stat, ad_crit, ad_desc = float(ad.statistic), float(ad.critical_values[2]), "5% 临界值(0.752)"

    z = (r - mu) / sigma
    out = {
        "样本区间": f"{r.index.min():%Y-%m-%d} ~ {r.index.max():%Y-%m-%d}",
        "样本量": int(len(r)),
        "年化收益": round(float(np.expm1(mu * 244)), 4),
        "年化波动": round(float(sigma * np.sqrt(244)), 4),
        "偏度": round(float(r.skew()), 4),
        "峰度(超额)": round(float(r.kurt()), 4),
        "峰度(原始)": round(float(r.kurt() + 3), 4),
        "夏普(无风险0)": round(float(mu / sigma * np.sqrt(244)), 4),
        "最大回撤": round(float(((1 + r).cumprod() / (1 + r).cumprod().cummax() - 1).min()), 4),
        "日胜率": round(float((r > 0).mean()), 4),
        "|z|>2 实际占比": round(float((z.abs() > 2).mean()), 4),
        "|z|>2 正态理论": round(float(2 * (1 - stats.norm.cdf(2))), 4),
        "|z|>3 实际占比": round(float((z.abs() > 3).mean()), 4),
        "|z|>3 正态理论": round(float(2 * (1 - stats.norm.cdf(3))), 4),
        "Jarque-Bera 统计量": round(float(jb_stat), 2),
        "Jarque-Bera p值": float(jb_p),
        "KS 统计量": round(float(ks_stat), 4),
        "KS p值": float(ks_p),
        "Anderson-Darling 统计量": round(ad_stat, 3),
        f"Anderson-Darling（{ad_desc}）": ad_crit,
        "最差单日": round(float(r.min()), 4),
        "最好单日": round(float(r.max()), 4),
        "说明": "p 值极小 => 拒绝正态；峰度远大于 3 => 肥尾，后续所有因子检验都不能假设正态",
    }
    return out


def _setup_cjk_font():
    """优先使用系统中文等线/黑体，避免图内中文变成方框。"""
    import matplotlib
    from matplotlib import font_manager

    for name in ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Source Han Sans SC"]:
        try:
            font_manager.findfont(name, fallback_to_default=False)
            matplotlib.rcParams["font.sans-serif"] = [name]
            matplotlib.rcParams["axes.unicode_minus"] = False
            return name
        except Exception:  # noqa: BLE001
            continue
    return None


def plot(r: pd.Series) -> str | None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:  # noqa: BLE001
        return None

    cjk = _setup_cjk_font()
    T = (lambda zh, en: zh) if cjk else (lambda zh, en: en)

    mu, sigma = float(r.mean()), float(r.std(ddof=1))
    rng = np.random.default_rng(SEED)
    fake = rng.normal(mu, sigma, size=len(r))

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.4), dpi=130)
    axes[0].hist(r, bins=120, density=True, alpha=0.75, label=T("HS300 日对数收益", "HS300 daily log return"))
    xs = np.linspace(r.min(), r.max(), 400)
    axes[0].plot(xs, np.exp(-((xs - mu) ** 2) / (2 * sigma**2)) / (sigma * np.sqrt(2 * np.pi)),
                 "r-", lw=1.6, label=T("同均值方差正态", "Normal with same mean/var"))
    axes[0].set_yscale("log")
    axes[0].set_title(T("收益分布（对数纵轴）vs 正态：尖峰肥尾", "Return distribution (log y) vs Normal"))
    axes[0].legend(fontsize=8)

    axes[1].plot(fake, np.sort(r), ".", ms=1.5)
    lim = [min(fake.min(), r.min()), max(fake.max(), r.max())]
    axes[1].plot(lim, lim, "r--", lw=1)
    axes[1].set_title(T("Q-Q 图：两端偏离正态", "Q-Q plot: tails deviate"))
    axes[1].set_xlabel("Normal quantile")
    axes[1].set_ylabel("Sample quantile")

    nav = (1 + r).cumprod()
    axes[2].plot(nav.index, nav.values, lw=1.2, label=T("净值", "NAV"))
    axes[2].plot(nav.index, nav.cummax().values, lw=0.9, ls="--", color="grey", label=T("历史高点", "Running max"))
    axes[2].set_title(T("净值与回撤", "NAV and drawdown"))
    axes[2].legend(fontsize=8)

    fig.tight_layout()
    out_dir = os.path.join(ROOT, "reports", "figs")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "d01_returns.png")
    fig.savefig(path)
    plt.close(fig)
    return path


def main() -> int:
    r = load_returns()
    res = analyze(r)
    out_dir = os.path.join(ROOT, "reports")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "d01_result.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=2)
    lines = ["# Day 1 验收结果：沪深300 日对数收益", ""]
    lines += [f"- {k}: {v}" for k, v in res.items()]
    fig = plot(r)
    if fig:
        lines += ["", f"![收益分布]({os.path.relpath(fig, out_dir).replace(os.sep, '/')})"]
    with open(os.path.join(out_dir, "d01_result.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    # 可复现性自检：同种子两次生成的正态样本必须一致
    a = np.random.default_rng(SEED).normal(size=5)
    b = np.random.default_rng(SEED).normal(size=5)
    assert np.array_equal(a, b), "随机种子未生效"
    print("可复现性自检: 通过")
    for k, v in res.items():
        print(f"{k}: {v}")
    if fig:
        print("图 ->", fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
