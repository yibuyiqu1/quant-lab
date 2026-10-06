# -*- coding: utf-8 -*-
"""抓取北大数院公开挂在学院主页的中文讲义（应用随机分析等）。"""
import os
import re
import time
import urllib.request
import urllib.error
import concurrent.futures as cf

ROOT = r"E:\AI结果\量化\资料库\06-中文概率与随机分析"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# 已知存在的讲义（来自公开检索），以及常见序号扫描
KNOWN = [
    "https://www.math.pku.edu.cn/teachers/liuyong/asa/lectnote25-2.pdf",
    "https://www.math.pku.edu.cn/teachers/liuyong/asa/lectnote24.pdf",
]
SCAN_DIRS = [
    "https://www.math.pku.edu.cn/teachers/liuyong/asa/",
    "https://www.math.pku.edu.cn/teachers/liuyong/",
]
SCAN_PATTERNS = [
    "lectnote{n}.pdf", "lectnote25-{n}.pdf", "lectnote24-{n}.pdf", "lectnote23-{n}.pdf",
]


def get(url, timeout=30, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read() if binary else resp.read()
        return data, resp.headers.get("Content-Type", ""), resp.geturl()


def try_download(url, dest):
    try:
        data, ctype, final = get(url, timeout=60, binary=True)
        if data[:4] != b"%PDF" or len(data) < 20_000:
            return None
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as fh:
            fh.write(data)
        return len(data)
    except Exception:  # noqa: BLE001
        return None


def list_dir(url):
    try:
        data, ctype, _ = get(url)
        text = data.decode("utf-8", "ignore")
        links = set(re.findall(r'href="([^"#?]+\.pdf)"', text, flags=re.I))
        return sorted(links)
    except Exception as exc:  # noqa: BLE001
        print(f"  [dir fail] {url} -> {type(exc).__name__}", flush=True)
        return []


def main():
    os.makedirs(ROOT, exist_ok=True)
    found = {}

    print("=== 扫描目录", flush=True)
    for d in SCAN_DIRS:
        links = list_dir(d)
        print(f"  {d} -> {len(links)} 个 PDF", flush=True)
        for link in links:
            full = urllib.parse.urljoin(d, link)
            found[full] = os.path.basename(link)

    print("\n=== 探测已知与推测的讲义", flush=True)
    candidates = set(KNOWN)
    base = "https://www.math.pku.edu.cn/teachers/liuyong/asa/"
    for pat in SCAN_PATTERNS:
        for n in list(range(1, 31)) + ["25-1", "25-3", "24-1", "24-2", "26-1", "26-2"]:
            candidates.add(base + pat.format(n=n))
    candidates |= set(found.keys())

    def probe_one(url):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=25) as resp:
                head = resp.read(4096)
                if head[:4] == b"%PDF":
                    clen = resp.headers.get("Content-Length", "?")
                    return url, True, clen
        except Exception:  # noqa: BLE001
            pass
        return url, False, "0"

    with cf.ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(probe_one, sorted(candidates)))

    alive = [u for u, ok, _ in results if ok]
    print(f"  可用讲义 {len(alive)} 份", flush=True)
    for u in alive:
        print("   ", u, flush=True)

    print("\n=== 下载", flush=True)
    for url in alive:
        name = os.path.basename(url)
        cn = f"北大数院-应用随机分析讲义-{name}"
        dest = os.path.join(ROOT, cn)
        size = try_download(url, dest)
        print(f"  {'OK ' if size else 'FAIL'} {cn} {size or ''}", flush=True)
        time.sleep(0.2)


if __name__ == "__main__":
    import urllib.parse  # noqa: E402
    main()
