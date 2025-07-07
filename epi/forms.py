# pat/epi/forms.py

from django import forms
from django.forms import inlineformset_factory, BaseFormSet 

# Importar apenas os modelos que são DESTE APP (EPI)
from .models import TipoEPI, EPI, EntradaEPI, SaidaEPI, ColaboradorEPI 

# IMPORTANTE: Importar os modelos de Absenteísmo do app 'rh'
from rh.models import TipoAbsenteismo, RegistroAbsenteismoDiario # Ajustado para importar de rh.models

# --- Formulários para Adição/Edição de EPIs ---

class TipoEPIForm(forms.ModelForm):
    class Meta:
        model = TipoEPI
        fields = ['nome', 'descricao']
        labels = {
            'nome': 'Nome do Tipo de EPI',
            'descricao': 'Descrição',
        }

class EPIForm(forms.ModelForm):
    class Meta:
        model = EPI
        fields = [
            'nome', 'ca', 'descricao', 'tipo_epi',
            'validade_ca', 'fabricante', 'modelo',
            'estoque_minimo', 'ativo'
        ]
        labels = {
            'nome': 'Nome do EPI',
            'ca': 'CA (Certificado de Aprovação)',
            'descricao': 'Descrição Detalhada',
            'tipo_epi': 'Tipo de EPI',
            'validade_ca': 'Validade do CA',
            'fabricante': 'Fabricante',
            'modelo': 'Modelo',
            'estoque_minimo': 'Estoque Mínimo',
            'ativo': 'Ativo',
        }
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'validade_ca': forms.DateInput(attrs={'type': 'date'}), 
        }
        help_texts = {
            'ca': 'Número do Certificado de Aprovação. Campo único e obrigatório.',
            'validade_ca': 'Data de vencimento do CA. Utilize o formato AAAA-MM-DD.',
            'ativo': 'Indica se o EPI está em uso ou desativado.',
        }

class EntradaEPIForm(forms.ModelForm):
    class Meta:
        model = EntradaEPI
        fields = ['epi', 'quantidade', 'observacoes']
        labels = {
            'epi': 'EPI',
            'quantidade': 'Quantidade',
            'observacoes': 'Observações',
        }
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }
        help_texts = {
            'quantidade': 'Quantidade de unidades de EPI que estão entrando no estoque.',
        }

class SaidaEPIForm(forms.ModelForm):
    class Meta:
        model = SaidaEPI
        # Note que 'colaborador' aqui se refere ao ForeignKey que aponta para ColaboradorEPI
        fields = ['epi', 'colaborador', 'quantidade', 'observacoes', 'assinatura_digital', 'pdf_documento'] 
        labels = {
            'epi': 'EPI',
            'colaborador': 'Colaborador',
            'quantidade': 'Quantidade Entregue',
            'observacoes': 'Observações da Entrega',
            'assinatura_digital': 'Assinatura Digital',
            'pdf_documento': 'Documento PDF da Saída',
        }
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }
        help_texts = {
            'quantidade': 'Quantidade de unidades de EPI sendo entregues.',
        }

# --- Formulários de Absenteísmo (AGORA USANDO MODELOS DE RH) ---
class TipoAbsenteismoForm(forms.ModelForm):
    class Meta:
        model = TipoAbsenteismo # Importado de rh.models
        fields = ['descricao', 'sigla']
        labels = {
            'descricao': 'Descrição do Tipo de Absenteísmo',
            'sigla': 'Sigla',
        }

class RegistroAbsenteismoForm(forms.ModelForm):
    class Meta:
        model = RegistroAbsenteismoDiario # Importado de rh.models, ajustado o nome
        # Note que 'colaborador' aqui se refere ao ForeignKey que aponta para ColaboradorEPI
        fields = ['colaborador', 'tipo_absenteismo', 'data_inicio', 'data_fim', 'observacoes']
        labels = {
            'colaborador': 'Colaborador',
            'tipo_absenteismo': 'Tipo de Absenteísmo',
            'data_inicio': 'Data Início',
            'data_fim': 'Data Fim',
            'observacoes': 'Observações',
        }
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }
        input_formats = {
            'data_inicio': ['%Y-%m-%d'],
            'data_fim': ['%Y-%m-%d'],
        }

# --- Formulários para Marcação Diária de Absenteísmo ---

class RegistroDiarioAbsenteismoIndividualForm(forms.ModelForm):
    """
    Formulário para um único registro de absenteísmo na tela de marcação diária.
    Não inclui campos de data, pois a data será definida para todos no formset.
    """
    class Meta:
        model = RegistroAbsenteismoDiario # Importado de rh.models, ajustado o nome
        fields = ['colaborador', 'tipo_absenteismo'] 
        widgets = {
            'colaborador': forms.HiddenInput(), # Colaborador é preenchido automaticamente
            'tipo_absenteismo': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }
        labels = {
            'tipo_absenteismo': 'Status',
        }

# Formset para a marcação diária de múltiplos colaboradores
RegistroDiarioAbsenteismoFormSet = forms.modelformset_factory(
    RegistroAbsenteismoDiario, # Importado de rh.models, ajustado o nome
    form=RegistroDiarioAbsenteismoIndividualForm,
    fields=['colaborador', 'tipo_absenteismo'],
    extra=0, 
    can_delete=False 
)


# --- Formulários para o modelo ColaboradorEPI (originalmente Colaborador) ---
# Agora eles pertencem e se referem especificamente ao ColaboradorEPI dentro do app 'epi'

class ColaboradorEPIForm(forms.ModelForm):
    class Meta:
        model = ColaboradorEPI # <--- Aponta para o modelo RENOMEADO
        fields = [
            'nome_completo', 'matricula', 'cpf',
            'station_id', 'codigo', 'bpo',
            'tipo_contrato', 'lider', 'cargo', # Estes são ForeignKeys para modelos de RH
            'turno',
            'data_admissao', 'data_desligamento', 'foto', 'ativo' 
        ]
        labels = {
            'nome_completo': 'Nome Completo',
            'matricula': 'Matrícula',
            'cpf': 'CPF',
            'station_id': 'Station ID',
            'codigo': 'Código do Colaborador',
            'bpo': 'BPO',
            'tipo_contrato': 'Tipo de Contrato', 
            'lider': 'Líder', 
            'cargo': 'Cargo', 
            'turno': 'Turno',
            'data_admissao': 'Data de Admissão',
            'data_desligamento': 'Data de Desligamento', 
            'foto': 'Foto do Colaborador', 
            'ativo': 'Ativo',
        }
        widgets = {
            'data_admissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'data_desligamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'), 
            'tipo_contrato': forms.Select(attrs={'class': 'form-select'}),
            'lider': forms.Select(attrs={'class': 'form-select'}),
            'cargo': forms.Select(attrs={'class': 'form-select'}),
            'turno': forms.Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'cpf': 'Formato: XXX.XXX.XXX-XX',
            'station_id': 'ID da Estação de Trabalho do Colaborador.',
            'codigo': 'Código interno de identificação do colaborador.',
            'bpo': 'Business Process Outsourcing (ex: fornecedor do serviço).',
            'ativo': 'Indica se o colaborador está ativo na empresa.',
        }
        input_formats = {
            'data_admissao': ['%Y-%m-%d'],
            'data_desligamento': ['%Y-%m-%d'],
        }

class ColaboradorEPIFilterForm(forms.Form): # <--- RENOMEADO
    search_query = forms.CharField(
        max_length=200,
        required=False,
        label='Pesquisar Colaborador',
        help_text='Nome, Matrícula ou CPF',
        widget=forms.TextInput(attrs={'placeholder': 'Pesquisar colaborador...'})
    )
    ativo = forms.ChoiceField(
        choices=[('', 'Todos'), ('True', 'Ativo'), ('False', 'Inativo')],
        required=False,
        label='Status do Colaborador'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Select, forms.Textarea)):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
                if field_name == 'ativo':
                    field.widget.attrs['class'] = 'form-check-input mt-0'

# --- Formulários de Filtro ---

class EPIFilterForm(forms.Form):
    search_query = forms.CharField(
        max_length=200,
        required=False,
        label='Pesquisar EPI',
        help_text='Nome, CA, Fabricante ou Modelo',
        widget=forms.TextInput(attrs={'placeholder': 'Pesquisar EPI...'})
    )
    tipo_epi = forms.ModelChoiceField(
        queryset=TipoEPI.objects.all().order_by('nome'),
        required=False,
        label='Tipo de EPI',
        empty_label="Todos os Tipos"
    )
    ca_vencido = forms.ChoiceField(
        choices=[('', 'Todos'), ('True', 'Vencido'), ('False', 'Não Vencido')],
        required=False,
        label='CA Vencido'
    )
    ativo = forms.ChoiceField(
        choices=[('', 'Todos'), ('True', 'Ativo'), ('False', 'Inativo')],
        required=False,
        label='Status do EPI'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Select, forms.Textarea)):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
                if field_name == 'ativo':
                    field.widget.attrs['class'] = 'form-check-input mt-0'


class EntradaSaidaFilterForm(forms.Form):
    epi = forms.ModelChoiceField(
        queryset=EPI.objects.all().order_by('nome'),
        required=False,
        label='EPI',
        empty_label="Todos os EPIs"
    )
    # Este filtro aponta para ColaboradorEPI
    colaborador = forms.ModelChoiceField(
        queryset=ColaboradorEPI.objects.all().order_by('nome_completo'), # <--- Aponta para ColaboradorEPI
        required=False,
        label='Colaborador (apenas Saídas)',
        empty_label="Todos os Colaboradores"
    )
    data_inicio = forms.DateField(
        required=False,
        label='Data Início',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    data_fim = forms.DateField(
        required=False,
        label='Data Fim',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Select, forms.DateInput)):
                field.widget.attrs['class'] = 'form-control'