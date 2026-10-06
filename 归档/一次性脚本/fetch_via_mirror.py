# -*- coding: utf-8 -*-
"""改用镜像站补齐 3 本大书：ESL 中文版 / 邱锡鹏深度学习 / ISLR2。

GitHub 直连在本机超时，改用常见公开镜像前缀重试；镜像不可用时回退直连。
"""
import os
import time
import urllib.request
import concurrent.futures as cf

ROOT = r"E:\AI结果\量化\资料库"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

MIRRORS = [
    "https://ghproxy.net/",
    "https://gh-proxy.com/",
    "https://ghfast.top/",
    "",
]

RAW = "https://raw.githubusercontent.com/szcf-weiya/ESL-CN/master/docs/The%20Elements%20of%20Statistical%20Learning(8.1).pdf"
NNDL = "https://github.com/nndl/nndl/releases/download/book-pdf/nndl-v2.pdf"
PML1 = "https://github.com/probml/pml-book/releases/download/2025-04-18/book1.pdf"
PUMPKIN = "https://github.com/datawhalechina/pumpkin-book/releases/download/v2.0.0/pumpkin_book.pdf"

ITEMS = [
    ("03-统计与机器学习", "统计学习基础-ESL-中文版.pdf", RAW, "ESL 中文翻译（ESL-CN 开源项目）"),
    ("03-统计与机器学习", "神经网络与深度学习-邱锡鹏-v2.pdf", NNDL, "邱锡鹏《神经网络与深度学习》v2（作者官方发布）"),
    ("03-统计与机器学习", "概率机器学习-ProbML-Book1.pdf", PML1, "Murphy 概率机器学习官方免费版"),
    ("03-统计与机器学习", "南瓜书-机器学习公式详解-v2.pdf", PUMPKIN, "Datawhale 南瓜书 v2"),
]


def grab(cat, name, url, note):
    dest = os.path.join(ROOT, cat, name)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return ("已存在", os.path.getsize(dest) // 1024, url)
    for prefix in MIRRORS:
        full = prefix + url if prefix else url
        try:
            req = urllib.request.Request(full, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                head = resp.read(65536)
                if head[:4] != b"%PDF":
                    print(f"  skip {name}: 非 PDF <- {full[:80]}", flush=True)
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
                        fh.write(chunk)
                os.replace(dest + ".part", dest)
                return ("成功", total // 1024, full)
        except Exception as exc:  # noqa: BLE001
            print(f"  fail {name}: {type(exc).__name__} <- {full[:80]}", flush=True)
            if os.path.exists(dest + ".part"):
                os.remove(dest + ".part")
        time.sleep(0.3)
    return ("失败", 0, url)


with cf.ThreadPoolExecutor(max_workers=2) as pool:
    results = [f.result() for f in [pool.submit(grab, *it) for it in ITEMS]]

for it, res in zip(ITEMS, results):
    print(f"{res[0]:5} {res[1]:>8}KB  {it[1]}", flush=True)

print("\n--- 资料库清点 ---")
for dirpath, _dirnames, filenames in os.walk(ROOT):
    for fn in sorted(filenames):
        p = os.path.join(dirpath, fn)
        rel = os.path.relpath(p, ROOT)
        print(f"{os.path.getsize(p)//1024:>8}KB  {rel}", flush=True)
