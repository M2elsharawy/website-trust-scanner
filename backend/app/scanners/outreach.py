"""
Outreach message generator.

Produces bilingual (Arabic + English) professional outreach messages.
Rules:
  - Never mention specific vulnerabilities, CVEs, or missing header names
  - Never include IP addresses, cert details, or raw scanner output
  - Use general improvement-area labels only
  - Tone: professional and helpful, not alarming
"""

from app.scanners.result import ScanData

# ── Improvement area labels ───────────────────────────────────────────────────

_AREA_LABELS: dict[str, dict[str, str]] = {
    "https_missing": {
        "en": "HTTPS Encryption",
        "ar": "تشفير HTTPS",
    },
    "ssl_issues": {
        "en": "SSL Certificate Management",
        "ar": "إدارة شهادة SSL",
    },
    "security_config": {
        "en": "Security Configuration",
        "ar": "إعدادات الأمان",
    },
    "secure_routing": {
        "en": "Secure Traffic Routing",
        "ar": "توجيه حركة المرور الآمنة",
    },
    "transport_policy": {
        "en": "Transport Security Policy",
        "ar": "سياسة أمان الاتصال",
    },
}


def _identify_areas(data: ScanData) -> list[str]:
    """Return up to 3 high-level improvement area keys. Never technical details."""
    areas: list[str] = []

    if not data.https.available:
        areas.append("https_missing")

    if not data.ssl.valid or data.ssl.expiry_warning:
        areas.append("ssl_issues")

    if data.headers.score < 3:
        areas.append("security_config")
    elif not data.https.hsts_present:
        areas.append("transport_policy")

    if data.https.available and not data.https.redirects_from_http:
        areas.append("secure_routing")

    return areas[:3]  # show at most 3 areas


_EN_TEMPLATE = """\
Subject: Complimentary Security Assessment — {domain}

Dear {domain} Team,

As part of our outreach program, we conducted a complimentary surface-level \
security review of {domain} and identified {count} area(s) where targeted \
improvements could strengthen your users' trust and protect your business reputation.

Areas of opportunity:
{areas_list}

Many organizations overlook these foundational security practices, which can \
directly impact customer confidence and search engine rankings.

We would welcome the opportunity to share our findings in a brief 20-minute call \
and provide a clear, prioritized improvement roadmap — at no cost.

Would you be available for a short call this week?

Best regards,
Website Trust & Security Advisors\
"""

_AR_TEMPLATE = """\
الموضوع: تقييم أمني مجاني — {domain}

عزيزي فريق {domain}،

ضمن برنامج التواصل لدينا، أجرينا مراجعة أمنية سطحية مجانية لـ {domain} وحددنا \
{count} مجال/مجالات يمكن من خلالها تحسينات موجهة تعزز ثقة مستخدميكم وتحمي سمعة عملكم.

مجالات الفرص:
{areas_list}

كثير من المؤسسات تتجاهل هذه الممارسات الأمنية الأساسية، مما قد يؤثر مباشرة \
على ثقة العملاء وترتيب محركات البحث.

يسعدنا مشاركة نتائجنا في مكالمة مدتها 20 دقيقة وتقديم خارطة تحسين واضحة \
ومرتبة حسب الأولوية — وذلك بدون أي تكلفة.

هل يناسبكم تحديد موعد مكالمة قصيرة هذا الأسبوع؟

مع أطيب التحيات،
مستشارو أمان وموثوقية المواقع\
"""


def generate_outreach(domain: str, data: ScanData) -> dict[str, object]:
    """
    Generate a bilingual outreach report.

    Returns a dict safe for the API response:
      domain, improvement_areas_en, improvement_areas_ar,
      outreach_message_en, outreach_message_ar

    Contains NO vulnerability details, IPs, cert info, or header values.
    """
    area_keys = _identify_areas(data)

    if not area_keys:
        # Site is well-secured — generic message about proactive monitoring
        area_keys = ["security_config"]

    areas_en = [_AREA_LABELS[k]["en"] for k in area_keys]
    areas_ar = [_AREA_LABELS[k]["ar"] for k in area_keys]

    count = len(area_keys)

    msg_en = _EN_TEMPLATE.format(
        domain=domain,
        count=count,
        areas_list="\n".join(f"  • {a}" for a in areas_en),
    )
    msg_ar = _AR_TEMPLATE.format(
        domain=domain,
        count=count,
        areas_list="\n".join(f"  • {a}" for a in areas_ar),
    )

    return {
        "domain": domain,
        "improvement_areas_en": areas_en,
        "improvement_areas_ar": areas_ar,
        "outreach_message_en": msg_en,
        "outreach_message_ar": msg_ar,
    }
