import os
import pandas as pd
import akshare as ak
import sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(ROOT,"data","raw","hs300.csv")
CLEAN_PATH = os.path.join(ROOT,"data","clean","hs300.parquet")
print(ROOT)
print(RAW_PATH)
print(CLEAN_PATH)

def main() -> None:
    os.makedirs(os.path.dirname(RAW_PATH),exist_ok = True)
    os.makedirs(os.path.dirname(CLEAN_PATH),exist_ok = True)

    print("\n 正在抓取沪深300日线")
    df = ak.stock_zh_index_daily(symbol = "sh000300")
    print(df.shape)
    print("列名：" ,list(df.columns))
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values('date').reset_index(drop = True)

    print(f"\n日期区间: {df['date'].min():%Y-%m-%d} ~ {df['date'].max():%Y-%m-%d}")
    print("每列缺失值个数:\n" + df.isna().sum().to_string())
    print("重复日期个数:", int(df["date"].duplicated().sum()))

    df.to_csv(RAW_PATH,index = False, encoding= 'utf-8-sig')
    print(f"\n已保存csv：{RAW_PATH}")

    df.to_parquet(CLEAN_PATH, index = False)
    print(f"\n已保存parquet：{CLEAN_PATH}")
    print("\n最后 3 行数据（确认最新日期）:")
    print(df.tail(3).to_string(index=False))





if __name__ == "__main__":
    main()