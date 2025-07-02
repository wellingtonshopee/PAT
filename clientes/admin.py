# C:\Users\SEAOps\Documents\pat\clientes\admin.py

from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'razao_social',
        'cnpj_cpf',
        'data_nascimento', # NOVO: Adicionado à lista de exibição
        'email',
        'telefone',
        'cidade',          # NOVO: Adicionado à lista de exibição
        'estado',          # NOVO: Adicionado à lista de exibição
        'data_cadastro'
    )
    search_fields = (
        'razao_social',
        'cnpj_cpf',
        'email',
        'telefone', # Já estava, mas bom revisar
        'cep',      # NOVO: Adicionado aos campos de busca
        'cidade',   # NOVO: Adicionado aos campos de busca
        'estado'    # NOVO: Adicionado aos campos de busca
    )
    list_filter = (
        'data_cadastro',
        'data_nascimento', # NOVO: Adicionado ao filtro
        'estado',          # NOVO: Adicionado ao filtro
    )
    ordering = ('razao_social',)
    readonly_fields = ('data_cadastro',)

    # Opcional: Para organizar a visualização dos campos na página de detalhes/edição do cliente no admin
    fieldsets = (
        (None, {
            'fields': ('razao_social', 'nome_fantasia', 'cnpj_cpf', 'data_nascimento')
        }),
        ('Contato', {
            'fields': ('email', 'telefone')
        }),
        ('Endereço', {
            'fields': ('endereco', 'cep', 'cidade', 'estado')
        }),
        ('Informações Adicionais', {
            'fields': ('data_cadastro',)
        }),
    )