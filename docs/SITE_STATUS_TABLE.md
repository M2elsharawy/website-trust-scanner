# جدول حالات الموقع — Site Status Table

## دورة حياة الموقع داخل النظام

```
[إدخال URL من مستخدم عام]
         ↓
   public_check_only
   
[الأدمن يضيف موقع كـ Lead]
         ↓
      lead/prospect
         ↓
      contacted
         ↓
   permission_requested
         ↓
   [مالك الموقع يضيف موقعه]
         ↓
   verified_owner ──────────→ active_client
         ↓                          ↓
   monitoring_enabled ←────────────┘
   
[في أي وقت]
         ↓
rejected_do_not_scan
```

---

## تفصيل كل حالة

### 1. `public_check_only`
**المعنى:** الموقع ظهر فقط في البحث العام من مستخدم عادي  
**من يُعيّن هذه الحالة:** النظام تلقائيًا عند أي فحص عام  
**الاحتفاظ بالبيانات:** 24 ساعة فقط  
**الفحوصات المسموحة:**
- SSL basic
- HTTPS check
- Security Headers (وجود/غياب)
- DNS reputation
- Google Safe Browsing

**الفحوصات الممنوعة:** جميع الفحوصات العميقة

---

### 2. `lead_prospect`
**المعنى:** الأدمن أضاف الموقع كعميل محتمل  
**من يُعيّن هذه الحالة:** Admin يدويًا  
**الاحتفاظ بالبيانات:** حتى يُحذف يدويًا  
**الفحوصات المسموحة:**
- SSL basic
- HTTPS check
- Security Headers (وجود/غياب فقط)
- DNS/SPF/DMARC (وجود/غياب فقط)
- Reputation check
- Lead Score calculation
- Outreach Report generation

**الفحوصات الممنوعة:** أي فحص عميق أو تفصيلي

---

### 3. `contacted`
**المعنى:** تم التواصل مع صاحب الموقع  
**من يُعيّن هذه الحالة:** Admin يدويًا  
**الاحتفاظ بالبيانات:** حتى يُحذف يدويًا  
**الفحوصات المسموحة:** نفس `lead_prospect`  
**الفحوصات الممنوعة:** نفس `lead_prospect`

---

### 4. `permission_requested`
**المعنى:** تم طلب الإذن من صاحب الموقع وننتظر رده  
**من يُعيّن هذه الحالة:** Admin يدويًا  
**تغيير مهم:** لا يُسمح بأي فحص إضافي حتى وصول الموافقة  
**الفحوصات المسموحة:** فحص سطحي واحد فقط للتأكد من حالة SSL  
**الفحوصات الممنوعة:** أي فحص إضافي حتى الانتقال للحالة التالية

---

### 5. `verified_owner`
**المعنى:** صاحب الموقع أثبت ملكيته (DNS TXT / HTML file / Meta tag)  
**من يُعيّن هذه الحالة:** النظام تلقائيًا بعد نجاح التحقق  
**الشرط الإلزامي:** وجود Authorization Record صالح  
**الاحتفاظ بالبيانات:** 90 يومًا للتقارير  
**الفحوصات المسموحة:**
- جميع فحوصات Public Check
- SSL/TLS مفصل
- Security Headers مفصل (قيم كاملة)
- DNS/SPF/DMARC/DKIM مفصل
- Exposed files (existence check فقط — بدون عرض أو تخزين محتوى)
- CMS detection (آمن)
- Reputation مفصل
- Security Score calculation
- Security Report generation
- Executive Report
- Developer Remediation Report

**الفحوصات الممنوعة:**
- Port scanning
- Crawling واسع
- XSS/SQL testing
- Brute force
- عرض أو تخزين محتوى ملفات حساسة

---

### 6. `active_client`
**المعنى:** الموقع عميل فعال مع عقد أو اتفاقية رسمية  
**من يُعيّن هذه الحالة:** Admin يدويًا بعد توثيق العقد  
**الشرط الإلزامي:** Authorization Record مكتمل + توثيق العقد  
**الفحوصات المسموحة:** جميع ما هو مسموح في `verified_owner` + تقارير دورية + تنبيهات  
**ملاحظة:** Port scanning وCrawling يحتاجان موافقة صريحة منفصلة في Authorization Record

---

### 7. `monitoring_enabled`
**المعنى:** تم تفعيل المراقبة الدورية للموقع  
**من يُعيّن هذه الحالة:** Admin أو Owner يدويًا  
**الشرط الإلزامي:** `active_client` + Authorization Record يسمح بالمراقبة  
**الفحوصات المسموحة:** جدولة الفحوصات المصرح بها تلقائيًا  
**تكرار الفحص:** يومي / أسبوعي / شهري (حسب إعداد الخطة)

---

### 8. `rejected_do_not_scan`
**المعنى:** الموقع محظور من الفحص نهائيًا  
**من يُعيّن هذه الحالة:** Admin أو Super Admin  
**الفحوصات المسموحة:** لا شيء — حتى Public Check مقيد  
**ملاحظة:** هذه الحالة لا يمكن تجاوزها برمجيًا — تُخزن في Do Not Scan List المستقلة

---

## جدول ملخص حالات الموقع

| الحالة | Public Check | Lead Audit | Security Report | Monitoring | PDF |
|--------|:-----------:|:----------:|:---------------:|:----------:|:---:|
| public_check_only | ✅ | ❌ | ❌ | ❌ | ❌ |
| lead_prospect | ✅ | ✅ | ❌ | ❌ | ❌ |
| contacted | ✅ | ✅ | ❌ | ❌ | ❌ |
| permission_requested | ✅ | ❌* | ❌ | ❌ | ❌ |
| verified_owner | ✅ | ✅ | ✅ | ❌ | ✅ |
| active_client | ✅ | ✅ | ✅ | ✅ | ✅ |
| monitoring_enabled | ✅ | ✅ | ✅ | ✅ | ✅ |
| rejected_do_not_scan | ❌ | ❌ | ❌ | ❌ | ❌ |

`*` = مقيد جدًا
