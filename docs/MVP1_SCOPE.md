# نطاق MVP 1 — MVP 1 Scope Definition

## تعريف MVP 1

الهدف من MVP 1: منتج قابل للعرض والاختبار مع المستخدمين الأوائل.  
يجب أن يكون **آمنًا، قابلًا للتوسع، ومفيدًا فعلًا** — ليس مجرد نموذج أولي.

---

## ✅ داخل نطاق MVP 1 (IN SCOPE)

### البنية الأساسية
- [ ] هيكل المشروع (Frontend + Backend)
- [ ] إعداد TypeScript (Frontend)
- [ ] إعداد قاعدة البيانات (PostgreSQL)
- [ ] إعداد Docker / docker-compose
- [ ] نظام environment variables آمن
- [ ] API health check endpoint
- [ ] Audit Logging أساسي

### الأمان الأساسي (قبل أي فحص)
- [ ] URL Safety Validator (SSRF prevention)
- [ ] Rate Limiting (IP-based للـ Guests)
- [ ] Do Not Scan List
- [ ] Scan Policy Engine (يقرر ما إذا كان الفحص مسموحًا)
- [ ] آمان الـ headers للـ API

### Public Trust Check
- [ ] واجهة إدخال URL (عربي/إنجليزي)
- [ ] SSL basic check (valid/expired/missing)
- [ ] HTTPS enforcement check
- [ ] Security Headers (وجود/غياب — 5 headers أساسية)
- [ ] DNS reputation check (بسيط)
- [ ] Google Safe Browsing integration (أو mock provider)
- [ ] HSTS presence check
- [ ] Trust Score calculation (0–100)
- [ ] Trust Report (بسيط، مبسّط لغير التقنيين)
- [ ] توصيات الاستخدام (تصفح / بريد / حساب / دفع)
- [ ] دعم RTL/LTR
- [ ] رسائل خطأ آمنة (لا تكشف تفاصيل داخلية)
- [ ] Loading/error/empty states

### Admin Lead Audit (MVP)
- [ ] صفحة تسجيل دخول Admin (أساسية)
- [ ] لوحة Leads البسيطة
- [ ] إضافة Lead يدويًا
- [ ] تشغيل Lead Audit (نفس فحوصات Public + DNS SPF/DMARC وجود/غياب)
- [ ] Lead Score calculation
- [ ] Outreach Report template (نص مهني غير حساس)
- [ ] حالات Lead (New → Contacted → Interested → Rejected)
- [ ] Do Not Contact flag
- [ ] Audit Log للأحداث الإدارية

### نظام المستخدمين (MVP أساسي)
- [ ] تسجيل دخول Admin فقط في MVP 1
- [ ] JWT authentication
- [ ] حماية API endpoints
- [ ] Super Admin account

---

## ❌ خارج نطاق MVP 1 (OUT OF SCOPE NOW)

### ميزات مؤجلة (Phase 2+)
- تسجيل مستخدمين عاديين (Guests يمكنهم الفحص بدون حساب)
- Website Ownership Verification (DNS TXT / HTML file)
- Security Report المفصل لصاحب الموقع
- Scheduled Monitoring (تقارير دورية)
- PDF Export
- Email notifications/alerts
- CMS detection
- Exposed files check
- TLS version check
- Cipher suites analysis
- مقارنة قبل/بعد
- Agency users management
- White-label

### ميزات خارج النطاق تمامًا (لن تُبنى في القريب)
- Port scanning
- Crawling واسع
- XSS/SQL testing
- Brute force
- اشتراكات مدفوعة / Payment gateway
- White-label / multi-tenant
- API for third parties
- Mobile app
- Browser extension
- DKIM check (تعقيد عالٍ، قيمة منخفضة في MVP)
- ربط Cloudflare / GitHub مباشرة

---

## معيار اعتبار MVP 1 مكتملًا

يُعتبر MVP 1 مكتملًا إذا تحققت **جميع** البنود التالية:

1. ✅ مستخدم عادي يستطيع إدخال URL ويحصل على Trust Score خلال 10 ثوانٍ
2. ✅ التقرير لا يكشف أي معلومات قابلة للاستغلال
3. ✅ الـ URL Validator يمنع SSRF بشكل موثوق (اختبارات مكتوبة)
4. ✅ Rate Limiting يعمل على مستوى الـ IP
5. ✅ Do Not Scan List تعمل برمجيًا
6. ✅ Audit Log يسجل كل فحص
7. ✅ Admin يستطيع إضافة Lead وتشغيل Lead Audit
8. ✅ Outreach Report لا يحتوي معلومات حساسة
9. ✅ الواجهة تعمل بالعربية والإنجليزية مع RTL/LTR صحيح
10. ✅ لا توجد API keys مكشوفة في الكود أو الـ logs
11. ✅ جميع API endpoints محمية بشكل صحيح
12. ✅ المشروع يعمل بـ docker-compose بأمر واحد

---

## مؤشرات نجاح MVP 1 (KPIs)

| المؤشر | الهدف |
|--------|-------|
| وقت استجابة Trust Check | < 10 ثوانٍ |
| نسبة نجاح SSRF tests | 100% |
| دعم اللغات | عربي + إنجليزي |
| وقت تشغيل المشروع من الصفر | < 5 دقائق بـ docker-compose |
| security findings في الكود | صفر (بعد مراجعة) |

---

## ترتيب أولويات التنفيذ (Phases)

```
Phase 0: Planning (الآن) ← نحن هنا
Phase 1: Technical Design
Phase 2: Project Bootstrap
Phase 3: Core Security Foundation  ← أهم مرحلة
Phase 4: Public Trust Check MVP    ← القيمة الأساسية
Phase 5: Admin Lead Audit MVP
Phase 6: Authentication & Authorization
...
```

**ملاحظة:** المرحلة 3 (Core Security Foundation) يجب أن تكتمل قبل أي فحص فعلي.
