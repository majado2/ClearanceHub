# تقارير الطلبات – CSV

هذا الملف يشرح لمبرمج الفرونت‑إند طريقة تصدير الطلبات بصيغة CSV مع **جميع معلومات الموظف**.

## المسار
```
GET /reports/requests/csv
```

## التوثيق
المسار محمي ويحتاج Bearer Token.

```
Authorization: Bearer <access_token>
```

## الفلاتر (Query Params)
- `type`: نوع الطلب (اختياري)
  - `card` أو `access`
- `status`: حالة الطلب (اختياري)
  - أمثلة: `PENDING_MANAGER_APPROVAL`, `PENDING_SECURITY_APPROVAL`, `IN_PROCESS`, `COMPLETED`
- `from`: تاريخ بداية (اختياري) بصيغة `YYYY-MM-DD`
- `to`: تاريخ نهاية (اختياري) بصيغة `YYYY-MM-DD`

مثال:
```
GET /reports/requests/csv?type=card&status=PENDING_SECURITY_APPROVAL&from=2026-01-01&to=2026-02-01
```

## الأعمدة في ملف CSV
> الأعمدة ثابتة لكل الأنواع (بطاقة/تصريح).

1. `request_id`
2. `request_type` (CARD أو ACCESS)
3. `status`
4. `request_date`
5. `created_at`
6. `updated_at`
7. `submitted_by_employee_id`
8. `employee_id`
9. `employee_name_ar`
10. `employee_name_en`
11. `job_title`
12. `nationality_ar`
13. `nationality_en`
14. `department_id`
15. `department_name`
16. `account_status`
17. `card_request_type` (فقط للبطاقات)
18. `card_request_reason` (فقط للبطاقات)
19. `photo_url` (فقط للبطاقات)
20. `permit_request_reason` (فقط للتصاريح)
21. `permit_area_ids` (قائمة IDs مفصولة بفاصلة)
22. `permit_area_names` (قائمة أسماء مفصولة بفاصلة)
23. `manager_employee_id`
24. `manager_updated_at`
25. `security_employee_id`
26. `security_updated_at`
27. `printing_employee_id`
28. `printing_updated_at`
29. `rejection_reason`

## ملاحظات صلاحيات
- مدير القسم يشاهد طلبات قسمه فقط.
- موظف الطباعة يشاهد فقط الحالات `IN_PROCESS` و `COMPLETED`.
- الأدمن/الأمن يشاهدون جميع الطلبات (حسب الدور).

## مثال cURL
```
curl -X GET "https://<host>/reports/requests/csv?type=card" \
  -H "Authorization: Bearer <token>"
```
