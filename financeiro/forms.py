# financeiro/forms.py

from django import forms
from django.utils import timezone # Adicionado para uso em initial date e clean methods
from django.contrib.auth import get_user_model # Adicionado para o queryset do campo cliente em ContaReceberFilterForm

# Importe seus modelos financeiros
from .models import CategoriaFinanceira, FormaPagamento, ContaPagar, ContaReceber

# Importe Fornecedor do seu app 'fornecedores'
from fornecedores.models import Fornecedor
from clientes.models import Cliente # Importe Cliente

User = get_user_model() # Para uso no queryset do campo cliente se necessário, mas para ContaReceber usaremos Cliente


# Formulário para Categorias Financeiras
class CategoriaFinanceiraForm(forms.ModelForm):
    class Meta:
        model = CategoriaFinanceira
        fields = ['nome', 'tipo', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Formulário para Formas de Pagamento
class FormaPagamentoForm(forms.ModelForm):
    class Meta:
        model = FormaPagamento
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Formulário para Contas a Pagar
class ContaPagarForm(forms.ModelForm):
    class Meta:
        model = ContaPagar
        fields = [
            'descricao', 'valor', 'data_lancamento', 'data_vencimento',
            'categoria', 'fornecedor', 'forma_pagamento', 'observacoes'
        ]
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'data_lancamento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_vencimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'fornecedor': forms.Select(attrs={'class': 'form-control'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = CategoriaFinanceira.objects.filter(tipo='DESPESA').order_by('nome')
        self.fields['fornecedor'].queryset = Fornecedor.objects.all().order_by('razao_social')
        self.fields['fornecedor'].label_from_instance = lambda obj: obj.razao_social
        self.fields['forma_pagamento'].queryset = FormaPagamento.objects.all().order_by('nome')

    def clean(self):
        cleaned_data = super().clean()
        data_vencimento = cleaned_data.get('data_vencimento')
        data_lancamento = cleaned_data.get('data_lancamento')

        if data_vencimento and data_lancamento and data_vencimento < data_lancamento:
            self.add_error('data_vencimento', "A data de vencimento não pode ser anterior à data de lançamento.")
        return cleaned_data

# Formulário para Baixa de Conta a Pagar
class BaixaContaPagarForm(forms.ModelForm):
    class Meta:
        model = ContaPagar
        fields = ['data_pagamento', 'forma_pagamento', 'observacoes']
        widgets = {
            'data_pagamento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_pagamento'].initial = timezone.localdate()
        self.fields['forma_pagamento'].queryset = FormaPagamento.objects.all().order_by('nome')


    def clean(self):
        cleaned_data = super().clean()
        data_pagamento = cleaned_data.get('data_pagamento')
        
        if data_pagamento and data_pagamento > timezone.localdate():
            self.add_error('data_pagamento', "A data de pagamento não pode ser futura.")
        return cleaned_data

# Formulário para Contas a Receber (Versão Consolidada)
class ContaReceberForm(forms.ModelForm):
    class Meta:
        model = ContaReceber
        fields = [
            'descricao', 'valor', 'data_lancamento', 'data_vencimento',
            'categoria', 'cliente', 'forma_pagamento', 'observacoes'
        ]
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'data_lancamento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_vencimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'descricao': 'Descrição da Receita',
            'valor': 'Valor a Receber',
            'data_lancamento': 'Data de Lançamento',
            'data_vencimento': 'Data de Vencimento',
            'categoria': 'Categoria da Receita',
            'forma_pagamento': 'Forma de Recebimento',
            'cliente': 'Cliente',
            'observacoes': 'Observações',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = CategoriaFinanceira.objects.filter(tipo='RECEITA').order_by('nome')
        self.fields['cliente'].queryset = Cliente.objects.all().order_by('razao_social')
        self.fields['cliente'].label_from_instance = lambda obj: obj.razao_social # Garante que o label exiba a razao_social
        self.fields['forma_pagamento'].queryset = FormaPagamento.objects.all().order_by('nome')

    def clean(self):
        cleaned_data = super().clean()
        data_vencimento = cleaned_data.get('data_vencimento')
        data_lancamento = cleaned_data.get('data_lancamento')

        if data_vencimento and data_lancamento and data_vencimento < data_lancamento:
            self.add_error('data_vencimento', "A data de vencimento não pode ser anterior à data de lançamento.")
        return cleaned_data

# Formulário para Baixa de Conta a Receber
class BaixaContaReceberForm(forms.ModelForm):
    class Meta:
        model = ContaReceber
        fields = ['data_recebimento', 'forma_pagamento', 'observacoes']
        widgets = {
            'data_recebimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'data_recebimento': 'Data do Recebimento',
            'forma_pagamento': 'Forma de Recebimento Realizada',
            'observacoes': 'Observações da Baixa',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['forma_pagamento'].queryset = FormaPagamento.objects.all().order_by('nome')
        self.fields['data_recebimento'].initial = timezone.localdate()
        self.fields['data_recebimento'].required = True

    def clean(self):
        cleaned_data = super().clean()
        data_recebimento = cleaned_data.get('data_recebimento')
        
        if data_recebimento and data_recebimento > timezone.localdate():
            self.add_error('data_recebimento', "A data de recebimento não pode ser futura.")
        return cleaned_data

# Formulário de Filtro para Contas a Pagar
class ContaPagarFilterForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        label="Buscar",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição, Fornecedor...'})
    )
    status = forms.ChoiceField(
        choices=[('', 'Todos')] + ContaPagar.STATUS_CHOICES,
        required=False,
        label="Status",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    categoria = forms.ModelChoiceField(
        queryset=CategoriaFinanceira.objects.filter(tipo='DESPESA'),
        required=False,
        label="Categoria",
        empty_label="Todas as Categorias",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    fornecedor = forms.ModelChoiceField(
        queryset=Fornecedor.objects.all(),
        required=False,
        label="Fornecedor",
        empty_label="Todos os Fornecedores",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    data_vencimento_inicio = forms.DateField(
        required=False,
        label="Vencimento De",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    data_vencimento_fim = forms.DateField(
        required=False,
        label="Vencimento Até",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    data_pagamento_inicio = forms.DateField(
        required=False,
        label="Pagamento De",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    data_pagamento_fim = forms.DateField(
        required=False,
        label="Pagamento Até",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # O loop abaixo não é mais estritamente necessário se todos os widgets já têm 'form-control'
        # mas pode ser útil como fallback ou para campos adicionados dinamicamente.
        # Mantendo para consistência com seu código original.
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.Select, forms.DateInput, forms.NumberInput)):
                field.widget.attrs.setdefault('class', 'form-control') # Usa setdefault para não sobrescrever se já existir

# Formulário de Filtro para Contas a Receber
class ContaReceberFilterForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        label="Buscar",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição, Cliente...'})
    )
    status = forms.ChoiceField(
        choices=[('', 'Todos')] + ContaReceber.STATUS_CHOICES,
        required=False,
        label="Status",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    categoria = forms.ModelChoiceField(
        queryset=CategoriaFinanceira.objects.filter(tipo='RECEITA'),
        required=False,
        label="Categoria",
        empty_label="Todas as Categorias",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cliente = forms.ModelChoiceField( # CORRIGIDO: Agora aponta para o modelo Cliente
        queryset=Cliente.objects.all().order_by('razao_social'), # Use Cliente.objects.all()
        required=False,
        label="Cliente",
        empty_label="Todos os Clientes",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    data_vencimento_inicio = forms.DateField(
        required=False,
        label="Vencimento De",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    data_vencimento_fim = forms.DateField(
        required=False,
        label="Vencimento Até",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    data_recebimento_inicio = forms.DateField(
        required=False,
        label="Recebimento De",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    data_recebimento_fim = forms.DateField(
        required=False,
        label="Recebimento Até",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.Select, forms.DateInput, forms.NumberInput)):
                field.widget.attrs.setdefault('class', 'form-control')

# NOVO: Formulário de Filtro para o Relatório Financeiro
class RelatorioFinanceiroFilterForm(forms.Form):
    data_inicio = forms.DateField(
        label="Data Início (Vencimento/Pagamento/Recebimento)",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    data_fim = forms.DateField(
        label="Data Fim (Vencimento/Pagamento/Recebimento)",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    
    TIPO_CONTA_CHOICES = [
        ('', 'Todos os Tipos'),
        ('pagar', 'Contas a Pagar'),
        ('receber', 'Contas a Receber'),
    ]
    tipo_conta = forms.ChoiceField(
        label="Tipo de Conta",
        choices=TIPO_CONTA_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    categoria = forms.ModelChoiceField(
        queryset=CategoriaFinanceira.objects.all().order_by('nome'),
        label="Categoria",
        required=False,
        empty_label="Todas as Categorias",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    
    # Status podem ser mais genéricos ou específicos, dependendo da necessidade
    STATUS_GERAL_CHOICES = [
        ('', 'Todos os Status'),
        ('pendente', 'Pendente'),
        ('realizado', 'Pago/Recebido'), # Unificado
        ('cancelado', 'Cancelado'),
        ('vencida', 'Vencida'), # Adicionado para flexibilidade
    ]
    status_geral = forms.ChoiceField(
        choices=STATUS_GERAL_CHOICES,
        label="Status Geral",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    
    fornecedor = forms.ModelChoiceField(
        queryset=Fornecedor.objects.all().order_by('razao_social'),
        label="Fornecedor",
        required=False,
        empty_label="Todos os Fornecedores",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all().order_by('razao_social'),
        label="Cliente",
        required=False,
        empty_label="Todos os Clientes",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    search_query = forms.CharField(
        label="Buscar (Descrição ou Observações)",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Termo de busca', 'class': 'form-control'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Garante que todos os campos recebam a classe 'form-control' ou 'form-select'
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.DateInput, forms.NumberInput)):
                field.widget.attrs.setdefault('class', 'form-control')
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-select')