# -*- coding: utf-8 -*-
"""诊断：电脑上到底有几个 Python，每个里面装了什么包，pip 装到了哪里。

用法（用任意一个能跑的 python 执行）：
    python src/diagnose_python.py
    py -3 src/diagnose_python.py

它会输出：
1. 当前正在运行的 Python 与它的包
2. 全盘扫到的其他 Python 解释器及各自版本
3. 用每个解释器去问"装没装 pyarrow/matplotlib"（用子进程，不受当前环境影响）
4. pip 的安装目标路径 vs 当前解释器路径（这是"装了却 import 不到"的根因）
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CHECK_PKGS = ["numpy", "pandas", "matplotlib", "scipy", "sklearn",
              "statsmodels", "pyarrow", "akshare", "baostock"]


def run(cmd: list[str], timeout: int = 60) -> tuple[int, str]:
    """跑一条命令，返回 (返回码, 输出)。用 subprocess，不受当前解释器影响。"""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except FileNotFoundError:
        return 127, "命令不存在"
    except Exception as exc:  # noqa: BLE001
        return 1, f"{type(exc).__name__}: {exc}"


def probe_interpreter(exe: str) -> dict:
    """用一个解释器检查：版本、site-packages、各包是否可 import。

    用子进程 + -c 一行脚本，所以结果只取决于这个解释器本身，
    不受当前运行环境（sys.path、已 import 的模块）影响。
    """
    one_liner = (
        "import sys,json,importlib.util as u;"
        "pkgs=" + repr(CHECK_PKGS) + ";"
        "print(json.dumps({'version':sys.version.split()[0],'exe':sys.executable,"
        "'prefix':sys.prefix,'site':[p for p in sys.path if 'site-packages' in p],"
        "'pkgs':{p:bool(u.find_spec(p)) for p in pkgs}}))"
    )
    rc, out = run([exe, "-c", one_liner])
    if rc != 0:
        return {"error": out.strip()[:200]}
    for line in reversed(out.strip().splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return {"error": "无法解析输出: " + out.strip()[:200]}


def find_pythons() -> list[str]:
    """扫描常见位置，收集所有 python.exe。"""
    candidates: set[str] = set()

    # 1) PATH 里的
    for name in ["python", "python3", "py"]:
        rc, out = run(["where", name] if os.name == "nt" else ["which", "-a", name])
        if rc == 0:
            for line in out.splitlines():
                line = line.strip()
                if line.lower().endswith(".exe") and os.path.exists(line):
                    candidates.add(line)

    # 2) 常见安装目录
    home = Path.home()
    roots = [
        home / "AppData" / "Local" / "Programs" / "Python",
        home / "anaconda3", home / "miniconda3", home / "Anaconda3",
        Path("C:/"), Path("C:/Program Files"), Path("C:/ProgramData"),
        home / "AppData" / "Local" / "Microsoft" / "WindowsApps",
    ]
    for root in roots:
        if not root.exists():
            continue
        try:
            for p in root.rglob("python.exe"):
                s = str(p)
                # 排除虚拟环境内部的重复项，避免刷屏
                if any(seg in s for seg in ["\\Lib\\venv\\", "\\envs\\", "\\.venv"]):
                    continue
                if len(s) < 200:
                    candidates.add(s)
        except Exception:  # noqa: BLE001
            continue
    return sorted(candidates)


def main() -> int:
    print("=" * 74)
    print("一、当前正在运行的解释器")
    print("=" * 74)
    print(f"  sys.executable : {sys.executable}")
    print(f"  版本           : {sys.version.split()[0]}")
    print(f"  sys.prefix     : {sys.prefix}")
    sites = [p for p in sys.path if "site-packages" in p]
    print(f"  site-packages  : {sites[0] if sites else '(未找到)'}")

    print("\n  当前解释器能 import 的包：")
    import importlib.util as iu

    for p in CHECK_PKGS:
        print(f"    {'有  ' if iu.find_spec(p) else '没有'} {p}")

    print("\n" + "=" * 74)
    print("二、pip 会装到哪里（关键！）")
    print("=" * 74)
    rc, out = run([sys.executable, "-m", "pip", "-V"])
    out = out.strip()
    print(f"  python -m pip -V : {out}")
    rc2, out2 = run(["pip", "-V"])
    out2 = out2.strip()
    print(f"  裸 pip -V        : {out2 if rc2 == 0 else '不可用'}")

    def pip_target(text: str) -> tuple[str, str]:
        """从 'pip 25.2 from <...>\\site-packages\\pip (python 3.11)' 取 (site-packages, 版本)。"""
        if not text or " from " not in text:
            return "", ""
        raw = text.split(" from ", 1)[1]
        raw = raw.rsplit(" (python", 1)[0].strip()
        ver = text.rsplit("(python", 1)[1].strip(" )") if "(python" in text else "?"
        # 去掉结尾的 \pip 或 /pip，得到真正的 site-packages 目录
        norm = os.path.normpath(raw)
        if os.path.basename(norm).lower() == "pip":
            norm = os.path.dirname(norm)
        return norm, ver

    my_site = os.path.normpath(next((p for p in sys.path if "site-packages" in p), ""))
    my_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    bare_site, bare_ver = pip_target(out2)

    print(f"\n  当前解释器      : python {my_ver}")
    print(f"  当前 site-pkgs  : {my_site or '(未找到)'}")
    if bare_site:
        print(f"  裸 pip 的 site  : {bare_site}  (python {bare_ver})")

    # 虚拟环境里裸 pip 可能来自父解释器，属于正常情况，单独说明
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    problems = []
    if bare_ver and bare_ver != my_ver:
        problems.append(f"裸 pip 装到 python {bare_ver}，但你现在运行的是 python {my_ver}")
    elif bare_site and my_site and bare_site.lower() != my_site.lower():
        if in_venv:
            print("\n  [说明] 你在虚拟环境里，裸 pip 指向父解释器，这属于正常现象，")
            print("         但为了不出错，仍然建议统一用 python -m pip。")
        else:
            problems.append("裸 pip 与当前解释器的安装目录不是同一个")

    if problems:
        print("\n  " + "!" * 66)
        print("  【找到原因了】")
        for p in problems:
            print("    - " + p)
        print("    这就是『我明明装过，却一个都没有』的机制：")
        print("      你以为的『装』  ->  装进了 python A 的目录")
        print("      脚本实际用的    ->  python B 解释器，看不到 A 的目录")
        print("  " + "!" * 66)
    else:
        print("\n  [正常] 裸 pip 与当前解释器指向同一环境。")

    print("\n  【铁律一】永远用：python -m pip install xxx")
    print("            不要用：pip install xxx（它可能属于另一个 Python）")
    print("  【铁律二】验证时永远用：python -m pip list")
    print("            而不是：pip list")

    print("\n" + "=" * 74)
    print("三、全盘扫描到的 Python 解释器")
    print("=" * 74)
    pythons = find_pythons()
    if not pythons:
        print("  没扫到其他解释器（也可能扫描权限不足）")
    results = []
    for exe in pythons:
        info = probe_interpreter(exe)
        results.append((exe, info))
        if "error" in info:
            print(f"\n  {exe}\n      -> 无法探测: {info['error']}")
            continue
        have = [p for p, ok in info["pkgs"].items() if ok]
        miss = [p for p, ok in info["pkgs"].items() if not ok]
        print(f"\n  {exe}")
        print(f"      版本 {info['version']} | 包 {len(have)}/{len(CHECK_PKGS)}")
        print(f"      有: {', '.join(have) if have else '（无）'}")
        print(f"      缺: {', '.join(miss) if miss else '（无）'}")

    print("\n" + "=" * 74)
    print("四、结论与建议")
    print("=" * 74)
    print(f"  总共找到 {len(pythons)} 个 Python 解释器。")
    if len(pythons) > 1:
        print("  解释器超过 1 个 —— 这正是『装了却找不到』的高发场景。")
        print("  推荐做法：不要猜哪个是哪个，直接建一个项目专用虚拟环境：")
    else:
        print("  只有 1 个解释器，那问题多半是 pip 与 python 不匹配。")
        print("  推荐做法：建项目专用虚拟环境，彻底消除歧义：")
    print()
    print("     cd /d E:\\你的项目目录")
    print("     python -m venv .venv --system-site-packages")
    print("     .venv\\Scripts\\python.exe -m pip install --upgrade pip")
    print("     .venv\\Scripts\\python.exe -m pip install -r requirements.txt")
    print("     .venv\\Scripts\\python.exe src\\check_env.py     <- 用这个解释器验证")
    print()
    print("  或者直接运行我准备好的脚本： python src/make_venv.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
