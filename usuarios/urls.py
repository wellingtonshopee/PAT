# pat/usuarios/urls.py
from django.urls import path
from . import views

app_name = 'usuarios' # <-- ESSA LINHA É CRUCIAL PARA O NAMESPACE!

urlpatterns = [
    # URL para a página inicial/dashboard (se ela estiver na app 'usuarios')
    path('', views.home, name='home'),

    # URL para a página de cadastro de usuários
    path('cadastro_usuario/', views.cadastro_usuario, name='cadastro_usuario'),

    # URL para a página de log de atividades
    path('log-atividades/', views.log_atividades, name='log_atividades'),

    # Se você removeu os paths de login/logout do seu projeto principal,
    # e deseja tê-los aqui, pode adicionar:
    # path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    # Mas lembre-se que, para isso, a linha 'from django.contrib.auth import views as auth_views' precisaria ser descomentada.
    # Pelo seu 'meu_projeto_admin/urls.py', parece que 'accounts/' já cuida disso no projeto principal.
]