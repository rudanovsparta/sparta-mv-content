#!/usr/bin/env python3
"""
Мирный Воин. Пробуждение — ЯМА
Читает текст из КНИГА_ПЛАТО_v2.md и верстает PDF
Стиль: Undivictus / Sparta aesthetics
"""
import urllib.request, os, re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, PageBreak, HRFlowable
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# ── ЦВЕТА ──
BLACK   = HexColor("#000000")
GOLD    = HexColor("#C8A96E")
GOLD_DK = HexColor("#A08040")
WHITE   = HexColor("#FFFFFF")
GRAY    = HexColor("#888888")
GRAY_LT = HexColor("#CCCCCC")
PAGE_BG = HexColor("#FAFAF8")
DARK    = HexColor("#111111")
BODY    = HexColor("#1C1C1C")

W, H = A4
ML = 22*mm; MR = 22*mm; MT = 28*mm; MB = 22*mm
CW = W - ML - MR

# ── ШРИФТЫ ──
FONT_DIR = Path("/tmp/fonts_mv")
FONT_DIR.mkdir(exist_ok=True)
FONT_URLS = {
    "Lora-R": "https://github.com/google/fonts/raw/main/ofl/lora/Lora%5Bwght%5D.ttf",
    "Lora-I": "https://github.com/google/fonts/raw/main/ofl/lora/Lora-Italic%5Bwght%5D.ttf",
    "PFD-B":  "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf",
}
reg = {}
for nm, url in FONT_URLS.items():
    fp = FONT_DIR / f"{nm}.ttf"
    if not fp.exists():
        try:
            print(f"Скачиваю {nm}...")
            urllib.request.urlretrieve(url, fp)
        except Exception as e:
            print(f"  Ошибка: {e}")
    try:
        pdfmetrics.registerFont(TTFont(nm, str(fp)))
        reg[nm] = True
        print(f"  Зарегистрирован: {nm}")
    except Exception as e:
        print(f"  Ошибка регистрации {nm}: {e}")

def F(r):
    if r == "b":    return "PFD-B"  if "PFD-B"  in reg else "Times-Bold"
    if r == "i":    return "Lora-I" if "Lora-I" in reg else "Times-Italic"
    return               "Lora-R" if "Lora-R" in reg else "Times-Roman"

# ── CUSTOM FLOWABLES ──
class OrnSep(Flowable):
    def __init__(self, w, col=GOLD_DK, sym="·"):
        Flowable.__init__(self)
        self.width = w; self.height = 22
        self.col = col; self.sym = sym
    def draw(self):
        c = self.canv
        c.setFillColor(self.col); c.setStrokeColor(self.col)
        mid = self.width / 2; c.setLineWidth(0.5)
        c.line(0, 9, mid - 16, 9)
        c.line(mid + 16, 9, self.width, 9)
        c.setFont(F("b"), 12)
        c.drawCentredString(mid, 5, self.sym)

class ChHdr(Flowable):
    def __init__(self, num, title, w):
        Flowable.__init__(self)
        self.num = num; self.title = title; self.width = w
        self.height = 130
    def wrap(self, aw, ah):
        return self.width, self.height
    def draw(self):
        c = self.canv
        # тёмный фон
        c.setFillColor(DARK)
        c.rect(0, self.height - 115, self.width, 115, fill=1, stroke=0)
        c.setStrokeColor(GOLD); c.setLineWidth(0.8)
        c.line(0, self.height - 115, self.width, self.height - 115)
        # номер главы
        c.setFillColor(GOLD); c.setFont(F("b"), 8)
        c.drawString(0, self.height - 20, self.num)
        # заголовок — умный перенос
        c.setFillColor(WHITE)
        t = self.title
        fs = 19 if len(t) <= 38 else 16 if len(t) <= 55 else 13
        c.setFont(F("b"), fs)
        mc = int(self.width / (fs * 0.50))
        words = t.split(); lines = []; cur = ""
        for word in words:
            test = (cur + " " + word).strip() if cur else word
            if len(test) <= mc:
                cur = test
            else:
                if cur: lines.append(cur)
                cur = word
        if cur: lines.append(cur)
        yp = self.height - 42
        for ln in lines[:4]:
            c.drawString(0, yp, ln)
            yp -= fs + 6

# ── PAGE CALLBACKS ──
def cover_cb(cv, doc):
    cv.saveState()
    cv.setFillColor(BLACK); cv.rect(0, 0, W, H, fill=1, stroke=0)
    # двойная золотая рамка
    cv.setStrokeColor(GOLD); cv.setLineWidth(0.8)
    m = 14*mm; cv.rect(m, m, W - 2*m, H - 2*m, fill=0, stroke=1)
    cv.setLineWidth(0.3); m2 = 17*mm
    cv.rect(m2, m2, W - 2*m2, H - 2*m2, fill=0, stroke=1)
    # СПАРТА
    cv.setFillColor(GOLD); cv.setFont(F("b"), 9)
    cv.drawCentredString(W/2, H - 32*mm, "С П А Р Т А")
    cv.setStrokeColor(GOLD); cv.setLineWidth(0.4)
    cv.line(W/2 - 38, H - 35*mm, W/2 + 38, H - 35*mm)
    # декоративная линия вместо символа
    cv.setStrokeColor(GOLD); cv.setLineWidth(0.6)
    cv.line(W/2 - 50, H/2 + 28*mm, W/2 + 50, H/2 + 28*mm)
    # МИРНЫЙ ВОИН
    cv.setFillColor(WHITE); cv.setFont(F("b"), 38)
    cv.drawCentredString(W/2, H/2 + 8*mm, "МИРНЫЙ ВОИН")
    cv.setStrokeColor(GOLD); cv.setLineWidth(0.9)
    cv.line(W/2 - 80, H/2 + 2*mm, W/2 + 80, H/2 + 2*mm)
    # ПРОБУЖДЕНИЕ
    cv.setFillColor(GOLD); cv.setFont(F("b"), 18)
    cv.drawCentredString(W/2, H/2 - 8*mm, "П Р О Б У Ж Д Е Н И Е")
    # подзаголовок
    cv.setFillColor(GRAY); cv.setFont(F("i"), 12)
    cv.drawCentredString(W/2, H/2 - 20*mm, "Для тех, кто потерял ориентир — и ищет опору")
    # тег ЯМА
    rw, rh = 95, 21; rx = W/2 - rw/2; ry = H/2 - 38*mm
    cv.setFillColor(GOLD); cv.rect(rx, ry, rw, rh, fill=1, stroke=0)
    cv.setFillColor(BLACK); cv.setFont(F("b"), 9)
    cv.drawCentredString(W/2, ry + 6, "ПЛАТО  ·  37%")
    # нижний орнамент
    cv.setStrokeColor(GOLD); cv.setLineWidth(0.4)
    cv.line(W/2 - 55, 36*mm, W/2 - 14, 36*mm)
    cv.setFillColor(GOLD); cv.setFont(F("b"), 13)
    cv.drawCentredString(W/2, 34*mm, "·")
    cv.line(W/2 + 14, 36*mm, W/2 + 55, 36*mm)
    # автор
    cv.setFillColor(GRAY_LT); cv.setFont(F("i"), 11)
    cv.drawCentredString(W/2, 27*mm, "Антон Бритва")
    cv.setFillColor(GRAY); cv.setFont(F("b"), 8)
    cv.drawCentredString(W/2, 20*mm, "СПАРТА | МИРНЫЙ ВОИН")
    cv.restoreState()

def page_cb(cv, doc):
    cv.saveState()
    cv.setFillColor(PAGE_BG); cv.rect(0, 0, W, H, fill=1, stroke=0)
    cv.setStrokeColor(GOLD); cv.setLineWidth(0.5)
    cv.line(ML, H - 18*mm, W - MR, H - 18*mm)
    cv.setFillColor(GOLD); cv.setFont(F("b"), 7)
    cv.drawString(ML, H - 14*mm, "СПАРТА | МИРНЫЙ ВОИН")
    cv.setFillColor(GRAY); cv.setFont(F("i"), 7)
    cv.drawRightString(W - MR, H - 14*mm, "ПРОБУЖДЕНИЕ · ПЛАТО")
    cv.setStrokeColor(GOLD_DK); cv.setLineWidth(0.3)
    cv.line(ML, 15*mm, W - MR, 15*mm)
    cv.setFillColor(GRAY); cv.setFont(F("i"), 8)
    cv.drawCentredString(W/2, 10*mm, str(doc.page))
    cv.restoreState()

# ── СТИЛИ ──
def make_styles():
    return {
        "body": ParagraphStyle("body", fontName=F("body" if False else "i"),
            fontSize=11.5, leading=20, textColor=BODY,
            alignment=TA_JUSTIFY, spaceAfter=11),
        "bold_line": ParagraphStyle("bold_line", fontName=F("b"),
            fontSize=12, leading=18, textColor=HexColor("#1A1A1A"),
            spaceAfter=8, spaceBefore=4),
        "scene": ParagraphStyle("scene", fontName=F("b"),
            fontSize=11, leading=16, textColor=HexColor("#2A2A2A"),
            spaceAfter=6, spaceBefore=6,
            leftIndent=0, rightIndent=0),
        "action_lbl": ParagraphStyle("action_lbl", fontName=F("b"),
            fontSize=9, leading=14, textColor=GOLD,
            spaceBefore=18, spaceAfter=5),
        "action": ParagraphStyle("action", fontName=F("i"),
            fontSize=12, leading=19, textColor=HexColor("#2A2A2A"),
            leftIndent=10, rightIndent=10, spaceAfter=10),
        "quote": ParagraphStyle("quote", fontName=F("i"),
            fontSize=13, leading=21, textColor=HexColor("#2A2A2A"),
            alignment=TA_CENTER, spaceBefore=14, spaceAfter=10),
        "brand": ParagraphStyle("brand", fontName=F("b"),
            fontSize=10, textColor=GOLD, alignment=TA_CENTER, spaceAfter=5),
        "cta": ParagraphStyle("cta", fontName=F("b"),
            fontSize=20, leading=30, textColor=GOLD,
            alignment=TA_CENTER, spaceBefore=28, spaceAfter=12),
        "cta_sub": ParagraphStyle("cta_sub", fontName=F("i"),
            fontSize=12, textColor=GRAY, alignment=TA_CENTER, spaceAfter=8),
        "cta_url": ParagraphStyle("cta_url", fontName=F("b"),
            fontSize=14, textColor=GOLD, alignment=TA_CENTER, spaceAfter=8),
        "copy": ParagraphStyle("copy", fontName=F("i"),
            fontSize=8, textColor=GRAY, alignment=TA_CENTER, spaceAfter=4),
        "intro_t": ParagraphStyle("intro_t", fontName=F("b"),
            fontSize=16, leading=24, textColor=HexColor("#1A1A1A"),
            alignment=TA_CENTER, spaceAfter=16),
    }

# ── ПАРСИНГ ТЕКСТА v2 ──
def parse_book_text(filepath):
    """Парсит markdown файл книги в структуру глав"""
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    chapters = []
    # Разбиваем по заголовкам глав
    parts = re.split(r'\n## ГЛАВА (\d+):', raw)
    
    # parts[0] — предисловие, parts[1],parts[2] — номер и тело главы 1, и т.д.
    i = 1
    while i < len(parts) - 1:
        num = parts[i].strip()
        body = parts[i + 1]
        # Первая строка — остаток заголовка после номера
        lines = body.split('\n')
        title = lines[0].strip()
        content = '\n'.join(lines[1:])
        chapters.append({
            "num": f"ГЛАВА {num}",
            "title": title,
            "content": content
        })
        i += 2
    
    return chapters

def content_to_flowables(content, styles):
    """Конвертирует текст главы в список flowables"""
    flowables = []
    
    lines = content.split('\n')
    i = 0
    in_action = False
    action_buffer = []
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Пустая строка
        if not line:
            i += 1
            continue
        
        # Разделитель ---
        if line == '---':
            if in_action and action_buffer:
                for ab in action_buffer:
                    flowables.append(Paragraph(ab, styles["action"]))
                action_buffer = []
                in_action = False
            flowables.append(OrnSep(CW))
            i += 1
            continue
        
        # Блок ДЕЙСТВИЕ / ACTION
        if line.startswith('**ДЕЙСТВИЕ') or line.startswith('**Действие'):
            in_action = True
            clean = line.replace('**ДЕЙСТВИЕ**', '').replace('**Действие**', '').strip()
            flowables.append(Spacer(1, 8))
            flowables.append(Paragraph("ДЕЙСТВИЕ", styles["action_lbl"]))
            if clean:
                flowables.append(Paragraph(clean, styles["action"]))
            i += 1
            continue
        
        # Жирные однострочные (короткие, сцена) — **текст**
        bold_match = re.match(r'^\*\*(.+?)\*\*$', line)
        if bold_match:
            text = bold_match.group(1)
            if len(text) < 80:
                flowables.append(Paragraph(text, styles["bold_line"]))
            else:
                flowables.append(Paragraph(text, styles["body"]))
            i += 1
            continue
        
        # Обычный текст — убираем markdown разметку
        clean_line = line
        clean_line = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', clean_line)
        clean_line = re.sub(r'\*(.+?)\*', r'<i>\1</i>', clean_line)
        clean_line = re.sub(r'_(.+?)_', r'<i>\1</i>', clean_line)
        
        # Определяем стиль
        if in_action:
            action_buffer.append(clean_line)
        else:
            # Проверяем — это сцена (имя персонажа, короткая строка с запятой)?
            # Паттерн: Имя, возраст лет. Профессия.
            if re.match(r'^[А-Я][а-яё]+,?\s+\d{2}', line) and len(line) < 100:
                flowables.append(Paragraph(clean_line, styles["scene"]))
            else:
                flowables.append(Paragraph(clean_line, styles["body"]))
        i += 1
    
    # Добавить оставшийся action buffer
    if action_buffer:
        for ab in action_buffer:
            flowables.append(Paragraph(ab, styles["action"]))
    
    return flowables

# ── ГЛАВНЫЙ СБОРЩИК ──
def build_pdf(text_file, output_path):
    styles = make_styles()
    chapters = parse_book_text(text_file)
    print(f"Глав найдено: {len(chapters)}")
    for ch in chapters:
        print(f"  {ch['num']}: {ch['title'][:50]}")

    # ── ОБЛОЖКА ──
    cover_path = "/tmp/mvs_cover_плато_v2.pdf"
    c = rl_canvas.Canvas(cover_path, pagesize=A4)
    c.setTitle("Мирный Воин. Пробуждение — ЯМА")
    c.setAuthor("Perplexity Computer")

    class FD:
        page = 0
    cover_cb(c, FD())
    c.showPage()
    c.save()

    # ── КОНТЕНТ ──
    content_path = "/tmp/mvs_content_плато_v2.pdf"

    def _page_cb(cv, doc):
        page_cb(cv, doc)

    doc = BaseDocTemplate(
        content_path,
        pagesize=A4,
        leftMargin=ML, rightMargin=MR,
        topMargin=MT, bottomMargin=MB,
        title="Мирный Воин. Пробуждение — ЯМА",
        author="Perplexity Computer",
    )
    frame = Frame(ML, MB, CW, H - MT - MB, id="main")
    doc.addPageTemplates([PageTemplate(id="pg", frames=[frame], onPage=_page_cb)])

    story = []

    # Предисловие / Intro страница
    story.append(Spacer(1, 20*mm))
    story.append(Paragraph("МИРНЫЙ ВОИН", styles["intro_t"]))
    story.append(Paragraph("Пробуждение", ParagraphStyle("sub", fontName=F("i"),
        fontSize=13, textColor=GRAY, alignment=TA_CENTER, spaceAfter=6)))
    story.append(Spacer(1, 4*mm))
    story.append(OrnSep(CW, GOLD))
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph(
        "Эта книга написана для мужчин которые застряли на «Стене» — "
        "знают что делать, понимают как, и всё равно тормозят. "
        "Не потому что ленивые. Потому что используют неправильный инструмент.",
        ParagraphStyle("pre", fontName=F("i"), fontSize=12, leading=20,
            textColor=BODY, alignment=TA_JUSTIFY, spaceAfter=12)))
    story.append(Paragraph(
        "Здесь нет универсальных методик. Есть механизмы. "
        "Читай главу — находи своё. Делай следующий честный шаг.",
        ParagraphStyle("pre2", fontName=F("i"), fontSize=12, leading=20,
            textColor=BODY, alignment=TA_JUSTIFY, spaceAfter=12)))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("Антон Бритва", ParagraphStyle("sig", fontName=F("b"),
        fontSize=11, textColor=HexColor("#2A2A2A"), alignment=TA_CENTER, spaceAfter=4)))
    story.append(Paragraph("СПАРТА | с 2011", ParagraphStyle("sig2", fontName=F("i"),
        fontSize=9, textColor=GRAY, alignment=TA_CENTER, spaceAfter=4)))
    story.append(PageBreak())

    # Главы
    for ch in chapters:
        # Заголовок главы
        story.append(ChHdr(ch["num"], ch["title"], CW))
        story.append(Spacer(1, 8*mm))
        
        # Контент
        ch_flowables = content_to_flowables(ch["content"], styles)
        story.extend(ch_flowables)
        
        # Отступ между главами
        story.append(Spacer(1, 10*mm))
        story.append(PageBreak())

    # ── CTA ФИНАЛЬНАЯ СТРАНИЦА ──
    story.append(Spacer(1, 15*mm))
    story.append(OrnSep(CW, GOLD, "·"))
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("ПОЛУЧИТЬ РАЗБОР МАРШРУТА", styles["cta"]))
    story.append(Paragraph(
        "Сорок минут. Один на один. Смотрим что именно тебя останавливает — "
        "не в теории, а в твоей конкретной ситуации.",
        styles["cta_sub"]))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(
        '<a href="https://spartamv.ru" color="#C8A96E">spartamv.ru</a>',
        styles["cta_url"]))
    story.append(Spacer(1, 8*mm))
    story.append(OrnSep(CW, GOLD_DK, "·"))
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph(
        "Не ещё один курс. Среда, где слово проверяется делом.",
        ParagraphStyle("mission", fontName=F("b"), fontSize=11, leading=17,
            textColor=GOLD, alignment=TA_CENTER, spaceAfter=6)))
    story.append(Paragraph(
        "СПАРТА | МИРНЫЙ ВОИН — мужская среда с 2011 года",
        ParagraphStyle("sp", fontName=F("i"), fontSize=9,
            textColor=GRAY, alignment=TA_CENTER, spaceAfter=4)))

    doc.build(story)
    print(f"Контент сгенерирован: {content_path}")

    # ── СКЛЕЙКА ──
    from pypdf import PdfWriter, PdfReader
    writer = PdfWriter()
    for path in [cover_path, content_path]:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)
    print(f"\nGOTOVO: {output_path}")
    import os
    size_kb = os.path.getsize(output_path) // 1024
    print(f"Размер: {size_kb} KB")

if __name__ == "__main__":
    TEXT_FILE = "/home/user/workspace/КНИГА_ПЛАТО_v2.md"
    OUTPUT = "/home/user/workspace/МВ_Пробуждение_ПЛАТО_v2.pdf"
    build_pdf(TEXT_FILE, OUTPUT)
