# -*- coding: utf-8 -*-
"""Day 4 向量化训练：速度对比、条件赋值、滚动、分组标准化、分层。"""
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_parquet(os.path.join(ROOT, "data", "clean", "hs300.parquet"))
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

print("=== 1. 速度对比：20 万次运算 ===")
n = 200_000
data = np.random.default_rng(42).normal(size=n)

t0 = time.perf_counter()
out_slow = np.empty(n)
for i in range(n):
    out_slow[i] = data[i] * 2 + 1
t_slow = time.perf_counter() - t0

t0 = time.perf_counter()
out_fast = data * 2 + 1
t_fast = time.perf_counter() - t0

print(f"for 循环: {t_slow:.3f} 秒")
print(f"向量化  : {t_fast:.4f} 秒")
print(f"加速比  : {t_slow / t_fast:.0f} 倍")
assert np.allclose(out_slow, out_fast)
print("两种写法结果一致 -> 断言通过")

print("\n=== 2. 条件赋值 np.where / np.select ===")
df["up"] = np.where(df["close"] > df["open"], 1, 0)
print("阳线占比:", round(float(df["up"].mean()), 3))
df["level"] = np.select([df["close"] > 4000, df["close"] > 3000], ["高位", "中位"], default="低位")
print(df["level"].value_counts().to_string())

print("\n=== 3. 滚动窗口 ===")
df["ma20"] = df["close"].rolling(20).mean()
df["std20"] = df["close"].pct_change().rolling(20).std()
df["mom20"] = df["close"] / df["close"].shift(20) - 1
print(df[["date", "close", "ma20", "std20", "mom20"]].tail(3).to_string(index=False))

print("\n=== 4. 分组 transform：横截面标准化 ===")
stock = pd.DataFrame({
    "date": np.tile(df["date"].values, 3),
    "code": np.repeat(["A", "B", "C"], len(df)),
    "factor": np.concatenate([
        np.random.default_rng(1).normal(0, 1, len(df)),
        np.random.default_rng(2).normal(5, 2, len(df)),
        np.random.default_rng(3).normal(-3, 0.5, len(df)),
    ]),
})
stock["z"] = stock.groupby("date")["factor"].transform(lambda s: (s - s.mean()) / s.std(ddof=0))
# 校验时也要用 ddof=0，否则 pandas 默认的 ddof=1 会得到 1.22 而不是 1.0
chk = stock.groupby("date")["z"].agg(["mean", lambda s: s.std(ddof=0)])
chk.columns = ["mean", "std(ddof=0)"]
print(chk.tail(3).round(6).to_string())
print("↑ 每日均值≈0、标准差≈1 才算标准化成功")

print("\n=== 5. agg vs transform ===")
print("agg（每组一个值）:")
print(stock.groupby("code")["factor"].agg(["mean", "std"]).round(3).to_string())
print(f"transform 结果长度 {stock['z'].shape[0]} = 原表长度 {len(stock)}")

print("\n=== 6. 排名与分层打分 ===")
# 说明：这里只有 3 只"股票"，所以只分 3 层；真实面板（几百只股票）才分 5 层
stock["rank_pct"] = stock.groupby("date")["factor"].rank(pct=True)
n_q = stock["code"].nunique()
stock["bucket"] = pd.qcut(stock["rank_pct"], n_q, labels=[f"Q{i + 1}" for i in range(n_q)])
print(stock.groupby("bucket", observed=True)["factor"].agg(["count", "mean"]).round(3).to_string())
print("↑ Q1→Q3 均值递增说明分层逻辑正确（分的是 factor 本身，所以必然单调）")
