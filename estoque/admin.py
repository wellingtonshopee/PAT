# pat/estoque/admin.py

from django.contrib import admin
from .models import Categoria, Localizacao, ItemEstoque, MovimentacaoEstoque # Importe MovimentacaoEstoque

# Personaliza como a Categoria aparece no Admin
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)

# Personaliza como a Localizacao aparece no Admin
@admin.register(Localizacao)
class LocalizacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)

# Personaliza como o ItemEstoque aparece no Admin
@admin.register(ItemEstoque)
class ItemEstoqueAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade', 'unidade_medida', 'categoria', 'localizacao', 'data_ultima_atualizacao')
    list_filter = ('categoria', 'localizacao', 'unidade_medida', 'data_ultima_atualizacao')
    search_fields = ('nome', 'codigo_interno', 'descricao')
    # Campos que podem ser editados diretamente na lista de itens
    list_editable = ('quantidade', 'unidade_medida', 'categoria', 'localizacao') 
    # Campos que aparecem no formulário de adição/edição na ordem desejada
    fieldsets = (
        (None, {
            'fields': ('nome', 'codigo_interno', 'descricao')
        }),
        ('Detalhes do Estoque', {
            'fields': ('quantidade', 'unidade_medida', 'preco_unitario', 'categoria', 'localizacao')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_ultima_atualizacao'),
            'classes': ('collapse',), # Colapsa a seção por padrão
        }),
    )
    # Campos somente leitura no formulário de edição
    readonly_fields = ('data_criacao', 'data_ultima_atualizacao')

@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('item', 'tipo_movimentacao', 'quantidade_movimentada', 'data_hora_movimentacao', 'movimentado_por')
    list_filter = ('tipo_movimentacao', 'item__categoria', 'movimentado_por', 'data_hora_movimentacao')
    search_fields = ('item__nome', 'item__codigo_interno', 'descricao', 'movimentado_por__username')

    # Definimos explicitamente os campos que queremos no formulário
    # E 'movimentado_por' está aqui para ser preenchido, mas será readonly.
    fields = (
        'item', 
        'tipo_movimentacao', 
        'quantidade_movimentada', 
        'descricao', 
        'movimentado_por', # Incluímos o campo aqui
        'data_hora_movimentacao', # Incluímos o campo aqui
    )

    # Definimos 'movimentado_por' e 'data_hora_movimentacao' como somente leitura
    # Assim, eles aparecem no formulário mas não podem ser editados.
    readonly_fields = ('data_hora_movimentacao', 'movimentado_por',) 

    # Sobrescreve o método save_model para garantir que 'movimentado_por' seja o usuário logado
    def save_model(self, request, obj, form, change):
        # Se for um novo objeto (não está editando um existente) E o campo não foi preenchido
        if not obj.pk or not obj.movimentado_por: 
            obj.movimentado_por = request.user # Atribui o usuário logado
        super().save_model(request, obj, form, change)

    # Removemos o método get_form completamente, pois a lógica de initialização
    # e readonly_fields já cuida do que precisamos, e a atribuição final é no save_model.