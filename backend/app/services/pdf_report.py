"""
PDF Security Report generator.

Layout: Arabic section first (RTL), then English section (LTR).
Font: FreeSerif (bundled with freefont-ttf, supports Arabic + Latin).
Uses arabic-reshaper + python-bidi for correct Arabic glyph rendering.
"""

import io
from pathlib import Path
from typing import Any

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

_FONT_PATH = Path("/usr/share/fonts/truetype/freefont/FreeSerif.ttf")
_FONT_BOLD_PATH = Path("/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf")
_FONT_NAME = "FreeSerif"
_FONT_BOLD = "FreeSerifBold"

_fonts_registered = False


def _ensure_fonts() -> None:
    global _fonts_registered
    if _fonts_registered:
        return
    pdfmetrics.registerFont(TTFont(_FONT_NAME, str(_FONT_PATH)))
    pdfmetrics.registerFont(TTFont(_FONT_BOLD, str(_FONT_BOLD_PATH)))
    _fonts_registered = True


def _ar(text: str) -> str:
    """Reshape + bidi-reorder Arabic text for correct PDF rendering."""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


_BRAND_BLUE = colors.HexColor("#0369a1")
_PASS_GREEN = colors.HexColor("#16a34a")
_FAIL_RED = colors.HexColor("#dc2626")
_WARN_ORANGE = colors.HexColor("#d97706")
_LIGHT_GREY = colors.HexColor("#f1f5f9")


def _styles() -> dict[str, ParagraphStyle]:
    _ensure_fonts()
    base = getSampleStyleSheet()
    return {
        "title_ar": ParagraphStyle(
            "title_ar",
            fontName=_FONT_BOLD,
            fontSize=18,
            leading=28,
            alignment=2,  # right
            textColor=_BRAND_BLUE,
        ),
        "title_en": ParagraphStyle(
            "title_en",
            fontName=_FONT_BOLD,
            fontSize=18,
            leading=28,
            alignment=0,  # left
            textColor=_BRAND_BLUE,
        ),
        "heading_ar": ParagraphStyle(
            "heading_ar",
            fontName=_FONT_BOLD,
            fontSize=13,
            leading=20,
            alignment=2,
            textColor=_BRAND_BLUE,
        ),
        "heading_en": ParagraphStyle(
            "heading_en",
            fontName=_FONT_BOLD,
            fontSize=13,
            leading=20,
            alignment=0,
            textColor=_BRAND_BLUE,
        ),
        "body_ar": ParagraphStyle(
            "body_ar",
            fontName=_FONT_NAME,
            fontSize=11,
            leading=18,
            alignment=2,
        ),
        "body_en": ParagraphStyle(
            "body_en",
            fontName=_FONT_NAME,
            fontSize=11,
            leading=18,
            alignment=0,
        ),
        "small_ar": ParagraphStyle(
            "small_ar",
            fontName=_FONT_NAME,
            fontSize=9,
            leading=14,
            alignment=2,
            textColor=colors.grey,
        ),
        "small_en": ParagraphStyle(
            "small_en",
            fontName=_FONT_NAME,
            fontSize=9,
            leading=14,
            alignment=0,
            textColor=colors.grey,
        ),
    }


def _score_colour(score: int) -> colors.Color:
    if score >= 80:
        return _PASS_GREEN
    if score >= 60:
        return _WARN_ORANGE
    return _FAIL_RED


def _check_row_ar(label: str, passed: bool) -> list:
    mark = "✓" if passed else "✗"
    colour = _PASS_GREEN if passed else _FAIL_RED
    status_ar = _ar("نجح") if passed else _ar("فشل")
    return [
        Paragraph(_ar(label), _styles()["body_ar"]),
        Paragraph(f'<font color="{colour.hexval()}">{mark} {status_ar}</font>',
                  _styles()["body_ar"]),
    ]


def _check_row_en(label: str, passed: bool) -> list:
    mark = "✓" if passed else "✗"
    colour = _PASS_GREEN if passed else _FAIL_RED
    status_en = "Pass" if passed else "Fail"
    return [
        Paragraph(label, _styles()["body_en"]),
        Paragraph(f'<font color="{colour.hexval()}">{mark} {status_en}</font>',
                  _styles()["body_en"]),
    ]


_TABLE_STYLE = TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), _LIGHT_GREY),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ("FONTNAME", (0, 0), (-1, -1), _FONT_NAME),
    ("FONTSIZE", (0, 0), (-1, -1), 11),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _LIGHT_GREY]),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
])


def generate_pdf_report(domain: str, report: dict[str, Any]) -> bytes:
    """
    Generate a bilingual PDF report.  Arabic section appears first.

    Args:
        domain: The scanned domain (used in headers only — no raw IPs).
        report: Sanitised trust report dict from compute_trust_report().

    Returns:
        PDF bytes.
    """
    _ensure_fonts()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    s = _styles()
    story = []

    score = report.get("trust_score", 0)
    level = report.get("trust_level", "low")
    checks = report.get("checks", {})
    recs = report.get("recommendations", [])

    score_colour = _score_colour(score)

    level_ar = {
        "high": "موثوق",
        "good": "جيد",
        "medium": "متوسط",
        "low": "خطر",
    }.get(level, level)

    level_en = {
        "high": "Trusted",
        "good": "Good",
        "medium": "Medium",
        "low": "Risky",
    }.get(level, level)

    # ── Arabic section ────────────────────────────────────────────────────────

    story.append(Paragraph(_ar("تقرير أمان الموقع"), s["title_ar"]))
    story.append(Paragraph(_ar(f"النطاق: {domain}"), s["body_ar"]))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        _ar(f"درجة الثقة: ")
        + f'<font color="{score_colour.hexval()}"><b>{score}/100</b></font>'
        + " — " + _ar(level_ar),
        s["heading_ar"],
    ))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph(_ar("فحوصات الأمان"), s["heading_ar"]))

    ar_check_data = [
        [Paragraph(_ar("الفحص"), s["heading_ar"]),
         Paragraph(_ar("النتيجة"), s["heading_ar"])],
    ]
    check_labels_ar = {
        "https_available": "HTTPS متاح",
        "https_redirects": "إعادة التوجيه من HTTP",
        "hsts": "HSTS",
        "ssl_valid": "شهادة SSL صالحة",
        "ssl_expiry_ok": "انتهاء صلاحية SSL",
        "headers_csp": "سياسة أمان المحتوى",
        "headers_xfo": "X-Frame-Options",
        "headers_xcto": "X-Content-Type-Options",
        "headers_rp": "Referrer-Policy",
        "headers_pp": "Permissions-Policy",
        "reputation": "السمعة",
        "dns_resolves": "DNS",
    }
    for key, label in check_labels_ar.items():
        if key in checks:
            ar_check_data.append(_check_row_ar(label, checks[key]))

    if len(ar_check_data) > 1:
        t = Table(ar_check_data, colWidths=[10 * cm, 5 * cm])
        t.setStyle(_TABLE_STYLE)
        story.append(t)

    story.append(Spacer(1, 0.4 * cm))

    if recs:
        story.append(Paragraph(_ar("التوصيات"), s["heading_ar"]))
        rec_labels_ar = {
            "safe_to_browse": "آمن للتصفح",
            "safe_for_email": "آمن لإدخال البريد الإلكتروني",
            "safe_for_account": "آمن لإنشاء حساب",
            "safe_for_payment": "آمن للدفع الإلكتروني",
        }
        for rec in recs:
            label = rec_labels_ar.get(rec, rec)
            story.append(Paragraph("• " + _ar(label), s["body_ar"]))

    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=_BRAND_BLUE))
    story.append(Spacer(1, 0.5 * cm))

    # ── English section ───────────────────────────────────────────────────────

    story.append(Paragraph("Website Security Report", s["title_en"]))
    story.append(Paragraph(f"Domain: {domain}", s["body_en"]))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        f"Trust Score: "
        + f'<font color="{score_colour.hexval()}"><b>{score}/100</b></font>'
        + f" — {level_en}",
        s["heading_en"],
    ))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Security Checks", s["heading_en"]))

    en_check_data = [
        [Paragraph("Check", s["heading_en"]),
         Paragraph("Result", s["heading_en"])],
    ]
    check_labels_en = {
        "https_available": "HTTPS Available",
        "https_redirects": "HTTP→HTTPS Redirect",
        "hsts": "HSTS Header",
        "ssl_valid": "Valid SSL Certificate",
        "ssl_expiry_ok": "SSL Expiry OK",
        "headers_csp": "Content-Security-Policy",
        "headers_xfo": "X-Frame-Options",
        "headers_xcto": "X-Content-Type-Options",
        "headers_rp": "Referrer-Policy",
        "headers_pp": "Permissions-Policy",
        "reputation": "Reputation",
        "dns_resolves": "DNS Resolution",
    }
    for key, label in check_labels_en.items():
        if key in checks:
            en_check_data.append(_check_row_en(label, checks[key]))

    if len(en_check_data) > 1:
        t = Table(en_check_data, colWidths=[10 * cm, 5 * cm])
        t.setStyle(_TABLE_STYLE)
        story.append(t)

    story.append(Spacer(1, 0.4 * cm))

    if recs:
        story.append(Paragraph("Recommendations", s["heading_en"]))
        rec_labels_en = {
            "safe_to_browse": "Safe to Browse",
            "safe_for_email": "Safe for Email",
            "safe_for_account": "Safe for Account Creation",
            "safe_for_payment": "Safe for Online Payment",
        }
        for rec in recs:
            label = rec_labels_en.get(rec, rec)
            story.append(Paragraph(f"• {label}", s["body_en"]))

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "Generated by Website Trust & Security Advisor",
        s["small_en"],
    ))

    doc.build(story)
    return buf.getvalue()
