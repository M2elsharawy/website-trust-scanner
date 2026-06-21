# API Specification
## Website Trust & Security Advisor — FastAPI v1

**Base URL:** `/api/v1`  
**Format:** JSON  
**Auth:** Bearer JWT (Access Token)  
**Version:** Phase 1 Design

---

## Authentication Headers

```
Authorization: Bearer <access_token>     # للـ endpoints المحمية
Content-Type: application/json
Accept-Language: ar | en                 # للـ i18n في responses
```

---

## 1. Public Scan Endpoints (بدون auth)

### POST `/scans/public`
تشغيل Public Trust Check لأي URL.

**Rate Limit:** 3 طلبات/ساعة/IP

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response 202 Accepted:**
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "estimated_seconds": 8
}
```

**Errors:**
- `400` — URL غير صالح (scheme ممنوع، عنوان داخلي، etc.)
- `403` — الموقع في قائمة Do Not Scan
- `429` — تجاوز Rate Limit

**ملاحظة أمنية:** رسائل الخطأ عامة — لا تكشف سبب الحظر الداخلي.

---

### GET `/scans/{scan_id}/status`
متابعة حالة أي فحص.

**Response 200:**
```json
{
  "scan_id": "550e8400-...",
  "status": "queued | running | completed | failed",
  "progress_percent": 60,
  "started_at": "2026-06-21T10:00:00Z",
  "estimated_completion": "2026-06-21T10:00:08Z"
}
```

**Response 202** (لا يزال يعمل): نفس الـ schema بـ status غير completed.  
**Response 404**: scan_id غير موجود أو انتهت صلاحيته.

---

### GET `/reports/{scan_id}/trust`
الحصول على Trust Report بعد اكتمال الفحص.

**Query:** `?lang=ar|en`

**Response 200:**
```json
{
  "scan_id": "550e8400-...",
  "domain": "example.com",
  "scanned_at": "2026-06-21T10:00:08Z",
  "trust_score": 72,
  "score_level": "good",
  "recommendations": {
    "safe_to_browse": true,
    "safe_for_email": true,
    "safe_for_account": false,
    "safe_for_payment": false
  },
  "summary": "الموقع يستخدم HTTPS ولديه شهادة صالحة، لكن بعض إعدادات الحماية غير مكتملة.",
  "highlights": [
    {
      "type": "positive",
      "message": "يستخدم HTTPS وشهادة SSL صالحة"
    },
    {
      "type": "warning",
      "message": "بعض إعدادات حماية المتصفح غير مفعّلة"
    }
  ],
  "expires_at": "2026-06-22T10:00:08Z"
}
```

**ملاحظة:** التقرير لا يحتوي:
- أسماء headers بقيمها
- مسارات ملفات
- معلومات server
- تفاصيل قابلة للاستغلال

---

## 2. Auth Endpoints

### POST `/auth/login`
```json
// Request
{ "email": "user@example.com", "password": "..." }

// Response 200
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": { "id": "uuid", "role": "admin", "preferred_lang": "ar" }
}
```

**Security:** Password never logged. Rate limit: 5 attempts/15 min/IP.

### POST `/auth/refresh`
```json
// Request
{ "refresh_token": "eyJ..." }

// Response 200
{ "access_token": "eyJ...", "expires_in": 900 }
```

### POST `/auth/logout`
**Auth Required**
```json
// Request
{ "refresh_token": "eyJ..." }
// Response 204 No Content
```

---

## 3. Sites Endpoints (Verified Owner)

### GET `/sites`
**Auth Required | Roles: verified_owner, agency_user, admin**

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "domain": "example.com",
      "status": "verified_owner",
      "last_scan": { "id": "uuid", "completed_at": "...", "security_score": 68 },
      "critical_findings": 1
    }
  ],
  "total": 1
}
```

### POST `/sites`
**Auth Required | Roles: free_user, verified_owner, admin**

```json
// Request
{
  "url": "https://example.com",
  "site_type": "ecommerce",
  "has_login": true,
  "collects_pii": true,
  "accepts_payment": true,
  "sends_email": true
}

// Response 201
{
  "id": "uuid",
  "domain": "example.com",
  "status": "pending_verification"
}
```

### POST `/sites/{site_id}/verify/dns`
**Auth Required | بدء عملية التحقق بـ DNS TXT**

```json
// Response 200
{
  "verification_token": "trust-scanner-verify=abc123xyz",
  "instructions": {
    "ar": "أضف سجل TXT في DNS لنطاقك بالقيمة التالية:",
    "en": "Add a TXT record to your domain DNS with the following value:"
  },
  "dns_record": {
    "type": "TXT",
    "name": "@",
    "value": "trust-scanner-verify=abc123xyz"
  },
  "note": {
    "ar": "قد يستغرق انتشار DNS حتى 48 ساعة",
    "en": "DNS propagation may take up to 48 hours"
  },
  "expires_at": "2026-06-28T10:00:00Z"
}
```

### GET `/sites/{site_id}/verify/status`
**Auth Required**
```json
{
  "status": "pending | verified | failed | expired",
  "checked_at": "2026-06-21T10:05:00Z",
  "message": "لم يتم العثور على سجل TXT بعد. تأكد من إضافته وانتظر انتشار DNS."
}
```

### POST `/sites/{site_id}/scans`
**Auth Required | Roles: verified_owner (for own sites), admin**  
**Requires:** Authorization Record active for site

```json
// Request
{ "scan_type": "owner_security", "lang": "ar" }

// Response 202
{ "scan_id": "uuid", "status": "queued" }
```

**Policy Check:** Backend يتحقق من:
1. المستخدم يملك الموقع أو لديه تفويض
2. الموقع في حالة `verified_owner` أو `active_client`
3. Authorization Record نشط وغير منتهي
4. الموقع ليس في Do Not Scan List

---

### GET `/sites/{site_id}/reports`
**Auth Required | Owner only**
```json
{
  "items": [
    {
      "id": "uuid",
      "scan_id": "uuid",
      "report_type": "security",
      "language": "ar",
      "created_at": "...",
      "security_score": 68
    }
  ]
}
```

---

## 4. Reports Endpoints

### GET `/reports/{scan_id}/security`
**Auth Required | Owner of site only**

```json
{
  "scan_id": "uuid",
  "domain": "example.com",
  "scanned_at": "...",
  "security_score": 68,
  "score_level": "medium",
  "site_context": {
    "site_type": "ecommerce",
    "has_payment": true,
    "risk_multiplier": 1.5
  },
  "findings": [
    {
      "id": "uuid",
      "category": "headers",
      "check_name": "csp_missing",
      "severity": "high",
      "likelihood": "medium",
      "impact": "high",
      "confidence": "confirmed",
      "evidence_level": "Confirmed",
      "title": { "ar": "سياسة أمان المحتوى (CSP) غائبة", "en": "Content Security Policy missing" },
      "description": { "ar": "...", "en": "..." },
      "business_impact": { "ar": "...", "en": "..." },
      "recommendation": { "ar": "...", "en": "..." },
      "remediation_owner": "developer",
      "remediation_effort": "hours",
      "is_new": true,
      "is_resolved": false,
      "fix_examples": {
        "nginx": "add_header Content-Security-Policy \"...\";",
        "apache": "Header set Content-Security-Policy \"...\"",
        "cloudflare": "...",
        "wordpress": "..."
      }
    }
  ],
  "summary": {
    "critical": 0,
    "high": 2,
    "medium": 3,
    "low": 1,
    "info": 2
  },
  "previous_scan": {
    "scan_id": "uuid",
    "security_score": 55,
    "scanned_at": "..."
  }
}
```

---

## 5. Admin Endpoints

**Auth Required | Roles: admin, super_admin**

### GET `/admin/leads`
```json
{
  "items": [
    {
      "id": "uuid",
      "domain": "example.com",
      "status": "contacted",
      "lead_score": 45,
      "contact_name": "...",
      "last_contacted_at": "...",
      "assigned_to": "uuid"
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 20
}
```

### POST `/admin/leads`
```json
// Request
{ "url": "https://example.com", "contact_name": "...", "contact_email": "..." }

// Response 201
{ "id": "uuid", "domain": "example.com", "status": "new" }
```

### POST `/admin/leads/{lead_id}/audit`
تشغيل Lead Audit — فحص سطحي تسويقي فقط.  
**مقيد برمجيًا:** لا يستطيع تشغيل Security Scan.

```json
// Response 202
{ "scan_id": "uuid", "scan_type": "lead_audit", "status": "queued" }
```

### GET `/admin/leads/{lead_id}/outreach-report`
```json
{
  "domain": "example.com",
  "lead_score": 45,
  "general_observations": [
    { "type": "improvement_opportunity", "message": "إعدادات حماية البريد قابلة للتحسين" }
  ],
  "outreach_message": "أجرينا مراجعة سطحية لمؤشرات الأمان العامة الظاهرة لموقعكم...",
  "note": "هذا التقرير لا يتضمن أي فحص عميق أو معلومات حساسة"
}
```

### PATCH `/admin/leads/{lead_id}/status`
```json
// Request
{ "status": "contacted", "notes": "..." }
// Response 200: updated lead object
```

### GET `/admin/audit-logs`
**Auth Required | Roles: admin, super_admin**
```json
{
  "items": [
    {
      "id": 1,
      "event_type": "scan.started",
      "actor_role": "admin",
      "target_type": "site",
      "target_id": "uuid",
      "outcome": "success",
      "created_at": "..."
    }
  ]
}
```
**ملاحظة:** `actor_ip` لا يُعرض في response — يُحفظ في DB فقط لأغراض التحقيق.

---

## 6. Error Response Format

جميع الأخطاء تتبع هذا الـ format:

```json
{
  "error": {
    "code": "SCAN_NOT_ALLOWED",
    "message": { "ar": "الفحص غير مسموح لهذا الموقع", "en": "Scan not allowed for this site" },
    "details": null
  }
}
```

**Error Codes:**
| Code | HTTP | المعنى |
|------|------|--------|
| `INVALID_URL` | 400 | رابط غير صالح |
| `URL_NOT_SAFE` | 400 | رابط يشير لعنوان داخلي أو محظور |
| `DOMAIN_BLOCKED` | 403 | الموقع في Do Not Scan List |
| `SCAN_NOT_ALLOWED` | 403 | الفحص غير مسموح لحالة الموقع الحالية |
| `AUTHORIZATION_REQUIRED` | 403 | يحتاج Authorization Record |
| `AUTHORIZATION_EXPIRED` | 403 | Authorization Record منتهي |
| `RATE_LIMIT_EXCEEDED` | 429 | تجاوز الحد المسموح |
| `SCAN_IN_PROGRESS` | 409 | يوجد فحص نشط بالفعل لهذا الموقع |
| `NOT_FOUND` | 404 | المورد غير موجود |
| `UNAUTHORIZED` | 401 | لا يوجد توكن صالح |
| `FORBIDDEN` | 403 | الصلاحيات غير كافية |

**قاعدة:** رسائل الخطأ لا تكشف معلومات داخلية (مسارات، stack traces، DB errors).

---

## 7. API Versioning Strategy

- الـ version في الـ URL: `/api/v1/`
- عند إضافة ميزات جديدة: نضيف endpoints جديدة في v1
- عند تغيير breaking changes: ننشئ `/api/v2/`
- كل endpoint يُعيد `X-API-Version: 1` header

---

## 8. Pagination

جميع الـ list endpoints تدعم:
```
GET /admin/leads?page=1&per_page=20&sort=created_at&order=desc
```

Response دائمًا:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "pages": 5
}
```
