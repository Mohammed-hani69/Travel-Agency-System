from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(3), unique=True, nullable=False)  # e.g., USD, SAR, EUR
    name = db.Column(db.String(50), nullable=False)  # e.g., US Dollar, Saudi Riyal
    symbol = db.Column(db.String(5), nullable=False)  # e.g., $, ﷼, €
    exchange_rate = db.Column(db.Float, nullable=False)  # Rate relative to base currency
    is_base = db.Column(db.Boolean, default=False)  # Is this the base currency?
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    preferred_currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='admin')
    permissions = db.Column(db.Text, nullable=True)  # JSON list of allowed pages
    is_active_db = db.Column(db.Boolean, default=True)  # حقل فعلي للحالة
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    preferred_currency = db.relationship('Currency', backref='admin_users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return self.is_active_db

    @is_active.setter
    def is_active(self, value):
        self.is_active_db = value

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    job_title = db.Column(db.String(200), nullable=False)
    salary_amount = db.Column(db.Float, nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)  # المستخدم الذي أضاف السطر
    salary_amount_egp = db.Column(db.Float, nullable=False)
    salary_amount_usd = db.Column(db.Float, nullable=False)
    salary_amount_eur = db.Column(db.Float, nullable=False)
    salary_amount_sar = db.Column(db.Float, nullable=False)

    currency = db.relationship('Currency', backref='employee_salaries')
    user = db.relationship('Admin', backref='employee_records')

    @property
    def salary_in_base_currency(self):
        if self.currency.is_base:
            return self.salary_amount
        return self.salary_amount * self.currency.exchange_rate

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    month_year = db.Column(db.String(7), nullable=False)  # Format: "2025-06"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    amount_egp = db.Column(db.Float, nullable=False)
    amount_usd = db.Column(db.Float, nullable=False)
    amount_eur = db.Column(db.Float, nullable=False)
    amount_sar = db.Column(db.Float, nullable=False)

    currency = db.relationship('Currency', backref='expenses')
    user = db.relationship('Admin', backref='expense_records')

    @property
    def amount_in_base_currency(self):
        if self.currency.is_base:
            return self.amount
        return self.amount * self.currency.exchange_rate

class Hotel(db.Model):
    __tablename__ = 'hotels'
    id = db.Column(db.Integer, primary_key=True)
    booking_number = db.Column(db.String(100), nullable=False)
    hotel_name = db.Column(db.String(200), nullable=False)
    guest_name = db.Column(db.String(200), nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False, default='cash')
    payment_fees = db.Column(db.Float, nullable=False, default=0.0)
    profit = db.Column(db.Float, nullable=False)
    month_year = db.Column(db.String(7), nullable=False)  # Format: "YYYY-MM"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    purchase_price_egp = db.Column(db.Float, nullable=False)
    purchase_price_usd = db.Column(db.Float, nullable=False)
    purchase_price_eur = db.Column(db.Float, nullable=False)
    purchase_price_sar = db.Column(db.Float, nullable=False)
    selling_price_egp = db.Column(db.Float, nullable=False)
    selling_price_usd = db.Column(db.Float, nullable=False)
    selling_price_eur = db.Column(db.Float, nullable=False)
    selling_price_sar = db.Column(db.Float, nullable=False)
    payment_fees_egp = db.Column(db.Float, nullable=False)
    payment_fees_usd = db.Column(db.Float, nullable=False)
    payment_fees_eur = db.Column(db.Float, nullable=False)
    payment_fees_sar = db.Column(db.Float, nullable=False)
    profit_egp = db.Column(db.Float, nullable=False)
    profit_usd = db.Column(db.Float, nullable=False)
    profit_eur = db.Column(db.Float, nullable=False)
    profit_sar = db.Column(db.Float, nullable=False)
    booking_source = db.Column(db.String(200), nullable=True)
    passengers_count = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    currency = db.relationship('Currency', backref='hotel_bookings')
    user = db.relationship('Admin', backref='hotel_records')

    @property
    def amounts_in_base_currency(self):
        if self.currency.is_base:
            return {
                'purchase_price': self.purchase_price,
                'selling_price': self.selling_price,
                'payment_fees': self.payment_fees,
                'profit': self.profit
            }
        rate = self.currency.exchange_rate
        return {
            'purchase_price': self.purchase_price * rate,
            'selling_price': self.selling_price * rate,
            'payment_fees': self.payment_fees * rate,
            'profit': self.profit * rate
        }

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(100), nullable=False)
    pnr = db.Column(db.String(100), nullable=False)
    departure_location = db.Column(db.String(200), nullable=False)
    arrival_location = db.Column(db.String(200), nullable=False)
    # customer_name = db.Column(db.String(200), nullable=True)  # اسم العميل (تم حذفه)
    ticket_source = db.Column(db.String(200), nullable=True)  # مصدر التذكرة
    passengers_count = db.Column(db.Integer, nullable=True)   # عدد الأفراد
    purchase_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'), nullable=False)
    payment_method = db.Column(db.String(100), nullable=True)  # طريقة الدفع نص
    notes = db.Column(db.Text, nullable=True)  # ملاحظات
    payment_fees = db.Column(db.Float, nullable=False, default=0.0)
    profit = db.Column(db.Float, nullable=False)
    month_year = db.Column(db.String(7), nullable=False)  # Format: "2025-06"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    purchase_price_egp = db.Column(db.Float, nullable=False)
    purchase_price_usd = db.Column(db.Float, nullable=False)
    purchase_price_eur = db.Column(db.Float, nullable=False)
    purchase_price_sar = db.Column(db.Float, nullable=False)
    selling_price_egp = db.Column(db.Float, nullable=False)
    selling_price_usd = db.Column(db.Float, nullable=False)
    selling_price_eur = db.Column(db.Float, nullable=False)
    selling_price_sar = db.Column(db.Float, nullable=False)
    payment_fees_egp = db.Column(db.Float, nullable=False)
    payment_fees_usd = db.Column(db.Float, nullable=False)
    payment_fees_eur = db.Column(db.Float, nullable=False)
    payment_fees_sar = db.Column(db.Float, nullable=False)
    profit_egp = db.Column(db.Float, nullable=False)
    profit_usd = db.Column(db.Float, nullable=False)
    profit_eur = db.Column(db.Float, nullable=False)
    profit_sar = db.Column(db.Float, nullable=False)

    currency = db.relationship('Currency', backref='tickets')
    user = db.relationship('Admin', backref='ticket_records')

    @property
    def amounts_in_base_currency(self):
        if self.currency.is_base:
            return {
                'purchase_price': self.purchase_price,
                'selling_price': self.selling_price,
                'payment_fees': self.payment_fees,
                'profit': self.profit
            }
        rate = self.currency.exchange_rate
        return {
            'purchase_price': self.purchase_price * rate,
            'selling_price': self.selling_price * rate,
            'payment_fees': self.payment_fees * rate,
            'profit': self.profit * rate
        }

class Visa(db.Model):
    __tablename__ = 'visas'
    id = db.Column(db.Integer, primary_key=True)
    visa_type = db.Column(db.String(100), nullable=False)
    visa_duration = db.Column(db.String(100), nullable=False)  # مدة التأشيرة
    visa_country = db.Column(db.String(100), nullable=False)   # بلد التأشيرة
    visa_source = db.Column(db.String(200), nullable=True)
    owner_name = db.Column(db.String(200), nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(100), nullable=True)
    payment_fees = db.Column(db.Float, nullable=False, default=0.0)
    profit = db.Column(db.Float, nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'), nullable=False)
    month_year = db.Column(db.String(7), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    # الحقول المحوّلة لكل عملة
    purchase_price_egp = db.Column(db.Float, nullable=False)
    purchase_price_usd = db.Column(db.Float, nullable=False)
    purchase_price_eur = db.Column(db.Float, nullable=False)
    purchase_price_sar = db.Column(db.Float, nullable=False)
    selling_price_egp = db.Column(db.Float, nullable=False)
    selling_price_usd = db.Column(db.Float, nullable=False)
    selling_price_eur = db.Column(db.Float, nullable=False)
    selling_price_sar = db.Column(db.Float, nullable=False)
    payment_fees_egp = db.Column(db.Float, nullable=False)
    payment_fees_usd = db.Column(db.Float, nullable=False)
    payment_fees_eur = db.Column(db.Float, nullable=False)
    payment_fees_sar = db.Column(db.Float, nullable=False)
    profit_egp = db.Column(db.Float, nullable=False)
    profit_usd = db.Column(db.Float, nullable=False)
    profit_eur = db.Column(db.Float, nullable=False)
    profit_sar = db.Column(db.Float, nullable=False)

    currency = db.relationship('Currency', backref='visa_records')
    user = db.relationship('Admin', backref='visa_records')
