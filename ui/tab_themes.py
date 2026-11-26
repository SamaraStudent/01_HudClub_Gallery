from nicegui import ui
from core.theme_manager import get_themes, save_current_theme, load_theme, undo_last_theme_load

def render_tab():
    with ui.row().classes('w-full gap-8 items-start'):
        with ui.card().classes('w-96 shadow-sm'):
            ui.label('Сохранить текущий дизайн').classes('text-xl font-bold mb-4')
            ui.label('Создаст резервную копию папок templates и static.').classes('text-sm text-gray-500 mb-4')
            
            theme_name_input = ui.input(label='Название темы').classes('w-full mb-4')
            
            def do_save_theme():
                success, msg = save_current_theme(theme_name_input.value)
                if success:
                    ui.notify(msg, type='positive')
                    theme_name_input.value = ''
                    refresh_themes_dropdown()
                else:
                    ui.notify(msg, type='negative')

            ui.button('Сохранить тему', on_click=do_save_theme).classes('w-full bg-green-600 text-white')

        with ui.card().classes('w-96 shadow-sm'):
            ui.label('Загрузить сохраненный дизайн').classes('text-xl font-bold mb-4')
            ui.label('Текущий дизайн будет сохранен в 00_undo!').classes('text-sm text-orange-500 mb-4')
            
            theme_select = ui.select(options=get_themes(), label='Выберите тему').classes('w-full mb-4')
            
            def refresh_themes_dropdown():
                theme_select.options = get_themes()
                theme_select.update()

            def do_load_theme():
                if not theme_select.value:
                    ui.notify('Выберите тему из списка!', type='warning')
                    return
                success, msg = load_theme(theme_select.value)
                ui.notify(msg, type='positive' if success else 'negative')

            def do_undo():
                success, msg = undo_last_theme_load()
                ui.notify(msg, type='positive' if success else 'warning')
                if success: refresh_themes_dropdown()

            ui.button('Загрузить тему', on_click=do_load_theme).classes('w-full bg-blue-500 text-white')
            ui.button('Отменить загрузку (Undo)', on_click=do_undo).classes('w-full bg-red-500 text-white mt-2')
            ui.button('Обновить список', icon='refresh', on_click=refresh_themes_dropdown).props('flat').classes('w-full mt-2 text-gray-500')