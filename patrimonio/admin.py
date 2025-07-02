# pat/patrimonio/admin.py

from django.contrib import admin
# Importe MovimentacaoPatrimonio junto com os outros modelos
from .models import CategoriaPatrimonio, LocalizacaoPatrimonio, ItemPatrimonio, MovimentacaoPatrimonio

# Classe Admin para CategoriaPatrimonio
@admin.register(CategoriaPatrimonio)
class CategoriaPatrimonioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',) # Campo de busca por nome
    list_filter = ('nome',) # Filtro lateral

# Classe Admin para LocalizacaoPatrimonio
@admin.register(LocalizacaoPatrimonio)
class LocalizacaoPatrimonioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',) # Campo de busca por nome
    list_filter = ('nome',) # Filtro lateral

# Classe Admin para ItemPatrimonio
@admin.register(ItemPatrimonio)
class ItemPatrimonioAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 'codigo_patrimonial', 'valor_aquisicao', 'data_aquisicao',
        'localizacao', 'categoria', 'responsavel_atual', 'estado_conservacao',
        'data_ultima_atualizacao'
    )
    list_filter = ('categoria', 'localizacao', 'estado_conservacao', 'responsavel_atual')
    search_fields = ('nome', 'codigo_patrimonial', 'numero_serie', 'descricao')
    date_hierarchy = 'data_aquisicao' # Permite navegar por data de aquisição
    raw_id_fields = ('responsavel_atual',) # Melhor para selecionar usuários em grande quantidade

    # Se você quiser preencher 'usuario_registro' automaticamente ao criar um ItemPatrimonio
    # no admin, você pode sobrescrever o método save_model
    def save_model(self, request, obj, form, change):
        if not obj.pk: # Apenas para novos objetos
            obj.usuario_registro = request.user
        super().save_model(request, obj, form, change)

# --- NOVO: Classe Admin para MovimentacaoPatrimonio ---
@admin.register(MovimentacaoPatrimonio)
class MovimentacaoPatrimonioAdmin(admin.ModelAdmin):
    list_display = (
        'item', 'tipo_movimentacao', 'data_movimentacao',
        'localizacao_origem', 'localizacao_destino',
        'responsavel_origem', 'responsavel_destino',
        'usuario_registro'
    )
    list_filter = (
        'tipo_movimentacao',
        'data_movimentacao',
        'localizacao_origem',
        'localizacao_destino',
        'responsavel_origem',
        'responsavel_destino',
        'usuario_registro'
    )
    search_fields = (
        'item__nome',
        'item__codigo_patrimonial',
        'observacoes',
        'localizacao_origem__nome', # Permite buscar pelo nome da localização de origem
        'localizacao_destino__nome', # Permite buscar pelo nome da localização de destino
        'responsavel_origem__first_name', 'responsavel_origem__last_name', 'responsavel_origem__username',
        'responsavel_destino__first_name', 'responsavel_destino__last_name', 'responsavel_destino__username',
    )
    date_hierarchy = 'data_movimentacao'
    # Use raw_id_fields para relacionamentos ForeignKey, melhora a performance em muitos registros
    raw_id_fields = (
        'item',
        'localizacao_origem',
        'localizacao_destino',
        'responsavel_origem',
        'responsavel_destino',
        'usuario_registro'
    )

    # Preenche automaticamente o campo usuario_registro com o usuário logado
    def save_model(self, request, obj, form, change):
        if not obj.pk: # Apenas para novos objetos (primeira criação)
            obj.usuario_registro = request.user
        super().save_model(request, obj, form, change)