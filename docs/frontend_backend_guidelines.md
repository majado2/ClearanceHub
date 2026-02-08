# توجيهات الباك‑إند لمبرمج الفرونت‑إند

هذا المستند يوضح ما يلزم من ناحية الواجهات (APIs) والتنسيقات لضمان عمل الفرونت‑إند بدون شاشات فارغة أو بيانات ناقصة.

---

## 1) المصادقة (OTP Login)
### طلب OTP
```
POST /auth/request-otp
```
Body:
```json
{ "email": "manager.it@company.com" }
```
> الحقل `email` يقبل **البريد الداخلي** أو **الرقم الوظيفي**.

### تحقق OTP
```
POST /auth/verify-otp
```
Body:
```json
{ "email": "manager.it@company.com", "otp": "123456" }
```
Response:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "role": "DEPT_MANAGER",
  "employee_id": "E1001",
  "email": "manager.it@company.com",
  "user": {
    "role": "DEPT_MANAGER",
    "employee_id": "E1001",
    "email": "manager.it@company.com"
  }
}
```
> الدور والرقم الوظيفي والإيميل متوفرة في الجذر وكذلك ضمن `user`.

### بيانات المستخدم بعد الدخول
```
GET /auth/me
```
Headers:
```
Authorization: Bearer <access_token>
```
Response:
```json
{
  "role": "DEPT_MANAGER",
  "employee_id": "E1001",
  "email": "manager.it@company.com"
}
```

---

## 2) Dashboard Summary (إحصائيات)
```
GET /reports/dashboard/summary
```
Headers:
```
Authorization: Bearer <access_token>
```
يعيد:
- `scope`, `all`, `card`, `access`

تجميع الحالات الافتراضي:
- Pending = `PENDING_MANAGER_APPROVAL` + `PENDING_SECURITY_APPROVAL`
- Approved = `IN_PROCESS` + `COMPLETED`
- Rejected = `REJECTED_BY_MANAGER` + `REJECTED_BY_SECURITY`

**ملاحظة للطباعة**:
- pending = `IN_PROCESS`
- approved = `COMPLETED`
- rejected = 0

---

## 3) صلاحيات العرض حسب الدور
- **مدير القسم**: يرى طلبات قسمه فقط.
- **الأمن/الأدمن**: يرون جميع الطلبات.
- **الطباعة**: ترى فقط حالتي `IN_PROCESS` و `COMPLETED`.

---

## 4) تصدير CSV
```
GET /reports/requests/csv
```
فلاتر:
- `type` = `card` أو `access`
- `status`
- `from` / `to` (YYYY-MM-DD)

الإخراج يحتوي جميع الأعمدة المذكورة في `docs/frontend_reports_csv.md`.

---

## 5) إلغاء الطلب (للأدمن)
```
POST /requests/{id}/cancel?type=card|access
```
Body (اختياري):
```json
{ "reason": "سبب الإلغاء" }
```
> يغير الحالة إلى `CANCELLED`.

---

## 6) ملاحظات عامة
- عند استخدام `GET /requests/{id}` يفضّل تمرير `type` لتجنب تعارض أرقام الـ id بين البطاقات والتصاريح.
- يمكن استخدام نفس الحقل `email` في الـ OTP سواء للبريد أو الرقم الوظيفي.
