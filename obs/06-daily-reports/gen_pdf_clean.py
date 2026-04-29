#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# gen_pdf_clean.py  --  Synapse for FinLease PDF  --  ai_systems_dev 2026-04-26

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.platypus.flowables import KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import os

# ---- Font -------------------------------------------------------------------
FN = "Helvetica"
FB = "Helvetica-Bold"
_font_pairs = [
    (r"C:\Windows\Fonts\msyh.ttc",   "MSYaHei",     False),
    (r"C:\Windows\Fonts\msyhbd.ttc", "MSYaHeiBold", True),
]
for _fp, _fn, _bold in _font_pairs:
    try:
        if os.path.exists(_fp):
            pdfmetrics.registerFont(TTFont(_fn, _fp, subfontIndex=0))
            if not _bold:
                FN = _fn
            else:
                FB = _fn
    except Exception:
        pass
print("[font]", FN, "/", FB)

# ---- Colors -----------------------------------------------------------------
C_DARK  = colors.HexColor("#0a2540")
C_LGRAY = colors.HexColor("#f7fafc")
C_BDR   = colors.HexColor("#e2e8f0")
C_GRAY  = colors.HexColor("#4a5568")
C_GRN   = colors.HexColor("#276749")
C_BLU   = colors.HexColor("#3354a8")

# ---- Style factory ----------------------------------------------------------
def sty(name, font, sz, ld, tc=None, sb=0, sa=4, li=0, fi=0, al=TA_LEFT):
    return ParagraphStyle(
        name, fontName=font, fontSize=sz, leading=ld,
        textColor=tc or colors.HexColor("#2d2d2d"),
        spaceBefore=sb, spaceAfter=sa,
        leftIndent=li, firstLineIndent=fi, alignment=al)

SH1  = sty("h1",  FB, 20, 26, C_DARK,   0,  4)
SH2  = sty("h2",  FB, 14, 18, C_DARK,  18,  6)
SH3  = sty("h3",  FB, 12, 16, colors.HexColor("#1a3a5c"), 12, 4)
SH4  = sty("h4",  FB, 10, 14, colors.HexColor("#2c5282"),  8, 3)
SBD  = sty("bd",  FN, 10, 15, None,     0,  4)
SSM  = sty("sm",  FN,  9, 13, C_GRAY,   0,  3)
SME  = sty("me",  FN,  9, 13, C_GRAY,   0,  2)
SBU  = sty("bu",  FN, 10, 14, None,     0,  2, 12, -12)
SQU  = sty("qu",  FN, 10, 14, C_GRAY,   0,  4, 12,   0)
SCO  = sty("co",  FB, 11, 17, colors.white, 0, 0, 0, 0, TA_JUSTIFY)
SFT  = sty("ft",  FN,  8, 11, C_GRAY,   0,  0, 0,  0, TA_CENTER)
STH  = sty("th",  FB,  9, 12, colors.white, 0, 0)
STD  = sty("td",  FN,  9, 13, None,     0,  0)
SSCH = sty("sch", FB, 11, 15, C_DARK,   0,  6)
SSLB = sty("slb", FB,  9, 13, None,     0,  2)
SSIT = sty("sit", FN,  9, 13, None,     0,  1, 10, -10)
SPHH = sty("phh", FB, 11, 15, C_BLU,   0,  4)
SPHB = sty("phb", FN,  9, 13, None,     0,  1, 10, -10)
SPHM = sty("phm", FN,  9, 13, C_BLU,   0,  1, 10, -10)
SRVH = sty("rvh", FB, 11, 15, C_DARK,   0,  4)
SRVP = sty("rvp", FN,  9, 13, C_GRN,   0,  1, 10, -10)
SRVI = sty("rvi", FN,  9, 13, None,     0,  1, 10, -10)
SROI = sty("roi", FB, 12, 16, colors.HexColor("#2b6cb0"), 0, 4)

W = 170  # usable width mm

# ---- Helpers ----------------------------------------------------------------
def sp(h=4):  return Spacer(1, h * mm)
def hr():     return HRFlowable(width="100%", thickness=1, color=C_BDR)
def h1(t):    return Paragraph(t, SH1)
def h2(t):    return Paragraph("  " + t, SH2)
def h3(t):    return Paragraph(t, SH3)
def h4(t):    return Paragraph(t, SH4)
def bd(t):    return Paragraph(t, SBD)
def sm(t):    return Paragraph(t, SSM)
def bl(t):    return Paragraph("  " + t, SBU)
def qu(t):    return Paragraph("  " + t, SQU)

_TS_BASE = [
    ("FONTNAME",      (0, 0), (-1,  0), FB),
    ("FONTSIZE",      (0, 0), (-1,  0), 9),
    ("BACKGROUND",    (0, 0), (-1,  0), C_DARK),
    ("TEXTCOLOR",     (0, 0), (-1,  0), colors.white),
    ("FONTNAME",      (0, 1), (-1, -1), FN),
    ("FONTSIZE",      (0, 1), (-1, -1), 9),
    ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, C_LGRAY]),
    ("GRID",          (0, 0), (-1, -1), 0.5, C_BDR),
    ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING",    (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
]

def tbl(data, ws=None):
    pd_ = []
    for ri, row in enumerate(data):
        pd_.append([Paragraph(str(c), STH if ri == 0 else STD) for c in row])
    t = Table(pd_, colWidths=ws, repeatRows=1)
    t.setStyle(TableStyle(_TS_BASE))
    return t


def scene_card(title, diff, dcol, can, rep, cant, eff):
    items = []
    items.append(Paragraph(
        '<b>' + title + '</b>  '
        '<font color="' + dcol + '" size="9">' + diff + '</font>',
        SSCH))
    for label, bullets, col in [
        ("能做什么",   can,  "#276749"),
        ("替代什么",   rep,  "#2b6cb0"),
        ("不能做什么", cant, "#c53030"),
        ("预期效果",   eff,  "#553c9a"),
    ]:
        items.append(Paragraph(
            '<font color="' + col + '"><b>' + label + '</b></font>', SSLB))
        for b in bullets:
            items.append(Paragraph("  " + b, SSIT))
        items.append(sp(1))
    t = Table([[items]], colWidths=[W * mm])
    t.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 1,  C_BDR),
        ("BACKGROUND",    (0, 0), (-1, -1),     colors.white),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    return KeepTogether([t, sp(3)])


def phase_block(title, goal, actions, milestones, cost):
    items = []
    items.append(Paragraph(title, SPHH))
    items.append(Paragraph("<b>目标：</b>" + goal, SSM))
    items.append(sp(1))
    items.append(Paragraph("<b>具体动作</b>", SH4))
    for a in actions:
        items.append(Paragraph("  " + a, SPHB))
    items.append(sp(1))
    items.append(Paragraph("<b>里程碑</b>", SH4))
    for m in milestones:
        items.append(Paragraph("  " + m, SPHM))
    items.append(sp(1))
    items.append(Paragraph("<b>成本：</b>" + cost, SSM))
    t = Table([[items]], colWidths=[W * mm])
    t.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 1,  colors.HexColor("#c3d3f7")),
        ("BACKGROUND",    (0, 0), (-1, -1),     colors.HexColor("#f0f4ff")),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    return KeepTogether([t, sp(3)])


def review_block(reviewer, score, positives, issues, conclusion):
    items = []
    items.append(Paragraph(reviewer + "  [" + score + "]", SRVH))
    if positives:
        items.append(Paragraph("<b>正面判断</b>", SH4))
        for p in positives:
            items.append(Paragraph("  " + p, SRVP))
    if issues:
        items.append(sp(1))
        items.append(Paragraph("<b>问题 / 补充</b>", SH4))
        for i in issues:
            items.append(Paragraph("  " + i, SRVI))
    items.append(sp(1))
    items.append(Paragraph("<b>结论：</b>" + conclusion, SSM))
    t = Table([[items]], colWidths=[W * mm])
    t.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 1,  C_BDR),
        ("BACKGROUND",    (0, 0), (-1, -1),     colors.white),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    return KeepTogether([t, sp(3)])


def _chrome(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(C_DARK)
    canvas.rect(0, A4[1] - 8 * mm, A4[0], 8 * mm, fill=1, stroke=0)
    canvas.setFont(FB, 9)
    canvas.setFillColor(colors.white)
    canvas.drawString(20 * mm, A4[1] - 5.5 * mm,
                      "Synapse for FinLease -- 应用场景与推广方案")
    canvas.drawRightString(A4[0] - 20 * mm, A4[1] - 5.5 * mm, "2026-04-26 | v1.0")
    canvas.setFillColor(C_DARK)
    canvas.rect(0, 0, A4[0], 8 * mm, fill=1, stroke=0)
    canvas.setFont(FN, 8)
    canvas.setFillColor(colors.white)
    canvas.drawCentredString(A4[0] / 2, 2.5 * mm, "Synapse Multi-Agent | 机密，仅供内部参考")
    if doc.page > 1:
        canvas.setFillColor(C_GRAY)
        canvas.setFont(FN, 8)
        canvas.drawCentredString(A4[0] / 2, 10 * mm, "第 " + str(doc.page) + " 页")
    canvas.restoreState()


# ---- Build ------------------------------------------------------------------
def build(out):
    doc = SimpleDocTemplate(
        out, pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title="Synapse for 金融租赁 -- 应用场景与推广方案",
        author="Synapse Multi-Agent 团队")

    s = []

    # Title
    s += [sp(8), h1("Synapse for 金融租赁"), h1("应用场景与推广方案"), sp(2), hr(),
          Paragraph("版本：v1.0  |  日期：2026-04-26  |  状态：定稿（智囊团评审通过）", SME),
          Paragraph("适用对象：经营金融租赁业务、当前依赖15人外包研发团队、意图引入AI工具降低外包依赖的中小型金融机构", SME),
          sp(4)]

    # Ch1
    s += [h2("1. 现状判断"),
          h3("1.1 金融租赁公司特殊性"),
          bd("金融租赁属于持牌金融机构，受国家金融监督管理总局监管。带来三个核心约束："),
          h4("强监管合规约束"),
          bl("代码部署须经内控审批，不能随意推生产环境"),
          bl("客户数据（贷款申请、还款记录、征信信息）属于金融敏感数据，不得出境、不得传入未经审查的第三方API"),
          bl("系统变更须有变更记录、影响评估、回滚方案"),
          sp(2), h4("核心业务流程（5个环节）"),
          tbl([["环节",     "业务动作",               "系统依赖"],
               ["客户准入", "资质审查、信用评分、KYC", "征信系统对接、工商查询"],
               ["贷款审核", "风控模型计算、审批流转",  "核心业务系统、OA工作流"],
               ["放款",     "合同签署、资金划拨",       "核心账务系统、银行接口"],
               ["还款管理", "还款提醒、台账核对",       "账务系统、短信通道"],
               ["逾期催收", "催收任务分配、记录跟踪",  "CRM、外呼系统"]],
              ws=[28*mm, 65*mm, 62*mm]),
          sp(2), h4("当前15人外包承担的工作（推断）"),
          tbl([["职能",            "人数估算", "工作内容"],
               ["功能迭代开发",    "6-8人",    "内部工具需求、报表定制、工作流配置"],
               ["系统维护/BUG修复","3-4人",    "线上问题处理、数据修复"],
               ["日常运维",        "2-3人",    "服务器监控、部署上线、数据库维护"],
               ["测试",            "1-2人",    "功能测试、回归测试"]],
              ws=[40*mm, 25*mm, 90*mm]),
          qu("关键发现：外包工作量中，估计40-60%属于低复杂度重复性工作——这正是AI的最佳切入点。"),
          h3("1.2 AI替代的可行性边界"),
          tbl([["类别",    "具体内容"],
               ["可替代",
                "内部工具类需求的代码生成（CRUD、报表、表单）/ 需求文档（PRD）结构化输出 / "
                "测试用例生成与自动化脚本 / 日志分析与运维报告 / 合规文档检索与整理"],
               ["不可替代",
                "核心风控模型开发与调优（需金融+技术复合专家）/ 涉及征信数据的API调用（监管红线）/ "
                "核心账务系统架构改造（重构风险极高）/ 与外部监管系统的接口对接"]],
              ws=[22*mm, 133*mm])]

    # Ch2
    s += [h2("2. 可落地的应用场景（5个）")]

    s.append(scene_card(
        "场景一：需求管理AI化（首选切入点）",
        diff="落地难度：低", dcol="#276749",
        can=["PM用自然语言描述需求，AI自动生成PRD模板（功能描述 + 用户故事 + 验收标准）",
             "自动生成接口设计草案、数据库字段建议、开发任务拆解清单",
             "历史需求文档沉淀到知识库，相似需求直接复用"],
        rep=["外包团队的需求沟通和理解转化环节（减少因需求不清导致的返工）",
             "外包项目经理的文档整理工作"],
        cant=["替代PM对业务的理解判断——AI生成的PRD必须人工审查",
              "涉及风控规则的需求设计——仍需风控专家参与"],
        eff=["需求文档产出时间：2-3天 → 2-4小时",
             "外包开发返工率降低30-50%",
             "预计替代1-2人的文档协调工作量"]))

    s.append(scene_card(
        "场景二：内部工具代码生成（替代效果最显著）",
        diff="落地难度：中", dcol="#c05621",
        can=["生成内部管理后台的CRUD功能代码（客户列表、合同查询、报表下载）",
             "生成数据报表的SQL查询语句和导出脚本",
             "生成工作流配置代码（审批流、通知规则）",
             "代码审查：检查逻辑漏洞、命名规范、注释完整性"],
        rep=["外包团队的低复杂度开发任务（估计占工作量40-60%）",
             "简单的数据提取和报表需求（让外包写个SQL的场景）"],
        cant=["生产系统核心业务逻辑——金融计算（利率、罚息）需要专业审查",
              "与征信/银行系统的对接代码——需要架构师评审",
              "直接部署上线——仍须经过内控审批流程"],
        eff=["简单功能开发周期：1-2周 → 2-3天",
             "外包人员需求：减少3-5人（保留架构师和核心开发）"]))

    s.append(scene_card(
        "场景三：测试自动化",
        diff="落地难度：中", dcol="#c05621",
        can=["根据PRD和代码自动生成测试用例清单",
             "生成接口测试脚本（Postman Collection / pytest脚本）",
             "回归测试脚本：每次发版前自动跑核心功能验证"],
        rep=["外包测试人员的重复性回归测试工作",
             "手写测试用例的时间（2天 → 2小时）"],
        cant=["业务逻辑测试的判断——测试用例正确与否仍需人工验证",
              "性能测试和压测场景设计"],
        eff=["回归测试覆盖率：30% → 70%+",
             "每次发版前测试时间：3天 → 1天",
             "外包测试人员需求：减少1-2人"]))

    s.append(scene_card(
        "场景四：运维监控与日志分析",
        diff="落地难度：中低", dcol="#276749",
        can=["自动分析系统日志，提取异常模式",
             "生成日志分析报告（自然语言描述，无需逐条查日志）",
             "标准化告警处理：触发 → AI分析根因 → 给出建议 → 通知负责人",
             "生成运维月报（系统健康度、发版记录、故障统计）"],
        rep=["外包运维人员的日常巡检工作",
             "故障复盘报告的撰写工作"],
        cant=["执行生产环境变更——仍须人工操作",
              "替代DBA的数据库优化工作"],
        eff=["运维巡检时间：2-3小时/天 → 30分钟/天",
             "故障响应时间缩短50%",
             "外包运维需求：减少1-2人"]))

    s.append(scene_card(
        "场景五：知识库 + 合规文档管理（金融公司特别需要）",
        diff="落地难度：低", dcol="#276749",
        can=["监管文件、产品规则、操作手册结构化入库，支持自然语言检索",
             "新员工培训材料自动生成（基于手册生成问答 + 培训测试题）",
             "新功能上线前AI合规初步自查（对照监管规定）",
             "监管文件变更追踪：新规出台时自动比对与现有业务的冲突点"],
        rep=["员工反复询问「这个规定在哪儿查」的低效信息获取",
             "合规部门手工整理监管文件的时间"],
        cant=["给出最终合规结论——必须由合规官确认",
              "替代法律顾问的专业判断"],
        eff=["合规信息查询效率提升5-10倍",
             "新员工上手时间缩短",
             "新功能合规风险提前发现"]))

    # Ch3
    s += [h2("3. PM AI化路径（3阶段）"),
          qu("前提假设：PM 2-4人，可能无编程背景；公司有IT架构师可提供技术指导；至少一个PM愿意先行试点。"),
          sp(2)]

    s.append(phase_block(
        "阶段一：工具化阶段（0-3个月）",
        goal="PM能用AI独立完成简单需求",
        actions=[
            "安装Claude Code CLI，建立公司专属的基础提示词库（适配金融租赁业务场景）",
            "PM学会用自然语言描述需求，AI生成PRD（每天练习1-2个真实需求）",
            "PM学会让AI生成简单功能的代码（从最简单的数据查询报表开始）",
            "PM学会读懂AI生成的代码（不需要能写，但要会审查基本逻辑）",
            "建立第一个知识库原型（把最常用的10-20个操作规范录入）",
        ],
        milestones=[
            "M1：第一个完整需求文档由AI辅助产出，PM评分>=7/10",
            "M2：第一段可运行的报表SQL由AI生成并上线",
            "M3：替代至少1个外包的简单需求（从接单到上线，PM独立完成）",
        ],
        cost="Claude API约$50-200/月，PM学习时间约20-30%工作量"))

    s.append(phase_block(
        "阶段二：流程化阶段（3-6个月）",
        goal="PM能独立完成中等复杂度需求的全周期",
        actions=[
            "建立公司专属Harness配置（定义金融租赁业务规则、代码规范、合规要求）",
            "建立需求管理流程：AI生成 → PM审查 → 架构师评审 → 开发执行",
            "建立代码审查流程：AI生成 → PM初审 → 架构师确认 → 内控审批 → 上线",
            "知识库扩展：覆盖产品规则、监管文件、历史需求文档",
            "测试自动化上线：核心功能建立回归测试套件",
        ],
        milestones=[
            "M1：Harness配置文件完成，AI输出质量稳定",
            "M2：外包人员减少到8-10人",
            "M3：PM团队能独立交付70%的内部工具需求",
        ],
        cost="Claude API约$200-500/月"))

    s.append(phase_block(
        "阶段三：体系化阶段（6个月后）",
        goal="AI-Native产品团队，外包仅保留核心架构支持",
        actions=[
            "建立简化版Multi-Agent体系：需求Agent+开发Agent+测试Agent+运维Agent",
            "自动化情报管线：AI定期扫描监管动态、竞品信息、技术趋势",
            "外包团队重组：裁减到2-3人（1个架构师+1-2个遗留系统维护）",
            "知识库成为公司核心资产：所有业务规则、历史决策、操作手册全量入库",
        ],
        milestones=[
            "M1：外包减少到3-5人，AI工具月成本<外包节省额的20%",
            "M2：PM团队能处理90%的非架构级需求",
            "M3：建立完整的AI工具治理规范（符合监管要求）",
        ],
        cost="Claude API约$500-1000/月"))

    # Ch4
    s += [h2("4. 推广策略"),
          h3("4.1 引入策略：从一个痛点切入"),
          qu("建议首选切入点：内部报表需求 — 高频出现、SQL是AI最擅长的任务之一、"
             "不涉及核心业务逻辑、效果可量化。"),
          bd("先不说裁外包，说提高内部团队效率。"
             "等AI工具跑通2-3个真实案例，让数据说话，再进入减少外包的讨论。"),
          sp(2), h3("4.2 关键干系人策略"),
          tbl([["干系人",    "策略"],
               ["PM团队",    "找最有好奇心和技术意愿的那个人先做试点，成功后让他带其他PM。不要一开始全员推。"],
               ["IT架构师",  "最关键的盟友，第一时间让他参与工具选型和代码审查规范制定，给他归属感。"],
               ["外包团队",  "不要事先通知。先跑通内部能力，让自然竞争说明问题。"]],
              ws=[25*mm, 130*mm]),
          sp(2), h3("4.3 成功条件（缺一不可）"),
          tbl([["条件",                    "说明",                              "验证方式"],
               ["至少一个PM有意愿且时间充足", "学习期需投入30-40%工作时间",         "和PM明确确认时间承诺"],
               ["IT架构师支持",             "不能绕开他，否则代码审查和上线会卡死", "第一周就让他参与工具调研"],
               ["有明确的第一个项目",        "范围明确、风险低、有数据对比",         "提前选好，不要等随机来一个"],
               ["管理层支持",               "否则PM的学习时间会被日常需求挤占",     "明确试点期PM可以花时间学AI工具"]],
              ws=[42*mm, 72*mm, 51*mm]),
          sp(2), h3("4.4 风险点及应对"),
          tbl([["风险",                         "概率", "影响", "应对措施"],
               ["金融监管对AI生成代码的额外审查要求", "高",  "中",
                "提前与合规部沟通，建立AI生成代码标注和额外审查流程"],
               ["PM学习曲线比预期慢",               "高",  "中",
                "第一个月只做最简单的任务，建立信心比速度更重要"],
               ["外包团队制造阻力",                 "高",  "中",
                "用实际案例反驳，让结果说话"],
               ["AI生成代码包含金融业务逻辑错误",    "中",  "高",
                "建立强制审查流程，绝不直接上线未审查的AI代码"],
               ["客户数据合规疑虑",                 "中",  "高",
                "明确规定：任何含真实客户数据的内容不得传入AI，用脱敏数据"],
               ["成本超预期（API费用）",             "低",  "低",
                "设定月度API费用上限，前3个月控制在$100以内"]],
              ws=[45*mm, 12*mm, 12*mm, 76*mm])]

    # Ch5
    s += [h2("5. 资源投入估算"),
          h3("工具成本"),
          tbl([["工具",           "月费用（估算）",     "说明"],
               ["Claude API",     "$100-500",          "按使用量计费，初期较低"],
               ["Claude Code CLI","包含在API费用中",    "不额外收费"],
               ["知识库存储",      "$0-50",             "本地方案免费"]],
              ws=[55*mm, 35*mm, 75*mm]),
          sp(2), h3("投资回报估算"),
          qu("当前假设：15人外包，平均约1.5-2万元/人/月 → 总计约22-30万/月。"),
          tbl([["阶段",    "外包规模",      "月节省额",    "AI工具月成本"],
               ["阶段一结束", "减少2-3人",  "3-6万/月",   "~700元"],
               ["阶段二结束", "减少到8-10人","7-15万/月",  "~2000元"],
               ["阶段三结束", "减少到2-3人", "18-22万/月", "~4000元"]],
              ws=[35*mm, 40*mm, 40*mm, 40*mm]),
          Paragraph("整体ROI > 50:1 — 阶段一结束即可实现正向回报", SROI)]

    # Ch6
    s += [h2("6. 一句话结论")]
    _txt = ("金融租赁公司引入Synapse体系的核心价值在于：用AI工具赋能内部PM接管外包的低复杂度工作，"
            "而非试图替代核心金融系统或绕过监管合规流程。从报表需求切入、3个月内验证第一个ROI、"
            "保留架构师作为技术把关者——这是在金融监管环境下最稳健可行的AI转型路径。")
    ct = Table([[Paragraph(_txt, SCO)]], colWidths=[W * mm])
    ct.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_DARK),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
    ]))
    s += [ct, sp(4)]

    # Appendix
    s.append(PageBreak())
    s += [h2("附录：智囊团评审意见"),
          sm("评审时间：2026-04-26 | 评审方式：多角色模拟评审"),
          sp(2)]

    s.append(review_block(
        "execution_auditor（执行审计师）", "4.2 / 5.0 -- 通过",
        positives=[
            "六个章节覆盖现状、场景、路径、策略、成本、结论，结构完整",
            "5个应用场景均有清晰的能做/不能做/替代边界，避免了夸大AI能力",
            "3阶段路径有具体里程碑（M1/M2/M3），可以被追踪和验证",
            "推广策略明确指出了关键干系人和成功条件",
        ],
        issues=[
            "场景三（测试自动化）实施路径略抽象，对无技术背景PM需要更多工具链指引",
            "阶段一和阶段二的边界稍模糊，实际执行可能需要更细的检查点",
            "外包团队阻力应对措施较被动，可补充更主动的沟通策略",
        ],
        conclusion="方案可执行，建议推进。场景三和阶段边界的细化可在实际启动时迭代调整。"))

    s.append(review_block(
        "risk_analyst（风险分析师）", "4.0 / 5.0 -- 通过（附重要补充）",
        positives=[
            "金融监管对AI生成代码的额外审查要求 — 已识别",
            "真实客户数据不得传入AI的合规红线 — 已识别",
            "核心业务系统不适合AI改造 — 已识别",
            "外包团队信息不对称问题 — 已识别",
        ],
        issues=[
            "风险A：AI代码责任归属 — 金融机构变更审批制度下需提前明确，建立AI辅助开发责任声明规范",
            "风险B：供应商数据处理合规 — Anthropic DPA是否符合中国金融监管要求，需法务确认",
            "风险C：AI生成代码知识产权 — 法律上存在争议，建议在公司AI使用政策中明确约定",
            "风险D：单一供应商业务连续性 — 建立关键流程的人工兜底方案",
        ],
        conclusion="核心合规红线把握准确。建议将4项补充风险纳入公司AI治理政策，并在方案提交时口头说明。"))

    s.append(review_block(
        "growth_strategist（增长策略师）", "4.4 / 5.0 -- 通过",
        positives=[
            "从痛点切入，不铺大摊子——报表需求作为切入点选择精准，能快速产生可展示的成功案例",
            "先增效，再减量——有效规避推进过程中最大的政治阻力",
            "优先拉拢IT架构师的逻辑正确，这个角色在金融公司技术话语权很强",
        ],
        issues=[
            "建议一：第一个成功案例要可视化、可传播——建立效果对比记录（外包 vs. PM+AI的时间和质量对比）",
            "建议二：给试点PM一个内部认可——金融公司文化偏保守，示范效应比任何培训都有说服力",
            "建议三：设定明确的退出条件——3个月后仍未完成M3里程碑，诊断原因调整策略",
        ],
        conclusion="推广策略可行，切入点选择准确。建议在启动前确认第一个项目的范围和对比基准。"))

    s += [sp(2), h3("评审综合结论"),
          tbl([["评审维度",          "评分",        "结论"],
               ["方案完整性与可执行性","4.2 / 5.0", "通过"],
               ["金融行业风险识别",   "4.0 / 5.0", "通过（附4项补充风险）"],
               ["推广策略可行性",     "4.4 / 5.0", "通过"],
               ["综合评分",          "4.2 / 5.0", "评审通过，建议定稿"]],
              ws=[70*mm, 35*mm, 60*mm]),
          sp(4),
          Paragraph("Synapse Multi-Agent 团队 | 执行者：industry_analyst + harness_engineer + "
                    "ai_systems_dev + knowledge_engineer + growth_strategist | Lysander CEO 审查", SFT),
          Paragraph("本文件由AI团队协作生成，评审意见为多角色模拟评审，供参考使用", SFT)]

    doc.build(s, onFirstPage=_chrome, onLaterPages=_chrome)
    print("[OK] PDF generated:", out)


if __name__ == "__main__":
    _out = r"C:\Users\lysanderl_janusd\Synapse-Mini\obs\06-daily-reports\finlease-synapse-proposal.pdf"
    build(_out)
