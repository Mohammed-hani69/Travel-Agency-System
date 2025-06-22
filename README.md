# Travel Agency System

نظام إدارة وكالة السفر

## المميزات
- إدارة التذاكر والفنادق والمصروفات والرواتب
- دعم تعدد العملات وتحويل العملة
- لوحة تحكم تفاعلية مع رسوم بيانية للأرباح والخسائر
- دعم كامل للغتين العربية والإنجليزية مع اتجاه الصفحة المناسب
- تصدير البيانات
- إدارة المستخدمين وصلاحياتهم

## المتطلبات
- Python 3.11 أو أحدث
- Flask
- Flask-Babel
- Flask-SQLAlchemy
- Flask-Login
- pandas, openpyxl, reportlab

## بدء التشغيل
1. تثبيت المتطلبات:
   ```
   pip install -r requirements.txt
   ```
2. تهيئة قاعدة البيانات:
   ```
   python seed.py
   ```
3. تجميع ملفات الترجمة:
   ```
   pybabel compile -d translations
   ```
4. تشغيل التطبيق:
   ```
   flask run
   ```

## الترجمة
- يمكنك تغيير اللغة من القائمة الجانبية.
- جميع النصوص تُترجم تلقائياً حسب اللغة المختارة.

## المجلدات المهمة
- `templates/` : قوالب الواجهة
- `translations/` : ملفات الترجمة
- `static/` : ملفات CSS وJS

## المساهمة
للمساهمة يرجى عمل Fork ثم Pull Request.

## رفع المشروع على GitHub

1. أنشئ مستودع جديد على GitHub من خلال الموقع.
2. في مجلد المشروع، افتح الطرفية ونفذ الأوامر التالية:
   ```
   git init
   git add .
   git commit -m "v 1.1.2"
   git branch -M main
   git remote add origin https://github.com/Mohammed-hani69/Travel-Agency-System.git
   git push -u origin main
   ```
   استبدل `USERNAME` و`REPO_NAME` باسم المستخدم واسم المستودع الخاص بك.
3. بعد الرفع، ستجد المشروع كاملاً على GitHub.

---
تم تطوير النظام لدعم وكالات السفر الصغيرة والمتوسطة مع واجهة سهلة الاستخدام ودعم كامل للغة العربية.
