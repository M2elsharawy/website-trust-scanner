# Security Controls Design
## Website Trust & Security Advisor

**Version:** Phase 1 Design  
**اعتمادًا على:** Defense in Depth، Least Privilege، Zero Trust للـ Scans

---

## 1. URL Safety Validator — تصميم مفصل

**الموقع:** `backend/app/core/url_validator.py`  
**متى يُستدعى:** قبل أي HTTP request يُرسله النظام للخارج — بدون استثناء.

### خوارزمية التحقق

```python
def validate_url(url: str) -> ValidatedUrl:
    """
    Returns ValidatedUrl if safe, raises UrlNotSafeError if not.
    Never logs the reason for blocking (prevents information disclosure).
    """
    
    # Step 1: Parse URL
    parsed = urlparse(url)
    
    # Step 2: Scheme whitelist
    if parsed.scheme not in ('http', 'https'):
        raise UrlNotSafeError()
    
    # Step 3: Extract hostname
    hostname = parsed.hostname
    if not hostname:
        raise UrlNotSafeError()
    
    # Step 4: Resolve DNS → get IP(s)
    try:
        ip_addresses = dns.resolver.resolve(hostname, 'A')  # + AAAA للـ IPv6
    except dns.exception.DNSException:
        raise UrlNotReachableError()
    
    # Step 5: Check each resolved IP against blocklist
    for ip in ip_addresses:
        if is_ip_blocked(str(ip)):
            raise UrlNotSafeError()
    
    # Step 6: Return validated URL (frozen, canonical)
    return ValidatedUrl(
        original=url,
        hostname=hostname,
        scheme=parsed.scheme,
        resolved_ips=[str(ip) for ip in ip_addresses]
    )


def is_ip_blocked(ip: str) -> bool:
    addr = ipaddress.ip_address(ip)
    return (
        addr.is_private or
        addr.is_loopback or
        addr.is_link_local or
        addr.is_multicast or
        addr.is_reserved or
        str(addr) == '169.254.169.254' or  # AWS/GCP/Azure metadata
        addr in ADDITIONAL_BLOCKED_RANGES
    )
```

### مواصفات httpx Client للفحص

```python
async def create_safe_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        follow_redirects=True,
        max_redirects=5,
        timeout=httpx.Timeout(
            connect=3.0,
            read=8.0,
            write=3.0,
            pool=3.0
        ),
        limits=httpx.Limits(
            max_response_size=2 * 1024 * 1024  # 2MB
        ),
        headers={
            'User-Agent': 'TrustScanner/1.0 (Security Assessment Tool)'
        },
        # منع تحميل الـ body كاملًا تلقائيًا
        # نقرأ headers فقط في معظم الفحوصات
    )
```

### التحقق بعد كل Redirect

```python
# كل redirect يمر عبر validate_url مجددًا
# httpx event hook:
async def check_redirect(response):
    if response.has_redirect_location:
        location = response.headers.get('location')
        validate_url(location)  # raises if unsafe
```

---

## 2. Scan Policy Engine — تصميم مفصل

**الموقع:** `backend/app/core/scan_policy.py`  
**متى يُستدعى:** قبل إنشاء أي Scan record — بعد URL validation.

### Decision Logic

```python
class ScanPolicyEngine:
    
    async def check(
        self,
        url: str,
        scan_type: ScanType,
        actor: User | None,
        db: AsyncSession
    ) -> PolicyDecision:
        """
        Returns PolicyDecision.ALLOWED or raises PolicyViolation.
        All denials are logged in audit_log.
        """
        
        domain = extract_domain(url)
        
        # Rule 1: Do Not Scan list (أعلى أولوية — لا استثناء)
        if await self.is_in_do_not_scan(domain, db):
            await self.log_denial(domain, scan_type, actor, 'domain_blocked')
            raise PolicyViolation('DOMAIN_BLOCKED')
        
        # Rule 2: Scan type permissions
        required_permission = SCAN_TYPE_PERMISSIONS[scan_type]
        
        if required_permission == Permission.PUBLIC:
            # Public Trust Check — بدون auth
            await self.check_rate_limit_ip(actor.ip if actor else request_ip)
            return PolicyDecision.ALLOWED
        
        if required_permission == Permission.AUTHENTICATED:
            if not actor:
                raise PolicyViolation('UNAUTHORIZED')
        
        # Rule 3: Deep scan يحتاج Authorization Record
        if required_permission == Permission.AUTHORIZED:
            if not actor:
                raise PolicyViolation('UNAUTHORIZED')
            
            site = await self.get_site(domain, actor, db)
            if not site:
                raise PolicyViolation('SITE_NOT_FOUND')
            
            # التحقق من حالة الموقع
            if site.status not in ALLOWED_STATUSES_FOR_DEEP_SCAN:
                raise PolicyViolation('SCAN_NOT_ALLOWED')
            
            # التحقق من Authorization Record
            auth_record = await self.get_active_authorization(site.id, db)
            if not auth_record:
                raise PolicyViolation('AUTHORIZATION_REQUIRED')
            
            if auth_record.valid_until and auth_record.valid_until < datetime.utcnow():
                raise PolicyViolation('AUTHORIZATION_EXPIRED')
            
            # التحقق من نوع الفحص المسموح
            if not self.scan_type_allowed_by_record(scan_type, auth_record):
                raise PolicyViolation('SCAN_TYPE_NOT_AUTHORIZED')
        
        return PolicyDecision.ALLOWED


# خريطة أنواع الفحص والصلاحيات المطلوبة
SCAN_TYPE_PERMISSIONS = {
    ScanType.PUBLIC_TRUST: Permission.PUBLIC,
    ScanType.LEAD_AUDIT: Permission.ADMIN,
    ScanType.OWNER_SECURITY: Permission.AUTHORIZED,
    ScanType.PERIODIC_MONITORING: Permission.AUTHORIZED,
}
```

---

## 3. Rate Limiting Design

**المكتبة:** `slowapi` (FastAPI integration لـ `limits`)  
**الـ Store:** Redis

### Tiers

```python
# Guest / IP-based
@limiter.limit("3/hour")
async def public_scan(request: Request, ...):
    ...

# Free User / Account-based  
@limiter.limit("10/day", key_func=get_user_id)
async def owner_scan(request: Request, ...):
    ...

# Admin — Lead Audit
@limiter.limit("20/hour", key_func=get_user_id)
async def lead_audit(request: Request, ...):
    ...

# Per-Domain limit (منع DDoS غير مباشر)
# كل domain لا يُفحص أكثر من 5 مرات/يوم من أي مستخدم
@limiter.limit("5/day", key_func=get_target_domain)
async def any_scan(request: Request, ...):
    ...
```

### Response عند تجاوز الحد

```json
HTTP 429 Too Many Requests
Retry-After: 3600

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": {
      "ar": "تجاوزت الحد المسموح. يمكنك المحاولة مجددًا بعد ساعة.",
      "en": "Rate limit exceeded. Please try again in 1 hour."
    }
  }
}
```

---

## 4. Authentication Design

### JWT Strategy

```
Access Token:  15 دقيقة (قصير — للأمان)
Refresh Token: 7 أيام (مُخزَّن في DB + HttpOnly Cookie)
```

### Token Flow

```
Login:
  → verify credentials
  → create access_token (JWT, 15min)
  → create refresh_token (opaque random, hashed in DB, 7days)
  → set refresh_token in HttpOnly Secure Cookie
  → return access_token in response body

API Requests:
  → Authorization: Bearer <access_token>
  → Backend validates JWT signature + expiry

Token Refresh:
  → Client sends refresh_token (from cookie)
  → Backend: hash it → lookup in DB → verify not revoked + not expired
  → Issue new access_token
  → Optionally rotate refresh_token

Logout:
  → Revoke refresh_token in DB
  → Clear cookie
```

### Security Headers للـ API (FastAPI Middleware)

```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "0"  # Deprecated, modern browsers ignore
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store"  # للـ API responses
    return response
```

---

## 5. RBAC Middleware

```python
# Dependency يُستخدم في كل endpoint محمي
async def require_role(*roles: UserRole):
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(403, "FORBIDDEN")
        return current_user
    return dependency

# مثال استخدام
@router.get("/admin/leads")
async def list_leads(
    admin: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    ...
```

---

## 6. Audit Logging Design

**الموقع:** `backend/app/services/audit_logger.py`

### قواعد:
1. كل فحص يُسجَّل (بدما أن يبدأ — قبل النتيجة)
2. كل رفض يُسجَّل مع السبب
3. كل دخول (ناجح وفاشل) يُسجَّل
4. كل تغيير في حالة الموقع يُسجَّل
5. لا `UPDATE` أو `DELETE` على جدول `audit_logs`
6. الـ IP يُخزَّن لكن لا يُعرض في الـ API responses العادية

```python
class AuditLogger:
    
    async def log(
        self,
        event_type: str,
        actor: User | None,
        actor_ip: str | None,
        target_type: str,
        target_id: UUID | None,
        outcome: str,           # success | denied | error
        details: dict | None,   # بدون أسرار أو محتوى حساس
        db: AsyncSession
    ) -> None:
        # details يُنقَّى قبل التخزين
        safe_details = self._sanitize_details(details)
        
        log = AuditLog(
            event_type=event_type,
            actor_id=actor.id if actor else None,
            actor_ip=actor_ip,
            actor_role=actor.role if actor else 'guest',
            target_type=target_type,
            target_id=target_id,
            outcome=outcome,
            details=safe_details
        )
        db.add(log)
        await db.flush()  # لا commit مستقل — جزء من transaction الطلب
    
    def _sanitize_details(self, details: dict) -> dict:
        # إزالة أي مفاتيح حساسة
        SENSITIVE_KEYS = {'password', 'token', 'api_key', 'secret', 'auth'}
        return {k: v for k, v in details.items() if k.lower() not in SENSITIVE_KEYS}
```

---

## 7. Do Not Scan List

**الموقع:** `backend/app/models/do_not_scan.py`  
**الاستعلام:** مباشر بدون ORM cache لضمان أحدث النتائج دائمًا.

```python
async def is_domain_blocked(domain: str, db: AsyncSession) -> bool:
    """
    Case-insensitive check. Called before every scan.
    Uses index on lower(domain) for performance.
    """
    result = await db.execute(
        select(DoNotScan.id)
        .where(func.lower(DoNotScan.domain) == domain.lower())
        .limit(1)
    )
    return result.scalar_one_or_none() is not None
```

**مصادر إضافة للقائمة:**
- Admin يضيف يدويًا
- صاحب الموقع يطلب وقف الفحص
- طلب قانوني
- نظام تلقائي عند رصد إساءة استخدام

---

## 8. Data Encryption

### حقول مُشفَّرة في قاعدة البيانات

| الجدول | الحقل | السبب |
|--------|-------|-------|
| (مستقبلًا) api_keys | key_value | مفاتيح API للمزودين |
| dns_verification_tokens | token | منع تخمين tokens التحقق |
| refresh_tokens | token_hash | SHA-256 (ليس encryption بل hashing) |

**المكتبة:** `cryptography` (Fernet symmetric encryption)  
**المفتاح:** مشتق من `APP_SECRET_KEY` عبر PBKDF2 — لا يُخزَّن في DB.

---

## 9. Report Output Security

### قواعد التقارير
1. Trust Report — public: لا headers values، لا server info، لا paths
2. Security Report — owner: يُعرض evidence آمن فقط
3. Lead/Outreach Report: نص مهني عام فقط
4. لا يُضمَّن أي محتوى من الموقع المفحوص مباشرة في التقرير
5. جميع القيم تمر عبر HTML escaping قبل الإدراج في قوالب PDF
6. روابط التقارير العامة: UUID + token عشوائي + expiry

### مثال Sanitization

```python
def safe_evidence(raw_value: str, max_length: int = 200) -> str:
    """
    Truncate and escape evidence before storing in scan_findings.
    Never store: file contents, API keys, passwords, tokens.
    """
    truncated = raw_value[:max_length]
    return html.escape(truncated)
```
