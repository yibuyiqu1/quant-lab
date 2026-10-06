# -*- coding: utf-8 -*-
r"""推送前验查：看看这次会把什么推到 GitHub 上。

用法（在项目根目录）：
    .venv\Scripts\python.exe src\check_repo.py
    .venv\Scripts\python.exe src\check_repo.py --files   # 列出每个被跟踪的文件

它会报告：
    1. 被跟踪的文件数、总大小、最大的几个文件
    2. 按目录统计
    3. 不该上传的东西（教材 PDF、归档、缓存、工具元数据、大数据文件）
    4. 会触发 GitHub 告警的项（单文件 > 50 MB、仓库 > 1 GB）
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
# git 可能不在 PATH 里，按常见位置找
GIT_CANDIDATES = [
    "git",
    r"E:\app\Git\cmd\git.exe",
    r"C:\Program Files\Git\cmd\git.exe",
    r"C:\Program Files (x86)\Git\cmd\git.exe",
    str(Path.home() / "AppData" / "Local" / "Programs" / "Git" / "cmd" / "git.exe"),
]

# 不应该进仓库的规则：(匹配前缀/片段, 说明)
# 注意：.vscode/ 是故意保留的——它把解释器钉在 .venv，属于"让别人能复现"的配置
SHOULD_NOT_TRACK = [
    ("资料库/", "教材与讲义 PDF（体积大 + 版权上不适合公开转存）"),
    ("归档/", "归档的一次性脚本与过期文件"),
    (".workbuddy/", "别的工具的元数据，与本项目无关"),
    (".venv/", "虚拟环境（几千个文件）"),
    ("__pycache__/", "Python 字节码缓存"),
    (".pytest_cache/", "测试缓存"),
    ("data/raw/", "原始数据（可由脚本重新下载）"),
    ("data/clean/", "清洗后数据（可由脚本重新生成）"),
]

# 报告类里的中间产物：建议不进仓库（规则写在 .gitignore 里，但已跟踪的需手动 git rm --cached）
# 说明：reports/d01_mine.json 是"你自己那版"的代表性结果，故意保留，不列入
INTERMEDIATE_PATTERNS = (
    "reports/_*.json",
    "reports/*_lecture.json",
    "reports/*_lesson.json",
    "reports/*_result.json",
    "reports/figs/_*.png",
)

# 报告类：可以留一部分，但通常不必全留
REPORT_LIKE = ("reports/",)

SIZE_WARN_MB = 50      # GitHub 单文件告警线


def find_git() -> str:
    for cand in GIT_CANDIDATES:
        try:
            subprocess.run([cand, "--version"], capture_output=True, check=True, timeout=20)
            return cand
        except Exception:  # noqa: BLE001
            continue
    return ""


def git(g: str, *args: str) -> str:
    p = subprocess.run([g, *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(ROOT), timeout=120)
    return (p.stdout or "") + (p.stderr or "")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", action="store_true", help="列出每个被跟踪的文件")
    args = ap.parse_args()

    g = find_git()
    if not g:
        print("[错误] 找不到 git。请确认已安装 Git for Windows，或修改本脚本顶部的 GIT_CANDIDATES。")
        return 1
    print(f"使用 git: {g}")
    print(f"项目根目录: {ROOT}")

    if not (ROOT / ".git").exists():
        print("\n[错误] 这里不是 git 仓库（没有 .git 目录）。先执行：git init")
        return 1

    tracked = [x for x in git(g, "ls-files").splitlines() if x.strip()]
    print(f"\n{'=' * 66}")
    print(f"被跟踪文件：{len(tracked)} 个")
    print("=" * 66)

    sizes = []
    total = 0
    for rel in tracked:
        p = ROOT / rel
        if p.exists():
            sz = p.stat().st_size
            total += sz
            sizes.append((sz, rel))
    print(f"工作区对应总大小：{total / 1024 / 1024:.2f} MB")

    # 按目录统计
    buckets: dict[str, list[int]] = {}
    for sz, rel in sizes:
        key = rel.split("/")[0] if "/" in rel else "(根目录)"
        buckets.setdefault(key, []).append(sz)
    print("\n按目录：")
    for key, arr in sorted(buckets.items(), key=lambda kv: -sum(kv[1])):
        print(f"  {key:<16} {len(arr):>4} 个   {sum(arr) / 1024 / 1024:>8.2f} MB")

    # 大文件
    print("\n最大的 8 个文件：")
    for sz, rel in sorted(sizes, reverse=True)[:8]:
        warn = "  ← 超过 50MB，GitHub 会告警" if sz > SIZE_WARN_MB * 1024 * 1024 else ""
        print(f"  {sz / 1024 / 1024:>8.2f} MB  {rel}{warn}")

    # 不该跟踪的
    print(f"\n{'=' * 66}")
    print("不该上传的内容")
    print("=" * 66)
    problems = []
    for prefix, why in SHOULD_NOT_TRACK:
        hit = [r for r in tracked if r.startswith(prefix)]
        if hit:
            problems.append((prefix, len(hit), why))
    if problems:
        for prefix, n, why in problems:
            print(f"  [有] {prefix:<18} {n:>3} 个文件    {why}")
        print("\n  处理办法（保留本地文件，只从 git 移除）：")
        for prefix, _n, _why in problems:
            print(f"    git rm -r --cached \"{prefix.rstrip('/')}\"")
        print("  然后把这些规则写进 .gitignore：")
        for prefix, _n, _why in problems:
            print(f"    {prefix.rstrip('/')}/")
    else:
        print("  [干净] 没有发现不该上传的内容")

    # 报告类里的中间产物
    import fnmatch
    inter = [r for r in tracked if any(fnmatch.fnmatch(r, p) for p in INTERMEDIATE_PATTERNS)]
    if inter:
        print(f"\n  提示：{len(inter)} 个报告中间产物还在仓库里（多次运行的 JSON 等）。")
        print("        建议只保留代表性的图与最终报告：")
        for r in inter:
            print(f"          {r}")
        print("        处理：")
        for p in INTERMEDIATE_PATTERNS:
            folder = os.path.dirname(p)
            print(f"          git rm --cached \"{folder}\"/*.json   # 按需调整")
        print("        （.gitignore 里已经写了规则，但已跟踪的文件必须显式移除）")
    else:
        print("\n  [干净] reports/ 下没有多余的中间产物")

    if args.files:
        print(f"\n{'=' * 66}")
        print("全部被跟踪文件")
        print("=" * 66)
        for rel in tracked:
            print("  " + rel)

    # 总结
    print(f"\n{'=' * 66}")
    if problems:
        print(f"结论：有 {len(problems)} 类内容不该上传，按上面的命令清理后再推送。")
    else:
        print("结论：可以推送。")
    print("=" * 66)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
