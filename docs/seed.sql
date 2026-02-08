-- Seed data for ClearanceHub (Arabic)
-- Assumes empty tables and the PRD schema migration applied.

-- Roles
INSERT INTO roles (role_code, role_name) VALUES
  ('DEPT_MANAGER', 'مدير قسم'),
  ('SECURITY_OFFICER', 'ضابط أمن'),
  ('CARD_PRINTING', 'قسم طباعة البطاقات'),
  ('ADMIN', 'مدير النظام');

-- Employees (10)
INSERT INTO employees (
  employee_id, name_ar, name_en, job_title, nationality_ar, nationality_en,
  department_id, department_name, account_status
) VALUES
  ('E1001', 'أحمد علي', 'Ahmed Ali', 'مدير تقنية المعلومات', 'سعودي', 'Saudi', 10, 'تقنية المعلومات', 'ACTIVE'),
  ('E1002', 'محمد سالم', 'Mohammed Salem', 'مدير المرافق', 'سعودي', 'Saudi', 20, 'المرافق', 'ACTIVE'),
  ('E1003', 'خالد ناصر', 'Khaled Nasser', 'ضابط أمن', 'سعودي', 'Saudi', 30, 'الأمن', 'ACTIVE'),
  ('E1004', 'فيصل عبدالله', 'Faisal Abdullah', 'مشرف طباعة', 'سعودي', 'Saudi', 40, 'الطباعة', 'ACTIVE'),
  ('E1005', 'يوسف إبراهيم', 'Yousef Ibrahim', 'مسؤول نظم', 'سعودي', 'Saudi', 50, 'الإدارة', 'ACTIVE'),
  ('E1006', 'سارة أحمد', 'Sara Ahmed', 'مهندسة نظم', 'مصرية', 'Egyptian', 10, 'تقنية المعلومات', 'ACTIVE'),
  ('E1007', 'نورة محمد', 'Noura Mohammed', 'محللة نظم', 'سعودية', 'Saudi', 10, 'تقنية المعلومات', 'ACTIVE'),
  ('E1008', 'ريم صالح', 'Reem Saleh', 'مشرفة صيانة', 'سعودية', 'Saudi', 20, 'المرافق', 'ACTIVE'),
  ('E1009', 'فهد حسن', 'Fahd Hassan', 'فني مرافق', 'سعودي', 'Saudi', 20, 'المرافق', 'ACTIVE'),
  ('E1010', 'علي عبدالعزيز', 'Ali Abdulaziz', 'مبرمج', 'سعودي', 'Saudi', 10, 'تقنية المعلومات', 'ACTIVE');

-- Employee permissions (for staff logins)
INSERT INTO employee_permissions (employee_id, internal_email, role_id) VALUES
  ('E1001', 'manager.it@company.com', (SELECT id FROM roles WHERE role_code = 'DEPT_MANAGER')),
  ('E1002', 'manager.fac@company.com', (SELECT id FROM roles WHERE role_code = 'DEPT_MANAGER')),
  ('E1003', 'security@company.com', (SELECT id FROM roles WHERE role_code = 'SECURITY_OFFICER')),
  ('E1004', 'printing@company.com', (SELECT id FROM roles WHERE role_code = 'CARD_PRINTING')),
  ('E1005', 'admin@company.com', (SELECT id FROM roles WHERE role_code = 'ADMIN'));

-- Areas (5)
INSERT INTO areas (area_id, area_name, status) VALUES
  (1, 'غرفة السيرفرات', 'ACTIVE'),
  (2, 'مركز البيانات', 'ACTIVE'),
  (3, 'المخازن', 'ACTIVE'),
  (4, 'الورشة', 'ACTIVE'),
  (5, 'موقف الخدمات', 'ACTIVE');

-- Card requests: 3 لكل حالة = 24 طلب
INSERT INTO card_requests (
  id, employee_id, submitted_by_employee_id, request_date, request_type, request_reason, photo_url,
  manager_employee_id, manager_updated_at, security_employee_id, security_updated_at,
  printing_employee_id, printing_updated_at, rejection_reason, status, created_at, updated_at
) VALUES
  -- DRAFT
  (1, 'E1006', NULL, DATE_SUB(NOW(), INTERVAL 20 DAY), 'NEW', 'طلب جديد', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'DRAFT', DATE_SUB(NOW(), INTERVAL 20 DAY), DATE_SUB(NOW(), INTERVAL 20 DAY)),
  (2, 'E1007', NULL, DATE_SUB(NOW(), INTERVAL 19 DAY), 'RENEW', 'تجديد بطاقة', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'DRAFT', DATE_SUB(NOW(), INTERVAL 19 DAY), DATE_SUB(NOW(), INTERVAL 19 DAY)),
  (3, 'E1008', NULL, DATE_SUB(NOW(), INTERVAL 18 DAY), 'REPLACE_LOST', 'بدل فاقد', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'DRAFT', DATE_SUB(NOW(), INTERVAL 18 DAY), DATE_SUB(NOW(), INTERVAL 18 DAY)),

  -- PENDING_MANAGER_APPROVAL
  (4, 'E1006', NULL, DATE_SUB(NOW(), INTERVAL 17 DAY), 'NEW', 'طلب جديد', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'PENDING_MANAGER_APPROVAL', DATE_SUB(NOW(), INTERVAL 17 DAY), DATE_SUB(NOW(), INTERVAL 17 DAY)),
  (5, 'E1007', 'E1001', DATE_SUB(NOW(), INTERVAL 16 DAY), 'RENEW', 'تجديد بطاقة', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'PENDING_MANAGER_APPROVAL', DATE_SUB(NOW(), INTERVAL 16 DAY), DATE_SUB(NOW(), INTERVAL 16 DAY)),
  (6, 'E1008', 'E1002', DATE_SUB(NOW(), INTERVAL 16 DAY), 'NEW', 'طلب بالنيابة', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'PENDING_MANAGER_APPROVAL', DATE_SUB(NOW(), INTERVAL 16 DAY), DATE_SUB(NOW(), INTERVAL 16 DAY)),

  -- REJECTED_BY_MANAGER
  (7, 'E1006', NULL, DATE_SUB(NOW(), INTERVAL 15 DAY), 'NEW', 'بيانات ناقصة', NULL, 'E1001', DATE_SUB(NOW(), INTERVAL 14 DAY), NULL, NULL, NULL, NULL, 'نقص البيانات', 'REJECTED_BY_MANAGER', DATE_SUB(NOW(), INTERVAL 15 DAY), DATE_SUB(NOW(), INTERVAL 14 DAY)),
  (8, 'E1007', NULL, DATE_SUB(NOW(), INTERVAL 15 DAY), 'RENEW', 'تجديد بطاقة', NULL, 'E1001', DATE_SUB(NOW(), INTERVAL 14 DAY), NULL, NULL, NULL, NULL, 'المستندات غير واضحة', 'REJECTED_BY_MANAGER', DATE_SUB(NOW(), INTERVAL 15 DAY), DATE_SUB(NOW(), INTERVAL 14 DAY)),
  (9, 'E1008', NULL, DATE_SUB(NOW(), INTERVAL 14 DAY), 'REPLACE_LOST', 'بدل فاقد', NULL, 'E1002', DATE_SUB(NOW(), INTERVAL 13 DAY), NULL, NULL, NULL, NULL, 'مرفقات غير مكتملة', 'REJECTED_BY_MANAGER', DATE_SUB(NOW(), INTERVAL 14 DAY), DATE_SUB(NOW(), INTERVAL 13 DAY)),

  -- PENDING_SECURITY_APPROVAL
  (10, 'E1006', NULL, DATE_SUB(NOW(), INTERVAL 13 DAY), 'NEW', 'طلب جديد', NULL, 'E1001', DATE_SUB(NOW(), INTERVAL 12 DAY), NULL, NULL, NULL, NULL, NULL, 'PENDING_SECURITY_APPROVAL', DATE_SUB(NOW(), INTERVAL 13 DAY), DATE_SUB(NOW(), INTERVAL 12 DAY)),
  (11, 'E1007', NULL, DATE_SUB(NOW(), INTERVAL 13 DAY), 'RENEW', 'تجديد بطاقة', NULL, 'E1001', DATE_SUB(NOW(), INTERVAL 12 DAY), NULL, NULL, NULL, NULL, NULL, 'PENDING_SECURITY_APPROVAL', DATE_SUB(NOW(), INTERVAL 13 DAY), DATE_SUB(NOW(), INTERVAL 12 DAY)),
  (12, 'E1008', NULL, DATE_SUB(NOW(), INTERVAL 12 DAY), 'NEW', 'طلب جديد', NULL, 'E1002', DATE_SUB(NOW(), INTERVAL 11 DAY), NULL, NULL, NULL, NULL, NULL, 'PENDING_SECURITY_APPROVAL', DATE_SUB(NOW(), INTERVAL 12 DAY), DATE_SUB(NOW(), INTERVAL 11 DAY)),

  -- REJECTED_BY_SECURITY
  (13, 'E1006', NULL, DATE_SUB(NOW(), INTERVAL 11 DAY), 'NEW', 'طلب جديد', NULL, 'E1001', DATE_SUB(NOW(), INTERVAL 10 DAY), 'E1003', DATE_SUB(NOW(), INTERVAL 9 DAY), NULL, NULL, 'ملاحظات أمنية', 'REJECTED_BY_SECURITY', DATE_SUB(NOW(), INTERVAL 11 DAY), DATE_SUB(NOW(), INTERVAL 9 DAY)),
  (14, 'E1007', NULL, DATE_SUB(NOW(), INTERVAL 11 DAY), 'RENEW', 'تجديد بطاقة', NULL, 'E1001', DATE_SUB(NOW(), INTERVAL 10 DAY), 'E1003', DATE_SUB(NOW(), INTERVAL 9 DAY), NULL, NULL, 'بيانات غير متطابقة', 'REJECTED_BY_SECURITY', DATE_SUB(NOW(), INTERVAL 11 DAY), DATE_SUB(NOW(), INTERVAL 9 DAY)),
  (15, 'E1008', NULL, DATE_SUB(NOW(), INTERVAL 10 DAY), 'REPLACE_LOST', 'بدل فاقد', NULL, 'E1002', DATE_SUB(NOW(), INTERVAL 9 DAY), 'E1003', DATE_SUB(NOW(), INTERVAL 8 DAY), NULL, NULL, 'سبب الرفض الأمني', 'REJECTED_BY_SECURITY', DATE_SUB(NOW(), INTERVAL 10 DAY), DATE_SUB(NOW(), INTERVAL 8 DAY)),

  -- IN_PROCESS
  (16, 'E1006', NULL, DATE_SUB(NOW(), INTERVAL 9 DAY), 'NEW', 'طلب جديد', NULL, 'E1001', DATE_SUB(NOW(), INTERVAL 8 DAY), 'E1003', DATE_SUB(NOW(), INTERVAL 7 DAY), NULL, NULL, NULL, 'IN_PROCESS', DATE_SUB(NOW(), INTERVAL 9 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY)),
  (17, 'E1007', NULL, DATE_SUB(NOW(), INTERVAL 9 DAY), 'RENEW', 'تجديد بطاقة', NULL, 'E1001', DATE_SUB(NOW(), INTERVAL 8 DAY), 'E1003', DATE_SUB(NOW(), INTERVAL 7 DAY), NULL, NULL, NULL, 'IN_PROCESS', DATE_SUB(NOW(), INTERVAL 9 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY)),
  (18, 'E1008', NULL, DATE_SUB(NOW(), INTERVAL 8 DAY), 'NEW', 'طلب جديد', NULL, 'E1002', DATE_SUB(NOW(), INTERVAL 7 DAY), 'E1003', DATE_SUB(NOW(), INTERVAL 6 DAY), NULL, NULL, NULL, 'IN_PROCESS', DATE_SUB(NOW(), INTERVAL 8 DAY), DATE_SUB(NOW(), INTERVAL 6 DAY)),

  -- COMPLETED
  (19, 'E1006', NULL, DATE_SUB(NOW(), INTERVAL 7 DAY), 'NEW', 'طلب جديد', NULL, 'E1001', DATE_SUB(NOW(), INTERVAL 6 DAY), 'E1003', DATE_SUB(NOW(), INTERVAL 5 DAY), 'E1004', DATE_SUB(NOW(), INTERVAL 4 DAY), NULL, 'COMPLETED', DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 4 DAY)),
  (20, 'E1007', NULL, DATE_SUB(NOW(), INTERVAL 7 DAY), 'RENEW', 'تجديد بطاقة', NULL, 'E1001', DATE_SUB(NOW(), INTERVAL 6 DAY), 'E1003', DATE_SUB(NOW(), INTERVAL 5 DAY), 'E1004', DATE_SUB(NOW(), INTERVAL 4 DAY), NULL, 'COMPLETED', DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 4 DAY)),
  (21, 'E1008', NULL, DATE_SUB(NOW(), INTERVAL 6 DAY), 'NEW', 'طلب جديد', NULL, 'E1002', DATE_SUB(NOW(), INTERVAL 5 DAY), 'E1003', DATE_SUB(NOW(), INTERVAL 4 DAY), 'E1004', DATE_SUB(NOW(), INTERVAL 3 DAY), NULL, 'COMPLETED', DATE_SUB(NOW(), INTERVAL 6 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY)),

  -- CANCELLED
  (22, 'E1006', NULL, DATE_SUB(NOW(), INTERVAL 5 DAY), 'NEW', 'إلغاء الطلب', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'CANCELLED', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY)),
  (23, 'E1007', NULL, DATE_SUB(NOW(), INTERVAL 4 DAY), 'RENEW', 'إلغاء الطلب', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'CANCELLED', DATE_SUB(NOW(), INTERVAL 4 DAY), DATE_SUB(NOW(), INTERVAL 4 DAY)),
  (24, 'E1008', NULL, DATE_SUB(NOW(), INTERVAL 4 DAY), 'REPLACE_LOST', 'إلغاء الطلب', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'CANCELLED', DATE_SUB(NOW(), INTERVAL 4 DAY), DATE_SUB(NOW(), INTERVAL 4 DAY));

-- Permit requests: 2 لكل حالة = 16 طلب
INSERT INTO permit_requests (
  id, employee_id, submitted_by_employee_id, request_date, request_reason,
  manager_employee_id, manager_updated_at, security_employee_id, security_updated_at,
  printing_employee_id, printing_updated_at, rejection_reason, status, created_at, updated_at
) VALUES
  -- DRAFT
  (1, 'E1006', NULL, DATE_SUB(NOW(), INTERVAL 20 DAY), 'تصريح صيانة', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'DRAFT', DATE_SUB(NOW(), INTERVAL 20 DAY), DATE_SUB(NOW(), INTERVAL 20 DAY)),
  (2, 'E1008', NULL, DATE_SUB(NOW(), INTERVAL 19 DAY), 'تصريح مؤقت', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'DRAFT', DATE_SUB(NOW(), INTERVAL 19 DAY), DATE_SUB(NOW(), INTERVAL 19 DAY)),

  -- PENDING_MANAGER_APPROVAL
  (3, 'E1007', NULL, DATE_SUB(NOW(), INTERVAL 18 DAY), 'تصريح عمل', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'PENDING_MANAGER_APPROVAL', DATE_SUB(NOW(), INTERVAL 18 DAY), DATE_SUB(NOW(), INTERVAL 18 DAY)),
  (4, 'E1009', 'E1002', DATE_SUB(NOW(), INTERVAL 17 DAY), 'تصريح صيانة', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'PENDING_MANAGER_APPROVAL', DATE_SUB(NOW(), INTERVAL 17 DAY), DATE_SUB(NOW(), INTERVAL 17 DAY)),

  -- REJECTED_BY_MANAGER
  (5, 'E1010', NULL, DATE_SUB(NOW(), INTERVAL 16 DAY), 'تصريح زيارة', 'E1001', DATE_SUB(NOW(), INTERVAL 15 DAY), NULL, NULL, NULL, NULL, 'بيانات غير مكتملة', 'REJECTED_BY_MANAGER', DATE_SUB(NOW(), INTERVAL 16 DAY), DATE_SUB(NOW(), INTERVAL 15 DAY)),
  (6, 'E1008', NULL, DATE_SUB(NOW(), INTERVAL 16 DAY), 'تصريح عمل', 'E1002', DATE_SUB(NOW(), INTERVAL 15 DAY), NULL, NULL, NULL, NULL, 'السبب غير واضح', 'REJECTED_BY_MANAGER', DATE_SUB(NOW(), INTERVAL 16 DAY), DATE_SUB(NOW(), INTERVAL 15 DAY)),

  -- PENDING_SECURITY_APPROVAL
  (7, 'E1006', NULL, DATE_SUB(NOW(), INTERVAL 15 DAY), 'تصريح صيانة', 'E1001', DATE_SUB(NOW(), INTERVAL 14 DAY), NULL, NULL, NULL, NULL, NULL, 'PENDING_SECURITY_APPROVAL', DATE_SUB(NOW(), INTERVAL 15 DAY), DATE_SUB(NOW(), INTERVAL 14 DAY)),
  (8, 'E1009', NULL, DATE_SUB(NOW(), INTERVAL 14 DAY), 'تصريح مؤقت', 'E1002', DATE_SUB(NOW(), INTERVAL 13 DAY), NULL, NULL, NULL, NULL, NULL, 'PENDING_SECURITY_APPROVAL', DATE_SUB(NOW(), INTERVAL 14 DAY), DATE_SUB(NOW(), INTERVAL 13 DAY)),

  -- REJECTED_BY_SECURITY
  (9, 'E1007', NULL, DATE_SUB(NOW(), INTERVAL 13 DAY), 'تصريح عمل', 'E1001', DATE_SUB(NOW(), INTERVAL 12 DAY), 'E1003', DATE_SUB(NOW(), INTERVAL 11 DAY), NULL, NULL, 'ملاحظات أمنية', 'REJECTED_BY_SECURITY', DATE_SUB(NOW(), INTERVAL 13 DAY), DATE_SUB(NOW(), INTERVAL 11 DAY)),
  (10, 'E1008', NULL, DATE_SUB(NOW(), INTERVAL 12 DAY), 'تصريح صيانة', 'E1002', DATE_SUB(NOW(), INTERVAL 11 DAY), 'E1003', DATE_SUB(NOW(), INTERVAL 10 DAY), NULL, NULL, 'رفض أمني', 'REJECTED_BY_SECURITY', DATE_SUB(NOW(), INTERVAL 12 DAY), DATE_SUB(NOW(), INTERVAL 10 DAY)),

  -- IN_PROCESS
  (11, 'E1006', NULL, DATE_SUB(NOW(), INTERVAL 11 DAY), 'تصريح عمل', 'E1001', DATE_SUB(NOW(), INTERVAL 10 DAY), 'E1003', DATE_SUB(NOW(), INTERVAL 9 DAY), NULL, NULL, NULL, 'IN_PROCESS', DATE_SUB(NOW(), INTERVAL 11 DAY), DATE_SUB(NOW(), INTERVAL 9 DAY)),
  (12, 'E1009', NULL, DATE_SUB(NOW(), INTERVAL 10 DAY), 'تصريح مؤقت', 'E1002', DATE_SUB(NOW(), INTERVAL 9 DAY), 'E1003', DATE_SUB(NOW(), INTERVAL 8 DAY), NULL, NULL, NULL, 'IN_PROCESS', DATE_SUB(NOW(), INTERVAL 10 DAY), DATE_SUB(NOW(), INTERVAL 8 DAY)),

  -- COMPLETED
  (13, 'E1007', NULL, DATE_SUB(NOW(), INTERVAL 9 DAY), 'تصريح عمل', 'E1001', DATE_SUB(NOW(), INTERVAL 8 DAY), 'E1003', DATE_SUB(NOW(), INTERVAL 7 DAY), 'E1004', DATE_SUB(NOW(), INTERVAL 6 DAY), NULL, 'COMPLETED', DATE_SUB(NOW(), INTERVAL 9 DAY), DATE_SUB(NOW(), INTERVAL 6 DAY)),
  (14, 'E1008', NULL, DATE_SUB(NOW(), INTERVAL 8 DAY), 'تصريح صيانة', 'E1002', DATE_SUB(NOW(), INTERVAL 7 DAY), 'E1003', DATE_SUB(NOW(), INTERVAL 6 DAY), 'E1004', DATE_SUB(NOW(), INTERVAL 5 DAY), NULL, 'COMPLETED', DATE_SUB(NOW(), INTERVAL 8 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY)),

  -- CANCELLED
  (15, 'E1006', NULL, DATE_SUB(NOW(), INTERVAL 7 DAY), 'إلغاء التصريح', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'CANCELLED', DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY)),
  (16, 'E1009', NULL, DATE_SUB(NOW(), INTERVAL 6 DAY), 'إلغاء التصريح', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'CANCELLED', DATE_SUB(NOW(), INTERVAL 6 DAY), DATE_SUB(NOW(), INTERVAL 6 DAY));

-- Permit request areas
INSERT INTO permit_request_areas (permit_request_id, area_id) VALUES
  (1, 1), (1, 2),
  (2, 3), (2, 4),
  (3, 1), (3, 3),
  (4, 2), (4, 5),
  (5, 4), (5, 5),
  (6, 1), (6, 2),
  (7, 3), (7, 5),
  (8, 2), (8, 4),
  (9, 1), (9, 2),
  (10, 3), (10, 4),
  (11, 2), (11, 5),
  (12, 1), (12, 3),
  (13, 4), (13, 5),
  (14, 2), (14, 3),
  (15, 1), (15, 5),
  (16, 2), (16, 4);
