import json
from datetime import datetime
from nicegui import ui
from core.hashtag_manager import load_hashtags, save_hashtags

CATEGORIES = ["Живопись", "Рисунок", "Композиция", "Декоративная живопись и композиция", "Пленэр"]

def render_tab():
    # Храним ID хештега, который сейчас редактируем. Если None - добавляем новый.
    editing_id = None

    # Функция для сброса формы в режим "Добавления"
    def reset_form():
        nonlocal editing_id
        editing_id = None
        form_title.text = 'Добавить новый хештег'
        new_tag.value = ''
        new_desc.value = ''
        new_tg.value = ''
        # new_cat, new_date, new_boosty оставляем как есть для удобства
        btn_save.text = 'Добавить'
        btn_save.classes(replace='w-full bg-green-600 text-white')

    @ui.refreshable
    def table_area():
        current_data = load_hashtags()
        # Сортировка по убыванию ID (новые сверху)
        sorted_data = sorted(current_data, key=lambda x: x.get('id', 0), reverse=True)
        
        rows = []
        for h in sorted_data:
            links = h.get('links', {})
            rows.append({
                'id': h.get('id'),
                'tag': h.get('hashtag'),
                'cat': h.get('category'),
                'desc': h.get('description', ''),
                'date': h.get('first_seen_date', ''),
                'tg': links.get('telegram', ''),
                'boosty': links.get('boosty', '')
            })
        
        # Кнопка удаления теперь в самой первой колонке (слева)
        columns = [
            {'name': 'actions', 'label': 'Удалить', 'field': 'id', 'align': 'center'},
            {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left', 'sortable': True},
            {'name': 'tag', 'label': 'Хештег', 'field': 'tag', 'align': 'left'},
            {'name': 'cat', 'label': 'Категория', 'field': 'cat', 'align': 'left'},
            {'name': 'desc', 'label': 'Описание', 'field': 'desc', 'align': 'left'},
            {'name': 'date', 'label': 'Дата', 'field': 'date', 'align': 'left'},
            {'name': 'links', 'label': 'Ссылки', 'field': 'tg', 'align': 'left'},
        ]
        
        table = ui.table(columns=columns, rows=rows, row_key='id').classes('w-full').props('wrap-cells')
        
        # Слот для ссылок
        table.add_slot('body-cell-links', '''
            <q-td :props="props">
                <div v-if="props.row.tg" class="mb-1"><a :href="props.row.tg" target="_blank" class="text-blue-500 hover:text-blue-400 font-bold">TG</a></div>
                <div v-if="props.row.boosty"><a :href="props.row.boosty" target="_blank" class="text-orange-500 hover:text-orange-400 font-bold">Boosty</a></div>
            </q-td>
        ''')
        
        # Слот для кнопки удаления (добавили @click.stop, чтобы клик по корзине не вызывал редактирование)
        table.add_slot('body-cell-actions', '''
            <q-td :props="props">
                <q-btn icon="delete" color="red" flat dense @click.stop="$parent.$emit('delete', props.row.id)" />
            </q-td>
        ''')
        
        # Обработка клика по строке (загружаем данные в левую панель)
        def on_row_click(e):
            nonlocal editing_id
            row = e.args[1] # Получаем данные строки
            editing_id = row['id']
            
            form_title.text = f'Редактировать (ID: {editing_id})'
            new_tag.value = row['tag']
            new_cat.value = row['cat']
            new_desc.value = row['desc']
            new_date.value = row['date']
            new_tg.value = row['tg']
            new_boosty.value = row['boosty']
            
            btn_save.text = 'Сохранить изменения'
            btn_save.classes(replace='w-full bg-orange-500 text-white')
            
        table.on('rowClick', on_row_click)
        
        # Обработка удаления
        def handle_delete(e):
            nonlocal editing_id
            item_id = e.args
            current_data = load_hashtags()
            new_data = [h for h in current_data if h.get('id') != item_id]
            save_hashtags(new_data)
            table_area.refresh()
            
            # Если удалили тот, который сейчас редактируется - сбрасываем форму
            if editing_id == item_id:
                reset_form()
                
            ui.notify(f'Хештег с ID {item_id} удален', type='info')
        
        table.on('delete', handle_delete)

    # --- Отрисовка интерфейса вкладки ---
    with ui.row().classes('w-full gap-6 items-start flex-nowrap'):
        
        # Левая панель - Форма
        with ui.card().classes('w-80 shrink-0 shadow-sm'):
            form_title = ui.label('Добавить новый хештег').classes('text-xl font-bold mb-4')
            
            new_tag = ui.input('Хештег (с решеткой)').classes('w-full mb-2')
            new_cat = ui.select(CATEGORIES, label='Категория', value=CATEGORIES[0]).classes('w-full mb-2')
            new_desc = ui.input('Описание').classes('w-full mb-2')
            today_str = datetime.now().strftime("%d.%m.%Y")
            new_date = ui.input('Дата появления', value=today_str).classes('w-full mb-2')
            new_tg = ui.input('Ссылка Telegram').classes('w-full mb-2')
            new_boosty = ui.input('Ссылка Boosty', value="https://boosty.to/kanalhudogka").classes('w-full mb-4')
            
            def save_item():
                nonlocal editing_id
                tag_val = str(new_tag.value or "").strip().lower()
                if not tag_val:
                    ui.notify('Введите хештег!', type='warning')
                    return
                if not tag_val.startswith('#'): 
                    tag_val = '#' + tag_val
                
                current_data = load_hashtags()
                
                # РЕЖИМ ДОБАВЛЕНИЯ
                if editing_id is None:
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
                    ui.notify(f'Хештег {tag_val} добавлен!', type='positive')
                    
                # РЕЖИМ РЕДАКТИРОВАНИЯ
                else:
                    if any(h.get('hashtag') == tag_val and h.get('id') != editing_id for h in current_data):
                        ui.notify('Такой хештег уже есть у другого ID!', type='negative')
                        return
                        
                    for h in current_data:
                        if h.get('id') == editing_id:
                            h['hashtag'] = tag_val
                            h['category'] = str(new_cat.value or "Разное")
                            h['description'] = str(new_desc.value or "").strip()
                            h['first_seen_date'] = str(new_date.value or "").strip()
                            h['links'] = {
                                "telegram": str(new_tg.value or "").strip(), 
                                "boosty": str(new_boosty.value or "").strip()
                            }
                            break
                    ui.notify(f'Хештег {tag_val} обновлен!', type='positive')
                
                save_hashtags(current_data)
                reset_form()
                table_area.refresh()

            btn_save = ui.button('Добавить', on_click=save_item).classes('w-full bg-green-600 text-white')
            ui.button('Отмена', on_click=reset_form).props('flat').classes('w-full mt-2 text-gray-500')
            
        # Правая панель - Таблица
        with ui.card().classes('flex-grow shadow-sm overflow-hidden'):
            with ui.row().classes('w-full justify-between items-center mb-4'):
                ui.label('Существующие хештеги').classes('text-xl font-bold')
                ui.button(icon='refresh', on_click=lambda: table_area.refresh()).props('flat')
            
            table_area()