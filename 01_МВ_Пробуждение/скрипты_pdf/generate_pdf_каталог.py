#!/usr/bin/env python3
"""
Генератор PDF-каталога «Мирный Воин. Пробуждение»
Навигатор по 5 сегментам — брендбук СПАРТА
"""

import os
import urllib.request
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.units import mm, cm

# ─── Пути ────────────────────────────────────────────────────────────────────
FONT_DIR = Path("/tmp/fonts_mv")
FONT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = "/home/user/workspace/МВ_Пробуждение_КАТАЛОГ.pdf"

# ─── Шрифты ──────────────────────────────────────────────────────────────────
fonts = {
    "Lora-R": "https://raw.githubusercontent.com/google/fonts/main/ofl/lora/Lora%5Bwght%5D.ttf",
    "Lora-I": "https://raw.githubusercontent.com/google/fonts/main/ofl/lora/Lora-Italic%5Bwght%5D.ttf",
    "PTSerif-R": "https://raw.githubusercontent.com/google/fonts/main/ofl/ptserif/PT_Serif-Web-Regular.ttf",
    "PTSerif-B": "https://raw.githubusercontent.com/google/fonts/main/ofl/ptserif/PT_Serif-Web-Bold.ttf",
    "PTSerif-I": "https://raw.githubusercontent.com/google/fonts/main/ofl/ptserif/PT_Serif-Web-Italic.ttf",
    "PTSerif-BI": "https://raw.githubusercontent.com/google/fonts/main/ofl/ptserif/PT_Serif-Web-BoldItalic.ttf",
}

print("Скачиваем шрифты...")
for name, url in fonts.items():
    path = FONT_DIR / f"{name}.ttf"
    if not path.exists():
        print(f"  → {name}")
        urllib.request.urlretrieve(url, path)
    else:
        print(f"  ✓ {name} (уже есть)")

# Нужна кириллица — проверяем NotoSansCJK нет, берём Noto Serif для кириллицы
# Lora и PTSerif поддерживают кириллицу
# Lora variable font — используем как regular/italic
pdfmetrics.registerFont(TTFont("Lora", str(FONT_DIR / "Lora-R.ttf")))
pdfmetrics.registerFont(TTFont("Lora-Italic", str(FONT_DIR / "Lora-I.ttf")))
# PTSerif
pdfmetrics.registerFont(TTFont("PTSerif", str(FONT_DIR / "PTSerif-R.ttf")))
pdfmetrics.registerFont(TTFont("PTSerif-Bold", str(FONT_DIR / "PTSerif-B.ttf")))
pdfmetrics.registerFont(TTFont("PTSerif-Italic", str(FONT_DIR / "PTSerif-I.ttf")))
pdfmetrics.registerFont(TTFont("PTSerif-BoldItalic", str(FONT_DIR / "PTSerif-BI.ttf")))
# NotoSerif из системы — для bold/bolditalic Lora (variable font не всегда поддерживает bold через wght)
pdfmetrics.registerFont(TTFont("Lora-Bold", "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Lora-BoldItalic", "/usr/share/fonts/truetype/noto/NotoSerif-BoldItalic.ttf"))

pdfmetrics.registerFontFamily("Lora",
    normal="Lora", bold="Lora-Bold",
    italic="Lora-Italic", boldItalic="Lora-BoldItalic")

print("Шрифты зарегистрированы.")

# ─── Цвета ───────────────────────────────────────────────────────────────────
BG_LIGHT   = HexColor("#FAFAF8")
BLACK      = HexColor("#000000")
GOLD       = HexColor("#C8A96E")
GOLD_DARK  = HexColor("#A08040")
WHITE      = HexColor("#FFFFFF")
GRAY_TEXT  = HexColor("#4A4A4A")
CARD_BG    = HexColor("#F2EFE8")  # чуть теплее фона для карточки
CARD_BG2   = HexColor("#EDE9E0")
DIVIDER    = HexColor("#D4C99A")

W, H = A4  # 595.28 x 841.89 pt

# ─── Хелперы ─────────────────────────────────────────────────────────────────

def set_color(c, color):
    r, g, b = color.red, color.green, color.blue
    c.setFillColorRGB(r, g, b)

def set_stroke(c, color):
    r, g, b = color.red, color.green, color.blue
    c.setStrokeColorRGB(r, g, b)

def draw_page_bg(c, color=BG_LIGHT):
    c.saveState()
    set_color(c, color)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.restoreState()

def gold_line(c, x, y, width, thickness=0.8):
    c.saveState()
    set_stroke(c, GOLD)
    c.setLineWidth(thickness)
    c.line(x, y, x + width, y)
    c.restoreState()

def gold_ornament(c, cx, y, half_w=80):
    """Тонкий орнамент: линия — ромб — линия"""
    c.saveState()
    set_stroke(c, GOLD)
    c.setLineWidth(0.6)
    # Левая линия
    c.line(cx - half_w, y, cx - 8, y)
    # Правая линия
    c.line(cx + 8, y, cx + half_w, y)
    # Ромб по центру
    c.setFillColorRGB(GOLD.red, GOLD.green, GOLD.blue)
    size = 4
    path = c.beginPath()
    path.moveTo(cx, y + size)
    path.lineTo(cx + size, y)
    path.lineTo(cx, y - size)
    path.lineTo(cx - size, y)
    path.close()
    c.drawPath(path, fill=1, stroke=0)
    c.restoreState()

def wrapped_text(c, text, x, y, max_width, font, size, leading, color=GRAY_TEXT):
    """Простой враппинг текста."""
    c.saveState()
    c.setFont(font, size)
    set_color(c, color)

    words = text.split()
    line = ""
    line_y = y
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, font, size) <= max_width:
            line = test
        else:
            if line:
                c.drawString(x, line_y, line)
                line_y -= leading
            line = word
    if line:
        c.drawString(x, line_y, line)
        line_y -= leading
    c.restoreState()
    return line_y  # возвращаем y после последней строки

def centered_text(c, text, y, font, size, color=WHITE):
    c.saveState()
    c.setFont(font, size)
    set_color(c, color)
    c.drawCentredString(W / 2, y, text)
    c.restoreState()

def right_text(c, text, x, y, font, size, color=GRAY_TEXT):
    c.saveState()
    c.setFont(font, size)
    set_color(c, color)
    c.drawRightString(x, y, text)
    c.restoreState()

# ─── СТРАНИЦА 1: ОБЛОЖКА ─────────────────────────────────────────────────────

def page_cover(c):
    draw_page_bg(c, BLACK)

    # Верхний орнамент
    gold_ornament(c, W / 2, H - 45, half_w=120)

    # Тонкая рамка
    c.saveState()
    set_stroke(c, GOLD_DARK)
    c.setLineWidth(0.5)
    margin = 18
    c.rect(margin, margin, W - 2 * margin, H - 2 * margin, fill=0, stroke=1)
    c.restoreState()

    # Декоративные горизонтальные линии вверху
    gold_line(c, 40, H - 70, W - 80, thickness=0.4)
    gold_line(c, 40, H - 74, W - 80, thickness=0.4)

    # МИРНЫЙ ВОИН — главный заголовок
    centered_text(c, "МИРНЫЙ ВОИН", H - 160, "Lora-Bold", 54, GOLD)

    # Орнамент под заголовком
    gold_ornament(c, W / 2, H - 195, half_w=100)

    # Пробуждение
    centered_text(c, "Пробуждение", H - 235, "Lora-Italic", 32, WHITE)

    # Вторая пара линий
    gold_line(c, 40, H - 265, W - 80, thickness=0.4)
    gold_line(c, 40, H - 269, W - 80, thickness=0.4)

    # Подпись в середине
    centered_text(c, "Навигатор по системе персонализированных книг", H - 330, "PTSerif", 11, HexColor("#888880"))
    centered_text(c, "для мужчин на пути к результату", H - 348, "PTSerif", 11, HexColor("#888880"))

    # Большой декоративный элемент — вертикальный акцент
    c.saveState()
    set_stroke(c, GOLD_DARK)
    c.setLineWidth(0.3)
    for i in range(5):
        yy = H / 2 - 30 + i * 18
        c.line(W / 2 - 60, yy, W / 2 + 60, yy)
    c.restoreState()

    # 5 СЕГМЕНТОВ
    centered_text(c, "5 СЕГМЕНТОВ", H / 2 - 20, "Lora-Bold", 20, GOLD)
    centered_text(c, "· Одна система · Один стандарт ·", H / 2 - 46, "PTSerif-Italic", 12, HexColor("#888880"))

    # Нижний блок
    gold_line(c, 40, 110, W - 80, thickness=0.4)
    gold_line(c, 40, 106, W - 80, thickness=0.4)

    centered_text(c, "Навигатор по 5 сегментам  ·  2026", 82, "PTSerif", 10, HexColor("#666660"))
    centered_text(c, "СПАРТА  |  МИРНЫЙ ВОИН", 58, "Lora-Bold", 11, GOLD)

    # Нижний орнамент
    gold_ornament(c, W / 2, 36, half_w=80)


# ─── СТРАНИЦА 2: ВВОДНАЯ ────────────────────────────────────────────────────

def page_intro(c):
    draw_page_bg(c)

    # Шапка
    gold_line(c, 40, H - 40, W - 80, thickness=0.5)
    c.setFont("PTSerif", 8)
    set_color(c, HexColor("#999990"))
    c.drawString(40, H - 32, "МИРНЫЙ ВОИН · ПРОБУЖДЕНИЕ")
    c.drawRightString(W - 40, H - 32, "НАВИГАТОР ПО СЕГМЕНТАМ")
    gold_line(c, 40, H - 42, W - 80, thickness=0.5)

    # Заголовок
    c.setFont("Lora-Bold", 28)
    set_color(c, BLACK)
    c.drawString(50, H - 110, "Как устроена система")

    # Золотая линия под заголовком
    gold_line(c, 50, H - 122, 200, thickness=1.5)

    # Основной текст
    intro_text = (
        "После прохождения квиза каждый мужчина получает "
        "персонализированную книгу под его запрос. "
        "5 сегментов — 5 книг. Одна система. Один стандарт."
    )
    c.saveState()
    c.setFont("PTSerif", 13)
    set_color(c, GRAY_TEXT)
    max_w = W - 100
    x_text = 50
    y_text = H - 155

    words = intro_text.split()
    line = ""
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, "PTSerif", 13) <= max_w:
            line = test
        else:
            c.drawString(x_text, y_text, line)
            y_text -= 22
            line = word
    if line:
        c.drawString(x_text, y_text, line)
        y_text -= 22
    c.restoreState()

    # Воронка
    funnel_y = H - 310
    c.setFont("Lora-Bold", 12)
    set_color(c, BLACK)
    c.drawString(50, funnel_y + 30, "Воронка:")
    gold_line(c, 50, funnel_y + 20, 80, thickness=1)

    steps = [
        ("КВИЗ", "Мужчина проходит 5 вопросов"),
        ("СЕГМЕНТАЦИЯ", "Алгоритм определяет тип запроса"),
        ("КНИГА", "Персонализированная лид-магнитная книга"),
        ("TELEGRAM-ЦЕПОЧКА", "Серия касаний по теме сегмента"),
        ("ЗВОНОК", "Созвон с куратором"),
        ("МВ ТРЕНИНГ", "Приглашение на программу"),
    ]

    step_x = 50
    step_y = funnel_y - 5
    box_h = 38
    box_gap = 8

    for i, (title, desc) in enumerate(steps):
        # Фон шага
        c.saveState()
        if i == 0:
            set_color(c, BLACK)
            text_col = GOLD
            desc_col = HexColor("#AAAAAA")
        elif i == len(steps) - 1:
            set_color(c, GOLD_DARK)
            text_col = WHITE
            desc_col = HexColor("#F0E8D0")
        else:
            set_color(c, CARD_BG2)
            text_col = GOLD_DARK
            desc_col = GRAY_TEXT

        bx = step_x
        by = step_y - box_h
        bw = W - 100

        c.rect(bx, by, bw, box_h, fill=1, stroke=0)

        # Левый золотой акцент
        if i not in (0, len(steps) - 1):
            set_color(c, GOLD)
            c.rect(bx, by, 4, box_h, fill=1, stroke=0)

        c.restoreState()

        # Номер + название
        c.saveState()
        c.setFont("Lora-Bold", 10)
        set_color(c, text_col)
        c.drawString(step_x + 14, step_y - 14, f"{i+1}.  {title}")

        c.setFont("PTSerif", 9)
        set_color(c, desc_col)
        c.drawString(step_x + 14, step_y - 27, desc)
        c.restoreStore = None
        c.restoreState()

        # Разделитель между шагами (кроме последнего)
        if i < len(steps) - 1:
            arrow_x = W / 2
            arrow_y = step_y - box_h
            c.saveState()
            set_color(c, GOLD)
            # Нарисовать маленький треугольник-стрелку
            path = c.beginPath()
            path.moveTo(arrow_x - 6, arrow_y)
            path.lineTo(arrow_x + 6, arrow_y)
            path.lineTo(arrow_x, arrow_y - box_gap + 1)
            path.close()
            c.drawPath(path, fill=1, stroke=0)
            c.restoreState()

        step_y -= box_h + box_gap

    # Подвал
    gold_line(c, 40, 35, W - 80, thickness=0.5)
    c.setFont("PTSerif", 8)
    set_color(c, HexColor("#AAAAAA"))
    c.drawCentredString(W / 2, 22, "СПАРТА  |  МИРНЫЙ ВОИН  |  spartamv.ru")


# ─── ДАННЫЕ СЕГМЕНТОВ ────────────────────────────────────────────────────────

segments = [
    {
        "num": "1",
        "name": "СТЕНА",
        "pct": "48%",
        "state": "«Знаю что делать — и всё равно торможу»",
        "ch1": "Буксую — и знаю почему. Не помогает",
        "pains": [
            "Топчусь на месте несмотря на понимание",
            "Начинаю — бросаю",
            "Устал объяснять себе, почему снова не сделал",
            "Злюсь на себя, но это не двигает",
        ],
        "tone": "Прямой, честный, без лекций — ПРОВОДНИК 70% / ВЫЗОВ 30%",
        "cta": "Проверить, подходит ли мне Мирный Воин",
        "url": "spartamv.ru",
    },
    {
        "num": "2",
        "name": "ЯМА",
        "pct": "8%",
        "state": "«Всё плохо. Нет опоры. Непонятно с чего начать»",
        "ch1": "Когда дна не видно — это не конец. Это точка",
        "pains": [
            "Потеря ориентиров",
            "Ощущение, что не справляюсь",
            "Нет мужчины рядом, кто понял бы",
            "Стыдно признать, что плохо",
        ],
        "tone": "Мягкий, опора, не жалость — ПРОВОДНИК 90%",
        "cta": "Разобрать мой узел",
        "url": "spartamv.ru",
    },
    {
        "num": "3",
        "name": "ПЛАТО",
        "pct": "37%",
        "state": "«Всё работает. Скучно. Непонятно куда дальше»",
        "ch1": "Система работает. Ты — нет",
        "pains": [
            "Всё есть, но нет огня",
            "Устал от своей же системы",
            "Хочу большего, но не знаю чего",
            "Результаты есть — интерес пропал",
        ],
        "tone": "Равный, уважение к достигнутому — ПРОВОДНИК 75% / ВЫЗОВ 25%",
        "cta": "Разобрать систему и перегруз",
        "url": "spartamv.ru",
    },
    {
        "num": "4",
        "name": "ПУСТОТА",
        "pct": "7%",
        "state": "«У меня всё есть. Кроме ответа — зачем»",
        "ch1": "Деньги пришли. Смысл — нет",
        "pains": [
            "Пустота при наличии всего",
            "Достигаю — и ничего не чувствую",
            "Огонь погас",
            "Успех без смысла — победа в пустой игре",
        ],
        "tone": "Тихий, глубокий, философский без пафоса — ПРОВОДНИК 90%",
        "cta": "Запросить личный разбор",
        "url": "spartamv.ru",
    },
    {
        "num": "5",
        "name": "НЕ УВЕРЕН",
        "pct": "смешанный",
        "state": "«Ответы пересекаются — не могу определить главное»",
        "ch1": "Смешанный запрос — это нормальная точка входа",
        "pains": [
            "Не могу понять, чего именно не хватает",
            "Несколько проблем сразу — не знаю с чего начать",
            "Не знаю — усталость, кризис или временная полоса?",
        ],
        "tone": "Открытый, исследовательский, братский — ПРОВОДНИК 85%",
        "cta": "Уточнить маршрут",
        "url": "spartamv.ru",
    },
]


# ─── СТРАНИЦЫ СЕГМЕНТОВ (3–7) ────────────────────────────────────────────────

def page_segment(c, seg, page_num):
    draw_page_bg(c)

    # Шапка
    gold_line(c, 40, H - 40, W - 80, thickness=0.5)
    c.setFont("PTSerif", 8)
    set_color(c, HexColor("#999990"))
    c.drawString(40, H - 32, "МИРНЫЙ ВОИН · ПРОБУЖДЕНИЕ")
    c.drawRightString(W - 40, H - 32, f"СЕГМЕНТ {seg['num']} / 5")
    gold_line(c, 40, H - 42, W - 80, thickness=0.5)

    # Декоративный элемент убран — конфликтовал с текстом

    # Название сегмента
    c.setFont("Lora-Bold", 36)
    set_color(c, GOLD)
    c.drawString(50, H - 105, seg["name"])

    # Процент справа
    c.saveState()
    c.setFont("Lora-Bold", 22)
    set_color(c, GOLD_DARK)
    pct_w = c.stringWidth(seg["pct"], "Lora-Bold", 22)
    c.drawString(W - 50 - pct_w, H - 90, seg["pct"])
    c.setFont("PTSerif", 9)
    set_color(c, HexColor("#888888"))
    c.drawString(W - 50 - pct_w, H - 103, "аудитории")
    c.restoreState()

    # Линия-разделитель
    gold_line(c, 50, H - 118, W - 100, thickness=1)

    # Состояние читателя
    c.setFont("PTSerif-Italic", 13)
    set_color(c, GRAY_TEXT)
    c.drawString(50, H - 140, seg["state"])

    # Глава 1
    cur_y = H - 178
    c.setFont("PTSerif", 9)
    set_color(c, GOLD_DARK)
    c.drawString(50, cur_y, "ГЛАВА 1")
    cur_y -= 18

    c.setFont("Lora-Bold", 14)
    set_color(c, BLACK)
    # Враппинг заголовка главы
    max_w = W - 100
    words = seg["ch1"].split()
    line = ""
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, "Lora-Bold", 14) <= max_w:
            line = test
        else:
            c.drawString(50, cur_y, line)
            cur_y -= 20
            line = word
    if line:
        c.drawString(50, cur_y, line)
        cur_y -= 20

    cur_y -= 12

    # Боли
    gold_line(c, 50, cur_y + 8, W - 100, thickness=0.4)
    cur_y -= 6

    c.setFont("PTSerif", 9)
    set_color(c, GOLD_DARK)
    c.drawString(50, cur_y, "КЛЮЧЕВЫЕ БОЛИ")
    cur_y -= 18

    for pain in seg["pains"]:
        # Маркер
        c.saveState()
        set_color(c, GOLD)
        c.circle(58, cur_y + 4, 2.5, fill=1, stroke=0)
        c.restoreState()

        # Текст боли с враппингом
        c.setFont("PTSerif", 11)
        set_color(c, GRAY_TEXT)
        max_w_pain = W - 130
        words_p = pain.split()
        line_p = ""
        first_line = True
        for word in words_p:
            test = (line_p + " " + word).strip()
            if c.stringWidth(test, "PTSerif", 11) <= max_w_pain:
                line_p = test
            else:
                x_start = 68 if first_line else 68
                c.drawString(x_start, cur_y, line_p)
                cur_y -= 16
                first_line = False
                line_p = word
        if line_p:
            c.drawString(68, cur_y, line_p)
            cur_y -= 16
        cur_y -= 4

    cur_y -= 10

    # Тон
    gold_line(c, 50, cur_y + 8, W - 100, thickness=0.4)
    cur_y -= 6

    c.setFont("PTSerif", 9)
    set_color(c, GOLD_DARK)
    c.drawString(50, cur_y, "ТОН КНИГИ")
    cur_y -= 18

    # Враппинг тона
    c.setFont("PTSerif-Italic", 11)
    set_color(c, GRAY_TEXT)
    words_t = seg["tone"].split()
    line_t = ""
    for word in words_t:
        test = (line_t + " " + word).strip()
        if c.stringWidth(test, "PTSerif-Italic", 11) <= (W - 100):
            line_t = test
        else:
            c.drawString(50, cur_y, line_t)
            cur_y -= 17
            line_t = word
    if line_t:
        c.drawString(50, cur_y, line_t)
        cur_y -= 17

    cur_y -= 14

    # CTA-блок
    cta_h = 60
    cta_y = max(cur_y - cta_h - 10, 80)

    # Фон CTA
    c.saveState()
    set_color(c, BLACK)
    c.rect(50, cta_y, W - 100, cta_h, fill=1, stroke=0)

    # Золотая рамка
    set_stroke(c, GOLD)
    c.setLineWidth(0.8)
    c.rect(50, cta_y, W - 100, cta_h, fill=0, stroke=1)

    # CTA текст
    c.setFont("PTSerif", 9)
    set_color(c, HexColor("#AAAAAA"))
    c.drawString(64, cta_y + cta_h - 16, "ЧТО ПОЛУЧАЕТ ЧИТАТЕЛЬ:")

    c.setFont("Lora-Bold", 12)
    set_color(c, GOLD)
    cta_text = f"«{seg['cta']}»"
    cta_w = c.stringWidth(cta_text, "Lora-Bold", 12)
    c.drawString(64, cta_y + cta_h - 34, cta_text)

    c.setFont("PTSerif", 10)
    set_color(c, WHITE)
    c.drawString(64, cta_y + 14, f">>  {seg['url']}")
    c.restoreState()

    # Подвал
    gold_line(c, 40, 35, W - 80, thickness=0.5)
    c.setFont("PTSerif", 8)
    set_color(c, HexColor("#AAAAAA"))
    c.drawCentredString(W / 2, 22, "СПАРТА  |  МИРНЫЙ ВОИН  |  spartamv.ru")


# ─── ФИНАЛЬНАЯ СТРАНИЦА ───────────────────────────────────────────────────────

def page_final(c):
    draw_page_bg(c, BLACK)

    # Рамка
    c.saveState()
    set_stroke(c, GOLD_DARK)
    c.setLineWidth(0.5)
    c.rect(18, 18, W - 36, H - 36, fill=0, stroke=1)
    c.restoreState()

    # Верхние линии
    gold_line(c, 40, H - 80, W - 80, thickness=0.4)
    gold_line(c, 40, H - 84, W - 80, thickness=0.4)

    # Орнамент вверху
    gold_ornament(c, W / 2, H - 55, half_w=100)

    # Главный слоган
    c.saveState()
    c.setFont("Lora-Bold", 26)
    set_color(c, WHITE)
    # Три строки
    lines_final = [
        "Не ещё один курс.",
        "Среда, где слово",
        "проверяется делом.",
    ]
    y_f = H - 160
    for ln in lines_final:
        c.drawCentredString(W / 2, y_f, ln)
        y_f -= 38
    c.restoreState()

    # Линии после слогана
    gold_line(c, 40, y_f + 10, W - 80, thickness=0.4)
    gold_line(c, 40, y_f + 6, W - 80, thickness=0.4)

    # Описание
    y_f -= 20
    desc_lines = [
        "Мирный Воин — программа для мужчин,",
        "которые хотят результата без потери себя.",
    ]
    c.setFont("PTSerif-Italic", 13)
    set_color(c, HexColor("#888880"))
    for dl in desc_lines:
        c.drawCentredString(W / 2, y_f, dl)
        y_f -= 22

    y_f -= 30

    # Сегменты кратко
    seg_names = ["СТЕНА", "ЯМА", "ПЛАТО", "ПУСТОТА", "НЕ УВЕРЕН"]
    c.setFont("Lora-Bold", 10)
    set_color(c, GOLD_DARK)
    total_w = 0
    for sn in seg_names:
        total_w += c.stringWidth(sn, "Lora-Bold", 10) + 20
    total_w -= 20

    sx = (W - total_w) / 2
    for i, sn in enumerate(seg_names):
        sw = c.stringWidth(sn, "Lora-Bold", 10)
        c.drawString(sx, y_f, sn)
        sx += sw + 20
        if i < len(seg_names) - 1:
            c.setFont("PTSerif", 8)
            set_color(c, GOLD_DARK)
            c.drawString(sx - 14, y_f + 1, "·")
            c.setFont("Lora-Bold", 10)
            set_color(c, GOLD_DARK)

    # Нижний блок
    gold_line(c, 40, 120, W - 80, thickness=0.5)

    # URL
    c.setFont("Lora-Bold", 20)
    set_color(c, GOLD)
    c.drawCentredString(W / 2, 88, "spartamv.ru")

    gold_ornament(c, W / 2, 68, half_w=80)

    c.setFont("Lora-Bold", 11)
    set_color(c, HexColor("#666660"))
    c.drawCentredString(W / 2, 46, "СПАРТА  |  МИРНЫЙ ВОИН")

    gold_line(c, 40, 36, W - 80, thickness=0.4)
    gold_line(c, 40, 32, W - 80, thickness=0.4)


# ─── СБОРКА PDF ───────────────────────────────────────────────────────────────

print(f"\nСобираем PDF: {OUTPUT_PATH}")
c = canvas.Canvas(OUTPUT_PATH, pagesize=A4)
c.setTitle("Мирный Воин. Пробуждение — Каталог сегментов")
c.setAuthor("Perplexity Computer")

# Стр. 1 — Обложка
page_cover(c)
c.showPage()

# Стр. 2 — Введение
page_intro(c)
c.showPage()

# Стр. 3–7 — Сегменты
for i, seg in enumerate(segments):
    page_segment(c, seg, i + 3)
    c.showPage()

# Стр. 8 — Финальная
page_final(c)
c.showPage()

c.save()

# ─── Результат ────────────────────────────────────────────────────────────────
file_size = os.path.getsize(OUTPUT_PATH)
print(f"\n✓ PDF создан успешно!")
print(f"  Страниц: 8 (обложка + введение + 5 сегментов + финал)")
print(f"  Размер: {file_size / 1024:.1f} KB")
print(f"  Путь: {OUTPUT_PATH}")
