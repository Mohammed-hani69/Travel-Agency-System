from flask import Flask, request, session, render_template, redirect, url_for, flash, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_required, logout_user
from flask_babel import Babel
from werkzeug.security import generate_password_hash
from models import db, Admin, Currency, Employee, Expense, Hotel, Ticket, Visa
from currency_utils import format_currency, convert_currency
from sqlalchemy import func
from datetime import datetime
import os
import json
from flask import abort
from functools import wraps
import pandas as pd
from io import BytesIO
from flask import send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_agency.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

babel = Babel(app)

@babel.localeselector
def get_locale():
    # Try to get locale from query string
    locale = request.args.get('lang')
    if locale in ['ar', 'en']:
        session['lang'] = locale
        return locale
    
    # Try to get locale from session
    if 'lang' in session:
        return session['lang']
    
    # Default to Arabic
    return 'ar'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

def create_tables():
    with app.app_context():
        db.create_all()
        # إضافة العملات الرئيسية إذا لم تكن موجودة
        main_currencies = [
            {'code': 'EGP', 'name': 'Egyptian Pound', 'symbol': 'ج.م', 'exchange_rate': 1.0, 'is_base': True},
            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'exchange_rate': 48.0, 'is_base': False},
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'exchange_rate': 52.0, 'is_base': False},
            {'code': 'SAR', 'name': 'Saudi Riyal', 'symbol': '﷼', 'exchange_rate': 12.8, 'is_base': False},
        ]
        for c in main_currencies:
            if not Currency.query.filter_by(code=c['code']).first():
                db.session.add(Currency(**c))
        db.session.commit()
        # إضافة حساب أدمن افتراضي إذا لم يكن موجوداً
        if not Admin.query.filter_by(email='ezezo291@gmail.com').first():
            default_currency = Currency.query.first()
            admin = Admin(
                email='ezezo291@gmail.com',
                password_hash=generate_password_hash('zxc65432'),
                preferred_currency_id=default_currency.id,
                role='admin',
                permissions=json.dumps(['dashboard', 'currencies', 'expenses', 'salaries', 'tickets', 'hotels', 'export', 'users'], ensure_ascii=False)
            )
            db.session.add(admin)
            db.session.commit()

def get_base_currency():
    return Currency.query.filter_by(is_base=True).first()

def get_all_currencies():
    return Currency.query.all()

def permission_required(page_key):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            try:
                allowed = json.loads(current_user.permissions) if current_user.permissions else []
            except Exception:
                allowed = []
            if current_user.role == 'admin' or page_key in allowed:
                return f(*args, **kwargs)
            return render_template('no_permission.html'), 403
        return decorated_function
    return decorator

@app.route('/', methods=['GET'])
@permission_required('dashboard')
def dashboard():
    base_currency = get_base_currency()
    month_year = request.args.get('month_year')
    if not month_year:
        month_year = datetime.now().strftime('%Y-%m')
    expenses = Expense.query.filter_by(created_by=current_user.id).all()
    employees = Employee.query.filter_by(created_by=current_user.id).all()
    tickets = Ticket.query.filter_by(created_by=current_user.id).all()
    hotels = Hotel.query.filter_by(created_by=current_user.id).all()

    # تحديد اسم العمود حسب العملة الرئيسية
    currency_code = base_currency.code.lower()
    expense_field = f'amount_{currency_code}'
    salary_field = f'salary_amount_{currency_code}'
    profit_field = f'profit_{currency_code}'

    months = []
    expenses_data = []
    salaries_data = []
    ticket_profits_data = []
    hotel_profits_data = []
    for m in range(1, 13):
        month_str = f"2025-{m:02d}"
        months.append(month_str)
        expenses_data.append(sum(getattr(e, expense_field) for e in expenses if e.month_year == month_str))
        salaries_data.append(sum(getattr(emp, salary_field) for emp in employees if emp.payment_date.strftime('%Y-%m') == month_str))
        ticket_profits_data.append(sum(getattr(t, profit_field) for t in tickets if t.month_year == month_str))
        hotel_profits_data.append(sum(getattr(h, profit_field) for h in hotels if h.month_year == month_str))
    total_expenses = sum(getattr(e, expense_field) for e in expenses if e.month_year == month_year)
    total_salaries = sum(getattr(emp, salary_field) for emp in employees if emp.payment_date.strftime('%Y-%m') == month_year)
    ticket_profits = sum(getattr(t, profit_field) for t in tickets if t.month_year == month_year)
    hotel_profits = sum(getattr(h, profit_field) for h in hotels if h.month_year == month_year)
    hotels_count = Hotel.query.filter_by(created_by=current_user.id).count()
    tickets_count = Ticket.query.filter_by(created_by=current_user.id).count()
    employees_count = Employee.query.filter_by(created_by=current_user.id).count()
    return render_template('dashboard.html',
        total_expenses=total_expenses,
        total_salaries=total_salaries,
        ticket_profits=ticket_profits,
        hotel_profits=hotel_profits,
        base_currency=base_currency,
        months=months,
        expenses_data=expenses_data,
        salaries_data=salaries_data,
        ticket_profits_data=ticket_profits_data,
        hotel_profits_data=hotel_profits_data,
        format_currency=format_currency,
        convert_currency=convert_currency,
        selected_month=month_year,
        hotels_count=hotels_count,
        tickets_count=tickets_count,
        employees_count=employees_count
    )

@app.route('/currencies', methods=['GET'])
@permission_required('currencies')
def currency_settings():
    currencies = Currency.query.all()
    return render_template('currency_settings.html', currencies=currencies)

@app.route('/currencies/add', methods=['POST'])
def add_currency():
    code = request.form['code'].upper()
    name = request.form['name']
    symbol = request.form['symbol']
    exchange_rate = float(request.form['exchange_rate'])
    if Currency.query.filter_by(code=code).first():
        flash('Currency already exists!')
        return redirect(url_for('currency_settings'))
    currency = Currency(code=code, name=name, symbol=symbol, exchange_rate=exchange_rate)
    db.session.add(currency)
    db.session.commit()
    flash('Currency added successfully!')
    return redirect(url_for('currency_settings'))

@app.route('/currencies/delete', methods=['POST'])
def delete_currency():
    currency_id = request.form['currency_id']
    currency = Currency.query.get(currency_id)
    if currency and not currency.is_base:
        db.session.delete(currency)
        db.session.commit()
        flash('Currency deleted!')
    else:
        flash('Cannot delete base currency!')
    return redirect(url_for('currency_settings'))

@app.route('/currencies/set_base', methods=['POST'])
def set_base_currency():
    base_id = int(request.form['base_currency_id'])
    currencies = Currency.query.all()
    for c in currencies:
        c.is_base = (c.id == base_id)
    db.session.commit()
    flash('Base currency updated!')
    return redirect(url_for('currency_settings'))

@app.route('/currencies/edit', methods=['POST'])
def edit_currency():
    currency_id = request.form['currency_id']
    code = request.form['code'].upper()
    name = request.form['name']
    symbol = request.form['symbol']
    exchange_rate = float(request.form['exchange_rate'])
    currency = Currency.query.get(currency_id)
    if currency:
        currency.code = code
        currency.name = name
        currency.symbol = symbol
        currency.exchange_rate = exchange_rate
        db.session.commit()
        flash('Currency updated successfully!')
    else:
        flash('Currency not found!')
    return redirect(url_for('currency_settings'))

@app.route('/expenses', methods=['GET', 'POST'])
@permission_required('expenses')
def expenses():
    currencies = get_all_currencies()
    base_currency = get_base_currency()
    if request.method == 'POST':
        name = request.form['name']
        amount = float(request.form['amount'])
        currency_id = int(request.form['currency_id'])
        date = request.form['date']
        from datetime import datetime
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        notes = request.form.get('notes', '')
        month_year = request.form['month_year']
        # حساب القيم المحوّلة
        amount_egp = convert_currency(amount, currency_id, Currency.query.filter_by(code='EGP').first().id)
        amount_usd = convert_currency(amount, currency_id, Currency.query.filter_by(code='USD').first().id)
        amount_eur = convert_currency(amount, currency_id, Currency.query.filter_by(code='EUR').first().id)
        amount_sar = convert_currency(amount, currency_id, Currency.query.filter_by(code='SAR').first().id)
        expense = Expense(name=name, amount=amount, currency_id=currency_id, date=date_obj, notes=notes, month_year=month_year, created_by=current_user.id,
                          amount_egp=amount_egp, amount_usd=amount_usd, amount_eur=amount_eur, amount_sar=amount_sar)
        db.session.add(expense)
        db.session.commit()
        flash('Expense added!')
        return redirect(url_for('expenses'))
    expenses = Expense.query.filter_by(created_by=current_user.id).order_by(Expense.date.desc()).all()
    return render_template('expenses.html', expenses=expenses, currencies=currencies, base_currency=base_currency, format_currency=format_currency, attribute=getattr)

@app.route('/expenses/delete', methods=['POST'])
def delete_expense():
    expense_id = request.form['expense_id']
    expense = Expense.query.get(expense_id)
    if expense and expense.created_by == current_user.id:
        db.session.delete(expense)
        db.session.commit()
        flash('Expense deleted!')
    return redirect(url_for('expenses'))

@app.route('/salaries', methods=['GET', 'POST'])
@permission_required('salaries')
def salaries():
    currencies = get_all_currencies()
    base_currency = get_base_currency()
    if request.method == 'POST':
        name = request.form['name']
        job_title = request.form['job_title']
        salary_amount = float(request.form['salary_amount'])
        currency_id = int(request.form['currency_id'])
        payment_date = request.form['payment_date']
        from datetime import datetime
        payment_date_obj = datetime.strptime(payment_date, '%Y-%m-%d').date()
        salary_egp = convert_currency(salary_amount, currency_id, Currency.query.filter_by(code='EGP').first().id)
        salary_usd = convert_currency(salary_amount, currency_id, Currency.query.filter_by(code='USD').first().id)
        salary_eur = convert_currency(salary_amount, currency_id, Currency.query.filter_by(code='EUR').first().id)
        salary_sar = convert_currency(salary_amount, currency_id, Currency.query.filter_by(code='SAR').first().id)
        employee = Employee(name=name, job_title=job_title, salary_amount=salary_amount, currency_id=currency_id, payment_date=payment_date_obj, created_by=current_user.id,
                            salary_amount_egp=salary_egp, salary_amount_usd=salary_usd, salary_amount_eur=salary_eur, salary_amount_sar=salary_sar)
        db.session.add(employee)
        db.session.commit()
        flash('Employee added!')
        return redirect(url_for('salaries'))
    employees = Employee.query.filter_by(created_by=current_user.id).order_by(Employee.payment_date.desc()).all()
    return render_template('salaries.html', employees=employees, currencies=currencies, base_currency=base_currency, format_currency=format_currency, attribute=getattr)

@app.route('/salaries/delete', methods=['POST'])
def delete_employee():
    employee_id = request.form['employee_id']
    employee = Employee.query.get(employee_id)
    if employee and employee.created_by == current_user.id:
        db.session.delete(employee)
        db.session.commit()
        flash('Employee deleted!')
    return redirect(url_for('salaries') )

@app.route('/tickets', methods=['GET', 'POST'])
@permission_required('tickets')
def tickets():
    currencies = get_all_currencies()
    base_currency = get_base_currency()
    if request.method == 'POST':
        ticket_number = request.form['ticket_number']
        pnr = request.form['pnr']
        departure_location = request.form['departure_location']
        arrival_location = request.form['arrival_location']
        purchase_price = float(request.form['purchase_price'])
        selling_price = float(request.form['selling_price'])
        currency_id = int(request.form['currency_id'])
        payment_fees = float(request.form.get('payment_fees', 0))
        payment_method = request.form.get('payment_method', '')
        notes = request.form.get('notes', '')
        profit = selling_price - purchase_price - payment_fees
        month_year = f"{request.form.get('month_year') or str(request.form.get('date', '')).split('-')[0:2]}"
        # حساب القيم المحوّلة
        purchase_price_egp = convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='EGP').first().id)
        purchase_price_usd = convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='USD').first().id)
        purchase_price_eur = convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='EUR').first().id)
        purchase_price_sar = convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='SAR').first().id)
        selling_price_egp = convert_currency(selling_price, currency_id, Currency.query.filter_by(code='EGP').first().id)
        selling_price_usd = convert_currency(selling_price, currency_id, Currency.query.filter_by(code='USD').first().id)
        selling_price_eur = convert_currency(selling_price, currency_id, Currency.query.filter_by(code='EUR').first().id)
        selling_price_sar = convert_currency(selling_price, currency_id, Currency.query.filter_by(code='SAR').first().id)
        payment_fees_egp = convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='EGP').first().id)
        payment_fees_usd = convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='USD').first().id)
        payment_fees_eur = convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='EUR').first().id)
        payment_fees_sar = convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='SAR').first().id)
        profit_egp = convert_currency(profit, currency_id, Currency.query.filter_by(code='EGP').first().id)
        profit_usd = convert_currency(profit, currency_id, Currency.query.filter_by(code='USD').first().id)
        profit_eur = convert_currency(profit, currency_id, Currency.query.filter_by(code='EUR').first().id)
        profit_sar = convert_currency(profit, currency_id, Currency.query.filter_by(code='SAR').first().id)
        ticket = Ticket(ticket_number=ticket_number, pnr=pnr, departure_location=departure_location, arrival_location=arrival_location, purchase_price=purchase_price, selling_price=selling_price, currency_id=currency_id, payment_fees=payment_fees, profit=profit, month_year=month_year, created_by=current_user.id,
                        payment_method=payment_method, notes=notes,
                        purchase_price_egp=purchase_price_egp, purchase_price_usd=purchase_price_usd, purchase_price_eur=purchase_price_eur, purchase_price_sar=purchase_price_sar,
                        selling_price_egp=selling_price_egp, selling_price_usd=selling_price_usd, selling_price_eur=selling_price_eur, selling_price_sar=selling_price_sar,
                        payment_fees_egp=payment_fees_egp, payment_fees_usd=payment_fees_usd, payment_fees_eur=payment_fees_eur, payment_fees_sar=payment_fees_sar,
                        profit_egp=profit_egp, profit_usd=profit_usd, profit_eur=profit_eur, profit_sar=profit_sar)
        db.session.add(ticket)
        db.session.commit()
        flash('Ticket added!')
        return redirect(url_for('tickets'))
    tickets = Ticket.query.filter_by(created_by=current_user.id).order_by(Ticket.created_at.desc()).all()
    return render_template('tickets.html', tickets=tickets, currencies=currencies, base_currency=base_currency, format_currency=format_currency, attribute=getattr)

@app.route('/hotels', methods=['GET', 'POST'])
@permission_required('hotels')
def hotels():
    currencies = get_all_currencies()
    base_currency = get_base_currency()
    if request.method == 'POST':
        booking_number = request.form['booking_number']
        hotel_name = request.form['hotel_name']
        guest_name = request.form['guest_name']
        check_in_date = datetime.strptime(request.form['check_in_date'], '%Y-%m-%d').date()
        check_out_date = datetime.strptime(request.form['check_out_date'], '%Y-%m-%d').date()
        purchase_price = float(request.form['purchase_price'])
        selling_price = float(request.form['selling_price'])
        currency_id = int(request.form['currency_id'])
        payment_fees = float(request.form.get('payment_fees', 0))
        profit = selling_price - purchase_price - payment_fees
        month_year = f"{check_in_date.year}-{check_in_date.month:02d}"
        booking_source = request.form.get('booking_source', '')
        passengers_count = request.form.get('passengers_count', 1)
        payment_method = request.form.get('payment_method', '')
        notes = request.form.get('notes', '')
        # حساب القيم المحوّلة
        purchase_price_egp = convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='EGP').first().id)
        purchase_price_usd = convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='USD').first().id)
        purchase_price_eur = convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='EUR').first().id)
        purchase_price_sar = convert_currency(purchase_price, currency_id, Currency.query.filter_by(code='SAR').first().id)
        selling_price_egp = convert_currency(selling_price, currency_id, Currency.query.filter_by(code='EGP').first().id)
        selling_price_usd = convert_currency(selling_price, currency_id, Currency.query.filter_by(code='USD').first().id)
        selling_price_eur = convert_currency(selling_price, currency_id, Currency.query.filter_by(code='EUR').first().id)
        selling_price_sar = convert_currency(selling_price, currency_id, Currency.query.filter_by(code='SAR').first().id)
        payment_fees_egp = convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='EGP').first().id)
        payment_fees_usd = convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='USD').first().id)
        payment_fees_eur = convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='EUR').first().id)
        payment_fees_sar = convert_currency(payment_fees, currency_id, Currency.query.filter_by(code='SAR').first().id)
        profit_egp = convert_currency(profit, currency_id, Currency.query.filter_by(code='EGP').first().id)
        profit_usd = convert_currency(profit, currency_id, Currency.query.filter_by(code='USD').first().id)
        profit_eur = convert_currency(profit, currency_id, Currency.query.filter_by(code='EUR').first().id)
        profit_sar = convert_currency(profit, currency_id, Currency.query.filter_by(code='SAR').first().id)
        hotel = Hotel(
            booking_number=booking_number,
            hotel_name=hotel_name,
            guest_name=guest_name,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            purchase_price=purchase_price,
            selling_price=selling_price,
            currency_id=currency_id,
            payment_fees=payment_fees,
            profit=profit,
            month_year=month_year,
            created_by=current_user.id,
            purchase_price_egp=purchase_price_egp,
            purchase_price_usd=purchase_price_usd,
            purchase_price_eur=purchase_price_eur,
            purchase_price_sar=purchase_price_sar,
            selling_price_egp=selling_price_egp,
            selling_price_usd=selling_price_usd,
            selling_price_eur=selling_price_eur,
            selling_price_sar=selling_price_sar,
            payment_fees_egp=payment_fees_egp,
            payment_fees_usd=payment_fees_usd,
            payment_fees_eur=payment_fees_eur,
            payment_fees_sar=payment_fees_sar,
            profit_egp=profit_egp,
            profit_usd=profit_usd,
            profit_eur=profit_eur,
            profit_sar=profit_sar,
            booking_source=booking_source,
            passengers_count=passengers_count,
            payment_method=payment_method,
            notes=notes
        )
        db.session.add(hotel)
        db.session.commit()
        flash('Hotel booking added!')
        return redirect(url_for('hotels'))
    hotels = Hotel.query.filter_by(created_by=current_user.id).order_by(Hotel.created_at.desc()).all()
    return render_template('hotels.html', hotels=hotels, currencies=currencies, base_currency=base_currency, format_currency=format_currency, attribute=getattr)

@app.route('/export', methods=['GET'])
@permission_required('export')
def export():
    return render_template('export.html')

@app.route('/export/download', methods=['GET'])
@permission_required('export')
def export_download():
    section = request.args.get('section')
    month_year = request.args.get('month_year')
    export_format = request.args.get('format')

    import re
    if month_year:
        match = re.match(r'^(\d{2})-(\d{4})$', month_year)
        if match:
            month_year = f"{match.group(2)}-{match.group(1)}"

    base_currency = get_base_currency()
    currency_code = base_currency.code.lower()
    # تحديد اسماء الحقول حسب العملة
    expense_field = f'amount_{currency_code}'
    salary_field = f'salary_amount_{currency_code}'
    purchase_field = f'purchase_price_{currency_code}'
    selling_field = f'selling_price_{currency_code}'
    payment_fees_field = f'payment_fees_{currency_code}'
    profit_field = f'profit_{currency_code}'

    if section == 'expenses':
        data = Expense.query.filter_by(month_year=month_year, created_by=current_user.id).all()
        headers = ['ID', 'Name', 'Amount', 'Currency', 'Date', 'Notes', 'Month-Year']
        rows = [[e.id, e.name, getattr(e, expense_field), base_currency.code, e.date.strftime('%Y-%m-%d'), e.notes, e.month_year] for e in data]
    elif section == 'salaries':
        data = Employee.query.filter(Employee.payment_date.like(f'{month_year}-%'), Employee.created_by==current_user.id).all()
        headers = ['ID', 'Name', 'Job Title', 'Salary', 'Currency', 'Payment Date']
        rows = [[e.id, e.name, e.job_title, getattr(e, salary_field), base_currency.code, e.payment_date.strftime('%Y-%m-%d')] for e in data]
    elif section == 'tickets':
        data = Ticket.query.filter_by(month_year=month_year, created_by=current_user.id).all()
        headers = ['ID', 'Ticket No.', 'PNR', 'From', 'To', 'Purchase', 'Selling', 'Profit', 'Currency', 'Month-Year', 'Payment Method', 'Notes']
        rows = [[t.id, t.ticket_number, t.pnr, t.departure_location, t.arrival_location, getattr(t, purchase_field), getattr(t, selling_field), getattr(t, profit_field), base_currency.code, t.month_year, t.payment_method, t.notes] for t in data]
    elif section == 'hotels':
        data = Hotel.query.filter_by(month_year=month_year, created_by=current_user.id).all()
        headers = ['ID', 'Booking No.', 'Hotel', 'Guest', 'Booking Source', 'Check-in', 'Check-out', 'Passengers', 'Purchase', 'Selling', 'Profit', 'Payment Method', 'Notes', 'Currency', 'Month-Year']
        rows = [[h.id, h.booking_number, h.hotel_name, h.guest_name, h.booking_source, h.check_in_date.strftime('%Y-%m-%d'), h.check_out_date.strftime('%Y-%m-%d'), h.passengers_count, getattr(h, purchase_field), getattr(h, selling_field), getattr(h, profit_field), h.payment_method, h.notes, base_currency.code, h.month_year] for h in data]
    elif section == 'visas':
        data = Visa.query.filter_by(month_year=month_year, created_by=current_user.id).all()
        headers = ['ID', 'Visa Type', 'Visa Duration', 'Visa Country', 'Visa Source', 'Owner Name', 'Purchase Price', 'Selling Price', 'Payment Method', 'Payment Fees', 'Profit', 'Currency', 'Notes']
        rows = [[v.id, v.visa_type, v.visa_duration, v.visa_country, v.visa_source, v.owner_name, getattr(v, purchase_field), getattr(v, selling_field), v.payment_method, getattr(v, payment_fees_field), getattr(v, profit_field), base_currency.code, v.notes] for v in data]
    else:
        return 'Invalid section', 400

    if export_format == 'excel':
        import pandas as pd
        from io import BytesIO
        df = pd.DataFrame(rows, columns=headers)
        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        filename = f'{section}_{month_year}.xlsx'
        return send_file(output, download_name=filename, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    elif export_format == 'pdf':
        from io import BytesIO
        from pdf_utils import create_custom_pdf
        output = BytesIO()
        logo_path = os.path.join('static', 'img', 'logo.png')
        company_name = 'ES-Travel'
        # يمكن تخصيص اسم الشركة حسب الإعدادات أو الترجمة
        create_custom_pdf(output, rows, headers, logo_path, company_name, section.capitalize(), month_year)
        output.seek(0)
        filename = f'{section}_{month_year}.pdf'
        return send_file(output, download_name=filename, as_attachment=True, mimetype='application/pdf')
    else:
        return 'Invalid format', 400

@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        permissions = request.form.getlist('permissions')
        # حفظ الصلاحيات كـ JSON
        permissions_json = json.dumps(permissions, ensure_ascii=False)
        # تعيين عملة افتراضية للمستخدم (الأولى في الجدول)
        default_currency = Currency.query.first()
        user = Admin(email=email, password_hash=generate_password_hash(password), preferred_currency_id=default_currency.id, role=role, permissions=permissions_json)
        db.session.add(user)
        db.session.commit()
        flash('تمت إضافة المستخدم بنجاح!')
        return redirect(url_for('users'))
    users = Admin.query.all()
    # فك صلاحيات الوصول
    for user in users:
        try:
            user.permissions = json.loads(user.permissions) if user.permissions else []
        except Exception:
            user.permissions = []
    return render_template('users.html', users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    from flask_login import login_user
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Admin.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('تم تسجيل الدخول بنجاح!')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('البريد الإلكتروني أو كلمة المرور غير صحيحة!')
    return render_template('login.html')



@app.route('/salaries/pay-again', methods=['POST'])
def pay_salary_again():
    employee_id = request.form['employee_id']
    employee = Employee.query.get(employee_id)
    if not employee:
        flash('الموظف غير موجود!')
        return redirect(url_for('salaries'))
    # حساب أول يوم من الشهر التالي
    old_date = employee.payment_date
    if old_date.month == 12:
        new_year = old_date.year + 1
        new_month = 1
    else:
        new_year = old_date.year
        new_month = old_date.month + 1
    from datetime import date
    new_date = date(new_year, new_month, 1)
    # إضافة جميع الحقول المطلوبة عند إعادة التقبيض
    new_salary = Employee(
        name=employee.name,
        job_title=employee.job_title,
        salary_amount=employee.salary_amount,
        currency_id=employee.currency_id,
        payment_date=new_date,
        created_by=employee.created_by,  # إصلاح المشكلة هنا
        salary_amount_egp=employee.salary_amount_egp,
        salary_amount_usd=employee.salary_amount_usd,
        salary_amount_eur=employee.salary_amount_eur,
        salary_amount_sar=employee.salary_amount_sar
    )
    db.session.add(new_salary)
    db.session.commit()
    flash('تم تقبيض الموظف مرة أخرى للشهر التالي بنجاح!')
    return redirect(url_for('salaries'))

@app.route('/users/toggle_active', methods=['POST'])
def toggle_user_active():
    user_id = request.form['user_id']
    user = Admin.query.get(user_id)
    if user:
        user.is_active = not user.is_active
        db.session.commit()
        flash('تم تحديث حالة المستخدم!')
    else:
        flash('المستخدم غير موجود!')
    return redirect(url_for('users'))

@app.route('/users/delete', methods=['POST'])
def delete_user():
    user_id = request.form['user_id']
    user = Admin.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('تم حذف المستخدم!')
    else:
        flash('المستخدم غير موجود!')
    return redirect(url_for('users'))


@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = Admin.query.get(user_id)
    currencies = get_all_currencies()
    if not user:
        flash('المستخدم غير موجود!')
        return redirect(url_for('users'))
    if request.method == 'POST':
        user.email = request.form['email']
        if request.form['password']:
            user.set_password(request.form['password'])
        user.role = request.form['role']
        user.permissions = json.dumps(request.form.getlist('permissions'), ensure_ascii=False)
        user.preferred_currency_id = int(request.form['preferred_currency_id'])
        db.session.commit()
        flash('تم تحديث بيانات المستخدم!')
        return redirect(url_for('users'))
    # فك صلاحيات الوصول
    try:
        user_permissions = json.loads(user.permissions) if user.permissions else []
    except Exception:
        user_permissions = []
    return render_template('edit_user.html', user=user, currencies=currencies, user_permissions=user_permissions)


@app.route('/visas', methods=['GET', 'POST'])
@permission_required('visas')
def visas():
    currencies = get_all_currencies()
    base_currency = get_base_currency()
    if request.method == 'POST':
        visa_type = request.form['visa_type']
        visa_duration = request.form['visa_duration']
        visa_country = request.form['visa_country']
        visa_source = request.form.get('visa_source', '')
        owner_name = request.form['owner_name']
        purchase_price = float(request.form['purchase_price'])
        selling_price = float(request.form['selling_price'])
        payment_method = request.form.get('payment_method', '')
        payment_fees = float(request.form.get('payment_fees', 0))
        notes = request.form.get('notes', '')
        currency_id = int(request.form['currency_id'])
        profit = selling_price - purchase_price - payment_fees
        month_year = request.form.get('month_year')
        if not month_year:
            from datetime import datetime
            month_year = f"{datetime.now().year}-{datetime.now().month:02d}"
        egp = Currency.query.filter_by(code='EGP').first()
        usd = Currency.query.filter_by(code='USD').first()
        eur = Currency.query.filter_by(code='EUR').first()
        sar = Currency.query.filter_by(code='SAR').first()
        if not all([egp, usd, eur, sar]):
            flash('يجب التأكد من وجود جميع العملات الرئيسية (EGP, USD, EUR, SAR) في قاعدة البيانات!')
            return redirect(url_for('visas'))
        purchase_price_egp = convert_currency(purchase_price, currency_id, egp.id)
        purchase_price_usd = convert_currency(purchase_price, currency_id, usd.id)
        purchase_price_eur = convert_currency(purchase_price, currency_id, eur.id)
        purchase_price_sar = convert_currency(purchase_price, currency_id, sar.id)
        selling_price_egp = convert_currency(selling_price, currency_id, egp.id)
        selling_price_usd = convert_currency(selling_price, currency_id, usd.id)
        selling_price_eur = convert_currency(selling_price, currency_id, eur.id)
        selling_price_sar = convert_currency(selling_price, currency_id, sar.id)
        payment_fees_egp = convert_currency(payment_fees, currency_id, egp.id)
        payment_fees_usd = convert_currency(payment_fees, currency_id, usd.id)
        payment_fees_eur = convert_currency(payment_fees, currency_id, eur.id)
        payment_fees_sar = convert_currency(payment_fees, currency_id, sar.id)
        profit_egp = convert_currency(profit, currency_id, egp.id)
        profit_usd = convert_currency(profit, currency_id, usd.id)
        profit_eur = convert_currency(profit, currency_id, eur.id)
        profit_sar = convert_currency(profit, currency_id, sar.id)
        visa = Visa(
            visa_type=visa_type,
            visa_duration=visa_duration,
            visa_country=visa_country,
            visa_source=visa_source,
            owner_name=owner_name,
            purchase_price=purchase_price,
            selling_price=selling_price,
            payment_method=payment_method,
            payment_fees=payment_fees,
            profit=profit,
            currency_id=currency_id,
            month_year=month_year,
            created_by=current_user.id,
            notes=notes,
            purchase_price_egp=purchase_price_egp,
            purchase_price_usd=purchase_price_usd,
            purchase_price_eur=purchase_price_eur,
            purchase_price_sar=purchase_price_sar,
            selling_price_egp=selling_price_egp,
            selling_price_usd=selling_price_usd,
            selling_price_eur=selling_price_eur,
            selling_price_sar=selling_price_sar,
            payment_fees_egp=payment_fees_egp,
            payment_fees_usd=payment_fees_usd,
            payment_fees_eur=payment_fees_eur,
            payment_fees_sar=payment_fees_sar,
            profit_egp=profit_egp,
            profit_usd=profit_usd,
            profit_eur=profit_eur,
            profit_sar=profit_sar
        )
        db.session.add(visa)
        db.session.commit()
        flash('تمت إضافة التأشيرة بنجاح!')
        return redirect(url_for('visas'))
    visas = Visa.query.filter_by(created_by=current_user.id).order_by(Visa.created_at.desc()).all()
    return render_template('visas.html', visas=visas, currencies=currencies, base_currency=base_currency, format_currency=format_currency, attribute=getattr)

@app.route('/visas/delete', methods=['POST'])
def delete_visa():
    visa_id = request.form['visa_id']
    visa = Visa.query.get(visa_id)
    if visa and visa.created_by == current_user.id:
        db.session.delete(visa)
        db.session.commit()
        flash('تم حذف التأشيرة!')
    return redirect(url_for('visas'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))


# Inject get_locale and convert_currency into Jinja2 templates
def inject_get_locale():
    return dict(get_locale=get_locale, convert_currency=convert_currency, format_currency=format_currency, attribute=getattr)
app.context_processor(inject_get_locale)

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
