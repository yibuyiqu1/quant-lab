# -*- coding: utf-8 -*-
"""补齐下载：ESL/ISLR/中文深度学习/概率ML 等失效源的可用镜像。"""
import os
import re
import time
import urllib.request
import concurrent.futures as cf

ROOT = r"E:\AI结果\量化\资料库"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
MAX_BYTES = 350 * 1024 * 1024

ITEMS = [
    ("03-统计与机器学习", "统计学习基础-ESL-中文版.pdf",
     ["https://raw.githubusercontent.com/szcf-weiya/ESL-CN/master/docs/The%20Elements%20of%20Statistical%20Learning(8.1).pdf"],
     "ESL 中文翻译（ESL-CN 开源项目，第 8.1 版）"),
    ("03-统计与机器学习", "统计学习基础-ESL-CN-SVD补充.pdf",
     ["https://raw.githubusercontent.com/szcf-weiya/ESL-CN/master/docs/SVD.pdf"],
     "ESL-CN 项目 SVD 专题补充材料"),
    ("03-统计与机器学习", "神经网络与深度学习-邱锡鹏-v2.pdf",
     ["https://github.com/nndl/nndl/releases/download/book-pdf/nndl-v2.pdf"],
     "邱锡鹏《神经网络与深度学习》v2（作者官方发布）"),
    ("03-统计与机器学习", "南瓜书-机器学习公式详解-v2.pdf",
     ["https://github.com/datawhalechina/pumpkin-book/releases/download/v2.0.0/pumpkin_book.pdf"],
     "Datawhale 南瓜书 v2（西瓜书公式推导）"),
    ("03-统计与机器学习", "概率机器学习-ProbML-Book1.pdf",
     ["https://github.com/probml/pml-book/releases/download/2025-04-18/book1.pdf"],
     "Murphy《Probabilistic Machine Learning: An Introduction》官方免费版"),
    ("03-统计与机器学习", "统计学习基础-ESL-CMU镜像.pdf",
     ["https://www.stat.cmu.edu/~brian/valerie/617-2022/0%20-%20books/ESLII.pdf",
      "https://www.stat.cmu.edu/~brian/valerie/617-2022/0%20-%20books/The%20Elements%20of%20Statistical%20Learning.pdf",
      "https://hastie.su.domains/Papers/ESLII.pdf"],
     "ESL 英文原版（CMU 课程镜像站）"),
    ("03-统计与机器学习", "统计学习导论-ISLR2-镜像.pdf",
     ["https://www.stat.cmu.edu/~brian/valerie/617-2022/0%20-%20books/ISLRv2_website.pdf",
      "https://hastie.su.domains/ISLR2/ISLRv2_website.pdf"],
     "ISLR2 英文原版（CMU 课程镜像站）"),
    ("03-统计与机器学习", "CMU-统计书籍目录.html",
     ["https://www.stat.cmu.edu/~brian/valerie/617-2022/0%20-%20books/?C=D;O=D"],
     "CMU 课程公开书籍目录（可继续挖掘其他统计教材）"),
]


def looks_valid(head, ctype):
    if head[:4] == b"%PDF":
        return "PDF"
    low = ctype.lower()
    if ("html" in low or "text" in low) and len(head) > 1500:
        return "HTML/TEXT"
    return None


def grab(cat, name, urls, note):
    dest = os.path.join(ROOT, cat, name)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return ("已存在", os.path.getsize(dest) // 1024, "-", urls[0])
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                ctype = resp.headers.get("Content-Type", "")
                head = resp.read(65536)
                kind = looks_valid(head, ctype)
                if not kind:
                    print(f"  skip {name} ({ctype[:30]}) <- {url}", flush=True)
                    continue
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                total = len(head)
                with open(dest + ".part", "wb") as fh:
                    fh.write(head)
                    while True:
                        chunk = resp.read(262144)
                        if not chunk:
                            break
                        total += len(chunk)
                        if total > MAX_BYTES:
                            raise RuntimeError("超限")
                        fh.write(chunk)
                os.replace(dest + ".part", dest)
                return ("成功", total // 1024, kind, resp.geturl())
        except Exception as exc:  # noqa: BLE001
            print(f"  fail {name}: {type(exc).__name__} {exc} <- {url}", flush=True)
            if os.path.exists(dest + ".part"):
                os.remove(dest + ".part")
        time.sleep(0.3)
    return ("失败", 0, "-", urls[0])


with cf.ThreadPoolExecutor(max_workers=4) as pool:
    results = [f.result() for f in [pool.submit(grab, *it) for it in ITEMS]]

for it, res in zip(ITEMS, results):
    print(f"{res[0]:4} {res[1]:>8}KB {res[2]:9} {it[1]}", flush=True)
