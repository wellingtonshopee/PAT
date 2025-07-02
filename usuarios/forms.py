# pat/usuarios/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group # Importe o modelo Group
from django.contrib.auth import get_user_model # Para obter o modelo de usuário atual

User = get_user_model() # Obtém o modelo de usuário ativo (pode ser o padrão ou um customizado)

class CustomUserCreationForm(UserCreationForm):
    # Campos para seleção de grupos
    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple, # Para exibir como checkboxes
        required=False, # Não é obrigatório atribuir um grupo no cadastro
        label="Grupos de Acesso"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name',)
        # Adicione 'email', 'first_name', 'last_name' se quiser que apareçam no formulário.
        # O campo 'username' já está incluído por padrão.

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Adiciona o usuário aos grupos selecionados
            self.cleaned_data['grupos'].update() # Garante que os grupos sejam adicionados corretamente
            if self.cleaned_data['grupos']:
                user.groups.set(self.cleaned_data['grupos']) # Define os grupos do usuário
        return user

class CustomUserChangeForm(UserChangeForm):
    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Grupos de Acesso"
    )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = UserChangeForm.Meta.fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Preenche os grupos existentes do usuário ao carregar o formulário de edição
            self.fields['grupos'].initial = self.instance.groups.all()

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            if self.cleaned_data['grupos']:
                user.groups.set(self.cleaned_data['grupos'])
            else:
                user.groups.clear() # Limpa todos os grupos se nenhum for selecionado
        return user