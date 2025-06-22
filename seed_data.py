from models import db, Admin, Employee, Expense, Hotel, Ticket, Visa, Currency
from currency_utils import convert_currency
from werkzeug.security import generate_password_hash
from datetime import date
from app import app

with app.app_context():
    # إضافة مستخدم أدمن
    if not Admin.query.filter_by(email='admin@demo.com').first():
        admin = Admin(
            email='admin@demo.com',
            password_hash=generate_password_hash('admin123'),
            preferred_currency_id=Currency.query.filter_by(is_base=True).first().id,
            role='admin',
            permissions='["dashboard", "currencies", "expenses", "salaries", "tickets", "hotels", "export", "users", "visas"]'
        )
        db.session.add(admin)
        db.session.commit()
    else:
        admin = Admin.query.filter_by(email='admin@demo.com').first()

    # إضافة موظف
    if not Employee.query.filter_by(name='John Doe').first():
        salary = 5000
        currency_id = Currency.query.filter_by(code='SAR').first().id
        payment_date = date(2025, 6, 1)
        emp = Employee(
            name='John Doe',
            job_title='Accountant',
            salary_amount=salary,
            currency_id=currency_id,
            payment_date=payment_date,
            created_by=admin.id,
            salary_amount_egp=convert_currency(salary, currency_id, Currency.query.filter_by(code='EGP').first().id),
            salary_amount_usd=convert_currency(salary, currency_id, Currency.query.filter_by(code='USD').first().id),
            salary_amount_eur=convert_currency(salary, currency_id, Currency.query.filter_by(code='EUR').first().id),
            salary_amount_sar=convert_currency(salary, currency_id, Currency.query.filter_by(code='SAR').first().id)
        )
        db.session.add(emp)
        db.session.commit()

    # إضافة مصروف
    if not Expense.query.filter_by(name='Office Rent').first():
        amount = 3000
        currency_id = Currency.query.filter_by(code='SAR').first().id
        exp = Expense(
            name='Office Rent',
            amount=amount,
            currency_id=currency_id,
            date=date(2025, 6, 5),
            notes='Monthly rent',
            month_year='2025-06',
            created_by=admin.id,
            amount_egp=convert_currency(amount, currency_id, Currency.query.filter_by(code='EGP').first().id),
            amount_usd=convert_currency(amount, currency_id, Currency.query.filter_by(code='USD').first().id),
            amount_eur=convert_currency(amount, currency_id, Currency.query.filter_by(code='EUR').first().id),
            amount_sar=convert_currency(amount, currency_id, Currency.query.filter_by(code='SAR').first().id)
        )
        db.session.add(exp)
        db.session.commit()

    # إضافة تذكرة
    if not Ticket.query.filter_by(ticket_number='TICK123').first():
        purchase_price = 2000
        selling_price = 2500
        payment_fees = 100
        currency_id = Currency.query.filter_by(code='SAR').first().id
        profit = selling_price - purchase_price - payment_fees
        ticket = Ticket(
            ticket_number='TICK123',
            pnr='PNR001',
            departure_location='Riyadh',
            arrival_location='Cairo',
            purchase_price=purchase_price,
            selling_price=selling_price,
            currency_id=currency_id,
            payment_fees=payment_fees,
            profit=profit,
            month_year='2025-06',
            created_by=admin.id,
            payment_method='Credit Card',
            notes='Business class',
            purchase_price_egp=convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='EGP').first().id),
            purchase_price_usd=convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='USD').first().id),
            purchase_price_eur=convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='EUR').first().id),
            purchase_price_sar=convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='SAR').first().id),
            selling_price_egp=convert_currency(selling_price, currency_id, Currency.query.filter_by(code='EGP').first().id),
            selling_price_usd=convert_currency(selling_price, currency_id, Currency.query.filter_by(code='USD').first().id),
            selling_price_eur=convert_currency(selling_price, currency_id, Currency.query.filter_by(code='EUR').first().id),
            selling_price_sar=convert_currency(selling_price, currency_id, Currency.query.filter_by(code='SAR').first().id),
            payment_fees_egp=convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='EGP').first().id),
            payment_fees_usd=convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='USD').first().id),
            payment_fees_eur=convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='EUR').first().id),
            payment_fees_sar=convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='SAR').first().id),
            profit_egp=convert_currency(profit, currency_id, Currency.query.filter_by(code='EGP').first().id),
            profit_usd=convert_currency(profit, currency_id, Currency.query.filter_by(code='USD').first().id),
            profit_eur=convert_currency(profit, currency_id, Currency.query.filter_by(code='EUR').first().id),
            profit_sar=convert_currency(profit, currency_id, Currency.query.filter_by(code='SAR').first().id)
        )
        db.session.add(ticket)
        db.session.commit()

    # إضافة فندق
    if not Hotel.query.filter_by(booking_number='HOTEL001').first():
        purchase_price = 3000
        selling_price = 4000
        payment_fees = 200
        currency_id = Currency.query.filter_by(code='SAR').first().id
        profit = selling_price - purchase_price - payment_fees
        hotel = Hotel(
            booking_number='HOTEL001',
            hotel_name='Hilton',
            guest_name='Ali Ahmed',
            check_in_date=date(2025, 6, 10),
            check_out_date=date(2025, 6, 15),
            purchase_price=purchase_price,
            selling_price=selling_price,
            currency_id=currency_id,
            payment_fees=payment_fees,
            profit=profit,
            month_year='2025-06',
            created_by=admin.id,
            purchase_price_egp=convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='EGP').first().id),
            purchase_price_usd=convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='USD').first().id),
            purchase_price_eur=convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='EUR').first().id),
            purchase_price_sar=convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='SAR').first().id),
            selling_price_egp=convert_currency(selling_price, currency_id, Currency.query.filter_by(code='EGP').first().id),
            selling_price_usd=convert_currency(selling_price, currency_id, Currency.query.filter_by(code='USD').first().id),
            selling_price_eur=convert_currency(selling_price, currency_id, Currency.query.filter_by(code='EUR').first().id),
            selling_price_sar=convert_currency(selling_price, currency_id, Currency.query.filter_by(code='SAR').first().id),
            payment_fees_egp=convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='EGP').first().id),
            payment_fees_usd=convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='USD').first().id),
            payment_fees_eur=convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='EUR').first().id),
            payment_fees_sar=convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='SAR').first().id),
            profit_egp=convert_currency(profit, currency_id, Currency.query.filter_by(code='EGP').first().id),
            profit_usd=convert_currency(profit, currency_id, Currency.query.filter_by(code='USD').first().id),
            profit_eur=convert_currency(profit, currency_id, Currency.query.filter_by(code='EUR').first().id),
            profit_sar=convert_currency(profit, currency_id, Currency.query.filter_by(code='SAR').first().id),
            booking_source='Booking.com',
            passengers_count=2,
            payment_method='Cash',
            notes='VIP guest'
        )
        db.session.add(hotel)
        db.session.commit()

    # إضافة تأشيرة
    if not Visa.query.filter_by(visa_type='Tourist').first():
        purchase_price = 1500
        selling_price = 2000
        payment_fees = 50
        currency_id = Currency.query.filter_by(code='SAR').first().id
        profit = selling_price - purchase_price - payment_fees
        visa = Visa(
            visa_type='Tourist',
            visa_duration='30 days',
            visa_country='UAE',
            visa_source='Embassy',
            owner_name='Sarah Johnson',
            purchase_price=purchase_price,
            selling_price=selling_price,
            payment_method='Bank Transfer',
            payment_fees=payment_fees,
            profit=profit,
            currency_id=currency_id,
            month_year='2025-06',
            created_by=admin.id,
            notes='Urgent',
            purchase_price_egp=convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='EGP').first().id),
            purchase_price_usd=convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='USD').first().id),
            purchase_price_eur=convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='EUR').first().id),
            purchase_price_sar=convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='SAR').first().id),
            selling_price_egp=convert_currency(selling_price, currency_id, Currency.query.filter_by(code='EGP').first().id),
            selling_price_usd=convert_currency(selling_price, currency_id, Currency.query.filter_by(code='USD').first().id),
            selling_price_eur=convert_currency(selling_price, currency_id, Currency.query.filter_by(code='EUR').first().id),
            selling_price_sar=convert_currency(selling_price, currency_id, Currency.query.filter_by(code='SAR').first().id),
            payment_fees_egp=convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='EGP').first().id),
            payment_fees_usd=convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='USD').first().id),
            payment_fees_eur=convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='EUR').first().id),
            payment_fees_sar=convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='SAR').first().id),
            profit_egp=convert_currency(profit, currency_id, Currency.query.filter_by(code='EGP').first().id),
            profit_usd=convert_currency(profit, currency_id, Currency.query.filter_by(code='USD').first().id),
            profit_eur=convert_currency(profit, currency_id, Currency.query.filter_by(code='EUR').first().id),
            profit_sar=convert_currency(profit, currency_id, Currency.query.filter_by(code='SAR').first().id)
        )
        db.session.add(visa)
        db.session.commit()

print('Seed data inserted successfully.')
