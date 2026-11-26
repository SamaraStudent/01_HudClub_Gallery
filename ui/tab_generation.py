from nicegui import ui, run
from core.generator import run_generation
from core.hashtag_manager import load_hashtags, save_hashtags

def update_main_icon(m_btn, c_items):
    act = sum(1 for i in c_items if i['is_active'])
    if act == len(c_items) and act > 0:
        m_btn.props('icon="check_box"')
    elif act == 0:
        m_btn.props('icon="check_box_outline_blank"')
    else:
        m_btn.props('icon="indeterminate_check_box"')

def render_tab():
    hashtags_data = load_hashtags()
    menu_refs = []

    with ui.row().classes('w-full items-start justify-start gap-4 mb-8 flex-nowrap'):
        for json_cat_name, display_name in [("Живопись", "Живопись"), ("Рисунок", "Рисунок"), ("Композиция", "Композиция"), ("Декоративная живопись и композиция", "Декоративка"), ("Пленэр", "Пленэр")]:
            cat_items = [item for item in hashtags_data if item.get('category') == json_cat_name]
            
            with ui.column().classes('w-64 shrink-0 relative'):
                with ui.row().classes('bg-blue-500 text-white p-2 rounded-md w-full items-center no-wrap cursor-pointer hover:bg-blue-600 transition-colors') as header:
                    main_btn = ui.button().props('flat dense color="white"').classes('p-0 min-h-0')
                    update_main_icon(main_btn, cat_items)
                    lbl = ui.label(display_name).classes('font-bold ml-2 flex-grow')
                    icon = ui.icon('expand_more').classes('text-white/80 transition-transform duration-200')
                
                with ui.menu().classes('p-0 w-64 shadow-lg border border-gray-200 rounded-md') as menu:
                    menu_refs.append(menu)
                    with ui.column().classes('p-2 max-h-[400px] overflow-y-auto gap-1 bg-white w-full'):
                        menu_cbs = []
                        for item in cat_items:
                            cb = ui.checkbox(item['hashtag'], value=item['is_active'])
                            menu_cbs.append(cb)
                            def on_child_change(e, it=item, m_btn=main_btn, c_items=cat_items):
                                it['is_active'] = e.value
                                save_hashtags(hashtags_data)
                                update_main_icon(m_btn, c_items)
                            cb.on_value_change(on_child_change)

                        def on_main_click(m_btn=main_btn, c_items=cat_items, m_cbs=menu_cbs):
                            act = sum(1 for i in c_items if i['is_active'])
                            target_val = not (act == len(c_items) and act > 0)
                            for it in c_items: it['is_active'] = target_val
                            save_hashtags(hashtags_data)
                            for cb in m_cbs: cb.value = target_val
                            update_main_icon(m_btn, c_items)

                        main_btn.on('click.stop', on_main_click)
                
                def on_menu_toggle(e, ic=icon):
                    if e.value: ic.classes(add='rotate-180')
                    else: ic.classes(remove='rotate-180')
                menu.on_value_change(on_menu_toggle)
                
                def open_menu(m=menu):
                    for m_ref in menu_refs:
                        if m_ref != m: m_ref.close()
                    m.open()
                header.on('click', open_menu)

    with ui.row().classes('mb-4 gap-4 items-center'):
        generate_btn = ui.button('Сгенерировать сайт', icon='play_arrow').classes('bg-blue-500 text-white font-bold px-6 py-2 rounded-md hover:bg-blue-600 transition-colors shadow-none')
        spinner = ui.spinner(size='lg', color='blue').classes('hidden')

    ui.label('Лог выполнения:').classes('mt-2 font-bold text-gray-500')
    log_area = ui.log(max_lines=100).classes('w-full h-48 font-mono text-sm bg-gray-900 text-green-400 border border-gray-700 rounded-md')

    async def start_generation():
        selected_tags = [item['hashtag'] for item in hashtags_data if item['is_active']]
        if not selected_tags:
            ui.notify('Выберите хотя бы один хештег!', type='warning')
            return
        
        generate_btn.disable()
        spinner.classes(remove='hidden')
        log_area.clear()
        log_area.push("Запуск генерации...")
        
        def gui_log(message):
            print(message)
            log_area.push(message)
        
        try:
            success = await run.io_bound(run_generation, selected_tags, gui_log)
            if success:
                log_area.push("\n✅ САЙТ УСПЕШНО СГЕНЕРИРОВАН!")
                ui.notify('Генерация завершена!', type='positive')
            else:
                log_area.push("\n❌ ОШИБКА ПРИ ГЕНЕРАЦИИ (см. лог)")
                ui.notify('Произошла ошибка, проверьте лог', type='negative')
        except Exception as e:
            log_area.push(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
            ui.notify('Критическая ошибка!', type='negative')
        finally:
            generate_btn.enable()
            spinner.classes(add='hidden')

    generate_btn.on_click(start_generation)