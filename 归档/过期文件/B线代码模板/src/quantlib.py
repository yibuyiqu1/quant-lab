# -*- coding: utf-8 -*-
"""量化研究工具库：本项目所有脚本共用。

设计原则：
1. 只放会被复用两次以上的函数
2. 每个函数写清输入输出，不含副作用（不打印、不画图）
3. 路径统一从项目根目录出发
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 42
ANNUAL = 244


# ---------------- 数据层 ----------------

def data_path(*parts: str) -> str:
    """拼接项目内的数据路径，例如 data_path('clean', 'hs300.parquet')。"""
    return os.path.join(ROOT, "data", *parts)


def load_index_returns(path: str | None = None, col: str = "close") -> pd.Series:
    """读取指数日线，返回以日期为索引的日对数收益序列。"""
    path = path or data_path("clean", "hs300.parquet")
    df = pd.read_parquet(path)
    df["date"] = pd.to_datetime(df["date"])
    s = df.sort_values("date").set_index("date")[col].astype(float)
    return np.log(s).diff().dropna()


# ---------------- 统计层 ----------------

def perf_stats(r: pd.Series, freq: int = ANNUAL) -> dict:
    """核心业绩指标。输入日收益序列，输出 dict。"""
    r = r.dropna()
    nav = (1 + r).cumprod()
    years = max(len(r) / freq, 1e-9)
    ann_ret = nav.iloc[-1] ** (1 / years) - 1
    ann_vol = r.std(ddof=1) * np.sqrt(freq)
    dd = nav / nav.cummax() - 1
    avg_loss = -r[r < 0].mean() if (r < 0).any() else np.nan
    ratio = r[r > 0].mean() / avg_loss if avg_loss == avg_loss and avg_loss > 0 else np.nan
    return {
        "累计收益": round(float(nav.iloc[-1] - 1), 4),
        "年化收益": round(float(ann_ret), 4),
        "年化波动": round(float(ann_vol), 4),
        "夏普": round(float(ann_ret / ann_vol), 3),
        "最大回撤": round(float(dd.min()), 4),
        "日胜率": round(float((r > 0).mean()), 4),
        "盈亏比": round(float(ratio), 3) if ratio == ratio else np.nan,
        "峰度": round(float(r.kurt() + 3), 3),
        "偏度": round(float(r.skew()), 3),
    }


def zscore(s: pd.Series) -> pd.Series:
    """横截面标准化；标准差为 0 时返回全 0 而不是 NaN。"""
    mu, sd = s.mean(), s.std(ddof=0)
    if sd and sd == sd and sd > 0:
        return (s - mu) / sd
    return s * 0.0


def max_drawdown_series(r: pd.Series) -> pd.Series:
    """逐日回撤序列（净值/历史高点 - 1）。"""
    nav = (1 + r.fillna(0)).cumprod()
    return nav / nav.cummax() - 1


# ---------------- 因子层 ----------------

def momentum(close: pd.Series, window: int = 20) -> pd.Series:
    """动量因子：过去 window 日收益率。"""
    return close / close.shift(window) - 1


def forward_return(close: pd.Series, horizon: int = 5) -> pd.Series:
    """未来 horizon 日收益（标签）。这是唯一允许使用未来数据的地方。"""
    return close.shift(-horizon) / close - 1


def quantile_portfolio(signal: pd.Series, fwd: pd.Series, n_q: int = 5):
    """按 signal 分层，返回 (每层平均未来收益, 每层样本数)。"""
    panel = pd.DataFrame({"signal": signal, "fwd": fwd}).dropna()
    if panel.empty:
        return pd.Series(dtype=float), pd.Series(dtype=int)
    panel["bucket"] = pd.qcut(panel["signal"].rank(method="first"), n_q,
                              labels=[f"Q{i + 1}" for i in range(n_q)])
    grp = panel.groupby("bucket", observed=True)["fwd"]
    return grp.mean(), grp.size()


def information_coefficient(signal: pd.Series, fwd: pd.Series) -> float:
    """IC：信号与未来收益的相关系数（单序列版本）。"""
    panel = pd.DataFrame({"signal": signal, "fwd": fwd}).dropna()
    if len(panel) < 3:
        return float("nan")
    return float(panel["signal"].corr(panel["fwd"]))
