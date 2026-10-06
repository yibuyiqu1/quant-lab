# -*- coding: utf-8 -*-
"""Day 2 pandas 基础练习：数据结构、选择、派生列、时间索引。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_parquet(os.path.join(ROOT, "data", "clean", "hs300.parquet"))
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

print("=== 1. 先看数据长什么样 ===")
print("形状:", df.shape)
print("类型:\n", df.dtypes.to_string())
print(df.head(3).to_string(index=False))

print("\n=== 2. 三种选择方式 ===")
print("df['close'] 类型:", type(df["close"]).__name__)
print("df[['close','volume']] 类型:", type(df[["close", "volume"]]).__name__)
print("df.loc[0,'close'] =", df.loc[0, "close"])
print("df.iloc[0,4]      =", df.iloc[0, 4])

print("\n=== 3. 布尔筛选 ===")
print("收盘价 > 4000 的天数:", len(df[df["close"] > 4000]))
print("2024 年以来行数:", len(df[df["date"] >= "2024-01-01"]))

print("\n=== 4. 派生新列 ===")
df["ret"] = df["close"].pct_change()
df["log_ret"] = np.log(df["close"]).diff()
df["amp"] = df["high"] - df["low"]
df["vol_ma20"] = df["volume"].rolling(20).mean()
print(df[["date", "close", "ret", "log_ret", "amp", "vol_ma20"]].tail(3).to_string(index=False))

print("\n=== 5. 缺失值（差分/滚动必然产生）===")
print(df.isna().sum().to_string())

print("\n=== 6. 排序与去重 ===")
print("振幅最大的 3 天:")
print(df.nlargest(3, "amp")[["date", "high", "low", "amp"]].to_string(index=False))
print("重复日期数:", int(df["date"].duplicated().sum()))

print("\n=== 7. 时间索引与重采样 ===")
ts = df.set_index("date")
print("按月最后一个交易日收盘:\n", ts["close"].resample("ME").last().tail(3).to_string())
print("月收益率:\n", ts["close"].resample("ME").last().pct_change().tail(3).round(4).to_string())
# 注意两点：
# 1) 要按"日收益 × 年份"分组算，不能对年线取 std（那样样本只有 2-3 个点）
# 2) 标准差是日频的，年化要乘以 sqrt(244)
ann_vol = ts["ret"].groupby(ts.index.year).std() * np.sqrt(244)
print("按年化波动率（年化后）:\n", ann_vol.tail(3).round(4).to_string())
