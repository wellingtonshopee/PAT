from django.contrib import admin

# Register your models here.
# pat/epi/admin.py

from django.contrib import admin
from .models import TipoEPI, EPI, Colaborador, EntradaEPI, SaidaEPI

# Admin para TipoEPI
@admin.register(TipoEPI)
class TipoEPIAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)

# Admin para Colaborador
@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'matricula', 'cpf', 'data_admissao', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome_completo', 'matricula', 'cpf')
    list_editable = ('ativo',) # Permite editar o status 'ativo' diretamente na lista

# Admin para EPI
@admin.register(EPI)
class EPIAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 'ca', 'tipo_epi', 'validade_ca', 'fabricante',
        'estoque_minimo', 'estoque_atual', 'ca_vencido', 'ativo'
    )
    list_filter = ('tipo_epi', 'ativo', 'validade_ca')
    search_fields = ('nome', 'ca', 'descricao', 'fabricante', 'modelo')
    readonly_fields = ('estoque_atual', 'ca_vencido') # Estes são @properties, não editáveis
    fieldsets = (
        (None, {
            'fields': ('nome', 'ca', 'descricao', 'tipo_epi', 'ativo')
        }),
        ('Detalhes do Fabricante e Validade', {
            'fields': ('fabricante', 'modelo', 'validade_ca')
        }),
        ('Controle de Estoque', {
            'fields': ('estoque_minimo',)
        }),
    )

# Admin para EntradaEPI
@admin.register(EntradaEPI)
class EntradaEPIAdmin(admin.ModelAdmin):
    list_display = ('epi', 'quantidade', 'data_entrada', 'observacoes')
    list_filter = ('epi', 'data_entrada')
    search_fields = ('epi__nome', 'epi__ca', 'observacoes')
    readonly_fields = ('data_entrada',) # Data de entrada é auto_now_add

# Admin para SaidaEPI
@admin.register(SaidaEPI)
class SaidaEPIAdmin(admin.ModelAdmin):
    list_display = ('epi', 'colaborador', 'quantidade', 'data_saida', 'observacoes')
    list_filter = ('epi', 'colaborador', 'data_saida')
    search_fields = ('epi__nome', 'epi__ca', 'colaborador__nome_completo', 'colaborador__matricula', 'observacoes')
    readonly_fields = ('data_saida',) # Data de saída é auto_now_add