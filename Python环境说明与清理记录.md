# Python 环境说明与清理记录

> 背景：用户反馈"依赖包一个都没有，但我明明装过"。根因是**本机存在多个 Python，`pip` 装到了 A，脚本跑在 B**。
> 本文记录诊断方法、已完成的清理、以及"以后不再重复装"的操作规范。

---

## 一、根因：9 个 python.exe，装与跑不是同一个

诊断命令（已脚本化：[src/diagnose_python.py](src/diagnose_python.py)）：

```powershell
python src/diagnose_python.py
```

关键证据：

```
裸 pip -V        : pip 25.2 from ...\Python311\Lib\site-packages\pip (python 3.11)
当前解释器       : python 3.12          ← 例如在 DSH 终端里跑时
```

以及：

```
where python
  C:\...\Programs\Python\Python311\python.exe        ← 真 Python 3.11
  C:\...\Microsoft\WindowsApps\python.exe            ← 0 字节的商店别名占位（截胡者）
```

**机制**：`pip` 属于某个具体解释器。当电脑上有多个 Python 时，
"我以为的装"和"实际跑的"很容易不是同一个，于是出现"装了却 import 不到"。

---

## 二、本机 Python 清点与处理结果

| 路径 | 版本 | 常用包 | 处理 |
|---|---|---|---|
| `AppData\Local\Programs\Python\Python311\python.exe` | 3.11.2 | **9/9** | **保留（主力）** |
| `AppData\Roaming\uv\python\cpython-3.12.14-...\python.exe` | 3.12.14 | 0/9 | **已删除**（含 Junction） |
| `AppData\Roaming\uv\python\cpython-3.12-...\python.exe` | 3.12.14 | 0/9 | **已删除**（Junction 链接） |
| `AppData\Local\Microsoft\WindowsApps\python.exe` | 占位 | — | **已删除别名** |
| `AppData\Local\Microsoft\WindowsApps\python3.exe` | 占位 | — | **已删除别名** |
| `~\.venv-html-to-docx\Scripts\python.exe` | 3.12.14 | 0/9 | **已删除**（依赖 uv 解释器，已失效） |
| `.dsh\dsh-runtimes\...\python\python.exe` | 3.12.14 | 8/9 | 保留（DSH 自带，删了工具链会坏） |
| `.workbuddy\binaries\python\versions\3.13.12\python.exe` | 3.13.14 | 0/9 | 保留（WorkBuddy 自带） |
| `.workbuddy\binaries\python\envs\default\Scripts\python.exe` | 3.13.14 | 1/9 | 保留（WorkBuddy 自带） |

**删除的坑（重要经验）**：`cpython-3.12-windows-x86_64-none` 是一个 **Junction（目录链接）**，
指向 `cpython-3.12.14-windows-x86_64-none`。直接 `Remove-Item -Recurse` 会顺着链接删掉真身，
却只报一次成功。正确顺序：**先删链接，再删真身**。

**清理结果**：
- `py -0p` 现在只剩 `-V:3.11 *`（uv 的 `Astral/CPython3.12.14` 条目已从注册表移除，备份在 [docs/reg-backup-python.reg](docs/reg-backup-python.reg)）
- `where python` 现在直接指向 Python311，中间没有任何截胡者
- 释放约 120 MB（uv 两个解释器目录 + 失效虚拟环境）
- 主力解释器 9/9 个包完好，项目 `.venv` 完好

**想进一步精简**（可选）：如果不再使用 WorkBuddy，可在"设置 → 应用"里卸载它，
两个 3.13 的运行时（约 200 MB+）会一并消失。

---

## 三、以后不再重复装：三条规范

### 规范 1：永远用 `python -m pip`，不用裸 `pip`

```powershell
python -m pip install pyarrow      # 对：pip 一定属于当前这个 python
pip install pyarrow                # 错：pip 可能属于另一个 python
```

检查两者是否一致：

```powershell
python -m pip -V        # 看 "from ... (python 3.x)"
pip -V                  # 对比
```

### 规范 2：每个项目用固定虚拟环境，并把绝对路径记住

本项目的虚拟环境已建好：`E:\AI结果\量化\.venv`

```powershell
cd /d "E:\AI结果\量化"

# 以后所有命令都用这个解释器，不依赖 PATH
.venv\Scripts\python.exe src\check_env.py
.venv\Scripts\python.exe src\d01_data.py
.venv\Scripts\python.exe -m pip install 新包
.venv\Scripts\python.exe -m pytest src\test_quantlib.py
```

重建脚本（换电脑或环境坏了时用）：

```powershell
python src\make_venv.py            # 自动挑解释器、建 .venv、装依赖、验证
python src\make_venv.py --find     # 只列出本机可用解释器
python src\make_venv.py --clean    # 删掉重建
```

### 规范 3：先查再装，装完必验

包是否已经有的**最可靠的检查方式**：用你现在实际要用的解释器去查。

```powershell
# 查某个包装没装（比 pip list 更准，因为看的是 import 结果）
python -c "import importlib.util as u; print(bool(u.find_spec('pyarrow')))"

# 一次性验证全套
python src\check_env.py
```

**绝不要**因为"好像没装"就重复执行 `pip install`——重复安装本身无害（会提示 already satisfied），
但它掩盖了真正的问题（装到别的解释器去了）。

---

## 四、VS Code 用户额外一步

VS Code 默认会自己挑解释器，经常挑错。固定下来：

1. `Ctrl+Shift+P` → 输入 `Python: Select Interpreter`
2. 选择带 `.venv` 的那一项：`E:\AI结果\量化\.venv\Scripts\python.exe`
3. 之后 VS Code 终端里 `python` 会优先走这个环境

如果状态栏显示的仍是 `Python 3.11.x (global)`，说明没选对，重做一次。

---

## 五、排查口诀（遇到"装了却没有"时按序做）

1. `python -c "import sys; print(sys.executable)"` —— 先看**实际在跑哪个**
2. `python -m pip -V` —— 看**pip 装到哪个**
3. 两者不一致 → 全部改用 `python -m pip`
4. 还是一致却找不到 → `python src\diagnose_python.py` 全盘扫描
5. 长期方案 → 用 `python src\make_venv.py` 建项目专用环境，从此不用管系统里有多少个 Python
