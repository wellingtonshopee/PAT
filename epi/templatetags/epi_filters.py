from django import template

register = template.Library()

@register.filter
def starts_with(value, arg):
    """
    Verifica se uma string 'value' começa com uma substring 'arg'.
    """
    return value.startswith(arg)