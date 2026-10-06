# -*- coding: utf-8 -*-
"""探测中文概率/随机分析讲义的可用来源（公开课程页与 PDF）。"""
import urllib.request
import urllib.error
import concurrent.futures as cf

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

URLS = [
    # 中国大学 MOOC / 课程页
    "https://www.icourse163.org/course/PKU-1002835007",
    "https://www.icourse163.org/course/USTC-1003491001",
    "https://www.icourse163.org/search.htm?search=%E6%A6%82%E7%8E%87%E8%AE%BA",
    # 高校公开讲义目录
    "https://www.math.pku.edu.cn/teachers/",
    "https://www.math.pku.edu.cn/kxyj/xzjl/index.htm",
    "http://www.stat.ustc.edu.cn/",
    "https://math.ecnu.edu.cn/~jypan/Teaching/",
    "https://math.ecnu.edu.cn/~jypan/Teaching/probability.html",
    "https://www.math.ecnu.edu.cn/",
    # 开源中文教材 / 讲义
    "https://raw.githubusercontent.com/datawhalechina/probability-theory-and-statistics/main/README.md",
    "https://github.com/datawhalechina/probability-theory-and-statistics",
    "https://raw.githubusercontent.com/apachecn/probability-and-statistics-zh/master/README.md",
    "https://github.com/apachecn/probability-and-statistics-zh",
    "https://raw.githubusercontent.com/Visualize-Probability/README/master/README.md",
    "https://github.com/GitHub-Dong/Probability-Theory",
    # 公开统计/概率中文讲义站点
    "https://esl-cn.readthedocs.io/",
    "https://esl-cn.readthedocs.io/zh/latest/",
    "https://www.cnblogs.com/",
    # 术语对照可用来源
    "https://zh.wikipedia.org/wiki/%E6%A6%82%E7%8E%87%E8%AE%BA",
    "https://en.wikipedia.org/wiki/Glossary_of_probability_and_statistics",
]


def probe(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            head = resp.read(2048)
            ctype = resp.headers.get("Content-Type", "")
            kind = "PDF" if head[:4] == b"%PDF" else ("TEXT" if len(head) > 500 else "?")
            return f"OK  {kind:5} {len(head):>6} {ctype[:32]:32} {url[:95]}"
    except urllib.error.HTTPError as exc:
        return f"HTTP{exc.code}  -     -      -                                {url[:95]}"
    except Exception as exc:  # noqa: BLE001
        return f"ERR:{type(exc).__name__[:14]:14} -     -      -                                {url[:95]}"


with cf.ThreadPoolExecutor(max_workers=8) as pool:
    for line in pool.map(probe, URLS):
        print(line, flush=True)
