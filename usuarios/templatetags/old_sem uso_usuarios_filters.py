# pat/usuarios/templatetags/usuarios_filters.py

from django import template

register = template.Library() # Esta linha é crucial!

@register.filter(name='add_class') # O 'name='add_class'' define como você o usa no template
def add_class(value, arg):
    """
    Adds a CSS class to a form field.
    Usage: {{ field|add_class:"my-class" }}
    """
    return value.as_widget(attrs={'class': arg})