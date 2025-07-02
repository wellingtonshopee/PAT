# pat/epi/forms.py

from django import forms
from django.forms import inlineformset_factory
from .models import TipoEPI, EPI, Colaborador, EntradaEPI, SaidaEPI

# --- Formulários para Adição/Edição ---

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
            'validade_ca': forms.DateInput(attrs={'type': 'date'}), # Input de data HTML5
        }
        help_texts = {
            'ca': 'Número do Certificado de Aprovação. Campo único e obrigatório.',
            'validade_ca': 'Data de vencimento do CA. Utilize o formato AAAA-MM-DD.',
            'ativo': 'Indica se o EPI está em uso ou desativado.',
        }

class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = [
            'nome_completo', 'matricula', 'cpf',
            'data_admissao', 'ativo'
        ]
        labels = {
            'nome_completo': 'Nome Completo',
            'matricula': 'Matrícula',
            'cpf': 'CPF',
            'data_admissao': 'Data de Admissão',
            'ativo': 'Ativo',
        }
        widgets = {
            'data_admissao': forms.DateInput(attrs={'type': 'date'}),
        }
        help_texts = {
            'cpf': 'Formato: XXX.XXX.XXX-XX',
            'ativo': 'Indica se o colaborador está ativo na empresa.',
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
        # Adicionado 'pdf_documento' aos campos do formulário
        fields = ['epi', 'colaborador', 'quantidade', 'observacoes', 'assinatura_digital', 'pdf_documento'] 
        labels = {
            'epi': 'EPI',
            'colaborador': 'Colaborador',
            'quantidade': 'Quantidade Entregue',
            'observacoes': 'Observações da Entrega',
            'assinatura_digital': 'Assinatura Digital', # Adicionado label para assinatura
            'pdf_documento': 'Documento PDF da Saída', # NOVO: Label para o campo PDF
        }
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }
        help_texts = {
            'quantidade': 'Quantidade de unidades de EPI sendo entregues.',
        }

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
                    field.widget.attrs['class'] = 'form-check-input mt-0' # Ajuste para alinhar com o label

class ColaboradorFilterForm(forms.Form):
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

class EntradaSaidaFilterForm(forms.Form): # Pode ser usado para filtrar entradas e saídas
    epi = forms.ModelChoiceField(
        queryset=EPI.objects.all().order_by('nome'),
        required=False,
        label='EPI',
        empty_label="Todos os EPIs"
    )
    colaborador = forms.ModelChoiceField(
        queryset=Colaborador.objects.all().order_by('nome_completo'),
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
