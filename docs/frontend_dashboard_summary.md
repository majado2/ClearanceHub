# Dashboard Summary (إحصائيات الطلبات)

هذا المستند يشرح لمبرمج الفرونت‑إند طريقة الحصول على إحصائيات الطلبات لكل نوع (بطاقات/تصاريح) مع تجميع حسب الحالات.

## المسار
```
GET /reports/dashboard/summary
```

## التوثيق
المسار محمي ويحتاج Bearer Token.

```
Authorization: Bearer <access_token>
```

## مخرجات الاستجابة (Response)
الاستجابة تحتوي على:
- `scope`: نطاق البيانات المعروضة (كل النظام أو قسم محدد)
- `all`: إحصائيات لجميع الطلبات
- `card`: إحصائيات طلبات البطاقات
- `access`: إحصائيات طلبات التصاريح

الحالات المجمّعة:
- **قيد الانتظار**: `PENDING_MANAGER_APPROVAL` و `PENDING_SECURITY_APPROVAL`
- **معتمدة**: `IN_PROCESS` و `COMPLETED`
- **مرفوضة**: `REJECTED_BY_MANAGER` و `REJECTED_BY_SECURITY`

## مثال استجابة
```
{
  "scope": {
    "type": "DEPARTMENT",
    "department_id": 10,
    "department_name": "تقنية المعلومات"
  },
  "all": {
    "total": 11,
    "pending": 0,
    "approved": 0,
    "rejected": 0
  },
  "card": {
    "total": 7,
    "pending": 0,
    "approved": 0,
    "rejected": 0
  },
  "access": {
    "total": 4,
    "pending": 0,
    "approved": 0,
    "rejected": 0
  }
}
```

## ملاحظات صلاحيات
- مدير القسم يشاهد إحصائيات قسمه فقط (`scope.type = DEPARTMENT`).
- موظف الطباعة يشاهد فقط حالات `IN_PROCESS` و `COMPLETED`.
- الأمن/الأدمن يشاهدون كل الطلبات (`scope.type = ALL`).

### ملاحظة خاصة بالطباعة
لموظف الطباعة يتم احتساب:
- **قيد الانتظار** = `IN_PROCESS` (بانتظار الطباعة)
- **معتمدة** = `COMPLETED` (مكتملة)
- **مرفوضة** = 0 (لا تُعرض له حالات مرفوضة)

## مثال cURL
```
curl -X GET "https://<host>/reports/dashboard/summary" \
  -H "Authorization: Bearer <token>"
```
