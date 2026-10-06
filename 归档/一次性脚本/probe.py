# -*- coding: utf-8 -*-
"""探测：Python 能否启动、能否联网、工作目录写权限。"""
import sys

print("python:", sys.version)
print("executable:", sys.executable)

try:
    import urllib.request

    req = urllib.request.Request(
        "https://www.math.pku.edu.cn/",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        print("net:", resp.status, resp.headers.get("Content-Type"))
except Exception as exc:  # noqa: BLE001
    print("net-failed:", type(exc).__name__, exc)

try:
    with open(r"E:\AI结果\量化\_probe.txt", "w", encoding="utf-8") as fh:
        fh.write("ok")
    print("write: ok")
except Exception as exc:  # noqa: BLE001
    print("write-failed:", type(exc).__name__, exc)
