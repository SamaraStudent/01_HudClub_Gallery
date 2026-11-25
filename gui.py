import json
from pathlib import Path
import nicegui.ui as ui
from config import HASHTAGS_JSON

# --- 辅助函数 ---
def load_hashtags():
    if HASHTAGS_JSON.exists():
        with open(HASHTAGS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_hashtags(data):
    with open(HASHTAGS_JSON, "w", encoding="utf-8") as f:
        # indent=2 делает файл красивым и читаемым
        json.dump(data, f, ensure_ascii=False, indent=2)

# 全局变量，存放从文件读取的数据
hashtags_data = load_hashtags()

@ui.page('/')
def main_page():
    ui.label('HudClub Gallery Admin').classes('text-3xl font-bold mb-6 text-blue-400')
    
    with ui.tabs().classes('w-full') as tabs:
        tab_paths = ui.tab('Настройки путей', icon='settings')
        tab_hashtags = ui.tab('Хештеги', icon='tag')
        
    with ui.tab_panels(tabs, value=tab_hashtags).classes('w-full'):
        
        # === Вкладка Пути (Пока пустышка) ===
        with ui.tab_panel(tab_paths):
            with ui.card().classes('w-full'):
                ui.label('Настройки путей (в разработке)').classes('text-lg')

        # === Вкладка Хештеги ===
        with ui.tab_panel(tab_hashtags):
            
            # Функция для обновления интерфейса (перерисовывает чекбоксы)
            @ui.refreshable
            def render_hashtags():
                # Группируем данные по категориям
                categories = {}
                for idx, item in enumerate(hashtags_data):
                    cat = item.get('category', 'Без категории')
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append((idx, item))

                # Выводим каждую категорию
                for cat_name, items in categories.items():
                    with ui.expansion(cat_name, icon='folder').classes('w-full bg-gray-800 text-white mb-2'):
                        with ui.column().classes('p-4 w-full gap-2'):
                            for global_idx, item in items:
                                # Создаем чекбокс и привязываем к функции сохранения
                                ui.checkbox(
                                    f"{item['hashtag']} — {item['description']}",
                                    value=item['is_active'],
                                    on_change=lambda e, i=global_idx: update_hashtag_state(i, e.value)
                                ).classes('text-lg')

            # Логика обновления состояния одного хештега
            def update_hashtag_state(idx, value):
                hashtags_data[idx]['is_active'] = value
                save_hashtags(hashtags_data)

            # Кнопки глобального управления
            def select_all():
                for item in hashtags_data:
                    item['is_active'] = True
                save_hashtags(hashtags_data)
                render_hashtags.refresh() # Перерисовываем только блок с чекбоксами
                
            def deselect_all():
                for item in hashtags_data:
                    item['is_active'] = False
                save_hashtags(hashtags_data)
                render_hashtags.refresh()

            # Блок с кнопками
            with ui.row().classes('mb-6 gap-4'):
                ui.button('Выбрать ВСЕ', on_click=select_all, color='green')
                ui.button('Снять ВСЕ', on_click=deselect_all, color='red')
                ui.button('Сохранить выбранное', on_click=lambda: ui.notify('Все изменения уже сохранены!', type='positive'), color='blue')

            # Вызов функции отрисовки чекбоксов
            render_hashtags()

ui.run(title='HudClub Gallery Admin', reload=False)