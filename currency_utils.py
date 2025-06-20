from models import Currency

def convert_currency(amount, from_currency_id, to_currency_id):
    """
    تحويل المبلغ أولاً إلى الجنيه المصري ثم إلى العملة المطلوبة
    """
    if from_currency_id == to_currency_id:
        return amount

    egp_currency = Currency.query.filter_by(code='EGP').first()
    from_currency = Currency.query.get(from_currency_id)
    to_currency = Currency.query.get(to_currency_id)

    if not from_currency or not to_currency or not egp_currency:
        return amount

    # الخطوة 1: التحويل من العملة الأصلية إلى الجنيه المصري
    if from_currency.id != egp_currency.id:
        # دائماً نضرب في سعر العملة بالجنيه المصري
        amount = amount * from_currency.exchange_rate
    # إذا كانت العملة الأصلية هي الجنيه المصري، لا حاجة للتحويل

    # الخطوة 2: التحويل من الجنيه المصري إلى العملة المطلوبة
    if to_currency.id != egp_currency.id:
        # دائماً نقسم على سعر العملة المطلوبة بالجنيه المصري
        amount = amount / to_currency.exchange_rate

    return round(amount, 2)

def get_amount_in_base_currency(amount, currency_id):
    """
    Convert any amount to the base currency
    """
    currency = Currency.query.get(currency_id)
    if not currency:
        return amount
        
    if currency.is_base:
        return amount
        
    return round(amount * currency.exchange_rate, 2)

def format_currency(amount, currency_id):
    """
    Format amount with currency symbol
    """
    currency = Currency.query.get(currency_id)
    if not currency:
        return f"{amount:,.2f}"
        
    if currency.symbol:
        return f"{currency.symbol} {amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency.code}"
