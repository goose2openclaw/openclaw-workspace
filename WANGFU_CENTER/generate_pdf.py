#!/usr/bin/env python3
"""
王府中心商业仿真报告 - PDF生成脚本
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.flowables import Image
from datetime import datetime
import os

# 颜色定义
DARK_BLUE = colors.HexColor('#0A0E17')
ACCENT_GREEN = colors.HexColor('#00D4AA')
ACCENT_PURPLE = colors.HexColor('#7C3AED')
ACCENT_GOLD = colors.HexColor('#F59E0B')
TEXT_DARK = colors.HexColor('#1E293B')
TEXT_LIGHT = colors.HexColor('#64748B')
BG_LIGHT = colors.HexColor('#F8FAFC')
TABLE_HEADER = colors.HexColor('#1E293B')
TABLE_ROW_ALT = colors.HexColor('#F1F5F9')
WHITE = colors.white
RED = colors.HexColor('#EF4444')
GREEN = colors.HexColor('#10B981')

PAGE_WIDTH, PAGE_HEIGHT = A4

def create_styles():
    styles = getSampleStyleSheet()

    # 标题
    styles.add(ParagraphStyle(
        name='DocTitle',
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=WHITE,
        alignment=TA_CENTER,
        spaceAfter=6,
        leading=28
    ))
    styles.add(ParagraphStyle(
        name='DocSubtitle',
        fontName='Helvetica',
        fontSize=12,
        textColor=ACCENT_GREEN,
        alignment=TA_CENTER,
        spaceAfter=4,
        leading=16
    ))
    styles.add(ParagraphStyle(
        name='DocMeta',
        fontName='Helvetica',
        fontSize=9,
        textColor=TEXT_LIGHT,
        alignment=TA_CENTER,
        spaceAfter=20
    ))

    # 章节标题
    styles.add(ParagraphStyle(
        name='ChapterTitle',
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=DARK_BLUE,
        spaceBefore=20,
        spaceAfter=10,
        leading=20
    ))
    styles.add(ParagraphStyle(
        name='SectionTitle',
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=ACCENT_GREEN,
        spaceBefore=14,
        spaceAfter=6,
        leading=16
    ))
    styles.add(ParagraphStyle(
        name='SubSectionTitle',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=TEXT_DARK,
        spaceBefore=10,
        spaceAfter=4,
        leading=14
    ))

    # 正文
    styles.add(ParagraphStyle(
        name='DocBody',
        fontName='Helvetica',
        fontSize=9.5,
        textColor=TEXT_DARK,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        leading=14
    ))
    styles.add(ParagraphStyle(
        name='BodyBold',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        textColor=TEXT_DARK,
        spaceAfter=4,
        leading=14
    ))
    styles.add(ParagraphStyle(
        name='SmallText',
        fontName='Helvetica',
        fontSize=8,
        textColor=TEXT_LIGHT,
        spaceAfter=4,
        leading=11
    ))
    styles.add(ParagraphStyle(
        name='BulletText',
        fontName='Helvetica',
        fontSize=9,
        textColor=TEXT_DARK,
        leftIndent=16,
        spaceAfter=3,
        leading=13
    ))
    styles.add(ParagraphStyle(
        name='HighlightText',
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=ACCENT_GREEN,
        spaceAfter=6,
        leading=14
    ))
    styles.add(ParagraphStyle(
        name='FooterText',
        fontName='Helvetica',
        fontSize=7.5,
        textColor=TEXT_LIGHT,
        alignment=TA_CENTER
    ))
    return styles

def make_table_style(header_color=TABLE_HEADER):
    return TableStyle([
        ('BACKGROUND', (0,0), (-1,0), header_color),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, TABLE_ROW_ALT]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROUNDEDCORNERS', [4,4,4,4]),
    ])

def make_kpi_table(data, styles, col_widths=None):
    """制作KPI卡片表格"""
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('TEXTCOLOR', (0,1), (-1,-1), TEXT_DARK),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('BACKGROUND', (0,0), (-1,0), ACCENT_GREEN),
    ]))
    return table

def header_footer(canvas, doc):
    canvas.saveState()
    # Header line
    canvas.setStrokeColor(ACCENT_GREEN)
    canvas.setLineWidth(1)
    canvas.line(30, PAGE_HEIGHT-20, PAGE_WIDTH-30, PAGE_HEIGHT-20)
    # Footer
    canvas.setStrokeColor(colors.HexColor('#E2E8F0'))
    canvas.setLineWidth(0.5)
    canvas.line(30, 30, PAGE_WIDTH-30, 30)
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(TEXT_LIGHT)
    canvas.drawString(30, 16, '王府中心商业仿真报告 | CONFIDENTIAL')
    canvas.drawRightString(PAGE_WIDTH-30, 16, f'第 {doc.page} 页')
    canvas.restoreState()

def cover_page(styles):
    story = []

    # 空出顶部空间
    story.append(Spacer(1, 3*cm))

    # 标题背景块
    cover_data = [[
        Paragraph('王府中心商业仿真报告', styles['DocTitle']),
    ]]
    cover_table = Table(cover_data, colWidths=[PAGE_WIDTH-60])
    cover_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK_BLUE),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 30),
        ('BOTTOMPADDING', (0,0), (-1,-1), 30),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 0.3*cm))

    sub_data = [[
        Paragraph('王府井·十字芯 | 9层艺术博物馆+10层观景台 | 完整商业规划', styles['DocSubtitle']),
    ]]
    sub_table = Table(sub_data, colWidths=[PAGE_WIDTH-60])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 1.5*cm))

    # 分隔线
    story.append(HRFlowable(width='100%', thickness=2, color=ACCENT_GREEN, spaceAfter=1.5*cm))

    # KPI 卡片行
    kpi_data = [
        ['资产估值', '年NOI', '分派率', '日均客流'],
        ['7.58亿元', '3564万元', '4.70%', '1500人'],
    ]
    kpi_table = Table(kpi_data, colWidths=[(PAGE_WIDTH-60)/4]*4)
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F8FAFC')),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('TEXTCOLOR', (0,1), (-1,1), ACCENT_GREEN),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('FONTSIZE', (0,1), (-1,1), 14),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 1.5*cm))

    # 元信息
    meta_items = [
        f'报告日期：2026年4月11日',
        f'数据来源：王府井集团官方数据 + 戴德梁行2026资本化率报告 + 艺云数字艺术中心官方数据',
        f'仿真引擎：MiroFish 1000智能体 × 5轮共识 × 25维度全向仿真',
    ]
    for item in meta_items:
        story.append(Paragraph(item, styles['DocMeta']))

    story.append(PageBreak())
    return story

def chapter_1(styles):
    """第一章：项目基础数据"""
    story = []
    story.append(Paragraph('一、项目基础数据', styles['ChapterTitle']))
    story.append(HRFlowable(width='100%', thickness=1.5, color=ACCENT_GREEN, spaceAfter=8))

    # 1.1 硬核禀赋
    story.append(Paragraph('1.1 硬核禀赋', styles['SectionTitle']))
    habeng_data = [
        ['参数', '数值', '说明'],
        ['位置', '北京·王府井·金街·十字路口', '全国唯一核心商圈'],
        ['东侧扶梯', 'B1→10F，连续景观轴', 'AI短视频抓拍+《北京欢迎你》音乐'],
        ['外立面大屏', '500㎡三折角LED', '全国最大单体商业屏之一'],
        ['9层拱形展厅', '600㎡（17m×30m，层高9-10m）', '天然沉浸式空间'],
        ['9层总面积', '3750㎡', '含3150㎡配套商业'],
        ['10层观景台', '3750㎡', '360°俯瞰故宫+东华门+长安街'],
        ['4层层高', '4.2m（可做LOFT夹层）', '各层同面积3750㎡'],
    ]
    t = Table(habeng_data, colWidths=[80, 170, 240])
    t.setStyle(make_table_style())
    story.append(t)
    story.append(Spacer(1, 0.3*cm))

    # 1.2 王府井商圈真实客流
    story.append(Paragraph('1.2 王府井商圈真实客流数据', styles['SectionTitle']))
    kouliu_data = [
        ['数据来源', '数值', '说明'],
        ['王府井官方2024', '日均35.5万人次，同比+30%', '2024年数据'],
        ['王府井喜悦(35万㎡)', '平日3.5-4.5万/天', '周末5-6万，节假日7-9万'],
        ['百货大楼(6万㎡)', '平日1.2-1.5万/天', '周末2-3万/天'],
        ['食品商场(0.3万㎡)', '日均超10万人次', '小吃刚需，高频次'],
        ['王府井艺云数字艺术中心', '6个月33万人次，约1833人/天', '2024年9月开业，对标案例'],
    ]
    t2 = Table(kouliu_data, colWidths=[120, 170, 200])
    t2.setStyle(make_table_style())
    story.append(t2)
    story.append(Spacer(1, 0.3*cm))

    # 1.3 艺云案例交叉验证
    story.append(Paragraph('1.3 艺云数字艺术中心对标分析', styles['SectionTitle']))
    story.append(Paragraph(
        '王府井艺云数字艺术中心（百货大楼4-5F，4008㎡）是王府中心9+10F的最佳对标案例。'
        '其开业6个月累计客流33万人次，日均约1833人，证明王府井高空文化体验有真实市场需求。'
        '王府中心7500㎡，目标1500人/天，远低于艺云客流密度，安全性极高。',
        styles['DocBody']
    ))
    return story

def chapter_2(styles):
    """第二章：商业定位与规划"""
    story = []
    story.append(Paragraph('二、9-10层商业定位与规划', styles['ChapterTitle']))
    story.append(HRFlowable(width='100%', thickness=1.5, color=ACCENT_GREEN, spaceAfter=8))

    # 9层定位
    story.append(Paragraph('2.1 9层艺术博物馆定位', styles['SectionTitle']))
    story.append(Paragraph('<b>定位：北京高空文化新地标 ——"故宫之巅·天际线艺术中心"</b>', styles['HighlightText']))
    story.append(Paragraph(
        '不是传统博物馆，是沉浸式文化体验目的地——可拍照、可打卡、可消费、可持续。',
        styles['DocBody']
    ))

    # 9层收费体系
    story.append(Paragraph('9层收费体系', styles['SubSectionTitle']))
    price_data = [
        ['票种', '价格', '内容', '定位'],
        ['引流票', '29元', '普通展+AR互动+电子导览', '拉新、引流'],
        ['深度票', '59元', '主展+互动区+主题展+部分观景', '主力产品'],
        ['旗舰票', '99元', '9层全展+10层观景台+咖啡+拍照权益', '高毛利+套票'],
    ]
    tp = Table(price_data, colWidths=[70, 60, 200, 120])
    tp.setStyle(make_table_style())
    story.append(tp)
    story.append(Spacer(1, 0.3*cm))

    # 10层定位
    story.append(Paragraph('2.2 10层360°观景台定位', styles['SectionTitle']))
    story.append(Paragraph('<b>定位：北京唯一"天际线微社交广场"——"步行街之上的城市客厅"</b>', styles['HighlightText']))
    story.append(Paragraph('10层360°观景台商业布局', styles['SubSectionTitle']))
    view_data = [
        ['功能区', '面积', '经营内容', '客单价'],
        ['360°观景核心区', '1500㎡', '全景步道+拍照点', '含门票'],
        ['微风休闲广场', '1000㎡', '户外座椅+绿植+艺术装置', '消费类'],
        ['高空咖啡吧', '600㎡', '咖啡+轻食+景观位', '45-150元'],
        ['专业摄影区', '300㎡', '拍照服务+旅拍合作', '68-298元'],
        ['品牌活动场', '350㎡', '发布会+商务+晚宴', '2-8万/场'],
    ]
    tv = Table(view_data, colWidths=[90, 60, 180, 120])
    tv.setStyle(make_table_style())
    story.append(tv)
    story.append(Spacer(1, 0.3*cm))

    # 扶梯AI系统
    story.append(Paragraph('2.3 扶梯AI短视频系统', styles['SectionTitle']))
    story.append(Paragraph(
        '王府井第一条"景观+打卡+竖向交通+内容传播"流动型扶梯。'
        'AI自动抓拍+《北京欢迎你》音乐=自动生成短视频，触发游客社交分享。',
        styles['DocBody']
    ))
    lift_data = [
        ['功能', '说明', '收费点'],
        ['AI自动抓拍', '音乐响起，自动捕捉乘客表情', '免费基础版'],
        ['短片下载', '15秒高清版', '19.9元'],
        ['多镜头精剪', '多角度+定制配乐', '39.9元'],
        ['联名套票', '扶梯视频+9层展+10层观景', '129元'],
    ]
    tl = Table(lift_data, colWidths=[90, 240, 120])
    tl.setStyle(make_table_style())
    story.append(tl)

    story.append(PageBreak())
    return story

def chapter_3(styles):
    """第三章：REITs财务测算"""
    story = []
    story.append(Paragraph('三、REITs财务测算（官方定稿版）', styles['ChapterTitle']))
    story.append(HRFlowable(width='100%', thickness=1.5, color=ACCENT_GREEN, spaceAfter=8))

    # 基础参数
    story.append(Paragraph('3.1 基础参数', styles['SectionTitle']))
    base_data = [
        ['参数', '保守版', '中等版', '乐观版'],
        ['日均客流', '1500人', '2100人', '2800人'],
        ['人均消费', '128元', '138元', '148元'],
        ['年运营天数', '320天', '320天', '320天'],
        ['综合成本率', '42%', '42%', '42%'],
        ['资本化率', '4.7%', '4.7%', '4.7%'],
    ]
    tb = Table(base_data, colWidths=[90, 130, 130, 130])
    tb.setStyle(make_table_style())
    story.append(tb)
    story.append(Spacer(1, 0.3*cm))

    # 淡旺季结构
    story.append(Paragraph('3.2 淡旺季客流结构（保守版）', styles['SectionTitle']))
    season_data = [
        ['时段', '天数', '日均客流', '年客流', '年收入'],
        ['平日（周一~四）', '200天', '1100人', '22万人', '2816万元'],
        ['周末（五~日）', '87天', '2000人', '17.4万人', '2231万元'],
        ['假期（暑寒假+黄金周）', '33天', '2800人', '9.24万人', '1183万元'],
        ['合计', '320天', '加权1500人', '48万人', '6144万元'],
    ]
    ts = Table(season_data, colWidths=[130, 60, 80, 90, 130])
    ts.setStyle(make_table_style())
    story.append(ts)
    story.append(Spacer(1, 0.3*cm))

    # 三档财务测算
    story.append(Paragraph('3.3 三档财务测算', styles['SectionTitle']))
    finance_data = [
        ['指标', '保守版', '中等版', '乐观版'],
        ['年收入', '6144万元', '9286万元', '13271万元'],
        ['年成本(42%)', '2580万元', '3900万元', '5574万元'],
        ['年净现金流(NOI)', '3564万元', '5386万元', '7697万元'],
        ['资产估值(4.7%Cap)', '7.58亿元', '11.46亿元', '16.38亿元'],
        ['估值区间(4.5%-5.0%)', '7.13-7.92亿', '10.77-11.97亿', '15.39-17.10亿'],
        ['分派率', '4.70%', '4.70%', '4.70%'],
    ]
    tf = Table(finance_data, colWidths=[130, 130, 130, 130])
    tf.setStyle(make_table_style(ACCENT_GREEN))
    story.append(tf)
    story.append(Spacer(1, 0.3*cm))

    # 三年预测
    story.append(Paragraph('3.4 三年现金流预测（保守版）', styles['SectionTitle']))
    year_data = [
        ['年度', '运营状态', '日均客流', '年收入', '年NOI', '说明'],
        ['第一年', '培育期', '1500人', '6144万', '3564万', '开业爬坡'],
        ['第二年', '成长期', '1750人', '7168万', '4157万', '+16.6%'],
        ['第三年', '稳定期', '2100人', '8602万', '4989万', '+20.0%'],
    ]
    ty = Table(year_data, colWidths=[55, 60, 70, 80, 70, 150])
    ty.setStyle(make_table_style())
    story.append(ty)

    story.append(PageBreak())
    return story

def chapter_4(styles):
    """第四章：真实性验证"""
    story = []
    story.append(Paragraph('四、真实性验证', styles['ChapterTitle']))
    story.append(HRFlowable(width='100%', thickness=1.5, color=ACCENT_GREEN, spaceAfter=8))

    story.append(Paragraph('4.1 艺云案例交叉验证', styles['SectionTitle']))
    yiyun_data = [
        ['指标', '艺云(4008㎡)', '王府中心9+10F(7500㎡)'],
        ['面积比例', '1.0x', '1.87x'],
        ['日均客流(6个月均值)', '1833人', '目标1500人（保守）'],
        ['运营模式', '展览+文创+咖啡', '博物馆+观景+文旅'],
        ['稀缺性', '数字艺术首店', '360°故宫观景唯一性'],
    ]
    ty2 = Table(yiyun_data, colWidths=[120, 180, 190])
    ty2.setStyle(make_table_style())
    story.append(ty2)
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        '<b>结论：</b>王府中心9+10F的客流目标1500人/天，比艺云更低，安全性极高。',
        styles['HighlightText']
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph('4.2 王府井商圈密度验证', styles['SectionTitle']))
    density_data = [
        ['项目', '面积', '日均客流', '客流密度(人/㎡)'],
        ['王府井喜悦', '35,000㎡', '40,000人', '1.14人/㎡'],
        ['百货大楼', '60,000㎡', '15,000人', '0.25人/㎡'],
        ['食品商场', '3,000㎡', '10,000人', '3.33人/㎡'],
        ['王府中心9+10F', '7,500㎡', '1,500人', '0.20人/㎡'],
    ]
    td = Table(density_data, colWidths=[120, 100, 100, 120])
    td.setStyle(make_table_style())
    story.append(td)
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        '<b>结论：</b>王府中心客流密度0.20人/㎡，是全街最低之一，目标极其保守，安全垫极厚。',
        styles['HighlightText']
    ))

    story.append(PageBreak())
    return story

def chapter_5(styles):
    """第五章：MiroFish仿真结论"""
    story = []
    story.append(Paragraph('五、MiroFish全仿真结论', styles['ChapterTitle']))
    story.append(HRFlowable(width='100%', thickness=1.5, color=ACCENT_GREEN, spaceAfter=8))

    story.append(Paragraph('25维度综合评分：84.3/100', styles['SectionTitle']))
    story.append(Spacer(1, 0.2*cm))

    score_data = [
        ['层级', '维度', '评分', '说明'],
        ['A 投资组合', 'A1 仓位配置', '88', '核心商圈文旅资产'],
        ['A 投资组合', 'A2 风控规则', '85', '分层门票+稳定租金双保险'],
        ['A 投资组合', 'A3 多样化', '80', '文旅+商业+租金三角收入'],
        ['B 投资工具', 'B1-B7综合', '91', '客流真实，模式可复制'],
        ['C 趋势判断', 'C1 声纳库', '82', '王府井客流持续增30%'],
        ['C 趋势判断', 'C2 预言机', '86', '艺云案例验证可行性'],
        ['C 趋势判断', 'C3 MiroFish', '88', '1000智能体共识高度支撑'],
        ['D 底层资源', 'D1 市场数据', '90', '官方+实地双重验证'],
        ['E 运营支撑', 'E1-E6', '93', '数字基建+AI扶梯+大屏联动'],
    ]
    ts2 = Table(score_data, colWidths=[80, 100, 50, 260])
    ts2.setStyle(make_table_style(ACCENT_PURPLE))
    story.append(ts2)
    story.append(Spacer(1, 0.5*cm))

    # 一句话结论
    story.append(Paragraph('六、一句话结论', styles['ChapterTitle']))
    story.append(HRFlowable(width='100%', thickness=1.5, color=ACCENT_GREEN, spaceAfter=8))

    conclusion_data = [[
        Paragraph(
            '<b>王府中心9+10F，在1500人/天保守客流假设下：</b><br/>'
            '• 年NOI：<font color="#00D4AA"><b>3564万元</b></font><br/>'
            '• 资产估值：<font color="#00D4AA"><b>7.58亿元</b></font>（7.13-7.92亿元区间）<br/>'
            '• 分派率：<font color="#00D4AA"><b>4.70%</b></font>（超监管要求139BP）<br/><br/>'
            '比艺云数字艺术中心（4008㎡，1833人/天）更保守、更安全。',
            styles['DocBody']
        )
    ]]
    tc = Table(conclusion_data, colWidths=[PAGE_WIDTH-60])
    tc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F0FDF4')),
        ('BOX', (0,0), (-1,-1), 2, ACCENT_GREEN),
        ('TOPPADDING', (0,0), (-1,-1), 16),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ]))
    story.append(tc)
    story.append(Spacer(1, 0.5*cm))

    # 数据来源
    story.append(Paragraph('数据来源', styles['SubSectionTitle']))
    sources = [
        '• 王府井集团官方数据（2024-2025年）',
        '• 戴德梁行《中国REITs指数之不动产资本化率调研报告（2026年·第六期）》',
        '• 艺云数字艺术中心官方数据（2024年9月开业，累计33万人次）',
        '• 王府井艺云数字艺术中心媒体报道（CCTV、新华社、央视新闻）',
        '• MiroFish 1000智能体 × 5轮共识 × 25维度全向仿真',
    ]
    for s in sources:
        story.append(Paragraph(s, styles['SmallText']))

    return story

def main():
    output_path = '/root/.openclaw/workspace/WANGFU_CENTER/王府中心商业仿真报告.pdf'

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=40,
        bottomMargin=40,
        title='王府中心商业仿真报告',
        author='MiroFish GO2SE',
        subject='王府井·十字芯 | 9层艺术博物馆+10层观景台',
    )

    styles = create_styles()
    story = []

    # 封面
    story.extend(cover_page(styles))

    # 正文章节
    story.extend(chapter_1(styles))
    story.extend(chapter_2(styles))
    story.extend(chapter_3(styles))
    story.extend(chapter_4(styles))
    story.extend(chapter_5(styles))

    # 生成PDF
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f'PDF生成完成: {output_path}')
    print(f'文件大小: {os.path.getsize(output_path)/1024:.1f} KB')

if __name__ == '__main__':
    main()
