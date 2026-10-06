# -*- coding: utf-8 -*-
"""生成《北大金数 -> 头部量化研究员 24个月路线图》工作簿。"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import CellIsRule, DataBarRule

OUT = r"E:\AI结果\量化\北大金数-头部量化研究员路线图.xlsx"

TITLE_FILL = PatternFill("solid", fgColor="1F3864")
TITLE_FONT = Font(name="Microsoft YaHei", size=13, bold=True, color="FFFFFF")
HDR_FILL = PatternFill("solid", fgColor="2E5C9A")
HDR_FONT = Font(name="Microsoft YaHei", size=10, bold=True, color="FFFFFF")
SEC_FILL = PatternFill("solid", fgColor="D9E2F3")
SEC_FONT = Font(name="Microsoft YaHei", size=11, bold=True, color="1F3864")
BODY_FONT = Font(name="Microsoft YaHei", size=10)
BOLD_FONT = Font(name="Microsoft YaHei", size=10, bold=True)
NOTE_FONT = Font(name="Microsoft YaHei", size=9, color="595959")
THIN = Side(style="thin", color="B4C6E7")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
WRAP_C = Alignment(wrap_text=True, vertical="center", horizontal="center")

wb = Workbook()

# ---------------------------------------------------------------- 1. 说明
ws = wb.active
ws.title = "0-使用说明"
ws.column_dimensions["A"].width = 22
ws.column_dimensions["B"].width = 104
rows = [
    ("使用说明", ""),
    ("这份表是什么", "面向「即将入学北大金融数学方向硕士、目标头部量化研究员」的 24 个月可执行路线图。核心逻辑：目标岗位只有一条主入口——暑期实习转正，因此所有学习都倒排到申请季。"),
    ("怎么用", "第一步看『1-三阶段与时间线』搞清倒排关系；第二步用『2-技能与知识地图』按 P0 逐项打勾；第三步照『5-月份行动表』每月执行；每周更新『3-资源清单』与『6-里程碑看板』的进度。"),
    ("三条铁律", "1) 没有实习经历，学历和成绩几乎无法单独敲开头部量化；2) 项目要比考试重要——能讲清一个自己挖出来的信号，胜过十门课的成绩单；3) 编程不是加分项，是准入门槛（Python 必须熟练，C++ 决定天花板）。"),
    ("岗位分层", "头部量化研究员分：①因子/Alpha 研究（数学统计+ML，最主流）②高频/微观结构研究（随机过程+低延迟工程）③AI 算法研究（大模型/深度学习，近年扩张最快）④量化开发/交易。硕士最现实的是①和③，②通常偏好顶尖博士。"),
    ("给北大的特别提示", "①北大数院最大的资源是课程深度和讨论班，把随机分析、高等概率、统计学习这三门学到能给别人讲；②不必读博，但要用研究质量弥补学位差异，硕士对博士的竞争靠『工程化 Alpha 能力』③尽早进实验室/做导师项目，暑期实习推荐信多来自导师与学长；④量化学会/社团/往届学长是最快的信息渠道，秋招内推几乎全靠这个。"),
    ("常见误区", "沉迷回测平台调参、堆砌 Kaggle 名次、只刷题不写代码、把『看懂教材』当成『会做研究』、暑假才开始找实习（头部暑期实习前一年 10-12 月就开招）。"),
]
for i, (a, b) in enumerate(rows, start=1):
    ws.cell(i, 1, a)
    ws.cell(i, 2, b)
    ws.cell(i, 1).font = TITLE_FONT if i == 1 else SEC_FONT
    ws.cell(i, 2).font = TITLE_FONT if i == 1 else BODY_FONT
    ws.cell(i, 1).fill = TITLE_FILL if i == 1 else SEC_FILL
    ws.cell(i, 2).fill = TITLE_FILL if i == 1 else PatternFill("solid", fgColor="F2F5FB")
    ws.cell(i, 1).alignment = WRAP_C
    ws.cell(i, 2).alignment = WRAP
    ws.row_dimensions[i].height = 22 if i == 1 else 52
ws.freeze_panes = "A2"

# ------------------------------------------------- 1. 三阶段与时间线
ws = wb.create_sheet("1-三阶段与时间线")
data = [
    ["阶段", "时间（入学=第0月）", "核心目标", "必须完成的事", "判断是否达标的硬指标"],
    ["阶段A 打地基", "入学前暑假 ~ 第4个月", "把数学与编程从『学过』变成『能推导、能写代码』", "高等概率/随机分析系统复习；Python 数据栈熟练；独立完成 1 个含交易成本的因子回测", "能手推伊藤公式与 Girsanov；LeetCode 中等 60 题；GitHub 上有可复现的回测仓库"],
    ["阶段B 出成果", "第5 ~ 10个月", "产出一段『像研究员做的事』的经历", "进课题组/做导师项目；完成 2 个自选 Alpha 研究（含数据清洗、稳健性检验、失败记录）；投递并拿到 2027 暑期实习", "有一份 8 页以内的研究报告：假设-数据-结果-归因-局限；至少 1 场量化面试走完终面"],
    ["阶段C 冲刺转正", "第11 ~ 24个月", "把暑期实习转成全职 offer，并准备兜底选项", "暑期实习全力转正；同步准备秋招/备选 3-8 家；把实习成果整理成可讲 20 分钟的案例", "拿到 return offer 或同级别社招/校招 offer；能清晰讲出自己策略的收益来源与最大回撤原因"],
    ["", "", "", "", ""],
    ["关键时间线（务必按此倒排）", "", "", "", ""],
    ["T-12月（入学前）", "现在", "信息战 + 基础战", "确认自己专业方向（数院金数）；建好学习/代码环境；锁定 2-3 本主教材", "每周固定 20 小时可支配学习时间"],
    ["T-9 ~ T-6月", "入学第1学期", "课程拿高分 + 工具链成型", "把随机分析/统计学习学扎实；参加一次行业竞赛或校内量化活动", "GPA 进入保研/求职不拖后腿区间（3.6+ 或专业前 30%）"],
    ["T-6 ~ T-3月", "入学第2学期", "第一次真正的量化研究", "完成 2 个自选项目；开始刷量化笔试（概率+编程）；投递日常实习", "有 1 段日常实习或等价项目经历写进简历"],
    ["T-3月 ~ 申请季", "暑期实习申请窗口", "拿到头部暑期实习", "头部量化暑期实习通常在前一年 10-12 月陆续开启，次年 1-4 月笔面", "拿到至少 1 个量化暑期实习 offer"],
    ["第1个暑假", "暑期实习", "转正评估", "把实习当试用期：主动汇报、复现、写清文档", "拿到 return offer 或明确得到强推荐信"],
    ["第2年秋招", "毕业前约 1 年", "兜底 + 抬价", "同时面 5-10 家（含外资/互联网研究岗）", "手上有 2 个以上可比 offer 才有议价空间"],
]
for r_i, row in enumerate(data, start=1):
    for c_i, v in enumerate(row, start=1):
        cell = ws.cell(r_i, c_i, v)
        cell.alignment = WRAP
        cell.border = BORDER
        if r_i == 1:
            cell.fill = HDR_FILL; cell.font = HDR_FONT; cell.alignment = WRAP_C
        elif r_i == 5:
            cell.fill = SEC_FILL; cell.font = SEC_FONT
        else:
            cell.font = BOLD_FONT if c_i == 1 else BODY_FONT
for col, w in zip("ABCDE", [20, 20, 30, 46, 48]):
    ws.column_dimensions[col].width = w
for r in range(2, len(data) + 1):
    ws.row_dimensions[r].height = 62
ws.row_dimensions[1].height = 26
ws.row_dimensions[5].height = 22
ws.freeze_panes = "B2"

# ------------------------------------------------- 2. 技能与知识地图
ws = wb.create_sheet("2-技能与知识地图")
hdr = ["维度", "具体能力", "达到什么程度算合格（头部标准）", "优先级", "我的水平(1-5)", "差距自评"]
data = [
    ["数学基础", "数学分析 / 实分析", "能独立读懂测度论证明，理解收敛定理的使用条件", "P0", 0, ""],
    ["数学基础", "高等概率论", "条件期望、鞅、停时、大数律与中心极限的标准工具随手可用", "P0", 0, ""],
    ["数学基础", "随机分析 / 随机微积分", "伊藤公式、Girsanov、鞅表示、SDE 求解与数值离散化", "P0", 0, ""],
    ["数学基础", "线性代数与数值方法", "矩阵分解、特征值稳定性、数值误差与病态问题意识", "P0", 0, ""],
    ["数学基础", "凸优化 / 随机优化", "能建模并解带约束的组合优化，理解正则化与稀疏解", "P1", 0, ""],
    ["数学基础", "微分方程与数值 PDE", "BS 方程两种解法、有限差分与蒙特卡洛的误差权衡", "P1", 0, ""],
    ["统计与机器学习", "数理统计与渐近理论", "MLE、假设检验、多重检验校正、重采样与 p 值陷阱", "P0", 0, ""],
    ["统计与机器学习", "回归 / 树模型 / GBDT", "在表格数据上独立完成建模、调参与特征重要性分析", "P0", 0, ""],
    ["统计与机器学习", "时间序列分析", "ARIMA/GARCH/状态空间、协整、平稳性、样本外滚动检验", "P0", 0, ""],
    ["统计与机器学习", "金融机器学习", "会做 purged/embargoed CV、防泄漏、多重检验下的因子筛选", "P0", 0, ""],
    ["统计与机器学习", "深度学习", "PyTorch 熟练，能读懂并复现一篇序列/图/Transformer 论文", "P1", 0, ""],
    ["统计与机器学习", "因果推断 / 实验设计", "理解混杂、工具变量、DID，能识别伪相关", "P2", 0, ""],
    ["计算机基础", "Python 科学计算", "numpy/pandas 向量化、内存与效率 profiling、可维护的代码结构", "P0", 0, ""],
    ["计算机基础", "算法与数据结构", "LeetCode 中等稳定、竞赛级思维、复杂度分析直觉", "P0", 0, ""],
    ["计算机基础", "C++ 与性能工程", "现代 C++、内存布局、缓存友好、多线程与无锁基础", "P1", 0, ""],
    ["计算机基础", "数据工程", "处理 tick/快照数据：清洗、对齐、复权、增量更新、存储选型", "P0", 0, ""],
    ["计算机基础", "回测与仿真系统", "能自建事件驱动回测：手续费、滑点、冲击成本、涨跌停与停牌约束", "P0", 0, ""],
    ["计算机基础", "Linux / Git / 工程习惯", "命令行、容器、版本管理、可复现实验记录", "P1", 0, ""],
    ["金融知识", "衍生品定价", "BS、希腊字母、隐含波动率曲面、利率与信用基础", "P1", 0, ""],
    ["金融知识", "市场微观结构", "订单簿、价差与流动性、信息不对称、做市与逆向选择", "P1", 0, ""],
    ["金融知识", "组合优化与风险", "均值方差、风险平价、因子中性、行业与风格约束、回撤管理", "P1", 0, ""],
    ["金融知识", "交易成本与最优执行", "Almgren-Chriss、冲击成本模型、执行滑点归因", "P2", 0, ""],
    ["金融知识", "中国市场制度", "T+1、涨跌停、印花税与佣金、融券约束、指数与行业分类", "P0", 0, ""],
    ["研究能力（最重）", "Alpha 研究全流程", "从想法→数据→信号构造→样本外验证→成本后收益→归因，全链路独立完成", "P0", 0, ""],
    ["研究能力（最重）", "防过拟合与稳健性", "多重检验意识、参数敏感性、时段/标的/市场状态分层检验", "P0", 0, ""],
    ["研究能力（最重）", "论文阅读与复现", "每周 1 篇，一年内复现 3 篇核心论文的关键结论", "P0", 0, ""],
    ["研究能力（最重）", "学术表达（英文）", "能写 1 页 research note，面试中用英文讲清方法与结论", "P0", 0, ""],
    ["软技能", "面试表达与压力应对", "概率题口算、白板写代码、被质疑时不慌并能说出边界条件", "P0", 0, ""],
    ["软技能", "信息网络", "有 3 位以上可请教的学长/从业者，能拿到内推", "P0", 0, ""],
    ["软技能", "时间与项目节奏", "在课业压力下仍能保持每周 ≥10 小时研究时间", "P1", 0, ""],
]
ws.append(hdr)
for row in data:
    ws.append(row)
for c_i in range(1, len(hdr) + 1):
    c = ws.cell(1, c_i); c.fill = HDR_FILL; c.font = HDR_FONT; c.alignment = WRAP_C
for r in range(2, len(data) + 2):
    for c_i in range(1, len(hdr) + 1):
        cell = ws.cell(r, c_i)
        cell.border = BORDER
        cell.alignment = WRAP if c_i in (2, 3, 6) else WRAP_C
        cell.font = BOLD_FONT if c_i == 2 else BODY_FONT
    ws.cell(r, 5).value = 0
for col, w in zip("ABCDEF", [16, 24, 52, 9, 13, 20]):
    ws.column_dimensions[col].width = w
for r in range(2, len(data) + 2):
    ws.row_dimensions[r].height = 34
ws.freeze_panes = "C2"
ws.conditional_formatting.add(f"E2:E{len(data)+1}",
    CellIsRule(operator="lessThanOrEqual", formula=["2"], fill=PatternFill("solid", fgColor="FFC7CE")))
ws.conditional_formatting.add(f"E2:E{len(data)+1}",
    CellIsRule(operator="equal", formula=["3"], fill=PatternFill("solid", fgColor="FFEB9C")))
ws.conditional_formatting.add(f"E2:E{len(data)+1}",
    CellIsRule(operator="greaterThanOrEqual", formula=["4"], fill=PatternFill("solid", fgColor="C6EFCE")))

# ------------------------------------------------- 3. 资源清单
ws = wb.create_sheet("3-资源清单")
hdr = ["类别", "资源", "类型", "优先级", "怎么用 / 关键章节", "进度"]
data = [
    ["数学", "Durrett《Probability: Theory and Examples》或 汪嘉冈《现代概率论基础》", "教材", "P0", "条件期望、鞅、大数律；配习题，重点是会证而不是会背", "未开始"],
    ["数学", "Shreve《Stochastic Calculus for Finance》I & II", "教材", "P0", "II 是金融数学圣经：伊藤、Girsanov、鞅表示、BS 两种推导都要能手推", "未开始"],
    ["数学", "Øksendal《Stochastic Differential Equations》", "教材", "P1", "补充 SDE 解的存在唯一性与数值离散", "未开始"],
    ["数学", "Karatzas & Shreve《Brownian Motion and Stochastic Calculus》", "参考书", "P1", "不要求通读，遇到难点查证用", "未开始"],
    ["数学", "Boyd《Convex Optimization》", "教材", "P1", "重点：对偶、KKT、正则化；只看前 5 章 + 应用", "未开始"],
    ["数学", "Glasserman《Monte Carlo Methods in Financial Engineering》", "教材", "P2", "方差缩减、 Greeks 的模拟估计", "未开始"],
    ["统计/ML", "van der Vaart《Asymptotic Statistics》", "教材", "P1", "M 估计、渐近正态、delta 方法；理解『估计量为什么有效』", "未开始"],
    ["统计/ML", "Hastie《ESL》或《ISLR》", "教材", "P0", "ISLR 快速过，ESL 精读树模型/正则化/模型选择", "未开始"],
    ["统计/ML", "López de Prado《Advances in Financial Machine Learning》", "教材", "P0", "第 4、7、8、11 章（样本权重、交叉验证、特征重要性、回测陷阱）直接决定你的研究会否自欺", "未开始"],
    ["统计/ML", "Hamilton《Time Series Analysis》/ Tsay《Analysis of Financial Time Series》", "教材", "P0", "Hamilton 补理论，Tsay 贴近金融数据；协整、GARCH、状态空间", "未开始"],
    ["统计/ML", "Murphy《Probabilistic Machine Learning》", "教材", "P2", "当作贝叶斯与概率模型的案头参考", "未开始"],
    ["统计/ML", "《Attention Is All You Need》/ 《Deep Learning for Time Series》综述", "论文", "P1", "建立序列建模的现代直觉", "未开始"],
    ["编程", "Fluent Python / Effective Python", "书", "P0", "写出别人能读的 Python，而不是脚本堆", "未开始"],
    ["编程", "《C++ Primer》+ cppreference", "书", "P1", "目标：能写高性能数据处理与回测核心", "未开始"],
    ["编程", "Efficient C++ / 性能剖析（perf、valgrind）", "实践", "P2", "只在确定走高频/开发方向时投入", "未开始"],
    ["编程", "LeetCode（中等为主）", "刷题", "P0", "目标 200 题以上，面试手写不依赖 IDE", "未开始"],
    ["编程", "Zipline / vectorbt / Backtrader 源码阅读", "开源", "P1", "读懂一个成熟回测框架，再写自己的简版", "未开始"],
    ["编程", "polars / duckdb / arrow", "工具", "P1", "处理亿级 tick 数据的现代数据栈", "未开始"],
    ["金融", "Hull《Options, Futures and Other Derivatives》", "教材", "P1", "希腊字母与波动率部分精读，作为面试常识", "未开始"],
    ["金融", "Gatheral《The Volatility Surface》", "书", "P2", "波动率建模的品味来源", "未开始"],
    ["金融", "O'Hara《Market Microstructure Theory》", "书", "P1", "订单簿、做市、信息不对称的经典框架", "未开始"],
    ["金融", "《Trading and Exchanges》(Harris)", "书", "P1", "理解交易制度、流动性与成本从哪来", "未开始"],
    ["金融", "Grinald & Kahn《Active Portfolio Management》", "书", "P1", "信息系数、组合构建与风险模型的行业标准语言", "未开始"],
    ["金融", "Almgren & Chriss (2000) 最优执行；Avellaneda & Stoikov (2008) 做市", "论文", "P2", "执行/做市方向必读，其他方向知道结论即可", "未开始"],
    ["金融", "Fama-French (1993)、Jegadeesh-Titman (1993) 动量", "论文", "P0", "因子研究的原点，理解因子是怎么被定义和检验的", "未开始"],
    ["金融", "中国：T+1、涨跌停、印花税、融券与指数编制规则", "制度", "P0", "所有 A 股回测有效性的前提，不搞清楚必然回测虚高", "未开始"],
    ["实战", "WorldQuant BRAIN / 国内因子平台竞赛", "比赛", "P0", "性价比最高的『可验证研究能力』证明之一", "未开始"],
    ["实战", "Kaggle（Jane Street / Optiver / 量化类 comp）", "比赛", "P1", "不为名次，为『在真实脏数据上做研究』的能力与简历背书", "未开始"],
    ["实战", "Optiver / IMC / Jane Street 的在线测评与谜题", "面试", "P1", "外资量化的笔试风格，提前适应", "未开始"],
    ["信息", "量化私募招聘页与 `niuqizp` 等校招聚合站", "渠道", "P0", "跟踪九坤、幻方、思勰、鸣石、明汯、灵均等暑期实习开放时间", "未开始"],
    ["信息", "SSRN / arXiv q-fin / 各大量化公众号研报复现", "论文", "P1", "每周 1 篇，做摘要卡片，积累研究品味", "未开始"],
    ["信息", "往届学长学姐 + 学院职业发展中心", "人脉", "P0", "内推与信息的第一来源，开学两周内就要建立联系", "未开始"],
]
ws.append(hdr)
for row in data:
    ws.append(row)
for c_i in range(1, len(hdr) + 1):
    c = ws.cell(1, c_i); c.fill = HDR_FILL; c.font = HDR_FONT; c.alignment = WRAP_C
for r in range(2, len(data) + 2):
    for c_i in range(1, len(hdr) + 1):
        cell = ws.cell(r, c_i)
        cell.border = BORDER
        cell.alignment = WRAP if c_i in (2, 5) else WRAP_C
        cell.font = BOLD_FONT if c_i == 2 else BODY_FONT
for col, w in zip("ABCDEF", [12, 50, 9, 9, 52, 11]):
    ws.column_dimensions[col].width = w
for r in range(2, len(data) + 2):
    ws.row_dimensions[r].height = 36
ws.freeze_panes = "C2"

# ------------------------------------------------- 4. 月份行动表
ws = wb.create_sheet("4-月份行动表")
hdr = ["时间", "阶段", "本阶段唯一重点", "数学", "编程与工程", "研究 / 项目", "求职与信息", "本月交付物（可验收）"]
data = [
    ["第0月\n入学前", "信息收集", "确定方向 + 环境就绪", "统计基础自测：条件期望、鞅、CLT 能否手推", "配好 Python 环境；GitHub 建库；学会 pandas 向量化", "读 3 篇中文量化科普，写一页『我想做什么方向』", "关注 10 家头部量化招聘页；加 2 个量化社群", "一页方向说明 + 可运行的 Python 环境截图"],
    ["第1月\n入学", "阶段A", "课程选好 + 概率地基", "高等概率论：鞅、停时、一致可积", "LeetCode 中等 15 题；写一个从数据到图表的完整脚本", "复现 Fama-French 三因子在 A 股的结果", "认识 3 位学长；问清 2027 暑期实习时间线", "三因子复现报告（含数据来源与代码）"],
    ["第2月", "阶段A", "随机分析入门", "伊藤积分与伊藤公式；配 Shreve II 第 4-5 章", "实现 BS 定价与希腊字母（解析 + 蒙特卡洛两条路）", "用蒙特卡洛给雪球/障碍期权定价并做敏感性分析", "加入学院量化社团或讨论班", "BS 定价代码 + 一份敏感性分析表"],
    ["第3月", "阶段A", "第一个真回测", "Girsanov 与鞅表示；BS 的两种推导", "自建事件驱动回测骨架：手续费、滑点、涨跌停、T+1", "动量因子研究：分年度/分市值/分行业稳健性检验", "投递 1-2 个日常实习（不要求头部）", "GitHub 回测框架 v1 + 动量研究报告"],
    ["第4月", "阶段A→B", "工具体系化", "SDE 数值解（Euler、Milstein）", "数据工程：tick 清洗、复权、对齐、增量存储", "把回测框架升级到支持多因子与组合约束", "把简历改到一页；请学长做一次 mock 面", "可复现的因子研究流水线（含 README）"],
    ["第5月", "阶段B", "进入课题组", "统计学习：正则化、模型选择、重采样", "开始 C++（若走高频/开发）或 polars 大数据处理", "在导师项目里承担一个可交付模块", "请导师写第一封推荐信的准备", "课题组的第一个交付物"],
    ["第6月", "阶段B", "防过拟合意识", "时间序列：平稳性、协整、GARCH", "实现 purged/embargoed 交叉验证与多重检验校正", "对第3月的动量研究做『证伪实验』，记录失败", "参加一次因子竞赛（WorldQuant BRAIN 等）", "一份含『失败记录』的研究笔记"],
    ["第7月", "阶段B", "第二个 Alpha 项目", "高频统计：波动率估计、已实现测度", "订单簿/tick 数据的处理与特征构造", "高频或日内信号研究（量价、订单流不平衡）", "秋季招聘会预热；更新 LinkedIn/实习僧", "高频信号研究报告（含成本后收益）"],
    ["第8月", "阶段B", "机器学习进研究", "ESL 树模型与集成；特征重要性", "PyTorch 基础；训练可复现（seed、日志、配置）", "用 GBDT 做横截面收益预测并与线性模型对比", "整理 3 个项目的 3 句话版本（简历/口述）", "ML 因子研究报告 + 简历定稿"],
    ["第9月", "阶段B", "投递准备", "凸优化：组合优化建模", "实现带约束的均值方差与风险平价", "把 2 个项目打磨成 8 页以内的研究文档", "确定 20 家目标公司清单；开始刷笔试", "研究文档 2 份 + 目标公司清单"],
    ["第10月", "申请季", "拿到暑期实习", "概率与脑筋急转弯专项", "LeetCode 中等累计 150 题；白板训练", "面试驱动的查漏补缺", "内推投递、笔试、面试密集期", "至少 1 个量化暑期实习 offer"],
    ["第11月", "申请季", "面试推进", "复现面试常考的 BS 推导、鞅、概率题", "手写代码训练（不依赖补全）", "准备『讲清一个我做过的研究』15 分钟版本", "并行推进 3-5 家流程", "完成 3 家终面"],
    ["第12月", "暑期实习前", "入职准备", "复习与岗位相关的数学", "熟悉公司技术栈与数据规范", "预习即将做的课题方向", "签实习协议；确认转正评估标准", "明确的实习目标与转正路径"],
    ["第13-15月", "阶段C", "转正评估", "按需补充", "把研究代码写成团队可用的工具", "独立负责一个小课题并主动汇报", "每月与 mentor 对齐一次期望", "一份实习期研究成果总结"],
    ["第16-18月", "阶段C", "锁定 offer", "按需补充", "沉淀个人研究框架", "把实习成果整理成可讲 20 分钟的案例", "谈 return offer，同时面 5-10 家抬价", "≥2 个可比 offer"],
    ["第19-24月", "阶段C", "毕业与入职", "完成学位论文", "整理个人代码库与作品集", "把论文与实习结合成一个完整研究故事", "确认入职时间与岗位", "毕业论文 + 入职确认"],
]
ws.append(hdr)
for row in data:
    ws.append(row)
for c_i in range(1, len(hdr) + 1):
    c = ws.cell(1, c_i); c.fill = HDR_FILL; c.font = HDR_FONT; c.alignment = WRAP_C
for r in range(2, len(data) + 2):
    for c_i in range(1, len(hdr) + 1):
        cell = ws.cell(r, c_i)
        cell.border = BORDER
        cell.alignment = WRAP_C if c_i == 1 else WRAP
        cell.font = BOLD_FONT if c_i in (1, 3) else BODY_FONT
for col, w in zip("ABCDEFGH", [12, 12, 20, 26, 32, 34, 28, 32]):
    ws.column_dimensions[col].width = w
for r in range(2, len(data) + 2):
    ws.row_dimensions[r].height = 56
ws.freeze_panes = "B2"

# ------------------------------------------------- 5. 里程碑看板
ws = wb.create_sheet("5-里程碑看板")
hdr = ["#", "里程碑", "目标时间", "达标标准（客观可验证）", "状态", "完成度", "备注"]
data = [
    [1, "数学地基复习完成", "入学前 ~ 第2月", "能手推伊藤公式、Girsanov、BS 两种推导", "未开始", 0, ""],
    [2, "编程工具链就绪", "第1月", "Python 环境 + GitHub 仓库 + 可复现实验记录模板", "未开始", 0, ""],
    [3, "LeetCode 中等 60 题", "第3月", "不看答案写出并通过，复杂度能解释", "未开始", 0, ""],
    [4, "自建回测框架 v1", "第3月", "含手续费、滑点、涨跌停、T+1 约束，可运行示例", "未开始", 0, ""],
    [5, "第一个因子研究报告", "第3月", "假设→数据→检验→成本后收益→局限，8 页以内", "未开始", 0, ""],
    [6, "进入课题组 / 导师项目", "第5月", "有明确的交付模块和负责人角色", "未开始", 0, ""],
    [7, "防过拟合工具箱", "第6月", "purged CV + 多重检验校正 + 分层稳健性检验脚本", "未开始", 0, ""],
    [8, "第二个 Alpha 项目（高频/日内）", "第7月", "tick 级数据处理 + 成本后收益为正或可解释", "未开始", 0, ""],
    [9, "机器学习因子研究", "第8月", "GBDT 横截面预测 + 与线性模型基准对比", "未开始", 0, ""],
    [10, "简历 + 3 个项目口述版本", "第8月", "每个项目 3 句话讲清问题、方法、结果", "未开始", 0, ""],
    [11, "20 家目标公司清单 + 笔试准备", "第9月", "含开放时间、岗位、内推渠道", "未开始", 0, ""],
    [12, "拿到暑期实习 offer", "第10-11月", "至少 1 个头部/准头部量化暑期实习", "未开始", 0, ""],
    [13, "LeetCode 中等 150 题", "第11月", "白板手写无阻力", "未开始", 0, ""],
    [14, "暑期实习转正", "第15月", "return offer 或明确强推荐", "未开始", 0, ""],
    [15, "多 offer 议价", "第18月", "≥2 个可比 offer", "未开始", 0, ""],
]
ws.append(hdr)
for row in data:
    ws.append(row)
for c_i in range(1, len(hdr) + 1):
    c = ws.cell(1, c_i); c.fill = HDR_FILL; c.font = HDR_FONT; c.alignment = WRAP_C
for r in range(2, len(data) + 2):
    for c_i in range(1, len(hdr) + 1):
        cell = ws.cell(r, c_i)
        cell.border = BORDER
        cell.alignment = WRAP if c_i in (2, 4) else WRAP_C
        cell.font = BOLD_FONT if c_i == 2 else BODY_FONT
    ws.cell(r, 6).number_format = "0%"
ws.conditional_formatting.add(f"F2:F{len(data)+1}",
    DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color="5B9BD5"))
for col, w in zip("ABCDEFG", [5, 30, 16, 50, 11, 10, 24]):
    ws.column_dimensions[col].width = w
for r in range(2, len(data) + 2):
    ws.row_dimensions[r].height = 34
ws.freeze_panes = "C2"

wb.save(OUT)
print("saved:", OUT)
