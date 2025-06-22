from models import Currency

def convert_currency(amount, from_currency_id, to_currency_id):
    """
    تحويل المبلغ دائماً عبر الدولار الأمريكي (USD) مهما كانت العملة الأساسية للموقع
    1. تحويل العملة الأصلية إلى دولار
    2. تحويل الدولار إلى العملة الهدف
    """
    if from_currency_id == to_currency_id:
        return round(float(amount), 2)

    usd_currency = Currency.query.filter_by(code='USD').first()
    from_currency = Currency.query.get(from_currency_id)
    to_currency = Currency.query.get(to_currency_id)

    if not from_currency or not to_currency or not usd_currency:
        return round(float(amount), 2)

    # الخطوة 1: تحويل من العملة الأصلية إلى الدولار
    amount_in_usd = float(amount) * float(from_currency.exchange_rate)
    # الخطوة 2: تحويل من الدولار إلى العملة الهدف
    result = amount_in_usd / float(to_currency.exchange_rate)
    return round(result, 2)

def get_amount_in_base_currency(amount, currency_id):
    """
    تحويل أي مبلغ إلى العملة الأساسية
    """
    currency = Currency.query.get(currency_id)
    if not currency:
        return round(float(amount), 2)
    if currency.is_base:
        return round(float(amount), 2)
    return round(float(amount) * float(currency.exchange_rate), 2)

def format_currency(amount, currency_id):
    """
    تنسيق المبلغ باستخدام رمز العملة
    """
    currency = Currency.query.get(currency_id)
    if not currency:
        return f"{float(amount):,.2f}"
    if currency.symbol:
        return f"{currency.symbol} {float(amount):,.2f}"
    else:
        return f"{float(amount):,.2f} {currency.code}"

def get_exchange_rate(code):
    """
    إرجاع سعر صرف العملة حسب الكود
    """
    currency = Currency.query.filter_by(code=code).first()
    if currency:
        return float(currency.exchange_rate)
    return 1.0
