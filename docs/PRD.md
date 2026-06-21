# Product Requirements Document (PRD)
## Website Trust & Security Advisor — مساعد تقييم أمان وموثوقية المواقع

**Version:** 0.1 — Phase 0 Lock  
**Status:** Draft — Awaiting Owner Approval  
**Date:** 2026-06-21

---

## 1. Problem Statement

**للمستخدم العادي:**  
لا يملك المستخدم العادي أدوات بسيطة تخبره إذا كان الموقع الذي يريد زيارته، أو إدخال بياناته فيه، موثوقًا وآمنًا. المؤشرات التقنية (مثل SSL أو Security Headers) موجودة لكنها غير مفهومة بدون خبرة.

**لصاحب الموقع:**  
أصحاب المواقع — خاصة الشركات الصغيرة — لا يعرفون نقاط الضعف الأمنية في مواقعهم، ولا يتلقون تقارير مستمرة أو توصيات إصلاح عملية بلغة واضحة.

**للوكالات والمسوّقين الأمنيين:**  
لا توجد أداة تتيح اكتشاف عملاء محتملين (Leads) بناءً على مؤشرات أمنية عامة، بطريقة أخلاقية وغير تدخلية.

---

## 2. Product Vision

منصة SaaS ثلاثية الطبقات تجمع بين:
- حماية المستخدم العادي (Trust Check)
- تمكين صاحب الموقع (Security Monitoring)
- مساعدة الوكالات على اكتشاف الفرص التجارية بأخلاقية (Lead Audit)

مع الالتزام الصارم بـ:
- الفحص غير التدخلي
- منع أي استخدام هجومي
- الفصل البرمجي بين مستويات الصلاحية
- دعم العربية والإنجليزية

---

## 3. Target Users

| رمز | المستخدم | الوصف |
|-----|----------|-------|
| G | **Guest** | زائر بدون حساب يريد تقييم موقع قبل استخدامه |
| FU | **Free User** | مستخدم مسجل يريد تقييم مواقع بشكل متكرر |
| VO | **Verified Owner** | شخص أو شركة أثبتت ملكية موقعها |
| AU | **Agency User** | وكالة لديها تفويض من عميل لمراقبة موقعه |
| AD | **Admin** | صاحب المنصة يدير العملاء والـ Leads |
| SA | **Super Admin** | تحكم كامل في المنصة والإعدادات |

---

## 4. Core Product Layers

### Layer 1 — Public Free Trust Check
**الجمهور:** Guest, Free User  
**الهدف:** تقييم الثقة العام لحماية المستخدم  
**المبدأ:** لا فحص عميق، لا تفاصيل قابلة للاستغلال

**المخرجات للمستخدم:**
- Trust Score (0–100) بأربعة مستويات: منخفض / متوسط / جيد / مرتفع
- هل آمن للتصفح؟
- هل آمن لإدخال البريد الإلكتروني؟
- هل آمن لإنشاء حساب؟
- هل آمن للدفع الإلكتروني؟
- سبب واحد أو اثنان للتقييم (بلغة مبسطة)
- توصية واحدة واضحة

**الفحوصات المسموحة:**
- SSL certificate validity (basic)
- HTTPS enforcement
- Security Headers (وجود/غياب — بدون تفاصيل القيم)
- DNS reputation
- Google Safe Browsing (أو mock provider في MVP)
- HSTS presence

### Layer 2 — Verified Owner Security Monitoring
**الجمهور:** Verified Owner, Agency User (بتفويض)  
**الشرط:** إثبات الملكية أولًا + وجود Authorization Record  
**الهدف:** تقرير أمني حقيقي وتحسين مستمر

**المخرجات:**
- Security Score مع تفاصيل كل نقطة
- Findings مع severity/impact/evidence
- توصيات إصلاح حسب البيئة
- تقارير دورية (يومي/أسبوعي/شهري)
- تنبيهات عند تغيير مهم
- مقارنة قبل/بعد
- PDF عربي/إنجليزي

### Layer 3 — Admin Lead Audit & Client Management
**الجمهور:** Admin, Super Admin  
**الهدف:** إدارة العملاء واكتشاف فرص تجارية أخلاقية

**مستويان:**
- **A — Lead Audit (قبل الإذن):** فحص سطحي تسويقي فقط → Lead Score → Outreach Report → رسالة تواصل
- **B — Authorized Client Scan (بعد الإذن):** فحص عميق بعد وجود Authorization Record صالح

---

## 5. Core Scores

| الدرجة | الجمهور | ما يقيسه |
|--------|---------|----------|
| **Trust Score** | المستخدم العادي | أمان الموقع للاستخدام الشخصي |
| **Security Score** | صاحب الموقع | قوة الإعدادات الأمنية وتقدم الإصلاح |
| **Lead Score** | الأدمن فقط | جاهزية الموقع كفرصة تجارية |

---

## 6. Website Status Lifecycle

```
Public Check
    ↓
Lead / Prospect
    ↓
Contacted
    ↓
Permission Requested
    ↓
Verified Owner ←→ Active Client
    ↓
Monitoring Enabled
    
(مسار خروج في أي وقت) → Rejected / Do Not Scan
```

---

## 7. Key Principles (Non-Negotiable)

1. **Authorization First** — لا فحص عميق بدون Authorization Record صالح
2. **No Offensive Testing** — لا payloads، لا brute force، لا bypass
3. **Data Minimization** — لا يُخزن محتوى حساس أبدًا
4. **SSRF Prevention** — URL Validator إلزامي قبل أي طلب
5. **Audit Everything** — كل فحص يُسجَّل مع السبب والصلاحية
6. **Do Not Scan List** — قائمة محظورة لا تُتجاوز أبدًا
7. **Bilingual First** — العربية والإنجليزية من اليوم الأول
8. **No Secret Exposure** — لا تظهر مفاتيح API أو أسرار في أي مكان
9. **Scan ID Non-Guessable** — UUID قوي لكل عملية فحص
10. **Context-Aware Risk** — الخطورة تعتمد على نوع الموقع وبياناته

---

## 8. Technical Stack (Proposed — Confirmed in Phase 1)

| الطبقة | التقنية المقترحة |
|--------|----------------|
| Frontend | Next.js 14 + TypeScript + Tailwind CSS |
| i18n | next-intl (Arabic + English, RTL/LTR) |
| Backend | FastAPI (Python) أو NestJS (TypeScript) |
| Database | PostgreSQL |
| Cache/Queue | Redis + Celery (أو BullMQ) |
| Scheduler | Celery Beat أو node-cron |
| Auth | JWT + Refresh Tokens أو NextAuth |
| PDF | WeasyPrint (RTL support) أو Puppeteer |
| Container | Docker + docker-compose |

---

## 9. Non-Functional Requirements

| المتطلب | المواصفة |
|---------|---------|
| Response time (Public Check) | < 10 ثوانٍ |
| Scan timeout | أقصى 30 ثانية لكل فحص |
| Rate Limiting (Guest) | 3 طلبات/ساعة لكل IP |
| Rate Limiting (Free User) | 10 طلبات/يوم |
| Rate Limiting (Verified Owner) | 50 طلب/يوم لكل موقع |
| Max redirects | 5 |
| Max response size | 2 MB |
| Scan ID format | UUID v4 |
| Report retention (Public) | 24 ساعة |
| Report retention (Owner) | 90 يومًا |
| API Keys storage | مشفرة في قاعدة البيانات |
| Logs | لا تحتوي API Keys أو أسرار |
| HTTPS | إلزامي لجميع الاتصالات |

---

## 10. Ethical & Legal Boundaries

### مسموح دائمًا (Passive / Public Information):
- DNS records العامة
- SSL certificate metadata
- HTTP headers العامة
- Reputation databases العامة
- WHOIS (metadata فقط)

### مسموح بعد تحقق الملكية فقط:
- فحص ملفات حساسة محدود (existence check فقط — بدون محتوى)
- CMS detection
- تقارير دورية

### ممنوع مطلقًا في أي وضع:
- Port scanning (بدون موافقة صريحة لاحقة)
- Crawling واسع
- إرسال payloads
- Brute force
- تحميل أو عرض محتوى ملفات حساسة
- Exploit suggestions
- Bypass instructions
- اختبار XSS/SQL عملي

---

## 11. Compliance Considerations

- GDPR: تقليل البيانات، حذف البيانات بطلب المستخدم، لا تخزين IP بدون سبب
- Computer Fraud Laws: كل فحص عميق يتطلب توثيق التفويض
- Terms of Service: يجب أن تنص بوضوح على حدود الاستخدام
- Rate Limiting: لمنع إساءة الاستخدام
