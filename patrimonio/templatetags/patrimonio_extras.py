from django import template
# A linha 'import locale' foi REMOVIDA, pois não será mais usada.

register = template.Library()

@register.filter
def currency_br(value):
    try:
        # Converte para float para garantir a formatação decimal
        value = float(value)
        # Formata como moeda brasileira:
        # Primeiro, formata com vírgula de milhares e ponto decimal (padrão americano)
        # Depois, inverte os separadores para o padrão brasileiro (ponto de milhares, vírgula decimal)
        # Adiciona o R$ no início
        return "R$ {:,.2f}".format(value).replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        # Retorna o valor original se não for um número válido
        return value