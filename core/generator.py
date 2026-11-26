import shutil
import json
from pathlib import Path
from config import IMG_DIR_NAME, SPISOK_JSON, CHATS_ROOT, WWW_ROOT, HASHTAGS_JSON
from core.utils import safe_id, get_russian_date, esc
from core.collector import collect_user_data
from core import renderer

def run_generation(target_hashtags, log_func=print):
    """
    Главная функция генерации.
    target_hashtags - список строк (например, ['#рисунок1', '#пленэр2026'])
    log_func - функция для вывода логов (в консоль или GUI)
    """
    spisok_path = Path(SPISOK_JSON)
    chats_root = Path(CHATS_ROOT)
    output_dir = Path(WWW_ROOT)

    if not spisok_path.exists():
        log_func(f"Ошибка: Spisok.JSON не найден по пути {spisok_path}")
        return False

    target_hashtags_set = set(target_hashtags)
    
    # --- НОВЫЙ БЛОК: Группировка выбранных тегов по категориям ---
    grouped_hashtags = {}
    if HASHTAGS_JSON.exists():
        with open(HASHTAGS_JSON, "r", encoding="utf-8") as f:
            all_hashtags = json.load(f)
            
        for item in all_hashtags:
            # Берем только те теги, которые пользователь выбрал в редакторе
            if item.get('hashtag') in target_hashtags_set:
                cat = item.get('category', 'Разное')
                if cat not in grouped_hashtags:
                    grouped_hashtags[cat] = []
                grouped_hashtags[cat].append(item['hashtag'])
    # -------------------------------------------------------------

    # Пока оставим новые задания пустыми (мы сделаем их чуть позже)
    new_reviews = []
    new_review_map = {}

    # Подготовка папок
    log_func("Подготовка папок...")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / IMG_DIR_NAME).mkdir(exist_ok=True)

    # Копируем static (CSS и JS)
    static_src = Path(__file__).parent.parent / "static"
    if static_src.exists():
        shutil.copytree(static_src, output_dir / "static")

    # Чтение данных
    with open(spisok_path, "r", encoding="utf-8") as f:
        spisok_data = json.load(f)
    spisok_ids = {str(u.get('from_id', '')) for u in spisok_data}

    json_files = sorted(chats_root.rglob("*.json"))
    if not json_files:
        log_func(f"В папке {chats_root} не найдено JSON файлов!")
        return False
    
    log_func(f"Анализ {len(json_files)} файлов...")
    user_photos, potential_names = collect_user_data(json_files, target_hashtags_set, new_review_map, new_reviews)

    # Подготовка списков пользователей
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

    log_func("Генерация HTML-страниц...")
    
    title_suffix = f" {esc(get_russian_date())} {' '.join(esc(t) for t in target_hashtags)}"

    # Рендеринг главной страницы (Передаем grouped_hashtags)
    index_html = renderer.render_index(main_users, unknown_users, new_count_by_user, new_reviews, title_suffix, grouped_hashtags)
    with open(output_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    # Копирование фото и генерация страниц
    for u in all_to_gen:
        fid = str(u['from_id'])
        safe_fid = safe_id(fid)
        if not safe_fid: continue
        
        u_dir = output_dir / IMG_DIR_NAME / safe_fid
        u_dir.mkdir(parents=True, exist_ok=True)
        
        u['photos'] = [] 
        for i, item in enumerate(user_photos.get(fid, [])):
            src_p = item["path"]
            fname = f"p_{i}{src_p.suffix}"
            shutil.copy2(src_p, u_dir / fname)
            
            web_p = f"{IMG_DIR_NAME}/{safe_fid}/{fname}"
            caption = f"{u['list_number']}. {u['name']} | {item['tag']}"
                
            u['photos'].append({
                "web_p": web_p, "tag": item["tag"],
                "new_idx": item["new_idx"], "new_color": item["new_color"],
                "caption": caption
            })

    # Рендеринг общей выставки (Передаем grouped_hashtags)
    all_html = renderer.render_all_photos(all_to_gen, target_hashtags, new_reviews, title_suffix, grouped_hashtags)
    with open(output_dir / "all_photos.html", "w", encoding="utf-8") as f:
        f.write(all_html)

    # Рендеринг страниц пользователей (Передаем grouped_hashtags)
    for u in all_to_gen:
        u_html = renderer.render_user(u, target_hashtags, new_reviews, grouped_hashtags)
        with open(output_dir / f"user_{safe_id(str(u['from_id']))}.html", "w", encoding="utf-8") as f:
            f.write(u_html)

    log_func("Готово! Сайт создан.")
    return True