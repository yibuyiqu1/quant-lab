# -*- coding: utf-8 -*-
r"""Day 2 · B线答案与逐步讲解

自己写完 src\day2_practice.py 之后再对照这份。
每一题都写清：怎么做、为什么这么做、常见错误。
运行本文件可以直接看到全部答案的输出：
    .venv\Scripts\python.exe src\day2_answers.py
"""
import os
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "clean", "hs300.parquet")


# ===========================================================================
# 第 0 题：读数据
# ===========================================================================
def load_index(path: str = DATA_PATH) -> pd.Series:
    """答案要点：
    四步走，一步都不能少：
      1. read_parquet        读文件
      2. to_datetime         文本 -> 时间类型
      3. sort_values("date") 按时间升序（时间序列的计算依赖顺序）
      4. set_index("date")   日期作索引，方便 .resample() 和画图

    常见错误：
      - 忘了 to_datetime：后面 r.index.year 会报错（字符串没有 .year）
      - 忘了 sort_values：数据恰好是倒序时，收益率符号会全部反过来
    """
    df = pd.read_parquet(path)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").set_index("date")["close"]


# ===========================================================================
# 第 1 题：派生列
# ===========================================================================
def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """答案要点：
    全部用向量化，一行算一列，不要写 for 循环。

    df.copy() 必须写：否则改的是传进来的那个 df（副作用），
    调用方的数据会被悄悄改掉，这种 bug 最难查。
    """
    out = df.copy()
    out["ret"] = out["close"] / out["close"].shift(1) - 1          # 简单收益
    out["log_ret"] = np.log(out["close"]).diff()                   # 对数收益
    out["amp"] = out["high"] - out["low"]                          # 振幅
    out["ma20"] = out["close"].rolling(20).mean()                  # 20 日均线
    out["vol20"] = out["ret"].rolling(20).std()                    # 20 日波动
    return out


# ===========================================================================
# 第 2 题：条件筛选
# ===========================================================================
def count_extreme(r: pd.Series, k: float = 3.0) -> int:
    """答案要点：
    标准化 -> 取绝对值 -> 布尔比较 -> 求和

    (z.abs() > k) 得到布尔序列；(布尔序列).sum() 把 True 当 1 求和，
    所以结果就是"满足条件的天数"。想要比例就用 .mean()。

    常见错误：
      - 用了 r.std() 默认 ddof=1 而标准化时又用了 ddof=0，导致阈值不一致
      - 写成 (z > k).sum()，漏了负方向（暴涨也算极端，所以要取 abs）
    """
    z = (r - r.mean()) / r.std(ddof=1)
    return int((z.abs() > k).sum())


# ===========================================================================
# 第 3 题：时间索引与重采样
# ===========================================================================
def yearly_vol(r: pd.Series, freq: int = 244) -> pd.Series:
    """答案要点：
    r.index 是日期索引 -> r.index.year 取出年份（int）
    groupby(年份).std() 得到"每年的日标准差"
    再乘 sqrt(244) 才是年化波动

    为什么不能写成 r.resample("YE").std()？
      因为 resample 到"年"之后，每组的样本只剩 1 个点（年末那个值），
      对 1 个点求标准差是 NaN。必须先把日收益按年份分组。

    常见错误：算出日标准差就当成年化波动（差了 15.6 倍）。
    """
    return r.groupby(r.index.year).std() * np.sqrt(freq)


def monthly_return(close: pd.Series) -> pd.Series:
    """答案要点：
    resample("ME")  按月分组，ME = month end（月末）
    .last()         每组取最后一个值 = 当月最后一个交易日的收盘价
    .pct_change()   相邻两个月环比 = 月收益率

    注意 pandas 版本：
      旧版写 "M"，新版（pandas 2.2+）写 "ME"，写 "M" 会告警。
    """
    return close.resample("ME").last().pct_change()


# ===========================================================================
# 第 4 题：横截面标准化（重点题）
# ===========================================================================
def make_panel(n_stock: int = 20, seed: int = 42) -> pd.DataFrame:
    close = load_index()
    dates = close.index
    rng = np.random.default_rng(seed)
    frames = [
        pd.DataFrame({
            "date": dates,
            "code": f"S{i:02d}",
            "factor": rng.normal(i * 0.1, 1.0, len(dates)),
        })
        for i in range(n_stock)
    ]
    return pd.concat(frames, ignore_index=True)


def cs_zscore(panel: pd.DataFrame) -> pd.DataFrame:
    """答案要点（Day 2 最重要的一条）：

      out = panel.copy()
      out["z"] = out.groupby("date")["factor"].transform(
                     lambda s: (s - s.mean()) / s.std(ddof=0))

    关键在 transform：
      - agg  -> 每个组返回"一个值"，结果长度 = 组数，没法填回原表
      - transform -> 每个组返回"与原组等长"的序列，正好填回每一行

    为什么用 ddof=0（总体标准差）：
      标准化公式 (x - μ) / σ 里的 σ 是总体标准差；
      用 ddof=1 会得到 std = 1.2247（当每组只有 3 个样本时），
      校验时就会觉得"没标准化成功"。

    常见错误：
      - 忘了 groupby("date")：那就变成"全样本标准化"，横截面信息就没了
      - 用 agg 回填：报长度不匹配
      - lambda 里返回标量：transform 报错
    """
    out = panel.copy()
    out["z"] = out.groupby("date")["factor"].transform(
        lambda s: (s - s.mean()) / s.std(ddof=0)
    )
    return out


def rank_pct(panel: pd.DataFrame) -> pd.DataFrame:
    """答案要点：
      out["rank_pct"] = out.groupby("date")["factor"].rank(pct=True)

    rank(pct=True) 返回 0~1 的百分位排名。
    这是分层回测的输入：排名前 20% 进 Q5，后 20% 进 Q1。

    常见错误：忘了 groupby，"全样本排名"在面板数据里没有意义。
    """
    out = panel.copy()
    out["rank_pct"] = out.groupby("date")["factor"].rank(pct=True)
    return out


# ===========================================================================
# 第 5 题：分组聚合
# ===========================================================================
def code_stats(panel: pd.DataFrame) -> pd.DataFrame:
    """答案要点：
      return panel.groupby("code")["factor"].agg(["mean", "std"])

    agg(["mean","std"]) 一次算多个统计量，自动生成同名的两列。
    std 默认 ddof=1（样本标准差），金融里通常就用这个。

    常见错误：
      - groupby("code")["factor"] 之后又写 ["factor"]，会 KeyError
      - 忘了 agg，直接 .mean() 只得到一列
    """
    return panel.groupby("code")["factor"].agg(["mean", "std"])


# ===========================================================================
# 直观对比：agg vs transform（打印出来一眼就懂）
# ===========================================================================
def demo_agg_vs_transform() -> None:
    print("\n" + "=" * 70)
    print("附：agg 与 transform 的区别（拿 3 行数据看最清楚）")
    print("=" * 70)
    small = pd.DataFrame({
        "date": ["D1", "D1", "D1", "D2", "D2", "D2"],
        "factor": [1.0, 2.0, 3.0, 10.0, 20.0, 30.0],
    })
    print("原始数据：")
    print(small.to_string(index=False))
    print("\nagg（每个组压缩成一个值，长度=组数=2）:")
    print(small.groupby("date")["factor"].agg(["mean", "std"]).round(4).to_string())
    print("\ntransform（每组返回等长结果，长度=原表=6，可回填）:")
    small["z"] = small.groupby("date")["factor"].transform(
        lambda s: (s - s.mean()) / s.std(ddof=0)
    )
    print(small.round(4).to_string(index=False))
    print("\n看第 1 组：均值 2，标准差 0.8165；")
    print("  (1-2)/0.8165 = -1.2247    (3-2)/0.8165 = +1.2247")
    print("  三个 z 的平方和 = 0 + 1.5 + 1.5 = 3，除以 n=3 得 1，开方 = 1 ✓")


# ===========================================================================
def main() -> int:
    close = load_index()
    print(f"[0] 行数 {len(close)}，区间 {close.index.min():%Y-%m-%d} ~ {close.index.max():%Y-%m-%d}")

    df = pd.read_parquet(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    feat = add_features(df)
    print("\n[1] 派生列（最后 3 行）:")
    print(feat[["date", "close", "ret", "log_ret", "amp", "ma20", "vol20"]].tail(3).round(6).to_string(index=False))
    print("    知识点：ret 第 1 行必为 NaN（没有前一天）→ 差分/滚动都会产生 NaN，正常")
    print("    又一个坑：feat 的索引是 0,1,2...（reset_index 之后丢了日期），")
    print("              所以下面要先把 date 设为索引，否则 r.index.year 会报 AttributeError")

    # 关键一步：把日期设为索引，才能按年份分组
    feat = feat.set_index("date")
    r = feat["log_ret"].dropna()
    print(f"\n[2] |z|>3 的天数: {count_extreme(r, 3)}   |z|>5: {count_extreme(r, 5)}")
    print(f"    占全部 {len(r)} 天的比例: {count_extreme(r,3)/len(r):.4%}（正态理论 0.27%）")

    print("\n[3] 按年年化波动（最后 3 年）:")
    print(yearly_vol(r).tail(3).round(4).to_string())
    print("\n[3] 最近 3 个月收益率:")
    print(monthly_return(close).tail(3).round(4).to_string())

    panel = make_panel()
    print(f"\n[4] 面板: {panel.shape[0]} 行 × {panel['code'].nunique()} 只股票")
    z = cs_zscore(panel)
    chk = z.groupby("date")["z"].agg(["mean", lambda s: s.std(ddof=0)])
    chk.columns = ["mean", "std(ddof=0)"]
    print("[4] 每日横截面 z 的统计（应 mean≈0、std=1）:")
    print(chk.tail(2).round(8).to_string())
    rk = rank_pct(panel)
    print("[4] rank_pct 每日最小值/最大值（20 只股票，min 应为 1/20=0.05，max=1）:")
    print(rk.groupby("date")["rank_pct"].agg(["min", "max"]).tail(2).to_string())

    print("\n[5] 每只股票的 factor 统计（前 3 行）:")
    print(code_stats(panel).head(3).round(3).to_string())
    print("    造数据时第 i 只股票均值设为 i*0.1，所以 S00≈0、S01≈0.1、S02≈0.2 ✓")

    demo_agg_vs_transform()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
