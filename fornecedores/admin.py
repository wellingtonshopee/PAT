# pat/fornecedores/admin.py

from django.contrib import admin
from .models import TipoFornecedor, Fornecedor

# Classe Admin para TipoFornecedor
@admin.register(TipoFornecedor)
class TipoFornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)
    list_filter = ('nome',)

# Classe Admin para Fornecedor
@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = (
        'nome_fantasia', 'razao_social', 'cnpj_cpf', 'telefone',
        'email', 'tipo_fornecedor', 'ativo', 'data_cadastro'
    )
    list_filter = ('tipo_fornecedor', 'ativo')
    search_fields = (
        'nome_fantasia', 'razao_social', 'cnpj_cpf', 'contato_principal',
        'email', 'telefone', 'endereco'
    )
    # Campos que aparecem nos detalhes do fornecedor, agrupados
    fieldsets = (
        (None, {
            'fields': ('nome_fantasia', 'razao_social', 'cnpj_cpf', 'ativo')
        }),
        ('Informações de Contato', {
            'fields': ('contato_principal', 'telefone', 'email', 'endereco')
        }),
        ('Classificação e Observações', {
            'fields': ('tipo_fornecedor', 'observacoes')
        }),
    )
    readonly_fields = ('data_cadastro', 'data_ultima_atualizacao') # Não podem ser editados manualmente