# pat/patrimonio/templatetags/patrimonio_extras.py

from django import template
import locale

register = template.Library()

@register.filter
def currency_br(value):
    try:
        # Tenta configurar o locale para pt_BR.UTF-8 ou pt_BR
        # Isso pode variar entre sistemas operacionais (Linux/Windows)
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR')
        except locale.Error:
            # Se falhar, tenta outra combinação comum ou desiste
            locale.setlocale(locale.LC_ALL, '') # Reseta para o padrão do sistema ou ""

    # Formata o valor como moeda. O True no final adiciona separador de milhares.
    # '%.' para decimal places, '2f' para 2 casas decimais, '%' para usar locale
    return locale.currency(value, grouping=True, symbol=True)
    # O symbol=True geralmente adiciona o R$. Se não adicionar, use f"R$ {locale.format_string('%.2f', value, grouping=True)}"