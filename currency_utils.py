from models import Currency

def convert_currency(amount, from_currency_id, to_currency_id):
    """
    تحويل المبلغ أولاً إلى الدولار الأمريكي ثم إلى العملة المطلوبة بدقة عالية
    """
    if from_currency_id == to_currency_id:
        return round(float(amount), 2)

    usd_currency = Currency.query.filter_by(code='USD').first()
    from_currency = Currency.query.get(from_currency_id)
    to_currency = Currency.query.get(to_currency_id)

    if not from_currency or not to_currency or not usd_currency:
        return round(float(amount), 2)

    # التحويل من العملة الأصلية إلى الدولار الأمريكي
    if from_currency.id != usd_currency.id:
        # التحويل إلى الدولار: المبلغ ÷ سعر صرف العملة مقابل الدولار
        amount = float(amount) / float(from_currency.exchange_rate)
    else:
        amount = float(amount)

    # التحويل من الدولار الأمريكي إلى العملة المطلوبة
    if to_currency.id != usd_currency.id:
        # التحويل من الدولار إلى العملة المطلوبة: المبلغ × سعر صرف العملة المطلوبة مقابل الدولار
        amount = amount * float(to_currency.exchange_rate)

    return round(amount, 2)

def get_amount_in_base_currency(amount, currency_id):
    """
    Convert any amount to the base currency
    """
    currency = Currency.query.get(currency_id)
    if not currency:
        return round(float(amount), 2)
    if currency.is_base:
        return round(float(amount), 2)
    return round(float(amount) / float(currency.exchange_rate), 2)

def format_currency(amount, currency_id):
    """
    Format amount with currency symbol
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
    إرجاع سعر الصرف الحالي للعملة بناءً على كود العملة
    """
    currency = Currency.query.filter_by(code=code).first()
    if currency:
        return float(currency.exchange_rate)
    return 1.0
