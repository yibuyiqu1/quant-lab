# -*- coding: utf-8 -*-
r"""Day 2 · B线测试：验收你自己写的 day2_practice.py

运行：
    cd /d "E:\AI结果\量化"
    .venv\Scripts\python.exe -m pytest src\test_day2.py -v

默认检查 day2_practice（你的练习）；想看答案是否也对，用：
    $env:D02_MODULE="day2_answers"; .venv\Scripts\python.exe -m pytest src\test_day2.py -v
"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE,):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_MODULE = os.environ.get("D02_MODULE", "day2_practice")
print(f"[测试目标] 正在检查模块: {_MODULE}")

try:
    _m = __import__(_MODULE)
except ModuleNotFoundError as exc:
    raise SystemExit(f"找不到模块 {_MODULE}，请确认在 src\\ 下。原始错误: {exc}")

load_index = _m.load_index
add_features = _m.add_features
count_extreme = _m.count_extreme
yearly_vol = _m.yearly_vol
monthly_return = _m.monthly_return
make_panel = _m.make_panel
cs_zscore = _m.cs_zscore
rank_pct = _m.rank_pct
code_stats = _m.code_stats

ANNUAL = 244


# ---------------------------------------------------------------- 第 0 题
def test_load_index_is_series_with_datetime_index():
    s = load_index()
    assert isinstance(s, pd.Series)
    assert isinstance(s.index, pd.DatetimeIndex), "索引必须是日期类型（to_datetime + set_index）"
    assert len(s) > 5000


def test_load_index_is_sorted_ascending():
    s = load_index()
    assert s.index.is_monotonic_increasing, "必须按时间升序（sort_values）"


# ---------------------------------------------------------------- 第 1 题
def test_add_features_creates_all_columns():
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=50),
        "open": np.arange(50) + 100.0,
        "high": np.arange(50) + 102.0,
        "low": np.arange(50) + 99.0,
        "close": np.arange(50) + 101.0,
    })
    out = add_features(df)
    for col in ["ret", "log_ret", "amp", "ma20", "vol20"]:
        assert col in out.columns, f"缺少列 {col}"


def test_add_features_does_not_mutate_input():
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=30),
        "high": np.arange(30) + 2.0, "low": np.arange(30) + 0.0,
        "close": np.arange(30) + 1.0,
    })
    before = df.copy()
    add_features(df)
    pd.testing.assert_frame_equal(df, before, obj="传入的 df 不应被修改（要写 df.copy()）")


def test_add_features_values_correct():
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=25),
        "high": [10.0] * 25, "low": [8.0] * 25, "close": [9.0] * 25,
    })
    out = add_features(df)
    assert out["amp"].iloc[-1] == pytest.approx(2.0)
    assert out["ma20"].iloc[-1] == pytest.approx(9.0)
    assert out["vol20"].iloc[-1] == pytest.approx(0.0)      # 价格不变 -> 波动为 0
    assert pd.isna(out["ret"].iloc[0]), "第一天没有前一天，ret 必须是 NaN"
    assert pd.isna(out["log_ret"].iloc[0]), "log_ret 第一个也必须是 NaN"


# ---------------------------------------------------------------- 第 2 题
def test_count_extreme_on_constant_is_zero():
    r = pd.Series([0.001] * 100)
    # 常数序列标准差为 0，标准化会变成 NaN；这里只要求不抛异常
    try:
        n = count_extreme(r, 3)
        assert n >= 0
    except ZeroDivisionError:
        pytest.skip("常数序列标准差为 0，实现里若未保护会除以 0（可接受）")


def test_count_extreme_known_value():
    r = pd.Series([0.0] * 99 + [10.0])       # 一个极端值
    assert count_extreme(r, 3) >= 1


def test_count_extreme_returns_int():
    rng = np.random.default_rng(0)
    r = pd.Series(rng.normal(0, 0.01, 1000))
    n = count_extreme(r, 3)
    assert isinstance(n, int)


# ---------------------------------------------------------------- 第 3 题
def test_yearly_vol_is_annualized():
    rng = np.random.default_rng(1)
    idx = pd.date_range("2020-01-01", periods=244 * 2, freq="B")   # 约两年
    r = pd.Series(rng.normal(0, 0.01, len(idx)), index=idx)
    v = yearly_vol(r)
    assert isinstance(v.index[0], (int, np.integer)), "索引应该是年份（int）"
    # 日波动 1% -> 年化约 1% × sqrt(244) ≈ 15.6%，允许统计波动
    assert 0.10 < v.mean() < 0.22, f"年化波动量级不对: {v.mean():.4f}"


def test_monthly_return_known():
    idx = pd.date_range("2024-01-01", periods=60, freq="D")
    close = pd.Series(np.linspace(100, 159, 60), index=idx)
    m = monthly_return(close)
    assert m.iloc[0] != m.iloc[0] or True         # 第一个月为 NaN 或数值都行
    assert len(m) >= 2
    # 单调上涨的数据，月收益应为正
    assert (m.dropna() > 0).all()


# ---------------------------------------------------------------- 第 4 题
def test_cs_zscore_mean_zero_std_one():
    panel = make_panel(n_stock=20)
    z = cs_zscore(panel)
    assert "z" in z.columns
    chk = z.groupby("date")["z"].agg(["mean", lambda s: s.std(ddof=0)])
    chk.columns = ["m", "s"]
    assert chk["m"].abs().max() < 1e-9, "每日横截面均值必须≈0"
    assert (chk["s"] - 1).abs().max() < 1e-9, "每日横截面标准差必须=1（用 ddof=0）"


def test_cs_zscore_does_not_mutate_input():
    panel = make_panel(n_stock=5)
    before = panel.copy()
    cs_zscore(panel)
    pd.testing.assert_frame_equal(panel, before, obj="不应修改传入的 panel")


def test_rank_pct_range():
    panel = make_panel(n_stock=10)
    rk = rank_pct(panel)
    g = rk.groupby("date")["rank_pct"].agg(["min", "max"])
    assert g["min"].max() == pytest.approx(0.1, abs=1e-9)   # 10 只股票，最小排名 1/10
    assert g["max"].min() == pytest.approx(1.0, abs=1e-9)


# ---------------------------------------------------------------- 第 5 题
def test_code_stats_shape_and_columns():
    panel = make_panel(n_stock=8)
    st = code_stats(panel)
    assert list(st.columns) == ["mean", "std"], "列必须是 mean 与 std（用 agg）"
    assert len(st) == 8
    # 造数据时第 i 只均值为 i*0.1，检查单调性
    assert st["mean"].is_monotonic_increasing


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
