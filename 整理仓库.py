# -*- coding: utf-8 -*-
r"""仓库整理：把知识文档收进 docs/，从 git 移除资料库/归档/元数据。

只做四件事，每件都可核验：
  1. git rm -r --cached 资料库 归档 .workbuddy   （本地文件保留）
  2. 把根目录的知识文档移动到 docs/
  3. 重写所有文档里的相对链接（md 之间、指向 src/、指向 README）
  4. 扫描全仓库，报告失效链接

用法：
    .venv\Scripts\python.exe 整理仓库.py
"""
from __future__ import annotations

import io
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
GIT = r"E:\app\Git\cmd\git.exe"

# 要移进 docs/ 的文档（按学习顺序）
TO_MOVE = [
    "项目索引与聊天记录整理.md",
    "量化研究员启动计划.xlsx",          # 主线任务表，一并收进 docs/
    "量化研究员启动手册-Day1起.md",
    "Day1完整逻辑与流程图解.md",
    "Day1零基础概念手册.md",
    "B线编程工程-零基础21天执行手册.md",
    "B线速查表.html",
    "Matplotlib画图逐行注解.md",
    "概率论中文精讲笔记-D1到D4.md",
    "量化数学双语术语对照表.md",
    "Python包速查表.md",
    "Git与GitHub零基础实操手册.md",
    "VSCode运行代码-排错手册.md",
    "Python环境说明与清理记录.md",
    "代码放哪里-目录约定.md",
    "Notebooks自学成果验收报告.md",
]

# 留在根目录：README.md（没有链接指向它自己，不需要改）

# 需要"加上 docs/ 前缀"的文件（不移动，但会被别的文档引用）
STAY_AT_ROOT = ["README.md"]

# 需要"加上 ../ 前缀"的目录（在 docs/ 里引用它们）
PARENT_DIRS = ["src/", "data/", "reports/", "资料库/", "归档/", ".vscode/"]

TRACKED_DIRS_TO_UNTRACK = ["资料库", "归档", ".workbuddy"]


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(cwd), timeout=300)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def step1_untrack() -> None:
    print("=" * 70)
    print("步骤 1：从 git 索引移除不该上传的目录（本地文件保留）")
    print("=" * 70)
    for d in TRACKED_DIRS_TO_UNTRACK:
        if not (ROOT / d).exists():
            print(f"  [跳过] {d} 不存在")
            continue
        rc, out = run([GIT, "rm", "-r", "--cached", "--quiet", d], ROOT)
        if rc == 0:
            print(f"  [已移除跟踪] {d}")
        else:
            print(f"  [失败] {d}: {out.strip()[:200]}")


def step2_move() -> list[str]:
    print()
    print("=" * 70)
    print("步骤 2：把知识文档移进 docs/")
    print("=" * 70)
    DOCS.mkdir(exist_ok=True)
    moved = []
    for name in TO_MOVE:
        src = ROOT / name
        dst = DOCS / name
        if not src.exists():
            if dst.exists():
                print(f"  [已在 docs] {name}")
                moved.append(name)
            else:
                print(f"  [缺失] {name}")
            continue
        if dst.exists():
            dst.unlink()
        shutil.move(str(src), str(dst))
        print(f"  [已移动] {name}  ->  docs/")
        moved.append(name)
    return moved


def step3_rewrite_links(moved: list[str]) -> tuple[int, int]:
    print()
    print("=" * 70)
    print("步骤 3：重写文档里的相对链接")
    print("=" * 70)

    files = [DOCS / n for n in moved if n.endswith((".md", ".html"))]
    files.append(ROOT / "README.md")

    total_files, total_subs = 0, 0
    for path in files:
        if not path.exists():
            continue
        text = io.open(path, encoding="utf-8").read()
        original = text

        # (a) 指向"已移入 docs/"的文件：从根目录的 README 看要加 docs/ 前缀，
        #     从 docs/ 内部的文档看是同级，直接裸文件名
        for name in moved:
            if path.parent == DOCS:
                text = text.replace(f"](docs/{name})", f"]({name})")
            else:
                text = text.replace(f"]({name})", f"](docs/{name})")

        # (a2) 指向"留在根目录"的文件（如 README.md）：
        #      根目录的文档写裸名，docs/ 里的文档必须加 ../，否则会指向 docs/README.md
        for name in STAY_AT_ROOT:
            if path.parent == DOCS:
                text = re.sub(rf"\]\((?<!\.\./){re.escape(name)}\)", rf"](../{name})", text)
            else:
                text = text.replace(f"](../{name})", f"]({name})")

        # (b) 指向 src/ data/ reports/ 等：docs/ 里的文档要加 ../
        if path.parent == DOCS:
            for d in PARENT_DIRS:
                text = text.replace(f"]({d}", f"](../{d}")

        # (c) docs/ 内部互相引用时，已经写成 ../docs/xxx 的要纠正
        if path.parent == DOCS:
            text = re.sub(r"\]\(\.\./docs/", "](../docs/", text)

        if text != original:
            io.open(path, "w", encoding="utf-8").write(text)
            n = sum(1 for a, b in zip(original.split("]("), text.split("](")) if a != b)
            total_files += 1
            total_subs += n
            print(f"  [已改写] {path.relative_to(ROOT)}")
    print(f"  共改写 {total_files} 个文件")
    return total_files, total_subs


def step4_verify() -> list[str]:
    print()
    print("=" * 70)
    print("步骤 4：扫描链接，报告失效项")
    print("=" * 70)
    broken = []
    link_re = re.compile(r"\]\(([^)]+)\)")

    for path in list(ROOT.glob("*.md")) + list(DOCS.glob("*.md")):
        text = io.open(path, encoding="utf-8").read()
        for raw in link_re.findall(text):
            target = raw.split("#")[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            # 以 / 结尾或含通配符的跳过
            if target.endswith("/") or "*" in target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                broken.append(f"{path.name}  ->  {raw}")
    if broken:
        for b in broken[:20]:
            print("  [失效] " + b)
        print(f"  共 {len(broken)} 个失效链接")
    else:
        print("  [OK] 没有失效链接")
    return broken


def main() -> int:
    step1_untrack()
    moved = step2_move()
    step3_rewrite_links(moved)
    broken = step4_verify()

    print()
    print("=" * 70)
    print("步骤 5：整理后的仓库结构")
    print("=" * 70)
    print("根目录：")
    for p in sorted(ROOT.iterdir()):
        if p.is_dir() and p.name not in (".git", ".venv", "__pycache__"):
            print(f"  [目录] {p.name}/")
    for p in sorted(ROOT.glob("*.md")):
        print(f"  [文件] {p.name}")
    for p in sorted(ROOT.glob("*.txt")):
        print(f"  [文件] {p.name}")
    for p in sorted(ROOT.glob("*.bat")):
        print(f"  [文件] {p.name}")
    print("docs/：")
    for p in sorted(DOCS.iterdir()):
        print(f"  {p.name}")

    print()
    print("=" * 70)
    print("下一步（需要你确认后执行，或用我给的一条命令）：")
    print("=" * 70)
    print('  git add -A')
    print('  git commit -m "chore: 排除资料库/归档/元数据，文档收进 docs/，修正 .gitignore"')
    print('  git push --force origin main')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
