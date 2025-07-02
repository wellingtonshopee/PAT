# financeiro/filters.py

import django_filters
from django.db.models import Q
from django import forms
# from django.utils import timezone # Não é necessário aqui, usado na view

from .models import ContaPagar, ContaReceber, CategoriaFinanceira, FormaPagamento
from fornecedores.models import Fornecedor
from clientes.models import Cliente


class ContaPagarFilter(django_filters.FilterSet):
    search_query = django_filters.CharFilter(
        method='filter_by_search_query',
        label="Buscar",
        widget=forms.TextInput(attrs={'placeholder': 'Descrição, Fornecedor...'})
    )

    status = django_filters.ChoiceFilter(
        choices=ContaPagar.STATUS_CHOICES,
        empty_label="Todos os Status",
        label="Status",
        widget=forms.Select()
    )

    categoria = django_filters.ModelChoiceFilter(
        queryset=CategoriaFinanceira.objects.filter(tipo='DESPESA').order_by('nome'),
        empty_label="Todas as Categorias",
        label="Categoria",
        widget=forms.Select()
    )

    fornecedor = django_filters.ModelChoiceFilter(
        queryset=Fornecedor.objects.all().order_by('razao_social'),
        empty_label="Todos os Fornecedores",
        label="Fornecedor",
        widget=forms.Select()
    )

    valor_min = django_filters.NumberFilter(
        field_name='valor', lookup_expr='gte',
        label='Valor mínimo',
        widget=forms.NumberInput(attrs={'placeholder': 'Valor mínimo'})
    )
    valor_max = django_filters.NumberFilter(
        field_name='valor', lookup_expr='lte',
        label='Valor máximo',
        widget=forms.NumberInput(attrs={'placeholder': 'Valor máximo'})
    )

    data_vencimento = django_filters.DateFromToRangeFilter(
        label="Vencimento",
        widget=django_filters.widgets.DateRangeWidget(attrs={'type': 'date'})
    )

    data_pagamento = django_filters.DateFromToRangeFilter(
        label="Pagamento",
        widget=django_filters.widgets.DateRangeWidget(attrs={'type': 'date'})
    )

    class Meta:
        model = ContaPagar
        fields = [
            'search_query', 'status', 'categoria', 'fornecedor',
            'valor_min', 'valor_max',
            'data_vencimento', 'data_pagamento'
        ]

    def filter_by_search_query(self, queryset, name, value):
        return queryset.filter(
            Q(descricao__icontains=value) |
            Q(fornecedor__razao_social__icontains=value) |
            Q(fornecedor__nome_fantasia__icontains=value)
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.form.fields.items():
            if isinstance(field.widget, django_filters.widgets.DateRangeWidget):
                # Para widgets DateRange, adicione a classe 'form-control' a cada sub-widget
                for subwidget in field.widget.widgets:
                    subwidget.attrs.update({'class': 'form-control'})
            else:
                # Para outros tipos de widgets, adicione a classe 'form-control'
                current_class = field.widget.attrs.get('class', '')
                if 'form-control' not in current_class:
                    field.widget.attrs['class'] = (current_class + ' form-control').strip()


class ContaReceberFilter(django_filters.FilterSet):
    search_query = django_filters.CharFilter(
        method='filter_by_search_query',
        label="Buscar",
        widget=forms.TextInput(attrs={'placeholder': 'Descrição, Cliente...'})
    )

    status = django_filters.ChoiceFilter(
        choices=ContaReceber.STATUS_CHOICES,
        empty_label="Todos os Status",
        label="Status",
        widget=forms.Select()
    )

    categoria = django_filters.ModelChoiceFilter(
        queryset=CategoriaFinanceira.objects.filter(tipo='RECEITA').order_by('nome'),
        empty_label="Todas as Categorias",
        label="Categoria",
        widget=forms.Select()
    )

    cliente = django_filters.ModelChoiceFilter(
        queryset=Cliente.objects.all().order_by('razao_social'),
        empty_label="Todos os Clientes",
        label="Cliente",
        widget=forms.Select()
    )

    valor_min = django_filters.NumberFilter(
        field_name='valor', lookup_expr='gte',
        label='Valor mínimo',
        widget=forms.NumberInput(attrs={'placeholder': 'Valor mínimo'})
    )
    valor_max = django_filters.NumberFilter(
        field_name='valor', lookup_expr='lte',
        label='Valor máximo',
        widget=forms.NumberInput(attrs={'placeholder': 'Valor máximo'})
    )

    data_lancamento = django_filters.DateFromToRangeFilter(
        label="Lançamento",
        widget=django_filters.widgets.DateRangeWidget(attrs={'type': 'date'})
    )

    data_vencimento = django_filters.DateFromToRangeFilter(
        label="Vencimento",
        widget=django_filters.widgets.DateRangeWidget(attrs={'type': 'date'})
    )

    data_recebimento = django_filters.DateFromToRangeFilter(
        label="Recebimento",
        widget=django_filters.widgets.DateRangeWidget(attrs={'type': 'date'})
    )

    class Meta:
        model = ContaReceber
        fields = [
            'search_query', 'status', 'categoria', 'cliente',
            'valor_min', 'valor_max',
            'data_lancamento',
            'data_vencimento', 'data_recebimento'
        ]

    def filter_by_search_query(self, queryset, name, value):
        return queryset.filter(
            Q(descricao__icontains=value) |
            Q(cliente__razao_social__icontains=value) |
            Q(cliente__nome_fantasia__icontains=value)
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.form.fields.items():
            if isinstance(field.widget, django_filters.widgets.DateRangeWidget):
                for subwidget in field.widget.widgets:
                    subwidget.attrs.update({'class': 'form-control'})
            else:
                current_class = field.widget.attrs.get('class', '')
                if 'form-control' not in current_class:
                    field.widget.attrs['class'] = (current_class + ' form-control').strip()



### Novo Filtro para o Relatório Financeiro (`RelatorioFinanceiroFilter`)

class RelatorioFinanceiroFilter(django_filters.FilterSet):
    # Usamos DateFilter simples aqui, pois DateFromToRangeFilter cria dois campos
    # e na view estamos usando data_inicio e data_fim separadamente.
    data_inicio = django_filters.DateFilter(
        field_name='data_vencimento', lookup_expr='gte',
        label='Data Início (Vencimento)',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    data_fim = django_filters.DateFilter(
        field_name='data_vencimento', lookup_expr='lte',
        label='Data Fim (Vencimento)',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    # Novo campo para Tipo de Conta (Contas a Pagar / Receber)
    TIPO_CONTA_CHOICES = [
        ('', 'Todas as Contas'),
        ('pagar', 'Contas a Pagar'),
        ('receber', 'Contas a Receber'),
    ]
    tipo_conta = django_filters.ChoiceFilter(
        choices=TIPO_CONTA_CHOICES,
        empty_label="Todas as Contas",
        label="Tipo de Conta",
        # Este método não precisa de lógica de filtragem aqui, pois a view decidirá qual queryset usar.
        # Ele serve apenas para o formulário.
        method='no_op_filter' 
    )

    # Status geral para o relatório (para consolidar 'PAGA/RECEBIDA', 'A_PAGAR/A_RECEBER', 'CANCELADA', 'VENCIDA')
    STATUS_GERAL_CHOICES = [
        ('', 'Todos os Status'),
        ('pendente', 'Pendente (Aberto)'),
        ('vencida', 'Vencida'),
        ('realizado', 'Realizado (Pago/Recebido)'),
        ('cancelado', 'Cancelado'),
    ]
    status_geral = django_filters.ChoiceFilter(
        choices=STATUS_GERAL_CHOICES,
        empty_label="Todos os Status",
        label="Status Geral",
        # Este método também não precisa de lógica de filtragem aqui.
        # A view usará o valor selecionado para aplicar a lógica de status em cada queryset.
        method='no_op_filter'
    )

    categoria = django_filters.ModelChoiceFilter(
        queryset=CategoriaFinanceira.objects.all().order_by('nome'), # Todas as categorias
        empty_label="Todas as Categorias",
        label="Categoria"
    )

    fornecedor = django_filters.ModelChoiceFilter(
        queryset=Fornecedor.objects.all().order_by('razao_social'),
        empty_label="Todos os Fornecedores",
        label="Fornecedor"
    )

    cliente = django_filters.ModelChoiceFilter(
        queryset=Cliente.objects.all().order_by('razao_social'),
        empty_label="Todos os Clientes",
        label="Cliente"
    )

    search_query = django_filters.CharFilter(
        label="Buscar (Descrição)",
        lookup_expr='icontains', # Busca direta na descrição
        field_name='descricao',
        widget=forms.TextInput(attrs={'placeholder': 'Descrição...'})
    )

    class Meta:
        # Não associamos a um modelo específico aqui, pois o filtro é para ambos os modelos
        model = None
        fields = [] # Os campos são definidos diretamente acima

    # Método de filtro "no-op" para campos que serão tratados na view
    def no_op_filter(self, queryset, name, value):
        return queryset

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona a classe 'form-control' para todos os widgets do formulário
        for field_name, field in self.form.fields.items():
            current_class = field.widget.attrs.get('class', '')
            if 'form-control' not in current_class:
                field.widget.attrs['class'] = (current_class + ' form-control').strip()