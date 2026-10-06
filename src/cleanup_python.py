# -*- coding: utf-8 -*-
"""清点本机所有 Python：来历、用途、是否可安全删除、怎么删。

只做只读盘点，不删除任何东西。删除前请人工确认。
用法：
    python src/cleanup_python.py            # 盘点并给出删除建议
    python src/cleanup_python.py --json     # 输出机器可读结果
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CHECK_PKGS = ["numpy", "pandas", "matplotlib", "scipy", "sklearn",
              "statsmodels", "pyarrow", "akshare", "baostock"]


def run(cmd: list[str], timeout: int = 60) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as exc:  # noqa: BLE001
        return 1, f"{type(exc).__name__}: {exc}"


def probe(exe: str) -> dict:
    one = (
        "import sys,json,importlib.util as u;"
        "pkgs=" + repr(CHECK_PKGS) + ";"
        "print(json.dumps({'ver':'%d.%d.%d'%sys.version_info[:3],"
        "'prefix':sys.prefix,'base':getattr(sys,'base_prefix',sys.prefix),"
        "'site':[p for p in sys.path if 'site-packages' in p],"
        "'pkgs':{p:bool(u.find_spec(p)) for p in pkgs},"
        "'in_venv':sys.prefix!=getattr(sys,'base_prefix',sys.prefix)}))"
    )
    rc, out = run([exe, "-c", one])
    if rc != 0:
        return {"error": out.strip()[:160]}
    for line in reversed(out.strip().splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return {"error": "解析失败"}


def enumerate_pythons() -> list[str]:
    seen: dict[str, None] = {}

    # 1) py 启动器注册的（最权威）
    rc, out = run(["py", "-0p"])
    if rc == 0:
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[-1].lower().endswith(".exe") and os.path.exists(parts[-1]):
                seen[parts[-1]] = None

    # 2) PATH
    for name in ["python", "python3"]:
        rc, out = run(["where", name])
        if rc == 0:
            for line in out.splitlines():
                line = line.strip()
                if line.lower().endswith(".exe") and os.path.exists(line):
                    seen[line] = None

    # 3) 常见目录
    home = Path.home()
    roots = [home / "AppData" / "Local" / "Programs" / "Python",
             home / ".dsh", home / ".workbuddy", home / ".venv-html-to-docx",
             home / "AppData" / "Roaming" / "uv",
             Path("C:/Program Files"), Path("C:/ProgramData")]
    for root in roots:
        if not root.exists():
            continue
        try:
            for p in root.rglob("python.exe"):
                s = str(p)
                if any(seg in s for seg in ["\\Lib\\venv\\", "\\node_modules\\"]):
                    continue
                if len(s) < 220:
                    seen[s] = None
        except Exception:  # noqa: BLE001
            continue
    return sorted(seen)


def classify(exe: str, info: dict, venvs: list[str]) -> tuple[str, str, str]:
    """返回 (建议, 理由, 删除方法)。"""
    low = exe.lower().replace("/", "\\")

    if "\\windowsapps\\" in low:
        return ("停用（推荐）", "Windows 应用商店占位程序，本身不是真 Python；它会截胡 python 命令",
                "设置 → 应用 → 高级应用设置 → 应用执行别名 → 关掉 python.exe / python3.exe")

    if "\\.dsh\\" in low:
        return ("保留", "DSH 运行环境自带，删了会影响 DSH 工具链", "不删")
    if "\\.workbuddy\\" in low:
        return ("保留", "WorkBuddy 捆绑的运行时，删了该工具会坏", "不删（除非你已不用 WorkBuddy）")
    if "\\uv\\python\\" in low:
        return ("可删", "uv 下载的托管解释器，只有 uv 工具会用；你目前没用 uv", "uv python uninstall 或直接删目录")
    if "\\.venv-html-to-docx\\" in low or "\\scripts\\python.exe" in low:
        return ("保留/可删", "某个项目自己的虚拟环境", "确认该项目不再用后整体删目录")

    if info.get("in_venv"):
        return ("可删", "虚拟环境内部解释器", "整体删除其上级目录")

    # 系统级解释器
    pkgs = info.get("pkgs", {})
    n_pkg = sum(1 for v in pkgs.values() if v)
    if n_pkg >= 3:
        return ("保留（主力）", f"装了 {n_pkg}/{len(CHECK_PKGS)} 个常用包，是你在用的主力解释器", "不删")
    if n_pkg == 0:
        return ("可删（最优先）", "一个常用包都没有，属于空装；很可能是误装或残留",
                "设置 → 应用 → 找到对应 Python → 卸载")
    return ("视情况", f"只有 {n_pkg} 个包，可能是别的项目的环境", "确认无项目依赖后再卸")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    pythons = enumerate_pythons()
    results = [(exe, probe(exe)) for exe in pythons]

    # 找出所有虚拟环境（前缀不等于基础前缀）
    venvs = [exe for exe, i in results if i.get("in_venv")]

    if args.json:
        print(json.dumps([{"exe": e, "info": i} for e, i in results], ensure_ascii=False, indent=2))
        return 0

    print("=" * 92)
    print(f"本机共扫到 {len(pythons)} 个 python.exe")
    print("=" * 92)

    rows = []
    for exe, info in results:
        if "error" in info and not info.get("ver"):
            verdict, reason, how = "停用（占位程序）" if "windowsapps" in exe.lower() else "无法探测", \
                "无法启动或不是真实解释器", "视情况处理"
        else:
            verdict, reason, how = classify(exe, info, venvs)
        n_pkg = sum(1 for v in info.get("pkgs", {}).values() if v) if info.get("pkgs") else 0
        rows.append((exe, info.get("ver", "-"), n_pkg, verdict, reason, how))
        print(f"\n解释器 : {exe}")
        print(f"  版本 : {info.get('ver', '无法启动')}   常用包 : {n_pkg}/{len(CHECK_PKGS)}")
        print(f"  建议 : 【{verdict}】{reason}")
        print(f"  做法 : {how}")

    print("\n" + "=" * 92)
    print("汇总清单")
    print("=" * 92)
    print(f"{'版本':<9}{'包数':<6}{'建议':<16}路径")
    for exe, ver, n_pkg, verdict, _r, _h in rows:
        print(f"{ver:<9}{n_pkg:<6}{verdict:<16}{exe}")

    kill = [r for r in rows if r[3].startswith(("可删", "停用"))]
    print("\n可以清理的：")
    for exe, ver, n_pkg, verdict, reason, how in kill:
        print(f"  - [{ver}] {exe}")
        print(f"      {reason}")
        print(f"      怎么删：{how}")
    if not kill:
        print("  （没有明确可以删的）")

    print("\n【重要】删除前请确认：")
    print("  1. 没有正在运行的程序依赖它（关掉 VS Code / Jupyter / 浏览器里的 notebook）")
    print("  2. 系统级 Python 优先用『设置 → 应用 → 卸载』，不要手删目录（会留注册表残留）")
    print("  3. 删完后重开终端，用 `py -0p` 和 `python -c \"import sys;print(sys.executable)\"` 复查")
    print("  4. 你自己的项目不要依赖系统 Python 的包，一律用项目内的 .venv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
