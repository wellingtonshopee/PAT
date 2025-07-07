# pat/usuarios/filters.py

import django_filters
from .models import LogAtividade
from django.contrib.auth.models import User
from django import forms # Importe 'forms' do Django para usar widgets padrão

class LogAtividadeFilter(django_filters.FilterSet):
    # Filtro para o campo 'acao' (ação realizada)
    acao = django_filters.CharFilter(
        lookup_expr='icontains', # Busca por "contém" (case-insensitive)
        label='Ação Contém',
        help_text='Filtrar por texto na ação (ex: "Cadastro", "Atualização")'
    )
    
    # Filtro para o campo 'descricao'
    descricao = django_filters.CharFilter(
        lookup_expr='icontains', # Busca por "contém" (case-insensitive)
        label='Descrição Contém',
        help_text='Filtrar por texto na descrição'
    )

    # Filtro para o campo 'usuario'
    usuario = django_filters.ModelChoiceFilter(
        queryset=User.objects.all().order_by('username'),
        field_name='usuario__username', # Filtra pelo username do usuário relacionado
        empty_label='Qualquer Usuário',
        label='Usuário',
        help_text='Filtrar por usuário que realizou a ação'
    )

    # Filtro para data de início (maior ou igual a)
    data_inicio = django_filters.DateFilter(
        field_name='data_hora', 
        lookup_expr='gte', # Greater than or equal (maior ou igual)
        label='A partir da Data',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
        help_text='Filtrar logs a partir desta data'
    )
    
    # Filtro para data de fim (menor ou igual a)
    data_fim = django_filters.DateFilter(
        field_name='data_hora', 
        lookup_expr='lte', # Less than or equal (menor ou igual)
        label='Até a Data',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text='Filtrar logs até esta data'
    )

    # NOVIDADE: Adicionando o filtro de IP explicitamente como CharFilter
    ip_endereco = django_filters.CharFilter(
        lookup_expr='icontains', # Permite buscar por "contém" no IP
        label='IP Contém',
        help_text='Filtrar por texto no endereço IP'
    )

    class Meta:
        model = LogAtividade
        # Definimos os campos que podem ser filtrados
        # Certifique-se que 'ip_endereco' está na lista de fields
        fields = ['acao', 'descricao', 'usuario', 'data_inicio', 'data_fim', 'ip_endereco']
        # REMOVIDO: O 'filter_overrides' que causava o erro
        # filter_overrides = {
        #     django_filters.GenericIPAddressFilter: {
        #         'filter_class': django_filters.CharFilter,
        #         'lookup_expr': 'icontains',
        #     },
        # }