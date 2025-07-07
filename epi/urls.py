# pat/epi/urls.py

from django.urls import path
from . import views
# Remove TemplateView import if AbsenteismoHomeView is no longer here
# from django.views.generic import TemplateView

urlpatterns = [
    # URLs para EPIs
    path('', views.listar_epis, name='listar_epis'),
    path('adicionar/', views.adicionar_epi, name='adicionar_epi'),
    path('editar/<int:pk>/', views.editar_epi, name='editar_epi'),
    path('excluir/<int:pk>/', views.excluir_epi, name='excluir_epi'),

    # URLs para Tipos de EPI
    path('tipos/', views.listar_tipos_epi, name='listar_tipos_epi'),
    path('tipos/adicionar/', views.adicionar_tipo_epi, name='adicionar_tipo_epi'),
    path('tipos/editar/<int:pk>/', views.editar_tipo_epi, name='editar_tipo_epi'),
    path('tipos/excluir/<int:pk>/', views.excluir_tipo_epi, name='excluir_tipo_epi'),

    # URLs para Colaboradores
    path('colaboradores/', views.listar_colaboradores, name='listar_colaboradores'),
    path('colaboradores/adicionar/', views.adicionar_colaborador, name='adicionar_colaborador'),
    path('colaboradores/editar/<int:pk>/', views.editar_colaborador, name='editar_colaborador'),
    path('colaboradores/excluir/<int:pk>/', views.excluir_colaborador, name='excluir_colaborador'),

    # **NOVA URL PARA A API DO COLABORADOR**
    path('api/colaborador/<int:pk>/', views.get_colaborador_data, name='api_get_colaborador_data'),

    # URLs para Entradas de EPI
    path('entradas/', views.listar_entradas_epi, name='listar_entradas_epi'),
    path('entradas/adicionar/', views.adicionar_entrada_epi, name='adicionar_entrada_epi'),
    path('entradas/editar/<int:pk>/', views.editar_entrada_epi, name='editar_entrada_epi'),
    path('entradas/excluir/<int:pk>/', views.excluir_entrada_epi, name='excluir_entrada_epi'),

    # URLs para Saídas de EPI
    path('saidas/', views.listar_saidas_epi, name='listar_saidas_epi'),
    path('saidas/adicionar/', views.adicionar_saida_epi, name='adicionar_saida_epi'),
    path('saidas/gerar_pdf/', views.gerar_pdf_saida_epi, name='gerar_pdf_saida_epi'),
    path('saidas/editar/<int:pk>/', views.editar_saida_epi, name='editar_saida_epi'),
    path('saidas/excluir/<int:pk>/', views.excluir_saida_epi, name='excluir_saida_epi'),
    # NOVO: URL para imprimir PDF de uma saída específica
    path('saidas/imprimir_pdf/<int:pk>/', views.imprimir_saida_epi_pdf, name='imprimir_saida_epi_pdf'),

    # As URLs para Absenteísmo foram MOVIDAS para rh/urls.py
]