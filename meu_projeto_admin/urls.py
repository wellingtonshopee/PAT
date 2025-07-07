# pat/meu_projeto_admin/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static 
from usuarios import views as usuarios_views
from usuarios.views import elevate_or_create_superuser_temp_view # Importa a nova função temporária

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', usuarios_views.home, name='home'),
    path('estoque/', include('estoque.urls')),
    path('patrimonio/', include('patrimonio.urls', namespace='patrimonio')),
    path('fornecedores/', include('fornecedores.urls')),
    path('epis/', include('epi.urls')),
    path('financeiro/', include('financeiro.urls', namespace='financeiro')),
    path('clientes/', include('clientes.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('rh/', include('rh.urls')), # Esta linha está correta para incluir as URLs do app 'rh'
    
    # URL TEMPORÁRIA PARA ELEVAR/CRIAR SUPERUSUÁRIO - REMOVER APÓS O USO!
    path('elevate-superuser-emergency/', elevate_or_create_superuser_temp_view, name='elevate_superuser_emergency'),
]

# Configuração para servir arquivos de mídia (uploads) e estáticos em DESENVOLVIMENTO
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)