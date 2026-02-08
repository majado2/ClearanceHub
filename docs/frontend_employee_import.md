# استيراد بيانات الموظفين (CSV)

هذا المستند يشرح لمبرمج الفرونت‑إند آلية رفع ملف الموظفين من النظام الخارجي.

---

## المسار
```
POST /employees/import
```

## التوثيق
المسار محمي ويحتاج Bearer Token بصلاحية **ADMIN / SYSTEM_ADMIN**.

```
Authorization: Bearer <access_token>
```

## نوع الطلب
- `multipart/form-data`
- الحقل المطلوب: `file` (ملف CSV)

مثال (FormData):
```
file: employees.csv
```

---

## ملاحظة مهمة (DROP TABLE)
عند الاستيراد يتم:
1) إسقاط جدول `employees` بالكامل
2) إعادة بنائه
3) إدخال البيانات الجديدة من الملف

> هذا يعني أن جدول الموظفين يُعاد بناؤه بالكامل في كل عملية استيراد.

---

## أسماء الأعمدة داخل ملف CSV
يجب أن يحتوي الملف على الأعمدة التالية بالضبط:

- `MedID`
- `EmpNameAR`
- `EmpNameEN`
- `CountryNameEN`
- `CountryNameAR`
- `DepID`
- `DepartmentName`
- `EmpID`
- `EmpStatusName`
- `JobTitleNameSum`

---

## التحويلات المعتمدة
- `MedID` → `med_id`
- `EmpID` → `employee_id`
- `EmpNameAR` → `name_ar`
- `EmpNameEN` → `name_en`
- `JobTitleNameSum` → `job_title`
- `CountryNameAR` → `nationality_ar`
- `CountryNameEN` → `nationality_en`
- `DepID` → `department_id`
- `DepartmentName` → `department_name`
- `EmpStatusName` → `account_status`

### قواعد حالة الموظف
- إذا كانت القيمة **"على رأس العمل"** → `ACTIVE`
- أي قيمة أخرى → `SUSPENDED`

---

## الاستجابة
```
{ "imported": 1500 }
```

---

## ملاحظات مهمة
- يجب أن يكون الملف UTF‑8 (يدعم العربية).
- إذا كان هناك خطأ في الأعمدة أو البيانات سيتم إرجاع خطأ 400.
- يجب التأكد أن الموظفين المرتبطين بصلاحيات الدخول موجودون في الملف حتى لا يتعطل الدخول.
