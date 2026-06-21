# جدول الصلاحيات — Permissions Table

## مبدأ التصريح المزدوج
> الصلاحية = الدور + حالة الموقع + Authorization Record  
> Admin Role وحده لا يمنح صلاحية الفحص العميق

---

## جدول الأدوار والصلاحيات الأساسية

| الصلاحية | Guest | Free User | Verified Owner | Agency User | Admin | Super Admin |
|----------|:-----:|:---------:|:--------------:|:-----------:|:-----:|:-----------:|
| Public Trust Check | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Trust Report (عام) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| إنشاء حساب | ✅ | — | — | — | — | — |
| إضافة موقع للمراقبة | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| إثبات ملكية الموقع | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Security Report (مالك) | ❌ | ❌ | ✅* | ✅* | ✅* | ✅ |
| تقارير دورية | ❌ | ❌ | ✅* | ✅* | ✅* | ✅ |
| تنبيهات | ❌ | ❌ | ✅* | ✅* | ✅* | ✅ |
| PDF Export | ❌ | ❌ | ✅* | ✅* | ✅* | ✅ |
| مقارنة قبل/بعد | ❌ | ❌ | ✅* | ✅* | ✅* | ✅ |
| عرض Leads | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Lead Audit (سطحي) | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Outreach Report | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| إنشاء Authorization Record | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Deep Scan (عميق) | ❌ | ❌ | ❌** | ❌** | ❌** | ❌** |
| إدارة المستخدمين | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| إدارة الإعدادات | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Do Not Scan List | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Audit Logs | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |

**ملاحظات:**
- `✅*` = مسموح فقط إذا كان الموقع في حالة `Verified Owner` أو `Active Client` ولديه Authorization Record صالح
- `❌**` = Deep Scan مسموح فقط بعد: (Verified Owner أو Active Client) + Authorization Record + موافقة صريحة على نوع الفحص

---

## تفصيل شروط Deep Scan

لتشغيل أي فحص "عميق" يجب توافر **جميع** الشروط التالية:

```
حالة الموقع = (Verified Owner) OR (Active Client) OR (Monitoring Enabled)
AND
Authorization Record.status = active
AND
Authorization Record.expiry_date > now()
AND
Authorization Record.allowed_scan_types INCLUDES requested_scan_type
AND
موقع الموقع NOT IN Do Not Scan List
```

---

## أنواع الفحص وشروطها

| نوع الفحص | الحد الأدنى المطلوب |
|-----------|-------------------|
| SSL basic check | Public — بدون شروط |
| HTTPS check | Public — بدون شروط |
| Security Headers (وجود/غياب) | Public — بدون شروط |
| DNS reputation check | Public — بدون شروط |
| Google Safe Browsing | Public — بدون شروط |
| Security Headers (قيم تفصيلية) | Verified Owner + Authorization Record |
| SSL/TLS مفصل | Verified Owner + Authorization Record |
| DNS/SPF/DMARC تفصيلي | Verified Owner + Authorization Record |
| Exposed files (existence only) | Verified Owner + Authorization Record |
| CMS detection | Verified Owner + Authorization Record |
| تقارير دورية | Active Client + Monitoring Enabled |
| Port scanning | ❌ خارج النطاق الآن (يحتاج موافقة صريحة مستقبلًا) |
| Crawling واسع | ❌ خارج النطاق الآن |
| اختبار XSS/SQL | ❌ ممنوع مطلقًا |

---

## حدود الاستخدام (Rate Limits)

| المستخدم | Public Check | Security Scan | تقارير دورية |
|----------|-------------|---------------|-------------|
| Guest | 3/ساعة/IP | ❌ | ❌ |
| Free User | 10/يوم | ❌ | ❌ |
| Verified Owner | 20/يوم | 5/يوم/موقع | حسب الخطة |
| Agency User | 30/يوم | 10/يوم/موقع | حسب العقد |
| Admin | 50/يوم | 20/يوم (بعد Authorization) | بدون حد |
| Super Admin | بدون حد | بدون حد | بدون حد |
