from __future__ import annotations

import re
import math
import os
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, PageTemplate, PageBreak, Spacer,
    Paragraph, Table, TableStyle, Preformatted, KeepTogether, HRFlowable,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "CloudNotes_Project_Report.md"
OUTPUT = ROOT / "CloudNotesProjectReport.pdf"

# Find logo in assets or diagrams
LOGO = ROOT / "assets" / "lpu_logo.png"
if not LOGO.exists():
    LOGO = ROOT / "diagrams" / "lpu_logo.png"

PAGE_W, PAGE_H = A4
LEFT = RIGHT = 19 * mm
TOP = 20 * mm
BOTTOM = 18 * mm
CONTENT_W = PAGE_W - LEFT - RIGHT

# Formal academic palette: neutral charcoals, crisp white, and subtle light grays.
CHARCOAL_DARK = colors.HexColor("#1A1A1A")
CHARCOAL_HEADER = colors.HexColor("#262626")
TEXT_MUTED = colors.HexColor("#555555")
BORDER_LIGHT = colors.HexColor("#CCCCCC")
ROW_ALT = colors.HexColor("#F8F9FA")
WHITE = colors.white
INK = colors.HexColor("#1A1A1A")

# Cross-platform font registration
def setup_fonts():
    win_fonts = Path("C:/Windows/Fonts")
    linux_serif = Path("/usr/share/fonts/truetype/liberation")
    linux_mono = Path("/usr/share/fonts/truetype/dejavu")

    # 1. Register Serif (Times New Roman)
    if (win_fonts / "times.ttf").exists():
        pdfmetrics.registerFont(TTFont("TimesNewRoman", str(win_fonts / "times.ttf")))
        pdfmetrics.registerFont(TTFont("TimesNewRoman-Bold", str(win_fonts / "timesbd.ttf")))
        pdfmetrics.registerFont(TTFont("TimesNewRoman-Italic", str(win_fonts / "timesi.ttf")))
        pdfmetrics.registerFont(TTFont("TimesNewRoman-BoldItalic", str(win_fonts / "timesbi.ttf")))
    elif (linux_serif / "LiberationSerif-Regular.ttf").exists():
        pdfmetrics.registerFont(TTFont("TimesNewRoman", str(linux_serif / "LiberationSerif-Regular.ttf")))
        pdfmetrics.registerFont(TTFont("TimesNewRoman-Bold", str(linux_serif / "LiberationSerif-Bold.ttf")))
        pdfmetrics.registerFont(TTFont("TimesNewRoman-Italic", str(linux_serif / "LiberationSerif-Italic.ttf")))
        pdfmetrics.registerFont(TTFont("TimesNewRoman-BoldItalic", str(linux_serif / "LiberationSerif-BoldItalic.ttf")))
    else:
        # Fallback to standard 14 fonts
        pass

    try:
        pdfmetrics.registerFontFamily(
            "TimesNewRoman",
            normal="TimesNewRoman",
            bold="TimesNewRoman-Bold",
            italic="TimesNewRoman-Italic",
            boldItalic="TimesNewRoman-BoldItalic",
        )
    except Exception:
        pass

    # 2. Register Monospace (CodeMono)
    if (win_fonts / "consola.ttf").exists():
        pdfmetrics.registerFont(TTFont("CodeMono", str(win_fonts / "consola.ttf")))
        if (win_fonts / "consolab.ttf").exists():
            pdfmetrics.registerFont(TTFont("CodeMono-Bold", str(win_fonts / "consolab.ttf")))
    elif (linux_mono / "DejaVuSansMono.ttf").exists():
        pdfmetrics.registerFont(TTFont("CodeMono", str(linux_mono / "DejaVuSansMono.ttf")))
        if (linux_mono / "DejaVuSansMono-Bold.ttf").exists():
            pdfmetrics.registerFont(TTFont("CodeMono-Bold", str(linux_mono / "DejaVuSansMono-Bold.ttf")))
    elif (win_fonts / "cour.ttf").exists():
        pdfmetrics.registerFont(TTFont("CodeMono", str(win_fonts / "cour.ttf")))

setup_fonts()

styles = getSampleStyleSheet()

# Cover Page Typography
styles.add(ParagraphStyle(
    "CoverUniversity", fontName="TimesNewRoman-Bold", fontSize=14.5, leading=17.5,
    textColor=colors.black, alignment=TA_CENTER, spaceAfter=1.2 * mm
))
styles.add(ParagraphStyle(
    "CoverLocation", fontName="TimesNewRoman", fontSize=12, leading=14.5,
    textColor=colors.black, alignment=TA_CENTER, spaceAfter=3 * mm
))
styles.add(ParagraphStyle(
    "CoverKicker", fontName="TimesNewRoman-Bold", fontSize=16, leading=20,
    textColor=colors.black, alignment=TA_CENTER, spaceAfter=2.2 * mm
))
styles.add(ParagraphStyle(
    "CoverTitle", fontName="TimesNewRoman-Bold", fontSize=17, leading=22,
    textColor=colors.black, alignment=TA_CENTER, spaceAfter=0
))
styles.add(ParagraphStyle(
    "CoverSubtitle", fontName="TimesNewRoman", fontSize=13.5, leading=17,
    textColor=colors.black, alignment=TA_CENTER, spaceAfter=2 * mm
))
styles.add(ParagraphStyle(
    "CoverMetaLabel", fontName="TimesNewRoman-Bold", fontSize=12, leading=15,
    textColor=colors.black, alignment=TA_LEFT
))
styles.add(ParagraphStyle(
    "CoverMetaValue", fontName="TimesNewRoman-Bold", fontSize=12, leading=15,
    textColor=colors.black, alignment=TA_LEFT
))
styles.add(ParagraphStyle(
    "CoverWordmark", fontName="TimesNewRoman", fontSize=17.5, leading=19.5,
    textColor=colors.HexColor("#262626"), alignment=TA_LEFT
))
styles.add(ParagraphStyle(
    "CoverLPUBox", fontName="TimesNewRoman-Bold", fontSize=17, leading=19,
    textColor=colors.black, alignment=TA_CENTER
))

# Headings: Formal academic hierarchy in clean black, without colored callout boxes
styles.add(ParagraphStyle(
    "ReportH1", fontName="TimesNewRoman-Bold", fontSize=16, leading=20,
    textColor=colors.black, spaceBefore=12, spaceAfter=6, keepWithNext=True,
))
styles.add(ParagraphStyle(
    "ReportH2", fontName="TimesNewRoman-Bold", fontSize=13.5, leading=17,
    textColor=colors.black, spaceBefore=9, spaceAfter=4, keepWithNext=True,
))
styles.add(ParagraphStyle(
    "ReportH2NoKeep", parent=styles["ReportH2"], keepWithNext=False,
))
styles.add(ParagraphStyle(
    "ReportH3", fontName="TimesNewRoman-Bold", fontSize=12, leading=15,
    textColor=CHARCOAL_DARK, spaceBefore=8, spaceAfter=4, keepWithNext=True,
))

# All running prose, lists, captions, and table content use strict 12 pt.
styles.add(ParagraphStyle(
    "ReportBody", fontName="TimesNewRoman", fontSize=12, leading=16.0,
    alignment=TA_JUSTIFY, textColor=INK, spaceAfter=6.5,
    allowWidows=0, allowOrphans=0,
))
styles.add(ParagraphStyle(
    "ReportBodyLeft", parent=styles["ReportBody"],
    alignment=TA_LEFT,
))
styles.add(ParagraphStyle(
    "ReportList", fontName="TimesNewRoman", fontSize=12, leading=15.8,
    alignment=TA_LEFT, textColor=INK, leftIndent=14, firstLineIndent=-10,
    spaceAfter=3.2, allowWidows=0, allowOrphans=0,
))
styles.add(ParagraphStyle(
    "ReportCell", fontName="TimesNewRoman", fontSize=12, leading=14.2,
    alignment=TA_LEFT, textColor=INK,
))
styles.add(ParagraphStyle(
    "ReportCellHeader", fontName="TimesNewRoman-Bold", fontSize=12, leading=14.2,
    alignment=TA_LEFT, textColor=WHITE,
))
styles.add(ParagraphStyle(
    "ReportCode", fontName="CodeMono", fontSize=12, leading=14.6,
    leftIndent=4, rightIndent=4, backColor=colors.HexColor("#F6F7F9"),
    borderColor=colors.HexColor("#D8D8D8"), borderWidth=0.4,
    borderPadding=6, spaceBefore=4, spaceAfter=8,
))
styles.add(ParagraphStyle(
    "ReportCaption", fontName="TimesNewRoman-Italic", fontSize=12, leading=14.5,
    textColor=colors.HexColor("#333333"), alignment=TA_CENTER, spaceBefore=4, spaceAfter=8,
))
styles.add(ParagraphStyle(
    "TOCLevel0", fontName="TimesNewRoman-Bold", fontSize=12, leading=16,
    textColor=colors.black, leftIndent=0, firstLineIndent=0, spaceBefore=4,
))
styles.add(ParagraphStyle(
    "TOCLevel1", fontName="TimesNewRoman", fontSize=12, leading=15,
    textColor=CHARCOAL_DARK, leftIndent=13, firstLineIndent=0, spaceBefore=1,
))


def normalize_text(value: str) -> str:
    swaps = {
        "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-",
        "\u2014": "-", "\u2212": "-", "\u00a0": " ",
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2192": "->",
    }
    for old, new in swaps.items():
        value = value.replace(old, new)
    return value


def inline_markup(value: str) -> str:
    value = escape(normalize_text(value))
    value = value.replace(r"\$", "$").replace("&amp;#36;", "$")
    value = value.replace("&amp;le;", "≤").replace("$\\le$", "≤").replace("&le;", "≤")
    value = value.replace("&lt;br/&gt;", "<br/>").replace("&lt;br&gt;", "<br/>").replace("&lt;br /&gt;", "<br/>")
    value = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",
                   r'<link href="\2" color="#003366"><u>\1</u></link>', value)
    value = re.sub(r"`([^`]+)`", r'<font name="CodeMono" size="12">\1</font>', value)
    value = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", value)
    return value


def parse_table_row(line: str) -> list[str]:
    raw = line.strip().strip("|")
    return [cell.strip().replace(r"\|", "|") for cell in re.split(r"(?<!\\)\|", raw)]


def choose_column_widths(rows: list[list[str]], ncols: int) -> list[float]:
    heads = [re.sub(r"[`*_]", "", c).lower() for c in rows[0]]
    joined = " ".join(heads)
    # 5-col API table: Method | Endpoint | Request Body | Status | Description
    if ncols == 5 and ("method" in joined and "endpoint" in joined):
        weights = [0.12, 0.28, 0.18, 0.14, 0.28]
    # 6-col API table fallback
    elif ncols == 6 and ("method" in joined and "endpoint" in joined):
        weights = [0.10, 0.23, 0.16, 0.11, 0.16, 0.24]
    # 4-col tech stack: Layer | Technology | Version | Purpose
    elif ncols == 4 and ("layer" in joined and "technology" in joined):
        weights = [0.18, 0.27, 0.12, 0.43]
    # 3-col alert rules: Alert Name | What It Checks | When It Fires
    elif ncols == 3 and "alert" in joined:
        weights = [0.32, 0.33, 0.35]
    # 4-col Grafana panels: Panel | Type | Metric | What It Shows
    elif ncols == 4 and "panel" in joined and "metric" in joined:
        weights = [0.15, 0.09, 0.50, 0.26]
    # 4-col risk matrix: Area | What I Implemented | Known Limitation | Future Improvement
    elif ncols == 4 and "area" in joined and ("limitation" in joined or "implemented" in joined):
        weights = [0.17, 0.27, 0.27, 0.29]
    # 4-col CO mapping: CO | Description | What I Built | How It Demonstrates
    elif ncols == 4 and ("co" in heads[0] or "course" in joined):
        weights = [0.08, 0.28, 0.32, 0.32]
    # 3-col verification: What | How | Result
    elif ncols == 3 and ("tested" in joined or "verification" in joined):
        weights = [0.20, 0.40, 0.40]
    # 2-col directory listing
    elif ncols == 2 and ("directory" in joined):
        weights = [0.28, 0.72]
    else:
        maxlens = []
        for c in range(ncols):
            candidates = [len(re.sub(r"[`*_]", "", row[c])) for row in rows if c < len(row)]
            maxlens.append(max(8, min(58, max(candidates or [8]))))
        weights = [math.sqrt(x) for x in maxlens]
    total = sum(weights)
    return [CONTENT_W * (w / total) for w in weights]


def make_table(lines: list[str]):
    parsed = [parse_table_row(line) for line in lines]
    if len(parsed) > 1 and all(re.fullmatch(r"\s*:?-{3,}:?\s*", c) for c in parsed[1]):
        parsed.pop(1)
    columns = max(len(row) for row in parsed)
    rows = [row + [""] * (columns - len(row)) for row in parsed]
    data = []
    for row_index, row in enumerate(rows):
        cell_style = styles["ReportCellHeader"] if row_index == 0 else styles["ReportCell"]
        data.append([Paragraph(inline_markup(cell), cell_style) for cell in row])
    widths = choose_column_widths(rows, columns)
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT", splitByRow=1)
    pad_h = 3.5 if columns >= 4 else 4.5
    pad_v = 3.2 if columns >= 3 else 4.0
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), CHARCOAL_HEADER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER_LIGHT),
        ("LEFTPADDING", (0, 0), (-1, -1), pad_h),
        ("RIGHTPADDING", (0, 0), (-1, -1), pad_h),
        ("TOPPADDING", (0, 0), (-1, -1), pad_v),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad_v),
    ]
    for row_idx in range(1, len(rows)):
        commands.append(("BACKGROUND", (0, row_idx), (-1, row_idx), ROW_ALT if row_idx % 2 else WHITE))
    table.setStyle(TableStyle(commands))
    return table


class ReportDoc(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(
            filename, pagesize=A4,
            leftMargin=LEFT, rightMargin=RIGHT, topMargin=TOP, bottomMargin=BOTTOM,
            title="CloudNotes: Course Project Report",
            author="Savinay Singh",
            subject="INT378: Advancements in Cloud and DevOps",
        )
        frame = Frame(LEFT, BOTTOM, CONTENT_W, PAGE_H - TOP - BOTTOM,
                      id="normal", leftPadding=0, rightPadding=0,
                      topPadding=0, bottomPadding=0)
        self.addPageTemplates(PageTemplate(id="report", frames=frame, onPage=self.draw_page))

    def draw_page(self, canvas, doc):
        if doc.page == 1:
            canvas.saveState()
            canvas.setStrokeColor(colors.HexColor("#9C9C9C"))
            canvas.setLineWidth(0.6)
            canvas.rect(8 * mm, 8 * mm, PAGE_W - 16 * mm, PAGE_H - 16 * mm, fill=0, stroke=1)
            canvas.restoreState()
            return
        canvas.saveState()
        # Running header: formal academic header with subtle rule
        canvas.setFont("TimesNewRoman-Bold", 9.5)
        canvas.setFillColor(CHARCOAL_DARK)
        canvas.drawString(LEFT, PAGE_H - 11.5 * mm, "CLOUDNOTES")
        canvas.setFont("TimesNewRoman", 9.5)
        canvas.setFillColor(TEXT_MUTED)
        canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 11.5 * mm, "INT378  |  ADVANCEMENTS IN CLOUD AND DEVOPS")
        canvas.setStrokeColor(BORDER_LIGHT)
        canvas.setLineWidth(0.5)
        canvas.line(LEFT, PAGE_H - 14.5 * mm, PAGE_W - RIGHT, PAGE_H - 14.5 * mm)
        # Footer with clear separation from body text.
        canvas.line(LEFT, 14.0 * mm, PAGE_W - RIGHT, 14.0 * mm)
        canvas.setFont("TimesNewRoman", 9.5)
        canvas.setFillColor(TEXT_MUTED)
        canvas.drawString(LEFT, 8.5 * mm, "School of Computer Science and Engineering  |  Lovely Professional University")
        canvas.setFont("TimesNewRoman-Bold", 9.5)
        canvas.setFillColor(CHARCOAL_DARK)
        canvas.drawRightString(PAGE_W - RIGHT, 8.5 * mm, f"PAGE {doc.page:02d}")
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        style_name = flowable.style.name
        if style_name not in ("ReportH1", "ReportH2", "ReportH3"):
            return
        plain = flowable.getPlainText().strip()
        if not plain or plain == "Contents":
            return
        level = {"ReportH1": 0, "ReportH2": 1, "ReportH3": 2}[style_name]
        key = f"toc-{level}-{self.page}-{abs(hash(plain))}"
        try:
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(plain, key, min(level, 2), closed=(level == 0))
        except Exception:
            pass
        if level == 0:
            self.notify("TOCEntry", (0, plain, self.page, key))


def cover_story(metadata: list[str]):
    """Create a formal LPU cover page."""
    story = []

    # Small crest at top left and printed cover page number at top right.
    small_logo = Image(str(LOGO), width=15 * mm, height=15 * mm) if LOGO.exists() else Spacer(15 * mm, 15 * mm)
    top_row = Table([[small_logo, Paragraph("1", ParagraphStyle(
        "CoverPageNumber", fontName="TimesNewRoman", fontSize=12, leading=14,
        alignment=TA_RIGHT, textColor=colors.black))]], colWidths=[22 * mm, CONTENT_W - 22 * mm],
        rowHeights=[16 * mm], hAlign="LEFT")
    top_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(top_row)
    story.append(Spacer(1, 7 * mm))

    # Project heading and title in a traditional academic style.
    story.append(Paragraph("COURSE PROJECT REPORT", styles["CoverKicker"]))
    story.append(Paragraph("ON", ParagraphStyle(
        "CoverOn", parent=styles["CoverSubtitle"], fontName="TimesNewRoman",
        fontSize=13, leading=16, spaceAfter=2 * mm)))

    title_lines = (
        "CLOUDNOTES: A CONTAINERIZED AND OBSERVABLE",
        "CLOUD-NATIVE APPLICATION WITH FULL-STACK",
        "DEVOPS AND DEVSECOPS PIPELINE",
    )
    story.append(Paragraph("<br/>".join(escape(v) for v in title_lines), styles["CoverTitle"]))
    story.append(Spacer(1, 5.5 * mm))
    story.append(Paragraph("Submitted for the course", styles["CoverSubtitle"]))
    course_code = next((m.split(":", 1)[1].strip() for m in metadata if m.startswith("Course Code:")), "INT378: Advancements in Cloud and DevOps")
    instructor = next((m.split(":", 1)[1].strip() for m in metadata if m.startswith("Course Instructor:")), "Mr. Ajay Kumar Badhan")
    story.append(Paragraph(escape(course_code), ParagraphStyle(
        "CoverCourse", parent=styles["CoverSubtitle"], fontName="TimesNewRoman-Bold",
        fontSize=12.5, leading=15, spaceAfter=1.4 * mm)))
    story.append(Paragraph("Course Instructor: " + escape(instructor), ParagraphStyle(
        "CoverInstructor", parent=styles["CoverSubtitle"], fontName="TimesNewRoman",
        fontSize=12, leading=14, spaceAfter=0)))

    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("Submitted by:", ParagraphStyle(
        "SubmittedBy", parent=styles["CoverSubtitle"], fontSize=14, leading=17,
        spaceAfter=3.5 * mm)))
    rows = [
        [Paragraph("Name:", styles["CoverMetaLabel"]), Paragraph("Savinay Singh", styles["CoverMetaValue"])],
        [Paragraph("Registration No.:", styles["CoverMetaLabel"]), Paragraph("12308126", styles["CoverMetaValue"])],
        [Paragraph("Roll No.:", styles["CoverMetaLabel"]), Paragraph("10", styles["CoverMetaValue"])],
        [Paragraph("Section:", styles["CoverMetaLabel"]), Paragraph("K3O2312", styles["CoverMetaValue"])],
    ]
    details = Table(rows, colWidths=[42 * mm, 60 * mm], hAlign="CENTER")
    details.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 2.4 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4 * mm),
    ]))
    story.append(details)
    story.append(Spacer(1, 6 * mm))

    fulfillment = (
        "Submitted in partial fulfilment of the requirements for the award of"
        "<br/>the degree of Bachelor of Technology (B.Tech.) in Computer Science and Engineering (CSE)"
    )
    story.append(Paragraph(fulfillment, ParagraphStyle(
        "CoverFulfilment", fontName="TimesNewRoman-Bold", fontSize=12, leading=16,
        textColor=colors.black, alignment=TA_CENTER, spaceAfter=6 * mm)))
    story.append(Paragraph("Submitted to:", ParagraphStyle(
        "SubmittedTo", parent=styles["CoverSubtitle"], fontSize=14, leading=17,
        spaceAfter=3 * mm)))

    # University crest and wordmark
    large_logo = Image(str(LOGO), width=38 * mm, height=38 * mm) if LOGO.exists() else Spacer(38 * mm, 38 * mm)
    wordmark_rows = []
    for letter, rest in [("L", "OVELY"), ("P", "ROFESSIONAL"), ("U", "NIVERSITY")]:
        wordmark_rows.append([Paragraph(letter, styles["CoverLPUBox"]), Paragraph(rest, styles["CoverWordmark"])])
    wordmark = Table(wordmark_rows, colWidths=[11 * mm, 48 * mm], rowHeights=[11 * mm] * 3, hAlign="LEFT")
    wordmark.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F58220")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, -1), 1),
        ("RIGHTPADDING", (0, 0), (0, -1), 1),
        ("LEFTPADDING", (1, 0), (1, -1), 3),
        ("RIGHTPADDING", (1, 0), (1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    logo_row = Table([[large_logo, wordmark]], colWidths=[42 * mm, 62 * mm], hAlign="CENTER")
    logo_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(logo_row)
    story.append(Spacer(1, 2.2 * mm))
    story.append(Paragraph("LOVELY PROFESSIONAL UNIVERSITY", styles["CoverUniversity"]))
    story.append(Paragraph("Phagwara, Punjab, India", styles["CoverLocation"]))
    session = next((m.split(":", 1)[1].strip() for m in metadata if m.startswith("Academic Session:")), "2026-2027")
    story.append(Paragraph("Academic Session: " + escape(session), ParagraphStyle(
        "CoverSession", parent=styles["CoverLocation"], fontSize=12, leading=14, spaceAfter=0)))
    story.append(PageBreak())
    return story


def parse_document():
    raw = SOURCE.read_text(encoding="utf-8")
    lines = raw.splitlines()
    metadata: list[str] = []
    while lines and lines[0].startswith("%"):
        value = lines.pop(0).lstrip("% ").strip()
        if value:
            metadata.append(value)
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].strip() == r"\newpage":
        lines.pop(0)

    story = cover_story(metadata)
    paragraph: list[str] = []
    in_code = False
    code_lines: list[str] = []
    skip_manual_toc = False
    current_section = "0"
    figure_counts: dict[str, int] = {}

    def flush_paragraph():
        if paragraph:
            combined = " ".join(normalize_text(p.strip()) for p in paragraph)
            has_long_tokens = any(len(tok) > 28 and ("/" in tok or "_" in tok or "http" in tok) for tok in combined.split())
            style = styles["ReportBodyLeft"] if has_long_tokens else styles["ReportBody"]
            story.append(Paragraph(inline_markup(combined), style))
            paragraph.clear()

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            i += 1
            continue

        if skip_manual_toc:
            if stripped == r"\newpage":
                story.append(PageBreak())
                skip_manual_toc = False
            i += 1
            continue

        if stripped == r"\newpage":
            flush_paragraph()
            if story and not isinstance(story[-1], PageBreak):
                story.append(PageBreak())
            i += 1
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            if not in_code:
                in_code = True
                code_lines = []
            else:
                code_text = "\n".join(normalize_text(x.expandtabs(2)) for x in code_lines)
                story.append(KeepTogether([Preformatted(code_text, styles["ReportCode"], maxLineLength=80)]))
                in_code = False
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if stripped.startswith("|"):
            flush_paragraph()
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            story.append(make_table(table_lines))
            story.append(Spacer(1, 5))
            continue

        image_match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", stripped)
        if image_match:
            flush_paragraph()
            alt, rel = image_match.groups()
            path = (ROOT / rel).resolve()
            if path.exists():
                image = Image(str(path))
                max_width = CONTENT_W * 0.96
                max_height = 90 * mm
                if path.name == "deployment_topology.png":
                    max_height = 70 * mm
                elif path.name == "service_component_architecture.png":
                    max_height = 65 * mm
                elif path.name == "k8s_traffic_scaling.png":
                    max_height = 90 * mm
                elif path.name == "system_architecture.png":
                    max_height = 58 * mm
                elif path.name == "terraform_aws_architecture.png":
                    max_height = 80 * mm
                elif path.name == "screenshot_app_health.png":
                    max_height = 30 * mm
                elif path.name in ("screenshot_app_home.png", "screenshot_app_created_note.png"):
                    max_height = 70 * mm
                elif path.name == "screenshot_jenkins.png":
                    max_height = 26 * mm
                elif path.name == "monitoring_telemetry_evidence.png":
                    max_height = 140 * mm
                scale = min(max_width / image.imageWidth, max_height / image.imageHeight, 1)
                image.drawWidth = image.imageWidth * scale
                image.drawHeight = image.imageHeight * scale
                image.hAlign = "CENTER"
                figure_counts[current_section] = figure_counts.get(current_section, 0) + 1
                if current_section.isdigit() and current_section != "0":
                    prefix = f"Figure {current_section}.{figure_counts[current_section]}: "
                else:
                    prefix = "Figure: "
                caption = Paragraph(escape(prefix + normalize_text(alt)), styles["ReportCaption"])
                story.append(KeepTogether([Spacer(1, 2), image, caption]))
            else:
                story.append(Paragraph(f"[Figure unavailable: {escape(rel)}]", styles["ReportCaption"]))
            i += 1
            continue

        heading = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            level, value = len(heading.group(1)), heading.group(2)
            if level == 1 and value == "Contents":
                story.append(Paragraph("Contents", styles["ReportH1"]))
                toc = TableOfContents()
                toc.levelStyles = [styles["TOCLevel0"]]
                toc.dotsMinLevel = 0
                toc.tableStyle = TableStyle([
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ])
                story.append(toc)
                skip_manual_toc = True
                i += 1
                continue
            if level == 1:
                match_num = re.match(r"^(\d+)\.", value)
                if match_num:
                    num = int(match_num.group(1))
                    current_section = str(num)
                    if num in (4, 7, 8):
                        if story and not isinstance(story[-1], PageBreak):
                            story.append(PageBreak())
                elif value == "References":
                    current_section = "R"
                    if story and not isinstance(story[-1], PageBreak):
                        story.append(PageBreak())
                elif value.startswith("Appendix"):
                    current_section = "A"
                    if story and not isinstance(story[-1], PageBreak):
                        story.append(PageBreak())
                elif value == "Executive Summary":
                    current_section = "0"
                style = styles["ReportH1"]
            elif level == 2:
                next_is_table = False
                for k in range(i + 1, min(i + 5, len(lines))):
                    if lines[k].strip():
                        if lines[k].strip().startswith("|"):
                            next_is_table = True
                        break
                style = styles["ReportH2NoKeep"] if next_is_table else styles["ReportH2"]
            else:
                style = styles["ReportH3"]
            story.append(Paragraph(inline_markup(value), style))
            i += 1
            continue

        unordered = re.match(r"^(\s*)[-*]\s+(.+)$", line)
        ordered = re.match(r"^(\s*)(\d+)\.\s+(.+)$", line)
        if unordered or ordered:
            flush_paragraph()
            match = unordered or ordered
            indent_chars = len(match.group(1).expandtabs(2))
            if ordered:
                marker = f"<b>{ordered.group(2)}.</b>&nbsp;"
                item = ordered.group(3)
            else:
                marker = "&bull;&nbsp;"
                item = unordered.group(2)
            style = ParagraphStyle(
                f"ListTmp{len(story)}", parent=styles["ReportList"],
                leftIndent=12 + min(indent_chars, 8) * 3,
            )
            story.append(KeepTogether([Paragraph(marker + inline_markup(item), style)]))
            i += 1
            continue

        if re.fullmatch(r"[-*_]{3,}", stripped):
            flush_paragraph()
            story.append(Spacer(1, 4))
            i += 1
            continue

        paragraph.append(stripped)
        i += 1

    flush_paragraph()
    if in_code and code_lines:
        story.append(KeepTogether([Preformatted("\n".join(code_lines), styles["ReportCode"], maxLineLength=80)]))
    return story


if __name__ == "__main__":
    doc = ReportDoc(str(OUTPUT))
    doc.multiBuild(parse_document(), maxPasses=6)
    print(f"Wrote {OUTPUT}")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from compress_pdf import compress_pdf
    compress_pdf(str(OUTPUT))

