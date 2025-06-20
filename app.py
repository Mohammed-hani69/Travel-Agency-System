from flask import Flask, request, session, render_template, redirect, url_for, flash, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_babel import Babel
from werkzeug.security import generate_password_hash
from models import db, Admin, Currency, Employee, Expense, Hotel, Ticket
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
        
        # Add default currencies if they don't exist
        if not Currency.query.first():
            currencies = [
                Currency(code='SAR', name='Saudi Riyal', symbol='﷼', exchange_rate=1.0, is_base=True),
                Currency(code='USD', name='US Dollar', symbol='$', exchange_rate=3.75),
                Currency(code='EUR', name='Euro', symbol='€', exchange_rate=4.10),
            ]
            for currency in currencies:
                db.session.add(currency)
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
    # الحصول على الشهر المطلوب من الباراميتر أو الشهر الحالي
    month_year = request.args.get('month_year')
    if not month_year:
        month_year = datetime.now().strftime('%Y-%m')
    # حساب الملخصات المالية مع التحويل الذكي
    expenses = Expense.query.all()
    employees = Employee.query.all()
    tickets = Ticket.query.all()
    hotels = Hotel.query.all()
    # بيانات الرسم البياني الشهري
    months = []
    expenses_data = []
    salaries_data = []
    ticket_profits_data = []
    hotel_profits_data = []
    for m in range(1, 13):
        month_str = f"2025-{m:02d}"
        months.append(month_str)
        expenses_data.append(sum(convert_currency(e.amount, e.currency_id, base_currency.id) for e in expenses if e.month_year == month_str))
        salaries_data.append(sum(convert_currency(emp.salary_amount, emp.currency_id, base_currency.id) for emp in employees if emp.payment_date.strftime('%Y-%m') == month_str))
        ticket_profits_data.append(sum(convert_currency(t.profit, t.currency_id, base_currency.id) for t in tickets if t.month_year == month_str))
        hotel_profits_data.append(sum(convert_currency(h.profit, h.currency_id, base_currency.id) for h in hotels if h.month_year == month_str))
    # بيانات الشهر المختار
    total_expenses = sum(convert_currency(e.amount, e.currency_id, base_currency.id) for e in expenses if e.month_year == month_year)
    total_salaries = sum(convert_currency(emp.salary_amount, emp.currency_id, base_currency.id) for emp in employees if emp.payment_date.strftime('%Y-%m') == month_year)
    ticket_profits = sum(convert_currency(t.profit, t.currency_id, base_currency.id) for t in tickets if t.month_year == month_year)
    hotel_profits = sum(convert_currency(h.profit, h.currency_id, base_currency.id) for h in hotels if h.month_year == month_year)
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
        selected_month=month_year
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
    if request.method == 'POST':
        name = request.form['name']
        amount = float(request.form['amount'])
        currency_id = int(request.form['currency_id'])
        # تحويل التاريخ من نص إلى كائن date
        date = request.form['date']
        from datetime import datetime
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        notes = request.form.get('notes', '')
        month_year = request.form['month_year']
        expense = Expense(name=name, amount=amount, currency_id=currency_id, date=date_obj, notes=notes, month_year=month_year)
        db.session.add(expense)
        db.session.commit()
        flash('Expense added!')
        return redirect(url_for('expenses'))
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return render_template('expenses.html', expenses=expenses, currencies=currencies, format_currency=format_currency)

@app.route('/expenses/delete', methods=['POST'])
def delete_expense():
    expense_id = request.form['expense_id']
    expense = Expense.query.get(expense_id)
    if expense:
        db.session.delete(expense)
        db.session.commit()
        flash('Expense deleted!')
    return redirect(url_for('expenses'))

@app.route('/salaries', methods=['GET', 'POST'])
@permission_required('salaries')
def salaries():
    currencies = get_all_currencies()
    if request.method == 'POST':
        name = request.form['name']
        job_title = request.form['job_title']
        salary_amount = float(request.form['salary_amount'])
        currency_id = int(request.form['currency_id'])
        payment_date = request.form['payment_date']
        from datetime import datetime
        payment_date_obj = datetime.strptime(payment_date, '%Y-%m-%d').date()
        employee = Employee(name=name, job_title=job_title, salary_amount=salary_amount, currency_id=currency_id, payment_date=payment_date_obj)
        db.session.add(employee)
        db.session.commit()
        flash('Employee added!')
        return redirect(url_for('salaries'))
    employees = Employee.query.order_by(Employee.payment_date.desc()).all()
    return render_template('salaries.html', employees=employees, currencies=currencies, format_currency=format_currency)

@app.route('/salaries/delete', methods=['POST'])
def delete_employee():
    employee_id = request.form['employee_id']
    employee = Employee.query.get(employee_id)
    if employee:
        db.session.delete(employee)
        db.session.commit()
        flash('Employee deleted!')
    return redirect(url_for('salaries'))

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
        profit = selling_price - purchase_price - payment_fees
        month_year = f"{request.form.get('month_year') or str(request.form.get('date', '')).split('-')[0:2]}"
        ticket = Ticket(ticket_number=ticket_number, pnr=pnr, departure_location=departure_location, arrival_location=arrival_location, purchase_price=purchase_price, selling_price=selling_price, currency_id=currency_id, payment_fees=payment_fees, profit=profit, month_year=month_year)
        db.session.add(ticket)
        db.session.commit()
        flash('Ticket added!')
        return redirect(url_for('tickets'))
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    return render_template('tickets.html', tickets=tickets, currencies=currencies, base_currency=base_currency, format_currency=format_currency, convert_currency=convert_currency)

@app.route('/tickets/delete', methods=['POST'])
def delete_ticket():
    ticket_id = request.form['ticket_id']
    ticket = Ticket.query.get(ticket_id)
    if ticket:
        db.session.delete(ticket)
        db.session.commit()
        flash('Ticket deleted!')
    return redirect(url_for('tickets'))

@app.route('/tickets/add', methods=['POST'])
def add_ticket():
    ticket_number = request.form['ticket_number']
    pnr = request.form['pnr']
    departure_location = request.form['departure_location']
    arrival_location = request.form['arrival_location']
    customer_name = request.form.get('customer_name')
    ticket_source = request.form.get('ticket_source')
    passengers_count = request.form.get('passengers_count', 1)
    purchase_price = float(request.form['purchase_price'])
    selling_price = float(request.form['selling_price'])
    currency_id = int(request.form['currency_id'])
    payment_fees = float(request.form.get('payment_fees', 0))
    profit = selling_price - purchase_price - payment_fees
    # month_year: استخدم السنة والشهر من تاريخ اليوم
    month_year = datetime.now().strftime('%Y-%m')
    ticket = Ticket(ticket_number=ticket_number, pnr=pnr, departure_location=departure_location, arrival_location=arrival_location, customer_name=customer_name,
    ticket_source=ticket_source,
    passengers_count=passengers_count,purchase_price=purchase_price, selling_price=selling_price, currency_id=currency_id, payment_fees=payment_fees, profit=profit, month_year=month_year)
    db.session.add(ticket)
    db.session.commit()
    flash('Ticket added!')
    return redirect(url_for('tickets'))

@app.route('/hotels', methods=['GET', 'POST'])
@permission_required('hotels')
def hotels():
    currencies = get_all_currencies()
    base_currency = get_base_currency()
    if request.method == 'POST':
        booking_number = request.form['booking_number']
        hotel_name = request.form['hotel_name']
        guest_name = request.form['guest_name']
        # تحويل التواريخ من نص إلى كائن date
        check_in_date = datetime.strptime(request.form['check_in_date'], '%Y-%m-%d').date()
        check_out_date = datetime.strptime(request.form['check_out_date'], '%Y-%m-%d').date()
        purchase_price = float(request.form['purchase_price'])
        selling_price = float(request.form['selling_price'])
        currency_id = int(request.form['currency_id'])
        payment_fees = float(request.form.get('payment_fees', 0))
        profit = selling_price - purchase_price - payment_fees
        # month_year: استخدم السنة والشهر من تاريخ الدخول
        month_year = f"{check_in_date.year}-{check_in_date.month:02d}"
        hotel = Hotel(booking_number=booking_number, hotel_name=hotel_name, guest_name=guest_name, check_in_date=check_in_date, check_out_date=check_out_date, purchase_price=purchase_price, selling_price=selling_price, currency_id=currency_id, payment_fees=payment_fees, profit=profit, month_year=month_year)
        db.session.add(hotel)
        db.session.commit()
        flash('Hotel booking added!')
        return redirect(url_for('hotels'))
    hotels = Hotel.query.order_by(Hotel.created_at.desc()).all()
    return render_template('hotels.html', hotels=hotels, currencies=currencies, base_currency=base_currency, format_currency=format_currency, convert_currency=convert_currency)

@app.route('/hotels/delete', methods=['POST'])
def delete_hotel():
    hotel_id = request.form['hotel_id']
    hotel = Hotel.query.get(hotel_id)
    if hotel:
        db.session.delete(hotel)
        db.session.commit()
        flash('Hotel booking deleted!')
    return redirect(url_for('hotels'))

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

    # معالجة month_year لقبول MM-YYYY وتحويلها إلى YYYY-MM
    import re
    if month_year:
        match = re.match(r'^(\d{2})-(\d{4})$', month_year)
        if match:
            # إذا كانت الصيغة MM-YYYY، حولها إلى YYYY-MM
            month_year = f"{match.group(2)}-{match.group(1)}"

    # جلب البيانات بدقة حسب القسم والشهر
    if section == 'expenses':
        data = Expense.query.filter_by(month_year=month_year).all()
        headers = ['ID', 'Name', 'Amount', 'Currency', 'Date', 'Notes', 'Month-Year']
        rows = [[e.id, e.name, e.amount, e.currency.code if e.currency else '', e.date.strftime('%Y-%m-%d'), e.notes, e.month_year] for e in data]
    elif section == 'salaries':
        # جلب الرواتب التي تاريخ الدفع فيها يبدأ بهذا الشهر
        data = Employee.query.filter(Employee.payment_date.like(f'{month_year}-%')).all()
        headers = ['ID', 'Name', 'Job Title', 'Salary', 'Currency', 'Payment Date']
        rows = [[e.id, e.name, e.job_title, e.salary_amount, e.currency.code if e.currency else '', e.payment_date.strftime('%Y-%m-%d')] for e in data]
    elif section == 'tickets':
        data = Ticket.query.filter_by(month_year=month_year).all()
        headers = ['ID', 'Ticket No.', 'PNR', 'From', 'To', 'Purchase', 'Selling', 'Profit', 'Currency', 'Month-Year']
        rows = [[t.id, t.ticket_number, t.pnr, t.departure_location, t.arrival_location, t.purchase_price, t.selling_price, t.profit, t.currency.code if t.currency else '', t.month_year] for t in data]
    elif section == 'hotels':
        data = Hotel.query.filter_by(month_year=month_year).all()
        headers = ['ID', 'Booking No.', 'Hotel', 'Guest', 'Check-in', 'Check-out', 'Purchase', 'Selling', 'Profit', 'Currency', 'Month-Year']
        rows = [[h.id, h.booking_number, h.hotel_name, h.guest_name, h.check_in_date.strftime('%Y-%m-%d'), h.check_out_date.strftime('%Y-%m-%d'), h.purchase_price, h.selling_price, h.profit, h.currency.code if h.currency else '', h.month_year] for h in data]
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
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from io import BytesIO
        output = BytesIO()
        c = canvas.Canvas(output, pagesize=A4)
        width, height = A4
        c.setFont('Helvetica-Bold', 14)
        c.drawString(40, height - 40, f'{section.capitalize()} - {month_year}')
        c.setFont('Helvetica', 10)
        y = height - 70
        col_width = (width - 80) // len(headers)
        for i, header in enumerate(headers):
            c.drawString(40 + i * col_width, y, str(header))
        y -= 20
        for row in rows:
            for i, cell in enumerate(row):
                c.drawString(40 + i * col_width, y, str(cell))
            y -= 18
            if y < 50:
                c.showPage()
                y = height - 50
        c.save()
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
    new_salary = Employee(
        name=employee.name,
        job_title=employee.job_title,
        salary_amount=employee.salary_amount,
        currency_id=employee.currency_id,
        payment_date=new_date
    )
    db.session.add(new_salary)
    db.session.commit()
    flash('تم تقبيض الموظف مرة أخرى للشهر التالي بنجاح!')
    return redirect(url_for('salaries'))

# Inject get_locale and convert_currency into Jinja2 templates
def inject_get_locale():
    return dict(get_locale=get_locale, convert_currency=convert_currency, format_currency=format_currency)
app.context_processor(inject_get_locale)

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
