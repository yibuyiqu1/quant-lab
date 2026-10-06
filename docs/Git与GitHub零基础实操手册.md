# Git 与 GitHub 零基础实操手册（量化项目专用）

> 你现在的状态：只会基础 Python 和简单调包，电脑上没装 git。
> 这份手册的目标：**30 分钟内**装好 git、建好第一个 GitHub 仓库、把代码推上去，并且理解"为什么要这么做"。

---

## 一、先搞清楚：Git、GitHub、仓库分别是什么

| 名词 | 是什么 | 类比 |
|---|---|---|
| **Git** | 装在你电脑上的**版本控制软件** | 游戏的"存档系统"，每次保存一个可以随时回退的存档点 |
| **GitHub** | 一个**网站**，用来存放 Git 仓库 | 云盘，但专门给代码用，而且能展示给别人看 |
| **仓库（repository / repo）** | 一个被 Git 管理的文件夹，含全部历史记录 | 一个"项目档案袋" |
| **commit（提交）** | 一次存档：记录"这次改了什么、为什么改" | 存档点 + 一句备注 |
| **push（推送）** | 把本地存档上传到 GitHub | 上传云盘 |
| **clone（克隆）** | 把 GitHub 上的仓库下载到本地 | 从云盘下载 |
| **branch（分支）** | 平行开发线，默认叫 `main` | 从主线分出去的试验田 |

**关键理解**：Git 是离线的（没网也能存档、回退），GitHub 是线上的（备份 + 展示 + 协作）。两者独立，通过 push/pull 同步。

---

## 二、GitHub 对一个量化求职者到底有什么用

不是"程序员才需要"，对你至少有 5 个直接作用：

1. **简历上的可验证证据**。面试官不会只听你说"我会写回测"，他会点开你的 GitHub 看代码。一个结构清晰、有 README、有提交记录的仓库，胜过简历上十行形容词。
2. **学习过程的存档**。你现在每天写的东西，半年后会变成"我做过哪些研究"的完整档案。没有仓库，三个月后你只剩下一堆散落的 `.ipynb`。
3. **可复现性证明**。量化研究最忌讳"结果只有我有"。仓库 + `requirements.txt` + 固定随机种子 = 别人能跑出同样结果，这正是研究员的核心素养。
4. **持续投入的证据**。绿色贡献格子、连续的 commit 记录，直观显示你在长期投入——面试官很吃这一套。
5. **防丢失 + 敢试错**。改坏了可以一条命令回退；想试新想法就开个分支，不污染主线。

**量化面试官会看什么（按顺序）**：README 写没写清 → 代码有没有结构 → 有没有回测/研究类项目 → commit 记录是不是"一次性上传"（一次性上传 = 从别处抄的，几乎必然被识破）。

---

## 三、第一步：装 Git（Windows）

### 方式 A：官方安装包（推荐，最稳）

1. 打开 https://git-scm.com/download/win
2. 下载 **64-bit Git for Windows Setup**
3. 一路"Next"，**遇到下面这两个选项时注意**：
   - **Default editor**：选 `Notepad` 或 `Visual Studio Code`（别选 Vim，新手会卡在退不出来）
   - **Adjusting your PATH environment**：保持默认 `Git from the command line and also from 3rd-party software`
   - **Line ending conversions**：选 `Checkout as-is, commit as-is`（避免 Windows 换行符把文件"全改了"）
4. 装完**关掉所有终端窗口，重新打开一个**（PATH 需要重启才生效）

### 验证安装

```powershell
git --version
```

看到类似 `git version 2.47.0.windows.1` 就成功了。如果提示"无法识别"，说明 PATH 没生效 → 重启终端，还不行就重启电脑。

### 方式 B：winget（如果你喜欢命令行）

```powershell
winget install --id Git.Git -e --source winget
```

装完同样要重开终端。

---

## 四、第二步：配置身份（只做一次）

Git 需要知道"这个存档是谁提交的"，否则不允许 commit。

```powershell
git config --global user.name "你的名字拼音"
git config --global user.email "你的邮箱@example.com"
git config --global init.defaultBranch main
git config --global core.quotepath false
git config --global core.autocrlf false
```

**逐条解释**：

| 命令 | 作用 |
|---|---|
| `user.name` / `user.email` | 提交记录里显示的作者信息，**邮箱建议和 GitHub 注册邮箱一致**（这样提交能关联到你的账号，显示在贡献格子里） |
| `init.defaultBranch main` | 新仓库默认分支叫 `main`（GitHub 现在的标准，避免 main/master 混乱） |
| `core.quotepath false` | 让中文文件名正常显示，而不是 `\346\226\207...` |
| `core.autocrlf false` | 不让 Git 自动改换行符，避免"我什么都没改，却显示整个文件都变了" |

验证：

```powershell
git config --global --list
```

---

## 五、第三步：在 GitHub 上创建仓库

### 5.1 注册账号（如果还没有）

1. 打开 https://github.com/signup
2. 用户名建议：**拼音 + 专业相关**，例如 `zhangsan-quant`。不要用奇怪的数字串，面试官会看到。
3. 验证邮箱（必须，否则不能推送）

### 5.2 创建仓库的两种方式

**方式 A：网页点选（最简单）**

1. 右上角 `+` → `New repository`
2. 填写：
   - **Repository name**：`quant-lab`（全小写，用连字符，别用中文和空格）
   - **Description**：`量化研究学习仓库：概率地基、因子研究、回测框架`
   - **Public / Private**：**建议 Public**（求职展示用；如果暂时不想公开就选 Private，以后可以改）
   - **Initialize this repository with**：**全部不勾选**（因为本地已经有项目了，勾了会冲突）
3. 点 `Create repository`
4. 创建后页面会显示一段命令，先不用管，下面我们用更省事的方式。

**方式 B：用 GitHub CLI（推荐，一条命令搞定）**

先装 gh：

```powershell
winget install --id GitHub.cli -e --source winget
# 重开终端后：
gh auth login
```

`gh auth login` 的交互选择（照着选）：

```
? What account do you want to log into?          → GitHub.com
? What is your preferred protocol for Git ops?   → HTTPS
? Authenticate Git with your GitHub credentials? → Yes
? How would you like to authenticate?            → Login with a web browser
# 复制屏幕上的一次性代码 → 浏览器里粘贴 → 授权
```

然后建仓库并推送（在项目文件夹里执行）：

```powershell
gh repo create quant-lab --public --source=. --remote=origin --push
```

这一条命令做了三件事：在 GitHub 上建仓库、把本地仓库关联为 `origin`、把当前分支推上去。

---

## 六、第四步：把本地项目变成仓库并推送

假设你的项目在 `E:\量化`（换成你自己的路径）。

### 6.1 先加一个 `.gitignore`（非常重要）

**为什么**：有些文件不该上传——数据文件（几十 MB，GitHub 单文件限制 100 MB）、虚拟环境（几千个文件）、临时文件。不排除的话，仓库会变得又大又乱。

在项目根目录建 `.gitignore`，内容：

```gitignore
# 虚拟环境
.venv/
venv/

# Python 缓存
__pycache__/
*.pyc
.ipynb_checkpoints/

# 数据（体积大，且可重新下载）
data/raw/*
data/clean/*
!data/raw/.gitkeep
!data/clean/.gitkeep

# 大体积资料（教材 PDF 不上传）
资料库/*.pdf
*.part

# 编辑器
.vscode/
.idea/
```

> 数据不上传是行规：别人 `clone` 你的仓库后，用你的抓取脚本重新下载即可。README 里要写清"数据怎么获取"。

### 6.2 初始化并提交

```powershell
cd E:\量化

git init                      # 把当前文件夹变成 Git 仓库，生成隐藏的 .git 目录
git add .                     # 把当前所有改动加入"暂存区"（准备存档的内容）
git status                    # 看一眼：哪些是新增(绿)、哪些被忽略
git commit -m "init: 项目结构 + 数据抓取 + 第一个可复现分析"
```

**三条命令在干什么**：

- `git init`：只在第一次执行。之后这个文件夹就受 Git 管理了。
- `git add .`：Git 的"存档"分两步——先选要存哪些改动（暂存），再真正存（commit）。`. ` 表示当前目录全部。
- `git commit -m "..."`：真正生成存档点。`-m` 后面是说明，**写清做了什么**，别写 "update"。

第一次 commit 后，用 `git log --oneline` 可以看到：

```
a1b2c3d init: 项目结构 + 数据抓取 + 第一个可复现分析
```

### 6.3 关联远程仓库并推送

```powershell
# 已用 gh repo create 的话，跳过 add remote 这步
git remote add origin https://github.com/你的用户名/quant-lab.git
git remote -v                 # 验证：应显示 origin 的两行 fetch/push 地址

git push -u origin main       # 第一次推送，-u 表示以后直接 git push 就行
```

**关于密码**：GitHub 从 2021 年起不再接受账号密码推送，需要 **Personal Access Token (PAT)**：

1. GitHub → 右上角头像 → `Settings` → 左侧最下 `Developer settings` → `Personal access tokens` → `Tokens (classic)` → `Generate new token (classic)`
2. Note 填 `my-windows-pc`，Expiration 选 `90 days`，勾选 **`repo`** 权限
3. 生成后**立刻复制**（页面关掉就再也看不到）
4. 推送时提示 `Username:` 输入 GitHub 用户名，`Password:` **粘贴这个 token**（不是你的登录密码）
5. 想免得每次输入：`git config --global credential.helper manager`（Windows 会记住）

---

## 七、日常使用：每天 4 条命令

掌握这 4 条就够用 90% 的场景：

```powershell
git status                        # 看现在有什么改动（最常用，随时敲）
git add -A                        # 把所有改动加入暂存区
git commit -m "d05: 加入条件期望的数值实验"   # 存档
git push                          # 上传到 GitHub
```

**Commit message 规范（面试官真的会看）**：

| 好的写法 | 差的写法 |
|---|---|
| `d05: 实现条件期望的最优L2预测实验` | `update` |
| `fix: 修正前复权导致的收益率漂移` | `修改` |
| `feat: 回测框架加入手续费与滑点` | `111` |
| `docs: 补充因子研究的样本外检验方法` | `final version` |

**建议格式**：`类型: 做了什么`，类型用 `feat`（新功能）/ `fix`（修 bug）/ `docs`（文档）/ `refactor`（重构）/ `dNN`（第几天）。

---

## 八、撤销与回退（新手最需要的救命命令）

| 场景 | 命令 | 说明 |
|---|---|---|
| 改乱了某个文件，想还原成上次提交的样子 | `git restore 文件名` | 丢弃未提交的修改（**不可恢复**） |
| `git add` 错了，想撤出暂存区 | `git restore --staged 文件名` | 文件内容不动，只是不再准备提交 |
| commit message 写错了（还没 push） | `git commit --amend -m "新的说明"` | 修改最后一次提交 |
| 想看某个文件的历史改动 | `git log -p 文件名` | 逐次提交的差异 |
| 想回到某个历史版本（看代码） | `git checkout a1b2c3d` | 进入"分离头指针"状态，看完用 `git checkout main` 回来 |
| 想把项目恢复到某个旧版本（危险） | `git reset --hard a1b2c3d` | **会删掉之后的所有改动**，新手慎用 |
| 想看自己改了什么 | `git diff` | 未暂存的差异 |

**记住一条**：只要 commit 过，就几乎不会真的丢失东西。真的慌，先 `git stash` 把当前改动收起来，再慢慢查。

---

## 九、常见报错与处理

| 报错 | 原因 | 处理 |
|---|---|---|
| `fatal: not a git repository` | 当前目录不是仓库（可能在子目录） | `cd` 到项目根目录，或 `git init` |
| `Please tell me who you are` | 没配置 user.name/email | 回到第四节配置 |
| `failed to push some refs ... rejected` | GitHub 上有本地没有的提交 | 先 `git pull --rebase origin main` 再 push |
| `Authentication failed` | token 失效或用了登录密码 | 重新生成 PAT，`git config --global credential.helper manager` 后重输 |
| `LF will be replaced by CRLF` | 换行符警告 | 执行第五节那条 `core.autocrlf false`，可忽略警告 |
| `file is 120.00 MB; this exceeds GitHub's file size limit` | 传了大数据文件 | 加 `.gitignore`，用 `git rm --cached 大文件` 从索引移除 |
| 中文文件名显示成 `\346\226\207` | 没关 quotepath | `git config --global core.quotepath false` |
| `error: remote origin already exists` | 重复添加 | `git remote set-url origin 新地址` |

---

## 十、给你的仓库设计一个"能拿去面试"的结构

```
quant-lab/
├─ README.md              ← 最重要：写清这是什么、怎么跑、有什么结论
├─ requirements.txt       ← 依赖清单，别人照着装就能跑
├─ .gitignore
├─ src/                   ← 可复用代码（函数化，不是复制粘贴）
│   ├─ io.py              ← 数据读写
│   ├─ clean.py           ← 清洗
│   ├─ factor.py          ← 因子计算
│   └─ backtest.py        ← 回测框架
├─ notebooks/             ← 探索性分析（命名 d01_xxx.ipynb）
├─ reports/               ← 研究报告与图表
│   ├─ figs/
│   └─ d01_result.md
└─ docs/                  ← 笔记、术语表
```

**README.md 模板（直接抄）**：

```markdown
# quant-lab

A 股量化研究学习仓库：概率地基 → 因子研究 → 回测框架。
目标：成为头部量化研究员。

## 已完成

| 日期 | 内容 | 产出 |
|---|---|---|
| D1 | 概率空间与 σ-代数；环境搭建 | [notes](d01.md) |
| D2 | 沪深300 收益分布与肥尾检验 | [report](../reports/d01_result.md) |

## 环境

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## 怎么跑

\`\`\`bash
python src/setup_day1.py          # 抓取数据到 data/
python src/my_d01_analysis.py  # 生成统计报告与图
\`\`\`

## 数据来源

沪深300 日线通过 akshare 获取：`ak.stock_zh_index_daily(symbol="sh000300")`，
2002-01-07 起，共 6000+ 个交易日。

## 主要结论

- 日对数收益峰度 7.69（正态为 3），|z|>3 的实际占比 1.78% vs 正态 0.27%
- 因此后续因子检验不使用正态假设，改用 bootstrap 与稳健统计量
```

---

## 十一、今天就能做完的清单（约 30 分钟）

- [ ] 装 Git 并重开终端，`git --version` 有版本号
- [ ] 配好 5 条 `git config` 命令
- [ ] 注册 GitHub 并验证邮箱
- [ ] 建 `quant-lab` 仓库（Public）
- [ ] 在项目根目录建 `.gitignore` 与 `README.md`
- [ ] `git init` → `git add .` → `git commit -m "init: 项目结构 + 数据抓取"` → `git push -u origin main`
- [ ] 打开网页确认代码和 README 都在
- [ ] 把仓库地址加到简历和邮箱签名

做完这一遍，你对 Git 的恐惧就结束了。之后每 3-5 天推一次，让贡献格子连续起来。
