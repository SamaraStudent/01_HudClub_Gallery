import shutil
from pathlib import Path
from datetime import datetime

THEMES_DIR = Path(__file__).parent.parent / "themes"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
STATIC_DIR = Path(__file__).parent.parent / "static"

def get_themes():
    """Возвращает список названий доступных тем"""
    if not THEMES_DIR.exists():
        return []
    return [d.name for d in THEMES_DIR.iterdir() if d.is_dir()]

def save_current_theme(theme_name):
    """Сохраняет текущие templates и static в папку themes/theme_name"""
    if not theme_name.strip():
        return False, "Имя темы не может быть пустым"
    
    # Очищаем имя от недопустимых символов
    safe_name = "".join(c for c in theme_name if c.isalnum() or c in ('-', '_')).rstrip()
    if not safe_name:
        return False, "Недопустимое имя темы"
        
    target_dir = THEMES_DIR / safe_name
    
    try:
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Копируем шаблоны и статику
        if TEMPLATES_DIR.exists():
            shutil.copytree(TEMPLATES_DIR, target_dir / "templates")
        if STATIC_DIR.exists():
            shutil.copytree(STATIC_DIR, target_dir / "static")
            
        return True, f"Тема '{safe_name}' успешно сохранена!"
    except Exception as e:
        return False, f"Ошибка при сохранении: {str(e)}"

def load_theme(theme_name):
    """Восстанавливает templates и static из выбранной темы"""
    source_dir = THEMES_DIR / theme_name
    
    if not source_dir.exists():
        return False, "Тема не найдена"
        
    try:
        # Удаляем текущие папки
        if TEMPLATES_DIR.exists():
            shutil.rmtree(TEMPLATES_DIR)
        if STATIC_DIR.exists():
            shutil.rmtree(STATIC_DIR)
            
        # Восстанавливаем из темы
        shutil.copytree(source_dir / "templates", TEMPLATES_DIR)
        shutil.copytree(source_dir / "static", STATIC_DIR)
        
        return True, f"Тема '{theme_name}' успешно загружена!"
    except Exception as e:
        return False, f"Ошибка при загрузке: {str(e)}"