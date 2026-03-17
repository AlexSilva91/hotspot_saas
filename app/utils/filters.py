def datetime_br(value):
    if not value:
        return ""
    return value.strftime("%d/%m/%Y %H:%M")