# pat/meu_projeto_admin/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings # IMPORTANTE: Adicionado para acessar settings.DEBUG, MEDIA_URL, MEDIA_ROOT
from django.conf.urls.static import static # IMPORTANTE: Adicionado para servir arquivos de mídia e estáticos em desenvolvimento
from usuarios import views as usuarios_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', usuarios_views.home, name='home'),
    path('estoque/', include('estoque.urls')),
    # AQUI ESTÁ A MUDANÇA: Adicionado namespace='patrimonio'
    path('patrimonio/', include('patrimonio.urls', namespace='patrimonio')), 
    path('fornecedores/', include('fornecedores.urls')), 
    path('epis/', include('epi.urls')),
    path('financeiro/', include('financeiro.urls', namespace='financeiro')),
    path('clientes/', include('clientes.urls')),
    path('usuarios/', include('usuarios.urls')), 
]

# IMPORTANTE: Configuração para servir arquivos de mídia (uploads) e estáticos
# Esta parte só funciona em ambiente de DESENVOLVIMENTO (quando DEBUG=True).
# Em produção, você usaria um servidor web (como Nginx, Apache) para servir estes arquivos diretamente.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Se você tiver STATICFILES_DIRS e quiser que o servidor de desenvolvimento sirva-os também
    # (além do STATIC_URL padrão que já é servido por django.contrib.staticfiles)
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Esta linha não é estritamente necessária se STATIC_ROOT estiver configurado corretamente, pois collectstatic move tudo para lá.

    