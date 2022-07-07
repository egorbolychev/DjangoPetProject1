from django import template
from men.models import *

register = template.Library()


@register.inclusion_tag('men/menu.html')
def show_menu():

    menu = [{'title': "О сайте", 'url_name': 'about'},
            {'title': "Добавить статью", 'url_name': 'add_page'},
            {'title': "Обратная связь", 'url_name': 'contact'},
            {'title': "Войти", 'url_name': 'login'}]

    return {"menu": menu}


@register.inclusion_tag('men/list_categories.html')
def show_categories(sort=None, cat_selected=0):
    if not sort:
        cats = Category.objects.all()
    else:
        cats = Category.objects.order_by(sort)

    return {"cats": cats, "cat_selected": cat_selected}
