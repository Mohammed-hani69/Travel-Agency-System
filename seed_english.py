from models import db, Admin, Currency, Employee, Expense, Hotel, Ticket, Visa
from werkzeug.security import generate_password_hash
from datetime import datetime, date
import json
from currency_utils import convert_currency  # تم إضافة هذا السطر

# This script seeds the database with English demo data for all tables.
def seed_english():
    # 1. Currencies
    if not Currency.query.filter_by(code='EGP').first():
        egp = Currency(code='EGP', name='Egyptian Pound', symbol='EGP', exchange_rate=1.0, is_base=True)
        db.session.add(egp)
        db.session.commit()
    else:
        egp = Currency.query.filter_by(code='EGP').first()
    usd = Currency.query.filter_by(code='USD').first()
    if not usd:
        usd = Currency(code='USD', name='US Dollar', symbol='$', exchange_rate=48.0)
        db.session.add(usd)
        db.session.commit()
    eur = Currency.query.filter_by(code='EUR').first()
    if not eur:
        eur = Currency(code='EUR', name='Euro', symbol='€', exchange_rate=52.0)
        db.session.add(eur)
        db.session.commit()
    sar = Currency.query.filter_by(code='SAR').first()
    if not sar:
        sar = Currency(code='SAR', name='Saudi Riyal', symbol='SAR', exchange_rate=12.8)
        db.session.add(sar)
        db.session.commit()

    # 2. Admin user
    if not Admin.query.filter_by(email='admin@en.com').first():
        admin = Admin(
            email='admin@en.com',
            password_hash=generate_password_hash('admin123'),
            preferred_currency_id=egp.id,
            role='admin',
            permissions=json.dumps(['dashboard', 'currencies', 'expenses', 'salaries', 'tickets', 'hotels', 'export', 'users', 'visas'], ensure_ascii=False)
        )
        db.session.add(admin)
        db.session.commit()
    else:
        admin = Admin.query.filter_by(email='admin@en.com').first()

    # 3. Employee
    if not Employee.query.filter_by(name='John Smith').first():
        emp = Employee(
            name='John Smith',
            job_title='Accountant',
            salary_amount=10000,
            currency_id=egp.id,
            payment_date=date(2025, 6, 1),
            created_by=admin.id,
            salary_amount_egp=10000,
            salary_amount_usd=convert_currency(10000, egp.id, usd.id),
            salary_amount_eur=convert_currency(10000, egp.id, eur.id),
            salary_amount_sar=convert_currency(10000, egp.id, sar.id)
        )
        db.session.add(emp)
        db.session.commit()

    # 4. Expense
    if not Expense.query.filter_by(name='Office Rent').first():
        exp = Expense(
            name='Office Rent',
            amount=5000,
            currency_id=egp.id,
            date=date(2025, 6, 5),
            notes='Monthly rent',
            month_year='2025-06',
            created_by=admin.id,
            amount_egp=5000,
            amount_usd=convert_currency(5000, egp.id, usd.id),
            amount_eur=convert_currency(5000, egp.id, eur.id),
            amount_sar=convert_currency(5000, egp.id, sar.id)
        )
        db.session.add(exp)
        db.session.commit()

    # 5. Ticket
    if not Ticket.query.filter_by(ticket_number='EN123456').first():
        ticket = Ticket(
            ticket_number='EN123456',
            pnr='ENPNR001',
            departure_location='Cairo',
            arrival_location='Dubai',
            purchase_price=4000,
            selling_price=5000,
            currency_id=egp.id,
            payment_fees=100,
            profit=900,
            month_year='2025-06',
            created_by=admin.id,
            payment_method='Credit Card',
            notes='Business class',
            purchase_price_egp=4000,
            purchase_price_usd=convert_currency(4000, egp.id, usd.id),
            purchase_price_eur=convert_currency(4000, egp.id, eur.id),
            purchase_price_sar=convert_currency(4000, egp.id, sar.id),
            selling_price_egp=5000,
            selling_price_usd=convert_currency(5000, egp.id, usd.id),
            selling_price_eur=convert_currency(5000, egp.id, eur.id),
            selling_price_sar=convert_currency(5000, egp.id, sar.id),
            payment_fees_egp=100,
            payment_fees_usd=convert_currency(100, egp.id, usd.id),
            payment_fees_eur=convert_currency(100, egp.id, eur.id),
            payment_fees_sar=convert_currency(100, egp.id, sar.id),
            profit_egp=900,
            profit_usd=convert_currency(900, egp.id, usd.id),
            profit_eur=convert_currency(900, egp.id, eur.id),
            profit_sar=convert_currency(900, egp.id, sar.id)
        )
        db.session.add(ticket)
        db.session.commit()

    # 6. Hotel
    if not Hotel.query.filter_by(booking_number='ENHOTEL001').first():
        hotel = Hotel(
            booking_number='ENHOTEL001',
            hotel_name='Nile Hotel',
            guest_name='Michael Brown',
            check_in_date=date(2025, 6, 10),
            check_out_date=date(2025, 6, 15),
            purchase_price=3000,
            selling_price=4000,
            currency_id=egp.id,
            payment_fees=100,
            profit=900,
            month_year='2025-06',
            created_by=admin.id,
            purchase_price_egp=3000,
            purchase_price_usd=convert_currency(3000, egp.id, usd.id),
            purchase_price_eur=convert_currency(3000, egp.id, eur.id),
            purchase_price_sar=convert_currency(3000, egp.id, sar.id),
            selling_price_egp=4000,
            selling_price_usd=convert_currency(4000, egp.id, usd.id),
            selling_price_eur=convert_currency(4000, egp.id, eur.id),
            selling_price_sar=convert_currency(4000, egp.id, sar.id),
            payment_fees_egp=100,
            payment_fees_usd=convert_currency(100, egp.id, usd.id),
            payment_fees_eur=convert_currency(100, egp.id, eur.id),
            payment_fees_sar=convert_currency(100, egp.id, sar.id),
            profit_egp=900,
            profit_usd=convert_currency(900, egp.id, usd.id),
            profit_eur=convert_currency(900, egp.id, eur.id),
            profit_sar=convert_currency(900, egp.id, sar.id),
            booking_source='Booking.com',
            passengers_count=2,
            payment_method='Cash',
            notes='VIP guest'
        )
        db.session.add(hotel)
        db.session.commit()

    # 7. Visa
    if not Visa.query.filter_by(visa_type='Tourist').first():
        visa = Visa(
            visa_type='Tourist',
            visa_duration='30 days',  # مدة التأشيرة
            visa_country='UAE',       # بلد التأشيرة
            visa_source='Embassy',
            owner_name='Sarah Johnson',
            purchase_price=1500,
            selling_price=2000,
            payment_method='Bank Transfer',
            payment_fees=50,
            profit=450,
            currency_id=egp.id,
            month_year='2025-06',
            created_by=admin.id,
            notes='Urgent',
            purchase_price_egp=1500,
            purchase_price_usd=convert_currency(1500, egp.id, usd.id),
            purchase_price_eur=convert_currency(1500, egp.id, eur.id),
            purchase_price_sar=convert_currency(1500, egp.id, sar.id),
            selling_price_egp=2000,
            selling_price_usd=convert_currency(2000, egp.id, usd.id),
            selling_price_eur=convert_currency(2000, egp.id, eur.id),
            selling_price_sar=convert_currency(2000, egp.id, sar.id),
            payment_fees_egp=50,
            payment_fees_usd=convert_currency(50, egp.id, usd.id),
            payment_fees_eur=convert_currency(50, egp.id, eur.id),
            payment_fees_sar=convert_currency(50, egp.id, sar.id),
            profit_egp=450,
            profit_usd=convert_currency(450, egp.id, usd.id),
            profit_eur=convert_currency(450, egp.id, eur.id),
            profit_sar=convert_currency(450, egp.id, sar.id)
        )
        db.session.add(visa)
        db.session.commit()

if __name__ == '__main__':
    from app import app
    with app.app_context():
        seed_english()
        print('English demo data seeded successfully!')
