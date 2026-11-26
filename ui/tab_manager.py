import json
from datetime import datetime
from nicegui import ui
from core.hashtag_manager import load_hashtags, save_hashtags

CATEGORIES = ["Живопись", "Рисунок", "Композиция", "Декоративная живопись и композиция", "Пленэр"]

def render_tab():
    @ui.refreshable
    def render_hashtag_table():
        # Загружаем актуальные данные при каждом обновлении
        current_data = load_hashtags()
        sorted_data = sorted(current_data, key=lambda x: x.get('id', 0))
        rows = [{'id': h.get('id'), 'tag': h.get('hashtag'), 'cat': h.get('category'), 'desc': h.get('description')} for h in sorted_data]
        
        columns = [
            {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left', 'sortable': True},
            {'name': 'tag', 'label': 'Хештег', 'field': 'tag', 'align': 'left'},
            {'name': 'cat', 'label': 'Категория', 'field': 'cat', 'align': 'left'},
            {'name': 'desc', 'label': 'Описание', 'field': 'desc', 'align': 'left'},
        ]
        
        table = ui.table(columns=columns, rows=rows, row_key='id').classes('w-full')
        table.add_slot('body-cell-actions', '<q-td :props="props"><q-btn icon="delete" color="red" flat dense @click="$parent.$emit(\'delete\', props.row.id)" /></q-td>')
        
        def handle_delete(e):
            item_id = e.args
            current_data = load_hashtags()
            new_data = [h for h in current_data if h.get('id') != item_id]
            save_hashtags(new_data)
            render_hashtag_table.refresh()
            ui.notify(f'Хештег с ID {item_id} удален', type='info')
        
        table.on('delete', handle_delete)

    with ui.row().classes('w-full gap-6 items-start flex-nowrap'):
        with ui.card().classes('w-96 shadow-sm'):
            ui.label('Добавить новый хештег').classes('text-xl font-bold mb-4')
            
            new_tag = ui.input('Хештег (с решеткой)').classes('w-full mb-2')
            new_cat = ui.select(CATEGORIES, label='Категория', value=CATEGORIES[0]).classes('w-full mb-2')
            new_desc = ui.input('Описание').classes('w-full mb-2')
            today_str = datetime.now().strftime("%d.%m.%Y")
            new_date = ui.input('Дата появления', value=today_str).classes('w-full mb-2')
            new_tg = ui.input('Ссылка Telegram').classes('w-full mb-2')
            new_boosty = ui.input('Ссылка Boosty', value="https://boosty.to/kanalhudogka").classes('w-full mb-4')
            
            def do_add_hashtag():
                # Используем str() и or "", чтобы гарантировать строку и убрать ошибки Pylance
                tag_val = str(new_tag.value or "").strip().lower()
                if not tag_val:
                    ui.notify('Введите хештег!', type='warning')
                    return
                if not tag_val.startswith('#'): 
                    tag_val = '#' + tag_val
                
                current_data = load_hashtags()
                if any(h.get('hashtag') == tag_val for h in current_data):
                    ui.notify('Такой хештег уже существует!', type='negative')
                    return
                
                max_id = max([h.get('id', 0) for h in current_data]) if current_data else 0
                new_item = {
                    "id": max_id + 1,
                    "hashtag": tag_val,
                    "category": str(new_cat.value or "Разное"),
                    "description": str(new_desc.value or "").strip(),
                    "first_seen_date": str(new_date.value or "").strip(),
                    "links": {
                        "telegram": str(new_tg.value or "").strip(), 
                        "boosty": str(new_boosty.value or "").strip()
                    },
                    "is_active": False
                }
                
                current_data.append(new_item)
                save_hashtags(current_data)
                
                ui.notify(f'Хештег {tag_val} добавлен!', type='positive')
                new_tag.value = ''
                new_desc.value = ''
                new_tg.value = ''
                render_hashtag_table.refresh()

            ui.button('Добавить', on_click=do_add_hashtag).classes('w-full bg-green-600 text-white')

        with ui.card().classes('flex-grow shadow-sm'):
            with ui.row().classes('w-full justify-between items-center mb-4'):
                ui.label('Существующие хештеги').classes('text-xl font-bold')
                ui.button(icon='refresh', on_click=lambda: render_hashtag_table.refresh()).props('flat')
            
            render_hashtag_table()