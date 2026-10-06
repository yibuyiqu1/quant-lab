# -*- coding: utf-8 -*-
"""最后补齐：ISLR2、Fama-French 因子研究相关材料、资料库总清单。"""
import os
import time
import urllib.request
import concurrent.futures as cf

ROOT = r"E:\AI结果\量化\资料库"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
MIRRORS = ["https://ghproxy.net/", "https://gh-proxy.com/", "https://ghfast.top/", ""]

ISLR_UPSTREAM = "https://github.com/szcf-weiya/ISLR-CN/releases"
ISLR_CANDIDATES = [
    "https://www.stat.cmu.edu/~brian/valerie/617-2022/0%20-%20books/ISLRv2_website.pdf",
    "https://hastie.su.domains/ISLR2/ISLRv2_website.pdf",
]

ITEMS = [
    ("03-统计与机器学习", "统计学习导论-ISLR2.pdf",
     ISLR_CANDIDATES + [m + "https://github.com/szcf-weiya/ISLR-CN/raw/master/docs/ISLRv2_website.pdf" for m in MIRRORS],
     "ISLR2 官方免费版（统计学习导论）"),
    ("04-金融与量化研究", "FamaFrench-因子数据说明.html",
     ["https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html"],
     "Kenneth French 官方因子数据库（A 股因子研究的对标基准，含三因子/五因子/动量数据）"),
    ("04-金融与量化研究", "中国A股指数与行业分类说明.html",
     ["http://www.csindex.com.cn/"],
     "中证指数公司官网（指数编制规则、行业分类、成分股名单的权威来源）"),
]


def grab(cat, name, urls, note):
    dest = os.path.join(ROOT, cat, name)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return ("已存在", os.path.getsize(dest) // 1024, urls[0])
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=90) as resp:
                ctype = resp.headers.get("Content-Type", "")
                head = resp.read(65536)
                ok_pdf = head[:4] == b"%PDF"
                ok_text = ("html" in ctype.lower() or "text" in ctype.lower()) and len(head) > 1200
                if not (ok_pdf or ok_text):
                    print(f"  skip {name} ({ctype[:30]}) <- {url[:70]}", flush=True)
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
                return ("成功", total // 1024, url)
        except Exception as exc:  # noqa: BLE001
            print(f"  fail {name}: {type(exc).__name__} <- {url[:70]}", flush=True)
            if os.path.exists(dest + ".part"):
                os.remove(dest + ".part")
        time.sleep(0.3)
    return ("失败", 0, urls[0])


with cf.ThreadPoolExecutor(max_workers=3) as pool:
    results = [f.result() for f in [pool.submit(grab, *it) for it in ITEMS]]
for it, res in zip(ITEMS, results):
    print(f"{res[0]:5} {res[1]:>8}KB  {it[1]}", flush=True)

# 清理残留 .part
for dirpath, _d, filenames in os.walk(ROOT):
    for fn in filenames:
        if fn.endswith(".part"):
            p = os.path.join(dirpath, fn)
            os.remove(p)
            print("清理残留:", fn, flush=True)

print("\n=== 资料库总清单 ===")
total_kb = 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames.sort()
    for fn in sorted(filenames):
        if fn.startswith("_"):
            continue
        p = os.path.join(dirpath, fn)
        kb = os.path.getsize(p) // 1024
        total_kb += kb
        print(f"{kb:>8}KB  {os.path.relpath(p, ROOT)}", flush=True)
print(f"\n合计 {total_kb/1024:.1f} MB", flush=True)
