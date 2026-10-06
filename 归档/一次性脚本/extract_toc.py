# -*- coding: utf-8 -*-
"""从北大数院中文讲义中抽取章节目录，生成阅读索引（精确到节号）。"""
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
from pypdf import PdfReader

SRC = r"E:\AI结果\量化\资料库\06-中文概率与随机分析"
OUT = r"E:\AI结果\量化\资料库\06-中文概率与随机分析\_讲义目录索引.md"

SEC = re.compile(r"^\s*(\d{1,2})(?:\.(\d{1,2})){0,2}\s*[.、]?\s*(\S.{0,60})$")

lines = ["# 北大数院《应用随机分析》讲义目录索引", "",
         "来源：刘勇 编著，北京大学数学科学学院（公开挂在学院教师主页）。",
         "用这份索引定位「某天要学的内容在第几节」，不必通读整本。", ""]

for path in sorted(glob.glob(os.path.join(SRC, "*lectnote*.pdf"))):
    name = os.path.basename(path)
    if any(k in name for k in ["CV", "marathon", "research"]):
        continue
    reader = PdfReader(path)
    found = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        for raw in text.split("\n"):
            raw = raw.strip()
            if not raw or len(raw) > 70:
                continue
            m = SEC.match(raw)
            if m and re.match(r"^[第\d]", raw):
                found.append((idx + 1, raw))
        if len(found) > 80:
            break
    lines += [f"## {name}", "", f"- 总页数：{len(reader.pages)}", ""]
    if found:
        lines += ["| 页码 | 节 |", "|---|---|"]
        seen = set()
        for pg, title in found:
            key = re.sub(r"\s+", "", title)
            if key in seen:
                continue
            seen.add(key)
            lines.append(f"| {pg} | {title} |")
    else:
        lines.append("（未抽到结构化目录，讲义为连续排版，按关键词检索即可）")
    lines.append("")
    print(f"{name}: 抽到 {len(found)} 条目录项")

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("saved:", OUT)
