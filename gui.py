from nicegui import ui
from ui import tab_paths, tab_generation, tab_manager, tab_themes

@ui.page('/')
def main_page():
    ui.label('HudClub Gallery Admin').classes('text-4xl font-bold mb-8 text-blue-500')
    
    with ui.tabs().classes('w-full border-b border-gray-300') as tabs:
        tab_p = ui.tab('Настройки путей', icon='settings')
        tab_g = ui.tab('Хештеги и генерация', icon='tag')
        tab_m = ui.tab('База хештегов', icon='edit')
        tab_t = ui.tab('Дизайн и Темы', icon='palette')
        
    with ui.tab_panels(tabs, value=tab_g).classes('w-full pt-4'):
        with ui.tab_panel(tab_p):
            tab_paths.render_tab()
            
        with ui.tab_panel(tab_g):
            tab_generation.render_tab()
            
        with ui.tab_panel(tab_m):
            tab_manager.render_tab()
            
        with ui.tab_panel(tab_t):
            tab_themes.render_tab()

ui.run(title='HudClub Gallery Admin', reload=False)