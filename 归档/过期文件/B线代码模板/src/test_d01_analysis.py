# -*- coding: utf-8 -*-
"""Day 1 练习测试：验收你自己写的 d01_analysis 里的 4 个函数。

用法：
    .venv\\Scripts\\python.exe -m pytest src\\test_d01_analysis.py -v

要求（在 src/d01_analysis.py 里实现，函数名必须一致）：
    log_returns(close)      -> 对数收益序列
    annualized_stats(r)     -> dict，含 "年化收益" 与 "年化波动"
    max_drawdown(r)         -> 一个负数（最大回撤）
    tail_ratio(r)           -> dict，含 "实际" 与 "正态理论" 的 P(|z|>3)
    setup_chinese_font()    -> 成功找到中文字体时返回 True

你可以先只写函数体、先不管数据文件；本测试用的是构造出来的小样本，
不依赖 data/ 目录，所以随时能跑。
"""
import math

import numpy as np
import pandas as pd
import pytest

# 从你自己的实现里导入；还没写就 import 失败，这本身就是第一个提示
from d01_analysis import (
    annualized_stats,
    log_returns,
    max_drawdown,
    setup_chinese_font,
    tail_ratio,
)

ANNUAL = 244


# ---------------------------------------------------------------- 1. 对数收益
def test_log_returns_basic():
    close = pd.Series([100.0, 110.0, 121.0])
    r = log_returns(close)
    # 第一个必然缺失（差分），后面两个都是 ln(1.1)
    assert r.isna().sum() == 1 or len(r) == 2
    assert r.iloc[-1] == pytest.approx(math.log(1.1), abs=1e-12)


def test_log_returns_length():
    close = pd.Series(np.linspace(100, 200, 50))
    r = log_returns(close)
    # 允许两种风格：保留 NaN（长度 50）或已 dropna（长度 49），但不能更少
    assert len(r) in (49, 50)


def test_log_returns_sign():
    """对数收益的方向必须正确：涨为正、跌为负。"""
    close = pd.Series([100.0, 90.0, 99.0])
    r = log_returns(close).dropna()
    assert r.iloc[0] < 0        # 100 -> 90 下跌
    assert r.iloc[1] > 0        # 90 -> 99 上涨


# ---------------------------------------------------------- 2. 年化收益与波动
def test_annualized_stats_keys():
    r = pd.Series(np.random.default_rng(0).normal(0.0005, 0.01, 244))
    st = annualized_stats(r)
    assert "年化收益" in st and "年化波动" in st


def test_annualized_vol_of_constant_returns_is_zero():
    """每天收益完全一样 -> 波动为 0。"""
    r = pd.Series([0.001] * 244)
    st = annualized_stats(r)
    assert st["年化波动"] == pytest.approx(0.0, abs=1e-12)


def test_annualized_vol_formula():
    """年化波动 = 日收益标准差 × sqrt(244)。"""
    rng = np.random.default_rng(1)
    r = pd.Series(rng.normal(0, 0.01, 500))
    st = annualized_stats(r)
    expect = r.std(ddof=1) * math.sqrt(ANNUAL)
    assert st["年化波动"] == pytest.approx(expect, rel=1e-9)


def test_annualized_return_positive_for_uptrend():
    """单调上涨的序列，年化收益必须为正，并且量级合理。"""
    r = pd.Series([0.001] * 244)
    st = annualized_stats(r)
    assert st["年化收益"] > 0
    assert st["年化收益"] == pytest.approx((1.001 ** 244) - 1, rel=1e-6)


# ------------------------------------------------------------ 3. 最大回撤
def test_max_drawdown_monotone_is_zero():
    """只涨不跌 -> 没有回撤。"""
    r = pd.Series([0.01] * 10)
    assert max_drawdown(r) == pytest.approx(0.0, abs=1e-12)


def test_max_drawdown_known_value():
    """净值 1 -> 1.5 -> 0.75：从高点 1.5 跌到 0.75，回撤 -50%。"""
    r = pd.Series([0.5, -0.5])          # 用简单收益构造：1*1.5=1.5, 1.5*0.5=0.75
    dd = max_drawdown(r)
    assert dd == pytest.approx(-0.5, abs=1e-9)
    assert dd < 0


def test_max_drawdown_is_negative():
    rng = np.random.default_rng(2)
    r = pd.Series(rng.normal(0, 0.02, 1000))
    assert max_drawdown(r) < 0


# ------------------------------------------------------- 4. 尾部概率（肥尾）
def test_tail_ratio_keys_and_values():
    rng = np.random.default_rng(3)
    r = pd.Series(rng.normal(0, 1, 20000))     # 标准正态
    tr = tail_ratio(r)
    assert set(tr) >= {"实际", "正态理论"}
    # 正态样本下，实际值应接近理论值 0.0027（允许较宽的容差）
    assert tr["正态理论"] == pytest.approx(0.0027, abs=1e-4)
    assert tr["实际"] == pytest.approx(0.0027, abs=0.002)


def test_tail_ratio_detects_fat_tail():
    """t 分布（自由度 3）的尾部远厚于正态：实际占比应明显大于理论值。"""
    r = pd.Series(np.random.default_rng(4).standard_t(3, 20000))
    tr = tail_ratio(r)
    assert tr["实际"] > tr["正态理论"] * 2


def test_tail_ratio_uses_own_mean_std():
    """把数据整体平移放大后，标准化后的尾部占比不应变化（说明用了 z-score）。"""
    rng = np.random.default_rng(5)
    r = pd.Series(rng.standard_t(4, 5000))
    a = tail_ratio(r)["实际"]
    b = tail_ratio(r * 3 + 100)["实际"]
    assert a == pytest.approx(b, abs=1e-12)


# ------------------------------------------------------------ 5. 中文字体
def test_setup_chinese_font_runs():
    """Windows 上应能找到微软雅黑；找不到也要能优雅返回 False 而不是报错。"""
    out = setup_chinese_font()
    assert isinstance(out, bool)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
