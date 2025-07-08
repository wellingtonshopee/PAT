import locale
import os

def configure_locale():
    try:
        # Tenta definir o locale para pt_BR.UTF-8
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error as e:
        # Se pt_BR.UTF-8 não for suportado, tenta pt_BR
        print(f"Aviso: Não foi possível definir o locale pt_BR.UTF-8: {e}. Tentando pt_BR.")
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR')
        except locale.Error as e_br:
            # Se pt_BR também não for suportado, tenta um locale padrão genérico para fallback
            # Isso pode causar a formatação de moeda sem o símbolo R$ ou com . ao invés de ,
            print(f"Aviso: Não foi possível definir o locale pt_BR: {e_br}. Tentando locale padrão do sistema.")
            try:
                locale.setlocale(locale.LC_ALL, '') # Tenta o padrão do sistema
            except locale.Error as e_default:
                print(f"Erro Crítico: Não foi possível definir nenhum locale: {e_default}")
                # Se mesmo o default falhar, pode ser um problema maior no ambiente
                # Para deploy, pode ser melhor deixar o erro acontecer para depuração
                pass # Ou levantar a exceção novamente se quiser que o app falhe neste ponto

# Chama a função para configurar o locale quando este módulo é importado
configure_locale()