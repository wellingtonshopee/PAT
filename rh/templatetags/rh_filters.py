# rh/templatetags/rh_filters.py

from django import template
from django.forms import BaseFormSet
from epi.models import ColaboradorEPI # Importe o modelo ColaboradorEPI aqui, se ainda não estiver importado

register = template.Library()

@register.filter
def get_form_for_colaborador(formset, colaborador_id):
    """
    Retorna o formulário do formset que corresponde ao ID do colaborador.
    Itera sobre os formulários do formset e verifica o campo 'colaborador'.
    """
    # Verifica se o primeiro argumento é realmente um BaseFormSet para evitar erros.
    if not isinstance(formset, BaseFormSet):
        return None

    # Converte o ID do colaborador para string para garantir comparação correta
    colaborador_id_str = str(colaborador_id)

    for form in formset.forms:
        form_colab_id = None
        
        # Tenta obter o ID do colaborador de diferentes lugares no formulário:
        # 1. Do 'initial' (para requisições GET, quando a view preenche os dados)
        if 'colaborador' in form.initial:
            form_colab_id = form.initial['colaborador']
        # 2. Do 'cleaned_data' (para requisições POST, após validação)
        elif form.is_bound and 'colaborador' in form.cleaned_data and form.cleaned_data['colaborador']:
            form_colab_id = form.cleaned_data['colaborador'].id
        # 3. Da instância do modelo associada ao formulário (para registros existentes)
        elif form.instance and form.instance.pk and form.instance.colaborador:
            form_colab_id = form.instance.colaborador.id

        # Compara o ID encontrado com o ID do colaborador atual
        if form_colab_id is not None and str(form_colab_id) == colaborador_id_str:
            return form
            
    return None # Retorna None se nenhum formulário correspondente for encontrado

# Se você precisar de um filtro para obter o nome do colaborador apenas pelo ID,
# embora o método de iterar sobre 'colaboradores_queryset' no HTML seja mais robusto,
# aqui está um exemplo (certifique-se de que ColaboradorEPI está importado acima):
# @register.filter
# def get_colaborador_name(colaborador_id):
#     try:
#         return ColaboradorEPI.objects.get(id=colaborador_id).nome_completo
#     except ColaboradorEPI.DoesNotExist:
#         return "Colaborador Não Encontrado"