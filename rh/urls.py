# C:\Users\SEAOps\Documents\pat\rh\urls.py

from django.urls import path
from . import views

urlpatterns = [
    # --- URLs Gerais de RH ---
    path('', views.rh_home, name='rh_home'), # Página inicial do RH

    # --- URLs para Tipos de Contrato ---
    path('tipos-contrato/', views.lista_tipos_contrato, name='lista_tipos_contrato'),
    path('tipos-contrato/adicionar/', views.adicionar_tipo_contrato, name='adicionar_tipo_contrato'),
    path('tipos-contrato/editar/<int:pk>/', views.editar_tipo_contrato, name='editar_tipo_contrato'),
    path('tipos-contrato/excluir/<int:pk>/', views.excluir_tipo_contrato, name='excluir_tipo_contrato'),

    # --- URLs para Absenteísmo ---
    path('absenteismo/', views.absenteismo_home, name='absenteismo_home'),
    path('absenteismo/registros/', views.lista_registros_absenteismo, name='lista_registros_absenteismo'),
    path('absenteismo/registros/adicionar/', views.adicionar_registro_absenteismo, name='adicionar_registro_absenteismo'),
    path('absenteismo/registros/editar/<int:pk>/', views.editar_registro_absenteismo, name='editar_registro_absenteismo'),
    path('absenteismo/registros/excluir/<int:pk>/', views.excluir_registro_absenteismo, name='excluir_registro_absenteismo'),
    
    # URLs para Tipos de Absenteísmo (sub-seção de Absenteísmo)
    path('absenteismo/tipos/', views.lista_tipos_absenteismo, name='lista_tipos_absenteismo'),
    path('absenteismo/tipos/adicionar/', views.adicionar_tipo_absenteismo, name='adicionar_tipo_absenteismo'),
    path('absenteismo/tipos/editar/<int:pk>/', views.editar_tipo_absenteismo, name='editar_tipo_absenteismo'),
    path('absenteismo/tipos/excluir/<int:pk>/', views.excluir_tipo_absenteismo, name='excluir_tipo_absenteismo'),

    # --- URL PARA MARCAÇÃO DIÁRIA DE ABSENTEÍSMO ---
    path('absenteismo/diario/', views.marcar_absenteismo_diario, name='marcar_absenteismo_diario'),
    
    # --- NOVAS URLs para Relatório de Absenteísmo CSV ---
    # Esta é a URL para a página que contém o formulário de seleção de mês/ano.
    # Exemplo de acesso: /rh/absenteismo/relatorio-mensal/
    path('absenteismo/relatorio-mensal/', views.relatorio_absenteismo_form, name='relatorio_absenteismo_form'),

    # Esta é a URL para a view que efetivamente gera e exporta o arquivo CSV.
    # Pode ser acessada tanto do formulário de seleção de mês/ano, quanto do botão na lista de registros.
    # Exemplo de acesso: /rh/absenteismo/relatorio/exportar-csv/
    path('absenteismo/relatorio/exportar-csv/', views.exportar_relatorio_absenteismo_csv, name='exportar_absenteismo_csv'),


    # --- URLs para Líderes ---
    path('lideres/', views.lista_lideres, name='lista_lideres'),
    path('lideres/adicionar/', views.adicionar_lider, name='adicionar_lider'),
    path('lideres/editar/<int:pk>/', views.editar_lider, name='editar_lider'),
    path('lideres/excluir/<int:pk>/', views.excluir_lider, name='excluir_lider'),

    # --- URLs para Cargos ---
    path('cargos/', views.lista_cargos, name='lista_cargos'),
    path('cargos/adicionar/', views.adicionar_cargo, name='adicionar_cargo'),
    path('cargos/editar/<int:pk>/', views.editar_cargo, name='editar_cargo'),
    path('cargos/excluir/<int:pk>/', views.excluir_cargo, name='excluir_cargo'),
]