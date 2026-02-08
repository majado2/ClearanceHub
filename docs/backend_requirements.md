# طلب رسمي لمتطلبات الباك‑إند

هذا المستند يوضح المتطلبات اللازمة من الباك‑إند لضمان عمل واجهة **ClearanceHub** بشكل صحيح ودون ظهور شاشات فارغة، مع توافق كامل مع الواجهات الحالية.

## 1) مصادقة المستخدم وإرجاع الدور
- في استجابة `POST /auth/verify-otp` يجب إرجاع:
  - `role`
  - `employee_id`
  - `email`
- يمكن إرجاعها مباشرة أو ضمن كائن `user`.
- الهدف: منع ظهور شاشة بيضاء بسبب غياب الدور بعد تسجيل الدخول.

## 2) Endpoint موثوق لبيانات المستخدم (مستحسن)
- إضافة `GET /auth/me` لإرجاع بيانات المستخدم بعد تسجيل الدخول:
  - `role`, `employee_id`, `email`
- الهدف: ضمان ثبات البيانات حتى لو تغيّر شكل استجابة التوكن.

## 3) Dashboard Summary
- التأكد من أن `GET /reports/dashboard/summary` يرجع الإحصائيات حسب المستند:
  - `scope`, `all`, `card`, `access`
  - تجميع الحالات:
    - **Pending** = `PENDING_MANAGER_APPROVAL` + `PENDING_SECURITY_APPROVAL`
    - **Approved** = `IN_PROCESS` + `COMPLETED`
    - **Rejected** = `REJECTED_BY_MANAGER` + `REJECTED_BY_SECURITY`
- **ملاحظة خاصة بحساب الطباعة**:
  - `pending = IN_PROCESS`
  - `approved = COMPLETED`
  - `rejected = 0`

## 4) صلاحيات العرض حسب الدور
- مدير القسم: يعرض فقط طلبات قسمه.
- الأمن/الأدمن: يعرضون جميع الطلبات.
- الطباعة: يعرض فقط حالات `IN_PROCESS` و `COMPLETED`.

## 5) CSV Export
- Endpoint: `GET /reports/requests/csv`
- يجب دعم الفلاتر: `type`, `status`, `from`, `to`
- يجب إرجاع جميع الأعمدة المذكورة في مستند `frontend_reports_csv.md`.
- إرجاع `Content-Type: text/csv`.

## 6) إلغاء الطلب للأدمن
- المطلوب: الأدمن **يلغي الطلب** وليس يوافق عليه.
- خياران مقترحان:
  1. إضافة `POST /requests/{id}/cancel` وتحديث الحالة إلى `CANCELLED`
  2. تمييز `reject` للأدمن ليعطي حالة `CANCELLED` بدل `REJECTED`

---
**ملاحظة:** هذه المتطلبات ضرورية لضمان تكامل الفرونت‑إند مع الباك‑إند بشكل كامل بدون حلول التفاف أو بيانات تجريبية.
