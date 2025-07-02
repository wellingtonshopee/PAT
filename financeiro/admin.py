# C:\Users\SEAOps\Documents\pat\financeiro\admin.py

from django.contrib import admin
from .models import CategoriaFinanceira, FormaPagamento, ContaPagar, ContaReceber

# Registro simples dos modelos
admin.site.register(CategoriaFinanceira)
admin.site.register(FormaPagamento)
admin.site.register(ContaPagar) # Mantido o registro simples para ContaPagar por enquanto

# Registro para ContaReceber usando ModelAdmin
@admin.register(ContaReceber)
class ContaReceberAdmin(admin.ModelAdmin):
    list_display = (
        'descricao', # Alterado de numero_documento
        'cliente',
        'valor', # Alterado de valor_original
        'data_lancamento', # Alterado de data_emissao
        'data_vencimento',
        'data_recebimento',
        'status',
        'categoria',
        'forma_pagamento',
        'registrado_por',
        'data_registro', # Alterado de data_cadastro
    )
    list_filter = (
        'status',
        'categoria',
        'forma_pagamento',
        'data_lancamento', # Alterado de data_emissao
        'data_vencimento',
        'data_recebimento',
        'cliente',
        'registrado_por',
    )
    search_fields = (
        'descricao',
        'cliente__razao_social', # Permite buscar pelo nome do cliente
        'cliente__cnpj_cpf',
        'observacoes',
    )
    readonly_fields = (
        'data_registro', # Alterado de data_cadastro
        'data_ultima_atualizacao', # Alterado de data_atualizacao
    )
    
    fieldsets = (
        (None, {
            'fields': ('cliente', 'descricao', 'valor', 'categoria', 'forma_pagamento', 'status')
        }),
        ('Datas', {
            'fields': ('data_lancamento', 'data_vencimento', 'data_recebimento')
        }),
        ('Observações e Registro', {
            'fields': ('observacoes', 'registrado_por')
        }),
        ('Auditoria', {
            'fields': ('data_registro', 'data_ultima_atualizacao')
        }),
    )

    # O método get_form não é mais necessário para saldo_devedor, pois a propriedade foi removida.
    # Se o campo valor_recebido for adicionado novamente para pagamentos parciais,
    # e saldo_devedor for reintroduzido como propriedade, este método pode ser reavaliado.
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     if 'saldo_devedor' in form.base_fields:
    #         form.base_fields['saldo_devedor'].required = False
    #         form.base_fields['saldo_devedor'].widget.attrs['readonly'] = 'readonly'
    #     return form