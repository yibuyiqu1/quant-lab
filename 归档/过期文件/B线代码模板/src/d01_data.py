# -*- coding: utf-8 -*-
"""Day 1 数据抓取：沪深300 日线，落盘 CSV + parquet。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

import akshare as ak
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "hs300.csv")
CLEAN = os.path.join(ROOT, "data", "clean", "hs300.parquet")


def main() -> None:
    os.makedirs(os.path.dirname(RAW), exist_ok=True)
    os.makedirs(os.path.dirname(CLEAN), exist_ok=True)

    df = ak.stock_zh_index_daily(symbol="sh000300")
    print("原始列名:", list(df.columns))

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    df.to_csv(RAW, index=False, encoding="utf-8-sig")   # CSV：能用 Excel 打开检查
    df.to_parquet(CLEAN, index=False)                   # parquet：体积小、类型不丢

    print(f"共 {len(df)} 行，区间 {df['date'].min():%Y-%m-%d} ~ {df['date'].max():%Y-%m-%d}")
    print(df.tail(3).to_string(index=False))
    print("\n已保存:\n ", RAW, "\n ", CLEAN)


if __name__ == "__main__":
    main()
