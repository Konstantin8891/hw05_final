import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    return {
        # ... datetime.date.today().year
        'year': datetime.date.today().year,
    }
