# C:\Users\SEAOps\Documents\pat\epi\admin.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Importa os modelos de EPI de .models (do próprio app epi)
from .models import EPI, TipoEPI, ColaboradorEPI, EntradaEPI, SaidaEPI

# IMPORTANTE: Importa os modelos de Absenteísmo do app 'rh'
# MANTENHA estas importações, pois elas são usadas nas raw_id_fields, etc.
from rh.models import TipoAbsenteismo, RegistroAbsenteismoDiario 


# 1. Defina o filtro customizado para 'CA Vencido'
class CAVencidoListFilter(admin.SimpleListFilter):
    title = _('Status do CA') # Título que aparece no filtro
    parameter_name = 'ca_vencido_status' # Parâmetro da URL para este filtro

    def lookups(self, request, model_admin):
        # Retorna uma tupla de tuplas: (valor_interno, título_exibido)
        return (
            ('vencido', _('Vencido')),
            ('nao_vencido', _('Não Vencido')),
            ('sem_validade', _('Sem Validade Informada')), # Nova opção para CAs sem data
        )

    def queryset(self, request, queryset):
        if self.value() == 'vencido':
            return queryset.filter(validade_ca__lt=timezone.now().date())
        if self.value() == 'nao_vencido':
            # Inclui CAs que ainda não venceram (validade_ca >= hoje)
            return queryset.filter(validade_ca__gte=timezone.now().date())
        if self.value() == 'sem_validade':
            # Inclui CAs onde a data de validade não foi informada
            return queryset.filter(validade_ca__isnull=True)
        return queryset # Retorna o queryset original se nenhum valor foi selecionado

# 2. Configure a classe Admin para o Modelo EPI
@admin.register(EPI)
class EPIAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 
        'ca', 
        'validade_ca', 
        'ca_vencido_display', # Vai exibir "Sim" ou "Não" na coluna
        'tipo_epi', 
        'estoque_atual', 
        'ativo'
    )
    list_filter = (
        'tipo_epi', 
        'ativo', 
        CAVencidoListFilter # <--- Adicione o filtro customizado aqui
    )
    search_fields = ('nome', 'ca', 'descricao', 'fabricante', 'modelo')
    list_per_page = 25

    # Método para exibir "Sim" ou "Não" na list_display
    def ca_vencido_display(self, obj):
        return "Sim" if obj.ca_vencido else "Não"
    ca_vencido_display.short_description = "CA Vencido?"
    ca_vencido_display.boolean = True # Para exibir um ícone de "check" ou "x"

# 3. Registre os outros modelos
@admin.register(TipoEPI)
class TipoEPIAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)

@admin.register(ColaboradorEPI)
class ColaboradorEPIAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'matricula', 'cpf', 'station_id', 'lider', 'cargo', 'ativo')
    list_filter = ('ativo', 'turno', 'tipo_contrato', 'lider', 'cargo')
    search_fields = ('nome_completo', 'matricula', 'cpf', 'station_id', 'codigo', 'bpo')
    # Estas raw_id_fields estão corretas porque ColaboradorEPI tem FKs para rh.models
    raw_id_fields = ('tipo_contrato', 'lider', 'cargo') 

@admin.register(EntradaEPI)
class EntradaEPIAdmin(admin.ModelAdmin):
    list_display = ('epi', 'quantidade', 'data_entrada')
    list_filter = ('epi', 'data_entrada')
    search_fields = ('epi__nome', 'epi__ca')
    raw_id_fields = ('epi',) # Use raw_id_fields para ForeignKey

@admin.register(SaidaEPI)
class SaidaEPIAdmin(admin.ModelAdmin):
    list_display = ('epi', 'colaborador', 'quantidade', 'data_saida')
    list_filter = ('epi', 'colaborador', 'data_saida')
    search_fields = ('epi__nome', 'epi__ca', 'colaborador__nome_completo', 'colaborador__matricula')
    raw_id_fields = ('epi', 'colaborador') # Use raw_id_fields para ForeignKey