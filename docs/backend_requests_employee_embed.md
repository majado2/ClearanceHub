# طلب رسمي: تضمين معلومات الموظف داخل استجابة الطلبات

هذا الطلب لضمان تقليل عدد الاتصالات من الفرونت‑إند، ولتسريع شاشة الطلبات.

## المشكلة الحالية
الواجهة الأمامية تستدعي:
1. `GET /requests` لجلب قائمة الطلبات
2. ثم **استدعاء لكل طلب**: `GET /employees/{employee_id}`

هذا يسبب **N+1 requests** ويؤثر على الأداء.

## المطلوب من الباك‑إند
تضمين بيانات الموظف داخل كل عنصر في استجابة:
```
GET /requests
```

## شكل الاستجابة المقترح
```
{
  "items": [
    {
      "id": 123,
      "request_type": "CARD",
      "employee_id": "E1001",
      "status": "PENDING_MANAGER_APPROVAL",
      "created_at": "2026-02-04T08:00:00Z",
      "employee": {
        "employee_id": "E1001",
        "name_ar": "أحمد محمد",
        "name_en": "Ahmed Mohammed",
        "job_title": "Software Engineer",
        "department_id": 10,
        "department_name": "تقنية المعلومات",
        "account_status": "ACTIVE"
      }
    }
  ],
  "total": 1
}
```

## ملاحظات مهمة
- يكفي تضمين الحقول الأساسية للعرض داخل الجدول:
  - `employee_id`, `name_ar`, `name_en`, `job_title`, `department_name`, `department_id`, `account_status`
- هذا التضمين يغني عن أي طلب إضافي للموظف.

---
**نتيجة متوقعة:** استدعاء API واحد فقط لصفحة الطلبات مع أداء أسرع.
