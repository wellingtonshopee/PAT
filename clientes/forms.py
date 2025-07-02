# C:\Users\SEAOps\Documents\pat\clientes\forms.py

from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'razao_social',
            'nome_fantasia',
            'cnpj_cpf',
            'data_nascimento', # NOVO CAMPO ADICIONADO AQUI
            'email',
            'telefone',
            'endereco',
            'cep',             # NOVO CAMPO ADICIONADO AQUI
            'cidade',          # NOVO CAMPO ADICIONADO AQUI
            'estado',          # NOVO CAMPO ADICIONADO AQUI
        ]
        widgets = {
            'razao_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Razão Social ou Nome Completo'}),
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome Fantasia (Opcional)'}),
            'cnpj_cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CNPJ ou CPF'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), # NOVO WIDGET
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemplo@email.com'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXXX-XXXX'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Endereço Completo'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 12345-678'}), # NOVO WIDGET
            'cidade': forms.TextInput(attrs={'class': 'form-control'}), # NOVO WIDGET
            'estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 2, 'placeholder': 'UF'}), # NOVO WIDGET
        }
        labels = {
            'razao_social': 'Razão Social / Nome Completo',
            'nome_fantasia': 'Nome Fantasia',
            'cnpj_cpf': 'CNPJ/CPF',
            'data_nascimento': 'Data de Nascimento', # NOVO LABEL
            'email': 'E-mail',
            'telefone': 'Telefone',
            'endereco': 'Endereço',
            'cep': 'CEP',             # NOVO LABEL
            'cidade': 'Cidade',       # NOVO LABEL
            'estado': 'Estado',       # NOVO LABEL
        }