# -*- coding: utf-8 -*-
"""手算示例：用真实数据把每个术语的算法逐步打印出来（前几步用小学算术就能验算）。"""
import sys
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"E:\AI结果\量化"
df = pd.read_parquet(rf"{ROOT}\data\clean\hs300.parquet")
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").set_index("date")

# ---------- 用最后 6 个交易日做"小学算术"演示 ----------
tail = df.tail(6)["close"]
print("=" * 78)
print("一、用真实数据做 6 天的小例子（数字都来自沪深300 收盘价）")
print("=" * 78)
print(tail.to_string())

p = tail.values
print("\n【简单收益】r_t = P_t / P_{t-1} - 1")
for i in range(1, len(p)):
    print(f"  {tail.index[i]:%Y-%m-%d}: {p[i]:.3f}/{p[i-1]:.3f} - 1 = {p[i]/p[i-1]-1:+.6f}")
print("  → 缺点：算 5 天累计收益要连乘 5 次，很麻烦")

print("\n【对数收益】r_t = ln(P_t) - ln(P_{t-1})")
lr = np.log(p)
for i in range(1, len(p)):
    print(f"  {tail.index[i]:%Y-%m-%d}: ln({p[i]:.3f})-ln({p[i-1]:.3f}) = {lr[i]-lr[i-1]:+.6f}")
print("  → 优点：5 天累计 = 5 个对数收益直接相加")

print("\n【两种口径对照】")
for i in range(1, len(p)):
    s = p[i]/p[i-1] - 1
    l = lr[i] - lr[i-1]
    print(f"  {tail.index[i]:%Y-%m-%d}  简单 {s:+.6f}   对数 {l:+.6f}   差 {s-l:+.8f}")
print("  → 收益很小时两者几乎相等（差在万分之一量级），这就是为什么两种都能用")

# ---------- 用一段人造净值把回撤讲透 ----------
print("\n" + "=" * 78)
print("二、回撤是什么：用人造净值逐步手算（这段最好拿纸笔跟一遍）")
print("=" * 78)
nav = pd.Series([1.00, 1.20, 1.50, 1.35, 1.05, 1.30, 1.80, 1.44],
                index=[f"第{i}天" for i in range(1, 9)], dtype=float)
peak = nav.cummax()
dd = nav / peak - 1
tbl = pd.DataFrame({"净值": nav, "历史最高净值": peak, "回撤": dd})
tbl["回撤%"] = (tbl["回撤"] * 100).round(2)
print(tbl.to_string())
print(f"\n最大回撤 = 回撤列的最小值 = {dd.min():.2%}（发生在第 5 天）")
print("注意：不是从最高点 1.80 算，是从'该时刻之前的历史最高点'算。")
print("  第 5 天净值 1.05，之前最高是 1.50 → 1.05/1.50-1 = -30%")
print("  第 8 天净值 1.44，之前最高是 1.80 → 1.44/1.80-1 = -20%")

# ---------- 真实数据的四项指标 ----------
print("\n" + "=" * 78)
print("三、真实沪深300 的对应数字（2002-01-07 ~ 2026-09-30）")
print("=" * 78)
r = np.log(df["close"].astype(float)).diff().dropna()
nav_real = (1 + r).cumprod()
years = len(r) / 244
ann_ret = nav_real.iloc[-1] ** (1 / years) - 1
ann_vol = r.std(ddof=1) * np.sqrt(244)
print(f"样本天数 {len(r)}  → 年数 = {len(r)}/244 = {years:.3f} 年")
print(f"累计净值 {nav_real.iloc[-1]:.4f}（1 元变 {nav_real.iloc[-1]:.4f} 元）")
print(f"年化收益 = {nav_real.iloc[-1]:.4f}^(1/{years:.3f}) - 1 = {ann_ret:.4f} = {ann_ret:.2%}")
print(f"日波动（标准差）= {r.std(ddof=1):.6f}")
print(f"年化波动 = {r.std(ddof=1):.6f} × √244 = {ann_vol:.4f} = {ann_vol:.2%}")
print(f"夏普（无风险利率取0）= {ann_ret:.4f} / {ann_vol:.4f} = {ann_ret/ann_vol:.3f}")
dd_real = nav_real / nav_real.cummax() - 1
print(f"最大回撤 = {dd_real.min():.4f} = {dd_real.min():.2%}，发生在 {dd_real.idxmin():%Y-%m-%d}")

print("\n【标准差为什么能用一只股票/指数算出来】")
print("  把日收益看成随机变量，样本标准差估计它的波动幅度。")
print(f"  日均值 {r.mean():+.6f}，日标准差 {r.std(ddof=1):.6f}")
print(f"  均值 ± 1 个标准差范围: [{r.mean()-r.std(ddof=1):.4f}, {r.mean()+r.std(ddof=1):.4f}]")
within = ((r > r.mean()-r.std(ddof=1)) & (r < r.mean()+r.std(ddof=1))).mean()
print(f"  实际落在该区间的比例 = {within:.2%}（正态理论 68.27%）")

print("\n【峰度与偏度】")
print(f"  偏度 skew = {r.skew():+.4f}（正态为 0；负值=左偏，暴跌比暴涨更极端）")
print(f"  超额峰度 kurt = {r.kurt():+.4f}（正态为 0）")
print(f"  峰度（通常说的）= {r.kurt()+3:.4f}（正态为 3）")
