from django.contrib import admin
from django.utils.translation import gettext_lazy as _ # Importado para o caso de usar lazy translation
from django.utils import timezone # Importado para o campo de data de emissão de certificado

# Importe todos os modelos que você vai registrar ou referenciar aqui
from .models import (
    Lider, Cargo, TipoContrato,
    TipoAbsenteismo, RegistroAbsenteismoDiario,
    Treinamento, TurmaTreinamento, ParticipacaoTurma # Novos modelos de treinamento
)
from epi.models import ColaboradorEPI # Importar ColaboradorEPI para usar no autocomplete_fields e inlines

# ==============================================================================
# Registros para Modelos de RH (Absenteísmo) - Ajustados pelo Usuário
# ==============================================================================

@admin.register(Lider)
class LiderAdmin(admin.ModelAdmin):
    list_display = ('nome', 'matricula') # Adicionado 'matricula' conforme models.py
    search_fields = ('nome', 'matricula')

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao') # Adicionado 'descricao' conforme models.py
    search_fields = ('nome', 'descricao')

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
        'colaborador__bpo', 
        'colaborador__tipo_contrato',
    ) 
    search_fields = (
        'colaborador__nome_completo', 
        'colaborador__station_id', 
        'observacoes', 
        'justificativa', # Adicionado para melhor busca
    )
    autocomplete_fields = ['colaborador']
    # Adicionado raw_id_fields se houver muitos registros para tipo_absenteismo
    # raw_id_fields = ('tipo_absenteismo',) 
    readonly_fields = ('data_registro',) # Garante que a data de registro não seja alterada manualmente


# ==============================================================================
# NOVOS REGISTROS PARA TREINAMENTO (conforme definido anteriormente)
# ==============================================================================

@admin.register(Treinamento)
class TreinamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'carga_horaria', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'descricao')
    ordering = ('nome',)
    fieldsets = (
        (None, {
            'fields': ('nome', 'descricao', 'carga_horaria', 'ativo')
        }),
    )

class ParticipacaoTurmaInline(admin.TabularInline):
    """
    Permite adicionar/editar participantes diretamente na tela da Turma de Treinamento.
    """
    model = ParticipacaoTurma
    extra = 1 # Quantidade de linhas vazias para adicionar novos participantes
    # Use autocomplete_fields em vez de raw_id_fields para ColaboradorEPI para melhor UX
    autocomplete_fields = ('colaborador',)
    fields = ('colaborador', 'status', 'nota_avaliacao', 'certificado_emitido', 'data_emissao_certificado', 'observacoes')

@admin.register(TurmaTreinamento)
class TurmaTreinamentoAdmin(admin.ModelAdmin):
    list_display = (
        'treinamento', 'data_realizacao', 'instrutor', 'local',
        'quantidade_participantes', # Método customizado para exibir contagem
    )
    list_filter = ('treinamento', 'data_realizacao', 'instrutor', 'local')
    search_fields = (
        'treinamento__nome', 'instrutor', 'local', 'observacoes'
    )
    date_hierarchy = 'data_realizacao'
    ordering = ('-data_realizacao', 'treinamento__nome')
    autocomplete_fields = ('treinamento',) # Use autocomplete_fields para Treinamento
    inlines = [ParticipacaoTurmaInline] # Adiciona a edição de participantes aqui

    # Método para contar participantes diretamente na listagem
    def quantidade_participantes(self, obj):
        return obj.participantes.count()
    quantidade_participantes.short_description = "Nº Participantes"

@admin.register(ParticipacaoTurma)
class ParticipacaoTurmaAdmin(admin.ModelAdmin):
    list_display = (
        'colaborador', 'turma', 'status', 'certificado_emitido', 'data_emissao_certificado'
    )
    list_filter = ('status', 'certificado_emitido', 'turma__treinamento', 'turma__data_realizacao')
    search_fields = (
        'colaborador__nome_completo', 'colaborador__matricula',
        'turma__treinamento__nome', 'turma__instrutor'
    )
    # Use autocomplete_fields para melhorar a seleção de colaborador e turma
    autocomplete_fields = ('colaborador', 'turma')
    date_hierarchy = 'data_registro_participacao'
    ordering = ('-turma__data_realizacao', 'colaborador__nome_completo')
    
    # Campo para auto-preenchimento da data de emissão do certificado
    def save_model(self, request, obj, form, change):
        if obj.certificado_emitido and not obj.data_emissao_certificado:
            obj.data_emissao_certificado = timezone.now().date()
        super().save_model(request, obj, form, change)