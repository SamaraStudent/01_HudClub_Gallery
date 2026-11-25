import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import shutil
import json
from config import *
from core.utils import normalize_input, get_russian_date, safe_id, esc
from core.parser import ask_new_reviews
from core.collector import collect_user_data
from core import renderer

def generate():
    if not SPISOK_JSON.exists():
        print(f"Ошибка: Файл не найден по пути {SPISOK_JSON}")
        return

    # 1. Ввод данных
    raw_input = input("Введите хештеги заданий через пробел: ")
    raw_input = normalize_input(raw_input).strip().lower()
    if not raw_input:
        return

    target_hashtags = [t if t.startswith('#') else '#'+t for t in raw_input.split()]
    target_hashtags_set = set(target_hashtags)

    new_reviews = ask_new_reviews(target_hashtags_set)
    new_review_map = {r["tag"]: (r["threshold"], r["color"]) for r in new_reviews}
    title_suffix = f" {esc(get_russian_date())} {' '.join(esc(t) for t in target_hashtags)}"

    # 2. Подготовка папок
    if WWW_ROOT.exists():
        if input(f"Удалить старую папку {WWW_ROOT.name}? (y/n): ").lower() not in ['y', 'yes', 'д', 'да']:
            return
        shutil.rmtree(WWW_ROOT)
    WWW_ROOT.mkdir(parents=True, exist_ok=True)
    (WWW_ROOT / IMG_DIR_NAME).mkdir(exist_ok=True)

    # 2.1. Копируем папку static (чтобы работали CSS и JS)
    static_src = SCRIPT_DIR / "static"
    static_dst = WWW_ROOT / "static"
    if static_src.exists():
        shutil.copytree(static_src, static_dst)

    # 3. Чтение данных и сбор фотографий
    with open(SPISOK_JSON, "r", encoding="utf-8") as f:
        spisok_data = json.load(f)
    spisok_ids = {str(u.get('from_id', '')) for u in spisok_data}

    json_files = sorted(CHATS_ROOT.rglob("*.json"))
    if not json_files:
        print(f"В папке {CHATS_ROOT} не найдено JSON файлов!")
        return
    
    print(f"Анализ {len(json_files)} файлов...")
    user_photos, potential_names = collect_user_data(json_files, target_hashtags_set, new_review_map, new_reviews)

    # 4. Подготовка списков пользователей
    unknown_users = [{"from_id": fid, "name": potential_names.get(fid, "Unknown"), "list_number": "?"} 
                     for fid in user_photos if fid not in spisok_ids]
    
    main_users = [u for u in spisok_data if str(u.get('from_id', '')) in user_photos]
    main_users.sort(key=lambda x: int(x['list_number']) if str(x['list_number']).isdigit() else 999)
    all_to_gen = main_users + unknown_users

    new_count_by_user = {}
    for fid, items in user_photos.items():
        for it in items:
            if it["new_idx"] is not None:
                new_count_by_user.setdefault(fid, {}).setdefault(it["new_idx"], 0)
                new_count_by_user[fid][it["new_idx"]] += 1

    # 5. Рендеринг HTML и копирование картинок
    print("Генерация HTML...")
    
    # 5.1. Index (Список участников)
    index_html = renderer.render_index(main_users, unknown_users, new_count_by_user, new_reviews, title_suffix)
    with open(WWW_ROOT / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    # 5.2. Копируем картинки и готовим данные для галерей
    for u in all_to_gen:
        fid = str(u['from_id'])
        safe_fid = safe_id(fid)
        if not safe_fid:
            continue
        
        u_dir = WWW_ROOT / IMG_DIR_NAME / safe_fid
        u_dir.mkdir(parents=True, exist_ok=True)
        
        u['photos'] = [] # Список для шаблона
        for i, item in enumerate(user_photos.get(fid, [])):
            src_p = item["path"]
            fname = f"p_{i}{src_p.suffix}"
            shutil.copy2(src_p, u_dir / fname)
            
            web_p = f"{IMG_DIR_NAME}/{safe_fid}/{fname}"
            caption = f"{u['list_number']}. {u['name']} | {item['tag']}"
            if item["new_idx"] is not None:
                caption += f" | НОВОЕ {item['new_idx']+1}"
                
            u['photos'].append({
                "web_p": web_p,
                "tag": item["tag"],
                "new_idx": item["new_idx"],
                "new_color": item["new_color"],
                "caption": caption
            })

    # 5.3. Генерация общей выставки
    all_html = renderer.render_all_photos(all_to_gen, target_hashtags, new_reviews, title_suffix)
    with open(WWW_ROOT / "all_photos.html", "w", encoding="utf-8") as f:
        f.write(all_html)

    # 5.4. Генерация страниц пользователей
    for u in all_to_gen:
        u_html = renderer.render_user(u, target_hashtags, new_reviews)
        with open(WWW_ROOT / f"user_{safe_id(str(u['from_id']))}.html", "w", encoding="utf-8") as f:
            f.write(u_html)

    print(f"\nГотово! Сайт создан в папке: {WWW_ROOT.name}")
    for idx, r in enumerate(new_reviews):
        print(f"  Новое {idx+1}: тег {r['tag']}, порог unixtime {r['threshold']}, цвет {r['color']}")

if __name__ == "__main__":
    generate()