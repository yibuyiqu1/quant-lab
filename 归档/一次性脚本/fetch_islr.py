# -*- coding: utf-8 -*-
"""最后一本：ISLR2（走 GitHub 镜像；上游 hastie.su.domains 在本机不可达）。"""
import os
import time
import urllib.request

ROOT = r"E:\AI结果\量化\资料库\03-统计与机器学习"
DEST = os.path.join(ROOT, "统计学习导论-ISLR2.pdf")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

CANDIDATES = []
for m in ["https://ghproxy.net/", "https://gh-proxy.com/", "https://ghfast.top/", ""]:
    CANDIDATES += [
        m + "https://raw.githubusercontent.com/szcf-weiya/ISLR-CN/master/docs/ISLRv2_website.pdf",
        m + "https://github.com/szcf-weiya/ISLR-CN/raw/master/docs/ISLRv2_website.pdf",
    ]

for url in CANDIDATES:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
        with urllib.request.urlopen(req, timeout=45) as resp:
            head = resp.read(65536)
            if head[:4] != b"%PDF":
                print("skip:", url[:90], flush=True)
                continue
            total = len(head)
            with open(DEST + ".part", "wb") as fh:
                fh.write(head)
                while True:
                    chunk = resp.read(262144)
                    if not chunk:
                        break
                    total += len(chunk)
                    fh.write(chunk)
            os.replace(DEST + ".part", DEST)
            print(f"OK ISLR2 {total//1024}KB  <- {url[:90]}", flush=True)
            break
    except Exception as exc:  # noqa: BLE001
        print(f"fail {type(exc).__name__} <- {url[:90]}", flush=True)
        if os.path.exists(DEST + ".part"):
            os.remove(DEST + ".part")
    time.sleep(0.3)
else:
    print("ISLR2 未取到，用 ESL 中文版 + ISLR 课程页替代即可", flush=True)

for fn in os.listdir(ROOT):
    if fn.endswith(".part"):
        os.remove(os.path.join(ROOT, fn))
        print("清理残留:", fn, flush=True)
