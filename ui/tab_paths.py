from nicegui import ui

def render_tab():
    with ui.card().classes('w-full shadow-sm'):
        ui.label('Настройки путей (в разработке)').classes('text-lg')