# -*- coding: utf-8 -*-
"""环境自检：确认 Python、依赖包、matplotlib 出图、数据源是否正常。

用法（在项目根目录下）：
    python src/check_env.py

它会做四件事：
1. 打印 Python 版本与解释器路径
2. 逐个检查依赖包是否安装，缺哪个就告诉你装什么
3. 用 matplotlib 画一张图并保存到 reports/figs/_env_check.png（能出图才算真的装好）
4. 尝试联网拉一小段沪深300数据，确认数据源可用
"""
from __future__ import annotations

import os
import sys

sys.stdout.reconfigure(encoding="utf-8")  # 避免中文在 PowerShell 里乱码

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 需要检查的包：包名 -> pip 安装名
DEPS = {
    "numpy": "numpy",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "scipy": "scipy",
    "sklearn": "scikit-learn",
    "statsmodels": "statsmodels",
    "pyarrow": "pyarrow",
    "akshare": "akshare",
    "baostock": "baostock",
}
# 这些是"必须有"的，缺一个图都画不出来
REQUIRED = {"numpy", "pandas", "matplotlib"}

OK = "[OK]"
NO = "[缺失]"


def check_python() -> None:
    print("=" * 62)
    print("1) Python 环境")
    print(f"   版本     : {sys.version.split()[0]}")
    print(f"   解释器   : {sys.executable}")
    print(f"   工作目录 : {os.getcwd()}")
    if sys.version_info < (3, 9):
        print("   [警告] 版本过低，建议 3.10 以上（matplotlib 新版需要）")


def check_deps() -> list[str]:
    import importlib
    import importlib.metadata as md

    print("=" * 62)
    print("2) 依赖包检查")
    missing_required, missing_optional = [], []
    for mod, pip_name in DEPS.items():
        try:
            importlib.import_module(mod)
            try:
                ver = md.version(pip_name)
            except Exception:  # noqa: BLE001
                ver = "已安装"
            print(f"   {OK:6} {mod:12} {ver}")
        except Exception:  # noqa: BLE001
            print(f"   {NO:6} {mod:12} -> 安装命令: pip install {pip_name}")
            (missing_required if mod in REQUIRED else missing_optional).append(pip_name)

    if missing_optional:
        print("\n   一条命令补齐所有缺失的包：")
        print(f"   pip install {' '.join(missing_optional)}")
    return missing_required


def check_plot() -> bool:
    print("=" * 62)
    print("3) matplotlib 出图测试")
    try:
        import matplotlib
        matplotlib.use("Agg")  # 不弹窗，直接存文件
        import matplotlib.pyplot as plt
        import numpy as np

        # 中文支持：Windows 自带微软雅黑
        for font in ["Microsoft YaHei", "SimHei"]:
            try:
                from matplotlib import font_manager

                font_manager.findfont(font, fallback_to_default=False)
                matplotlib.rcParams["font.sans-serif"] = [font]
                matplotlib.rcParams["axes.unicode_minus"] = False
                break
            except Exception:  # noqa: BLE001
                continue

        rng = np.random.default_rng(42)
        x = np.linspace(0, 10, 200)
        y = np.sin(x) + 0.1 * rng.normal(size=200)

        fig, ax = plt.subplots(figsize=(7, 3.6), dpi=130)
        ax.plot(x, y, label="sin(x) + 噪声")
        ax.set_title("matplotlib 出图测试：如果你看到这张图，环境就是好的")
        ax.legend()
        fig.tight_layout()

        out_dir = os.path.join(ROOT, "reports", "figs")
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "_env_check.png")
        fig.savefig(path)
        plt.close(fig)
        print(f"   {OK} 已生成图片: {path}")
        print(f"   matplotlib 版本: {matplotlib.__version__}")
        print("   打开这张图看看，能显示就说明 matplotlib 完全可用")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"   [失败] {type(exc).__name__}: {exc}")
        print("   处理办法：pip install --upgrade matplotlib")
        return False


def check_data() -> bool:
    print("=" * 62)
    print("4) 数据源测试（拉最近 5 个交易日的沪深300）")
    try:
        import akshare as ak

        df = ak.stock_zh_index_daily(symbol="sh000300")
        print(f"   {OK} akshare 正常，共 {len(df)} 行，最后 3 天：")
        print(df.tail(3).to_string(index=False))
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"   [失败] akshare: {type(exc).__name__}: {exc}")
        print("   备选：改用 baostock（pip install baostock），或直接手动下载 CSV")
        return False


def main() -> int:
    check_python()
    missing_required = check_deps()
    if missing_required:
        print("\n   [重要] 以下必需包缺失，先安装再继续：")
        print(f"   pip install {' '.join(missing_required)}")
        return 1
    ok_plot = check_plot()
    check_data()
    print("=" * 62)
    print("结论：" + ("环境可用，可以开始 Day 1" if ok_plot else "matplotlib 有问题，先修好再继续"))
    return 0 if ok_plot else 1


if __name__ == "__main__":
    raise SystemExit(main())
