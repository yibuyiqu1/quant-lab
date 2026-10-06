# -*- coding: utf-8 -*-
"""最小测试：保证工具库的关键函数没被改坏。

运行：
    cd src
    python -m pytest test_quantlib.py -v
"""
import numpy as np
import pandas as pd
import pytest

from quantlib import forward_return, momentum, max_drawdown_series, perf_stats, zscore


def test_zscore_mean_zero_std_one():
    s = pd.Series([1.0, 2.0, 3.0, 4.0])
    z = zscore(s)
    assert abs(z.mean()) < 1e-12
    assert abs(z.std(ddof=0) - 1) < 1e-12


def test_zscore_constant_returns_zero():
    s = pd.Series([5.0, 5.0, 5.0])
    assert (zscore(s) == 0).all()


def test_momentum_known_value():
    close = pd.Series([100.0, 110.0])
    assert momentum(close, window=1).iloc[1] == pytest.approx(0.1)


def test_forward_return_alignment():
    close = pd.Series([100.0, 110.0, 121.0])
    fwd = forward_return(close, horizon=1)
    assert np.isnan(fwd.iloc[-1])          # 最后一天没有未来收益
    assert fwd.iloc[0] == pytest.approx(0.1)


def test_perf_stats_on_constant_positive():
    r = pd.Series([0.001] * 244)
    st = perf_stats(r)
    assert st["日胜率"] == 1.0
    assert st["最大回撤"] == 0.0
    assert st["年化收益"] > 0.2


def test_max_drawdown_zero_when_monotone():
    r = pd.Series([0.01] * 10)
    assert max_drawdown_series(r).min() == pytest.approx(0.0)
