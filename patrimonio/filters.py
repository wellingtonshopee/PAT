import django_filters
from django import forms
from .models import ItemPatrimonio, CategoriaPatrimonio, LocalizacaoPatrimonio
from django.contrib.auth import get_user_model

User = get_user_model()

class ItemPatrimonioFilter(django_filters.FilterSet):
    search_query = django_filters.CharFilter(
        method='filter_by_search_query',
        label='Pesquisar (Nome ou Código)',
    )

    categoria = django_filters.ModelChoiceFilter(
        queryset=CategoriaPatrimonio.objects.all(),
        empty_label="Todas as Categorias",
        label='Categoria',
    )

    localizacao = django_filters.ModelChoiceFilter(
        queryset=LocalizacaoPatrimonio.objects.all(),
        empty_label="Todas as Localizações",
        label='Localização',
    )

    responsavel_atual = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        empty_label="Todos os Responsáveis",
        label='Responsável',
    )

    estado_conservacao = django_filters.ChoiceFilter(
        choices=ItemPatrimonio.ESTADO_CONSERVACAO_CHOICES,
        empty_label="Todos os Estados",
        label='Estado de Conservação',
    )

    status = django_filters.ChoiceFilter(
        choices=ItemPatrimonio.STATUS_CHOICES,
        empty_label="Todos os Status",
        label='Status',
    )

    data_aquisicao_inicio = django_filters.DateFilter(
        field_name='data_aquisicao',
        lookup_expr='gte',
        label='Data Aquisição (De)',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    data_aquisicao_fim = django_filters.DateFilter(
        field_name='data_aquisicao',
        lookup_expr='lte',
        label='Data Aquisição (Até)',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = ItemPatrimonio
        fields = [
            'search_query',
            'categoria',
            'localizacao',
            'responsavel_atual',
            'estado_conservacao',
            'status',
            'data_aquisicao_inicio',
            'data_aquisicao_fim',
        ]

    def filter_by_search_query(self, queryset, name, value):
        from django.db.models import Q
        return queryset.filter(
            Q(nome__icontains=value) |
            Q(codigo_patrimonial__icontains=value)
        )
