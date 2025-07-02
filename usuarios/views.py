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

# --- NOVIDADE: FUNÇÃO TEMPORÁRIA PARA ELEVAR/CRIAR SUPERUSUÁRIO ---
# ATENÇÃO: REMOVER ESTA FUNÇÃO E SUA URL ASSIM QUE O SUPERUSUÁRIO FOR CONFIGURADO!
def elevate_or_create_superuser_temp_view(request):
    if request.method == 'GET':
        username_to_elevate = 'g.nilson@LMG21' # O usuário que você quer elevar ou criar
        email_for_new_user = 'g.nilson@example.com' # Email, mesmo que não seja usado para login
        new_password_for_user = 'Qaz241059@989910' # A nova senha definida

        try:
            user = User.objects.get(username=username_to_elevate)
            # Se o usuário existe, eleva a superusuário e define a nova senha
            user.is_staff = True
            user.is_superuser = True
            user.set_password(new_password_for_user)
            user.save()
            messages.success(request, f"Usuário '{username_to_elevate}' elevado a superusuário e senha alterada com sucesso!")
            return redirect('/accounts/login/')
        except User.DoesNotExist:
            # Se o usuário não existe, cria-o como superusuário
            try:
                user = User.objects.create_superuser(username_to_elevate, email_for_new_user, new_password_for_user)
                messages.success(request, f"Superusuário '{username_to_elevate}' criado com sucesso!")
                return redirect('/accounts/login/')
            except Exception as e:
                messages.error(request, f"Erro ao criar superusuário: {e}")
                return HttpResponse(f"Erro ao criar superusuário: {e}")
        except Exception as e:
            messages.error(request, f"Ocorreu um erro inesperado: {e}")
            return HttpResponse(f"Erro inesperado: {e}")
    return HttpResponse("Método não permitido ou acesso direto inválido. Esta é uma função de uso único.")