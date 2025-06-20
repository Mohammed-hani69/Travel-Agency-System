from models import db, Admin, Currency, Employee, Expense, Hotel, Ticket
from werkzeug.security import generate_password_hash
from datetime import datetime, date
from flask import Flask
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_agency.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

    # 1. العملات
    if not Currency.query.filter_by(code='EGP').first():
        egp = Currency(code='EGP', name='Egyptian Pound', symbol='ج.م', exchange_rate=1.0, is_base=True)
        db.session.add(egp)
        db.session.commit()
    else:
        egp = Currency.query.filter_by(code='EGP').first()

    # إضافة عملات أخرى
    currencies = [
        {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'exchange_rate': 48.0},
        {'code': 'SAR', 'name': 'Saudi Riyal', 'symbol': '﷼', 'exchange_rate': 12.8},
        {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'exchange_rate': 52.0},
    ]
    for c in currencies:
        if not Currency.query.filter_by(code=c['code']).first():
            db.session.add(Currency(code=c['code'], name=c['name'], symbol=c['symbol'], exchange_rate=c['exchange_rate'], is_base=False))
    db.session.commit()

    # 2. حساب الأدمن
    if not Admin.query.filter_by(email='admin@gmail.com').first():
        admin = Admin(
            email='admin@admin.com',
            password_hash=generate_password_hash('12345678'),
            preferred_currency_id=egp.id,
            role='admin',
            permissions=json.dumps(['dashboard', 'currencies', 'expenses', 'salaries', 'tickets', 'hotels', 'export', 'users'], ensure_ascii=False)
        )
        db.session.add(admin)
        db.session.commit()

    # 3. موظف تجريبي
    if not Employee.query.first():
        emp = Employee(
            name='أحمد علي',
            job_title='محاسب',
            salary_amount=10000,
            currency_id=egp.id,
            payment_date=date(2025, 6, 1)
        )
        db.session.add(emp)
        db.session.commit()

    # 4. مصروف تجريبي
    if not Expense.query.first():
        exp = Expense(
            name='إيجار المكتب',
            amount=5000,
            currency_id=egp.id,
            date=date(2025, 6, 5),
            notes='إيجار شهري',
            month_year='2025-06'
        )
        db.session.add(exp)
        db.session.commit()

    # 5. تذكرة طيران تجريبية
    if not Ticket.query.first():
        ticket = Ticket(
            ticket_number='1234567890',
            pnr='PNR001',
            departure_location='القاهرة',
            arrival_location='دبي',
            purchase_price=4000,
            selling_price=5000,
            currency_id=egp.id,
            payment_fees=100,
            profit=900,
            month_year='2025-06'
        )
        db.session.add(ticket)
        db.session.commit()

    # 6. حجز فندق تجريبي
    if not Hotel.query.first():
        hotel = Hotel(
            booking_number='HOTEL001',
            hotel_name='فندق النيل',
            guest_name='محمد حسن',
            check_in_date=date(2025, 6, 10),
            check_out_date=date(2025, 6, 15),
            purchase_price=3000,
            selling_price=4000,
            currency_id=egp.id,
            payment_fees=100,
            profit=900,
            month_year='2025-06'
        )
        db.session.add(hotel)
        db.session.commit()

    print('تمت إضافة البيانات التجريبية بنجاح!')
