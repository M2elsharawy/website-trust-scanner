# Database Schema
## Website Trust & Security Advisor — PostgreSQL 16

**Version:** 1.0 — Phase 1  
**ORM:** SQLAlchemy 2.x (async)

---

## ملاحظات تصميمية

- جميع الـ `id` من نوع `UUID` (لا auto-increment integers للجداول العامة)
- جميع الجداول تحتوي `created_at` و `updated_at`
- الحقول الحساسة (API keys) تُشفَّر في قاعدة البيانات
- `audit_logs` جدول append-only (لا UPDATE، لا DELETE)
- `do_not_scan` جدول مستقل لا يُستعلم منه عبر ORM العادي — query مباشر لضمان الأداء

---

## 1. جدول: `users`

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255),
    role            VARCHAR(50) NOT NULL DEFAULT 'free_user',
                    -- guest | free_user | verified_owner | agency_user | admin | super_admin
    is_active       BOOLEAN NOT NULL DEFAULT true,
    is_verified     BOOLEAN NOT NULL DEFAULT false,
    preferred_lang  VARCHAR(10) NOT NULL DEFAULT 'ar',  -- ar | en
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

---

## 2. جدول: `sites`

```sql
CREATE TABLE sites (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain          VARCHAR(255) NOT NULL,  -- example.com (بدون scheme)
    display_url     VARCHAR(512),           -- كما أدخله المستخدم
    owner_id        UUID REFERENCES users(id) ON DELETE SET NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'public_check_only',
                    -- public_check_only | lead_prospect | contacted |
                    -- permission_requested | verified_owner | active_client |
                    -- monitoring_enabled | rejected_do_not_scan
    site_type       VARCHAR(50),
                    -- ecommerce | saas | blog | corporate | government |
                    -- medical | educational | agency | other
    has_login       BOOLEAN,
    collects_pii    BOOLEAN,
    accepts_payment BOOLEAN,
    sends_email     BOOLEAN,
    cms_hint        VARCHAR(50),  -- wordpress | laravel | nextjs | other | unknown
    hosting_hint    VARCHAR(50),  -- cloudflare | cpanel | nginx | apache | other
    notes           TEXT,         -- ملاحظات الأدمن (لا تُعرض للعامة)
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT sites_domain_owner_unique UNIQUE (domain, owner_id)
);

CREATE INDEX idx_sites_domain ON sites(domain);
CREATE INDEX idx_sites_status ON sites(status);
CREATE INDEX idx_sites_owner ON sites(owner_id);
```

---

## 3. جدول: `site_status_history`

```sql
CREATE TABLE site_status_history (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id         UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    from_status     VARCHAR(50),
    to_status       VARCHAR(50) NOT NULL,
    changed_by      UUID REFERENCES users(id) ON DELETE SET NULL,
    reason          TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_status_history_site ON site_status_history(site_id);
```

---

## 4. جدول: `authorization_records`

هذا الجدول هو قلب نظام الأمان — لا deep scan بدون سجل نشط هنا.

```sql
CREATE TABLE authorization_records (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id             UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    authorized_by       UUID NOT NULL REFERENCES users(id),
    authorization_type  VARCHAR(50) NOT NULL,
                        -- owner_verified | agency_contract | admin_approval
    status              VARCHAR(20) NOT NULL DEFAULT 'active',
                        -- active | expired | revoked | pending
    
    -- نطاق الصلاحية
    allows_security_scan    BOOLEAN NOT NULL DEFAULT true,
    allows_periodic_reports BOOLEAN NOT NULL DEFAULT false,
    allows_port_scan        BOOLEAN NOT NULL DEFAULT false,  -- دائمًا false في MVP
    allows_crawling         BOOLEAN NOT NULL DEFAULT false,  -- دائمًا false في MVP
    allows_cms_detection    BOOLEAN NOT NULL DEFAULT true,
    allows_exposed_files    BOOLEAN NOT NULL DEFAULT true,
    
    -- توقيت
    valid_from          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_until         TIMESTAMPTZ,  -- NULL = لا تنتهي
    
    -- توثيق
    verification_method VARCHAR(50),
                        -- dns_txt | html_file | meta_tag | contract_upload
    verification_token  VARCHAR(255),  -- التوكن المُستخدم في التحقق
    verified_at         TIMESTAMPTZ,
    contract_reference  VARCHAR(255),  -- رقم العقد أو المرجع (للوكالات)
    
    -- من وافق
    approved_by         UUID REFERENCES users(id),
    approved_at         TIMESTAMPTZ,
    
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_auth_records_site ON authorization_records(site_id);
CREATE INDEX idx_auth_records_status ON authorization_records(status);
-- المؤشر الأهم — الاستعلام الأكثر استخدامًا في Policy Engine
CREATE INDEX idx_auth_records_active ON authorization_records(site_id, status, valid_until)
    WHERE status = 'active';
```

---

## 5. جدول: `dns_verification_tokens`

```sql
CREATE TABLE dns_verification_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id     UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token       VARCHAR(255) NOT NULL UNIQUE,  -- trust-scanner-verify=<random>
    method      VARCHAR(20) NOT NULL DEFAULT 'dns_txt',
    status      VARCHAR(20) NOT NULL DEFAULT 'pending',
                -- pending | verified | expired | failed
    attempts    INTEGER NOT NULL DEFAULT 0,
    expires_at  TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '7 days'),
    verified_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_dns_tokens_site ON dns_verification_tokens(site_id);
CREATE INDEX idx_dns_tokens_token ON dns_verification_tokens(token);
```

---

## 6. جدول: `scans`

```sql
CREATE TABLE scans (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id         UUID REFERENCES sites(id) ON DELETE SET NULL,
    scan_type       VARCHAR(50) NOT NULL,
                    -- public_trust | lead_audit | owner_security | admin_deep
    status          VARCHAR(20) NOT NULL DEFAULT 'queued',
                    -- queued | running | completed | failed | cancelled
    triggered_by    UUID REFERENCES users(id) ON DELETE SET NULL,
    triggered_ip    INET,  -- IP المستخدم — Audit Log فقط، لا يُعرض
    
    -- التفويض المستخدم
    authorization_record_id UUID REFERENCES authorization_records(id) ON DELETE SET NULL,
    
    -- النتيجة
    trust_score         SMALLINT,   -- 0–100 (للـ public)
    security_score      SMALLINT,   -- 0–100 (للـ owner)
    lead_score          SMALLINT,   -- 0–100 (للـ admin)
    score_level         VARCHAR(20),  -- low | medium | good | high
    
    -- بيانات الفحص الخام (JSON مُختصر — لا محتوى ملفات حساسة)
    raw_results     JSONB,
    
    -- إحصاءات
    findings_count          SMALLINT DEFAULT 0,
    critical_findings_count SMALLINT DEFAULT 0,
    
    -- توقيت
    queued_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    duration_ms     INTEGER,
    
    -- cache key للنتائج المتكررة
    cache_key       VARCHAR(255),
    cached_until    TIMESTAMPTZ,
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_scans_site ON scans(site_id);
CREATE INDEX idx_scans_status ON scans(status);
CREATE INDEX idx_scans_type ON scans(scan_type);
CREATE INDEX idx_scans_cache ON scans(cache_key, cached_until) WHERE cache_key IS NOT NULL;
```

---

## 7. جدول: `scan_findings`

```sql
CREATE TABLE scan_findings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id         UUID NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
    
    -- التصنيف
    category        VARCHAR(50) NOT NULL,
                    -- ssl | headers | dns | reputation | exposed_files | cms
    check_name      VARCHAR(100) NOT NULL,  -- مثل: csp_missing، hsts_missing
    
    -- التقييم السياقي
    severity        VARCHAR(20) NOT NULL,
                    -- critical | high | medium | low | info
    likelihood      VARCHAR(20),  -- high | medium | low
    impact          VARCHAR(20),  -- high | medium | low
    confidence      VARCHAR(20),  -- confirmed | likely | informational | needs_verification
    evidence_level  VARCHAR(30),  -- Confirmed | Likely | Informational | Needs Verification
    
    -- التأثير على الدرجات
    trust_score_impact    SMALLINT DEFAULT 0,   -- سالب = ينقص من الدرجة
    security_score_impact SMALLINT DEFAULT 0,
    
    -- Evidence آمن (بدون محتوى حساس)
    evidence_safe   TEXT,  -- مثل: "Header CSP غائب في HTTP response"
    
    -- الإصلاح
    recommendation      TEXT,
    remediation_owner   VARCHAR(50),  -- developer | hosting | dns_admin | security
    remediation_effort  VARCHAR(20),  -- minutes | hours | days
    
    -- الحالة
    is_new          BOOLEAN NOT NULL DEFAULT true,  -- مقارنة بآخر فحص
    is_resolved     BOOLEAN NOT NULL DEFAULT false,
    resolved_at     TIMESTAMPTZ,
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_findings_scan ON scan_findings(scan_id);
CREATE INDEX idx_findings_severity ON scan_findings(severity);
CREATE INDEX idx_findings_category ON scan_findings(category);
```

---

## 8. جدول: `reports`

```sql
CREATE TABLE reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id         UUID NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
    report_type     VARCHAR(30) NOT NULL,
                    -- trust | security | executive | developer | outreach | lead
    language        VARCHAR(10) NOT NULL DEFAULT 'ar',  -- ar | en
    
    -- محتوى التقرير (HTML/JSON — لا أسرار)
    content_json    JSONB,
    pdf_path        VARCHAR(512),  -- مسار PDF المُخزَّن (Phase 10)
    
    -- صلاحية الوصول
    access_token    VARCHAR(255) UNIQUE,  -- للروابط العامة المؤقتة
    expires_at      TIMESTAMPTZ,
    is_public       BOOLEAN NOT NULL DEFAULT false,
    
    -- من يستطيع الوصول
    owner_id        UUID REFERENCES users(id) ON DELETE SET NULL,
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_reports_scan ON reports(scan_id);
CREATE INDEX idx_reports_token ON reports(access_token) WHERE access_token IS NOT NULL;
CREATE INDEX idx_reports_owner ON reports(owner_id);
```

---

## 9. جدول: `leads` (للأدمن فقط)

```sql
CREATE TABLE leads (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id         UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    assigned_to     UUID REFERENCES users(id) ON DELETE SET NULL,
    
    status          VARCHAR(30) NOT NULL DEFAULT 'new',
                    -- new | contacted | interested | permission_requested |
                    -- verified | active_client | rejected | do_not_contact
    
    -- بيانات التواصل
    contact_name    VARCHAR(255),
    contact_email   VARCHAR(255),
    contact_phone   VARCHAR(50),
    
    -- نتائج Lead Audit
    lead_score      SMALLINT,
    outreach_report_id UUID REFERENCES reports(id) ON DELETE SET NULL,
    
    -- ملاحظات
    admin_notes     TEXT,
    outreach_message TEXT,  -- الرسالة المُولَّدة (بدون تفاصيل حساسة)
    
    -- تواريخ
    first_contacted_at  TIMESTAMPTZ,
    last_contacted_at   TIMESTAMPTZ,
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_leads_site ON leads(site_id);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_assigned ON leads(assigned_to);
```

---

## 10. جدول: `do_not_scan` (مستقل وحساس)

```sql
CREATE TABLE do_not_scan (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain      VARCHAR(255) NOT NULL UNIQUE,
    reason      VARCHAR(50) NOT NULL,
                -- requested_by_owner | legal_request | abuse | system
    notes       TEXT,
    added_by    UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- مؤشر الأداء الأهم — يُستعلم قبل كل فحص
CREATE UNIQUE INDEX idx_dns_domain ON do_not_scan(lower(domain));
```

---

## 11. جدول: `audit_logs` (append-only)

```sql
CREATE TABLE audit_logs (
    id          BIGSERIAL PRIMARY KEY,  -- serial هنا مقبول (داخلي فقط)
    event_type  VARCHAR(100) NOT NULL,
                -- scan.started | scan.completed | scan.blocked | scan.failed
                -- auth.login | auth.logout | auth.failed
                -- site.added | site.verified | site.status_changed
                -- lead.created | lead.audit_run | lead.status_changed
                -- auth_record.created | auth_record.revoked
                -- report.generated | report.accessed | report.exported
                -- admin.do_not_scan_added | admin.user_role_changed
    
    actor_id    UUID REFERENCES users(id) ON DELETE SET NULL,
    actor_ip    INET,  -- IP المستخدم
    actor_role  VARCHAR(50),
    
    target_type VARCHAR(50),  -- site | scan | report | user | lead
    target_id   UUID,
    
    -- تفاصيل الحدث (بدون أسرار أو محتوى حساس)
    details     JSONB,
    
    -- هل كان مسموحًا أم محظورًا
    outcome     VARCHAR(20) NOT NULL DEFAULT 'success',
                -- success | denied | error
    
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
    -- لا updated_at — هذا الجدول append-only
);

CREATE INDEX idx_audit_event ON audit_logs(event_type);
CREATE INDEX idx_audit_actor ON audit_logs(actor_id);
CREATE INDEX idx_audit_target ON audit_logs(target_type, target_id);
CREATE INDEX idx_audit_time ON audit_logs(created_at DESC);
```

---

## 12. جدول: `refresh_tokens`

```sql
CREATE TABLE refresh_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  VARCHAR(255) NOT NULL UNIQUE,  -- SHA-256 للتوكن
    issued_ip   INET,
    expires_at  TIMESTAMPTZ NOT NULL,
    revoked_at  TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_refresh_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_hash ON refresh_tokens(token_hash);
```

---

## Entity Relationship Summary

```
users ──< sites (owner_id)
users ──< authorization_records (authorized_by, approved_by)
users ──< audit_logs (actor_id)
users ──< refresh_tokens
users ──< leads (assigned_to)

sites ──< site_status_history
sites ──< authorization_records
sites ──< dns_verification_tokens
sites ──< scans
sites ──< leads
sites ──1 do_not_scan (domain check)

scans ──< scan_findings
scans ──< reports

leads ──1 reports (outreach_report_id)
authorization_records ──< scans (used for)
```

---

## Data Retention (Summary — تفاصيل في DATA_RETENTION_POLICY.md)

| الجدول | مدة الاحتفاظ |
|--------|-------------|
| scans (public) | 24 ساعة |
| scans (owner) | 90 يومًا |
| scans (lead) | 30 يومًا |
| scan_findings | مرتبط بـ scans |
| reports (public) | 24 ساعة |
| reports (owner) | 90 يومًا |
| audit_logs | سنة كاملة |
| refresh_tokens | 7 أيام أو حتى الإلغاء |
| dns_verification_tokens | 7 أيام أو حتى التحقق |
