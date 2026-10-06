import json                    
import math                   
import os                      
import sys                    

import numpy as np            
import pandas as pd 
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "clean", "hs300.parquet")
SEED = 42
ANNUAL = 244

def log_returns(close: pd.Series):
    return np.log(close.astype(float)).diff()


def annualized_stats(r:pd.Series,freq: int = ANNUAL):
    r= r.dropna()
    nav = (1+r).cumprod()
    years = len(r)/freq
    ann_ret = nav.iloc[-1]**(1/years) - 1
    ann_vol = r.std(ddof = 1)*math.sqrt(freq)

    # 注意：字典用「冒号」分隔键和值；用逗号会变成 set（集合），无法用 ["键"] 取值
    return {"年化收益": float(ann_ret), "年化波动": float(ann_vol)}

def max_drawdown(r:pd.Series):
    r = r.fillna(0)
    nav = (1+r).cumprod()
    dd = nav/nav.cummax() -1 
    return float(dd.min())
def normal_cdf(x :float) ->float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))
def tail_ratio(r:pd.Series,k:float = 3.0):
    r = r.dropna()
    z = (r - r.mean())/r.std(ddof = 1)
    actual = float((z.abs()>k).mean())
    theo = float(2*(1 - normal_cdf(k)))
    return {"实际":actual,"正态理论":theo ,"倍数":actual/theo if theo else float("nan") }




def load_close():
    df = pd.read_parquet(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").set_index("date")["close"]


def setup_chinese_font() -> bool:
    """让 matplotlib 能显示中文。成功返回 True，找不到字体返回 False。

    不设的话，图里所有中文会变成一个个方框（豆腐块）。
    """
    import matplotlib
    from matplotlib import font_manager

    # 按优先级尝试微软雅黑、黑体、思源黑体
    for name in ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC"]:
        try:
            # findfont(名字, fallback_to_default=False)
            #   找一个真实的字体文件；fallback_to_default=False 表示"找不到就报错"
            #   报错正好被 except 捕获，于是我们继续试下一个字体名
            font_manager.findfont(name, fallback_to_default=False)

            # 设置全局默认字体族
            matplotlib.rcParams["font.sans-serif"] = [name]
            # 让负号正常显示（否则 -0.05 的减号也会变方框）
            matplotlib.rcParams["axes.unicode_minus"] = False
            return True
        except Exception:      # 找不到这个字体就换下一个，不算错误
            continue
    return False


def plot_three(r:pd.Seriers,out_rel:str = "reports/figs/d01_lesson.png"):
    import matplotlib
    matplotlib.use("Agg")

    import matplotlib.pyplot as plt

    mu = float(r.mean)
    sigma = float(r.std(off=1))

    fake = np.random.default_rng(SEED).normal(mu,sigma,len(r))

    fig,axes = plt.subplots(1,3,figsize= (16,4.4),dpi = 130)

    axes[0].hist(r, bins=120, density=True, alpha=0.75, label="HS300 日对数收益")
    # np.linspace(起点, 终点, 个数) 生成等间距的横坐标，用来画平滑曲线
    xs = np.linspace(r.min(), r.max(), 400)
    # 手写正态密度函数（不调 scipy，看清楚公式）
    pdf = np.exp(-((xs - mu) ** 2) / (2 * sigma ** 2)) / (sigma * math.sqrt(2 * math.pi))
    axes[0].plot(xs, pdf, "r-", lw=1.6, label="同均值方差正态")
    # 纵轴取对数：正态的尾部会衰减到 1e-5 量级，不取对数根本看不出尾部差异
    axes[0].set_yscale("log")
    axes[0].set_title("分布（对数纵轴）vs 正态")
    axes[0].legend(fontsize=8)      # 显示图例，字号调小一点

    # --- 图 2：Q-Q 图 ---
    # 横轴是正态分位数，纵轴是实际分位数。
    # 若数据真的正态，点会落在 45° 红线上；两端翘起 = 肥尾。
    axes[1].plot(fake, np.sort(r.values), ".", ms=1.5)
    lim = [min(fake.min(), r.min()), max(fake.max(), r.max())]
    axes[1].plot(lim, lim, "r--", lw=1)      # 参考线（虚线）
    axes[1].set_title("Q-Q 图：两端偏离")

    # --- 图 3：净值与历史高点 ---
    nav = (1 + r).cumprod()
    axes[2].plot(nav.index, nav.values, lw=1.2, label="净值")
    axes[2].plot(nav.index, nav.cummax().values, ls="--", lw=0.8, color="grey", label="历史高点")
    axes[2].set_title("净值与历史高点")
    axes[2].legend(fontsize=8)

    # tight_layout() 自动调整子图间距，避免标题/坐标轴被裁掉
    fig.tight_layout()

    path = os.path.join(ROOT, out_rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # savefig 存文件；plt.close(fig) 释放内存（批量画图时不关会越画越慢）
    fig.savefig(path)
    plt.close(fig)
    return path


def main():
    font_ok = setup_chinese_font()
    print("中文字体:", "已设置" if font_ok else "未找到，图内中文会变方框")

    close = load_close()
    r = log_returns(close).dropna()
    st = annualized_stats(r)
    res = {
        "样本天数": int(len(r)),
        "样本区间": f"{r.index.min():%Y-%m-%d} ~ {r.index.max():%Y-%m-%d}",
        "年化收益": round(st["年化收益"], 4),
        "年化波动": round(st["年化波动"], 4),
        "夏普(0利率)": round(st["年化收益"] / st["年化波动"], 3),
        "最大回撤": round(max_drawdown(r), 4),
        "偏度": round(float(r.skew()), 3),
        # .kurt() 返回"超额峰度"（正态为 0），+3 才是通常说的峰度（正态为 3）
        "峰度(原始)": round(float(r.kurt() + 3), 3),
        # (r > 0).mean() 布尔序列求均值 = 上涨天数占比
        "日胜率": round(float((r > 0).mean()), 4),
        # 3 倍与 5 倍标准差的尾部概率对比（5 倍时正态几乎不可能发生）
        "|z|>3": {k: round(v, 6) for k, v in tail_ratio(r, 3).items()},
        "|z|>5": {k: round(v, 6) for k, v in tail_ratio(r, 5).items()},
        "可复现性": f"固定种子 SEED={SEED}",

        
    }

    print("=" * 58)
    for k, v in res.items():
        # f-string 的 {:12} 表示这个字段占 12 个字符宽度，左对齐 → 输出整齐
        print(f"{k:14}: {v}")

    # 4.5 输出"三句话结论"——这是研究报告的雏形
    print("=" * 58)
    print("三句话结论（抄进 docs/d01.md）:")
    print(f"  1. 沪深300 日对数收益峰度 {res['峰度(原始)']}，正态应为 3 —— 尖峰肥尾。")
    print(f"  2. |z|>3 实际占比 {res['|z|>3']['实际']:.4%}，是正态理论 "
          f"{res['|z|>3']['正态理论']:.4%} 的 {res['|z|>3']['倍数']:.1f} 倍。")
    print("  3. 因此后续因子检验不能假设正态，要用 bootstrap 或稳健统计量。")


    fig = plot_three(r)
    out_dir = os.path.join(ROOT, "reports")
    os.makedirs(out_dir, exist_ok=True)
    # open(路径, "w", encoding="utf-8") 写文本文件；
    # json.dump(对象, 文件, ensure_ascii=False 保留中文, indent=2 缩进美化)
    with open(os.path.join(out_dir, "d01_lesson.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=2)

    print("图  ->", fig)
    print("数据->", os.path.join(out_dir, "d01_lesson.json"))

    a = np.random.default_rng(SEED).normal(size=3)
    b = np.random.default_rng(SEED).normal(size=3)
    assert np.array_equal(a, b), "随机种子失效！"
    print("可复现性自检: 通过")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())