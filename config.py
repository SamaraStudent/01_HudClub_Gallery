from pathlib import Path
import re


# --- НАСТРОЙКИ ПУТЕЙ ---
SCRIPT_DIR = Path(__file__).parent

# Указываем абсолютные пути к новым данным
BASE_DATA_DIR = Path(r"D:\PRJ_Python\00_TelegaJSON\02_HudClub")
CHATS_ROOT = Path(r"D:\PRJ_Python\00_TelegaJSON\02_HudClub\02_ExportedChats")
SPISOK_JSON = Path(r"D:\PRJ_Python\00_TelegaJSON\02_HudClub\SpisokHudClub.JSON")
NEW_USER_JSON = BASE_DATA_DIR / "NEW_USER.JSON" # Будет создаваться в той же папке с данными

# Папка для генерации сайта (остается в проекте)
WWW_ROOT = SCRIPT_DIR / "Gallery_Web"
IMG_DIR_NAME = "assets"

SAFE_ID_RE = re.compile(r'^[A-Za-z0-9_]+$')

# Цвета бейджей «новое» для разных заданий
NEW_COLORS = [
    "#1e7a1e",  # зелёный
    "#8b1e8b",  # пурпур
    "#1e4a8b",  # синий
    "#8b4a1e",  # оранжевый
    "#8b1e1e",  # красный
    "#1e8b8b",  # бирюзовый
    "#5a1e8b",  # фиолетовый
]

# Невидимые/экзотические пробелы и BOM/ZWSP — часто попадают при копировании
_WS_REPLACEMENTS = [
    ('\u00a0', ' '),   # NBSP
    ('\u202f', ' '),   # narrow NBSP
    ('\u2007', ' '),   # figure space
    ('\u2009', ' '),   # thin space
    ('\u200a', ' '),   # hair space
    ('\u2002', ' '),   # en space
    ('\u2003', ' '),   # em space
    ('\u2004', ' '),   # three-per-em
    ('\u2005', ' '),   # four-per-em
    ('\u2006', ' '),   # six-per-em
    ('\u2008', ' '),   # punctuation space
    ('\u205f', ' '),   # medium math space
    ('\u3000', ' '),   # ideographic space
    ('\u200b', ''),    # zero-width space
    ('\u200c', ''),    # zero-width non-joiner
    ('\u200d', ''),    # zero-width joiner
    ('\ufeff', ''),    # BOM
]
