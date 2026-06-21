# جدول سياسة الفحص — Scan Policy Table
## الفحوصات المسموحة والممنوعة لكل حالة وكل دور

---

## مفتاح الرموز

| الرمز | المعنى |
|-------|--------|
| ✅ | مسموح بدون شروط إضافية |
| ✅* | مسموح بشروط محددة |
| ⚠️ | مسموح بحدود صارمة |
| ❌ | ممنوع برمجيًا |
| 🚫 | ممنوع مطلقًا في المشروع كله |

---

## 1. فحوصات SSL / TLS

| الفحص | Public | Lead | Verified Owner | Active Client | الملاحظات |
|-------|:------:|:----:|:--------------:|:-------------:|----------|
| HTTPS (هل يستخدم https) | ✅ | ✅ | ✅ | ✅ | — |
| SSL Certificate validity (valid/expired) | ✅ | ✅ | ✅ | ✅ | — |
| SSL Certificate issuer | ⚠️ | ⚠️ | ✅ | ✅ | Public: اسم الجهة فقط |
| SSL expiry date | ⚠️ | ⚠️ | ✅ | ✅ | Public: "سينتهي قريبًا" فقط |
| TLS version (1.2/1.3) | ❌ | ❌ | ✅ | ✅ | — |
| Cipher suites | ❌ | ❌ | ✅ | ✅ | — |
| Certificate chain | ❌ | ❌ | ✅ | ✅ | — |
| HSTS presence | ✅ | ✅ | ✅ | ✅ | — |
| HSTS max-age value | ❌ | ❌ | ✅ | ✅ | — |

---

## 2. فحوصات Security Headers

| الفحص | Public | Lead | Verified Owner | Active Client | الملاحظات |
|-------|:------:|:----:|:--------------:|:-------------:|----------|
| وجود/غياب Content-Security-Policy | ✅ | ✅ | ✅ | ✅ | — |
| قيمة CSP التفصيلية | ❌ | ❌ | ✅ | ✅ | — |
| وجود/غياب X-Frame-Options | ✅ | ✅ | ✅ | ✅ | — |
| قيمة X-Frame-Options | ❌ | ❌ | ✅ | ✅ | — |
| وجود/غياب X-Content-Type-Options | ✅ | ✅ | ✅ | ✅ | — |
| وجود/غياب Referrer-Policy | ✅ | ✅ | ✅ | ✅ | — |
| قيمة Referrer-Policy | ❌ | ❌ | ✅ | ✅ | — |
| وجود/غياب Permissions-Policy | ✅ | ✅ | ✅ | ✅ | — |
| قيمة Permissions-Policy | ❌ | ❌ | ✅ | ✅ | — |
| Server header (وجود) | ❌ | ❌ | ✅ | ✅ | لا تعرض القيمة في Public |
| X-Powered-By exposure | ❌ | ❌ | ✅ | ✅ | — |

---

## 3. فحوصات DNS

| الفحص | Public | Lead | Verified Owner | Active Client | الملاحظات |
|-------|:------:|:----:|:--------------:|:-------------:|----------|
| SPF record (وجود/غياب) | ✅ | ✅ | ✅ | ✅ | — |
| SPF record (قيمة) | ❌ | ❌ | ✅ | ✅ | — |
| DMARC record (وجود/غياب) | ✅ | ✅ | ✅ | ✅ | — |
| DMARC policy (none/quarantine/reject) | ⚠️ | ⚠️ | ✅ | ✅ | Public: مؤشر عام فقط |
| DKIM check | ❌ | ❌ | ✅* | ✅ | يحتاج إلى selector |
| MX records (وجود) | ⚠️ | ⚠️ | ✅ | ✅ | — |
| CAA records | ❌ | ❌ | ✅ | ✅ | — |
| DNS over HTTPS support | ❌ | ❌ | ✅ | ✅ | — |
| Subdomain enumeration | 🚫 | 🚫 | 🚫 | 🚫 | ممنوع مطلقًا |

---

## 4. فحوصات السمعة (Reputation)

| الفحص | Public | Lead | Verified Owner | Active Client | الملاحظات |
|-------|:------:|:----:|:--------------:|:-------------:|----------|
| Google Safe Browsing | ✅ | ✅ | ✅ | ✅ | — |
| VirusTotal domain check | ⚠️ | ⚠️ | ✅ | ✅ | Public: نتيجة عامة فقط |
| Phishing database check | ✅ | ✅ | ✅ | ✅ | — |
| Malware database check | ✅ | ✅ | ✅ | ✅ | — |
| Domain age | ✅ | ✅ | ✅ | ✅ | — |
| WHOIS data | ⚠️ | ⚠️ | ✅ | ✅ | Public: عمر الدومين فقط |

---

## 5. فحوصات الملفات الحساسة

| الفحص | Public | Lead | Verified Owner | Active Client | الملاحظات |
|-------|:------:|:----:|:--------------:|:-------------:|----------|
| فحص وجود ملفات حساسة (.env, backup, etc.) | 🚫 | 🚫 | ✅* | ✅* | existence check فقط، لا محتوى |
| عرض محتوى الملفات الحساسة | 🚫 | 🚫 | 🚫 | 🚫 | ممنوع مطلقًا |
| تخزين محتوى الملفات الحساسة | 🚫 | 🚫 | 🚫 | 🚫 | ممنوع مطلقًا |
| فحص robots.txt | ✅ | ✅ | ✅ | ✅ | public info |
| فحص sitemap.xml | ✅ | ✅ | ✅ | ✅ | public info |
| فحص /.well-known/ | ❌ | ❌ | ✅ | ✅ | — |

**الملفات الحساسة المقصودة (existence check فقط):**
- `.env`, `.env.local`, `.env.production`
- `backup.sql`, `dump.sql`, `database.sql`
- `wp-config.php.bak`
- `.git/config`
- `composer.json`, `package.json` (version exposure)

---

## 6. CMS Detection

| الفحص | Public | Lead | Verified Owner | Active Client | الملاحظات |
|-------|:------:|:----:|:--------------:|:-------------:|----------|
| CMS type detection (WordPress/Joomla/etc.) | ❌ | ❌ | ✅ | ✅ | — |
| CMS version | ❌ | ❌ | ✅ | ✅ | — |
| Plugin detection | ❌ | ❌ | ✅* | ✅* | آمن فقط، لا exploit |
| Plugin vulnerabilities lookup | ❌ | ❌ | ✅* | ✅* | مقارنة مع CVE database فقط |
| Theme detection | ❌ | ❌ | ✅ | ✅ | — |
| Admin panel detection | 🚫 | 🚫 | 🚫 | 🚫 | ممنوع مطلقًا |

---

## 7. فحوصات ممنوعة مطلقًا (في أي وضع)

| الفحص | السبب |
|-------|-------|
| Port scanning | هجومي، يحتاج إذنًا قانونيًا صريحًا خارج نطاق MVP |
| SQL Injection testing | هجومي، غير قانوني بدون إذن |
| XSS payload testing | هجومي، غير قانوني بدون إذن |
| Brute force | هجومي، غير قانوني |
| Admin panel bruteforce | هجومي، غير قانوني |
| Directory traversal | هجومي، غير قانوني |
| SSRF exploitation | يهدد البنية التحتية للمنصة نفسها |
| DNS rebinding attacks | هجومي |
| Subdomain takeover testing | هجومي |
| عرض/تخزين محتوى ملفات حساسة | انتهاك خصوصية، خطر قانوني |
| تحميل ملفات من الموقع المفحوص | خطر أمني على المنصة |
| JavaScript execution في الفحص | خطر XSS على المنصة |
| Cookie stealing/session hijacking | هجومي، غير قانوني |
| Social engineering | خارج نطاق المنصة |

---

## 8. سياسة URL Safety (SSRF Prevention)

يجب رفض الطلبات التالية **قبل** إرسال أي طلب HTTP:

### العناوين المحظورة:
```
localhost, 127.0.0.1, 0.0.0.0
10.0.0.0/8
172.16.0.0/12
192.168.0.0/16
169.254.0.0/16 (link-local / AWS metadata)
::1 (IPv6 loopback)
fc00::/7 (IPv6 private)
fe80::/10 (IPv6 link-local)
```

### البروتوكولات المسموحة فقط:
```
http://
https://
```

### البروتوكولات الممنوعة:
```
file://, ftp://, gopher://, dict://, ssh://, sftp://
javascript://, data://, vbscript://
أي بروتوكول آخر
```

### قواعد إضافية:
- التحقق من IP بعد DNS resolution
- إعادة التحقق بعد كل redirect
- الحد الأقصى للـ redirects: 5
- الحد الأقصى للـ timeout: 10 ثوانٍ
- الحد الأقصى لحجم الاستجابة: 2 MB
- منع cloud metadata endpoints: `169.254.169.254`
