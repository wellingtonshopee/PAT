# financeiro/templatetags/custom_filters.py
from django import template
import locale # Importe o módulo locale

register = template.Library()

@register.filter
def format_currency_br(value):
    """
    Formata um valor numérico para o padrão monetário brasileiro (ex: 1.100,00).
    Tenta usar o locale pt_BR para formatação. Se falhar, usa um fallback manual.
    """
    if value is None:
        return ""
    
    try:
        val_float = float(value)
        
        # Tenta configurar o locale para português do Brasil
        # Pode falhar em alguns ambientes (ex: Windows sem pt_BR instalado ou Linux sem locale gerado)
        current_locale = None
        try:
            # Tenta pt_BR.UTF-8 (para Linux/macOS)
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8') 
            current_locale = locale.getlocale(locale.LC_ALL)
        except locale.Error:
            try:
                # Tenta Portuguese_Brazil.1252 (para Windows)
                locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
                current_locale = locale.getlocale(locale.LC_ALL)
            except locale.Error:
                # Se ambos falharem, o locale permanece o padrão ou é None
                pass

        # Se o locale foi configurado com sucesso para algo brasileiro, usa o formato de moeda
        if current_locale and ('pt_BR' in current_locale[0] or 'Portuguese_Brazil' in current_locale[0]):
            # Formata como moeda, com duas casas decimais, sem símbolo (o R$ já está no HTML)
            # e com agrupamento de milhares.
            formatted_value = locale.currency(val_float, grouping=True, symbol=False)
            # O locale.currency pode retornar X.XXX,XX ou X,XXX.XX dependendo da versão do Python/OS
            # Garantimos o padrão X.XXX,XX
            if '.' in formatted_value and ',' in formatted_value:
                 # Se tem ponto e vírgula, verifica a ordem. 
                 # Se ponto antes da vírgula, está ok (1.000,00)
                 # Se vírgula antes do ponto, inverte (1,000.00 -> 1.000,00)
                if formatted_value.find('.') > formatted_value.find(','): # Ex: 1,000.00
                    formatted_value = formatted_value.replace(',', 'X').replace('.', ',').replace('X', '.')
            elif ',' not in formatted_value and '.' in formatted_value: # Ex: 1000.00 (sem separador de milhares, mas ponto decimal)
                formatted_value = formatted_value.replace('.', ',') # Só troca o decimal

        else:
            # Fallback manual se o locale não puder ser configurado ou não for brasileiro
            # Garante duas casas decimais e depois troca ponto por vírgula e adiciona separador de milhares
            formatted_value = f"{val_float:,.2f}" # Ex: 2500.00 -> "2,500.00" (padrão americano com vírgula de milhar)
            # Troca vírgula de milhar americana por "X" temporário
            formatted_value = formatted_value.replace(",", "X")
            # Troca ponto decimal americano por vírgula brasileira
            formatted_value = formatted_value.replace(".", ",")
            # Troca "X" de volta para ponto (separador de milhar brasileiro)
            formatted_value = formatted_value.replace("X", ".")
        
        # Reseta o locale para evitar efeitos colaterais em outras partes da aplicação
        locale.setlocale(locale.LC_ALL, '') 
        
        return formatted_value
    except (ValueError, TypeError):
        # Se não for um número válido, retorna o valor original como string
        return str(value)