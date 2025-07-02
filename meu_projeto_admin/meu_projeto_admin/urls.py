# pat/usuarios/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views # Importa as views de autenticação do Django
from . import views # Importa as views do seu próprio app 'usuarios'

urlpatterns = [
    # URL para a página de login
    # Usamos a LoginView do Django, que já vem com a lógica de autenticação
    # O template_name aponta para o nosso arquivo HTML personalizado
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    # URL para a página de logout
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'), # Redireciona para login após logout
    # Você pode adicionar outras URLs aqui, como registro, recuperação de senha, etc.
]