# financeiro/urls.py

from django.urls import path
from . import views

app_name = 'financeiro' # Importante para referenciar URLs como 'financeiro:listar_contas_pagar'

urlpatterns = [
    # URLs para Contas a Pagar
    path('contas-a-pagar/', views.listar_contas_pagar, name='listar_contas_pagar'),
    path('contas-a-pagar/adicionar/', views.adicionar_conta_pagar, name='adicionar_conta_pagar'),
    path('contas-a-pagar/detalhar/<int:pk>/', views.detalhar_conta_pagar, name='detalhar_conta_pagar'),
    path('contas-a-pagar/editar/<int:pk>/', views.editar_conta_pagar, name='editar_conta_pagar'),
    path('contas-a-pagar/baixar/<int:pk>/', views.baixar_conta_pagar, name='baixar_conta_pagar'),
    path('contas-a-pagar/excluir/<int:pk>/', views.excluir_conta_pagar, name='excluir_conta_pagar'),
    path('contas-a-pagar/exportar-csv/', views.exportar_contas_pagar_csv, name='exportar_contas_pagar_csv'),

    # URLs para Contas a Receber
    # Padronizado para usar hífens e nomes de URLs mais descritivos
    path('contas-a-receber/', views.lista_contas_receber, name='lista_contas_receber'), # Agora o nome da URL corresponde ao template
    path('contas-a-receber/nova/', views.nova_conta_receber, name='nova_conta_receber'),
    path('contas-a-receber/detalhar/<int:pk>/', views.detalhar_conta_receber, name='detalhar_conta_receber'),
    path('contas-a-receber/editar/<int:pk>/', views.editar_conta_receber, name='editar_conta_receber'),
    path('contas-a-receber/baixar/<int:pk>/', views.baixar_conta_receber, name='baixar_conta_receber'),
    path('contas-a-receber/excluir/<int:pk>/', views.excluir_conta_receber, name='excluir_conta_receber'),
    path('contas-a-receber/exportar-csv/', views.exportar_contas_receber_csv, name='exportar_contas_receber_csv'), # Ajustei o nome da URL para o CSV também
    path('relatorio/', views.relatorio_financeiro, name='relatorio_financeiro'),
]