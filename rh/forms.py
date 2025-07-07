# C:\Users\SEAOps\Documents\pat\rh\forms.py

from django import forms
from .models import RegistroAbsenteismoDiario, TipoContrato, TipoAbsenteismo, Lider, Cargo
from epi.models import ColaboradorEPI # Importação Correta

# --- Formulário Principal para Registro de Absenteísmo (por Período) ---
# Este formulário é ideal para adicionar/editar um único registro de absenteísmo,
# que pode abranger um período (data_inicio a data_fim).
class RegistroAbsenteismoForm(forms.ModelForm):
    class Meta:
        # Usamos RegistroAbsenteismoDiario, pois é o modelo definido e importado.
        # Ele deve ter os campos 'data_inicio' e 'data_fim' para suportar períodos.
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
    
    # Campo 'colaborador' como ModelChoiceField visível.
    # Usado para selecionar o colaborador ao adicionar/editar um ÚNICO registro.
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
        empty_label="--- Não Ausente ---", # Opção para desmarcar o absenteísmo
        required=False, # Permite que o campo seja vazio, essencial para "desmarcar" um absenteísmo
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
        
        # Para um registro "diário", data_inicio e data_fim devem ser iguais.
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
        label="Tipo de Absenteísmo (Descrição)", # Melhorado o label para clareza
        required=False,
        empty_label="-- Todos os Tipos --",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # NOVO CAMPO DE FILTRO PARA SIGLA
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


# --- Outros Formulários (permanecem os mesmos) ---
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
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome do Líder',
        }


class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome do Cargo',
        }