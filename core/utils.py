import html
import re
import locale
from datetime import datetime
from config import _WS_REPLACEMENTS, SAFE_ID_RE



def normalize_input(s):
    """Убирает экзотические пробелы и невидимые символы."""
    for bad, good in _WS_REPLACEMENTS:
        s = s.replace(bad, good)
    return s


def esc(value):
    return html.escape(str(value), quote=True)


def safe_id(value):
    s = str(value)
    return s if SAFE_ID_RE.match(s) else ""


def get_russian_date():
    try:
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    except Exception:
        try:
            locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')
        except Exception:
            pass
    now = datetime.now()
    months_ru = {1:'января', 2:'февраля', 3:'марта', 4:'апреля', 5:'мая', 6:'июня',
                 7:'июля', 8:'августа', 9:'сентября', 10:'октября', 11:'ноября', 12:'декабря'}
    return f"{now.day} {months_ru[now.month]} {now.year} год"
