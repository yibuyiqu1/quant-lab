# -*- coding: utf-8 -*-
"""Day 7 阶段验收：跑通全链路并输出汇总报告。

一条命令验证 D1–D6 的所有产物：
    python src/d07_acceptance.py
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quantlib import (  # noqa: E402
    forward_return,
    information_coefficient,
    load_index_returns,
    momentum,
    perf_stats,
    quantile_portfolio,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    checks = []

    # 1) 数据文件
    for rel in ["data/raw/hs300.csv", "data/clean/hs300.parquet"]:
        p = os.path.join(ROOT, rel)
        ok = os.path.exists(p) and os.path.getsize(p) > 0
        checks.append((f"数据文件 {rel}", ok, f"{os.path.getsize(p) // 1024} KB" if ok else "缺失"))

    # 2) 图
    for rel in ["d01_returns.png", "d06_nav_drawdown.png", "d06_quantile_bar.png"]:
        p = os.path.join(ROOT, "reports", "figs", rel)
        ok = os.path.exists(p)
        checks.append((f"图表 {rel}", ok, "存在" if ok else "缺失"))

    # 3) 指标
    r = load_index_returns()
    st = perf_stats(r)
    checks.append(("收益序列可读取", len(r) > 5000, f"{len(r)} 个交易日"))
    checks.append(("峰度 > 3（肥尾）", st["峰度"] > 3, f"峰度 {st['峰度']}"))
    checks.append(("最大回撤 < -50%（含 2008）", st["最大回撤"] < -0.5, f"{st['最大回撤']:.2%}"))

    # 4) 因子链路
    close = pd.read_parquet(os.path.join(ROOT, "data", "clean", "hs300.parquet")) \
        .assign(date=lambda d: pd.to_datetime(d["date"])).sort_values("date").set_index("date")["close"]
    mom, fwd = momentum(close, 20), forward_return(close, 5)
    grp, cnt = quantile_portfolio(mom, fwd, 5)
    ic = information_coefficient(mom, fwd)
    spread = float(grp.iloc[-1] - grp.iloc[0])
    checks.append(("分层组合可计算", len(grp) == 5, f"5 层样本数 {cnt.tolist()}"))
    checks.append(("IC 可计算", ic == ic, f"IC = {ic:.4f}（未扣成本）"))
    checks.append(("多空价差 > 0", spread > 0, f"Q5-Q1 = {spread:.4%}"))

    print("=" * 66)
    print("D1–D7 验收报告")
    print("=" * 66)
    for name, ok, detail in checks:
        print(f"  [{'通过' if ok else '未通过'}] {name:34} {detail}")
    print("=" * 66)

    passed = sum(1 for _, ok, _ in checks if ok)
    print(f"总计 {passed}/{len(checks)} 项通过")
    if passed < len(checks):
        print("未通过项的处理：缺数据跑 src/d01_data.py；缺图跑 src/d01_analysis.py 与 src/d06_plots.py")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
