# -*- coding: utf-8 -*-
"""下载补充的中文公开讲义（全部来自高校公开课程主页）。"""
import os
import time
import urllib.parse
import urllib.request
import concurrent.futures as cf

ROOT = r"E:\AI结果\量化\资料库\06-中文概率与随机分析"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

ITEMS = [
    ("中科大-概率论习题课讲义（试用版）.pdf",
     "http://home.ustc.edu.cn/~zyx240014/article/Recitation%20of%20Probability.pdf",
     "中科大概率论习题课讲义：中文练习题与思路，配概率论基础学习"),
    ("中科大-概率论第4次习题课讲义.pdf",
     "http://home.ustc.edu.cn/~zyx240014/USTCProbability/files/Recitation4%20of%20Probability.pdf",
     "中科大概率论习题课（第 4 次）：条件分布与条件期望练习"),
    ("北大数院-应用随机分析-2024作业.pdf",
     "https://www.math.pku.edu.cn/teachers/liuyong/asa/hw24.pdf",
     "刘勇《应用随机分析》2024 版配套作业（含讲义的验证题）"),
    ("复旦-测度论与概率论专题讲义-性质与证明.pdf",
     "https://faculty.fudan.edu.cn/__local/A/D3/8D/8DB75E2C760CF5DD7E79A61B576_E3A91534_E2DE8.pdf",
     "复旦公开讲义：概率性质与证明（中文，补测度论细节）"),
    ("复旦-概率论专题讲义-条件数学期望.pdf",
     "https://faculty.fudan.edu.cn/__local/1/E3/17/33885FDA92C1773FAF783AD635A_15B27B01_11F1A1.pdf",
     "复旦公开讲义：从经典条件概率到条件数学期望的过渡"),
    ("复旦-概率论专题讲义-独立同分布.pdf",
     "https://faculty.fudan.edu.cn/__local/D/4A/B1/E3059D74554FD9FB1FA031271A8_96C48B34_E8B6D.pdf",
     "复旦公开讲义：独立同分布的直观与严格定义"),
]


def grab(name, url, note):
    dest = os.path.join(ROOT, name)
    if os.path.exists(dest) and os.path.getsize(dest) > 5000:
        return ("已存在", os.path.getsize(dest) // 1024, url)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        if data[:4] != b"%PDF" or len(data) < 5000:
            return ("非PDF/过小", len(data) // 1024, url)
        with open(dest, "wb") as fh:
            fh.write(data)
        return ("成功", len(data) // 1024, url)
    except Exception as exc:  # noqa: BLE001
        return (f"失败:{type(exc).__name__}", 0, url)


with cf.ThreadPoolExecutor(max_workers=3) as pool:
    results = [f.result() for f in [pool.submit(grab, *it) for it in ITEMS]]

for (name, url, note), (status, kb, _) in zip(ITEMS, results):
    print(f"{status:16} {kb:>6}KB  {name}", flush=True)
    time.sleep(0.1)

# 追加说明文件
readme = os.path.join(ROOT, "_本目录说明.md")
with open(readme, "w", encoding="utf-8") as fh:
    fh.write("# 中文概率与随机分析资料\n\n"
             "全部来自高校公开课程主页（北大数院、中科大、复旦），可自由用于学习。\n\n"
             "## 怎么用\n\n"
             "| 阶段 | 中文主线 | 英文对照 |\n|---|---|---|\n"
             "| D1–D21 概率地基 | 中科大习题课讲义（练手）+ 复旦专题讲义（条件期望、独立性） | Durrett 1–6 章 |\n"
             "| D22–D42 随机分析 | **北大刘勇《应用随机分析》2024 版讲义**（131 页，主教材）+ 作业 | MIT 18.S096、Shreve II |\n"
             "| 全程查证 | `_讲义目录索引.md` 定位节号 | — |\n\n"
             "## 注意\n\n"
             "- 刘勇讲义需要**测度论基础**（第 1 章压缩得比较快），D1–D21 的概率地基不能跳。\n"
             "- 商业教材（陈希孺、茆诗松、Shreve、Hull）未收录，请用图书馆或正版；\n"
             "  其中 Shreve II 有中文译本《连续时间金融》（中国人民大学出版社），图书馆通常有。\n")
print("saved:", readme, flush=True)
