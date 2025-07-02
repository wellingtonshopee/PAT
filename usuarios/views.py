# pat/usuarios/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages # Importe messages
from django.urls import reverse # Importe reverse para construir URLs dinamicamente
from .forms import CustomUserCreationForm
from .models import LogAtividade
from django.db.models import Q
# NOVIDADE: Importe o modelo User do Django
from django.contrib.auth.models import User
from django.http import HttpResponse # NOVIDADE: Importe HttpResponse

# --- FUNÇÃO AUXILIAR PARA VERIFICAR GRUPO ---
def is_in_group(user, group_name):
    """
    Verifica se o usuário pertence ao grupo especificado ou se é um superusuário.
    """
    if user.is_superuser:
        return True
    return user.groups.filter(name=group_name).exists()

# --- Função de Teste Customizada para Redirecionamento e Mensagem (AJUSTADA) ---
def group_required_with_message(group_names, redirect_url_name='usuarios:home', message_text='Você não tem permissão para acessar esta página.'):
    def check_group(user):
        if user.is_superuser:
            return True
        for group_name in group_names:
            if user.groups.filter(name=group_name).exists():
                return True
        return False

    def decorator(view_func):
        @login_required # Garante que o usuário esteja logado antes de verificar o grupo
        def _wrapped_view(request, *args, **kwargs):
            if not check_group(request.user):
                # Adiciona a mensagem de erro antes do redirecionamento
                messages.error(request, message_text)
                return redirect(redirect_url_name)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# --- VIEWS DO PROJETO COM CONTROLE DE ACESSO POR GRUPO E MENSAGEM ---

@login_required
def home(request):
    return render(request, 'usuarios/home.html', {'user': request.user, 'active_page': 'home'})

# Aplicando a função ajustada para 'cadastro_usuario'
@group_required_with_message(['Administradores'], message_text='Você não tem permissão para cadastrar usuários.')
def cadastro_usuario(request):
    # O decorador acima já garantiu que apenas superusuários ou membros do grupo 'Administradores' cheguem aqui.
    # Não precisamos mais da verificação interna e redirecionamento.

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuário "{user.username}" cadastrado com sucesso!')
            return redirect('usuarios:cadastro_usuario')
        else:
            messages.error(request, 'Erro ao cadastrar usuário. Verifique os campos.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'usuarios/cadastro_usuario.html', {'form': form, 'active_page': 'cadastro_usuario'})

# Aplicando a função ajustada para 'log_atividades'
@group_required_with_message(['Gerentes', 'Administradores'], message_text='Você não tem permissão para visualizar o Log de Atividades.')
def log_atividades(request):
    # O decorador acima já garantiu que apenas superusuários ou membros dos grupos 'Gerentes'/'Administradores' cheguem aqui.
    # Não precisamos mais da verificação interna e redirecionamento.

    if request.user.is_superuser:
        logs = LogAtividade.objects.all()
    else:
        user_group_ids = [group.id for group in request.user.groups.all()]
        logs = LogAtividade.objects.filter(
            Q(usuario__groups__id__in=user_group_ids) | Q(usuario=request.user)
        ).distinct()

    context = {
        'logs': logs,
        'active_page': 'log_atividades'
    }
    return render(request, 'usuarios/log_atividades.html', context)

# --- NOVIDADE: FUNÇÃO TEMPORÁRIA PARA ALTERAR SENHA DO ADMIN ---
# ATENÇÃO: REMOVER ESTA FUNÇÃO E SUA URL ASSIM QUE A SENHA FOR ALTERADA COM SUCESSO!
def set_admin_password_temp_view(request):
    if request.method == 'GET':
        username = 'wcampos@241059' # O usuário que você quer resetar
        new_password = 'Qaz241059@989910' # A nova senha

        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            messages.success(request, f"Senha do usuário {username} alterada com sucesso!")
            # Redireciona para a página de login para você testar
            return redirect('/accounts/login/')
        except User.DoesNotExist:
            messages.error(request, f"Usuário {username} não encontrado.")
            return HttpResponse(f"Usuário {username} não encontrado.")
        except Exception as e:
            messages.error(request, f"Ocorreu um erro: {e}")
            return HttpResponse(f"Erro ao alterar senha: {e}")
    return HttpResponse("Método não permitido ou acesso direto inválido. Esta é uma função de uso único.")