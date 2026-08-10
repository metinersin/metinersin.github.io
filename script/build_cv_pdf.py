#!/usr/bin/env python3
"""Build the downloadable academic CV PDF.

The factual content is based on the former ``_pages/cv.md`` source.  The
website now links the generated file at ``output/pdf/Metin_Ersin_Arican_CV.pdf``.
Run this script from any working directory; it resolves paths relative to the
repository root.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence
from xml.sax.saxutils import escape as xml_escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "output" / "pdf" / "Metin_Ersin_Arican_CV.pdf"

PAPER = colors.HexColor("#fffefa")
INK = colors.HexColor("#262321")
MUTED = colors.HexColor("#6e6762")
LINE = colors.HexColor("#ddd5ce")
ACCENT = colors.HexColor("#a3482c")
ACCENT_DARK = colors.HexColor("#7e321e")
ACCENT_SOFT = colors.HexColor("#f6e8e1")


@dataclass(frozen=True)
class Entry:
    title: str
    organization: str
    dates: str = ""
    paragraphs: tuple[str, ...] = ()
    bullets: tuple[str, ...] = ()


def _register_font_family(
    family: str,
    regular: Path,
    bold: Path,
    italic: Path,
    bold_italic: Path,
) -> bool:
    if not all(path.exists() for path in (regular, bold, italic, bold_italic)):
        return False
    pdfmetrics.registerFont(TTFont(f"{family}-Regular", str(regular)))
    pdfmetrics.registerFont(TTFont(f"{family}-Bold", str(bold)))
    pdfmetrics.registerFont(TTFont(f"{family}-Italic", str(italic)))
    pdfmetrics.registerFont(TTFont(f"{family}-BoldItalic", str(bold_italic)))
    pdfmetrics.registerFontFamily(
        family,
        normal=f"{family}-Regular",
        bold=f"{family}-Bold",
        italic=f"{family}-Italic",
        boldItalic=f"{family}-BoldItalic",
    )
    return True


def register_fonts() -> tuple[str, str]:
    """Register Unicode font families and return (sans, serif) family names."""
    mac = Path("/System/Library/Fonts/Supplemental")
    linux = Path("/usr/share/fonts/truetype/dejavu")

    sans_ok = _register_font_family(
        "CVSans",
        mac / "Arial.ttf",
        mac / "Arial Bold.ttf",
        mac / "Arial Italic.ttf",
        mac / "Arial Bold Italic.ttf",
    ) or _register_font_family(
        "CVSans",
        linux / "DejaVuSans.ttf",
        linux / "DejaVuSans-Bold.ttf",
        linux / "DejaVuSans-Oblique.ttf",
        linux / "DejaVuSans-BoldOblique.ttf",
    )

    serif_ok = _register_font_family(
        "CVSerif",
        mac / "Georgia.ttf",
        mac / "Georgia Bold.ttf",
        mac / "Georgia Italic.ttf",
        mac / "Georgia Bold Italic.ttf",
    ) or _register_font_family(
        "CVSerif",
        linux / "DejaVuSerif.ttf",
        linux / "DejaVuSerif-Bold.ttf",
        linux / "DejaVuSerif-Italic.ttf",
        linux / "DejaVuSerif-BoldItalic.ttf",
    )

    if not sans_ok or not serif_ok:
        raise RuntimeError(
            "No supported Unicode font family was found. Install Arial/Georgia "
            "(macOS) or DejaVu Sans/Serif (Linux)."
        )
    return "CVSans", "CVSerif"


def normalize_punctuation(text: str) -> str:
    """Use portable punctuation while preserving names and Turkish glyphs."""
    return (
        text.replace("\N{EN DASH}", "-")
        .replace("\N{EM DASH}", "-")
        .replace("\N{NON-BREAKING HYPHEN}", "-")
    )


def markdown_to_reportlab(text: str) -> str:
    """Convert the small inline-Markdown subset used by the CV to RL markup."""
    text = normalize_punctuation(text)
    tokens: dict[str, str] = {}

    def stash(markup: str) -> str:
        token = f"CVTOKEN{len(tokens):04d}END"
        tokens[token] = markup
        return token

    text = text.replace(r"\*", stash("*"))

    def link_repl(match: re.Match[str]) -> str:
        label = xml_escape(match.group(1))
        href = xml_escape(match.group(2), {'"': "&quot;"})
        return stash(f'<link href="{href}" color="#7e321e"><u>{label}</u></link>')

    text = re.sub(r"\[([^]]+)]\(([^)]+)\)", link_repl, text)

    def bold_repl(match: re.Match[str]) -> str:
        return stash(f"<b>{xml_escape(match.group(1))}</b>")

    text = re.sub(r"\*\*(.+?)\*\*", bold_repl, text)

    def italic_repl(match: re.Match[str]) -> str:
        return stash(f"<i>{xml_escape(match.group(1))}</i>")

    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", italic_repl, text)
    text = xml_escape(text)
    for token, markup in tokens.items():
        text = text.replace(token, markup)
    return text


class SectionHeading(Flowable):
    """Compact section marker with a navigable PDF outline entry."""

    def __init__(self, title: str, font_name: str) -> None:
        super().__init__()
        self.title = title
        self.font_name = font_name
        self.height = 24
        self.keepWithNext = True
        self.anchor = "section-" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

    def wrap(self, available_width: float, available_height: float) -> tuple[float, float]:
        self.width = available_width
        return available_width, self.height

    def draw(self) -> None:
        canvas = self.canv
        canvas.saveState()
        canvas.bookmarkPage(self.anchor)
        canvas.addOutlineEntry(self.title, self.anchor, level=0, closed=False)
        canvas.setFillColor(ACCENT)
        canvas.roundRect(0, 5, 3, 13, 1.5, fill=1, stroke=0)
        text = canvas.beginText(10, 8)
        text.setFont(self.font_name, 8.3)
        text.setFillColor(ACCENT_DARK)
        text.setCharSpace(0.75)
        text.textOut(self.title.upper())
        canvas.drawText(text)
        label_width = pdfmetrics.stringWidth(self.title.upper(), self.font_name, 8.3)
        line_start = min(10 + label_width + 13, self.width - 16)
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.65)
        canvas.line(line_start, 11.5, self.width, 11.5)
        canvas.restoreState()


def make_styles(sans: str, serif: str) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "eyebrow": ParagraphStyle(
            "Eyebrow",
            parent=base["Normal"],
            fontName=f"{sans}-Bold",
            fontSize=7.4,
            leading=9,
            textColor=ACCENT_DARK,
            spaceAfter=3,
        ),
        "name": ParagraphStyle(
            "Name",
            parent=base["Title"],
            fontName=f"{serif}-Bold",
            fontSize=27,
            leading=30,
            textColor=INK,
            spaceAfter=1,
        ),
        "summary": ParagraphStyle(
            "Summary",
            parent=base["BodyText"],
            fontName=f"{serif}-Regular",
            fontSize=9.4,
            leading=14.1,
            textColor=colors.HexColor("#403a36"),
        ),
        "entry_title": ParagraphStyle(
            "EntryTitle",
            parent=base["Heading3"],
            fontName=f"{serif}-Bold",
            fontSize=10.6,
            leading=13,
            textColor=INK,
            spaceAfter=2.2,
        ),
        "meta": ParagraphStyle(
            "Meta",
            parent=base["Normal"],
            fontName=f"{sans}-Bold",
            fontSize=7.7,
            leading=9.4,
            textColor=MUTED,
        ),
        "meta_right": ParagraphStyle(
            "MetaRight",
            parent=base["Normal"],
            fontName=f"{sans}-Bold",
            fontSize=7.7,
            leading=9.4,
            textColor=ACCENT_DARK,
            alignment=TA_RIGHT,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName=f"{sans}-Regular",
            fontSize=8.45,
            leading=11.55,
            textColor=INK,
            spaceAfter=3.5,
        ),
        "publication": ParagraphStyle(
            "Publication",
            parent=base["BodyText"],
            fontName=f"{sans}-Regular",
            fontSize=8.55,
            leading=12.2,
            textColor=INK,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName=f"{sans}-Regular",
            fontSize=8.3,
            leading=11.35,
            textColor=INK,
        ),
        "bullet_mark": ParagraphStyle(
            "BulletMark",
            parent=base["Normal"],
            fontName=f"{sans}-Bold",
            fontSize=9,
            leading=10,
            textColor=ACCENT,
            alignment=TA_LEFT,
        ),
        "updated": ParagraphStyle(
            "Updated",
            parent=base["Normal"],
            fontName=f"{sans}-Italic",
            fontSize=7.6,
            leading=10,
            textColor=MUTED,
            alignment=TA_RIGHT,
            spaceBefore=6,
        ),
    }


def entry_flowables(
    entry: Entry,
    styles: dict[str, ParagraphStyle],
    content_width: float,
) -> KeepTogether:
    items: list[Flowable] = [
        Paragraph(markdown_to_reportlab(entry.title), styles["entry_title"]),
    ]
    if entry.organization or entry.dates:
        left = Paragraph(markdown_to_reportlab(entry.organization), styles["meta"])
        right = Paragraph(markdown_to_reportlab(entry.dates), styles["meta_right"])
        meta = Table(
            [[left, right]],
            colWidths=[content_width * 0.73, content_width * 0.27],
            hAlign="LEFT",
        )
        meta.setStyle(
            TableStyle(
                [
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        items.append(meta)
    for paragraph in entry.paragraphs:
        items.append(Paragraph(markdown_to_reportlab(paragraph), styles["body"]))
    for bullet in entry.bullets:
        items.append(bullet_row(bullet, styles, content_width, compact=True))
    items.append(Spacer(1, 5.5))
    return KeepTogether(items)


def bullet_row(
    text: str,
    styles: dict[str, ParagraphStyle],
    content_width: float,
    *,
    compact: bool = False,
) -> Table:
    table = Table(
        [
            [
                Paragraph("&#8226;", styles["bullet_mark"]),
                Paragraph(markdown_to_reportlab(text), styles["bullet"]),
            ]
        ],
        colWidths=[10, content_width - 10],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2 if compact else 3.3),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return table


def add_section(
    story: list[Flowable],
    title: str,
    sans: str,
    *,
    top_space: float = 4,
) -> None:
    if top_space:
        story.append(Spacer(1, top_space))
    story.append(SectionHeading(title, f"{sans}-Bold"))


def add_entries(
    story: list[Flowable],
    entries: Iterable[Entry],
    styles: dict[str, ParagraphStyle],
    content_width: float,
) -> None:
    for entry in entries:
        story.append(entry_flowables(entry, styles, content_width))


def add_bullet_section(
    story: list[Flowable],
    title: str,
    bullets: Sequence[str],
    sans: str,
    styles: dict[str, ParagraphStyle],
    content_width: float,
) -> None:
    add_section(story, title, sans, top_space=6)
    for bullet in bullets:
        story.append(bullet_row(bullet, styles, content_width))


def draw_page(canvas, doc, sans: str, *, first: bool) -> None:
    width, height = A4
    canvas.saveState()
    canvas.setTitle("Curriculum Vitae - Metin Ersin Arican")
    canvas.setAuthor("Metin Ersin Arican")
    canvas.setSubject("Academic curriculum vitae")
    canvas.setCreator("script/build_cv_pdf.py (ReportLab)")
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, width, height, fill=1, stroke=0)

    if not first:
        canvas.setFillColor(MUTED)
        canvas.setFont(f"{sans}-Bold", 7.3)
        canvas.drawString(doc.leftMargin, height - 22, "METIN ERSIN ARICAN")
        canvas.setFillColor(ACCENT_DARK)
        canvas.drawRightString(width - doc.rightMargin, height - 22, "CURRICULUM VITAE")
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.65)
        canvas.line(doc.leftMargin, height - 31, width - doc.rightMargin, height - 31)

    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.6)
    canvas.line(doc.leftMargin, 27, width - doc.rightMargin, 27)
    canvas.setFillColor(MUTED)
    canvas.setFont(f"{sans}-Regular", 7.1)
    canvas.drawString(doc.leftMargin, 16, "ACADEMIC CV  /  AUGUST 2026")
    canvas.drawRightString(width - doc.rightMargin, 16, f"PAGE {doc.page}")
    canvas.restoreState()


def build_story(
    styles: dict[str, ParagraphStyle],
    sans: str,
    content_width: float,
) -> list[Flowable]:
    story: list[Flowable] = []

    story.append(Paragraph("ACADEMIC CURRICULUM VITAE", styles["eyebrow"]))
    story.append(Paragraph("Metin Ersin Arıcan", styles["name"]))
    story.append(Spacer(1, 8))
    story.append(
        Table(
            [
                [
                    Paragraph(
                        markdown_to_reportlab(
                            "My research interests are model theory and mathematical logic; "
                            "formal mathematics and automated theorem proving; and visual and "
                            "category-theoretic approaches to formal languages."
                        ),
                        styles["summary"],
                    )
                ]
            ],
            colWidths=[content_width],
            hAlign="LEFT",
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), ACCENT_SOFT),
                    ("LINEBEFORE", (0, 0), (0, -1), 3, ACCENT),
                    ("LEFTPADDING", (0, 0), (-1, -1), 13),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 13),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            ),
        )
    )
    story.append(Spacer(1, 10))

    education = (
        Entry(
            "Ph.D. in Mathematics (incoming)",
            "University of Leeds",
            "Starts 2026",
            (
                "**Primary supervisor:** [Dr Pantelis Eleftheriou](https://pelefthe.github.io/)",
                "**Secondary supervisor:** [Dr Vincenzo L. Mantova](https://poisson.phc.dm.unipi.it/~mantova/index.html)",
            ),
        ),
        Entry(
            "M.Sc. in Mathematics",
            "Boğaziçi University",
            "2023-2026  ·  GPA: 4.00/4.00",
            (
                "**Thesis:** *VC-density in pairs of strongly minimal structures*",
                "**Advisor:** [Assoc. Prof. Ayhan Günaydın](https://web.bogazici.edu.tr/ayhan.gunaydin/)",
                "**Selected coursework:** O-minimal theories, applications of model theory to number theory, algebraic number theory, modern algebraic geometry, algebraic topology II, computational complexity theory, functional programming, logic for computer science, and software verification.",
            ),
        ),
        Entry(
            "B.S. in Electrical and Electronics Engineering",
            "Boğaziçi University",
            "2018-2023  ·  GPA: 3.99/4.00",
            (
                "**Senior project:** *Synchronization in several coupled van der Pol oscillators*",
                "**Advisor:** Prof. Yağmur Denizhan",
                "**Selected coursework:** Linear multivariable systems theory, chaotic dynamics, nonlinear control, signal processing, functional analysis, representation theory, algebraic topology I, measure theory, and algebra I & II.",
            ),
        ),
        Entry(
            "B.S. in Physics",
            "Boğaziçi University",
            "2018-2023  ·  GPA: 3.99/4.00",
            (
                "**Selected coursework:** Lie groups and Lie algebras, statistical mechanics, relativistic electromagnetic theory, and quantum mechanics.",
            ),
        ),
    )
    add_section(story, "Education", sans, top_space=0)
    add_entries(story, education, styles, content_width)

    research = (
        Entry(
            "Project course: Formalizing Quantifier Elimination in Lean",
            "Boğaziçi University",
            paragraphs=(
                "Collaborated with four undergraduate students and Assoc. Prof. Ayhan Günaydın on formalizing quantifier-elimination results in Lean.",
            ),
            bullets=(
                "Formalized the back-and-forth method for quantifier elimination.",
                "Applied the formalized method to prove that the theory of dense linear orders without endpoints admits quantifier elimination.",
            ),
        ),
        Entry(
            "Undergraduate Research Assistant",
            "ETH Zürich, Computer Vision Lab",
            "2021-2022",
            ("**Supervisor:** Assoc. Prof. Ender Konukoğlu",),
            (
                "Studied the spatial inductive bias of convolutional neural networks in the Deep Image Prior framework.",
                "Helped develop a training-free, image-specific neural architecture search method by formulating metrics, designing experiments, developing most of the codebase, and writing the manuscript.",
                "The work was accepted at CVPR 2022.",
            ),
        ),
        Entry(
            "Undergraduate Research Assistant",
            "Boğaziçi University, Microwave Radar and Communications Laboratory",
            "2019-2021",
            ("**Supervisor:** Assoc. Prof. Ahmet Öncü",),
            (
                "Developed graphical interfaces for programming digital circuits.",
                "Contributed to digital circuit design and verification.",
            ),
        ),
    )
    add_section(story, "Research experience", sans, top_space=5)
    add_entries(story, research[:1], styles, content_width)

    story.append(PageBreak())
    add_section(story, "Research experience (continued)", sans, top_space=0)
    add_entries(story, research[1:], styles, content_width)

    add_section(story, "Publication", sans, top_space=5)
    publication = (
        r"Metin Ersin Arıcan\*, Özgür Kara\*, G. Bredell, and Ender Konukoğlu. "
        '"ISNAS-DIP: Image-Specific Neural Architecture Search for Deep Image Prior." '
        "In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern "
        "Recognition (CVPR)*, 1960-1968, 2022. "
        "[Paper](https://openaccess.thecvf.com/content/CVPR2022/html/"
        "Arican_ISNAS-DIP_Image-Specific_Neural_Architecture_Search_for_Deep_"
        "Image_Prior_CVPR_2022_paper.html)"
    )
    publication_box = Table(
        [[Paragraph(markdown_to_reportlab(publication), styles["publication"])]],
        colWidths=[content_width],
        hAlign="LEFT",
        style=TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fbf7f3")),
                ("LINEBEFORE", (0, 0), (0, -1), 2.2, ACCENT),
                ("LEFTPADDING", (0, 0), (-1, -1), 11),
                ("RIGHTPADDING", (0, 0), (-1, -1), 11),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        ),
    )
    story.append(KeepTogether([publication_box, Spacer(1, 3), Paragraph("* Equal contribution.", styles["body"])]))

    teaching = (
        Entry(
            "Graduate Teaching Assistant",
            "Boğaziçi University",
            "2023-Present",
            (
                "MATH 412 (Introduction to Axiomatic Set Theory), MATH 411 (Introduction to Mathematical Logic), MATH 323 (Rings, Fields and Galois Theory), MATH 222 (Group Theory), MATH 201 (Linear Algebra), MATH 105 (Introduction to Finite Mathematics), MATH 102 (Calculus II), and MATH 101 (Calculus I).",
            ),
        ),
        Entry(
            "Physics Instructor",
            "TÜBİTAK",
            "2019",
            (
                "Delivered lectures and problem-solving sessions in electromagnetism, mechanics, and modern physics to nominees for Turkey's national physics olympiad team.",
            ),
        ),
    )
    add_section(story, "Teaching", sans, top_space=5)
    add_entries(story, teaching, styles, content_width)

    professional = (
        Entry(
            "Data & Machine Learning Engineer / AI Tutor",
            "Kili Technologies & Project Numina",
            "2024-2025",
            (
                "Prepared a formal mathematics dataset for training large language models on autoformalization and automated theorem proving.",
            ),
        ),
        Entry(
            "Cryptanalyst Intern",
            "TÜBİTAK BİLGEM Cryptanalysis Laboratory",
            "2022-2023",
            bullets=(
                "Prepared technical presentations and reports on linear and differential cryptanalysis of DES-like block ciphers, and implemented the algorithms from scratch in Python.",
                "Presented Grover's and Shor's algorithms and their applications to breaking RSA.",
                "Prepared reports on lattice-based cryptography and the Fiat-Shamir transform.",
            ),
        ),
        Entry(
            "R&D Intern",
            "SESTEK",
            "2021",
            bullets=(
                "Studied voice activity detection using recurrent neural networks and handcrafted features.",
                "Designed experiments and benchmarks for comparing state-of-the-art voice activity detection systems.",
            ),
        ),
    )
    add_section(story, "Professional experience", sans, top_space=5)
    add_entries(story, professional[:1], styles, content_width)

    story.append(PageBreak())
    add_section(story, "Professional experience (continued)", sans, top_space=0)
    add_entries(story, professional[1:], styles, content_width)

    workshops = (
        "**Mentor, Directed Reading Program Turkey · Jun-Aug 2024.** Mentored a third-year mathematics student at Middle East Technical University on enriched categories, abelian categories, and Mitchell's embedding theorem.",
        "**School on Formal Mathematics, Hausdorff Institute · May 2024.** Worked on a Fourier theory formalization project in Lean led by Prof. Floris van Doorn.",
        "**eCHT Homotopy Theory Course · Jan-May 2024.** Completed an online course on homotopy theory taught by Dr Jack H. Carlisle.",
        "**Participant, Directed Reading Program Turkey · Jun-Aug 2023.** Studied categorical logic and topos theory with Praneet Srivastava, wrote a report, and gave a concluding talk at Sabancı University.",
        "**Reading Program, Boğaziçi University · Apr-Sep 2022.** Studied mathematical logic and axiomatic set theory with Prof. Betül Tanbay and gave a concluding talk at Boğaziçi University.",
    )
    add_bullet_section(story, "Workshops & programs", workshops, sans, styles, content_width)

    talks = (
        "**Formal Mathematics: An Introduction · Feb 2026, Feza Gürsey Institute.** Surveyed developments at the intersection of mathematics, artificial intelligence, and formalization; compared ZFC in first-order logic with Martin-Löf type theory; and introduced the core ideas of Martin-Löf type theory.",
        "**An Introduction to Lean for Mathematicians · Dec 2024, Boğaziçi University**",
        "**O-minimal Structures and VC-Dimension · Dec 2023, Boğaziçi University**",
        "**An Introduction to Categorical Logic and Topoi · Aug 2023, Sabancı University**",
        "**Counterexamples in Topology via Ordinals & Cardinals · Dec 2022, Boğaziçi University**",
    )
    add_bullet_section(story, "Talks", talks, sans, styles, content_width)

    awards = (
        "**Graduate Scholarship, Turkish Education Foundation (TEV) · 2023-2025**",
        "**2210-E Graduate Scholarship, TÜBİTAK · 2023-2025**",
        "**2205-E Undergraduate Scholarship, TÜBİTAK · 2018-2023**",
        "**Finalist, Travel Datathon and Machine Learning Competition, Turkish Airlines · 2019.** Finalist among 75 teams.",
        "**437th place, Turkish National University Entrance Exam · 2018.** Ranked 437th among approximately two million candidates.",
        "**Silver Medal, International Physics Olympiad · 2018**",
        "**Bronze Medal, European Physics Olympiad · 2018**",
        "**Honorable Mention, Asian Physics Olympiad · 2018**",
        "**Silver Medal, Turkish Physics Olympiad · 2017**",
    )
    add_bullet_section(story, "Awards & scholarships", awards, sans, styles, content_width)
    story.append(Paragraph("Last updated: August 9, 2026.", styles["updated"]))
    return story


def build_pdf(output_path: Path = OUTPUT_PATH) -> Path:
    sans, serif = register_fonts()
    styles = make_styles(sans, serif)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=15 * mm,
        bottomMargin=14 * mm,
        title="Curriculum Vitae - Metin Ersin Arican",
        author="Metin Ersin Arican",
        subject="Academic curriculum vitae",
        creator="script/build_cv_pdf.py (ReportLab)",
        pageCompression=1,
    )
    story = build_story(styles, sans, doc.width)
    doc.build(
        story,
        onFirstPage=lambda canvas, current_doc: draw_page(
            canvas, current_doc, sans, first=True
        ),
        onLaterPages=lambda canvas, current_doc: draw_page(
            canvas, current_doc, sans, first=False
        ),
    )
    return output_path


def main() -> None:
    path = build_pdf()
    print(f"Built {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
