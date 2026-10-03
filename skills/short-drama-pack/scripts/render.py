#!/usr/bin/env python3
"""把 project.json 渲染成 AI 短剧制作包：独立的 Markdown 文件 + 可复制的 HTML 查看页，并做一致性校验。

用法：
    python3 render.py <project.json> [--out <输出目录>]

输出目录默认是 project.json 所在目录。会生成：
    00_总览.md  01_角色多视图提示词.md  02_道具提示词.md  03_场景提示词.md
    04_场景关联表.md  05_角色音色.md  06_分镜脚本.md  07_后期清单.md  index.html

文本里的 [[ID]] 会被展开：角色资产和场景 → 平台引用「@分组-名称」；道具 → 有 group 时为 @分组-名称，
否则为它的固定外观 desc；音色（voices.characters 里带 id 的）→ 它的短版音色。
{ratio_phrase} 会被替换成 meta.ratio_phrase。
有错误时退出码为 1，并在终端、00_总览.md、index.html 里列出。
"""
import argparse
import html
import json
import os
import re
import sys

REF = re.compile(r'\[\[([A-Za-z0-9_]+)\]\]')
QUOTE = re.compile(r'“(.+?)”', re.S)
KEEP = re.compile(r'[^0-9A-Za-z\u4e00-\u9fff]')
HANZI = re.compile(r'[\u4e00-\u9fff]')
PLACEHOLDER = re.compile(r'\{[^{}\s]{1,20}\}')

DEFAULT_SEGMENT_HEADER = '本片段场景设定在: {scenes}。生成一个由以下{n}个分镜组成的视频。'
DEFAULT_SHOT_LINE = '分镜{i}[时长: {dur}s]: {text}'
SINGLE_LAYOUT = '单人全身正面站立，画面右侧一格为面部特写，纯净浅灰色无缝背景，均匀柔和的影棚平光，无文字标注。'
LAYOUTS = ('多视图', '表情', '单张全身')

FILES = [
    ('00_总览.md', '总览'),
    ('01_角色多视图提示词.md', '角色'),
    ('02_道具提示词.md', '道具'),
    ('03_场景提示词.md', '场景提示词'),
    ('04_场景关联表.md', '场景关联'),
    ('05_角色音色.md', '音色'),
    ('06_分镜脚本.md', '分镜脚本'),
    ('07_后期清单.md', '后期'),
]


# ---------------------------------------------------------------- 工具函数
def cell(s):
    return str(s if s is not None else '').replace('|', '\\|').replace('\n', ' ')


def table(headers, rows):
    out = ['| ' + ' | '.join(cell(h) for h in headers) + ' |',
           '|' + '|'.join('---' for _ in headers) + '|']
    for r in rows:
        r = list(r) + [''] * (len(headers) - len(r))
        out.append('| ' + ' | '.join(cell(c) for c in r) + ' |')
    return '\n'.join(out)


def code(text, lang=''):
    return f'```{lang}\n{(text or "").rstrip()}\n```'


def spoken(text):
    """分镜文本里引号内的台词。"""
    return QUOTE.findall(text or '')


def norm_line(s):
    """核对台词时只看汉字、字母和数字。"""
    return KEEP.sub('', s or '')


def outside_quotes(text):
    return QUOTE.sub('', text or '')


def fill(template, **kw):
    """模板替换：只替换给定的变量，其余花括号原样保留。"""
    for k, v in kw.items():
        template = template.replace('{' + k + '}', str(v))
    return template


class Report:
    def __init__(self):
        self.errors, self.warnings, self.infos = [], [], []
        self._seen = set()

    def _add(self, bucket, m):
        if m not in self._seen:
            self._seen.add(m)
            bucket.append(m)

    def err(self, m):
        self._add(self.errors, m)

    def warn(self, m):
        self._add(self.warnings, m)

    def info(self, m):
        self._add(self.infos, m)


# ---------------------------------------------------------------- 结构检查：缺字段、类型不对时报错并补默认值，后面的代码不会崩
def sanitize(d, rep):
    def lst(obj, key, where):
        v = obj.get(key)
        if v is None:
            obj[key] = []
        elif not isinstance(v, list):
            rep.err(f'{where}.{key} 应该是数组')
            obj[key] = []
        return obj[key]

    def dct(obj, key, where):
        v = obj.get(key)
        if v is None:
            obj[key] = {}
        elif not isinstance(v, dict):
            rep.err(f'{where}.{key} 应该是对象')
            obj[key] = {}
        return obj[key]

    def text(obj, key, where, required=False):
        v = obj.get(key)
        if v is None or v == '':
            if required:
                rep.err(f'{where} 缺少 {key}')
            obj[key] = obj.get(key) or ''
        elif not isinstance(v, str):
            rep.err(f'{where}.{key} 应该是文字')
            obj[key] = str(v)
        return obj[key]

    meta = dct(d, 'meta', 'project')
    dct(d, 'style', 'project')
    for i, ch in enumerate(lst(d, 'characters', 'project'), 1):
        w = f'characters[{i}]'
        text(ch, 'name', w, True) or ch.__setitem__('name', f'未命名角色{i}')
        lst(ch, 'aliases', w)
        for j, a in enumerate(lst(ch, 'assets', w), 1):
            text(a, 'id', f'{w} 的第 {j} 个资产', True) or a.__setitem__('id', f'_缺ID_{i}_{j}')
            text(a, 'name', f'资产 {a["id"]}', True) or a.__setitem__('name', a['id'])
            lst(a, 'refs', f'资产 {a["id"]}')
            lst(a, 'expressions', f'资产 {a["id"]}')
    for i, pr in enumerate(lst(d, 'props', 'project'), 1):
        text(pr, 'name', f'props[{i}]', True)
        lst(pr, 'keywords', f'props[{i}]')
        lst(pr, 'refs', f'props[{i}]')
    v = dct(d, 'voices', 'project')
    for i, vc in enumerate(lst(v, 'characters', 'voices'), 1):
        text(vc, 'character', f'voices.characters[{i}]', True)
    for i, ln in enumerate(lst(v, 'lines', 'voices'), 1):
        text(ln, 'character', f'voices.lines[{i}]', True)
        text(ln, 'line', f'voices.lines[{i}]', True)
    lst(v, 'notes', 'voices')
    for key in ('lighting',):
        t = d.get(key)
        if t is not None and (not isinstance(t, dict) or not isinstance(t.get('headers'), list) or not isinstance(t.get('rows'), list)):
            rep.err(f'{key} 要写成 {{"headers": [...], "rows": [[...]]}}')
            d[key] = None
    cmp_ = v.get('compare')
    if cmp_ is not None and (not isinstance(cmp_, dict) or not isinstance(cmp_.get('headers'), list) or not isinstance(cmp_.get('rows'), list)):
        rep.err('voices.compare 要写成 {"headers": [...], "rows": [[...]]}')
        v['compare'] = None
    for i, sp in enumerate(lst(d, 'space', 'project'), 1):
        text(sp, 'area', f'space[{i}]', True)
        lst(sp, 'items', f'space[{i}]')
    lst(d, 'scene_rules', 'project')
    lst(d, 'scene_groups', 'project')
    for i, s in enumerate(lst(d, 'scenes', 'project'), 1):
        w = f'scenes[{i}]'
        text(s, 'id', w, True) or s.__setitem__('id', f'_缺ID_S{i}')
        text(s, 'name', f'场景 {s["id"]}', True) or s.__setitem__('name', s['id'])
        text(s, 'group', f'场景 {s["id"]}', True)
        lst(s, 'refs', f'场景 {s["id"]}')
    lst(d, 'script_lines', 'project')
    dr = dct(d, 'director', 'project')
    for i, sec in enumerate(lst(dr, 'sections', 'director'), 1):
        text(sec, 'title', f'director.sections[{i}]', True)
        lst(sec, 'items', f'director.sections[{i}]')
    lst(d, 'music_cues', 'project')
    lst(d, 'post_global', 'project')
    for si, seg in enumerate(lst(d, 'segments', 'project'), 1):
        w = f'片段{si:02d}'
        lst(seg, 'post', w)
        for k, sh in enumerate(lst(seg, 'shots', w), 1):
            text(sh, 'text', f'{w} 分镜{k}', True)
            dur = sh.get('dur')
            if not isinstance(dur, int) or isinstance(dur, bool) or dur <= 0:
                rep.err(f'{w} 分镜{k}：dur 必须是正整数（秒），现在是 {dur!r}')
                sh['dur'] = int(dur) if isinstance(dur, (int, float)) and dur > 0 else 0
            b = sh.get('beats')
            if b is not None and (not isinstance(b, (int, float)) or isinstance(b, bool) or b < 0):
                rep.err(f'{w} 分镜{k}：beats 必须是数字（动作数），现在是 {b!r}')
                sh['beats'] = 0
            if sh.get('speakers') is not None and not isinstance(sh['speakers'], list):
                rep.err(f'{w} 分镜{k}：speakers 应该是角色名数组')
                sh['speakers'] = None
    for k in ('decisions', 'unverified'):
        if not meta.get(k):
            rep.warn(f'meta.{k} 是空的：替用户做的决定和没核实的事要写出来，交付时告诉用户')


# ---------------------------------------------------------------- 项目与资产索引
class Project:
    def __init__(self, data, rep):
        self.d = data
        self.rep = rep
        self.meta = data['meta']
        self.style = data['style']
        self.assets = {}      # id -> dict(kind, group, name, owner, obj)
        self.order = []
        for ch in data['characters']:
            for a in ch['assets']:
                self._add(a, 'character', ch['name'], ch['name'])
        for pr in data['props']:
            if pr.get('id'):
                self._add(pr, 'prop', pr.get('group', ''), '')
        for vc in data['voices']['characters']:
            if vc.get('id'):
                self._add(dict(vc, name=f'{vc["character"]}的音色'), 'voice', '', vc['character'])
        for s in data['scenes']:
            self._add(s, 'scene', s['group'], s['group'])
        r = self.meta.get('ratio', '21:9')
        self.ratio_phrase = self.meta.get('ratio_phrase') or ('电影宽银幕21:9横版' if r == '21:9' else f'{r}画幅')
        self.max_sec = self.meta.get('max_segment_seconds', 30)
        self.max_shots = self.meta.get('max_shots_per_segment', 5)
        self.default_cps = self.meta.get('default_cps', self.meta.get('max_chars_per_second', 3.5))
        self.beat_sec = self.meta.get('seconds_per_beat', 1.5)
        self.seg_header = self.meta.get('segment_header', DEFAULT_SEGMENT_HEADER)
        self.shot_line = self.meta.get('shot_line', DEFAULT_SHOT_LINE)
        self.cps = {v['character']: v['cps'] for v in data['voices']['characters'] if v.get('cps')}
        self.names = {}       # 名字或别称 -> 角色名
        for ch in data['characters']:
            for n in [ch['name']] + ch['aliases']:
                if n:
                    self.names[n] = ch['name']

    def _add(self, a, kind, group, owner):
        aid = a['id']
        if aid in self.assets:
            self.rep.err(f'ID 重复：{aid}')
            return
        self.assets[aid] = dict(kind=kind, group=group, name=a.get('name', aid), owner=owner, obj=a)
        self.order.append(aid)

    def ref(self, aid):
        a = self.assets[aid]
        if a['kind'] == 'voice':
            return a['obj'].get('short', '')
        if a['kind'] == 'prop' and not a['group']:
            return a['obj'].get('desc') or a['name']
        return f"@{a['group']}-{a['name']}"

    def expand(self, text, where, report=True):
        def sub(m):
            aid = m.group(1)
            if aid not in self.assets:
                if report:
                    self.rep.err(f'{where}：引用了不存在的 [[{aid}]]')
                return m.group(0)
            return self.ref(aid)
        out = REF.sub(sub, text or '')
        return out.replace('{ratio_phrase}', self.ratio_phrase)

    def ids_in(self, text):
        return [m.group(1) for m in REF.finditer(text or '')]

    def kind_ids(self, text, kind):
        return [i for i in dict.fromkeys(self.ids_in(text)) if i in self.assets and self.assets[i]['kind'] == kind]


# ---------------------------------------------------------------- 角色提示词组装
def expression_layout(items):
    lines = '；\n'.join(f'{i} {x}' for i, x in enumerate(items, 1))
    return ('角色表情设定图，横版16:9，纯净浅灰色背景，2行3列共六个肩部以上头像，每格同一角色、同一发型、同样的服装领口，无文字标注。'
            f'六个表情依次为：\n{lines}。')


def inherited_outfit(p, a, depth=0):
    """状态变体没写 outfit 时，沿 refs 找同一角色的上游资产继承。"""
    if a.get('outfit') or depth > 5:
        return a.get('outfit', '')
    for r in a.get('refs', []):
        x = p.assets.get(r)
        if x and x['kind'] == 'character':
            o = inherited_outfit(p, x['obj'], depth + 1)
            if o:
                return o
    return ''


def character_prompt(p, ch, a):
    """资产写了 prompt 就原样用；否则按「风格锁 + 参考说明 + DNA + 服装 + 状态 + 版式 + extra」组装。"""
    if a.get('prompt'):
        return p.expand(a['prompt'], f'角色资产 {a["id"]}')
    st = p.style
    parts = []
    if st.get('character_style_lock'):
        parts.append(st['character_style_lock'])
    if a.get('ref_clause'):
        parts.append(a['ref_clause'])
    elif a.get('refs'):
        names = '、'.join(p.assets[r]['name'] for r in a['refs'] if r in p.assets)
        parts.append(f'以参考图（{names}）中的角色为准，脸、发型、体型和身高比例与参考图完全一致，画风一致。')
    elif ch.get('reference_image'):
        parts.append(f'以上传的参考照片人物为原型，保留其脸型、五官比例、皱纹和肤色、发型与体型特征，不要年轻化、不要美化，'
                     f'转化为{p.meta.get("style", "")}角色，不是真人照片。只取人物，忽略照片里的背景。')
    parts.append(ch.get('dna', ''))
    outfit = inherited_outfit(p, a)
    if outfit:
        parts.append('服装：' + outfit)
    if a.get('state'):
        parts.append('状态：' + a['state'])
    layout = a.get('layout', '')
    if layout == '多视图':
        parts.append(st.get('multiview_layout', ''))
    elif layout == '表情':
        parts.append(expression_layout(a.get('expressions', [])))
    elif layout == '单张全身':
        parts.append(SINGLE_LAYOUT)
    if a.get('extra'):
        parts.append(a['extra'])
    return p.expand('\n\n'.join(x for x in parts if x), f'角色资产 {a["id"]}')


# ---------------------------------------------------------------- 说话人
SENT_END = re.compile(r'[。！？]')


def char_mentions(p, s):
    """一段文字里按出现顺序找角色：[[角色资产ID]] 或角色名/别称。返回 [(位置, 角色名)]。"""
    found = []
    for m in REF.finditer(s):
        a = p.assets.get(m.group(1))
        if a and a['kind'] == 'character':
            found.append((m.start(), a['owner']))
    for n in p.names:
        for m in re.finditer(re.escape(n), s):
            found.append((m.start(), p.names[n]))
    return sorted(found)


def speakers_of(p, sh):
    """每句台词的说话人。shot 写了 speakers 就用它；否则取台词前那一句里第一个出现的角色，找不到再往前找最近的角色。"""
    t = sh.get('text', '')
    quotes = list(QUOTE.finditer(t))
    given = sh.get('speakers') or []
    res = []
    plain = QUOTE.sub(lambda m: '“' + '　' * len(m.group(1)) + '”', t)  # 抹掉台词内容，避免把台词里的称呼当成说话人
    for qi, m in enumerate(quotes):
        if qi < len(given) and given[qi]:
            res.append(given[qi])
            continue
        before = plain[:m.start()]
        cut = max([x.end() for x in SENT_END.finditer(before)] + [before.rfind('”') + 1, 0])
        clause = before[cut:]
        ms = char_mentions(p, clause)
        if ms:
            res.append(ms[0][1])
            continue
        ms = char_mentions(p, before)
        res.append(ms[-1][1] if ms else None)
    return res


# ---------------------------------------------------------------- 校验
def validate(p):
    rep, d = p.rep, p.d
    meta = p.meta
    for k in ('title', 'style', 'ratio'):
        if not meta.get(k):
            rep.err(f'meta.{k} 没有填')
    for k in ('character_style_lock', 'character_negative', 'multiview_layout', 'scene_negative'):
        for ph in PLACEHOLDER.findall(p.style.get(k, '') or ''):
            if ph != '{ratio_phrase}':
                rep.warn(f'style.{k} 里还有没替换的占位符 {ph}')
    for k, tpl in (('segment_header', p.seg_header), ('shot_line', p.shot_line)):
        need = ('{scenes}', '{n}') if k == 'segment_header' else ('{i}', '{dur}', '{text}')
        for x in need:
            if x not in tpl:
                rep.warn(f'meta.{k} 里没有 {x}，平台格式可能不完整')

    # 名称
    names = {}
    for aid in p.order:
        a = p.assets[aid]
        if a['kind'] == 'voice' or (a['kind'] == 'prop' and not a['group']):
            continue
        key = (a['group'], a['name'])
        if key in names:
            rep.err(f'平台名称重复：{a["group"]}-{a["name"]}（{names[key]} 与 {aid}）')
        names[key] = aid
        if '-' in a['name']:
            rep.warn(f'名称「{a["name"]}」含连字符，平台按「分组-名称」解析时可能断错，建议改用下划线')
    if not meta.get('allow_group_hyphen'):
        for g in dict.fromkeys(p.assets[i]['group'] for i in p.order if p.assets[i]['group']):
            if '-' in g:
                rep.warn(f'分组名「{g}」含连字符。平台自动起的名字照用即可（设 meta.allow_group_hyphen=true 关闭此提醒），自己起名时改用下划线')

    # 角色资产
    seen = set()
    for ch in d['characters']:
        if not ch.get('dna'):
            rep.err(f'角色 {ch["name"]} 没有 DNA')
        if ch.get('cps'):
            rep.warn(f'角色 {ch["name"]} 的 cps 写在了 characters 里，请挪到 voices.characters 里同名的那一项')
            p.cps.setdefault(ch['name'], ch['cps'])
        for a in ch['assets']:
            for r in a['refs']:
                if r not in p.assets:
                    rep.err(f'角色资产 {a["id"]} 的参考图 {r} 不存在')
                elif p.assets[r]['kind'] == 'character' and r not in seen:
                    rep.err(f'角色资产 {a["id"]} 的参考图 {r} 排在它后面，出图时还没生成')
            lay = a.get('layout')
            if lay and lay not in LAYOUTS:
                rep.err(f'角色资产 {a["id"]} 的 layout「{lay}」不认识，只能是：{"、".join(LAYOUTS)}')
            if not a.get('prompt'):
                if not lay:
                    rep.err(f'角色资产 {a["id"]} 既没有 prompt，也没有 layout，无法组装提示词')
                if lay == '多视图' and not p.style.get('multiview_layout'):
                    rep.warn('有资产用多视图版式，但 style.multiview_layout 是空的')
                if lay in ('多视图', '单张全身') and not inherited_outfit(p, a):
                    rep.warn(f'角色资产 {a["id"]} 没有 outfit，参考链上也继承不到，组装出的提示词里没有服装')
            if lay == '表情' and len(a['expressions']) != 6:
                rep.warn(f'表情资产 {a["id"]} 的 expressions 不是 6 条')
            seen.add(a['id'])

    # 道具
    for pr in d['props']:
        if pr.get('id') and not pr.get('group') and not pr.get('desc'):
            rep.err(f'道具 {pr["id"]} 没有 desc，分镜里的 [[{pr["id"]}]] 会只剩名字，各镜外观会不一致')
        if pr.get('keywords') and not pr.get('id'):
            rep.warn(f'道具「{pr["name"]}」写了 keywords 但没有 id，分镜里没法引用，也不会检查')

    # 音色
    char_set = {c['name'] for c in d['characters']}
    for v in d['voices']['characters']:
        nm = v['character']
        if nm not in char_set:
            rep.err(f'voices 里的「{nm}」和 characters 里的角色名对不上（注意空格和别称），它的 cps 不会生效')
        if len(re.sub(r'\s', '', v.get('long', ''))) > 200:
            rep.warn(f'{nm} 的长版音色超过 200 字，火山音色设计放不下')
        if v.get('short') and len(norm_line(v['short'])) > 15:
            rep.warn(f'{nm} 的短版音色超过 15 字，嵌进视频提示词太长')
        if v.get('audition'):
            hz = len(HANZI.findall(v['audition']))
            if hz < 100:
                rep.warn(f'{nm} 的试听文本只有 {hz} 个汉字，至少要 100 个（不含标点）')
            if len(re.sub(r'\s', '', v['audition'])) > 300:
                rep.warn(f'{nm} 的试听文本超过 300 字（含标点），火山放不下')
        else:
            rep.warn(f'{nm} 没有试听文本')

    # 场景
    seen = set()
    ONLY_CHANGE = re.compile(r'^\s*(以|在|基于)参考图|参考图(的)?基础上|只改')
    for s in d['scenes']:
        par = s.get('parent')
        if not par:
            first = next((r for r in s['refs'] if r in p.assets and p.assets[r]['kind'] == 'scene'), None)
            if first:
                s['parent'] = par = first          # 新项目默认：第一张场景参考图
        if par:
            if par not in p.assets:
                rep.err(f'场景 {s["id"]} 的父场景 {par} 不存在')
            elif p.assets[par]['kind'] != 'scene':
                rep.err(f'场景 {s["id"]} 的父场景 {par} 不是场景')
            elif par not in seen:
                rep.err(f'场景 {s["id"]} 的父场景 {par} 排在它后面')
        for r in s['refs']:
            if r not in p.assets:
                rep.err(f'场景 {s["id"]} 的参考图 {r} 不存在')
            elif p.assets[r]['kind'] == 'scene' and r not in seen:
                rep.err(f'场景 {s["id"]} 的参考图 {r} 排在它后面，出图时还没生成')
        ru = s.get('reuse_of')
        if ru:
            if ru == s['id']:
                rep.err(f'场景 {s["id"]} 复用了自己')
            elif ru not in p.assets or p.assets[ru]['kind'] != 'scene':
                rep.err(f'场景 {s["id"]} 复用的 {ru} 不是已有的场景')
            elif ru not in seen:
                rep.err(f'场景 {s["id"]} 复用的 {ru} 排在它后面')
            elif p.assets[ru]['obj'].get('reuse_of'):
                rep.err(f'场景 {s["id"]} 复用的 {ru} 本身也是复用，请直接指向原图')
            if s.get('prompt'):
                rep.warn(f'场景 {s["id"]} 标了复用，提示词不会被使用')
        elif not s.get('prompt'):
            rep.err(f'场景 {s["id"]} 既没有提示词，也没有标注复用')
        elif ONLY_CHANGE.search(s['prompt']):
            rep.warn(f'场景 {s["id"]} 的提示词写成了「在参考图基础上改」，不带参考图时用不了。请写成完整描述，参考说明放进 prefix')
        if s.get('prompt') and PLACEHOLDER.search(p.expand(s['prompt'], '', report=False)):
            rep.warn(f'场景 {s["id"]} 的提示词里有没替换的占位符：{PLACEHOLDER.search(p.expand(s["prompt"], "", report=False)).group(0)}')
        seen.add(s['id'])

    # 分镜
    usage = {}
    said = []          # [(在拼接串里的起点, 台词规范化文本)]
    total = 0
    shot_keys = set()
    for si, seg in enumerate(d['segments'], 1):
        shots = seg['shots']
        dur = sum(x['dur'] for x in shots)
        total += dur
        tag = f'片段{si:02d}'
        if dur > p.max_sec:
            rep.err(f'{tag} 共 {dur} 秒，超过上限 {p.max_sec} 秒')
        if len(shots) > p.max_shots:
            rep.err(f'{tag} 有 {len(shots)} 个分镜，超过上限 {p.max_shots} 个')
        if not shots:
            rep.err(f'{tag} 没有分镜')
        for k, sh in enumerate(shots, 1):
            shot_keys.add(f'{si:02d}-{k}')
            t = sh['text']
            w = f'{tag} 分镜{k}'
            for aid in dict.fromkeys(p.ids_in(t)):
                usage.setdefault(aid, []).append(f'{si:02d}-{k}')
            scene_ids = p.kind_ids(t, 'scene')
            if not scene_ids:
                rep.err(f'{w}：没有引用任何场景')
            elif len(scene_ids) > 1:
                rep.warn(f'{w}：一个分镜引用了 {len(scene_ids)} 张场景图，模型容易把空间糊在一起，建议拆开')
            if not re.match(r'^在\[\[[A-Za-z0-9_]+\]\]', t):
                rep.warn(f'{w}：没有以「在[[场景ID]]，」开头')
            # 语速与动作
            spk = speakers_of(p, sh)
            need = 0.0
            for qi, m in enumerate(QUOTE.finditer(t)):
                said.append(norm_line(m.group(1)))
                need += len(norm_line(m.group(1))) / p.cps.get(spk[qi], p.default_cps)
                if '“' in m.group(1):
                    rep.warn(f'{w}：台词里有嵌套的双引号，内层请改成单引号')
            if sh.get('beats'):
                need += sh['beats'] * p.beat_sec
            if sh['dur'] and need > sh['dur'] + 0.05:
                rep.warn(f'{w}：台词' + ('和动作' if sh.get('beats') else '') + f'约需 {need:.1f} 秒，只给了 {sh["dur"]} 秒，容易被截断，建议加时长或拆镜')
            body = outside_quotes(t)
            for word in ('字幕', '定格'):
                if word in body:
                    rep.warn(f'{w}：提示词里出现「{word}」，视频模型做不好，建议放进后期')
            if re.search(r'写着|显示着|屏幕上|字样|上面的字', body) and not re.search(r'背面|空白|背对|朝向(他|她)自己|后期', body):
                rep.warn(f'{w}：画面里可能要出字（写着、屏幕上…），请改成背对镜头或空白，字留给后期')
            if re.search(r'画外音|画面外传来|画外响起', body) and p.kind_ids(t, 'character') \
                    and not re.search(r'嘴[^。]{0,8}(闭|合拢)|(双唇|嘴唇)(紧闭|合拢)|闭着嘴|闭嘴|抿着嘴|抿嘴', body):
                rep.warn(f'{w}：有画外音，但没写画面里人物的嘴闭着，模型可能给他对上口型')
            present = {p.assets[i]['owner'] for i in p.kind_ids(t, 'character')}
            for cname in {c['name'] for c in d['characters']} - present:
                hit = None
                for n, owner in p.names.items():
                    if owner != cname:
                        continue
                    for m in re.finditer(re.escape(n), body):
                        clause = re.split(r'[。，；！？]', body[:m.start()])[-1]
                        if '画面外' not in clause:
                            hit = n
                            break
                    if hit:
                        break
                if hit:
                    rep.warn(f'{w}：提到「{hit}」，但这一镜没有他的资产引用。他不在画面里就写「画面外的{hit}」，在的话写成 [[ID]]')
            for pr in d['props']:
                if not pr.get('id') or pr['id'] in p.ids_in(t):
                    continue
                kw = next((x for x in pr['keywords'] if x and x in body), None)
                if kw:
                    rep.warn(f'{w}：出现了道具「{kw}」，但没有写 [[{pr["id"]}]]，这一镜的道具外观会和别的镜头不一样')

    # 台词覆盖：优先在某句台词的开头对上，避免短台词误配到别的台词中间
    starts, pos_ = set(), 0
    for s_ in said:
        starts.add(pos_)
        pos_ += len(s_)
    joined = ''.join(said)
    pos = 0
    for ln in d['script_lines']:
        x = norm_line(ln)
        if not x:
            continue
        j = joined.find(x, pos)
        k = j
        while k >= 0 and k not in starts:
            k = joined.find(x, k + 1)
        if k >= 0:
            j = k
        if j < 0:
            rep.err(f'剧本台词缺失或顺序不对：{ln}')
        else:
            pos = j + len(x)
    if not d['script_lines']:
        rep.warn('没有 script_lines，没法核对台词是否逐字覆盖')

    # 音乐进出
    for c in d['music_cues']:
        if isinstance(c, dict) and c.get('shot') and c['shot'] not in shot_keys:
            rep.warn(f'music_cues 里的分镜 {c["shot"]} 不存在（写法是「片段-分镜」，如 03-2）')

    # 总时长倍数
    ss = meta.get('script_seconds')
    if ss and total:
        ratio = total / ss
        if ratio < 1.3 or ratio > 1.6:
            rep.warn(f'素材总时长 {total} 秒是剧本标称 {ss} 秒的 {ratio:.2f} 倍，常见范围是 1.3 到 1.6 倍')

    # 场景优先级、未使用的资产（道具、表情、音色不报）
    ref_by = {}
    for ch in d['characters']:
        for a in ch['assets']:
            for r in a['refs']:
                ref_by.setdefault(r, []).append(a['id'])
    for s in d['scenes']:
        for r in ([s['parent']] if s.get('parent') else []) + s['refs'] + ([s['reuse_of']] if s.get('reuse_of') else []):
            ref_by.setdefault(r, []).append(s['id'])
    for aid in p.order:
        a = p.assets[aid]
        if a['kind'] in ('prop', 'voice'):
            continue
        used = aid in usage or aid in ref_by
        if a['kind'] == 'scene' and used and a['obj'].get('priority') == '按需':
            rep.warn(f'场景 {a["name"]} 被分镜或其他场景用到了，优先级应该是「必加」而不是「按需」')
        if not used and a['obj'].get('layout') != '表情' and a['obj'].get('type') != '表情':
            rep.info(f'{"场景" if a["kind"] == "scene" else "角色资产"} {a["name"]} 没有被任何分镜或其他资产用到')
    return usage, ref_by


# ---------------------------------------------------------------- 各文件
def f_overview(p, usage, stats):
    d, m = p.d, p.meta
    o = [f'# 《{m.get("title", "")}》制作包总览', '']
    if m.get('logline'):
        o += [p.expand(m['logline'], 'meta.logline'), '']
    rows = [
        ['风格', m.get('style', '')],
        ['画幅', m.get('ratio', '')],
        ['角色', f'{stats["characters"]} 人，{stats["char_assets"]} 个角色资产'],
        ['场景', f'{stats["scenes"]} 个场景位，实际出图 {stats["scene_images"]} 张'],
        ['分镜', f'{stats["segments"]} 个片段、{stats["shots"]} 个分镜，素材总时长 {stats["seconds"]} 秒（约 {stats["seconds"] // 60} 分 {stats["seconds"] % 60} 秒）'],
    ]
    if m.get('script_seconds'):
        rows.append(['剧本标称', f'{m["script_seconds"]} 秒，素材是它的 {stats["seconds"] / m["script_seconds"]:.2f} 倍，多出来的是剪辑余量'])
    o += [table(['项目', '内容'], rows), '']
    o += ['## 文件清单', '', table(['文件', '用途'], [
        ['01_角色多视图提示词.md', '角色定妆多视图、表情、状态变体的出图提示词'],
        ['02_道具提示词.md', '关键道具的固定外观和设定图'],
        ['03_场景提示词.md', '可交给 AI 直接按编号批量出图的场景提示词'],
        ['04_场景关联表.md', '场景分组、父子关系、参考图、人物站位，以及每个资产用在哪些分镜'],
        ['05_角色音色.md', '每个角色的固定音色、试听文本、逐句表演指令'],
        ['06_分镜脚本.md', '按平台格式写好的分镜脚本，每个片段整段粘贴'],
        ['07_后期清单.md', '字幕、定格、叠化、音效、人声处理，以及按分镜排列的台词表'],
        ['index.html', '以上全部内容的查看页，代码块和引用名一键复制'],
        ['project.json', '以上所有文件的数据源。改内容请改它，再重新渲染'],
    ]), '']
    o += ['## 制作顺序', '']
    for i, s in enumerate([
        '角色：按 01 先出每个角色的定妆图，挑定后再用它做参考出表情和状态变体。图片按「资产名」命名，上传到平台对应的角色分组。',
        '道具：按 02 出道具设定图，分镜里出现道具时作为参考。',
        '场景：把 03 整份交给出图 AI 按编号生成。主设定图先自检，合格再往下生成。',
        '在平台建场景：按 04 的分组和名称逐字新建，复用的位置直接选同一张图。',
        '音色：按 05 为每个角色造一次音色并固化，平台能绑定音色就绑在角色上。',
        '分镜：06 的每个片段整段粘贴到平台。粘贴后确认 @ 变成了引用。',
        '后期：按 07 加字幕、定格、叠化，处理人声。',
    ], 1):
        o.append(f'{i}. {s}')
    o.append('')
    o += ['## 资产清单（上传时按这个名字建）', '']

    def used_str(aid):
        u = usage.get(aid, [])
        return '、'.join(u[:6]) + (f' 等 {len(u)} 处' if len(u) > 6 else '')
    rows = []
    for ch in d.get('characters', []):
        for a in ch.get('assets', []):
            rows.append(['角色', ch['name'], a['name'], a.get('type') or a.get('layout', ''), used_str(a['id'])])
    for pr in d.get('props', []):
        if pr.get('id') and pr.get('group'):
            rows.append(['道具', pr['group'], pr['name'], '道具图', used_str(pr['id'])])
    for s in d.get('scenes', []):
        src = f'复用 {p.assets[s["reuse_of"]]["name"]}' if s.get('reuse_of') in p.assets else (s.get('priority') or '新出图')
        rows.append(['场景', s['group'], s['name'], src, used_str(s['id'])])
    o += [table(['类型', '分组', '名称', '说明', '用在分镜'], rows), '']
    if m.get('decisions'):
        o += ['## 替你做的决定', '', *[f'- {p.expand(x, "meta.decisions")}' for x in m['decisions']], '']
    if m.get('unverified'):
        o += ['## 没有核实的事', '', *[f'- {p.expand(x, "meta.unverified")}' for x in m['unverified']], '']
    o += ['## 校验结果', '']
    rep = p.rep
    if not rep.errors and not rep.warnings:
        o += ['没有错误，也没有提醒：引用名、时长、分镜数、台词覆盖都核对过。', '']
    elif not rep.errors:
        o += ['没有错误。下面的提醒请逐条确认。', '']
    if rep.errors:
        o += ['**错误（必须改）**', '', *[f'- {x}' for x in rep.errors], '']
    if rep.warnings:
        o += ['**提醒**', '', *[f'- {x}' for x in rep.warnings], '']
    if rep.infos:
        o += ['**备注**', '', *[f'- {x}' for x in rep.infos], '']
    return '\n'.join(o)


def f_characters(p, usage):
    d, st = p.d, p.style
    o = [f'# 《{p.meta.get("title", "")}》角色多视图提示词', '',
         '每个角色先出定妆图，挑定后用它当参考图再出其他资产，不再用真人照片。角色 DNA 在每条提示词里都原样带着，不要改写同义词。', '']
    if st.get('character_style_lock'):
        o += ['## 风格锁', '', code(st['character_style_lock']), '']
    if st.get('character_negative'):
        o += ['## 通用负面词', '', code(st['character_negative']), '']
    if st.get('multiview_layout'):
        o += ['## 多视图版式', '', code(st['multiview_layout']), '']
    o += ['## 角色总表', '', table(['角色', '定位', '主色', '剪影', '资产'], [
        [c['name'], c.get('role', ''), c.get('color', ''), c.get('silhouette', ''),
         '、'.join(a['name'] for a in c.get('assets', []))] for c in d.get('characters', [])]), '']
    for c in d.get('characters', []):
        o += [f'## {c["name"]}', '']
        if c.get('reference_image'):
            o += [f'原型参考图：`{c["reference_image"]}`', '']
        if c.get('notes'):
            o += [*[f'- {x}' for x in c['notes']], '']
        o += ['**角色 DNA**', '', code(c.get('dna', '')), '']
        for a in c.get('assets', []):
            o += [f'### {a["name"]}', '']
            meta = []
            if a.get('type') or a.get('layout'):
                meta.append(f'类型：{a.get("type") or a.get("layout")}')
            if a.get('use'):
                meta.append(f'用于：{a["use"]}')
            meta.append('参考图：' + ('、'.join(p.assets[r]['name'] if r in p.assets else r for r in a.get('refs', []))
                                       or (f'`{c["reference_image"]}`' if c.get('reference_image') else '无')))
            used = usage.get(a['id'], [])
            if used:
                meta.append(f'用在 {len(used)} 个分镜')
            o += ['；'.join(meta) + '。', '']
            if a.get('note'):
                o += [a['note'], '']
            o += [code(character_prompt(p, c, a)), '']
    return '\n'.join(o)


def f_props(p, usage):
    props = p.d.get('props', [])
    o = [f'# 《{p.meta.get("title", "")}》道具提示词', '']
    if not props:
        o.append('这部剧没有需要单独出图的道具。')
        return '\n'.join(o)
    o += ['跟着人走的道具（杯子、手机、工具）不画进场景图，由角色带着；分镜里每次出现都写同一段固定外观，渲染时由 [[道具ID]] 自动展开，'
          '所以每一镜的道具都长得一样。画面里要出现的文字一律留空，后期再加。', '']
    rows = [[pr.get('name', ''), pr.get('desc', ''), '、'.join(usage.get(pr['id'], [])) if pr.get('id') else '']
            for pr in props if pr.get('desc')]
    if rows:
        o += ['## 道具固定外观', '', table(['道具', '固定外观（分镜里原样出现）', '用在分镜'], rows), '']
    for pr in props:
        if not pr.get('prompt'):
            continue
        o += [f'## {pr["name"]}', '']
        if pr.get('group'):
            o += [f'平台名称：`@{pr["group"]}-{pr["name"]}`', '']
        if pr.get('refs'):
            o += ['参考图：' + '、'.join(p.assets[r]['name'] if r in p.assets else r for r in pr['refs']), '']
        if pr.get('note'):
            o += [pr['note'], '']
        o += [code(p.expand(pr['prompt'], f'道具 {pr["name"]}')), '']
    return '\n'.join(o)


EXEC_NOTES = [
    '按编号从小到大依次生成，每个场景生成一张图。编号顺序已经保证被引用的参考图先生成。标了「复用」的场景不要生成，直接用它复用的那张图。',
    '所有图都是{ratio}空镜，画面里没有人物。出图工具需要单独设置画幅时选 {ratio_short}。',
    '每个场景的「提示词」原样使用，不要改写、删减、合并或翻译。同一物件在不同提示词里的用词是故意保持逐字一致的。',
    '「参考图」列出的是本文件里已经生成的场景图，或已经出好的角色、道具图。工具支持参考图时，按列出的顺序上传，并把「参考图前缀」加在提示词最前面；不支持参考图时，只用提示词、不加前缀；只能传一张时，只传第一张，并去掉前缀里提到第二张参考图的那半句。',
    '负面提示词所有场景共用下面这一条；工具没有负面提示词输入框时忽略。',
    '生成的图片用场景名命名，例如 `{example}.png`。',
    '标了「主设定图」的场景是其余图的源头，生成后先对照它的自检要点检查，有一项不符就重出这一张，最多重出 3 次；仍不符就停下来交给用户确认。',
]


def f_scene_prompts(p, usage):
    d, st, m = p.d, p.style, p.meta
    scenes = d.get('scenes', [])
    num = {s['id']: i for i, s in enumerate(scenes, 1)}
    first = next((s['name'] for s in scenes if not s.get('reuse_of')), '场景名')
    o = [f'# 《{m.get("title", "")}》场景提示词（{m.get("ratio", "")}）', '',
         '本文件只包含场景，每条提示词都是完整的，可以单独使用，也可以整份交给出图 AI 按编号批量生成。', '',
         '## 执行说明', '']
    for i, x in enumerate(EXEC_NOTES, 1):
        o.append(f'{i}. ' + x.format(ratio=p.ratio_phrase, ratio_short=m.get('ratio', ''), example=first))
    o += ['']
    if st.get('scene_negative'):
        o += ['负面提示词：', '', code(st['scene_negative']), '']
    o += ['## 场景总表', '', table(['编号', '场景名', '分组', '类型', '参考图', '用在哪里'], [
        [f'{num[s["id"]]:02d}', s['name'], s['group'],
         ('复用 ' + f'{num.get(s["reuse_of"], 0):02d}') if s.get('reuse_of') else (s.get('priority') or ''),
         '、'.join(f'{num[r]:02d}' if r in num else p.assets.get(r, {}).get('name', r) for r in s.get('refs', [])) or '无',
         s.get('use', '')] for s in scenes]), '']
    if d.get('space'):
        o += ['## 空间设定（供核对，不用于出图）', '']
        for sp in d['space']:
            o += [f'**{sp["area"]}**', '', *[f'- {x}' for x in sp.get('items', [])], '']
    if d.get('scene_rules'):
        o += ['## 拍摄规则', '', *[f'- {x}' for x in d['scene_rules']], '']
    o += ['---', '', '## 场景', '']
    for s in scenes:
        n = num[s['id']]
        o += [f'### {n:02d} {s["name"]}', '']
        o.append(f'- 分组：{s["group"]}')
        if s.get('reuse_of'):
            o += [f'- 复用：直接使用 {num.get(s["reuse_of"], 0):02d} {p.assets.get(s["reuse_of"], {}).get("name", "")} 的图，不要重新生成。', '']
            continue
        if s.get('priority'):
            o.append(f'- 类型：{s["priority"]}')
        if s.get('use'):
            o.append(f'- 用在哪里：{s["use"]}')
        if s.get('refs'):
            def show(r):
                a = p.assets[r]
                src = a['obj'].get('reuse_of') if a['kind'] == 'scene' else None
                if src in p.assets:
                    return f'{num.get(src, 0):02d} {p.assets[src]["name"]}（即 {a["name"]}）'
                return (f'{num[r]:02d} ' if r in num else '') + a['name']
            o.append('- 参考图（按顺序上传）：' + '；'.join(show(r) for r in s['refs'] if r in p.assets))
        else:
            o.append('- 参考图：无')
        if s.get('check'):
            o.append(f'- 自检要点：{s["check"]}')
        o.append('')
        if s.get('prefix'):
            o += ['参考图前缀：', '', code(p.expand(s['prefix'], f'场景 {s["id"]} 前缀')), '']
        o += ['提示词：', '', code(p.expand(s.get('prompt', ''), f'场景 {s["id"]}')), '']
    return '\n'.join(o)


def f_scene_relations(p, usage):
    d = p.d
    scenes = d.get('scenes', [])
    num = {s['id']: i for i, s in enumerate(scenes, 1)}
    o = [f'# 《{p.meta.get("title", "")}》场景关联表', '',
         '平台里的分组和名称要与这里逐字一致，分镜脚本里的 @ 引用才能对上。「用在分镜」写成「片段-分镜」，例如 03-2 是片段 03 的分镜 2。', '']
    groups = list(dict.fromkeys([g['name'] for g in d.get('scene_groups', [])] + [s['group'] for s in scenes]))
    gnote = {g['name']: g.get('note', '') for g in d.get('scene_groups', [])}
    o += ['## 分组与层级', '', '缩进表示父子关系（平台画布上的连线）。父场景在别的分组时，这一项显示在本组的第一层。', '']
    for g in groups:
        o += [f'**{g}**' + (f'：{gnote[g]}' if gnote.get(g) else ''), '']
        members = [s for s in scenes if s['group'] == g]
        ids = {s['id'] for s in members}

        def walk(parent, depth):
            lines = []
            for s in members:
                par = s.get('parent') if s.get('parent') in ids else None
                if par == parent:
                    extra = f'（复用 {p.assets[s["reuse_of"]]["name"]}）' if s.get('reuse_of') in p.assets else ''
                    if not par and s.get('parent') in p.assets:
                        extra += f'（父场景在「{p.assets[s["parent"]]["group"]}」：{p.assets[s["parent"]]["name"]}）'
                    lines.append('  ' * depth + f'- `{s["name"]}`{extra}')
                    lines.extend(walk(s['id'], depth + 1))
            return lines
        o += walk(None, 0) + ['']
    o += ['## 场景明细', '', table(['编号', '分组', '场景名', '父场景', '参考图', '类型', '用在分镜'], [
        [f'{num[s["id"]]:02d}', s['group'], s['name'],
         p.assets[s['parent']]['name'] if s.get('parent') in p.assets else '—',
         '、'.join(p.assets[r]['name'] for r in s.get('refs', []) if r in p.assets) or '—',
         (f'复用 {p.assets[s["reuse_of"]]["name"]}' if s.get('reuse_of') in p.assets else s.get('priority', '')),
         '、'.join(usage.get(s['id'], [])) or '—'] for s in scenes]), '']
    stand = [[s['name'], s['stand']] for s in scenes if s.get('stand')]
    if stand:
        o += ['## 人物能站在哪', '', '写分镜里的「画面左侧、右侧」之前先对照这里，斜机位下人的位置和直觉常常不一样。', '',
              table(['场景', '人物可站位置'], stand), '']
    o += ['## 角色资产用在哪里', '', table(['角色', '资产名', '平台引用', '用在分镜'], [
        [c['name'], a['name'], p.ref(a['id']), '、'.join(usage.get(a['id'], [])) or '—']
        for c in d.get('characters', []) for a in c.get('assets', [])]), '']
    seg_rows = []
    for si, seg in enumerate(d.get('segments', []), 1):
        text = ' '.join(sh.get('text', '') for sh in seg.get('shots', []))
        seg_rows.append([f'{si:02d} {seg.get("title", "")}',
                         '、'.join(p.assets[i]['name'] for i in p.kind_ids(text, 'scene')),
                         '、'.join(p.assets[i]['name'] for i in p.kind_ids(text, 'character')),
                         '、'.join(p.assets[i]['name'] for i in p.kind_ids(text, 'prop'))])
    o += ['## 每个片段用到的资产', '', table(['片段', '场景', '角色资产', '道具'], seg_rows), '']
    if d.get('lighting'):
        lt = d['lighting']
        o += ['## 时间与光线', '', table(lt['headers'], lt['rows']), '']
    return '\n'.join(o)


VOICE_TOOLS = [
    ['平台能给角色绑定音色', '把造好的音色或参考音频绑在角色上', '分镜里不用再写音色描述，按角色引用即可。'],
    ['即梦 / Seedance', '上传参考音频，并在提示词里写短版音色', '官方句式是“使用@音频1……的音色说”。参考音频最多 3 个。'],
    ['可灵', '把音色绑定到角色，或创建自定义音色后引用', '参考素材要单人、干净、无背景音乐。'],
    ['Veo', '只能写在提示词里，用英文', '跨次生成不保证同一个嗓子，可靠做法是后期统一换人声轨。'],
    ['MiniMax 音色设计', '长版 + 试听文本，得到音色 ID', '新音色 ID 要在 7 天内正式合成过一次才保留。'],
    ['ElevenLabs', '英文版 + 中文试听文本', '试听文本至少 100 字符；固定 seed 可复现同一声音。'],
    ['火山 / 豆包语音', '音色设计或声音复刻', '音色描述限 200 字，试听文本限 300 字。单句情绪用指令调，不换音色。'],
]


def f_voices(p):
    v = p.d.get('voices', {})
    o = [f'# 《{p.meta.get("title", "")}》角色音色', '',
         '固定音色只描述“这个人天生的嗓子”，全片不变，原样粘贴；逐句表演指令描述“这一句怎么说”。两样不要混写，否则造出来的嗓子每一句都带着那种情绪。', '']
    for c in v.get('characters', []):
        o += [f'## {c["character"]}', '']
        if c.get('cps'):
            o += [f'语速：每秒约 {c["cps"]} 个字。', '']
        if c.get('long'):
            o += ['长版（给文字造音色的工具）：', '', code(c['long']), '']
        if c.get('short'):
            o += ['短版（平台不能绑定音色时，嵌进说话的分镜）：', '', code(c['short']), '']
        if c.get('en'):
            o += ['英文版：', '', code(c['en']), '']
        if c.get('en_short'):
            o += [f'英文短版：`{c["en_short"]}`', '']
        if c.get('watch'):
            o += [f'验收时注意：{c["watch"]}', '']
        if c.get('audition'):
            hz = len(HANZI.findall(c['audition']))
            o += [f'建音色用的试听文本（{hz} 个汉字' + (f'；{c["audition_note"]}' if c.get('audition_note') else '') + '）：', '',
                  code(c['audition']), '']
    if v.get('compare'):
        o += ['## 声音区分表', '', table(v['compare']['headers'], v['compare']['rows']), '']
    if v.get('lines'):
        o += ['## 逐句表演指令', '']
        by = {}
        for ln in v['lines']:
            by.setdefault(ln['character'], []).append(ln)
        for ch, lns in by.items():
            o += [f'### {ch}', '', table(['场次', '台词', '这一句怎么说'],
                                         [[x.get('where', ''), f'「{x["line"]}」', x.get('direction', '')] for x in lns]), '']
    o += ['## 让同一个角色全片是同一个嗓子', '',
          '1. 每个角色用长版加试听文本在造音色工具里生成一次，挑最像的一条，保存音色 ID。',
          '2. 用这条音色把试听文本合成一遍，导出一段干净的单人音频，作为该角色的参考音频。',
          '3. 之后全片都引用同一个音色 ID 或同一段参考音频。表演变化只写在每句的指令里。', '',
          table(['工具', '音色怎么指定', '注意'], VOICE_TOOLS), '',
          '工具限制会变，使用前以当时的官方说明为准。', '']
    if v.get('notes'):
        o += ['## 读音、合声与后期', '', *[f'- {x}' for x in v['notes']], '']
    return '\n'.join(o)


def segment_block(p, si, seg):
    shots = seg.get('shots', [])
    text = ' '.join(sh.get('text', '') for sh in shots)
    scene_ids = p.kind_ids(text, 'scene')
    head = fill(p.seg_header, scenes=','.join(p.ref(i) for i in scene_ids), n=len(shots))
    body = [fill(p.shot_line, i=k, dur=int(sh['dur']), text=p.expand(sh['text'], f'片段{si:02d} 分镜{k}'))
            for k, sh in enumerate(shots, 1)]
    return head + '\n' + '\n'.join(body)


def camera_of(p, text):
    """分镜第一句（场景之后到第一个句号）：景别、机位、焦段、运镜。"""
    t = REF.sub(lambda m: '', text, count=1) if text.startswith('在[[') else text
    t = re.sub(r'^在，?', '', t)
    first = t.split('。', 1)[0]
    return p.expand(first, '镜头一览', report=False).strip('，')


def f_storyboard(p, stats):
    d, m = p.d, p.meta
    o = [f'# 《{m.get("title", "")}》分镜脚本', '',
         f'共 {stats["segments"]} 个视频片段、{stats["shots"]} 个分镜，素材总时长 {stats["seconds"]} 秒（约 {stats["seconds"] // 60} 分 {stats["seconds"] % 60} 秒）。'
         f'每个片段不超过 {p.max_sec} 秒、最多 {p.max_shots} 个分镜。', '',
         '每个片段的代码块可以整段粘贴到平台。`@` 后面是平台里的「分组-名称」，与资产清单逐字对应。', '']
    dr = d.get('director', {})
    if dr:
        o += ['## 导演阐述', '']
        if dr.get('logline'):
            o += [f'**一句话**：{dr["logline"]}', '']
        for sec in dr.get('sections', []):
            o += [f'**{sec["title"]}**', '', *[f'- {x}' for x in sec.get('items', [])], '']
    if d.get('music_cues'):
        o += ['## 音乐进出', '', table(['分镜', '音乐', '进或出', '由什么触发'],
                                    [[c.get('shot', ''), c.get('music', ''), c.get('action', ''), c.get('trigger', '')] for c in d['music_cues']]), '']
    o += ['## 片段总表', '', table(['片段', '剧本位置', '分镜数', '时长'], [
        [f'{si:02d}｜{seg.get("title", "")}', seg.get('script_pos', ''), len(seg.get('shots', [])),
         f'{sum(int(x["dur"]) for x in seg.get("shots", []))} 秒'] for si, seg in enumerate(d.get('segments', []), 1)]
        + [['合计', '', stats['shots'], f'{stats["seconds"]} 秒']]), '', '---', '']
    for si, seg in enumerate(d.get('segments', []), 1):
        shots = seg.get('shots', [])
        o += [f'## 片段 {si:02d}｜{seg.get("title", "")}', '',
              f'剧本位置：{seg.get("script_pos", "")}。{len(shots)} 个分镜，共 {sum(int(x["dur"]) for x in shots)} 秒。', '']
        if seg.get('note'):
            o += [f'导演备注：{seg["note"]}', '']
        o += [code(segment_block(p, si, seg), 'txt'), '']
        if seg.get('post'):
            o += ['后期：', '', *[f'- {x}' for x in seg['post']], '']
    rows = []
    for si, seg in enumerate(d.get('segments', []), 1):
        for k, sh in enumerate(seg.get('shots', []), 1):
            sc = p.kind_ids(sh.get('text', ''), 'scene')
            rows.append([f'{si:02d}-{k}', f'{sh.get("dur", "")}s', p.assets[sc[0]]['name'] if sc else '', camera_of(p, sh.get('text', ''))])
    o += ['---', '', '## 镜头一览', '', '每个分镜的第一句，方便对照导演阐述检查景别、焦段和运镜是否统一。', '',
          table(['分镜', '时长', '场景', '镜头'], rows), '']
    return '\n'.join(o)


def f_post(p):
    d = p.d
    o = [f'# 《{p.meta.get("title", "")}》后期清单', '']
    if d.get('post_global'):
        o += ['## 全片统一处理', '', *[f'- {x}' for x in d['post_global']], '']
    rows = []
    for si, seg in enumerate(d.get('segments', []), 1):
        for x in seg.get('post', []):
            rows.append([f'{si:02d} {seg.get("title", "")}', x])
    o += ['## 按片段', '', table(['片段', '要做的事'], rows) if rows else '没有片段级的后期项。', '']
    o += ['## 台词表（配音、字幕用）', '', '按片段和分镜排列，引号里的内容就是这一镜要说的话。', '']
    rows = []
    for si, seg in enumerate(d.get('segments', []), 1):
        for k, sh in enumerate(seg.get('shots', []), 1):
            spk = speakers_of(p, sh)
            for qi, q in enumerate(spoken(sh.get('text', ''))):
                rows.append([f'{si:02d}-{k}', spk[qi] or '?', q])
    o += [table(['分镜', '说话人（推断）', '台词'], rows) if rows else '没有台词。', '']
    return '\n'.join(o)


# ---------------------------------------------------------------- Markdown → HTML（只覆盖本脚本输出的写法）
def md_inline(s):
    s = html.escape(s, quote=False)
    codes = []

    def keep(m):
        codes.append(m.group(1))
        return f'\x00{len(codes) - 1}\x00'
    s = re.sub(r'`([^`]+)`', keep, s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', s)
    return re.sub('\x00(\\d+)\x00', lambda m: f'<code class="ic" title="点击复制">{codes[int(m.group(1))]}</code>', s)


def split_row(line):
    line = line.strip().strip('|')
    parts = re.split(r'(?<!\\)\|', line)
    return [x.strip().replace('\\|', '|') for x in parts]


def md_to_html(md, prefix):
    lines = md.split('\n')
    out, i, n_code, n_head = [], 0, 0, 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('```'):
            buf = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                buf.append(lines[i])
                i += 1
            i += 1
            n_code += 1
            out.append(f'<div class="code"><button class="copy" type="button">复制</button>'
                       f'<pre><code>{html.escape(chr(10).join(buf), quote=False)}</code></pre></div>')
            continue
        mh = re.match(r'^(#{1,6})\s+(.*)$', ln)
        if mh:
            n_head += 1
            lv = len(mh.group(1))
            out.append(f'<h{lv} id="{prefix}-h{n_head}">{md_inline(mh.group(2))}</h{lv}>')
            i += 1
            continue
        if ln.strip() == '---':
            out.append('<hr>')
            i += 1
            continue
        if ln.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append(lines[i])
                i += 1
            head = split_row(rows[0])
            body = [split_row(r) for r in rows[2:]]
            t = '<div class="tw"><table><thead><tr>' + ''.join(f'<th>{md_inline(c)}</th>' for c in head) + '</tr></thead><tbody>'
            for r in body:
                t += '<tr>' + ''.join(f'<td>{md_inline(c)}</td>' for c in r) + '</tr>'
            out.append(t + '</tbody></table></div>')
            continue
        if re.match(r'^\s*- ', ln) or re.match(r'^\s*\d+\. ', ln):
            ordered = bool(re.match(r'^\s*\d+\. ', ln))
            items = []
            while i < len(lines) and (re.match(r'^\s*- ', lines[i]) or re.match(r'^\s*\d+\. ', lines[i])):
                depth = (len(lines[i]) - len(lines[i].lstrip())) // 2
                txt = re.sub(r'^\s*(- |\d+\. )', '', lines[i])
                items.append(f'<li style="margin-left:{depth * 1.2}em">{md_inline(txt)}</li>')
                i += 1
            tag = 'ol' if ordered else 'ul'
            out.append(f'<{tag}>' + ''.join(items) + f'</{tag}>')
            continue
        if not ln.strip():
            i += 1
            continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r'^(```|#{1,6}\s|\||\s*- |\s*\d+\. |---\s*$)', lines[i]):
            buf.append(lines[i])
            i += 1
        out.append('<p>' + '<br>'.join(md_inline(b) for b in buf) + '</p>')
    return '\n'.join(out)


CSS = r"""
:root{--bg:#f6f5f1;--panel:#ffffff;--ink:#1f2328;--muted:#6b7079;--line:#e3e1da;--accent:#b4472d;--accent-ink:#ffffff;
--code-bg:#f3f1ea;--ok:#2f7d4f;--warn:#a86a00;--bad:#b42d2d;--chip:#efe9dc}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#16171a;--panel:#1e2024;--ink:#e8e6e1;--muted:#9a9ea6;
--line:#2f3238;--accent:#e2795c;--accent-ink:#16171a;--code-bg:#24272c;--ok:#6cc08f;--warn:#e0a640;--bad:#ef7373;--chip:#2a2d33}}
:root[data-theme="dark"]{--bg:#16171a;--panel:#1e2024;--ink:#e8e6e1;--muted:#9a9ea6;--line:#2f3238;--accent:#e2795c;
--accent-ink:#16171a;--code-bg:#24272c;--ok:#6cc08f;--warn:#e0a640;--bad:#ef7373;--chip:#2a2d33}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.75 -apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
header{position:sticky;top:0;z-index:5;background:var(--panel);border-bottom:1px solid var(--line);padding:12px 20px;display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center}
header h1{font-size:18px;margin:0;font-weight:650}
.stats{display:flex;flex-wrap:wrap;gap:6px}
.stats span{background:var(--chip);border-radius:999px;padding:2px 10px;font-size:13px;color:var(--muted)}
.status{font-size:13px;font-weight:600}
.status.ok{color:var(--ok)}.status.warn{color:var(--warn)}.status.bad{color:var(--bad)}
.tools{margin-left:auto;display:flex;gap:8px;align-items:center}
.tools input{background:var(--bg);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:5px 10px;font:inherit;font-size:14px;width:180px}
.tools button{background:transparent;color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:4px 10px;font:inherit;font-size:13px;cursor:pointer}
nav{display:flex;gap:4px;overflow-x:auto;padding:8px 20px;background:var(--panel);border-bottom:1px solid var(--line);position:sticky;top:57px;z-index:4}
nav button{background:transparent;border:0;border-radius:8px;padding:6px 12px;font:inherit;font-size:14px;color:var(--muted);cursor:pointer;white-space:nowrap}
nav button.on{background:var(--accent);color:var(--accent-ink)}
main{max-width:1100px;margin:0 auto;padding:20px 16px 80px}
section.doc{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:8px 28px 28px;margin-bottom:24px}
section.doc[hidden]{display:none}
h1,h2,h3,h4{line-height:1.35}
section h1{font-size:24px;margin:22px 0 12px}
section h2{font-size:19px;margin:30px 0 10px;padding-top:6px;border-top:1px solid var(--line)}
section h3{font-size:16px;margin:22px 0 8px}
p{margin:8px 0}
a{color:var(--accent)}
ul,ol{padding-left:1.3em;margin:6px 0}
hr{border:0;border-top:1px dashed var(--line);margin:24px 0}
.tw{overflow-x:auto;margin:10px 0}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{border:1px solid var(--line);padding:6px 9px;vertical-align:top;text-align:left}
th{background:var(--code-bg);font-weight:600;white-space:nowrap}
.code{position:relative;margin:10px 0}
.code pre{background:var(--code-bg);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:0;white-space:pre-wrap;word-break:break-word;font:14px/1.75 "SF Mono",Menlo,Consolas,"PingFang SC",monospace}
.copy{position:absolute;top:8px;right:8px;background:var(--accent);color:var(--accent-ink);border:0;border-radius:7px;padding:3px 12px;font:inherit;font-size:13px;cursor:pointer;opacity:.92}
.copy.done{background:var(--ok)}
code.ic{background:var(--chip);border-radius:5px;padding:1px 5px;font-size:.92em;cursor:copy}
code.ic.done{outline:2px solid var(--ok)}
mark{background:#ffe08a;color:#1f2328;border-radius:3px}
.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:var(--ink);color:var(--bg);padding:6px 14px;border-radius:8px;font-size:13px;opacity:0;transition:opacity .2s;pointer-events:none}
.toast.show{opacity:1}
@media (max-width:700px){header{padding:10px 16px}nav{top:0;position:static}section.doc{padding:4px 16px 20px}.tools{margin-left:0;width:100%}.tools input{flex:1;width:auto}}
"""

JS = r"""
const docs=[...document.querySelectorAll('section.doc')], tabs=[...document.querySelectorAll('nav button')];
function show(id){tabs.forEach(b=>b.classList.toggle('on',b.dataset.id===id));
 docs.forEach(d=>d.hidden=!(id==='all'||d.id==='doc-'+id));try{localStorage.setItem('tab',id)}catch(e){} window.scrollTo(0,0)}
tabs.forEach(b=>b.addEventListener('click',()=>show(b.dataset.id)));
let start='00';try{start=localStorage.getItem('tab')||'00'}catch(e){} const hash=location.hash.slice(1); if(tabs.some(b=>b.dataset.id===hash))start=hash;
if(!tabs.some(b=>b.dataset.id===start))start='00'; show(start);
const toast=document.querySelector('.toast');
function tip(t){toast.textContent=t;toast.classList.add('show');clearTimeout(tip.t);tip.t=setTimeout(()=>toast.classList.remove('show'),1300)}
async function copyText(t){try{await navigator.clipboard.writeText(t);return true}catch(e){const a=document.createElement('textarea');a.value=t;
 a.style.position='fixed';a.style.opacity='0';document.body.appendChild(a);a.select();let ok=false;try{ok=document.execCommand('copy')}catch(_){}a.remove();return ok}}
document.addEventListener('click',async e=>{const b=e.target.closest('.copy');if(b){const t=b.parentElement.querySelector('code').innerText;
 if(await copyText(t)){b.textContent='已复制';b.classList.add('done');setTimeout(()=>{b.textContent='复制';b.classList.remove('done')},1300)}return}
 const c=e.target.closest('code.ic');if(c){if(await copyText(c.innerText)){c.classList.add('done');tip('已复制：'+c.innerText.slice(0,40));setTimeout(()=>c.classList.remove('done'),900)}}});
const q=document.getElementById('q');
q.addEventListener('keydown',e=>{if(e.key!=='Enter')return;const k=q.value.trim();document.querySelectorAll('mark').forEach(m=>m.replaceWith(m.textContent));
 if(!k)return;show('all');const w=document.createTreeWalker(document.querySelector('main'),NodeFilter.SHOW_TEXT);let first=null,n=[];
 while(w.nextNode())n.push(w.currentNode);n.forEach(t=>{const i=t.nodeValue.indexOf(k);if(i<0)return;const r=document.createRange();r.setStart(t,i);r.setEnd(t,i+k.length);
 const m=document.createElement('mark');r.surroundContents(m);if(!first)first=m});if(first){first.scrollIntoView({block:'center'})}else tip('没有找到：'+k)});
document.getElementById('theme').addEventListener('click',()=>{const r=document.documentElement;const dark=r.dataset.theme?r.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;
 r.dataset.theme=dark?'light':'dark';try{localStorage.setItem('theme',r.dataset.theme)}catch(e){}});
try{const t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}catch(e){}
"""


def build_html(p, docs, stats):
    rep = p.rep
    if rep.errors:
        status = f'<span class="status bad">校验：{len(rep.errors)} 个错误</span>'
    elif rep.warnings:
        status = f'<span class="status warn">校验通过，{len(rep.warnings)} 条提醒</span>'
    else:
        status = '<span class="status ok">校验全部通过</span>'
    title = html.escape(p.meta.get('title', ''))
    chips = ''.join(f'<span>{html.escape(x)}</span>' for x in [
        p.meta.get('style', ''), p.meta.get('ratio', ''), f'{stats["characters"]} 个角色', f'{stats["scene_images"]} 张场景图',
        f'{stats["segments"]} 个片段', f'{stats["shots"]} 个分镜', f'{stats["seconds"] // 60} 分 {stats["seconds"] % 60} 秒'] if x)
    nav = ''.join(f'<button type="button" data-id="{fn[:2]}">{label}</button>' for fn, label in FILES) + \
        '<button type="button" data-id="all">全部</button>'
    secs = ''.join(f'<section class="doc" id="doc-{fn[:2]}">{md_to_html(docs[fn], fn[:2])}</section>' for fn, _ in FILES)
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} 制作包</title><style>{CSS}</style></head>
<body><header><h1>《{title}》制作包</h1><div class="stats">{chips}</div>{status}
<div class="tools"><input id="q" placeholder="搜索，回车" aria-label="搜索"><button id="theme" type="button">明暗</button></div></header>
<nav>{nav}</nav><main>{secs}</main><div class="toast"></div><script>{JS}</script></body></html>"""


# ---------------------------------------------------------------- 主流程
def load_project(path, depth=0):
    """读取 project.json；include 列出的分文件按顺序合并（列表拼接，字典合并，其余覆盖），分文件里还可以再 include。"""
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    base = os.path.dirname(os.path.abspath(path))
    for part in data.pop('include', []) if depth < 5 else []:
        extra = load_project(os.path.join(base, part), depth + 1)
        for k, v in extra.items():
            if isinstance(v, list) and isinstance(data.get(k), list):
                data[k] = data[k] + v
            elif isinstance(v, dict) and isinstance(data.get(k), dict):
                data[k] = {**data[k], **v}
            else:
                data[k] = v
    return data


def main():
    ap = argparse.ArgumentParser(description='渲染短剧制作包')
    ap.add_argument('project')
    ap.add_argument('--out')
    args = ap.parse_args()
    data = load_project(args.project)
    out = args.out or os.path.dirname(os.path.abspath(args.project))
    os.makedirs(out, exist_ok=True)
    rep = Report()
    sanitize(data, rep)
    p = Project(data, rep)
    usage, _ = validate(p)
    segs = data.get('segments', [])
    stats = dict(
        characters=len(data.get('characters', [])),
        char_assets=sum(len(c.get('assets', [])) for c in data.get('characters', [])),
        scenes=len(data.get('scenes', [])),
        scene_images=sum(1 for s in data.get('scenes', []) if not s.get('reuse_of')),
        segments=len(segs),
        shots=sum(len(s.get('shots', [])) for s in segs),
        seconds=sum(int(x.get('dur', 0)) for s in segs for x in s.get('shots', [])),
    )
    docs = {}
    docs['01_角色多视图提示词.md'] = f_characters(p, usage)
    docs['02_道具提示词.md'] = f_props(p, usage)
    docs['03_场景提示词.md'] = f_scene_prompts(p, usage)
    docs['04_场景关联表.md'] = f_scene_relations(p, usage)
    docs['05_角色音色.md'] = f_voices(p)
    docs['06_分镜脚本.md'] = f_storyboard(p, stats)
    docs['07_后期清单.md'] = f_post(p)
    for fn in list(docs):    # 说明、备注、站位等字段里写的 [[ID]] 也一并展开
        docs[fn] = p.expand(docs[fn], fn)
    docs['00_总览.md'] = f_overview(p, usage, stats)   # 最后生成，带上前面发现的错误；校验信息里的 [[…]] 原样保留
    for fn, _ in FILES:
        with open(os.path.join(out, fn), 'w', encoding='utf-8') as f:
            f.write(docs[fn].rstrip() + '\n')
    with open(os.path.join(out, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(build_html(p, docs, stats))
    print(f'输出目录：{out}')
    print(f'角色 {stats["characters"]}、角色资产 {stats["char_assets"]}、场景位 {stats["scenes"]}（出图 {stats["scene_images"]}）、'
          f'片段 {stats["segments"]}、分镜 {stats["shots"]}、总时长 {stats["seconds"]} 秒')
    for label, items in (('错误', rep.errors), ('提醒', rep.warnings), ('备注', rep.infos)):
        for x in items:
            print(f'[{label}] {x}')
    print(f'校验：错误 {len(rep.errors)}，提醒 {len(rep.warnings)}，备注 {len(rep.infos)}')
    sys.exit(1 if rep.errors else 0)


if __name__ == '__main__':
    main()
