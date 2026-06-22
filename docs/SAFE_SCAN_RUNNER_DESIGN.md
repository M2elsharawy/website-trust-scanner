# Safe Scan Runner — Design Document

**Status:** Design only — no implementation yet
**Relates to:** Issue #15 (Central Scan Orchestrator / Safe Scan Runner)
**Phase:** B (pending explicit approval before implementation)

---

## 1. الهدف

نحتاج Safe Scan Runner لأن كل مسار فحص حالي (Public Trust, Owner Scan, Scheduled Scan, Admin Lead Audit) يُطبّق قواعد الأمان — Do Not Scan, URL validation, scan policy — بشكل مستقل ومتناثر.

المشكلة ليست في صحة الكود الحالي (الكود الحالي صحيح)، بل في أن أي مسار جديد يُضاف في المستقبل يمكن أن ينسى تطبيق أحد هذه القواعد، ولا يوجد مكان واحد يُجبر على احترامها جميعًا.

**الهدف:** جعل Safe Scan Runner هو المسار الوحيد المسموح له بتشغيل أي فحص، بحيث يستحيل تجاوز أي قاعدة أمان بالخطأ.

---

## 2. المشكلة الحالية

Enforcement موزع حاليًا بين أربعة مسارات:

| المسار | الملف | الحالة |
|--------|-------|--------|
| Public Trust Check | `app/api/v1/public_scan.py` | يُطبّق validation مستقل |
| Owner Scan | `app/api/v1/owner_scans.py` | يُطبّق validation مستقل |
| Scheduled Scan | `app/tasks/scheduled_scans.py` | يُطبّق validation مستقل |
| Admin Lead Audit | `app/api/v1/admin_lead_audit.py` | يُطبّق validation مستقل |

**المخاطر المستقبلية:**

- إضافة مسار جديد (webhook, batch job, internal API) بدون تطبيق Do Not Scan.
- تغيير ترتيب العمليات في مسار واحد دون تذكر تأثيره على الأمان.
- تكرار كود validation مع احتمال أن تتباين الإصدارات بمرور الوقت.
- لا يوجد audit log موحد لجميع محاولات الفحص.

---

## 3. المسارات التي سيغطيها Runner لاحقًا

1. **Public Trust Check** — طلب مجاني من أي مستخدم عبر الـ API العام.
2. **Owner Scan** — طلب يدوي من مالك الموقع المصادق عليه.
3. **Scheduled Scan** — إعادة فحص تلقائي دوري عبر Celery.
4. **Admin Lead Audit** — فحص يطلبه admin على موقع lead محدد.

---

## 4. الترتيب الأمني الإلزامي داخل Runner

الترتيب التالي **غير قابل للتغيير** — كل خطوة يجب أن تكتمل بنجاح قبل الانتقال للتالية:

```
1. Normalize input
   - تنظيف الـ domain/URL من المسافات، strip الـ scheme
   - لا DNS lookup في هذه الخطوة

2. Do Not Scan check
   - استعلام قاعدة البيانات: هل الـ domain مدرج في قائمة Do Not Scan؟
   - رفض فوري إن وُجد — قبل أي عملية شبكة

3. URL validation / SSRF protection
   - استدعاء validate_url()
   - يشمل DNS resolution + IP range check
   - يرفض private/loopback/link-local/reserved ranges

4. استخراج validated hostname
   - من نتيجة validate_url() فقط
   - حراسة: إن كان فارغًا → رفض فوري

5. Scan policy check
   - استدعاء check_scan_allowed() مع (domain, scan_type, actor_role)
   - يرفض إن كان scan_type غير مسموح لهذا الـ actor

6. Rate limit / quota check
   - التحقق من حد الطلبات للـ actor_id أو request_ip
   - يرفض إن تجاوز الحد

7. Audit log: scan requested
   - تسجيل: من طلب، متى، أي domain، أي scan_type، أي source
   - لا تسجيل لـ raw URL أو response body

8. Run allowed passive scanners only
   - استدعاء run_public_scan(validated_hostname)
   - جميع الطلبات الخارجية عبر make_safe_client() فقط

9. Audit log: scan completed or failed
   - تسجيل: النتيجة، المدة، أي checker فشل إن وجد

10. Store sanitized result فقط
    - لا تخزين header values أو response bodies
    - تخزين presence flags فقط
```

---

## 5. المدخلات والمخرجات المقترحة

### Input

```
domain          : str          # الـ domain الخام قبل validation
scan_type       : ScanType     # PUBLIC_TRUST | OWNER | SCHEDULED | ADMIN_LEAD
actor_id        : UUID | None  # معرّف المستخدم أو None للطلبات العامة
actor_role      : Role         # PUBLIC | OWNER | ADMIN
site_id         : UUID | None  # اختياري — للـ owner scan والـ scheduled
source          : ScanSource   # public | owner | scheduled | admin_lead
request_ip      : str | None   # IP الطالب — للـ rate limiting والـ audit
```

### Output

```
normalized_domain   : str
validated_hostname  : str
scan_id             : UUID
status              : ScanStatus   # completed | blocked | failed
sanitized_results   : dict         # presence flags فقط — لا values
score               : int | None   # إن وُجد scoring engine
blocked_reason      : str | None   # do_not_scan | ssrf_blocked | policy_denied | rate_limited
```

---

## 6. ما الذي لا يجب أن يفعله Runner

- **لا port scanning** — خارج نطاق الفحص السلبي.
- **لا crawling** — لا متابعة روابط داخلية أو زيارة صفحات متعددة.
- **لا exposed files scan** — في هذه المرحلة على الأقل (يتطلب موافقة منفصلة).
- **لا raw responses** — لا تمرير أو تخزين محتوى HTTP responses.
- **لا عرض أو تخزين header values** — presence فقط.
- **لا bypass للـ policy** — لا exception لأي scan_type بدون تعديل policy صريح.
- **لا admin override** بدون Authorization Record مسجل في الـ audit log.
- **لا استدعاء httpx مباشرة** — كل outbound HTTP عبر `make_safe_client()` فقط.

---

## 7. علاقة Runner بالملفات الحالية

| الملف الحالي | الدور بعد Phase B |
|---|---|
| `app/core/url_validator.py` | لا تغيير — runner يستدعيه في الخطوة 3 |
| `app/core/http_client.py` | لا تغيير — make_safe_client() يبقى كما هو |
| `app/core/scan_policy.py` | لا تغيير — runner يستدعيه في الخطوة 5 |
| `app/core/audit_logger.py` | لا تغيير — runner يستدعيه في الخطوتين 7 و9 |
| `app/scanners/run_public_scan()` | يبقى كما هو — runner يستدعيه في الخطوة 8 |
| `app/api/v1/owner_scans.py` | يُحذف منه كود validation — يفوّض للـ runner |
| `app/tasks/scheduled_scans.py` | يُحذف منه كود validation — يفوّض للـ runner |
| `app/api/v1/admin_lead_audit.py` | يُحذف منه كود validation — يفوّض للـ runner |

**المبدأ:** كل ملف يحذف validation code خاص به ويستبدله بـ `await safe_scan_runner.run(...)`.

---

## 8. خطة تنفيذ Phase B (مقترحة)

### PR 1 — إنشاء Runner وتوصيل Public Trust فقط

- إنشاء `app/core/safe_scan_runner.py` بالترتيب الأمني الإلزامي الكامل.
- تعديل `app/api/v1/public_scan.py` فقط للاستخدام الجديد.
- إضافة tests تغطي: الترتيب الأمني، Do Not Scan block، SSRF block، policy deny، نجاح فحص كامل.
- **لا تغيير** في owner_scans / scheduled_scans / admin_lead_audit في هذا الـ PR.

### PR 2 — نقل باقي المسارات

- تعديل `owner_scans.py` + `scheduled_scans.py` + `admin_lead_audit.py` للاستخدام الجديد.
- حذف كود validation المتكرر من كل منها.
- إضافة static analysis test يمنع direct calls للـ scanners خارج runner.
- Tests لكل مسار بشكل منفصل.

---

## 9. المخاطر

| المخاطرة | التأثير | الاحتياط |
|---|---|---|
| تغيير سلوك الفحص الحالي | عالٍ | PR 1 يغطي مسارًا واحدًا فقط أولًا |
| تكرار validation في runner والملفات القديمة أثناء الانتقال | متوسط | كل PR يحذف validation القديم فور إضافة runner |
| كسر scheduled scans (Celery) | عالٍ | PR 2 يتضمن integration tests للـ scheduled flow |
| تسجيل بيانات زائدة في audit log | متوسط | مراجعة صريحة لكل حقل يُسجَّل قبل merge |
| تضخم runner وتحوله لـ god object | متوسط | runner لا ينفّذ أي فحص بنفسه — يفوّض فقط |

---

## 10. Acceptance Criteria (Phase B)

### Functional

- [ ] جميع المسارات الأربعة تمر عبر `safe_scan_runner.run()` دون استثناء.
- [ ] Do Not Scan check يحدث قبل أي DNS resolution في جميع المسارات.
- [ ] SSRF protection مطبق على كل domain قبل أي outbound HTTP.
- [ ] Scan policy check يحدث بعد URL validation وقبل تشغيل أي checker.
- [ ] لا توجد استدعاءات مباشرة للـ scanners خارج runner (static analysis test).

### Security

- [ ] لا يمكن الوصول لـ `run_public_scan()` مباشرة من API handlers بعد PR 2.
- [ ] لا raw response bodies أو header values مخزنة في قاعدة البيانات.
- [ ] كل محاولة فحص مسجلة في audit log سواء نجحت أو رُفضت.
- [ ] Admin Lead Audit لا يتجاوز Do Not Scan أو scan policy.

### Quality

- [ ] Unit tests تغطي كل خطوة من الخطوات العشر بشكل منفصل.
- [ ] Integration tests لكل مسار من المسارات الأربعة.
- [ ] CI يمر بالكامل على كلا الـ PR قبل merge.
- [ ] لا regression في الفحوصات الحالية (نتائج متطابقة قبل وبعد).

### Process

- [ ] موافقة صريحة على PR 1 قبل البدء في PR 2.
- [ ] لا auto-merge.
