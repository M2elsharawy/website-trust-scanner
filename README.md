# Website Trust & Security Advisor
## مساعد تقييم أمان وموثوقية المواقع

منصة SaaS ثلاثية الطبقات لتقييم أمان المواقع وحماية المستخدمين واكتشاف الفرص التجارية الأخلاقية.

---

## الحالة الحالية

**المرحلة 0: Product Planning & Scope Lock** ✅ مكتملة — بانتظار موافقة المالك

---

## وثائق المشروع

| الملف | الوصف |
|-------|-------|
| [docs/PRD.md](docs/PRD.md) | Product Requirements Document |
| [docs/PERMISSIONS_TABLE.md](docs/PERMISSIONS_TABLE.md) | جدول الصلاحيات |
| [docs/SITE_STATUS_TABLE.md](docs/SITE_STATUS_TABLE.md) | جدول حالات الموقع |
| [docs/SCAN_POLICY_TABLE.md](docs/SCAN_POLICY_TABLE.md) | سياسة الفحص المسموح والممنوع |
| [docs/MVP1_SCOPE.md](docs/MVP1_SCOPE.md) | نطاق MVP 1 |
| [docs/SECURITY_RISKS.md](docs/SECURITY_RISKS.md) | المخاطر الأمنية والقانونية |
| [docs/OPEN_QUESTIONS.md](docs/OPEN_QUESTIONS.md) | أسئلة تحتاج موافقة المالك |

---

## طبقات المنتج

1. **Public Free Trust Check** — لأي مستخدم يريد تقييم موقع
2. **Verified Owner Security Monitoring** — لصاحب الموقع بعد إثبات الملكية
3. **Admin Lead Audit & Client Management** — لصاحب المنصة

---

## مبادئ غير قابلة للتفاوض

- لا فحص عميق بدون Authorization Record صالح
- لا payloads، لا brute force، لا bypass
- URL Safety Validator إلزامي قبل أي طلب
- لا يُخزَّن محتوى ملفات حساسة
- دعم العربية والإنجليزية من اليوم الأول
