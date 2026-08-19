#!/usr/bin/env python3
"""Build HTML chapters from the parsed markdown of 智能资本论."""

import re
import os

SOURCE = "/Coze/Drive/大黑塔/智能资本论-精美版_1787145884947_0_8mpc.docx.parsed.md"
OUT_DIR = "/Coze/Drive/大黑塔/github-site/intelligent-capital/"

# ── Read source ──────────────────────────────────────────────────────────────
with open(SOURCE, "r", encoding="utf-8") as f:
    lines = f.readlines()

# ── Chapter definitions (1-indexed line numbers → 0-indexed) ────────────────
chapters_raw = [
    (72,   111,  "preface.html",    "序言",   "马克思在莲洲，巨莲叶上"),
    (112,  243,  "prologue.html",   "楔子",   "一个算法的解剖"),
    (245,  988,  "vol1.html",       "卷一",   "智能商品——数据如何成为新的商品"),
    (990,  1803, "vol2.html",       "卷二",   "数据货币——注意力如何成为一般等价物"),
    (1805, 2294, "vol3.html",       "卷三",   "劳动力的新形态——认知劳动如何被吸纳进资本"),
    (2296, 2755, "vol4.html",       "卷四",   "算法剩余价值——利润的新来源"),
    (2757, 3204, "vol5.html",       "卷五",   "智能资本积累——数据如何自我增殖，算法如何形成壁垒"),
    (3206, 3661, "vol6.html",       "卷六",   "利润率下降趋势——资本主义内置的死刑判决"),
    (3663, 4228, "vol7.html",       "卷七",   "智能资本的循环与周转——从数据采集到变现的完整周期"),
    (4230, 4653, "vol8.html",       "卷八",   "金融资本——钱如何自己生钱，智能资本的金融化与虚拟经济"),
    (4655, 5144, "vol9.html",       "卷九",   "危机与周期——繁荣与崩溃的钟摆，智能资本的内在矛盾总爆发"),
    (5146, 5337, "epilogue.html",   "尾声",   "资本的边界——当物质丰裕，意识觉醒，资本关系还剩什么？"),
]

# ── Heading detection patterns ──────────────────────────────────────────────
# 第X节 ... → h2 (section heading)
RE_SECTION = re.compile(r'^第[一二三四五六七八九十]+节\s+(.+)')
# X、... → h3 (sub-section heading, Chinese numeral)
RE_SUBSECTION = re.compile(r'^([一二三四五六七八九十]+)、(.+)')
# 本章结构 → h3
RE_CHAPTER_STRUCT = re.compile(r'^本章结构$')
# 一、二、三、 in epilogue etc → h3 (already covered by RE_SUBSECTION)
# X.Y.Z numbered patterns like "96. xxx" → h3
RE_NUMBERED = re.compile(r'^(\d+)\.\s+(.+)')
# "（X）..." patterns → h4
RE_PAREN = re.compile(r'^[（(]([一二三四五六七八九十]+)[)）](.+)')


def md_to_html(md_text):
    """Convert markdown text to HTML with Chinese heading detection."""
    raw_lines = md_text.split('\n')
    result = []
    in_list = False
    in_blockquote = False
    list_type = 'ul'
    
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i]
        stripped = line.strip()
        
        # Empty line
        if not stripped:
            if in_list:
                result.append(f'</{list_type}>')
                in_list = False
            if in_blockquote:
                result.append('</blockquote>')
                in_blockquote = False
            result.append('')
            i += 1
            continue
        
        # Close blockquote if no longer in blockquote
        if in_blockquote and not stripped.startswith('>'):
            result.append('</blockquote>')
            in_blockquote = False
        
        # Blockquote
        if stripped.startswith('>'):
            if not in_blockquote:
                if in_list:
                    result.append(f'</{list_type}>')
                    in_list = False
                result.append('<blockquote>')
                in_blockquote = True
            content = stripped[1:].strip()
            content = inline_md(content)
            result.append(f'<p>{content}</p>')
            i += 1
            continue
        
        # Markdown headings (just in case)
        if stripped.startswith('#### '):
            if in_list:
                result.append(f'</{list_type}>')
                in_list = False
            content = inline_md(stripped[5:])
            result.append(f'<h4>{content}</h4>')
            i += 1
            continue
        if stripped.startswith('### '):
            if in_list:
                result.append(f'</{list_type}>')
                in_list = False
            content = inline_md(stripped[4:])
            result.append(f'<h4>{content}</h4>')
            i += 1
            continue
        if stripped.startswith('## '):
            if in_list:
                result.append(f'</{list_type}>')
                in_list = False
            content = inline_md(stripped[3:])
            result.append(f'<h3>{content}</h3>')
            i += 1
            continue
        if stripped.startswith('# '):
            if in_list:
                result.append(f'</{list_type}>')
                in_list = False
            content = inline_md(stripped[2:])
            result.append(f'<h2>{content}</h2>')
            i += 1
            continue
        
        # Chinese section heading: 第X节 ...
        m = RE_SECTION.match(stripped)
        if m:
            if in_list:
                result.append(f'</{list_type}>')
                in_list = False
            content = inline_md(m.group(1))
            result.append(f'<h2>{content}</h2>')
            i += 1
            continue
        
        # Chinese sub-section heading: X、...
        m = RE_SUBSECTION.match(stripped)
        if m:
            if in_list:
                result.append(f'</{list_type}>')
                in_list = False
            content = inline_md(f'{m.group(1)}、{m.group(2)}')
            result.append(f'<h3>{content}</h3>')
            i += 1
            continue
        
        # 本章结构
        if RE_CHAPTER_STRUCT.match(stripped):
            if in_list:
                result.append(f'</{list_type}>')
                in_list = False
            result.append('<h3>本章结构</h3>')
            i += 1
            continue
        
        # Numbered sections: "96. xxx"
        m = RE_NUMBERED.match(stripped)
        if m and int(m.group(1)) <= 200:
            if in_list:
                result.append(f'</{list_type}>')
                in_list = False
            content = inline_md(m.group(2))
            result.append(f'<h3>{content}</h3>')
            i += 1
            continue
        
        # Unordered list
        if stripped.startswith('• ') or stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                result.append('<ul>')
                in_list = True
                list_type = 'ul'
            content = inline_md(stripped[2:])
            result.append(f'<li>{content}</li>')
            i += 1
            continue
        
        # Ordered list
        ol_match = re.match(r'^(\d+)\.\s+(.+)', stripped)
        if ol_match and int(ol_match.group(1)) > 200:
            # This is an ordered list item, not a heading
            if not in_list or list_type != 'ol':
                if in_list:
                    result.append(f'</{list_type}>')
                result.append('<ol>')
                in_list = True
                list_type = 'ol'
            content = inline_md(ol_match.group(2))
            result.append(f'<li>{content}</li>')
            i += 1
            continue
        
        # Close list if we hit a non-list item
        if in_list:
            result.append(f'</{list_type}>')
            in_list = False
        
        # Regular paragraph
        content = inline_md(stripped)
        result.append(f'<p>{content}</p>')
        i += 1
    
    if in_list:
        result.append(f'</{list_type}>')
    if in_blockquote:
        result.append('</blockquote>')
    
    return '\n'.join(result)


def inline_md(text):
    """Convert inline markdown formatting."""
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text


# ── CSS Template ─────────────────────────────────────────────────────────────
CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
    --bg: #1a1a2e;
    --bg-content: #16162a;
    --gold: #d4af37;
    --gold-dim: #b8962e;
    --text: #e0e0e0;
    --text-dim: #9a9ab0;
    --border: rgba(212,175,55,0.2);
    --link: #e8c84a;
}
html { scroll-behavior: smooth; }
body {
    font-family: Georgia, 'Noto Serif SC', 'Source Han Serif SC', '宋体', serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.8;
    min-height: 100vh;
}
.page-wrap {
    max-width: 720px;
    margin: 0 auto;
    padding: 0 1.5rem;
}
/* Top navigation */
.top-nav {
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(26,26,46,0.95);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid var(--border);
    padding: 0.8rem 0;
    margin-bottom: 0;
}
.top-nav .inner {
    max-width: 720px;
    margin: 0 auto;
    padding: 0 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.85rem;
    gap: 0.5rem;
}
.top-nav a {
    color: var(--gold);
    text-decoration: none;
    transition: opacity 0.2s;
    white-space: nowrap;
}
.top-nav a:hover { opacity: 0.7; }
.top-nav .nav-disabled { color: var(--text-dim); opacity: 0.4; pointer-events: none; }
.top-nav .nav-center { display: flex; gap: 0.5rem; align-items: center; flex: 1; justify-content: center; }
/* Chapter header */
.chapter-header {
    text-align: center;
    padding: 3rem 0 2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2.5rem;
}
.chapter-header .label {
    font-size: 0.85rem;
    color: var(--gold-dim);
    letter-spacing: 0.3em;
    margin-bottom: 0.8rem;
}
.chapter-header h1 {
    font-size: clamp(1.6rem, 5vw, 2.2rem);
    color: var(--gold);
    font-weight: 700;
    margin-bottom: 0.6rem;
    line-height: 1.3;
}
.chapter-header .subtitle {
    font-size: 1rem;
    color: var(--text-dim);
    font-style: italic;
}
/* Content */
.content { padding-bottom: 3rem; }
.content h2 {
    font-size: 1.4rem;
    color: var(--gold);
    margin: 2.5rem 0 1rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
}
.content h3 {
    font-size: 1.15rem;
    color: var(--gold);
    margin: 2rem 0 0.8rem;
}
.content h4 {
    font-size: 1.05rem;
    color: var(--gold-dim);
    margin: 1.5rem 0 0.6rem;
}
.content p {
    margin-bottom: 1.2rem;
    text-align: justify;
}
.content blockquote {
    margin: 1.5rem 0;
    padding: 1rem 1.5rem;
    border-left: 3px solid var(--gold);
    background: rgba(212,175,55,0.05);
    border-radius: 0 6px 6px 0;
    font-style: italic;
    color: var(--text-dim);
}
.content blockquote p { margin-bottom: 0.5rem; }
.content blockquote p:last-child { margin-bottom: 0; }
.content ul, .content ol {
    margin: 1rem 0 1.5rem 1.5rem;
}
.content li {
    margin-bottom: 0.5rem;
}
.content strong { color: #f0f0f0; }
.content code {
    background: rgba(212,175,55,0.15);
    padding: 0.1em 0.4em;
    border-radius: 3px;
    font-size: 0.9em;
    color: var(--gold);
}
/* Footer */
.page-footer {
    border-top: 1px solid var(--border);
    padding: 1.5rem 0;
    text-align: center;
    font-size: 0.8rem;
    color: var(--text-dim);
}
.page-footer a {
    color: var(--gold-dim);
    text-decoration: none;
}
.page-footer a:hover { text-decoration: underline; }
.footer-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
@media (max-width: 600px) {
    .page-wrap { padding: 0 1rem; }
    .top-nav .inner { padding: 0 1rem; font-size: 0.78rem; }
    .chapter-header { padding: 2rem 0 1.5rem; }
    .content p { text-align: left; }
    .footer-nav { flex-wrap: wrap; gap: 0.5rem; justify-content: center; }
}
"""


def make_chapter_html(title, subtitle, content_html, prev_file, prev_title, next_file, next_title, label=""):
    prev_link = f'<a href="{prev_file}">← {prev_title}</a>' if prev_file else '<span class="nav-disabled">← 上一章</span>'
    next_link = f'<a href="{next_file}">{next_title} →</a>' if next_file else '<span class="nav-disabled">下一章 →</span>'
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - 智能资本论</title>
<style>{CSS}</style>
</head>
<body>
<nav class="top-nav">
    <div class="inner">
        <a href="index.html">目录</a>
        <span class="nav-center">{prev_link}</span>
        <span>{next_link}</span>
    </div>
</nav>
<div class="page-wrap">
    <div class="chapter-header">
        <div class="label">{label or title}</div>
        <h1>{title}：{subtitle}</h1>
    </div>
    <div class="content">
{content_html}
    </div>
    <footer class="page-footer">
        <div class="footer-nav">
            <span>{f'<a href="{prev_file}">← {prev_title}</a>' if prev_file else ''}</span>
            <a href="#" onclick="window.scrollTo({{top:0,behavior:'smooth'}});return false;">↑ 返回顶部</a>
            <span>{f'<a href="{next_file}">{next_title} →</a>' if next_file else ''}</span>
        </div>
    </footer>
</div>
</body>
</html>"""


# ── Build chapter nav map ────────────────────────────────────────────────────
chapters = []
for (s, e, fn, title, sub) in chapters_raw:
    chapters.append((fn, title, sub, s - 1, e))

file_list = [c[0] for c in chapters]
title_list = [c[1] for c in chapters]

nav_info = {}
for i, (fn, title, sub, start, end) in enumerate(chapters):
    prev_f = chapters[i-1][0] if i > 0 else None
    prev_t = chapters[i-1][1] if i > 0 else None
    next_f = chapters[i+1][0] if i < len(chapters)-1 else None
    next_t = chapters[i+1][1] if i < len(chapters)-1 else None
    nav_info[fn] = (prev_f, prev_t, next_f, next_t)


def extract_chapter_md(start_0, end_0):
    """Extract markdown lines for a chapter, skipping the title line."""
    chapter_lines = lines[start_0:end_0]
    text = ''.join(chapter_lines[1:])
    # Remove end markers
    text = re.sub(r'\n(楔子完|卷[一二三四五六七八九]完)\s*$', '', text)
    # Remove trailing "尾声完" or similar
    text = re.sub(r'\n(尾声完|全书完)\s*$', '', text)
    return text.strip()


# ── Build index.html ─────────────────────────────────────────────────────────
def build_index():
    toc_items = []
    for fn, title, sub, start, end in chapters:
        toc_items.append(
            f'<li><a href="{fn}">'
            f'<span class="toc-title">{title}</span>'
            f'<span class="toc-sub">{sub}</span></a></li>'
        )
    
    toc_html = '\n'.join(toc_items)
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>智能资本论</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
:root {{
    --bg: #1a1a2e;
    --gold: #d4af37;
    --gold-dim: #b8962e;
    --text: #e0e0e0;
    --text-dim: #9a9ab0;
    --border: rgba(212,175,55,0.2);
}}
html {{ scroll-behavior: smooth; }}
body {{
    font-family: Georgia, 'Noto Serif SC', 'Source Han Serif SC', '宋体', serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.8;
    min-height: 100vh;
}}
.cover {{
    max-width: 720px;
    margin: 0 auto;
    padding: 4rem 1.5rem 2rem;
    text-align: center;
}}
.cover .series {{
    font-size: 0.85rem;
    color: var(--gold-dim);
    letter-spacing: 0.4em;
    margin-bottom: 1rem;
}}
.cover h1 {{
    font-size: clamp(2rem, 8vw, 3.5rem);
    color: var(--gold);
    font-weight: 700;
    margin-bottom: 0.5rem;
    letter-spacing: 0.1em;
    line-height: 1.2;
}}
.cover .main-subtitle {{
    font-size: 1.1rem;
    color: var(--text-dim);
    font-style: italic;
    margin-bottom: 0.5rem;
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
}}
.cover .author {{
    font-size: 0.95rem;
    color: var(--text-dim);
    margin-top: 1.5rem;
    margin-bottom: 0.3rem;
}}
.cover .year {{
    font-size: 0.85rem;
    color: var(--gold-dim);
    letter-spacing: 0.3em;
}}
.cover .ornament {{
    margin: 2rem auto;
    width: 60px;
    height: 1px;
    background: var(--gold);
    opacity: 0.5;
}}
.toc-section {{
    max-width: 720px;
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;
}}
.toc-section h2 {{
    text-align: center;
    font-size: 1.2rem;
    color: var(--gold-dim);
    letter-spacing: 0.3em;
    margin-bottom: 2rem;
}}
.toc-list {{
    list-style: none;
}}
.toc-list li {{
    border-bottom: 1px solid var(--border);
}}
.toc-list li:last-child {{ border-bottom: none; }}
.toc-list a {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: 1rem 0.5rem;
    text-decoration: none;
    transition: background 0.2s;
    border-radius: 4px;
}}
.toc-list a:hover {{
    background: rgba(212,175,55,0.05);
}}
.toc-title {{
    color: var(--text);
    font-size: 1rem;
    font-weight: 600;
    flex-shrink: 0;
}}
.toc-sub {{
    color: var(--text-dim);
    font-size: 0.85rem;
    text-align: right;
    font-style: italic;
    margin-left: 1rem;
}}
.footer-note {{
    text-align: center;
    padding: 2rem 1.5rem 3rem;
    font-size: 0.85rem;
    color: var(--text-dim);
    max-width: 720px;
    margin: 0 auto;
    border-top: 1px solid var(--border);
}}
.footer-note a {{
    color: var(--gold-dim);
    text-decoration: none;
}}
.footer-note a:hover {{ text-decoration: underline; }}
@media (max-width: 600px) {{
    .cover {{ padding: 3rem 1rem 1.5rem; }}
    .toc-list a {{ flex-direction: column; gap: 0.3rem; }}
    .toc-sub {{ text-align: left; margin-left: 0; }}
}}
</style>
</head>
<body>
<div class="cover">
    <div class="series">六本书系列 · 第一本</div>
    <h1>智能资本论</h1>
    <p class="main-subtitle">承接马克思《资本论》，分析智能时代的资本新形态</p>
    <div class="ornament"></div>
    <p class="author">马克思在莲洲，巨莲叶上</p>
    <p class="year">2026</p>
</div>

<div class="toc-section">
    <h2>全 书 目 录</h2>
    <ul class="toc-list">
{toc_html}
    </ul>
</div>

<div class="footer-note">
    <p>下一本：《科技论》——技术是凝固的社会关系</p>
    <p style="margin-top: 1rem;"><a href="../index.html">← 返回首页</a></p>
</div>
</body>
</html>"""


# ── Write all files ──────────────────────────────────────────────────────────
os.makedirs(OUT_DIR, exist_ok=True)

# Write index.html
index_html = build_index()
with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)
print("✓ index.html")

# Write each chapter
for i, (fn, title, subtitle, start, end) in enumerate(chapters):
    md_text = extract_chapter_md(start, end)
    content_html = md_to_html(md_text)
    prev_f, prev_t, next_f, next_t = nav_info[fn]
    
    html = make_chapter_html(title, subtitle, content_html, prev_f, prev_t, next_f, next_t, label=title)
    
    with open(os.path.join(OUT_DIR, fn), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ {fn} ({len(md_text)} chars)")

print(f"\nDone! {len(chapters)+1} files written to {OUT_DIR}")
