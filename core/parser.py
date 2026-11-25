import re
from datetime import datetime
from core.utils import normalize_input
from config import NEW_COLORS


def get_message_hashtags(msg):
    tags = []
    for ent in msg.get("text_entities", []):
        if ent.get("type") == "hashtag":
            t = ent.get("text", "").lower()
            if t:
                tags.append(t)
    return tags


def parse_review_input(raw):
    """
    Гибкий разбор строки. Принимает дату и тег в любом порядке.
    Форматы даты: 22.09.2026, 22.09.26, 22/09/2026, 22-09-2026.
    Устойчиво к NBSP, ZWSP и прочим экзотическим пробелам.
    Возвращает (threshold_unixtime, tag) или (None, None).
    """
    raw = normalize_input(raw).strip()
    if not raw:
        return (None, None)

    parts = [p for p in re.split(r'[\s,;|]+', raw) if p]

    date_str = None
    tag = None

    for p in parts:
        if p.startswith('#') and tag is None:
            tag = p.lower()
        elif date_str is None and any(sep in p for sep in ('.', '/', '-')):
            date_str = p.replace('/', '.').replace('-', '.')

    if not (date_str and tag):
        return (None, None)

    dt = None
    for fmt in ("%d.%m.%Y", "%d.%m.%y"):
        try:
            dt = datetime.strptime(date_str, fmt)
            break
        except ValueError:
            continue

    if dt is None:
        return (None, None)

    return (int(dt.timestamp()), tag)



def ask_new_reviews(target_hashtags_set):
    """
    Спрашивает количество «новых» заданий, затем по каждому — дату и тег.
    Возвращает список словарей: [{"threshold": int, "tag": str, "color": str}, ...]
    """
    raw = input("Сколько новых заданий (хештегов) для отметки 'новое'? [Enter = 0]: ").strip()
    if not raw:
        return []
    try:
        n = int(raw)
    except ValueError:
        print("Не понял число. Принимаю как 0 новых.")
        return []
    if n <= 0:
        return []
    if n > len(NEW_COLORS):
        print(f"Максимум {len(NEW_COLORS)} заданий. Ограничиваю.")
        n = len(NEW_COLORS)

    result = []
    for i in range(n):
        prompt = (f"Введите хештег задания прошлого просмотра и дату через пробел "
                  f"(например 15.09.2026 #поле) [{i+1}/{n}]: ")
        raw_review = input(prompt)
        threshold, tag = parse_review_input(raw_review)

        if threshold is None or tag is None:
            print(f"  Не удалось разобрать. Получено: {raw_review!r}")
            norm = normalize_input(raw_review).strip()
            if norm != raw_review:
                print(f"  После нормализации: {norm!r}")
            parts = [p for p in re.split(r'[\s,;|]+', norm) if p]
            print(f"  Токены: {parts!r}")
            print(f"  Ожидание: дата (дд.мм.гггг или дд.мм.гг) и хештег (#...) в любом порядке.")
            print(f"  Пропускаю.")
            continue

        if tag not in target_hashtags_set:
            print(f"  Тег {tag} не входит в список заданий. Пропускаю.")
            continue

        result.append({
            "threshold": threshold,
            "tag": tag,
            "color": NEW_COLORS[i],
        })
    return result

