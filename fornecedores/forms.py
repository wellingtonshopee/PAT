# pat/fornecedores/forms.py

from django import forms
from .models import Fornecedor, TipoFornecedor

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        # Lista explícita dos campos que queremos no formulário
        fields = [
            'nome_fantasia', 'razao_social', 'cnpj_cpf', 'contato_principal',
            'telefone', 'email', 'endereco', 'tipo_fornecedor',
            'observacoes', 'ativo'
        ]
        # Campos que o Django gerencia automaticamente e não devem estar no formulário
        exclude = ['data_cadastro', 'data_ultima_atualizacao']

        labels = {
            'nome_fantasia': 'Nome Fantasia',
            'razao_social': 'Razão Social',
            'cnpj_cpf': 'CNPJ/CPF',
            'contato_principal': 'Contato Principal',
            'telefone': 'Telefone',
            'email': 'E-mail',
            'endereco': 'Endereço Completo',
            'tipo_fornecedor': 'Tipo de Fornecedor',
            'observacoes': 'Observações',
            'ativo': 'Ativo',
        }
        help_texts = {
            'cnpj_cpf': 'Formato: XX.XXX.XXX/XXXX-XX ou XXX.XXX.XXX-XX',
            'ativo': 'Marque se o fornecedor está ativo e em uso.',
        }
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 4}), # Ajusta o tamanho da área de texto
            'endereco': forms.Textarea(attrs={'rows': 3}), # Ajusta o tamanho da área de texto
        }

    # Opcional: Adicionar um campo de confirmação de e-mail ou validação de telefone/CNPJ-CPF
    # def clean_cnpj_cpf(self):
    #     cnpj_cpf = self.cleaned_data['cnpj_cpf']
    #     # Remover caracteres não numéricos para validação interna, se precisar
    #     # Limpar antes de retornar, se quiser salvar apenas números no banco (modelo precisa ser ajustado)
    #     # Ex: cnpj_cpf_numerico = ''.join(filter(str.isdigit, cnpj_cpf))
    #     return cnpj_cpf

class FornecedorFilterForm(forms.Form):
    # Campos de filtro
    search_query = forms.CharField(
        max_length=200,
        required=False,
        label='Pesquisar',
        help_text='Nome, Razão Social, CNPJ/CPF ou Contato',
        widget=forms.TextInput(attrs={'placeholder': 'Pesquisar fornecedor...'})
    )

    tipo_fornecedor = forms.ModelChoiceField(
        queryset=TipoFornecedor.objects.all().order_by('nome'), # Lista os tipos de fornecedor
        required=False,
        label='Tipo de Fornecedor',
        empty_label="Todos os Tipos" # Opção para selecionar todos
    )

    ativo = forms.ChoiceField(
        choices=[('', 'Todos'), ('True', 'Ativo'), ('False', 'Inativo')], # Opções para o status ativo
        required=False,
        label='Status'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes CSS do Bootstrap para styling automático
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput) or isinstance(field.widget, forms.Select) or isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input' # Classe para checkboxes
                if field_name == 'ativo': # Ajuste para checkboxes para ficar mais legível no layout
                    field.widget.attrs['class'] = 'form-check-input mt-0' # Bootstrap 5 ajusta margem