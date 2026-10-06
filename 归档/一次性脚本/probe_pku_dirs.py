# -*- coding: utf-8 -*-
"""扫描北大数院及其他高校公开主页上的中文概率/测度论讲义。"""
import os
import re
import urllib.parse
import urllib.request
import concurrent.futures as cf

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

DIRS = [
    "https://www.math.pku.edu.cn/teachers/liuyong/",
    "https://www.math.pku.edu.cn/teachers/liuyong/asa/",
    "https://www.math.pku.edu.cn/teachers/",
]

# 常见中文概率讲义可能路径（用于确认公开可下载）
GUESS = [
    "https://www.math.pku.edu.cn/teachers/liuyong/prob/lectnote.pdf",
    "https://www.math.pku.edu.cn/teachers/liuyong/probability/lectnote.pdf",
]


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), resp.headers.get("Content-Type", "")


for d in DIRS:
    print(f"\n=== {d}")
    try:
        data, ctype = fetch(d)
        text = data.decode("utf-8", "ignore")
        links = sorted(set(re.findall(r'href="([^"#?]+)"', text, flags=re.I)))
        for link in links:
            low = link.lower()
            if any(k in low for k in ["pdf", "prob", "lect", "note", "asa", "measure", "stoch"]):
                print("   ", urllib.parse.urljoin(d, link))
        print(f"    （共 {len(links)} 个链接，已筛选）")
    except Exception as exc:  # noqa: BLE001
        print(f"    ERR {type(exc).__name__}: {exc}")

print("\n=== 猜测路径探测")
for url in GUESS:
    try:
        data, ctype = fetch(url)
        ok = data[:4] == b"%PDF"
        print(f"  {'OK' if ok else 'NOT-PDF'} {len(data)//1024}KB {url}")
    except Exception as exc:  # noqa: BLE001
        print(f"  ERR {type(exc).__name__} {url}")
