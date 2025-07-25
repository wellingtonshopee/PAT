# rh/forms.py

from django import forms
from django.forms import inlineformset_factory 

# Importa todos os modelos de rh
from .models import (
    RegistroAbsenteismoDiario, TipoContrato, TipoAbsenteismo, Lider, Cargo,
    Treinamento, TurmaTreinamento, ParticipacaoTurma 
)
# Importa ColaboradorEPI do app 'epi'
from epi.models import ColaboradorEPI 

# ==============================================================================
# Formulários de RH (Absenteísmo e Gerais) - Ajustados pelo Usuário
# ==============================================================================

# --- Formulário Principal para Registro de Absenteísmo (por Período) ---
class RegistroAbsenteismoForm(forms.ModelForm):
    class Meta:
        model = RegistroAbsenteismoDiario
        fields = ['colaborador', 'data_inicio', 'data_fim', 'tipo_absenteismo', 'justificativa', 'atestado_medico', 'observacoes']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Detalhes ou motivo do absenteísmo'}),
            'justificativa': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Justificativa do absenteísmo'}),
            'atestado_medico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tipo_absenteismo': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'colaborador': 'Colaborador',
            'data_inicio': 'Data de Início',
            'data_fim': 'Data de Fim',
            'tipo_absenteismo': 'Tipo de Absenteísmo',
            'justificativa': 'Justificativa',
            'atestado_medico': 'Possui Atestado Médico?',
            'observacoes': 'Observações',
        }
    
    colaborador = forms.ModelChoiceField(
        queryset=ColaboradorEPI.objects.all().order_by('nome_completo'),
        label="Colaborador",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')

        if data_inicio and data_fim and data_fim < data_inicio:
            self.add_error('data_fim', "A data final não pode ser anterior à data de início.")
        return cleaned_data


# --- Formulário para Marcação de Absenteísmo Diário (usado no Formset) ---
class RegistroAbsenteismoDiarioForm(forms.ModelForm):
    class Meta:
        model = RegistroAbsenteismoDiario 
        fields = ['colaborador', 'data_inicio', 'data_fim', 'tipo_absenteismo', 'observacoes'] 
        widgets = {
            'colaborador': forms.HiddenInput(), 
            'data_inicio': forms.HiddenInput(), 
            'data_fim': forms.HiddenInput(), 
            'tipo_absenteismo': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'observacoes': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Observações (opcional)'}),
        }
        labels = {
            'tipo_absenteismo': 'Tipo',
            'observacoes': 'Obs.',
        }

    tipo_absenteismo = forms.ModelChoiceField(
        queryset=TipoAbsenteismo.objects.all().order_by('descricao'),
        empty_label="--- Não Ausente ---",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )

    def clean_tipo_absenteismo(self):
        tipo = self.cleaned_data.get('tipo_absenteismo')
        return tipo

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        colaborador = cleaned_data.get('colaborador')
        
        if data_inicio and data_fim and data_fim != data_inicio:
            self.add_error('data_fim', "Para registros diários, a data de início e fim devem ser iguais.")
        
        if not colaborador:
            self.add_error('colaborador', "Colaborador é obrigatório.")
            
        return cleaned_data


# --- Formulário para Filtrar o Relatório de Absenteísmo ---
class RelatorioAbsenteismoFilterForm(forms.Form):
    """
    Formulário para filtrar o relatório de absenteísmo (para exibição e exportação).
    """
    data_inicio = forms.DateField(
        label="Data Início",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    data_fim = forms.DateField(
        label="Data Fim",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    colaborador = forms.ModelChoiceField(
        queryset=ColaboradorEPI.objects.all().order_by('nome_completo'),
        label="Colaborador",
        required=False,
        empty_label="-- Todos os Colaboradores --",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tipo_contrato = forms.ModelChoiceField(
        queryset=TipoContrato.objects.all().order_by('nome'),
        label="Tipo de Contrato",
        required=False,
        empty_label="-- Todos os Tipos de Contrato --",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tipo_absenteismo = forms.ModelChoiceField(
        queryset=TipoAbsenteismo.objects.all().order_by('descricao'),
        label="Tipo de Absenteísmo (Descrição)",
        required=False,
        empty_label="-- Todos os Tipos --",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    sigla_absenteismo = forms.CharField( 
        label="Sigla Absenteísmo",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: AM, FER'})
    )
    cargo = forms.ModelChoiceField(
        queryset=Cargo.objects.all().order_by('nome'),
        label="Cargo",
        required=False,
        empty_label="-- Todos os Cargos --",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    observacoes = forms.CharField(
        label="Observações (contém)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pesquisar em observações'})
    )


# --- Outros Formulários Gerais ---
class TipoContratoForm(forms.ModelForm):
    class Meta:
        model = TipoContrato
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome do Tipo de Contrato',
            'descricao': 'Descrição',
        }

class TipoAbsenteismoForm(forms.ModelForm):
    class Meta:
        model = TipoAbsenteismo
        fields = ['sigla', 'descricao', 'e_ausencia']
        widgets = {
            'sigla': forms.TextInput(attrs={'placeholder': 'Ex: AM, FER', 'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'placeholder': 'Ex: Atestado Médico, Férias', 'class': 'form-control'}),
            'e_ausencia': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'sigla': 'Sigla',
            'descricao': 'Descrição Completa',
            'e_ausencia': 'Conta como Ausência?',
        }


class LiderForm(forms.ModelForm):
    class Meta:
        model = Lider
        fields = ['nome', 'matricula'] 
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome do Líder',
            'matricula': 'Matrícula',
        }


class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ['nome', 'descricao'] 
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome do Cargo',
            'descricao': 'Descrição',
        }


# --- Formulários para Modelos de Treinamento ---
class TreinamentoForm(forms.ModelForm):
    class Meta:
        model = Treinamento
        fields = ['nome', 'descricao', 'carga_horaria', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'carga_horaria': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nome': 'Nome do Treinamento',
            'descricao': 'Descrição',
            'carga_horaria': 'Carga Horária (horas)',
            'ativo': 'Ativo',
        }

class TurmaTreinamentoForm(forms.ModelForm):
    # NOVO CAMPO: Para selecionar múltiplos colaboradores
    participantes_selecionados = forms.ModelMultipleChoiceField(
        queryset=ColaboradorEPI.objects.all().order_by('nome_completo'),
        label="Selecionar Participantes",
        required=False, # Pode ser True se a turma sempre exigir participantes
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '10'}) # size para mostrar mais opções
    )

    class Meta:
        model = TurmaTreinamento
        fields = ['treinamento', 'data_realizacao', 'horario_inicio', 'horario_fim', 'local', 'instrutor', 'observacoes']
        widgets = {
            'treinamento': forms.Select(attrs={'class': 'form-select'}),
            'data_realizacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'horario_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'horario_fim': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'local': forms.TextInput(attrs={'class': 'form-control'}),
            'instrutor': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'treinamento': 'Treinamento',
            'data_realizacao': 'Data de Realização',
            'horario_inicio': 'Horário de Início',
            'horario_fim': 'Horário de Fim',
            'local': 'Local',
            'instrutor': 'Instrutor',
            'observacoes': 'Observações da Turma',
        }

class ParticipacaoTurmaForm(forms.ModelForm):
    # Sobrescreve o campo 'colaborador' para usar ModelChoiceField com ColaboradorEPI
    colaborador = forms.ModelChoiceField(
        queryset=ColaboradorEPI.objects.all().order_by('nome_completo'), # Garante ordenação
        label="Colaborador",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = ParticipacaoTurma
        fields = [
            'colaborador',
            'status',
            'nota_avaliacao',
            'certificado_emitido',
            'data_emissao_certificado',
            'observacoes',
        ]
        labels = {
            'colaborador': 'Colaborador',
            'status': 'Status da Participação',
            'nota_avaliacao': 'Nota da Avaliação',
            'certificado_emitido': 'Certificado Emitido',
            'data_emissao_certificado': 'Data de Emissão do Certificado',
            'observacoes': 'Observações',
        }
        widgets = {
            'data_emissao_certificado': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'nota_avaliacao': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}), 
            'certificado_emitido': forms.CheckboxInput(attrs={'class': 'form-check-input'}), 
        }

# REMOVIDO: ParticipacaoTurmaFormSet não será mais usado para seleção múltipla
# ParticipacaoTurmaFormSet = inlineformset_factory(
#     TurmaTreinamento,
#     ParticipacaoTurma,
#     form=ParticipacaoTurmaForm, 
#     fields='__all__',
#     extra=1,
#     can_delete=True,
#     min_num=0,
#     max_num=999,
#     validate_max=False,
# )
