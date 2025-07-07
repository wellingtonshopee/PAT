# C:\Users\SEAOps\Documents\pat\rh\admin.py
from django.contrib import admin
# Importe todos os modelos que você vai registrar ou referenciar aqui
from .models import Lider, Cargo, TipoContrato, TipoAbsenteismo, RegistroAbsenteismoDiario 

@admin.register(Lider)
class LiderAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(TipoContrato)
class TipoContratoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao',)
    search_fields = ('nome', 'descricao',)

@admin.register(TipoAbsenteismo)
class TipoAbsenteismoAdmin(admin.ModelAdmin):
    list_display = ('sigla', 'descricao', 'e_ausencia')
    list_filter = ('e_ausencia',)
    search_fields = ('sigla', 'descricao',)

@admin.register(RegistroAbsenteismoDiario)
class RegistroAbsenteismoDiarioAdmin(admin.ModelAdmin):
    list_display = (
        'colaborador', 
        'data_inicio', 
        'data_fim', 
        'tipo_absenteismo', 
        'total_dias', 
        'observacoes', 
    )
    list_filter = (
        'data_inicio', 
        'tipo_absenteismo', 
        'colaborador__bpo',         # Reativado
        'colaborador__tipo_contrato', # Reativado
    ) 
    search_fields = (
        'colaborador__nome_completo', 
        'colaborador__station_id', 
        'observacoes' 
    )
    autocomplete_fields = ['colaborador']