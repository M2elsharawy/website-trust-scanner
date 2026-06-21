# Data Retention Policy
## Website Trust & Security Advisor

**Version:** Phase 1 Design  
**المبدأ:** تقليل البيانات — لا نخزن ما لا نحتاج، لا نحتفظ بما أنهى غرضه.

---

## 1. جدول مدد الاحتفاظ

| نوع البيانات | الجدول | مدة الاحتفاظ | سبب الاحتفاظ | طريقة الحذف |
|-------------|--------|-------------|-------------|------------|
| Public Trust Scan | `scans` | 24 ساعة | Cache ونتيجة مؤقتة | Celery Beat job يومي |
| Public Trust Report | `reports` | 24 ساعة | رابط مؤقت للمستخدم | مع الـ scan |
| Lead Audit Scan | `scans` | 30 يومًا | مرجع للأدمن | Celery Beat job أسبوعي |
| Owner Security Scan | `scans` + `scan_findings` | 90 يومًا | مقارنة قبل/بعد | Celery Beat job أسبوعي |
| Owner Security Report | `reports` | 90 يومًا | تاريخ الموقع | مع الـ scan |
| Audit Logs | `audit_logs` | 365 يومًا | امتثال قانوني + تحقيق | Celery Beat job شهري |
| Refresh Tokens | `refresh_tokens` | 7 أيام أو حتى الإلغاء | Auth | Auto-expire |
| DNS Verification Tokens | `dns_verification_tokens` | 7 أيام | التحقق | Auto-expire |
| IP Addresses (في audit_log) | `audit_logs.actor_ip` | 365 يومًا (مع الـ log) | منع إساءة الاستخدام | مع الـ log |
| بيانات المستخدم | `users` | حتى طلب الحذف | خدمة الحساب | Manual + automated |
| بيانات الموقع | `sites` | حتى الحذف اليدوي | خدمة المالك | Manual |
| Authorization Records | `authorization_records` | حتى الإلغاء + 90 يوم | توثيق التفويض | Manual بعد نهاية العلاقة |

---

## 2. ما لا يُخزَّن أبدًا

| النوع | السبب |
|-------|-------|
| محتوى ملفات حساسة (.env، backup.sql، إلخ) | مخاطر قانونية وأمنية |
| محتوى صفحات HTML كاملة | حجم كبير، لا قيمة، مخاطر |
| HTTP response bodies الكاملة | لا نحتاجها، headers تكفي |
| كلمات المرور بشكل واضح | bcrypt hash فقط |
| مفاتيح API بشكل واضح | مُشفَّرة أو في env فقط |
| بيانات دفع أو بطاقات ائتمان | خارج نطاق المنتج تمامًا |
| محتوى رسائل البريد الإلكتروني للمواقع | لا نفحصها أبدًا |
| بيانات cookies أو sessions للمواقع المفحوصة | لا نجلب ما لا نحتاج |

---

## 3. حقوق المستخدم (GDPR Alignment)

### الحق في الحذف (Right to Erasure)

```
مستخدم يطلب حذف حسابه:
  1. حذف بيانات المستخدم الشخصية (email، name، password)
  2. anonymize المستخدم في audit_logs (actor_id → NULL، actor_ip → masking)
  3. تحويل ملكية المواقع أو حذفها حسب طلبه
  4. إلغاء جميع Authorization Records النشطة
  5. حذف Refresh Tokens
  6. إرسال تأكيد بالحذف

مدة التنفيذ: خلال 30 يومًا من الطلب (GDPR requirement)
```

### الحق في الوصول (Right of Access)

```
مستخدم يطلب بياناته:
  → تصدير JSON يشمل:
    - بيانات حسابه
    - قائمة مواقعه
    - ملخص التقارير (بدون raw scan data)
    - Authorization Records الخاصة به
```

### الحق في التصحيح (Right of Rectification)

```
المستخدم يستطيع تحديث:
  - الاسم
  - البريد الإلكتروني (مع تحقق جديد)
  - اللغة المفضلة
  - كلمة المرور
```

---

## 4. Data Minimization Rules

### عند إنشاء Scan Finding

```python
# ✅ صحيح — evidence مختصر وآمن
finding.evidence_safe = "Header 'Content-Security-Policy' absent in HTTP response"

# ❌ خطأ — محتوى حساس
finding.evidence_safe = response.headers.get('server')  # قد يكشف server version
finding.evidence_safe = file_content  # ممنوع مطلقًا
```

### عند تسجيل Audit Log

```python
# ✅ صحيح
audit.details = {
    "scan_type": "public_trust",
    "domain": "example.com",
    "policy_result": "allowed"
}

# ❌ خطأ
audit.details = {
    "url": full_url_with_params,  # قد يحتوي tokens في query string
    "headers": request.headers,  # قد يحتوي Authorization header
    "api_response": raw_response  # ممنوع
}
```

---

## 5. Automated Cleanup Jobs (Celery Beat)

```python
# في celery_app.py

CELERYBEAT_SCHEDULE = {
    # يوميًا — حذف public scans منتهية الصلاحية
    'cleanup-public-scans': {
        'task': 'workers.cleanup.delete_expired_public_scans',
        'schedule': crontab(hour=2, minute=0),  # 2am
    },
    
    # أسبوعيًا — حذف lead scans قديمة
    'cleanup-lead-scans': {
        'task': 'workers.cleanup.delete_old_lead_scans',
        'schedule': crontab(day_of_week=0, hour=3, minute=0),  # الأحد 3am
    },
    
    # أسبوعيًا — حذف owner scans أكثر من 90 يوم
    'cleanup-owner-scans': {
        'task': 'workers.cleanup.delete_old_owner_scans',
        'schedule': crontab(day_of_week=0, hour=3, minute=30),
    },
    
    # شهريًا — حذف audit logs أكثر من 365 يوم
    'cleanup-audit-logs': {
        'task': 'workers.cleanup.delete_old_audit_logs',
        'schedule': crontab(day_of_month=1, hour=4, minute=0),
    },
    
    # يوميًا — حذف tokens منتهية الصلاحية
    'cleanup-tokens': {
        'task': 'workers.cleanup.delete_expired_tokens',
        'schedule': crontab(hour=1, minute=0),
    },
}
```

---

## 6. Scan Results Cache Policy

للـ Public Trust Check، النتائج تُخزَّن مؤقتًا لتحسين الأداء:

```python
CACHE_SETTINGS = {
    'public_trust': {
        'ttl': 24 * 60 * 60,        # 24 ساعة (ثواني)
        'key_pattern': 'scan:public:{domain}',
        'store': 'redis',
    },
    'lead_audit': {
        'ttl': 4 * 60 * 60,          # 4 ساعات
        'key_pattern': 'scan:lead:{domain}',
        'store': 'redis',
    },
}
```

**قاعدة:** إذا طُلب فحص لنفس الـ domain خلال TTL، يُعاد استخدام النتيجة المُخزَّنة.  
**استثناء:** المستخدم يستطيع طلب "إعادة فحص" إجبارية لمواقعه المُتحقَّق منها.

---

## 7. Public vs Private Data Classification

| البيانات | التصنيف | من يرى |
|---------|---------|--------|
| Trust Score | Public (للموقع المفحوص) | أي مستخدم فحص الموقع |
| Security Score | Private | المالك المُتحقَّق فقط |
| Lead Score | Admin Only | Admin/Super Admin فقط |
| Scan Findings (general) | Private | المالك المُتحقَّق فقط |
| Scan Findings (exploitable details) | لا يُخزَّن | لا أحد |
| Actor IP | Internal Only | لا يُعرض في API |
| Authorization Records | Private | المالك + Admin |
| Audit Logs | Admin Only | Admin/Super Admin |
| Do Not Scan List | Admin Only | Admin/Super Admin |
