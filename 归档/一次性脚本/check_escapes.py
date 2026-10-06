# -*- coding: utf-8 -*-
"""检查 src/*.py 是否存在 Windows 路径引发的转义警告，并给出精确位置。"""
import glob
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")

# 匹配：三引号开头但不是 r"""，且文件里出现了 Windows 反斜杠路径
PAT = re.compile(r'\\[A-Za-z]')

for path in sorted(glob.glob(os.path.join(SRC, "*.py"))):
    name = os.path.basename(path)
    text = io.open(path, encoding="utf-8").read()
    lines = text.splitlines()

    issues = []
    in_doc = False
    raw_doc = False
    for i, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if not in_doc and ('"""' in line or "'''" in line):
            in_doc = True
            raw_doc = stripped.startswith(('r"""', "r'''", 'R"""'))
            continue
        if in_doc:
            if '"""' in line or "'''" in line:
                in_doc = False
                continue
            # 文档字符串内部出现 \X 这种转义序列，且不是 raw 字符串 → 会报警
            if not raw_doc:
                for m in PAT.finditer(line):
                    seg = line[max(0, m.start() - 12):m.start() + 14]
                    issues.append((i, m.group(0), seg.strip()))
    if issues:
        print(f"[需修复] {name}")
        for ln, seq, seg in issues[:4]:
            print(f"    第 {ln} 行  序列 {seq!r}  上下文: ...{seg}...")
    else:
        print(f"[干净]  {name}")
