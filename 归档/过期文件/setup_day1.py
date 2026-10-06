# -*- coding: utf-8 -*-
"""Day 1 环境验证脚本：检查依赖、建目录、尝试拉取沪深300数据并落盘。

用法：
    python src/setup_day1.py
输出：
    data/raw/hs300.csv        原始数据
    data/clean/hs300.parquet  清洗后数据（若安装了 pyarrow）
    docs/env.md               环境与数据源探测结果
"""
from __future__ import annotations

import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = ["data/raw", "data/clean", "src", "notebooks", "reports", "docs", "资料库"]
DEPS = ["numpy", "pandas", "matplotlib", "scipy", "sklearn", "statsmodels", "pyarrow", "akshare", "baostock"]


def ensure_dirs() -> None:
    for d in DIRS:
        os.makedirs(os.path.join(ROOT, d), exist_ok=True)
    print("[ok] 目录结构就绪")


def check_deps() -> dict[str, str]:
    import importlib
    import importlib.metadata as md

    found = {}
    for name in DEPS:
        try:
            importlib.import_module(name)
            try:
                found[name] = md.version(name)
            except Exception:  # noqa: BLE001
                found[name] = "installed"
        except Exception:  # noqa: BLE001
            found[name] = "MISSING"
    return found


def fetch_hs300() -> tuple[object | None, str]:
    """优先 akshare，失败回退 baostock。返回 (DataFrame|None, 说明)。"""
    import pandas as pd

    # --- 路线 1: akshare ---
    try:
        import akshare as ak

        df = ak.stock_zh_index_daily(symbol="sh000300")
        df = df.rename(columns=str.lower)
        if {"date", "close"} <= set(df.columns):
            df["date"] = pd.to_datetime(df["date"])
            return df.sort_values("date").reset_index(drop=True), "akshare:stock_zh_index_daily(sh000300)"
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] akshare 失败: {type(exc).__name__}: {exc}")

    # --- 路线 2: baostock ---
    try:
        import baostock as bs
        import pandas as pd

        lg = bs.login()
        if lg.error_code != "0":
            raise RuntimeError(f"baostock 登录失败: {lg.error_msg}")
        rs = bs.query_history_k_data_plus(
            "sh.000300", "date,code,open,high,low,close,volume,amount",
            start_date="2015-01-01", end_date=datetime.now().strftime("%Y-%m-%d"),
            frequency="d", adjustflag="3",
        )
        rows = []
        while rs.error_code == "0" and rs.next():
            rows.append(rs.get_row_data())
        bs.logout()
        df = pd.DataFrame(rows, columns=rs.fields)
        if df.empty:
            raise RuntimeError("baostock 返回空数据")
        for col in ["open", "high", "low", "close", "volume", "amount"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["date"] = pd.to_datetime(df["date"])
        return df, "baostock:query_history_k_data_plus(sh.000300)"
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] baostock 失败: {type(exc).__name__}: {exc}")

    return None, "两个数据源均不可用（离线环境请自行准备 CSV 到 data/raw/hs300.csv）"


def main() -> int:
    ensure_dirs()
    deps = check_deps()
    print("[ok] 依赖检查:", ", ".join(f"{k}={v}" for k, v in deps.items()))

    df, source = fetch_hs300()
    lines = [f"# 环境快照 {datetime.now():%Y-%m-%d %H:%M}", "", "## Python", f"- 解释器: `{sys.executable}`",
             f"- 版本: {sys.version.split()[0]}", "", "## 依赖"]
    lines += [f"- {k}: {v}" for k, v in deps.items()]
    lines += ["", "## 数据源", f"- 结果: {source}"]

    if df is not None:
        raw_path = os.path.join(ROOT, "data/raw/hs300.csv")
        df.to_csv(raw_path, index=False, encoding="utf-8-sig")
        print(f"[ok] 原始数据 -> {raw_path} ({len(df)} 行, {df['date'].min():%Y-%m-%d} ~ {df['date'].max():%Y-%m-%d})")
        lines += [f"- 行数: {len(df)}", f"- 区间: {df['date'].min():%Y-%m-%d} ~ {df['date'].max():%Y-%m-%d}"]
        try:
            clean = os.path.join(ROOT, "data/clean/hs300.parquet")
            df.to_parquet(clean, index=False)
            print(f"[ok] parquet -> {clean}")
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] parquet 写入失败（装 pyarrow 即可）: {exc}")
    else:
        lines += ["- 说明: 需手动放置 data/raw/hs300.csv，列含 date/close"]

    with open(os.path.join(ROOT, "docs/env.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("[ok] 环境快照 -> docs/env.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
