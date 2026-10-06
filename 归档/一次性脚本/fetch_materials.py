# -*- coding: utf-8 -*-
"""抓取公开/开放授权的量化学习资料（v2）。

改进：
- 跟随重定向（urllib 默认跟随 301/302）
- 校验内容：PDF 必须首字节为 %PDF，HTML 必须含 >2KB 正文
- 每条目多个候选 URL，按顺序回退
- 报告写入 TSV，便于复核
只抓取作者/机构公开发布或开源许可的材料，不抓盗版商业教材。
"""
import os
import re
import time
import urllib.error
import urllib.request
import concurrent.futures as cf

ROOT = r"E:\AI结果\量化\资料库"
REPORT = os.path.join(ROOT, "_下载报告.tsv")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
MAX_BYTES = 350 * 1024 * 1024
OCW = "https://ocw.mit.edu"

# (分类, 文件名, [候选URL...], 说明, 期望类型)
ITEMS = [
    ("01-数学地基", "MIT18.100A-实分析完整讲义.pdf",
     [f"{OCW}/courses/18-100a-real-analysis-fall-2020/mit18_100af20_lec_full.pdf"],
     "MIT 18.100A Real Analysis 完整讲义（测度与实分析前置）", "pdf"),
    ("01-数学地基", "凸优化-Boyd教材全文.pdf",
     ["https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf"],
     "Boyd《Convex Optimization》官方免费全文", "pdf"),
    ("01-数学地基", "凸优化习题集-官方附加题.pdf",
     ["https://raw.githubusercontent.com/cvxgrp/cvxbook_additional_exercises/main/additional_exercises.pdf"],
     "凸优化官方附加习题（建模训练）", "pdf"),
    ("01-数学地基", "斯坦福EE364a-凸优化课程页.html",
     ["https://web.stanford.edu/class/ee364a/lectures.html"],
     "Stanford EE364a 讲义索引页（含各讲 slide 链接）", "html"),
    ("01-数学地基", "MIT18.06-线性代数-Strange讲义索引.html",
     ["https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/pages/lecture-notes/",
      "https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/"],
     "MIT 18.06 线性代数讲义索引（矩阵分解/特征值）", "any"),

    ("02-概率与随机分析", "Durrett-概率论与实例-第5版作者公开稿.pdf",
     ["https://services.math.duke.edu/~rtd/PTE/PTE5_011119.pdf",
      "https://sites.math.duke.edu/~rtd/PTE/PTE5_011119.pdf"],
     "Durrett《Probability: Theory and Examples》作者主页公开稿（鞅/收敛定理标准参考）", "pdf"),
    ("02-概率与随机分析", "MIT18.175-概率论讲义索引.html",
     ["https://ocw.mit.edu/courses/18-175-theory-of-probability-spring-2014/pages/lecture-notes/",
      "https://ocw.mit.edu/courses/18-175-theory-of-probability-spring-2014/"],
     "MIT 18.175 Theory of Probability（高等概率论，配 Durrett）", "any"),
    ("02-概率与随机分析", "MIT18.S096-金融数学专题讲义索引.html",
     ["https://ocw.mit.edu/courses/18-s096-topics-in-mathematics-with-applications-in-finance-fall-2013/pages/lecture-notes/",
      "https://ocw.mit.edu/courses/18-s096-topics-in-mathematics-with-applications-in-finance-fall-2013/"],
     "MIT 18.S096 金融数学专题：Itô 公式、鞅表示、BS 推导（Shreve 体系的合法公开替代）", "any"),
    ("02-概率与随机分析", "MIT15.450-金融分析讲义索引.html",
     ["https://ocw.mit.edu/courses/15-450-analytics-of-finance-fall-2010/pages/lecture-notes/",
      "https://ocw.mit.edu/courses/15-450-analytics-of-finance-fall-2010/"],
     "MIT 15.450 Analytics of Finance（随机过程+蒙特卡洛+衍生品）", "any"),
    ("02-概率与随机分析", "MIT6.262-离散随机过程讲义索引.html",
     ["https://ocw.mit.edu/courses/6-262-discrete-stochastic-processes-spring-2011/pages/lecture-notes/",
      "https://ocw.mit.edu/courses/6-262-discrete-stochastic-processes-spring-2011/"],
     "离散随机过程（马尔可夫链/泊松过程）", "any"),
    ("02-概率与随机分析", "MIT6.041-概率系统分析讲义索引.html",
     ["https://ocw.mit.edu/courses/6-041-probabilistic-systems-analysis-and-applied-probability-fall-2010/pages/lecture-notes/",
      "https://ocw.mit.edu/courses/6-041-probabilistic-systems-analysis-and-applied-probability-fall-2010/"],
     "概率系统分析（条件期望/大数律/CLT 的工程化讲法）", "any"),
    ("02-概率与随机分析", "MIT18.05-概率统计导论课程页.html",
     [f"{OCW}/courses/18-05-introduction-to-probability-and-statistics-spring-2022/"],
     "MIT 18.05 概率统计导论（快速补基础）", "any"),

    ("03-统计与机器学习", "统计学习基础-ESL-官方免费版.pdf",
     ["https://hastie.su.domains/Papers/ESLII.pdf",
      "https://web.stanford.edu/~hastie/Papers/ESLII.pdf",
      "https://link.springer.com/content/pdf/10.1007/978-0-387-84858-7.pdf"],
     "Hastie《Elements of Statistical Learning》作者官网免费版", "pdf"),
    ("03-统计与机器学习", "统计学习导论-ISLR2.pdf",
     ["https://hastie.su.domains/ISLR2/ISLRv2_website.pdf",
      "https://www.statlearning.com/s/ISLRv2_website.pdf"],
     "ISLR2 官方免费版（统计学习地图）", "pdf"),
    ("03-统计与机器学习", "ESL中文版-ESL-CN.pdf",
     ["https://raw.githubusercontent.com/szcf-weiya/ESL-CN/master/docs/ESL-CN.pdf",
      "https://raw.githubusercontent.com/szcf-weiya/ESL-CN/master/docs/ESL-CN-2nd.pdf",
      "https://github.com/szcf-weiya/ESL-CN/releases"],
     "ESL 中文翻译（开源项目发布）", "any"),
    ("03-统计与机器学习", "神经网络与深度学习-邱锡鹏.pdf",
     ["https://raw.githubusercontent.com/nndl/nndl.github.io/master/nndl-book.pdf",
      "https://raw.githubusercontent.com/nndl/nndl.github.io/master/nndl-book-5.pdf",
      "https://github.com/nndl/nndl.github.io/releases"],
     "邱锡鹏《神经网络与深度学习》开源书（中文 DL 教材）", "any"),
    ("03-统计与机器学习", "南瓜书-机器学习公式详解.pdf",
     ["https://github.com/datawhalechina/pumpkin-book/releases",
      "https://raw.githubusercontent.com/datawhalechina/pumpkin-book/master/README.md"],
     "Datawhale 南瓜书（西瓜书公式推导配套，含 PDF 发布页）", "any"),
    ("03-统计与机器学习", "概率机器学习-ProbML-Book1发布页.html",
     ["https://github.com/probml/pml-book/releases",
      "https://probml.github.io/pml-book/book1.html"],
     "Murphy Probabilistic ML 官方免费书（发布页，含 PDF 下载）", "any"),
    ("03-统计与机器学习", "MIT18.650-应用统计讲义索引.html",
     ["https://ocw.mit.edu/courses/18-650-statistics-for-applications-fall-2016/pages/lecture-notes/",
      "https://ocw.mit.edu/courses/18-650-statistics-for-applications-fall-2016/"],
     "MIT 18.650 应用统计（假设检验/回归/渐近）", "any"),

    ("04-金融与量化研究", "AvellanedaStoikov2008-高频做市.pdf",
     ["https://www.math.nyu.edu/~avellane/HighFrequencyTrading.pdf",
      "https://math.nyu.edu/inmemoriam/avellaneda//HighFrequencyTrading.pdf"],
     "Avellaneda & Stoikov (2008) 高频做市与库存风险（微观结构必读）", "pdf"),
    ("04-金融与量化研究", "AlmgrenChriss2000-最优执行.pdf",
     ["https://www.smallake.kr/wp-content/uploads/2016/03/optliq.pdf"],
     "Almgren & Chriss 最优执行经典（交易成本建模）", "pdf"),
    ("04-金融与量化研究", "论文-深度学习时序综述-arXiv1609.02890.pdf",
     ["https://arxiv.org/pdf/1609.02890"],
     "arXiv 综述：深度学习在时间序列上的应用", "pdf"),
    ("04-金融与量化研究", "论文-金融NLP综述-arXiv2112.08534.pdf",
     ["https://arxiv.org/pdf/2112.08534"],
     "arXiv：金融领域 NLP 综述（另类数据方向参考）", "pdf"),
    ("04-金融与量化研究", "论文-量化交易机器学习综述-arXiv1905.01332.pdf",
     ["https://arxiv.org/pdf/1905.01332"],
     "arXiv：机器学习的量化交易综述", "pdf"),
    ("04-金融与量化研究", "JaneStreet-谜题存档.html",
     ["https://www.janestreet.com/puzzles/archive/"],
     "Jane Street 官方谜题存档（外资量化笔试题感训练）", "html"),
    ("04-金融与量化研究", "WorldQuant-BRAIN-因子平台.html",
     ["https://platform.worldquantbrain.com/"],
     "WorldQuant BRAIN 公开因子研究平台入口", "any"),

    ("05-中文公开资料", "北大数院-教学培养页.html",
     ["https://www.math.pku.edu.cn/",
      "https://www.math.pku.edu.cn/jxpy/"],
     "北大数院官网入口（课程与培养方案权威来源）", "any"),
    ("05-中文公开资料", "MIT-OCW-金融课程搜索页.html",
     [f"{OCW}/search/?q=finance"],
     "MIT OCW 金融类公开课索引（可持续挖掘）", "html"),
    ("05-中文公开资料", "GluonTS-概率时间序列库说明.md",
     ["https://raw.githubusercontent.com/awslabs/gluonts/master/README.md"],
     "GluonTS 官方说明（概率时序建模工具）", "any"),
]


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    return urllib.request.urlopen(req, timeout=timeout)


def looks_valid(head: bytes, ctype: str, want: str):
    if head[:4] == b"%PDF":
        return "pdf" if want in ("pdf", "any") else None, "PDF"
    low = ctype.lower()
    if "html" in low or head.lstrip()[:1] in (b"<", b"#"):
        if len(head) > 1500:
            return ("html" if want in ("html", "any") else None), "HTML/TEXT"
    if "text" in low and len(head) > 200:
        return ("html" if want in ("html", "any") else None), "TEXT"
    return None, "OTHER"


def grab(cat, name, urls, note, want):
    dest = os.path.join(ROOT, cat, name)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return ("已存在", os.path.getsize(dest) // 1024, "-", urls[0])
    for url in urls:
        try:
            with fetch(url) as resp:
                ctype = resp.headers.get("Content-Type", "")
                head = resp.read(65536)
                kind, label = looks_valid(head, ctype, want)
                if not kind:
                    print(f"  skip {name}: 内容不符 ({label}) <- {url}", flush=True)
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
                            raise RuntimeError("超过 350MB 上限")
                        fh.write(chunk)
                os.replace(dest + ".part", dest)
                return ("成功", total // 1024, label, resp.geturl())
        except Exception as exc:  # noqa: BLE001
            print(f"  fail {name}: {type(exc).__name__} {exc} <- {url}", flush=True)
            if os.path.exists(dest + ".part"):
                os.remove(dest + ".part")
        time.sleep(0.3)
    return ("失败", 0, "-", urls[0])


def main():
    os.makedirs(ROOT, exist_ok=True)
    rows = ["分类\t文件\t结果\t大小KB\t类型\t实际来源\t说明"]
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(grab, *item) for item in ITEMS]
        results = [f.result() for f in futures]
    for item, res in zip(ITEMS, results):
        cat, name, urls, note, _want = item
        status, kb, kind, src = res
        rows.append(f"{cat}\t{name}\t{status}\t{kb}\t{kind}\t{src}\t{note}")
        print(f"{status:4} {kb:>8}KB {kind:8} {cat}/{name}", flush=True)
    with open(REPORT, "w", encoding="utf-8-sig") as fh:
        fh.write("\n".join(rows))
    ok = sum(1 for r in rows[1:] if "\t成功\t" in r or "\t已存在\t" in r)
    print(f"\nDONE {ok}/{len(ITEMS)} -> {REPORT}", flush=True)


if __name__ == "__main__":
    main()
