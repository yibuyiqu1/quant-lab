# -*- coding: utf-8 -*-
"""逐条探测候选资料的 URL 可用性（只读头部，不下载完整文件）。"""
import urllib.request
import urllib.error
import concurrent.futures as cf

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

URLS = [
    # --- MIT OCW ---
    "https://ocw.mit.edu/courses/18-100a-real-analysis-fall-2020/mit18_100af20_lec_full.pdf",
    "https://ocw.mit.edu/courses/18-100a-real-analysis-fall-2020/resources/mit18_100af20_lec_full/",
    "https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/resources/mit18_06s10_notes/",
    "https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/mit18_06s10_notes.pdf",
    "https://ocw.mit.edu/courses/18-175-theory-of-probability-spring-2014/mit18_175s14_lecturenotes.pdf",
    "https://ocw.mit.edu/courses/18-175-theory-of-probability-spring-2014/resources/mit18_175s14_lecturenotes/",
    "https://ocw.mit.edu/courses/18-s096-topics-in-mathematics-with-applications-in-finance-fall-2013/mit18_s096f13_lecnote_all.pdf",
    "https://ocw.mit.edu/courses/18-s096-topics-in-mathematics-with-applications-in-finance-fall-2013/resources/mit18_s096f13_lecnote_all/",
    "https://ocw.mit.edu/courses/15-450-analytics-of-finance-fall-2010/mit15_450f10_lecnotes.pdf",
    "https://ocw.mit.edu/courses/6-262-discrete-stochastic-processes-spring-2011/mit6_262s11_book.pdf",
    "https://ocw.mit.edu/courses/6-041-probabilistic-systems-analysis-and-applied-probability-fall-2010/mit6_041f10_notes.pdf",
    "https://ocw.mit.edu/courses/18-650-statistics-for-applications-fall-2016/mit18_650f16_lecture_notes.pdf",
    "https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/",
    # --- 概率教材 ---
    "https://services.math.duke.edu/~rtd/PTE/PTE5_011119.pdf",
    "https://www.math.duke.edu/~rtd/PTE/PTE5_011119.pdf",
    "https://services.math.duke.edu/~rtd/PTE/PTE4_1.pdf",
    # --- 统计/ML ---
    "https://hastie.su.domains/Papers/ESLII.pdf",
    "https://hastie.su.domains/ISLR2/ISLRv2_website.pdf",
    "https://www.statlearning.com/s/ISLRv2_website.pdf",
    "https://raw.githubusercontent.com/szcf-weiya/ESL-CN/master/docs/ESL-CN.pdf",
    "https://raw.githubusercontent.com/szcf-weiya/ESL-CN/master/docs/The-Elements-of-Statistical-Learning.pdf",
    "https://raw.githubusercontent.com/nndl/nndl.github.io/master/nndl-book.pdf",
    "https://raw.githubusercontent.com/nndl/nndl.github.io/master/nndl-book-5.pdf",
    "https://raw.githubusercontent.com/probml/pml-book/main/book1/pml-book-1.pdf",
    "https://raw.githubusercontent.com/probml/pml-book/main/book2/pml-book-2.pdf",
    "https://raw.githubusercontent.com/percyliang/cs229t/master/scribe/notes.pdf",
    # --- 时间序列 ---
    "https://raw.githubusercontent.com/Shitao/MLForTimeSeries/master/README.md",
    "https://otexts.com/fpp3/fpp3.pdf",
    "https://raw.githubusercontent.com/awslabs/gluonts/master/README.md",
    # --- 凸优化 ---
    "https://raw.githubusercontent.com/cvxgrp/cvxbook_additional_exercises/main/additional_exercises.pdf",
    "https://web.stanford.edu/class/ee364a/lectures.html",
    "https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf",
    "https://raw.githubusercontent.com/ebrahimpichka/awesome-optimization/master/README.md",
    # --- 金融论文 ---
    "https://www.math.nyu.edu/~avellane/HighFrequencyTrading.pdf",
    "https://faculty.chicagobooth.edu/-/media/faculty/eugene-fama/translations/1993-jf-fama-french.pdf",
    "https://www.smallake.kr/wp-content/uploads/2016/03/optliq.pdf",
    "https://arxiv.org/pdf/1609.02890",
    "https://arxiv.org/pdf/2112.08534",
    "https://arxiv.org/pdf/1905.01332",
    "https://www.janestreet.com/puzzles/archive/",
    "https://platform.worldquantbrain.com/",
    # --- 中文公开课/资料 ---
    "https://www.math.pku.edu.cn/jxpy/index.htm",
    "https://ocw.mit.edu/search/?q=finance",
    "https://raw.githubusercontent.com/datawhalechina/pumpkin-book/master/docs/chapter1/chapter1.md",
    "https://raw.githubusercontent.com/apachecn/apachecn-dl-zh/master/README.md",
]


def probe(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            head = resp.read(2048)
            ctype = resp.headers.get("Content-Type", "")
            clen = resp.headers.get("Content-Length", "")
            magic = head[:4]
            kind = "PDF" if magic[:4] == b"%PDF" else ("HTML" if b"<" in head[:200] else "OTHER")
            return f"OK\t{resp.status}\t{kind}\t{clen}\t{ctype[:40]}\t{resp.geturl()[:110]}"
    except urllib.error.HTTPError as exc:
        return f"HTTP{exc.code}\t-\t-\t-\t-\t{url[:110]}"
    except Exception as exc:  # noqa: BLE001
        return f"ERR:{type(exc).__name__}\t-\t-\t-\t-\t{url[:110]}"


with cf.ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(probe, URLS))

for url, res in zip(URLS, results):
    print(f"{res}\n    <- {url}", flush=True)
