from jinja2 import Environment, FileSystemLoader
from pathlib import Path

# Указываем папку с шаблонами
env = Environment(loader=FileSystemLoader('templates'))

def make_nav_buttons(all_active: bool, list_active: bool) -> str:
    """Собирает HTML двух кнопок: 'Все' и 'Список'."""
    if all_active:
        all_btn = '<span class="btn btn-active">🖼️ Все</span>'
    else:
        all_btn = '<a href="all_photos.html" class="btn">🖼️ Все</a>'

    if list_active:
        list_btn = '<span class="btn btn-active">📋 Список</span>'
    else:
        list_btn = '<a href="index.html" class="btn">📋 Список</a>'

    return all_btn + list_btn

def render_index(main_users, unknown_users, new_count_by_user, new_reviews, title_suffix, grouped_hashtags):
    """Рендерит страницу со списком участников (index.html)"""
    template = env.get_template('index.html')
    return template.render(
        title="Список авторов",
        nav_buttons=make_nav_buttons(all_active=False, list_active=True),
        main_users=main_users,
        unknown_users=unknown_users,
        new_count_by_user=new_count_by_user,
        new_reviews=new_reviews,
        title_suffix=title_suffix,
        grouped_hashtags=grouped_hashtags
    )

def render_all_photos(all_to_gen, target_hashtags, new_reviews, title_suffix, grouped_hashtags):
    """Рендерит страницу 'Общая выставка' (all_photos.html)"""
    template = env.get_template('all_photos.html')
    return template.render(
        title="Общая выставка",
        nav_buttons=make_nav_buttons(all_active=True, list_active=False),
        all_to_gen=all_to_gen,
        target_hashtags=target_hashtags,
        new_reviews=new_reviews,
        title_suffix=title_suffix,
        grouped_hashtags=grouped_hashtags
    )

def render_user(user, target_hashtags, new_reviews, grouped_hashtags):
    """Рендерит персональную страницу автора (user.html)"""
    template = env.get_template('user.html')
    return template.render(
        title=f"{user['list_number']}. {user['name']}",
        nav_buttons=make_nav_buttons(all_active=False, list_active=False),
        user=user,
        target_hashtags=target_hashtags,
        new_reviews=new_reviews,
        grouped_hashtags=grouped_hashtags
    )