# -*- coding: utf-8 -*-
r"""Day 2 · B线练习（自己动手填）

主题：pandas 数据结构与选择、时间序列操作、向量化
运行：
    cd /d "E:\AI结果\量化"
    .venv\Scripts\python.exe src\day2_practice.py

规则：每个函数下方有 TODO，把实现写出来。
      写完运行本文件 → 看打印结果是否正确；
      再跑测试：.venv\Scripts\python.exe -m pytest src\test_day2.py -v
      卡住时看 src\day2_answers.py（答案与逐步讲解）。
"""
import os
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "clean", "hs300.parquet")


# ===========================================================================
# 第 0 题（热身）：读数据
# ===========================================================================
def load_index(path: str = DATA_PATH) -> pd.Series:
    """读沪深300 parquet，返回以日期为索引的 close 序列（升序）。

    知识点：
      pd.read_parquet(路径)     读 parquet
      pd.to_datetime(列)         文本 -> 时间类型（不转的话没法按月汇总）
      sort_values("date")        按时间升序
      set_index("date")          把日期变成索引
      ["close"]                  只取收盘价这一列 -> Series
    """
    # TODO
    raise NotImplementedError("请实现 load_index")


# ===========================================================================
# 第 1 题：派生列（向量化，不要写 for 循环）
# ===========================================================================
def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """在 df 上新增 5 列并返回新的 DataFrame（不改动传入的 df）。

    要求：
      ret       简单收益率 = close / close.shift(1) - 1
      log_ret   对数收益率 = ln(close).diff()
      amp       振幅       = high - low
      ma20      20 日均线  = close 的 20 期滚动均值
      vol20     20 日波动  = ret 的 20 期滚动标准差（ddof=1）

    知识点：
      df.copy()                     先复制，避免改到外面的数据
      s.shift(1)                    整体下移一行（昨天的值）
      np.log(s).diff()              对数收益
      s.rolling(20).mean()          滚动均值
      s.rolling(20).std()           滚动标准差（默认 ddof=1）
    """
    # TODO
    raise NotImplementedError("请实现 add_features")


# ===========================================================================
# 第 2 题：条件筛选（布尔索引）
# ===========================================================================
def count_extreme(r: pd.Series, k: float = 3.0) -> int:
    """统计 |标准化收益| > k 的天数。

    步骤：
      z = (r - r.mean()) / r.std(ddof=1)      标准化
      count = (z.abs() > k).sum()             布尔序列求和 = True 的个数
    返回 int。
    """
    # TODO
    raise NotImplementedError("请实现 count_extreme")


# ===========================================================================
# 第 3 题：时间索引与重采样
# ===========================================================================
def yearly_vol(r: pd.Series, freq: int = 244) -> pd.Series:
    """按年计算**年化**波动率，索引是年份（int）。

    步骤：
      d = r.groupby(r.index.year).std()        按"年份"分组求日标准差
      return d * sqrt(freq)                     年化
    注意两个坑：
      ① 要按"日收益 × 年份"分组，不能对年线取 std（那样样本只剩 2-3 个点）
      ② 得到的是日标准差，年化要乘 sqrt(244)
    """
    # TODO
    raise NotImplementedError("请实现 yearly_vol")


def monthly_return(close: pd.Series) -> pd.Series:
    """按自然月计算**月收益率**：每月最后一个交易日的收盘价，算环比。

    步骤：
      m = close.resample("ME").last()       按月末取最后一个值（ME = month end）
      return m.pct_change()                 环比收益率
    """
    # TODO
    raise NotImplementedError("请实现 monthly_return")


# ===========================================================================
# 第 4 题：横截面标准化（因子研究最核心的一个操作）
# ===========================================================================
def make_panel(n_stock: int = 20, seed: int = 42) -> pd.DataFrame:
    """造一个多股票面板，列：date / code / factor。日期范围与真实数据一致。"""
    close = load_index()
    dates = close.index
    rng = np.random.default_rng(seed)
    frames = []
    for i in range(n_stock):
        frames.append(pd.DataFrame({
            "date": dates,
            "code": f"S{i:02d}",
            "factor": rng.normal(i * 0.1, 1.0, len(dates)),   # 每只股票均值不同
        }))
    return pd.concat(frames, ignore_index=True)


def cs_zscore(panel: pd.DataFrame) -> pd.DataFrame:
    """在每个交易日内部做横截面标准化，新增列 z（返回新 DataFrame）。

    要 求：z = (factor - 当日均值) / 当日标准差(ddof=0)

    知识点（Day 2 最重要的一条）：
      groupby("date")["factor"].transform(...)   transform 返回**与原表等长**的结果，
                                                 这样才能把标准化后的值填回每一行
      对比 agg：agg 每个组只返回一个值（长度=组数），没法回填
    """
    # TODO
    raise NotImplementedError("请实现 cs_zscore")


def rank_pct(panel: pd.DataFrame) -> pd.DataFrame:
    """新增列 rank_pct = 每个交易日内部 factor 的百分位排名（0~1）。"""
    # TODO
    raise NotImplementedError("请实现 rank_pct")


# ===========================================================================
# 第 5 题：分组聚合（你写的代码要能通过测试）
# ===========================================================================
def code_stats(panel: pd.DataFrame) -> pd.DataFrame:
    """按 code 分组，统计每只股票的 factor 均值与标准差，返回 DataFrame。

    要求：索引是 code，列为 ["mean", "std"] 两列（用 agg 得到）。
    """
    # TODO
    raise NotImplementedError("请实现 code_stats")


# ===========================================================================
# 自测入口：把结果打印出来，和注释里的"预期"对照
# ===========================================================================
def main() -> int:
    close = load_index()
    print(f"[0] 数据行数: {len(close)}  首尾: {close.index.min():%Y-%m-%d} ~ {close.index.max():%Y-%m-%d}")

    df = pd.read_parquet(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    feat = add_features(df)
    print("[1] 新增列:", [c for c in feat.columns if c not in df.columns])
    print(feat[["date", "close", "ret", "log_ret", "amp", "ma20", "vol20"]].tail(3).to_string(index=False))

    r = feat["log_ret"].dropna()
    print(f"[2] |z|>3 的天数: {count_extreme(r, 3)}   （预期 107）")
    print("[3] 按年年化波动:")
    print(yearly_vol(r).tail(3).round(4).to_string())
    print("[3] 最近 3 个月收益率:")
    print(monthly_return(close).tail(3).round(4).to_string())

    panel = make_panel()
    print(f"[4] 面板形状: {panel.shape}  股票数: {panel['code'].nunique()}")
    z = cs_zscore(panel)
    chk = z.groupby("date")["z"].agg(["mean", lambda s: s.std(ddof=0)])
    chk.columns = ["mean", "std(ddof=0)"]
    print("[4] 每日 z 的均值/标准差（应≈0 / =1）:")
    print(chk.tail(2).round(6).to_string())
    print(f"[5] 每只股票统计（前 3 行）:\n{code_stats(panel).head(3).round(3).to_string()}")
    print("\n如果以上数字都对上了，Day 2 的 B 线就过关了。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
