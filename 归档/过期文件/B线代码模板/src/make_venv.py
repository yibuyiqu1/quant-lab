# -*- coding: utf-8 -*-
"""一次性建好项目专用虚拟环境 .venv，并装齐所有依赖。

为什么需要它：
    电脑上有多个 Python 时，`pip install` 和 `python` 很容易不是同一个环境，
    于是出现"我明明装了却 import 不到"。虚拟环境把解释器和包目录绑死，
    之后每一步都用 .venv 里的 python，就再也不会错。

用法：
    python src/make_venv.py            # 自动挑选合适的解释器建环境
    python src/make_venv.py --clean    # 先删掉旧 .venv 再重建
    python src/make_venv.py --find     # 只列出本机可用解释器，不做任何修改

成功后你只需要用这一个 Python：
    .venv\\Scripts\\python.exe src\\check_env.py
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
VENV = ROOT / ".venv"
REQ = ROOT / "requirements.txt"

# 国内镜像（先试官方，失败再换镜像）
MIRRORS = [
    None,
    "https://pypi.tuna.tsinghua.edu.cn/simple",
    "https://mirrors.aliyun.com/pypi/simple",
]

MIN_VERSION = (3, 10)


def run(cmd: list[str], timeout: int = 900) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 1, "超时"
    except Exception as exc:  # noqa: BLE001
        return 1, f"{type(exc).__name__}: {exc}"


def py_launcher_list() -> list[tuple[str, str, str]]:
    """用 Windows 的 py 启动器列出所有已注册的 Python（这是最权威的名单）。"""
    out_list = []
    rc, out = run(["py", "-0p"], timeout=30)
    if rc != 0:
        return out_list
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("-"):
            continue
        # 形如:  -V:3.11 *        C:\...\python.exe
        parts = line.split()
        if len(parts) < 2:
            continue
        tag = parts[0].lstrip("-V:").rstrip("*")
        exe = " ".join(parts[1:])
        if not exe.lower().endswith(".exe"):
            continue
        out_list.append((tag, exe, "默认" if "*" in line else ""))
    return out_list


def version_of(exe: str) -> tuple[int, int] | None:
    rc, out = run([exe, "-c", "import sys;print('%d %d' % sys.version_info[:2])"], timeout=60)
    if rc != 0:
        return None
    try:
        major, minor = out.strip().split()[:2]
        return int(major), int(minor)
    except Exception:  # noqa: BLE001
        return None


def candidates() -> list[tuple[str, tuple[int, int], str]]:
    """收集候选解释器：来源为 py 启动器 + 当前解释器，去重后按版本排序。"""
    found: dict[str, tuple[int, int]] = {}

    for tag, exe, _flag in py_launcher_list():
        if os.path.exists(exe):
            v = version_of(exe)
            if v:
                found[exe] = v

    # 当前解释器也算一个候选（如果它满足版本要求）
    cur = sys.executable
    v = version_of(cur)
    if v and cur not in found:
        found[cur] = v

    # 常见位置兜底（只在 py 启动器不可用时才需要）
    if not found:
        for name in ["python", "python3"]:
            rc, out = run(["where", name], timeout=20)
            if rc == 0:
                for line in out.splitlines():
                    line = line.strip()
                    if line.lower().endswith(".exe") and os.path.exists(line):
                        vv = version_of(line)
                        if vv:
                            found[line] = vv

    good = [(e, v, "") for e, v in found.items() if v >= MIN_VERSION]
    bad = [(e, v, "") for e, v in found.items() if v < MIN_VERSION]
    good.sort(key=lambda t: t[1], reverse=True)   # 版本高的优先
    return good + bad


def pick_python(cands) -> str | None:
    """挑选：优先 3.11/3.12（生态最稳），其次版本最高的可用项。"""
    for pref in [(3, 12), (3, 11)]:
        for exe, v, _ in cands:
            if v == pref:
                return exe
    for exe, v, _ in cands:
        if v >= MIN_VERSION:
            return exe
    return None


def make_venv(exe: str, fresh: bool) -> bool:
    if fresh and VENV.exists():
        print(f"[1/5] 删除旧环境 {VENV} ...")
        shutil.rmtree(VENV, ignore_errors=True)
    if VENV.exists():
        print(f"[1/5] 已有虚拟环境，跳过创建：{VENV}")
        return True
    print(f"[1/5] 用 {exe} 创建虚拟环境（继承已装的系统包，避免重复下载）...")
    rc, out = run([exe, "-m", "venv", "--system-site-packages", str(VENV)])
    if rc != 0:
        print("      创建失败：", out.strip()[-400:])
        return False
    print("      完成:", VENV)
    return True


def venv_python() -> str:
    """虚拟环境里的 python 可执行文件路径。"""
    if os.name == "nt":
        return str(VENV / "Scripts" / "python.exe")
    return str(VENV / "bin" / "python")


def install(py: str) -> bool:
    print("[2/5] 升级 pip ...")
    run([py, "-m", "pip", "install", "--quiet", "--upgrade", "pip"], timeout=600)

    if not REQ.exists():
        print(f"      找不到 {REQ}，跳过依赖安装")
        return True

    print("[3/5] 安装 requirements.txt 里的依赖 ...")
    for mirror in MIRRORS:
        cmd = [py, "-m", "pip", "install", "--quiet", "-r", str(REQ)]
        if mirror:
            cmd += ["-i", mirror]
            print(f"      尝试镜像: {mirror}")
        rc, out = run(cmd)
        if rc == 0:
            print("      安装完成")
            return True
        print("      失败：", out.strip()[-300:])
    print("      [警告] 依赖安装未全部成功，可稍后手动重试")
    return False


def verify(py: str) -> bool:
    print("[4/5] 验证关键依赖 ...")
    code = (
        "import importlib.util as u;"
        "pkgs=['numpy','pandas','matplotlib','scipy','sklearn','statsmodels','pyarrow','akshare','baostock'];"
        "miss=[p for p in pkgs if not u.find_spec(p)];"
        "print('OK' if not miss else 'MISSING:'+','.join(miss))"
    )
    rc, out = run([py, "-c", code], timeout=180)
    ok = rc == 0 and "OK" in out
    print("      " + out.strip()[:200])
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="建立项目专用虚拟环境")
    ap.add_argument("--clean", action="store_true", help="删除旧 .venv 后重建")
    ap.add_argument("--find", action="store_true", help="只列出可用解释器")
    args = ap.parse_args()

    print("=" * 70)
    print("项目虚拟环境安装器")
    print(f"项目根目录: {ROOT}")
    print("=" * 70)

    cands = candidates()
    print("\n本机可用的 Python 解释器：")
    if not cands:
        print("  （没找到，请先安装 Python 3.11 或 3.12：https://www.python.org/downloads/）")
        return 1
    for exe, v, flag in cands:
        mark = "可用" if v >= MIN_VERSION else "版本过低"
        print(f"  {v[0]}.{v[1]:<3} [{mark}] {exe}")

    if args.find:
        return 0

    exe = pick_python(cands)
    if not exe:
        print("\n[错误] 没有 3.10 以上的解释器，无法继续。请先安装 Python 3.11。")
        return 1
    print(f"\n将使用: {exe}")

    if not make_venv(exe, args.clean):
        return 1

    py = venv_python()
    if not os.path.exists(py):
        print("[错误] 虚拟环境里没有找到 python.exe：", py)
        return 1

    install(py)
    ok = verify(py)

    print("[5/5] 完成")
    print("=" * 70)
    print("以后固定用这个解释器（复制这几条即可）：")
    print()
    print(f"  cd /d {ROOT}")
    print(f"  {py} src\\check_env.py                 <- 环境自检")
    print(f"  {py} src\\d01_data.py                  <- 抓数据")
    print(f"  {py} src\\d01_first_analysis.py        <- 出报告")
    print(f"  {py} -m pip install 某个包            <- 以后装包都这么装")
    print(f"  {py} -m pytest src\\test_quantlib.py   <- 跑测试")
    print()
    print("VS Code 用户：Ctrl+Shift+P -> Python: Select Interpreter -> 选 .venv 里的那个")
    print("=" * 70)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
