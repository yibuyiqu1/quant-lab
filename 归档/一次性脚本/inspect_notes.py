# -*- coding: utf-8 -*-
"""提取中文讲义的前几页文字，用于核对内容覆盖范围。"""
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

from pypdf import PdfReader

OUT = r"E:\AI结果\量化\reports\_讲义内容抽样.json"
SRC = r"E:\AI结果\量化\资料库\06-中文概率与随机分析"

info = {}
for path in sorted(glob.glob(os.path.join(SRC, "*lectnote*.pdf"))):
    reader = PdfReader(path)
    pages = len(reader.pages)
    sample = "\n".join((reader.pages[i].extract_text() or "") for i in range(min(4, pages)))
    keywords = ["σ代数", "σ-代数", "可测", "条件期望", "鞅", "停时", "布朗运动", "伊藤", "Itô",
                "随机积分", "Girsanov", "马尔可夫", "随机微分方程", "测度", "期望"]
    hit = {k: sample.count(k) for k in keywords if sample.count(k) > 0}
    info[os.path.basename(path)] = {"页数": pages, "命中关键词": hit, "前400字": sample[:400]}
    print("=" * 70)
    print(os.path.basename(path), "| 页数", pages)
    print("命中:", hit)
    print(sample[:300].replace("\n", " "))

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(info, fh, ensure_ascii=False, indent=2)
print("\nsaved:", OUT)
