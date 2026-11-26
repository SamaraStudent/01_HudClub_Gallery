import shutil
from pathlib import Path

THEMES_DIR = Path(__file__).parent.parent / "themes"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
STATIC_DIR = Path(__file__).parent.parent / "static"
UNDO_DIR = THEMES_DIR / "00_undo" # Папка для отмены

def get_themes():
    """Возвращает список названий доступных тем"""
    if not THEMES_DIR.exists():
        return []
    # Исключаем папку 00_undo из списка доступных тем
    return [d.name for d in THEMES_DIR.iterdir() if d.is_dir() and d.name != "00_undo"]

def save_current_theme(theme_name):
    """Сохраняет текущие templates и static в папку themes/theme_name"""
    if not theme_name.strip():
        return False, "Имя темы не может быть пустым"
    
    safe_name = "".join(c for c in theme_name if c.isalnum() or c in ('-', '_')).rstrip()
    if not safe_name:
        return False, "Недопустимое имя темы"
    if safe_name == "00_undo":
        return False, "Имя '00_undo' зарезервировано системой"
        
    target_dir = THEMES_DIR / safe_name
    
    try:
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        if TEMPLATES_DIR.exists():
            shutil.copytree(TEMPLATES_DIR, target_dir / "templates")
        if STATIC_DIR.exists():
            shutil.copytree(STATIC_DIR, target_dir / "static")
            
        return True, f"Тема '{safe_name}' успешно сохранена!"
    except Exception as e:
        return False, f"Ошибка при сохранении: {str(e)}"

def load_theme(theme_name):
    """Восстанавливает templates и static из выбранной темы (с бэкапом текущего)"""
    source_dir = THEMES_DIR / theme_name
    
    if not source_dir.exists():
        return False, "Тема не найдена"
        
    try:
        # --- СОХРАНЯЕМ ТЕКУЩЕЕ СОСТОЯНИЕ В 00_undo ---
        if UNDO_DIR.exists():
            shutil.rmtree(UNDO_DIR)
        UNDO_DIR.mkdir(parents=True, exist_ok=True)
        
        if TEMPLATES_DIR.exists():
            shutil.copytree(TEMPLATES_DIR, UNDO_DIR / "templates")
        if STATIC_DIR.exists():
            shutil.copytree(STATIC_DIR, UNDO_DIR / "static")
        # ----------------------------------------------

        # Удаляем текущие папки и восстанавливаем из темы
        if TEMPLATES_DIR.exists():
            shutil.rmtree(TEMPLATES_DIR)
        if STATIC_DIR.exists():
            shutil.rmtree(STATIC_DIR)
            
        shutil.copytree(source_dir / "templates", TEMPLATES_DIR)
        shutil.copytree(source_dir / "static", STATIC_DIR)
        
        return True, f"Тема '{theme_name}' загружена. Предыдущее состояние сохранено."
    except Exception as e:
        return False, f"Ошибка при загрузке: {str(e)}"

def undo_last_theme_load():
    """Восстанавливает состояние из папки 00_undo"""
    if not UNDO_DIR.exists():
        return False, "Нечего отменять! Предыдущее состояние не найдено."
        
    try:
        if TEMPLATES_DIR.exists():
            shutil.rmtree(TEMPLATES_DIR)
        if STATIC_DIR.exists():
            shutil.rmtree(STATIC_DIR)
            
        shutil.copytree(UNDO_DIR / "templates", TEMPLATES_DIR)
        shutil.copytree(UNDO_DIR / "static", STATIC_DIR)
        
        # После успешного восстановления удаляем бэкап, чтобы не нажать дважды
        shutil.rmtree(UNDO_DIR)
        
        return True, "Отмена успешна! Возвращен предыдущий дизайн."
    except Exception as e:
        return False, f"Ошибка при отмене: {str(e)}"