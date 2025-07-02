# clientes/filters.py

import django_filters
from .models import Cliente

class ClienteFilter(django_filters.FilterSet):
    # Filtro para 'razao_social' que faz uma busca "contains" (sensível a maiúsculas/minúsculas)
    razao_social = django_filters.CharFilter(
        field_name='razao_social',
        lookup_expr='icontains', # 'icontains' para busca case-insensitive
        label='Razão Social / Nome'
    )
    # Filtro para 'cnpj_cpf' que faz uma busca "contains" (sensível a maiúsculas/minúsculas)
    cnpj_cpf = django_filters.CharFilter(
        field_name='cnpj_cpf',
        lookup_expr='icontains',
        label='CNPJ/CPF'
    )
    # Filtro para 'email' com busca "contains"
    email = django_filters.CharFilter(
        field_name='email',
        lookup_expr='icontains',
        label='E-mail'
    )

    class Meta:
        model = Cliente
        fields = ['razao_social', 'cnpj_cpf', 'email'] # Campos que você quer filtrar