# -*- coding: utf-8 -*-
"""由 src/cards.py 和样例数据生成：dist/index.html（网站）、dist/skills/*.md（AI 技能包）、dist/llms.txt。
用法：python3 build.py"""
import json, re, html, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from cards import CARDS, GROUPS, DEMO, QUESTIONS, PHASE2, SRC_FW
ROOT = os.path.dirname(os.path.abspath(__file__))
S = lambda p: os.path.join(ROOT, "src", p)
D = lambda p: os.path.join(ROOT, "dist", p)
E = html.escape

LV = [(50, "优", "优", "rgb(0,228,0)", "#0c2a0c"), (100, "良", "良", "rgb(255,255,0)", "#2b2a00"),
      (150, "轻度污染", "轻", "rgb(255,126,0)", "#2a1400"), (200, "中度污染", "中", "rgb(255,0,0)", "#fff"),
      (300, "重度污染", "重", "rgb(153,0,76)", "#fff"), (500, "严重污染", "严重", "rgb(126,0,35)", "#fff")]
AB = {l[2]: l for l in LV}
def lv(a):
    for l in LV:
        if a <= l[0]: return l
    return LV[-1]
def lvtd(text, ab, cls="lv"):
    l = AB[ab.split("-")[-1]]
    return "<td class='%s' style='background:%s;color:%s'>%s</td>" % (cls, l[3], l[4], text)
def fig(title, use, who, body, note="", out=False, demo=False):
    w = "<span class='who%s'>%s</span>" % (" out" if out else "", who) if who else ""
    return "<figure><div class='fh'><b>%s</b><span class='use'>%s</span>%s%s</div><div class='fb'>%s%s</div></figure>" % (
        title, use, DEMO if demo else "", w, body, "<div class='note'>%s</div>" % note if note else "")
def gtable(head, rows):
    return "<div class='scroll'><table class='g'><tr>%s</tr>%s</table></div>" % ("".join("<th>%s</th>" % h for h in head), "".join(rows))

# ---------- 样例数据 ----------
B1 = json.load(open(S("sample_b1.json"), encoding="utf-8"))
A1D = json.load(open(S("sample_a1.json"), encoding="utf-8"))
DAY0 = list(A1D.values())[0]["days"]
daylab = lambda d: "%d/%d" % (int(d[4:6]), int(d[6:8]))

def b1_curve():
    W, H, L, R, T, B = 880, 300, 46, 96, 28, 48
    n = 168; ymax = 80
    x = lambda i: L + (W - L - R) * i / (n - 1)
    y = lambda v: T + (H - T - B) * (1 - v / ymax)
    s = ""
    for v in (0, 20, 40, 60, 80):
        s += "<line x1='%d' x2='%d' y1='%.1f' y2='%.1f' stroke='var(--line2)'/><text x='%d' y='%.1f' text-anchor='end'>%d</text>" % (L, W - R, y(v), y(v), L - 8, y(v) + 4, v)
    for d in range(7):
        s += "<line x1='%.1f' x2='%.1f' y1='%d' y2='%d' stroke='var(--line)'/><text x='%.1f' y='%d' text-anchor='middle'>%s</text>" % (
            x(d * 24), x(d * 24), T, H - B, x(d * 24 + 12), H - B + 17, daylab(DAY0[d]["d"]))
    s += "<text x='%d' y='12' text-anchor='end'>μg/m³</text><text x='%.1f' y='%d' text-anchor='middle'>日期（2026 年），每格 24 小时</text>" % (L - 8, (L + W - R) / 2, H - 6)
    top = max(B1, key=lambda k: B1[k]["max"])
    for k, v in B1.items():
        if k == top: continue
        s += "<polyline fill='none' stroke='var(--ink3)' stroke-width='1' points='%s'/>" % " ".join("%.1f,%.1f" % (x(i), y(min(c, ymax))) for i, c in enumerate(v["h"]))
    v = B1[top]
    s += "<polyline fill='none' stroke='var(--accent)' stroke-width='2' stroke-linejoin='round' points='%s'/>" % " ".join("%.1f,%.1f" % (x(i), y(min(c, ymax))) for i, c in enumerate(v["h"]))
    s += "<circle cx='%.1f' cy='%.1f' r='4' fill='var(--accent)' stroke='var(--surface)' stroke-width='2'/><text x='%.1f' y='%.1f' style='fill:var(--accent);font-weight:700'>%s 峰值 %.1f</text>" % (
        x(v["imax"]), y(v["max"]), x(v["imax"]) + 8, y(v["max"]) - 6, top, v["max"])
    s += "<text x='%d' y='%.1f'>其余 4 个模式</text>" % (W - R + 8, y(22))
    return "<svg viewBox='0 0 %d %d' width='100%%' role='img' aria-label='各模式 PM2.5 逐小时预报曲线'>%s</svg>" % (W, H, s)

def hourlab(i):
    d = DAY0[i // 24]["d"]; h = i % 24
    part = "凌晨" if h < 6 else "上午" if h < 12 else "午后" if h < 18 else "夜间"
    return "%d日%s" % (int(d[6:8]), part)
def b1_table():
    rows = []
    for k, v in B1.items():
        rows.append("<tr><td class='l'>%s</td><td>%.1f</td><td>%s</td><td>%.1f</td>%s<td>未识别</td></tr>" % (k, v["max"], hourlab(v["imax"]), v["smax"], lvtd("优", "优")))
    rows.append("<tr><td class='l'>动态择优 OEF</td><td class='na' colspan='5'>缺测（-999），不参与统计</td></tr>")
    return gtable(["模式", "小时峰值", "峰值时间", "24 小时滑动平均最大值", "滑动平均级别", "污染过程"], rows)
def b2_tables():
    rows = []
    for k, v in B1.items():
        rows.append("<tr><td class='l'>%s</td><td>%.1f</td><td>0</td><td>0</td><td>0</td><td>%d</td><td>未达到</td></tr>" % (k, v["smax"], v["n150"]))
    t1 = gtable(["模式", "滑动平均最大值", "H_mid", "H_heavy", "H_severe", "N_short", "达到的预警级别"], rows)
    amax = max(r["aqi"] for m in A1D.values() if m["days"][0]["conc"]["PM25"] >= 0 for r in m["days"][:7])
    t2 = gtable(["级别", "预案要求", "样例预报", "是否满足"], [
        "<tr><td class='l'>黄色</td><td class='l'>AQI 大于 200 持续 24 小时，或大于 150 持续 36 小时</td><td>各模式日 AQI 最高 %d</td><td>否</td></tr>" % amax,
        "<tr><td class='l'>橙色</td><td class='l'>AQI 大于 200 持续 36 小时，或大于 150 持续 48 小时</td><td>同上</td><td>否</td></tr>",
        "<tr><td class='l'>红色</td><td class='l'>AQI 大于 200 持续 48 小时，且大于 300 持续 24 小时</td><td>同上</td><td>否</td></tr>"])
    return t1, t2

ILLU_DAYS = ["11/13", "11/14", "11/15", "11/16", "11/17", "11/18", "11/19"]
def a2_table():
    data = [("高压后部", "偏南 1.6", "78", "420", "0", "较差", "bad"), ("均压场", "东南 1.3", "82", "350", "0", "较差（持续转差）", "bad"),
            ("高空槽过境", "西北 2.4", "75", "600", "3.2", "一般", ""), ("冷空气过境", "西北 3.8", "52", "1100", "0", "较好（转折）", "good"),
            ("高压前部", "西北 3.2", "45", "1250", "0", "较好", "good"), ("高压控制", "偏北 2.6", "48", "980", "0", "一般", ""), ("弱冷空气补充", "西北 3.4", "44", "1150", "0", "较好", "good")]
    rows = ["<tr><td class='l'>%s</td><td class='l'>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class='l'><span class='%s'>%s</span></td></tr>" % ((ILLU_DAYS[i],) + r[:5] + (r[6], r[5])) for i, r in enumerate(data)]
    return gtable(["日期", "主导系统", "地面风（m/s）", "相对湿度（%）", "边界层高度（m）", "降水（mm）", "扩散条件"], rows)
def a2_maps():
    rows = [("500hPa 高度场 + 850hPa 风场", "槽脊位置和移动；850hPa 的风向", "处于脊前或平直西风、850hPa 偏南风", "高空槽过境、槽后西北气流"),
            ("地面气压场 + 风场", "高低压位置、等压线疏密", "高压后部、均压场，等压线稀疏", "冷高压前部，等压线密集"),
            ("24 小时变温", "冷暖平流", "持续正变温", "明显负变温，冷空气到达"),
            ("相对湿度 + 风场", "高湿区范围、辐合线", "湿度高于 70% 的区域覆盖本地，风场辐合", "湿度下降，风向一致且风速大")]
    return gtable(["图", "看什么", "不利信号", "有利信号"], ["<tr>" + "".join("<td class='l' style='white-space:normal'>%s</td>" % c for c in r) + "</tr>" for r in rows])
def a3_total():
    reg = [("关中", [("西安市", ["中", "中-重", "轻-中", "良", "良", "良", "良"], [(150,180),(185,215),(130,160),(70,100),(65,95),(70,100),(75,105)]),
                    ("咸阳市", ["中", "中-重", "轻-中", "良", "良", "良", "良"], [(155,185),(190,220),(135,165),(70,100),(65,95),(70,100),(70,100)]),
                    ("渭南市", ["中", "中-重", "中", "良-轻", "良", "良", "良"], [(160,190),(195,225),(150,180),(85,115),(65,95),(70,100),(70,100)]),
                    ("宝鸡市", ["轻", "轻-中", "轻", "良", "良", "良", "良"], [(110,140),(135,165),(105,135),(60,90),(55,85),(60,90),(60,90)]),
                    ("铜川市", ["轻", "轻-中", "轻", "良", "良", "良", "良"], [(105,135),(130,160),(100,130),(60,90),(55,85),(55,85),(60,90)])]),
           ("陕北", [("延安市", ["良-轻", "良-轻", "良", "良", "优-良", "良", "良"], [(85,115),(90,120),(65,95),(55,85),(40,70),(50,80),(55,85)]),
                    ("榆林市", ["良", "良-轻", "良", "良", "优-良", "良", "良"], [(70,100),(85,115),(60,90),(50,80),(35,65),(50,80),(50,80)])]),
           ("陕南", [("汉中市", ["良-轻", "良-轻", "良", "良", "良", "良", "良"], [(85,115),(90,120),(70,100),(55,85),(55,85),(55,85),(60,90)]),
                    ("安康市", ["良", "良-轻", "良", "良", "良", "良", "良"], [(70,100),(85,115),(65,95),(55,85),(50,80),(55,85),(55,85)]),
                    ("商洛市", ["良", "良", "良", "良", "优-良", "良", "良"], [(65,95),(70,100),(60,90),(50,80),(40,70),(50,80),(50,80)])])]
    rows = []
    for g, cs in reg:
        for i, (c, ls, rs) in enumerate(cs):
            star = c in ("西安市", "咸阳市", "渭南市")
            rows.append("<tr>" + ("<td class='l' rowspan='%d'>%s</td>" % (len(cs), g) if i == 0 else "") + "<td class='l'%s>%s</td>" % (" style='font-weight:700'" if star else "", c + ("　重点" if star else "")) +
                        "".join(lvtd("%s<small>%d-%d</small>" % (l, r[0], r[1]), l, "c") for l, r in zip(ls, rs)) + "</tr>")
    return gtable(["区域", "城市"] + ILLU_DAYS, rows)
def a3_list():
    rows = [("西安市", "13 至 15 日", "规则一、三", "14 日范围 185 至 215，上限超过重度污染线"), ("咸阳市", "13 至 15 日", "规则一、三", "14 日范围 190 至 220"), ("渭南市", "13 至 15 日", "规则一、三", "14 日范围 195 至 225，回落最慢")]
    return gtable(["城市", "关注日期", "命中规则", "理由"], ["<tr>" + "".join("<td class='l'>%s</td>" % c for c in r) + "</tr>" for r in rows])
def b3_table():
    rows = [("实况是否低于启动标准", "近 24 小时 PM2.5 平均 128", "否，仍为中度污染", "bad"), ("预报何时回落", "各模式滑动平均降到 115 以下的时间：16 日上午至午后", "最早 16 日上午", ""),
            ("回落后能否保持 36 小时", "回落后 36 小时内各模式均未再高于 115", "能", "good"), ("后面有无第二波", "7 天内无新过程", "无", "good")]
    return gtable(["检查项", "数据", "结论"], ["<tr><td class='l'>%s</td><td class='l' style='white-space:normal'>%s</td><td class='l'><span class='%s'>%s</span></td></tr>" % (r[0], r[1], r[3], r[2]) for r in rows])
def c1_tables():
    d = [("11/13", "85-115", 104, "准确", 0, 98), ("11/14", "95-125", 168, "偏低", 43, 118), ("11/15", "110-140", 131, "准确", 0, 126)]
    t1 = gtable(["日期", "人工预报", "实况 AQI", "实况级别", "判定", "偏差", "模式中位数"], [
        "<tr><td class='l'>%s</td><td>%s</td><td>%d</td>%s<td class='l'><span class='%s'>%s</span></td><td>%s</td><td>%d</td></tr>" % (r[0], r[1], r[2], lvtd(lv(r[2])[2], lv(r[2])[2]), "bad" if r[3] != "准确" else "", r[3], ("+%d" % r[4]) if r[4] else "—", r[5]) for r in d])
    m = [("地面风速（m/s）", "2.8", "1.4", "风速报大"), ("相对湿度（%）", "62", "81", "湿度报低"), ("降水（mm）", "2.0", "0.0", "降水报空"), ("边界层高度（m）", "650", "380", "边界层报高")]
    t2 = gtable(["11/14 气象要素", "预报", "实况", "标注"], ["<tr><td class='l'>%s</td><td>%s</td><td>%s</td><td class='l'><span class='bad'>%s</span></td></tr>" % r for r in m])
    c = [("气象预报偏差", "是", "风速、湿度、降水、边界层四项均偏向有利"), ("排放异常", "无法判断", "需人工补充当日管控和焚烧信息"), ("区域传输", "无法判断", "需查看上游城市实况和后向轨迹"),
         ("模式系统性偏差", "否", "13、15 日模式中位数与实况接近"), ("人工订正偏差", "否", "模式中位数 118，与人工预报同样偏低")]
    t3 = gtable(["原因类别", "是否", "证据"], ["<tr>" + "".join("<td class='l' style='white-space:normal'>%s</td>" % x for x in r) + "</tr>" for r in c])
    return t1, t2, t3
def c2_table():
    d = [("集合预报 OEF", 15, "+34%", "28.6", "0.71", "67%"), ("循环网络 RNN", 15, "−21%", "22.4", "0.68", "73%"), ("神经网络 DNN", 15, "+4%", "14.9", "0.82", "87%"), ("S2S", 15, "−9%", "19.3", "0.74", "80%"), ("XAIR", 15, "+12%", "21.7", "0.77", "80%")]
    return gtable(["模式", "样本天数", "PM2.5 NMB", "AQI RMSE", "AQI 相关系数", "AQI 级别命中率"], [
        "<tr><td class='l'%s>%s</td><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td%s>%s</td></tr>" % (" style='font-weight:700'" if "DNN" in r[0] else "", r[0] + ("　推荐" if "DNN" in r[0] else ""), r[1], r[2], r[3], r[4], " style='font-weight:700'" if "DNN" in r[0] else "", r[5]) for r in d])
def c3_table():
    d = [("24 小时", 31, "90%", "77%", "85%", "3%", "7%"), ("48 小时", 31, "87%", "71%", "82%", "3%", "10%"), ("72 小时", 31, "84%", "65%", "79%", "6%", "10%"), ("污染时段（24 小时）", 7, "71%", "57%", "86%", "0%", "29%")]
    return gtable(["时效", "样本数", "级别准确率", "AQI 范围准确率", "首要污染物准确率", "偏高率", "偏低率"], ["<tr><td class='l'>%s</td><td>%d</td>" % r[:2] + "".join("<td>%s</td>" % x for x in r[2:]) + "</tr>" for r in d])

B4S = json.load(open(S("sample_b4.json"), encoding="utf-8"))
def a2_nodes():
    d = [("起始", "高压后部、均压场", "11/13 夜间", "—", "污染开始累积", "稳定（3 次起报一致）", ""),
         ("弱降水", "高空槽过境", "11/15 午后", "3 至 5 毫米", "关中西部略有缓解，东部效果有限", "不稳定（雨量两次调小）", "bad"),
         ("结束", "冷空气过境", "11/16 上午", "转西北风 3 至 4 m/s", "全省清除至良", "较稳定（前后差半天）", "good")]
    return gtable(["节点", "天气系统", "时间", "强度", "预计清除效果", "预报稳定性"], ["<tr>" + "".join("<td class='l' style='white-space:normal'>%s</td>" % x for x in r[:5]) + "<td class='l'><span class='%s'>%s</span></td></tr>" % (r[6], r[5]) for r in d])
def a2_local():
    d = [("地形", "关中为东西走向的渭河谷地，南依秦岭，北接黄土高原", "通用地理特征"),
         ("偏东风", "汾渭平原的污染向关中汇聚", "总站交流材料"),
         ("偏西风", "关中污染向河南东部、山西南部输送", "总站交流材料"),
         ("边界层", "秋冬季典型污染过程边界层高度一般在 800 至 900 米以下", "总站交流材料"),
         ("多大风速起作用", "待本地统计：过程结束时的地面风速和风向", "待补"),
         ("早晚湿度与雾", "待本地统计：秋冬季夜间相对湿度、雾日频率", "待补"),
         ("山谷风", "待本地统计：秦岭北麓山谷风的日变化", "待补"),
         ("沙尘", "待本地统计：春季沙尘路径与频次", "待补")]
    return gtable(["要素", "本地特点", "来源"], ["<tr><td class='l'>%s</td><td class='l' style='white-space:normal'>%s</td><td class='l'>%s</td></tr>" % (a, b if c != "待补" else "<span class='note'>%s</span>" % b, c) for a, b, c in d])
def a4_back():
    d = [("时段", "11 月 1 日至 30 日，共 30 天"), ("已过", "12 天，均值 88，合计 1056"), ("去年同期已过均值", "79（同比上升 12%）"), ("目标值", "70"),
         ("剩余日均上限", "<b>58</b>"), ("预测剩余均值", "82（偏好 70，偏差 94）"), ("时段均值预估", "偏好 77，中性 84，偏差 92"), ("判断", "<span class='bad'>完成难度大</span>")]
    return gtable(["项目", "数值"], ["<tr><td class='l'>%s</td><td class='l'>%s</td></tr>" % r for r in d])
def a4_band():
    d = [("11/13–11/15", "10 天内", "中至重度污染过程", "中", "bad"), ("11/16–11/22", "10 天内", "以良为主", "良", ""), ("11/23–12/02", "11 至 20 天", "可能出现一次过程", "轻-中", "bad"), ("12/03–12/17", "20 天以上", "总体略差于去年同期", "—", "")]
    return gtable(["时段", "时效", "展望", "倾向级别"], ["<tr><td class='l'>%s</td><td class='l'>%s</td><td class='l'><span class='%s'>%s</span></td>%s</tr>" % (r[0], r[1], r[4], r[2], lvtd(r[3], r[3]) if r[3] != "—" else "<td>—</td>") for r in d])
def b4_src():
    rows = ["<tr><td class='l'>%s</td><td>%.1f%%</td></tr>" % (n, v) for n, v in B4S["regions"]]
    t1 = gtable(["来源地区（前 8）", "占比"], rows)
    seg = "<div class='segbar'><i style='width:%.1f%%;background:var(--ink)'></i><i style='width:%.1f%%;background:var(--accent)'></i><i style='width:%.1f%%;background:var(--line2)'></i></div><div class='legend'><span><i class='sw' style='background:var(--ink)'></i>本地 %.1f%%</span><span><i class='sw' style='background:var(--accent)'></i>省内其他城市 %.1f%%</span><span><i class='sw' style='background:var(--line2)'></i>外省及其他 %.1f%%</span></div>" % (
        B4S["local"], 100 - B4S["local"] - B4S["outside"], B4S["outside"], B4S["local"], 100 - B4S["local"] - B4S["outside"], B4S["outside"])
    return seg + t1
def b4_cities():
    rows = ["<tr><td class='l'>%s</td><td>%.1f</td><td>%.1f%%</td><td>%.1f%%</td><td>%.1f%%</td></tr>" % (n, t, l, 100 - l - o, o) for n, t, l, o in B4S["cities"]]
    return gtable(["城市", "模拟 PM2.5", "本地", "省内其他", "外省及其他"], rows)
def b4_traj():
    dirs = ["北", "北东北", "东北", "东东北", "东", "东东南", "东南", "南东南", "南", "南西南", "西南", "西西南", "西", "西西北", "西北", "北西北"]
    rows = ["<tr><td class='l'>后向 %d 小时</td><td>%.2f°N, %.2f°E</td><td>%s</td><td>%d km</td></tr>" % (h, la, lo, dirs[int((b + 11.25) % 360 // 22.5)], km) for h, la, lo, km, b in B4S["traj"]["h"]]
    return gtable(["时刻", "位置", "相对起点方向", "距离"], rows)
t_b2a, t_b2b = b2_tables(); t_c1a, t_c1b, t_c1c = c1_tables()
ILLU = "本表为版式示意，数值不是实际预报或实况。"
FIGS = {
 "A2": [fig("图表一　关键节点表", "每个节点：什么时间、多强、能清除到哪里", "交付件", a2_nodes(), ILLU, out=True, demo=True),
        fig("图表二　形势图读图要点", "四张图各看什么", "自用", a2_maps(), "形势图由系统直接出图，本卡不重画。每页图下配两到三条按时段写的结论。"),
        fig("图表三　扩散条件逐日判定表", "每天一行，结论给 A1 用", "交付件", a2_table(), ILLU, out=True, demo=True),
        fig("图表四　本地气象特征表（关中）", "汇报气象时突出本地特点", "自用", a2_local(), "标“待补”的项目需用本地历史资料统计后填写。")],
 "A4": [fig("图表一　目标倒推表", "领导最关心的一个数：剩余日均上限", "交付件", a4_back(), ILLU, out=True, demo=True),
        fig("图表二　分段展望", "时效越长，说得越粗", "交付件", a4_band(), ILLU, out=True, demo=True)],
 "B4": [fig("图表一　西安市 PM2.5 来源构成", "本地、省内其他、外省三段", "交付件", b4_src(), "真实样例数据：源解析（OSAM）起报 2026-10-21 16 时，近地面层。该时段为清洁时段（模拟 PM2.5 为 %.1f μg/m³），比例不代表污染过程。“陆地其他地区+海洋”主要反映模拟边界的影响。" % B4S["tot"], out=True),
        fig("图表二　陕西各市本地与外来贡献", "同一时刻各市对比", "自用", b4_cities(), "真实样例数据，同上。咸阳、渭南在源解析中按区县组合统计。"),
        fig("图表三　后向轨迹摘要", "看气团从哪里来", "自用", b4_traj(), "真实样例数据：起点 %.2f°N、%.2f°E，高度 500 米，2026-10-28 15 时起向后追踪。" % tuple(B4S["traj"]["start"]))],
 "A3": [fig("图表一　城市 × 日期等级总表", "分区排列，城市顺序固定", "交付件", a3_total(), ILLU + "格内上方是级别，下方是 AQI 范围。", out=True, demo=True),
        fig("图表二　重点城市名单", "不超过 5 个，每个一句理由", "交付件", a3_list(), ILLU, out=True, demo=True)],
 "B1": [fig("图表一　各模式 PM2.5 逐小时预报曲线", "看起落是否同步，峰值在哪", "自用", b1_curve(), "真实样例数据：站点 659004109、659004111，起报 2026-10-21 12 时，未来 7 天。蓝线为小时峰值最高的模式，灰线为其余模式。"),
        fig("图表二　过程要素表", "各模式一行", "交付件", b1_table(), "真实样例数据。样例期间没有污染过程，所以“污染过程”一列均为未识别。有过程时，该列展开为起始、结束和持续小时数。", out=True)],
 "B2": [fig("图表一　省级启动条件对照表", "按 PM2.5 滑动平均浓度判定", "交付件", t_b2a, "真实样例数据。H_mid、H_heavy、H_severe 分别是滑动平均连续处于中度、重度、严重及以上的最长小时数；N_short 是小时浓度高于 150 的小时数。", out=True),
        fig("图表二　地市级启动条件对照表", "按 AQI 判定", "交付件", t_b2b, "真实样例数据。正式使用时“样例预报”一列填 AQI 大于 150、200、300 的连续小时数。", out=True)],
 "B3": [fig("图表一　解除条件对照表", "四项都通过才建议解除", "交付件", b3_table(), ILLU, out=True, demo=True)],
 "C1": [fig("图表一　预报与实况对比表", "先定性：准确、偏高还是偏低", "交付件", t_c1a, ILLU, out=True, demo=True),
        fig("图表二　气象要素偏差表", "只列出现偏差的那一天", "自用", t_c1b, ILLU, demo=True),
        fig("图表三　归因清单", "五类原因逐项排查", "交付件", t_c1c, ILLU, out=True, demo=True)],
 "C2": [fig("图表一　模式评估指标表", "近 15 天，提前 24 小时预报", "交付件", c2_table(), ILLU + "正式使用时 PM2.5、O3、AQI 各出一张。", out=True, demo=True)],
 "C3": [fig("图表一　准确率统计表", "分时效，污染时段单列", "交付件", c3_table(), ILLU, out=True, demo=True)],
}

# ---------- A1：沿用样板卡 ----------
LEG = open(S("a1_legacy.html"), encoding="utf-8").read()
A1_SECTIONS = re.findall(r'<section id="step-\d">.*?</section>', LEG, flags=re.S)
assert len(A1_SECTIONS) == 5
A1_SECTIONS = [re.sub(r'<section id="step-(\d)">', r'<section class="step">', s) for s in A1_SECTIONS]
A1_SCRIPT = re.search(r"<script>\n(const DATA=.*?)</script>", LEG, flags=re.S).group(1)
LEG_CSS = re.search(r"<style>(.*?)</style>", LEG, flags=re.S).group(1)
A1_PROMPT = html.unescape(re.search(r'<pre id="prompt">(.*?)</pre>', LEG, flags=re.S).group(1))
A1_CHECKS = [re.sub(r"<.*?>", "", x) for x in re.findall(r"<li>(.*?)</li>", re.search(r'<ul class="check">(.*?)</ul>', LEG, flags=re.S).group(1), flags=re.S)]
CARDS["A1"]["prompt"] = A1_PROMPT; CARDS["A1"]["checks"] = A1_CHECKS
A1_SECTIONS[4] = A1_SECTIONS[4].replace('<div><i>④</i><b>首要污染物</b>每段结尾固定一句。</div>', '<div><i>④</i><b>首要污染物</b>每段结尾固定一句。</div><div><i>⑤</i><b>管理含义</b>结论之后补一句：持续时间长对应预警提前量，传输明显对应联动范围，见卡 B2、B4。</div>', 1)
A1_SECTIONS[4] = A1_SECTIONS[4].replace('<h3>结论页：地市级范例</h3>', '<div class="say"><span class="lab">管理含义（示例文字，接在结论之后）</span><p>本轮过程持续约 2 天，建议提前 48 小时研判预警（卡 B2）；前期偏东风，汾渭平原污染向关中汇聚，建议与渭南、山西南部同步沟通（卡 B4）。剩余时段完成月度目标的压力见卡 A4。</p></div><h3>结论页：地市级范例</h3>', 1)
assert '⑤' in A1_SECTIONS[4] and '管理含义（示例文字' in A1_SECTIONS[4]
A1_NOTICE = re.search(r'<div class="notice">.*?</div>', LEG, flags=re.S).group(0)

# ---------- 页面部件 ----------
def sec(n, title, q, inner):
    return "<section class='step'><div class='sh'><span class='no'>0%d</span><h2>%s</h2><span class='q'>%s</span></div><div class='sb'>%s</div></section>" % (n, title, q, inner)
ul = lambda xs, cls="": "<ul%s>%s</ul>" % (" class='%s'" % cls if cls else "", "".join("<li>%s</li>" % x for x in xs))
def card_body(cid, c):
    if cid == "A1": return A1_NOTICE + "".join(A1_SECTIONS)
    s1 = "<div class='two'><div class='box'><h4>领导可能这样说</h4>%s</div><div class='box'><h4>他真正要的</h4>%s</div></div><h3>您要交出的东西</h3><div class='three'>%s</div>" % (
        ul(c["says"]), ul(c["wants"]), "".join("<div class='box'><h4>%s</h4><div class='big'>%s</div><span class='note'>%s</span></div>" % d for d in c["deliverables"]))
    rows = "".join("<tr><td>%s<br><span class='note'>%s</span></td><td>%s</td><td><span class='pill %s'>%s</span></td><td>%s</td></tr>" % (n, sub, use, "must" if must else "opt", "必选" if must else "佐证", have) for n, sub, use, must, have in c["data"])
    s2 = "<div class='scroll'><table class='t'><tr><th>数据</th><th>用来做什么</th><th>必选</th><th>您是否具备</th></tr>%s</table></div><h3>交给 AI 的标准数据包</h3>%s" % (rows, c["pack"])
    s3 = "".join(FIGS[cid]) + "<h3>画法与判定规范</h3><div class='rules'>%s</div><h3>常见错误</h3>%s" % ("".join("<div class='rule'><b>%s</b>%s</div>" % r for r in c["rules"]), ul(c["mistakes"]))
    s4 = "<pre id='prompt-%s'>%s</pre><div class='bar'><button class='copy' type='button' data-for='prompt-%s'>复制提示词</button><span class='note'>提示词不依赖任何特定模型，判定条件已写在里面。</span></div><h3>AI 应当给出的结果</h3><div class='say'>%s</div><h3>必须人工复核的事项</h3>%s" % (
        cid, E(c["prompt"]), cid, c["expect"], ul(c["checks"], "check"))
    qa = "".join("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % r for r in c["qa"])
    s5 = "<h3>省级范例</h3><div class='say'><span class='lab'>示例文字，非实际预报</span>%s</div><h3>地市级范例</h3><div class='say'><span class='lab'>示例文字，非实际预报</span>%s</div><h3>领导常见追问</h3><div class='scroll'><table class='t'><tr><th>追问</th><th>怎么答</th><th>依据</th></tr>%s</table></div>" % (c["say_prov"], c["say_city"], qa)
    note = "<div class='notice'><b>初稿说明</b>本卡内容为初稿，尚未经预报业务专家审核。标有“示意数据”的图表只演示版式；标有“真实样例数据”的图表由标准数据集计算，但站点不是西安。</div>"
    return note + sec(1, "指令与意图", "领导到底要什么", s1) + sec(2, "必用数据", "先看有没有，再决定能做到哪一步", s2) + sec(3, "标准图表", "按规范出图出表", s3) + sec(4, "AI 研判", "把数据包和下面这段话一起交给任意一个大模型", s4) + sec(5, "交付话术", "怎么向领导交差", s5)

STEPS = ["指令与意图", "必用数据", "标准图表", "AI 研判", "交付话术"]
GN = dict(GROUPS)
def card_page(cid, c):
    tags = "".join("<span class='tag'>%s</span>" % t for t in [GN[c["group"]], c["level"], "业务人员与驻场人员", "HJ 633—2026"])
    seg = "".join("<button type='button' class='segb' data-step='%d'><span class='mono'>%d</span>%s</button>" % (i, i + 1, t) for i, t in enumerate(STEPS))
    return "<article class='route card' data-route='%s'><div class='crumb'><a href='#home'>指令卡</a>　/　%s　/　<span>%s</span></div><div class='chead'><div class='tags'><span class='code'>%s</span>%s<span class='st %s'>%s</span></div><h1>“%s”</h1><p class='lead'>%s</p></div><nav class='seg' aria-label='步骤'>%s</nav>%s<p class='foot'>内部对照：%s　技能文件：<a href='skills/%s.md'>skills/%s.md</a></p></article>" % (
        cid.lower(), GN[c["group"]], cid, cid, tags, "on" if c["status"] == "可试用" else "", c["status"], c["q"], c["lead"], seg, card_body(cid, c), c["internal"], cid, cid)

def qpanel():
    li = "".join("<li>%s%s</li>" % (q, "".join("<a class='code' href='#%s'>%s</a>" % (c.lower(), c) for c in cs)) for q, cs in QUESTIONS)
    return "<section class='qs'><h2>未来 10 天，领导最常问的 8 个问题</h2><ol>%s</ol><p class='note'>问题清单依据%s整理。</p></section>" % (li, SRC_FW)
def home():
    def card(cid, c):
        on = c["status"] == "可试用"
        return "<a class='cardlink' href='#%s' data-text='%s'><div class='crow'><span class='code'>%s</span><span class='st %s'>%s</span></div><div class='cq'>“%s”</div><div class='cm'><span>交付：%s</span><span class='lvl'>%s</span></div></a>" % (
            cid.lower(), E(cid + c["q"] + c["deliver"] + "".join(c["data_use"]) + "".join(c["chart_use"])), cid, "on" if on else "", c["status"], c["q"], c["deliver"], c["level"])
    groups = ""
    for g, name in GROUPS:
        ids = [k for k in CARDS if CARDS[k]["group"] == g]
        groups += "<section class='grp'><div class='gh'><h2>%s</h2><span class='mono'>%s–%s</span></div><div class='cards'>%s</div></section>" % (name, ids[0], ids[-1], "".join(card(k, CARDS[k]) for k in ids))
    quick = "".join("<a class='quick' href='#%s'><b>%s</b><span>%s</span></a>" % q for q in [("home", "按领导指令", "9 条原话"), ("by-data", "按数据", "预报、实况、气象"), ("by-chart", "按图表", "矩阵、刷色表、曲线"), ("standards", "标准与规范", "HJ 633—2026 等")])
    # A1 样例产出
    vn = [k for k, v in A1D.items() if v["days"][0]["conc"]["PM25"] >= 0]
    mini = ""
    for i in range(7):
        vals = sorted(A1D[k]["days"][i]["aqi"] for k in vn); med = vals[len(vals) // 2]
        lo, hi = max(0, med - 10), med + 10; a, b = lv(lo), lv(hi)
        mini += "<div class='mc'><span class='mono'>%s</span><span class='chipl' style='background:%s;color:%s'>%s</span><span class='mono'>%d-%d</span></div>" % (daylab(DAY0[i]["d"]), b[3], b[4], a[2] if a is b else a[2] + "-" + b[2], lo, hi)
    n_on = sum(1 for c in CARDS.values() if c["status"] == "可试用")
    return "<article class='route' data-route='home'><div class='hero'><div class='hl'><h1>接到领导指令，<br>先找对应的卡</h1><p class='lead'>每张卡写明用什么数据、出什么图表、怎么让 AI 起草研判、怎么向领导交差。专职、兼职和驻场人员按同一套标准做。</p><div class='quicks'>%s</div><div class='prog'><div><span>一期进度</span><b>%d 张可试用，%d 张初稿</b></div><div class='bar2'><i style='width:%d%%'></i></div></div></div><div class='panel'><div class='crow'><span class='code'>A1</span><b>样板卡产出示例</b><span class='lvl'>样例数据，非西安</span></div><div class='note'>未来七日预报结论表（各模式中位数上下各 10）</div><div class='mini'>%s</div><div class='inset'>分时段结论由 AI 按级别合并起草，扩散条件一句留给预报员补写。</div><a class='btn' href='#a1'>打开 A1 卡</a></div></div>%s<div id='nores' class='notice' hidden><b>没有找到对应的卡</b>换一个说法试试，或者按数据、按图表查找。</div>%s</article>" % (
        quick, n_on, len(CARDS) - n_on, round(100 * n_on / len(CARDS)), mini, qpanel(), groups)

DATA_DESC = {"多模式空气质量预报": "各模式逐小时、逐日的六项污染物预报，统计、集合与数值模式", "空气质量实况": "站点和城市的小时、日均浓度及 AQI", "气象实况": "自动气象站的风、温、湿、降水",
             "气象形势预报": "高空与地面形势专题图、变温、湿度风场", "污染气象诊断指数": "边界层高度、通风、静稳等指数", "沙尘预报": "含沙尘的颗粒物浓度预报", "模式评估结果": "各模式近期的偏差与命中率",
             "各市上报的预报": "各市预报员每日上报的结论", "重污染天气应急预案": "本地现行预案的预警分级与启动、解除条件", "历史预报存档": "当时发布的人工预报与各模式结果", "气象预报存档": "当时的气象要素预报值", "延伸期预报": "未来 15 至 45 天的空气质量与气象预报", "天气分型": "逐日天气型及历史同期频率",
             "历史同期实况": "往年同一时段的逐日浓度", "源解析": "各城市污染物按来源地区和行业的贡献", "气团轨迹": "后向、前向轨迹与聚类"}
def index_page(route, title, lead, key, desc=None):
    m = {}
    for cid, c in CARDS.items():
        for x in c[key]: m.setdefault(x, []).append(cid)
    rows = "".join("<tr><td>%s%s</td><td>%s</td></tr>" % (k, "<br><span class='note'>%s</span>" % desc.get(k, "") if desc else "", " ".join("<a class='code' href='#%s'>%s</a>" % (i.lower(), i) for i in v)) for k, v in sorted(m.items(), key=lambda kv: -len(kv[1])))
    return "<article class='route' data-route='%s'><div class='chead'><h1>%s</h1><p class='lead'>%s</p></div><section class='plain'><div class='scroll'><table class='t'><tr><th>%s</th><th>用到它的卡</th></tr>%s</table></div></section></article>" % (route, title, lead, "数据" if desc else "图表", rows)

def standards():
    lvrows = "".join("<tr><td class='l'>%s</td><td>%d–%d</td>%s<td>%s</td></tr>" % (l[1], (LV[i - 1][0] + 1) if i else 0, l[0], lvtd(l[2], l[2]), l[3][4:-1]) for i, l in enumerate(LV))
    bp = [("PM2.5（24 小时）", "0/35/60/115/150/250/350/500"), ("PM10（24 小时）", "0/50/120/250/350/420/500/600"), ("SO2（24 小时）", "0/50/150/475/800/1600/2100/2620"), ("NO2（24 小时）", "0/40/80/180/280/565/750/940"), ("CO（24 小时，mg/m³）", "0/2/4/14/24/36/48/60"), ("O3（8 小时滑动平均）", "0/100/160/215/265/800")]
    bprows = "".join("<tr><td class='l'>%s</td>%s</tr>" % (n, "".join("<td>%s</td>" % x for x in (v.split("/") + ["—"] * 8)[:8])) for n, v in bp)
    docs = [("环境空气质量标准", "GB 3095—2026", "浓度限值"), ("环境空气质量指数（AQI）技术规定", "HJ 633—2026", "分指数限值、级别与颜色，本站图表的依据"), ("环境空气质量评价技术规范", "HJ 663—2026", "评价方法"),
            ("数值修约规则与极限数值的表示和判定", "GB/T 8170—2008", "四舍六入五成双"), ("城市环境空气质量指数（AQI）预报评估技术规定（暂行）", "总站预报字〔2020〕549 号", "预报准确率评估，卡 C3"),
            ("全国环境空气质量预报效果评估工作方案（试行）", "总站预报字〔2024〕73 号", "预报效果评估，卡 C3"), ("陕西省重污染天气应急预案（2023年修订）", "征求意见稿", "省级预警条件，卡 B2、B3；正式稿为陕政办函〔2023〕183 号，文本未取得"),
            ("灞桥区重污染天气应急预案（2024年修订）", "灞政办发〔2024〕37 号", "地市级预警条件的暂用依据；西安市预案正文未取得")]
    drows = "".join("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % d for d in docs)
    return "<article class='route' data-route='standards'><div class='chead'><h1>标准与规范</h1><p class='lead'>全站图表和判定所依据的文件，以及最常用的两张表。</p></div><section class='plain'><h3>AQI 级别与颜色（HJ 633—2026）</h3><div class='scroll'><table class='g'><tr><th>级别</th><th>AQI</th><th>简写与色块</th><th>RGB</th></tr>%s</table></div><h3>分指数对应的浓度限值（HJ 633—2026 表 3）</h3><div class='scroll'><table class='g'><tr><th>污染物</th><th>0</th><th>50</th><th>100</th><th>150</th><th>200</th><th>300</th><th>400</th><th>500</th></tr>%s</table></div><p class='note'>单位除 CO 外均为 μg/m³。浓度先按“四舍六入五成双”修约，分指数和 AQI 向上进位取整；AQI 大于 50 时才有首要污染物。O3 的 8 小时浓度高于 800 时不再计算分指数。</p><h3>依据文件</h3><div class='scroll'><table class='t'><tr><th>文件</th><th>文号</th><th>在本站的用途</th></tr>%s</table></div><div class='notice'><b>预警依据的局限</b>省级条件摘自征求意见稿，地市级条件摘自区级下位预案，都不是使用单位的正式文本。使用预警类卡片前，请以本单位持有的现行预案核对启动和解除条件。</div></section></article>" % (lvrows, bprows, drows)

CSS_NEW = """
:root:root:root{color-scheme:light;--bg:#F6F6F7;--surface:#fff;--sunk:#F6F6F7;--ink:#222;--ink2:#444;--ink3:#6B7280;--line:#E5E7EB;--line2:#D5D9DE;--accent:#1F5FD1;--accent-ink:#fff;--accent-soft:#EAF1FD;--good:#0a7d3c;--bad:#c2271d;--warn-bg:#FFF8E1;--warn-line:#E0A800;--shadow:none;
--font:"Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif;--display:var(--font);--mono:"JetBrains Mono","SF Mono",Menlo,Consolas,monospace}
body{font-size:14px;line-height:1.7}
.mono{font-family:var(--mono)}
.ann{background:var(--surface);border-bottom:1px solid var(--line);text-align:center;font-size:12px;color:var(--ink2);padding:6px 16px}
.top{background:var(--surface);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
header.top{padding:0}
.top>div{max-width:1200px;margin:0 auto;padding:8px 24px;min-height:56px;display:flex;flex-wrap:wrap;align-items:center;gap:8px 16px;box-sizing:border-box}
.brand{display:flex;align-items:center;gap:8px;text-decoration:none;color:var(--ink);font-weight:700;font-size:15px}
.brand i{font:500 12px var(--mono);font-style:normal;background:var(--ink);color:#fff;border-radius:5px;padding:3px 7px}
.nav{position:static;align-self:auto;display:flex;flex-direction:row;flex-wrap:wrap;gap:4px;margin:0 auto}
.nav a{text-decoration:none;font-size:14px;font-weight:500;padding:6px 12px;border-radius:8px;color:#282B3B}
.nav a:hover{background:var(--sunk)}.nav a.cur{background:var(--ink);color:#fff}
.search{display:flex;align-items:center;gap:8px;border:1px solid var(--line);border-radius:8px;padding:6px 10px;min-width:230px}
.search input{border:0;outline:none;font:inherit;flex:1;background:transparent;color:var(--ink);min-width:0}
.search:focus-within{outline:3px solid var(--warn-line);outline-offset:1px}
main.wrap{max-width:1200px;margin:0 auto;padding:32px 24px 64px;display:block}
.route{display:none;flex-direction:column;gap:24px}.route.show{display:flex}
h1{font:700 40px/1.25 var(--font);margin:0;letter-spacing:0}
.lead{margin:0;font-size:16px;color:var(--ink2);max-width:40em}
.hero{display:flex;flex-wrap:wrap;gap:32px;align-items:stretch;padding:16px 0 8px}
.hl{flex:1 1 520px;min-width:0;display:flex;flex-direction:column;gap:20px}
.quicks{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;max-width:520px}
.quick{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:10px 16px;text-decoration:none;color:var(--ink);display:flex;flex-direction:column}
.quick b{font-weight:500}.quick span{font-size:12px;color:var(--ink3)}
.quick:hover,.cardlink:hover{border-color:#B9C2CC}
.prog{max-width:520px;display:flex;flex-direction:column;gap:6px;font-size:12px;color:var(--ink2)}
.prog>div:first-child{display:flex;justify-content:space-between}.prog b{font-weight:500;color:var(--ink)}
.bar2{height:4px;background:var(--line);border-radius:8px;overflow:hidden}.bar2 i{display:block;height:100%;background:var(--accent)}
.panel{flex:1 1 420px;min-width:0;background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:20px;display:flex;flex-direction:column;gap:12px}
.mini{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:6px;background:var(--sunk);border:1px solid var(--line);border-radius:8px;padding:12px}
.mc{display:flex;flex-direction:column;gap:4px;align-items:center;font-size:11px;color:var(--ink2)}
.chipl{width:100%;text-align:center;border-radius:4px;font-weight:700;font-size:12px;padding:3px 0}
.inset{background:var(--sunk);border:1px solid var(--line);border-radius:8px;padding:10px 14px;font-size:13.5px;color:var(--ink2)}
.btn{align-self:flex-start;font-weight:500;text-decoration:none;border:1px solid var(--line);border-radius:8px;padding:6px 12px;color:#282B3B}.btn:hover{background:var(--sunk)}
.grp{display:flex;flex-direction:column;gap:12px;background:none;border:0;box-shadow:none;overflow:visible;border-radius:0}
.gh{display:flex;align-items:baseline;gap:10px}.gh h2{font:600 18px var(--font);margin:0}.gh .mono{font-size:12px;color:var(--ink3)}
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.cardlink{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:16px;text-decoration:none;color:inherit;display:flex;flex-direction:column;gap:10px}
.crow{display:flex;align-items:center;gap:8px}
.code{font:500 12px var(--mono);color:#282B3B;background:#F0F0F0;border-radius:2px;padding:1px 6px;text-decoration:none}
a.code:hover{background:var(--accent-soft);color:var(--accent)}
.st{margin-left:auto;font-size:12px;font-weight:500;border:1px solid var(--line);border-radius:20px;padding:0 10px;color:var(--ink3)}
.st.on{background:var(--ink);border-color:var(--ink);color:#fff}
.lvl{margin-left:auto;font-size:12px;color:var(--ink3)}
.cq{font-size:16px;font-weight:600;line-height:1.5}
.cm{display:flex;gap:8px;font-size:13px;color:var(--ink2);margin-top:auto}
.crumb{font-size:13px;color:var(--ink3)}.crumb a{color:var(--ink3);text-decoration:none}.crumb span{color:var(--ink)}
.chead{display:flex;flex-direction:column;gap:12px}
.tags{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.tag{font-size:12px;border:1px solid var(--line);border-radius:20px;padding:0 10px;color:var(--ink2);background:var(--surface)}
.tags .st{margin-left:0}
.seg{position:static;align-self:flex-start;display:flex;flex-direction:row;flex-wrap:wrap;gap:2px;background:var(--sunk);border:1px solid var(--line);border-radius:8px;padding:3px}
.segb{font:inherit;font-weight:500;border:1px solid transparent;background:transparent;border-radius:7px;padding:5px 14px;color:var(--ink2);cursor:pointer;display:flex;gap:6px;align-items:center}
.segb .mono{font-size:12px;color:var(--ink3)}
.segb:hover,.segb.cur{background:var(--surface);border-color:var(--line);color:var(--ink)}
section{border-radius:8px}
section.plain{padding:20px 24px;display:flex;flex-direction:column;gap:14px}
.sh{background:var(--surface);padding:16px 24px 12px}
.sh .no{border:0;background:#F0F0F0;color:#282B3B;border-radius:2px;padding:3px 6px;top:-2px}
h2{font:600 20px/1.3 var(--font)}
.sb{padding:20px 24px 24px}
.box,figure,.rule,.check li,pre,.anat,.slide{border-radius:8px}
.box .big{font:600 16px/1.4 var(--font)}
.pill.must,figure .fh .who.out{background:var(--ink);border-color:var(--ink);color:#fff}
figure .fh .who.demo{margin-left:auto;background:var(--warn-bg);border-color:var(--warn-line);color:#6B4E00}
figure .fh .who.demo+.who{margin-left:0}
button.copy{background:var(--ink);border-radius:8px}
.say{border-left:1px solid var(--line);border-radius:8px}
.notice{border-radius:8px;border-left-width:1px}
table.g td.l{white-space:nowrap}
.anat{grid-template-columns:repeat(5,minmax(0,1fr))}
.segbar{display:flex;height:14px;border-radius:4px;overflow:hidden;gap:2px}.segbar i{display:block}
.qs{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:16px 20px;display:flex;flex-direction:column;gap:6px}
.qs h2{font:600 18px var(--font);margin:0 0 4px}.qs ol{margin:0;padding-left:1.4em;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:4px 32px;max-width:none}.qs li{margin:0}.qs .code{margin-left:6px}
.foot{font-size:12.5px;color:var(--ink3);max-width:none}
footer.site{border-top:1px solid var(--line);background:var(--surface)}footer.site div{max-width:1200px;margin:0 auto;padding:16px 24px;font-size:12px;color:var(--ink3)}
[hidden]{display:none!important}
@media (max-width:900px){.qs ol{grid-template-columns:1fr}.anat{grid-template-columns:1fr 1fr}h1{font-size:28px}.cards{grid-template-columns:1fr}.nav{margin:0;order:3;width:100%}.search{flex:1}main.wrap{padding:20px 16px 48px}.sh,.sb,section.plain{padding-left:16px;padding-right:16px}}
"""
JS = """
const ROUTES=[...document.querySelectorAll('.route')].map(a=>a.dataset.route);
function go(){let r=(location.hash||'#home').slice(1);if(!ROUTES.includes(r))r='home';
  document.querySelectorAll('.route').forEach(a=>a.classList.toggle('show',a.dataset.route===r));
  document.querySelectorAll('.nav a').forEach(a=>{const t=a.getAttribute('href').slice(1);a.classList.toggle('cur',t===r||(t==='home'&&/^[abc][0-9]$/.test(r)));});
  window.scrollTo(0,0);}
window.addEventListener('hashchange',go);go();
document.addEventListener('click',e=>{const b=e.target.closest('.segb');if(b){const art=b.closest('.route');const s=art.querySelectorAll('section.step')[+b.dataset.step];if(s)s.scrollIntoView({behavior:'smooth',block:'start'});art.querySelectorAll('.segb').forEach(x=>x.classList.toggle('cur',x===b));return;}
  const c=e.target.closest('button.copy[data-for]');if(c){const t=document.getElementById(c.dataset.for).textContent;navigator.clipboard.writeText(t).then(()=>{c.textContent='已复制'},()=>{c.textContent='复制失败，请手动选中文本'});}});
const q=document.getElementById('q');q.addEventListener('input',()=>{if((location.hash||'#home')!=='#home')location.hash='#home';const v=q.value.trim().toLowerCase();let n=0;
  document.querySelectorAll('.cardlink').forEach(a=>{const hit=!v||a.dataset.text.toLowerCase().includes(v);a.hidden=!hit;if(hit)n++;});
  document.querySelectorAll('.grp').forEach(g=>{g.hidden=!g.querySelector('.cardlink:not([hidden])');});document.getElementById('nores').hidden=n>0;});
"""

def build():
    arts = home() + "".join(card_page(k, c) for k, c in CARDS.items()) + index_page("by-data", "按数据查", "手里有哪些数据，就能做哪些卡。", "data_use", DATA_DESC) + index_page("by-chart", "按图表查", "需要出某种图表时，看哪张卡有画法规范。", "chart_use") + standards()
    page = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>预报会商指令卡</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>%s%s</style>
</head>
<body>
<div class="ann">一期共 %d 张卡 · 图表标准 HJ 633—2026 · A1 可试用，其余为初稿</div>
<header class="top"><div><a class="brand" href="#home"><i>DEBPG</i>预报会商指令卡</a>
<nav class="nav" aria-label="主导航"><a href="#home">指令卡</a><a href="#by-data">按数据</a><a href="#by-chart">按图表</a><a href="#standards">标准与规范</a></nav>
<label class="search"><span class="note">搜索</span><input id="q" type="search" placeholder="输入领导原话，如“预警”" aria-label="搜索指令卡"></label></div></header>
<main class="wrap">%s</main>
<footer class="site"><div>图表配色依据 HJ 633—2026 附录 A；预警依据各地重污染天气应急预案。AI 技能文件见 skills 目录，站点索引见 llms.txt。</div></footer>
<script>
%s</script>
<script>%s</script>
</body>
</html>
""" % (LEG_CSS, CSS_NEW, len(CARDS), arts, A1_SCRIPT, JS)
    os.makedirs(D("skills"), exist_ok=True)
    open(D("index.html"), "w", encoding="utf-8").write(page)
    for cid, c in CARDS.items():
        md = "# 技能 %s：%s\n\n> 预报会商指令卡 · %s · 适用：%s · 状态：%s\n\n## 何时使用\n\n领导问“%s”或类似的话时使用。最终交付：%s。\n\n## 输入\n\n%s\n\n## 步骤（可直接作为提示词）\n\n```\n%s\n```\n\n## 输出\n\n%s\n\n## 必须人工复核\n\n%s\n\n## 说明\n\n- 本技能不依赖特定大模型，只使用自然语言和固定的输入输出格式。\n- 图表与级别判定依据 HJ 633—2026。\n- AI 的输出是初稿，必须经预报员复核后才能对外使用。\n" % (
            cid, c["q"], GN[c["group"]], c["level"], c["status"], c["q"], c["deliver"], c["skill_in"], c["prompt"], c["skill_out"], "\n".join("- " + re.sub(r"<.*?>", "", x) for x in c["checks"]))
        open(D("skills/%s.md" % cid), "w", encoding="utf-8").write(md)
    ll = "# 预报会商指令卡\n\n> 面向省级和地市级环境空气质量预报业务人员及驻场人员。每张卡对应一条领导指令，写明必用数据、标准图表、AI 研判提示词和交付话术。一期覆盖预报会商主线 %d 张卡。图表标准为 HJ 633—2026。\n\n## 指令卡\n\n%s\n\n## 索引\n\n- [按数据查](index.html#by-data)\n- [按图表查](index.html#by-chart)\n- [标准与规范](index.html#standards)\n\n## 使用须知\n\n- A1 为可试用样板，其余为初稿，尚未经预报业务专家审核。\n- 预警类卡片（B2、B3）的条件摘自征求意见稿和区级下位预案，使用前须以本单位正式预案核对。\n- 技能文件的输出是初稿，须经预报员复核。\n\n## 领导常问的问题\n\n%s\n" % (
        len(CARDS), "\n".join("- [%s %s](index.html#%s)：%s。技能文件：[skills/%s.md](skills/%s.md)" % (k, c["q"], k.lower(), c["deliver"], k, k) for k, c in CARDS.items()), "\n".join("- %s：%s" % (q, "、".join(cs)) for q, cs in QUESTIONS))
    open(D("llms.txt"), "w", encoding="utf-8").write(ll)
    print("built", len(page))
build()
