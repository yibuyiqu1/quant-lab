"""
01 · 拉取 A 股日线数据（前复权）

用法:
    python src/01_fetch_data.py

输出:
    data/daily.parquet   若没有 pyarrow 则自动回退为 data/daily.csv

说明:
    - 这里用 30 只高流动性蓝筹做示例股票池，目的是「零依赖跑通流程」。
      真正做研究时请扩展到沪深300 / 中证500 / 全市场，并剔除 ST、停牌、
      上市不足 60 日的样本 —— 30 只样本的统计结论没有意义。
    - akshare 接口偶有变动。若报错，先 `pip install -U akshare` 再重试；
      仍失败则对照 https://github.com/akfamily/akshare 的文档改字段名。
"""
from pathlib import Path
import time

import pandas as pd
import akshare as ak

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data"
OUT_DIR.mkdir(exist_ok=True)

START, END = "20200101", "20260925"

# 示例股票池：30 只高流动性蓝筹（代码均为常见 A 股代码）
UNIVERSE = [
    "600519", "000858", "601318", "600036", "000001", "601899", "600900",
    "000333", "002594", "600030", "601012", "600276", "000651", "601888",
    "603288", "600887", "600104", "601166", "600000", "000002", "601398",
    "601988", "600028", "601857", "600585", "002415", "000725", "600309",
    "601601", "600019",
]

RENAME = {
    "日期": "date", "股票代码": "code", "开盘": "open", "收盘": "close",
    "最高": "high", "最低": "low", "成交量": "volume", "成交额": "amount",
}


def fetch_one(code: str) -> pd.DataFrame | None:
    """拉单只股票的前复权日线。失败返回 None，不中断整体流程。"""
    try:
        df = ak.stock_zh_a_hist(
            symbol=code, period="daily",
            start_date=START, end_date=END, adjust="qfq",
        )
    except Exception as e:  # 接口抖动 / 网络问题
        print(f"  [FAIL] {code}: {e}")
        return None

    df = df.rename(columns=RENAME)
    keep = ["date", "code", "open", "high", "low", "close", "volume", "amount"]
    missing = [c for c in keep if c not in df.columns]
    if missing:
        print(f"  [SKIP] {code}: 缺少字段 {missing}，请检查 akshare 版本")
        return None

    df = df[keep].copy()
    df["date"] = pd.to_datetime(df["date"])
    return df


def main() -> None:
    frames = []
    for i, code in enumerate(UNIVERSE, 1):
        print(f"[{i:2d}/{len(UNIVERSE)}] fetching {code} ...")
        df = fetch_one(code)
        if df is not None and not df.empty:
            frames.append(df)
        time.sleep(0.3)  # 温和一点，避免被限流

    if not frames:
        raise SystemExit("没有拉到任何数据，请检查网络或 akshare 版本。")

    daily = (
        pd.concat(frames, ignore_index=True)
        .sort_values(["code", "date"])
        .reset_index(drop=True)
    )

    # 落盘：优先 parquet（体积小、类型稳定），无 pyarrow 则回退 csv
    parquet_path = OUT_DIR / "daily.parquet"
    try:
        daily.to_parquet(parquet_path, index=False)
        target = parquet_path
    except Exception:
        target = OUT_DIR / "daily.csv"
        daily.to_csv(target, index=False)

    print("\n" + "=" * 56)
    print(f"股票数      : {daily['code'].nunique()}")
    print(f"交易日区间  : {daily['date'].min().date()} ~ {daily['date'].max().date()}")
    print(f"总行数      : {len(daily):,}")
    print(f"已保存到    : {target}")
    print("=" * 56)


if __name__ == "__main__":
    main()
