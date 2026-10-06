# -*- coding: utf-8 -*-
"""生成《量化研究员启动计划》工作簿：21天启动营 + 90天路线 + 打卡表。"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import CellIsRule, DataBarRule
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

OUT = r"E:\AI结果\量化\量化研究员启动计划.xlsx"

TITLE_FILL = PatternFill("solid", fgColor="1F3864")
TITLE_FONT = Font(name="Microsoft YaHei", size=13, bold=True, color="FFFFFF")
HDR_FILL = PatternFill("solid", fgColor="2E5C9A")
HDR_FONT = Font(name="Microsoft YaHei", size=10, bold=True, color="FFFFFF")
SEC_FILL = PatternFill("solid", fgColor="D9E2F3")
SEC_FONT = Font(name="Microsoft YaHei", size=11, bold=True, color="1F3864")
BODY = Font(name="Microsoft YaHei", size=10)
BOLD = Font(name="Microsoft YaHei", size=10, bold=True)
THIN = Side(style="thin", color="B4C6E7")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
WRAPC = Alignment(wrap_text=True, vertical="center", horizontal="center")

wb = Workbook()


def style_header(ws, ncol, row=1, height=26):
    for c in range(1, ncol + 1):
        cell = ws.cell(row, c)
        cell.fill = HDR_FILL
        cell.font = HDR_FONT
        cell.alignment = WRAPC
        cell.border = BORDER
    ws.row_dimensions[row].height = height


def style_body(ws, first_row, last_row, ncol, widths, center_cols=(), heights=36):
    for c, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(c)].width = w
    for r in range(first_row, last_row + 1):
        ws.row_dimensions[r].height = heights
        for c in range(1, ncol + 1):
            cell = ws.cell(r, c)
            cell.border = BORDER
            cell.font = BODY
            cell.alignment = WRAPC if c in center_cols else WRAP


# ============================================================ 0 说明
ws = wb.active
ws.title = "0-怎么用"
ws.column_dimensions["A"].width = 20
ws.column_dimensions["B"].width = 110
rows = [
    ("量化研究员启动计划", ""),
    ("今天该做什么", "打开『1-21天启动营』，找到 Day 1，照『今日任务』做完，用『验收标准』自查能否复述/复现，然后在『5-每日打卡』记 30 秒。不要看后面的天，做完一天再翻下一天。"),
    ("每日时间预算", "工作日 3.5 小时：数学 1.5h + 编程 1.5h + 打卡复盘 0.5h。周末 6 小时：数学 2h + 编程 3h + 写文档 1h。低于这个量，90 天计划必然延期。"),
    ("两条并行线", "A 线=数学（概率→随机分析→统计/ML→金融）；B 线=工程（环境→pandas→数据→回测框架）。A 线每天都做，B 线从 Day 1 就并行，两线在 Day 22 之后的项目里汇合。"),
    ("为什么这么排", "概率论是量化的通用货币，也是笔试面试的第一道门；随机分析决定你能否理解衍生品与扩散模型；统计学习决定你能否做出可验证的 Alpha；工程决定你能不能把想法跑出来。顺序不能颠倒。"),
    ("验收的硬标准", "每天结束时必须能回答：①今天这个定义/定理，我能不能不看书画出来并证明关键一步？②今天的代码能不能重跑出同样结果？③今天的内容能不能用 3 句话讲给同学听？三条都过才算完成。"),
    ("资料在哪", "同目录『资料库/』文件夹，分类存放；下载报告见『资料库/_下载报告.tsv』。教材类（Shreve/Hull 等商业书）请用图书馆或正版渠道，公开替代品已在资料库中标注。"),
    ("每周日必做", "①更新『5-每日打卡』②把本周所有代码提交一次 Git ③写一页周报（学到的 3 件事 + 卡住的 2 个问题 + 下周调整）④在『2-90天路线』里把完成项标 ✅。"),
]
for i, (a, b) in enumerate(rows, start=1):
    ws.cell(i, 1, a)
    ws.cell(i, 2, b)
    ws.cell(i, 1).font = TITLE_FONT if i == 1 else SEC_FONT
    ws.cell(i, 2).font = TITLE_FONT if i == 1 else BODY
    ws.cell(i, 1).fill = TITLE_FILL if i == 1 else SEC_FILL
    ws.cell(i, 2).fill = TITLE_FILL if i == 1 else PatternFill("solid", fgColor="F2F5FB")
    ws.cell(i, 1).alignment = WRAPC
    ws.cell(i, 2).alignment = WRAP
    ws.row_dimensions[i].height = 24 if i == 1 else 54
ws.freeze_panes = "A2"

# ============================================================ 1 21天启动营
ws = wb.create_sheet("1-21天启动营")
hdr = ["天", "阶段", "A线·数学与理论（知识点，精确到节）", "B线·编程与工程（任务，精确到函数）",
       "今日验收标准（可客观自查）", "建议时长", "完成"]
data = [
    [1, "概率地基", "概率空间：σ-代数、测度、可测性；概率的连续性。读 Durrett 第1章 1.1-1.2 + 18.175 Lec1。手写练习：证明单调序列的连续性 P(Aₙ)↑P(∪Aₙ)",
     "装好环境：Python 3.11+、pandas、numpy、matplotlib、jupyter；建 GitHub 私有仓库 quant-lab；写第一个 notebook：读本地 CSV → 描述统计 → 出图",
     "能不看书写出 σ-代数定义并证明『可数并封闭』；notebook 能一键重跑出同样的图", "3.5h", ""],
    [2, "概率地基", "随机变量与分布函数：分布函数三大性质、离散/连续/奇异、随机变量是 Borel 可测映射。Durrett 1.3 + 18.175 Lec2。经典题：两个均匀分布之和的密度（卷积）",
     "pandas 向量化：不用 for 循环完成分组统计 groupby.transform、rolling、shift；用 numpy 手写一次『两个均匀分布相加』的蒙特卡洛并和解析解对比",
     "能解释为什么分布函数右连续；能把任何一个 for 循环改写成向量化写法", "3.5h", ""],
    [3, "概率地基", "期望与积分：Lebesgue 积分构造、单调收敛定理 MCT、Fatou 引理、控制收敛定理 DCT。Durrett 1.4-1.5。练习：用 DCT 证明期望的连续性",
     "数据获取：用 akshare 或 baostock 拉 2018 年至今沪深300成分股日线；写 download.py 并落盘为 parquet；计算各股票日收益率与波动率排序",
     "能写出 MCT/DCT 的条件并各举一个反例；本地有可复现的数据落盘脚本与 parquet 文件", "3.5h", ""],
    [4, "概率地基", "独立性与乘积测度：Fubini/Tonelli 定理、独立性刻画、Borel-Cantelli 引理。Durrett 1.6-1.7 + 2.3。练习：用 Borel-Cantelli 证明『几乎必然无穷多次』",
     "数据清洗：复权价格处理（前复权/后复权差异）、停牌与新股剔除法、缺失值对齐；写出可复用的 clean.py",
     "能独立证明 Borel-Cantelli 两个方向；能说出前复权与后复权对收益率计算的影响", "3.5h", ""],
    [5, "概率地基", "四种收敛：几乎必然、依概率、Lᵖ、依分布，以及相互蕴含关系与反例。Durrett 2.1-2.2 + 18.175 Lec5",
     "描述统计与因子初探：算 20 日动量、20 日波动率、成交额对数；做 5 分位分层看未来 5 日收益（此刻先不扣成本，感受一下）",
     "能画出收敛关系图并各举一个『不反向蕴含』的反例；能得到一张分层收益柱状图", "3.5h", ""],
    [6, "概率地基", "弱大数律：切比雪夫与 Khintchine；特征函数定义与性质。Durrett 2.2 + 2.5前半",
     "经典概率题专项（笔试第一关）：生日问题、优惠券收集、Monty Hall、两孩悖论、投硬币直到出现 HT 的期望步数。每题写解析解 + 蒙特卡洛验证",
     "5 道经典题都能写出解析推导并用模拟验证；误差随样本量下降符合预期", "3.5h", ""],
    [7, "概率地基", "强大数律：Borel 强大数律、Kolmogorov 三级数定理思路。Durrett 2.4。第 1 周复盘：把前 6 天定义串成一张思维导图",
     "第一周复盘 + 周报：整理代码结构（data/ src/ notebooks/），写 README，提交 Git；总结 3 个卡住的点",
     "能讲清『几乎必然收敛』比『依概率收敛』强在哪；仓库有 README 且结构清晰", "5h", ""],
    [8, "概率地基", "中心极限定理：Lindeberg-Feller、Lyapunov、i.i.d. 情形；正态近似的误差。Durrett 3.1-3.4",
     "蒙特卡洛方法：用 numpy 实现 MC 估计 π 与欧式期权价格，比较不同样本量与方差缩减（对偶变量法）的效果",
     "能写出 CLT 的两种形式与使用条件；能画出『误差 ~ 1/√n』的收敛图", "3.5h", ""],
    [9, "概率地基", "Lᵖ 空间与不等式：Hölder、Minkowski、Jensen、Cauchy-Schwarz；一致可积性定义。Durrett 1.5 + 2.2",
     "随机数工程：固定随机种子、可复现实验模板（config + log + seed）；把 Day 8 的 MC 实验重构成可复现脚本",
     "能独立证明 Hölder 不等式（用 Young 不等式）；同一个 config 两次运行结果完全一致", "3.5h", ""],
    [10, "条件期望", "条件期望：以 σ-代数与随机变量为条件的定义、存在唯一性、『可测+积分相等』证明法。Durrett 4.1 + 18.175 Lec6（本周核心，务必吃透）",
     "线性回归从零实现：用 numpy 正规方程解 β，与 sklearn 结果对比；推导 β 的方差表达式并在模拟中验证",
     "能解释『条件期望是最优 L² 预测』并证明；模拟的 β 方差与理论值吻合", "4h", ""],
    [11, "条件期望", "条件期望性质：塔性质（全期望公式）、条件 Jensen、条件方差分解 Var(X)=E[Var(X|Y)]+Var(E[X|Y])。Durrett 4.1",
     "回归诊断：残差图、异方差、多重共线性（VIF）、异常值影响；用真实股票收益做一次截面回归并解释 R²",
     "能手推条件方差分解公式；能指出你回归结果中最可疑的一个假设违反", "3.5h", ""],
    [12, "条件期望", "条件分布与正则条件概率；『Borel 悖论』式反例（条件概率不能随意定义）。Durrett 4.1.3。经典题：两孩问题、Monty Hall 的条件期望视角",
     "时间序列入门：计算并画 ACF/PACF，做平稳性检验（ADF），理解自相关对 t 检验的破坏（有效样本量问题）",
     "能说明为什么『条件概率一般不能取版本』；能演示忽略自相关导致 t 值虚高", "3.5h", ""],
    [13, "鞅", "鞅的定义与例子：随机游走、Doob 鞅、分支过程、似然比鞅。Durrett 5.1-5.2 + 18.175 Lec7",
     "从零实现最小二乘 + 岭回归（含闭式解与梯度下降两条路）；比较 L1/L2 正则的几何直觉",
     "能自己构造 3 个鞅的例子并证明；两条路的解在容差内一致", "3.5h", ""],
    [14, "鞅", "停时与可选停时定理（OST）：条件、应用、赌徒破产问题的完整解法。Durrett 5.3-5.4",
     "模拟赌徒破产：解析解 vs 蒙特卡洛；画出『资金 vs 破产概率』曲线；第 2 周复盘与周报",
     "能写出 OST 成立的条件并说明何时失效；模拟曲线与解析解重合", "5h", ""],
    [15, "鞅", "鞅收敛定理、上穿不等式、Doob 分解。Durrett 5.5-5.6",
     "回测框架 v0：事件驱动骨架（策略接口 + 撮合 + 净值曲线），先只支持日频多空组合",
     "能陈述鞅收敛定理并解释为何需要 L¹ 有界；框架能跑通一个 buy&hold 策略", "3.5h", ""],
    [16, "鞅", "一致可积鞅、Lᵖ 收敛、鞅的 L² 结构。Durrett 5.6 + 18.175 Lec8",
     "回测框架 v1：加入手续费、滑点、涨跌停、T+1 约束；写一份『成本假设说明』文档",
     "能证明 UI + a.s. 收敛 ⇒ L¹ 收敛；能定量说明手续费对 20 日动量策略的侵蚀", "4h", ""],
    [17, "应用", "随机游走与布朗运动雏形：反射原理、首达时间分布、重对数律简介。Durrett 6-7 选读",
     "用蒙特卡洛验证首达时间分布（反射原理），并模拟布朗运动路径；画出 √t 标度律",
     "能用反射原理推出首达时间分布；模拟的标度指数接近 0.5", "3.5h", ""],
    [18, "应用", "马尔可夫链：转移矩阵、常返/瞬态、平稳分布、细致平衡。Durrett 6 章",
     "马尔可夫链实战：把 A 股市场状态划成牛/震荡/熊（用收益与波动分位），估计转移矩阵与平稳分布",
     "能求平稳分布并判断是否常返；能报告状态转移矩阵与平均停留期", "3.5h", ""],
    [19, "应用", "布朗运动构造与性质：高斯过程视角、协方差结构、二次变差、不可微性。Durrett 8 章 + 18.S096 Lec1-2",
     "模拟布朗运动：随机游走细分的收敛、二次变差的数值验证（Σ(ΔB)²→t）",
     "能手写布朗运动的三条定义性质；数值验证二次变差收敛到 t", "3.5h", ""],
    [20, "应用", "随机积分动机：为什么需要 Itô 积分、简单过程积分、Itô 等距。18.S096 Lec3-4",
     "第一个完整因子研究：横截面动量/反转因子，滚动样本外、分层组合、成本后收益、稳健性检验（分年/分市值）",
     "能写出 Itô 等距并说明其概率意义；因子研究报告初稿（含成本后 IC 与净值）", "5h", ""],
    [21, "结营验收", "自测：闭卷写出 σ-代数/条件期望/鞅/OST/CLT 的定义与条件；重做 Day 6 的 5 道经典题（限时 40 分钟）",
     "把 21 天代码整理成一个可展示仓库；写一份《启动营复盘》并规划第 22-42 天（随机分析）",
     "21 天全部验收通过；仓库有 README + 3 个 notebook + 1 份报告；能对同学讲 10 分钟", "6h", ""],
]
ws.append(hdr)
for row in data:
    ws.append(row)
style_header(ws, len(hdr))
style_body(ws, 2, len(data) + 1, len(hdr), [5, 11, 52, 52, 42, 9, 8], center_cols=(1, 2, 6, 7), heights=92)
ws.freeze_panes = "C2"
dv = DataValidation(type="list", formula1='"待开始,进行中,已完成"', allow_blank=True)
ws.add_data_validation(dv)
dv.add(f"G2:G{len(data)+1}")

# ============================================================ 2 90天路线
ws = wb.create_sheet("2-90天路线")
hdr = ["阶段", "天数", "主题", "核心知识点清单", "产出物（硬交付）", "完成标志"]
data = [
    ["启动营", "D1-D21", "概率论地基 + 工程环境",
     "σ-代数与测度、可测性、MCT/DCT、独立性、Borel-Cantelli、四种收敛、大数律、CLT、Lᵖ与不等式、条件期望、鞅、停时与OST、鞅收敛、随机游走、马尔可夫链、布朗运动",
     "回测框架 v1（含成本与交易约束）、1 份因子研究报告、5 道经典概率题解析、可复现实验模板",
     "闭卷写出所有核心定义并证明关键一步"],
    ["随机分析", "D22-D42", "Itô 微积分 + 衍生品定价",
     "简单过程积分、Itô 等距、Itô 公式（一维/多维）、鞅表示定理、Girsanov 与测度变换、SDE 存在唯一性、Euler-Maruyama/Milstein 数值解、Feynman-Kac、BS 方程两种推导、希腊字母、蒙特卡洛定价与方差缩减",
     "BS 定价库（解析+MC 两条路）、蒙特卡洛期权定价与 Greeks、随机微分方程数值解实验、读书笔记 1 份",
     "能手推 Itô 公式与 Girsanov，并解释 BS 两种推导的等价性"],
    ["统计与ML", "D43-D70", "统计推断 + 时间序列 + 金融ML",
     "M估计与渐近正态、delta 方法、假设检验与多重检验校正（Bonferroni/FDR）、重采样与 bootstrap、正则化、树模型与 GBDT、特征重要性、交叉验证的金融修正（purged/embargoed CV）、平稳性与协整、GARCH、状态空间、PyTorch 基础",
     "GBDT 横截面收益预测 vs 线性基准对比报告、purged CV 工具函数、时间序列建模 notebook、一篇论文复现",
     "能解释你的模型为什么不会过拟合，并用样本外数据自证"],
    ["金融与项目", "D71-D90", "市场制度 + 第一个完整 Alpha",
     "中国市场制度（T+1、涨跌停、印花税与佣金、融券、指数编制）、交易成本与冲击、组合优化与因子中性、市场微观结构入门、订单簿与订单流不平衡、信息系数与组合构建",
     "完整 Alpha 研究文档（8 页：假设/数据/信号/样本外/成本后/归因/局限）、简历定稿、20 家目标公司清单",
     "一份让面试官愿意追问 20 分钟的研究报告"],
]
ws.append(hdr)
for row in data:
    ws.append(row)
style_header(ws, len(hdr))
style_body(ws, 2, len(data) + 1, len(hdr), [12, 10, 22, 60, 48, 34], center_cols=(1, 2), heights=150)
ws.freeze_panes = "C2"

# ============================================================ 3 技能清单
ws = wb.create_sheet("3-技能清单")
hdr = ["维度", "技能", "目标水平", "验证方式", "我的水平(1-5)", "优先级"]
data = [
    ["数学", "测度与概率基础", "能证 MCT/DCT/Borel-Cantelli", "闭卷推导 + 面试口述", 0, "P0"],
    ["数学", "条件期望与鞅", "熟练运用塔性质与 OST", "解赌徒破产等 5 道题", 0, "P0"],
    ["数学", "随机分析（Itô/Girsanov）", "手推 Itô 公式与测度变换", "闭卷推导 BS 两种证明", 0, "P0"],
    ["数学", "凸优化", "建模并求解带约束组合问题", "实现带约束均值方差", 0, "P1"],
    ["统计", "估计与渐近理论", "理解估计量为何有效", "复现一个 MLE 的渐近正态", 0, "P1"],
    ["统计", "假设检验与多重检验", "识别 p-hacking 并校正", "对因子池做 FDR 校正", 0, "P0"],
    ["统计", "时间序列", "平稳性/协整/GARCH 建模", "完成一个波动率预测任务", 0, "P0"],
    ["ML", "树模型与 GBDT", "独立完成横截面预测", "样本外 R²/IC 对比基准", 0, "P0"],
    ["ML", "金融交叉验证", "purged/embargoed CV 落地", "代码 + 泄漏演示", 0, "P0"],
    ["ML", "深度学习", "PyTorch 复现一篇论文", "复现序列模型并给出结果", 0, "P1"],
    ["工程", "Python 向量化", "无 for 循环处理千万行", "把脚本提速 10 倍以上", 0, "P0"],
    ["工程", "数据处理", "tick/日频清洗与对齐", "数据管道可增量更新", 0, "P0"],
    ["工程", "回测系统", "含成本与交易约束", "成本前后收益对比", 0, "P0"],
    ["工程", "算法与数据结构", "LeetCode 中等 200 题", "白板手写通过", 0, "P0"],
    ["工程", "C++", "现代 C++ 性能代码", "实现一个高效回测核心", 0, "P1"],
    ["工程", "Git/可复现", "实验可一键重跑", "同一 config 结果一致", 0, "P0"],
    ["金融", "中国市场制度", "说清 T+1/涨跌停/费用影响", "回测中正确建模", 0, "P0"],
    ["金融", "衍生品定价", "BS/希腊字母/波动率", "实现定价库", 0, "P1"],
    ["金融", "组合与风险", "因子中性/风险约束", "实现带约束组合优化", 0, "P1"],
    ["金融", "微观结构", "订单簿与订单流", "做一个日内信号", 0, "P1"],
    ["研究", "Alpha 全流程", "独立完成闭环研究", "一份 8 页研究报告", 0, "P0"],
    ["研究", "防过拟合", "系统化稳健性检验", "证伪实验记录", 0, "P0"],
    ["研究", "论文阅读与复现", "每周 1 篇，年复现 3 篇", "复现笔记与代码", 0, "P0"],
    ["表达", "英文 research note", "1 页讲清方法与结论", "模面录像自查", 0, "P0"],
    ["表达", "面试表达", "被追问不崩、说清边界", "完成 3 场 mock", 0, "P0"],
    ["人脉", "信息网络", "3 位可请教 + 内推渠道", "开学两周内建立联系", 0, "P0"],
]
ws.append(hdr)
for row in data:
    ws.append(row)
style_header(ws, len(hdr))
style_body(ws, 2, len(data) + 1, len(hdr), [10, 26, 30, 30, 13, 8], center_cols=(1, 5, 6), heights=32)
ws.freeze_panes = "C2"
ws.conditional_formatting.add(f"E2:E{len(data)+1}", CellIsRule(operator="lessThanOrEqual", formula=["2"], fill=PatternFill("solid", fgColor="FFC7CE")))
ws.conditional_formatting.add(f"E2:E{len(data)+1}", CellIsRule(operator="equal", formula=["3"], fill=PatternFill("solid", fgColor="FFEB9C")))
ws.conditional_formatting.add(f"E2:E{len(data)+1}", CellIsRule(operator="greaterThanOrEqual", formula=["4"], fill=PatternFill("solid", fgColor="C6EFCE")))

# ============================================================ 4 里程碑
ws = wb.create_sheet("4-里程碑")
hdr = ["#", "里程碑", "目标日", "客观达标标准", "状态"]
data = [
    [1, "环境与仓库就绪", "D1", "Python 环境 + GitHub 仓库 + 可复现 notebook", "未开始"],
    [2, "真实数据落盘", "D3", "沪深300成分股日线 parquet，脚本可一键更新", "未开始"],
    [3, "5 道经典概率题解析+模拟", "D6", "每题解析推导 + 蒙特卡洛验证一致", "未开始"],
    [4, "条件期望吃透", "D12", "能证最优 L² 预测与条件方差分解", "未开始"],
    [5, "鞅与 OST 应用", "D14", "赌徒破产解析解=模拟解", "未开始"],
    [6, "回测框架 v1", "D16", "含手续费/滑点/涨跌停/T+1，成本前后对比可出", "未开始"],
    [7, "第一个因子研究报告", "D20", "8 页以内，含样本外与成本后收益", "未开始"],
    [8, "启动营结营自测", "D21", "闭卷写出全部核心定义并限时做题", "未开始"],
    [9, "Itô 公式与 Girsanov 手推", "D30", "不看讲义完整推导", "未开始"],
    [10, "BS 定价库（解析+MC）", "D35", "两条路结果一致，含 Greeks", "未开始"],
    [11, "SDE 数值解实验", "D42", "Euler-Maruyama/Milstein 收敛阶数值验证", "未开始"],
    [12, "purged CV 工具", "D55", "代码 + 数据泄漏对比演示", "未开始"],
    [13, "GBDT 因子对比报告", "D65", "与线性基准的样本外对比", "未开始"],
    [14, "论文复现 1 篇", "D70", "关键结论可复现，含复现笔记", "未开始"],
    [15, "完整 Alpha 研究文档", "D85", "8 页，含归因与局限，能讲 20 分钟", "未开始"],
    [16, "简历 + 目标公司清单", "D90", "一页简历 + 20 家公司投递清单", "未开始"],
]
ws.append(hdr)
for row in data:
    ws.append(row)
style_header(ws, len(hdr))
style_body(ws, 2, len(data) + 1, len(hdr), [5, 28, 9, 52, 11], center_cols=(1, 3, 5), heights=32)
ws.freeze_panes = "C2"
dv2 = DataValidation(type="list", formula1='"未开始,进行中,已完成,已延期"', allow_blank=True)
ws.add_data_validation(dv2)
dv2.add(f"E2:E{len(data)+1}")

# ============================================================ 5 每日打卡
ws = wb.create_sheet("5-每日打卡")
hdr = ["日期", "Day", "A线主题", "A线时长(h)", "B线任务", "B线时长(h)", "今日是否通过验收",
       "卡住的问题（写具体）", "明天第一件事", "累计A线(h)", "累计B线(h)", "累计总时长(h)"]
examples = [
    ["2026-01-01", 1, "概率空间 σ-代数", 1.5, "环境 + 第一个 notebook", 1.5, "是", "条件期望的『可测』条件不直观", "读 Durrett 4.1 前两页", None, None, None],
]
for row in examples:
    ws.append(hdr)
    ws.append(row)
ws.delete_rows(1)
for i, row in enumerate(examples, start=2):
    for c, v in enumerate(row, start=1):
        ws.cell(i, c, v)
style_header(ws, len(hdr), row=1)
last = 200
style_body(ws, 2, last, len(hdr), [12, 6, 26, 11, 30, 11, 15, 34, 26, 11, 11, 13], center_cols=(2, 4, 6, 7, 10, 11, 12), heights=22)
for r in range(2, last + 1):
    ws.cell(r, 10).value = f'=IF(D{r}="","",SUM($D$2:D{r}))'
    ws.cell(r, 11).value = f'=IF(F{r}="","",SUM($F$2:F{r}))'
    ws.cell(r, 12).value = f'=IF(AND(D{r}="",F{r}=""),"",N(D{r})+N(F{r}))'
dv3 = DataValidation(type="list", formula1='"是,否"', allow_blank=True)
ws.add_data_validation(dv3)
dv3.add(f"G2:G{last}")
ws.freeze_panes = "C2"

# ============================================================ 6 面试题库索引
ws = wb.create_sheet("6-面试题库索引")
hdr = ["类别", "题目/考点", "训练时点", "要点提示"]
data = [
    ["经典概率", "生日悖论：n 人至少两人生日相同", "D6", "1-P(全不同)，n=23 即过半"],
    ["经典概率", "优惠券收集：集齐 n 种的期望次数", "D6", "n·Hₙ，用期望线性性"],
    ["经典概率", "Monty Hall（换不换门）", "D6/D12", "条件概率版本与条件期望视角各讲一遍"],
    ["经典概率", "两孩悖论：已知至少一个男孩", "D12", "关键在于『如何获得信息』决定样本空间"],
    ["经典概率", "首次出现 HT vs HH 的期望步数", "D6", "4 步 vs 6 步，用鞅或状态方程"],
    ["经典概率", "赌徒破产问题", "D14", "OST 的标准应用，写出边界条件"],
    ["经典概率", "投针问题 / 几何概率", "D8", "几何概率与蒙特卡洛验证"],
    ["经典概率", "随机排列的圈数期望", "D17", "指示变量 + 期望线性性"],
    ["鞅与随机过程", "可选停时定理何时失效", "D14", "必须给出反例（如无界停时）"],
    ["鞅与随机过程", "反射原理求首达时间分布", "D17", "对称随机游走的经典结论"],
    ["鞅与随机过程", "二次变差为什么是 t", "D19", "Σ(ΔB)² 的数值验证"],
    ["统计", "为什么重复检验会假阳性", "D55", "多重检验：Bonferroni 与 FDR"],
    ["统计", "区间估计与置信区间解释", "D50", "频率派解释，避免『95% 概率包含真值』"],
    ["统计", "自相关如何破坏 t 检验", "D52", "有效样本量下降，方差被低估"],
    ["统计", "过拟合与交叉验证陷阱", "D55", "purged/embargoed CV 与泄漏"],
    ["统计", "贝叶斯 vs 频率派在因子上的取舍", "D60", "收缩估计与先验的实务意义"],
    ["编程", "数组第 k 大 / 两数之和 / 滑动窗口", "D1 起", "LeetCode 中等稳定输出"],
    ["编程", "LRU 缓存、堆、并查集", "D30 起", "高频手写题，注意边界与复杂度"],
    ["编程", "多线程与内存布局（C++）", "D40 起", "缓存友好、false sharing"],
    ["研究", "讲清一个你做的因子：假设-检验-成本-局限", "D20 起", "准备 3 句话版与 15 分钟版"],
    ["研究", "你的信号为什么会失效", "D85", "容量、拥挤、制度变化、成本上升"],
    ["金融", "A 股 T+1 与涨跌停如何影响回测", "D75", "约束实现与收益高估"],
    ["金融", "隐含波动率微笑的解释", "D40", "跳跃、随机波动率、供需"],
    ["金融", "订单流不平衡与短期收益", "D80", "微观结构信号的核心变量"],
]
ws.append(hdr)
for row in data:
    ws.append(row)
style_header(ws, len(hdr))
style_body(ws, 2, len(data) + 1, len(hdr), [16, 44, 10, 46], center_cols=(3,), heights=30)
ws.freeze_panes = "B2"

wb.save(OUT)
print("saved:", OUT)
