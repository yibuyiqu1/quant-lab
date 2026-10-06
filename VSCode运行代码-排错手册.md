# VS Code 里怎么跑代码：四种常见错误与解决

> 背景：你在 VS Code 里遇到 `SyntaxError: invalid syntax`，报错行是
> `& E:/work/anaconda/python.exe e:/AI结果/量化/src/my_d01_analysis.py`
> **这不是代码的错误，是把"终端命令"粘进了"Python 交互环境"。**
> 本文把这类问题一次讲清，以后不再卡住。

---

## 一、先认清：四种出错场景的分辨方法

| 报错样子 | 真实原因 | 属于哪类问题 |
|---|---|---|
| `SyntaxError: invalid syntax`，箭头指向 `&` 或路径 | 你在 **Python 交互环境**（`>>>`）里粘了 PowerShell 命令 | 环境用错 |
| `ModuleNotFoundError: No module named 'akshare'` | VS Code 用了 **Anaconda 解释器**，它没装这个包 | 解释器选错 |
| `SyntaxWarning: invalid escape sequence '\A'` | docstring 里有 Windows 路径但没加 `r` 前缀 | 代码小瑕疵 |
| **运行后什么都没发生，也不报错** | 文件末尾缺少调用入口（`if __name__ == "__main__":`） | 代码缺入口 |

**⚠️ 另一个容易误判的情况**：终端里最后出现 `[exit code: 1]` 或红色 `NativeCommandError`，
**不一定代表脚本失败**。看有没有正常的输出内容——有输出就说明脚本跑成功了，
那个 1 是 PowerShell 管道的退出码（比如 `| Select-Object -First 5` 提前截断了输出流）。

---

## 二、错误 1：把 PowerShell 命令粘进了 Python 环境

### 怎么看出你在哪个环境

| 提示符 | 你在哪 | 能执行什么 |
|---|---|---|
| `>>>` 或 `In [1]:` | **Python 交互环境**（REPL） | 只能写 **Python 代码** |
| `PS E:\AI结果\量化>` | **PowerShell 终端** | 能执行系统命令、也能启动 Python |
| `(.venv) PS E:\AI结果\量化>` | 已激活虚拟环境的 PowerShell | 同上，且 `python` 指向 .venv |

### 为什么 `&` 会报错

```python
>>> & E:/work/anaconda/python.exe e:/AI结果/量化/src/my_d01_analysis.py
SyntaxError: invalid syntax
```

- `&` 是 **PowerShell 的"调用运算符"**（意思是"执行这个程序"），Python 里没有这个东西
- 而且你已经在 Python 环境里了，**不需要再用命令行去启动另一个 Python**
- `>>>` 里只接受 Python 语法，比如 `print(1+1)`、`import pandas`

### 怎么解决

**先退出 Python 交互环境**（三种任选）：

| 方法 | 操作 |
|---|---|
| 输入 `exit()` | 回车 |
| 输入 `quit()` | 回车 |
| 快捷键 | `Ctrl + Z` 然后回车（Windows） |

退出后提示符会变成 `PS E:\AI结果\量化>`，这时才能执行 PowerShell 命令。

**然后**，在正确的地方运行：

```powershell
cd /d "E:\AI结果\量化"
.venv\Scripts\python.exe src\my_d01_analysis.py
```

### 一个关键区别：路径里的斜杠

| 场景 | 路径写法 |
|---|---|
| PowerShell / cmd 命令行 | 反斜杠 `\` 或正斜杠 `/` 都能识别 |
| **Python 代码里的字符串** | 反斜杠是转义符，**必须写 `r"E:\..."` 或双反斜杠** |
| VS Code 的"运行"按钮 | 它自己处理，你只要选对解释器 |

---

## 三、错误 2：VS Code 用了错误的解释器（你这次的主因）

### 证据（本机实测）

```
C:\...\Python311\python.exe          3.11.2   缺失包: 无
E:\work\anaconda\python.exe          3.12.7   缺失包: ['akshare']   ← 用它跑数据脚本必然报错
E:\AI结果\量化\.venv\Scripts\python.exe  3.11.2   缺失包: 无        ← 应该用这个
```

而且项目里**原本没有任何 `.vscode` 配置文件**，所以 VS Code 自己在猜——
它找到了 Anaconda，于是跑数据脚本就 `ModuleNotFoundError: No module named 'akshare'`。

### 已修复：我加了两个配置文件

**`.vscode/settings.json`** —— 把解释器钉死在 `.venv`：

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
  "python.terminal.activateEnvironment": true,
  "python.analysis.extraPaths": ["${workspaceFolder}\\src"]
}
```

**`.vscode/launch.json`** —— 按 F5 直接跑，不用敲命令：

| 配置名 | 做什么 |
|---|---|
| `Python: 当前文件（用 .venv）` | 跑你当前打开的任意文件 |
| `Day1: 抓数据` | 跑 `src/my_d01_data.py` |
| `Day1: 做分析` | 跑 `src/my_d01_analysis.py` |
| `Day1: 全部测试` | 跑 14 项 pytest 测试 |

### 你还需要手动确认一次（很重要）

1. 关掉 VS Code，重新打开 `E:\AI结果\量化` 这个文件夹（让它读取新配置）
2. `Ctrl + Shift + P` → 输入 `Python: Select Interpreter` → 回车
3. 选择带 **`.venv`** 的那一项：`.venv\Scripts\python.exe`
4. 看左下角状态栏，应该显示 `Python 3.11.2 ('.venv': venv)` 之类的字样

**如果状态栏还显示 Anaconda**，就是没选对，重做第 2 步。

### 怎么自查"当前用的是哪个 Python"

在 VS Code 的终端里敲：

```powershell
python -c "import sys; print(sys.executable)"
```

- 输出含 `.venv` → 对了
- 输出含 `anaconda` → 还是 Anaconda，重选解释器

---

## 四、错误 3：Windows 路径引发的转义警告

### 症状

```
SyntaxWarning: invalid escape sequence '\A'
```

### 原因

我给你的教学文件里，docstring 写了运行示例：

```python
"""Day 1 教学版

运行：
    cd /d "E:\AI结果\量化"        ← 这里的 \A 被 Python 当成转义序列
"""
```

Python 里 `\A`、`\S`、`\p` 这类都**不是**合法转义序列（合法的是 `\n` 换行、`\t` 制表、`\\` 反斜杠本身），
所以 Python 3.12 会警告"你这可能写错了"。

### 修复（已对 3 个文件做完）

在 docstring 前面加一个 `r`，表示"原始字符串"，反斜杠不再转义：

```python
r"""Day 1 教学版

运行：
    cd /d "E:\AI结果\量化"        ← 加了 r 之后，\A 就是普通的两个字符
"""
```

**规则**：**只要字符串里出现 Windows 路径，就在引号前加 `r`**。
这个规则适用于 docstring，也适用于普通字符串：`path = r"E:\AI结果\量化\data"`。

**另一种等价写法**：把反斜杠写成两个 `"E:\\AI结果\\量化"`（不推荐，难看且容易漏）。

---

## 五、错误 4：运行后毫无反应（静默失败）

### 症状

```
PS E:\AI结果\量化> .venv\Scripts\python.exe src\my_d01_analysis.py
PS E:\AI结果\量化>            ← 光标直接回来，没有任何输出
```

### 原因

文件里只有函数定义，**没有任何地方调用它们**：

```python
def main():          # ← 只是"把菜谱写下来"
    print("...")

# ← 缺了这两行："照着菜谱做菜"
if __name__ == "__main__":
    raise SystemExit(main())
```

### 排查口诀

1. 文件末尾有没有 `if __name__ == "__main__":` ？
2. 里面有没有**真的调用**（`main()` 或 `raise SystemExit(main())`）？
3. 有没有 `print` 写在函数里、但那个函数从未被调用？

**这三条能定位 90% 的"静默失败"。**

---

## 六、三种正确的运行方式（选最顺手的）

### 方式 A：双击 `.bat` 启动器（最省事，零命令）

我在项目根目录放了三个：

| 文件 | 作用 |
|---|---|
| `运行-抓数据.bat` | 跑数据脚本并显示退出码 |
| `运行-做分析.bat` | 跑分析脚本并显示退出码 |
| `运行-全部测试.bat` | 跑 14 项测试并显示退出码 |

双击即可，跑完会停住让你看结果（`pause`），看够了按键关闭。

### 方式 B：VS Code 里按 F5（推荐日常用）

1. 打开要运行的文件（比如 `src/my_d01_analysis.py`）
2. 按 `F5`，或点左侧"运行和调试"图标选配置
3. 输出显示在下方的"终端"面板

前提：按第三节确认过解释器选的是 `.venv`。

### 方式 C：手动敲命令（最可控，出错信息最全）

VS Code 里按 `` Ctrl + ` `` 打开终端，然后：

```powershell
cd /d "E:\AI结果\量化"
.venv\Scripts\python.exe src\my_d01_analysis.py
```

**如果你喜欢输 `python` 而不是完整路径**，先激活虚拟环境：

```powershell
.venv\Scripts\Activate.ps1     # 提示符会变成 (.venv) PS E:\AI结果\量化>
python src\my_d01_analysis.py
deactivate                      # 用完退出
```

> 如果 `Activate.ps1` 报"禁止运行脚本"，执行一次：
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` 然后输入 `Y`。

---

## 七、我做了什么兜底（你现在用哪个 Python 都能跑）

| 操作 | 结果 |
|---|---|
| 把 akshare 装进 Anaconda | Anaconda 现在也能跑数据脚本（实测通过） |
| 加了 `.vscode/settings.json` | 新建终端自动指向 `.venv` |
| 加了 `.vscode/launch.json` | F5 就能跑，不会再用错解释器 |
| 修了 3 个文件的转义警告 | Python 3.12 下不再报警告 |
| 加了 3 个 `.bat` | 不敲任何命令也能运行 |

**但请记住**：兜底是为了"万一"。**正确习惯是用 `.venv`**——
因为项目依赖的版本是固定的（见 `docs/requirements-lock.txt`），
用别的 Python 迟早会遇到"这个版本能跑那个版本不能跑"的问题。

---

## 八、一页速查

| 你看到的现象 | 第一反应 |
|---|---|
| `SyntaxError: invalid syntax` 指向 `&` 或路径 | 你不在终端里，在 Python 里。先 `exit()` |
| 提示符是 `>>>` | Python 交互环境，敲 `exit()` 退出 |
| `ModuleNotFoundError` | 用 `python -c "import sys;print(sys.executable)"` 看是哪个 Python |
| 输出含 `anaconda` | `Ctrl+Shift+P` → `Python: Select Interpreter` → 选 `.venv` |
| `SyntaxWarning: invalid escape sequence` | 给那个字符串加 `r` 前缀 |
| 运行毫无反应 | 检查有没有 `if __name__ == "__main__":` 和真正的调用 |
| 终端出现 `[exit code: 1]` 但有正常输出 | 可能是管道截断，不算失败；用 `echo $LASTEXITCODE` 单独确认 |
| 不知道 `python` 指向谁 | `where.exe python` 看顺序，`python -c "import sys;print(sys.executable)"` 看实际 |
