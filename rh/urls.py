# C:\Users\SEAOps\Documents\pat\rh\urls.py

from django.urls import path
from . import views

# ADICIONE ESTA LINHA AQUI
app_name = 'rh'

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
    path('absenteismo/relatorio-mensal/', views.relatorio_absenteismo_form, name='relatorio_absenteismo_form'),
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

    # ==============================================================================
    # NOVAS URLs PARA TREINAMENTO (já com os nomes corretos para Treinamento)
    # ==============================================================================

    # NOVO: URL para a Home de Treinamento
    path('treinamentos-home/', views.treinamento_home, name='treinamento_home'),

    # URLs para Treinamento (Tipo de Treinamento)
    path('treinamentos/', views.TreinamentoListView.as_view(), name='treinamento_list'),
    path('treinamentos/<int:pk>/', views.TreinamentoDetailView.as_view(), name='treinamento_detail'),
    path('treinamentos/adicionar/', views.TreinamentoCreateView.as_view(), name='treinamento_create'),
    path('treinamentos/editar/<int:pk>/', views.TreinamentoUpdateView.as_view(), name='treinamento_update'),
    path('treinamentos/excluir/<int:pk>/', views.TreinamentoDeleteView.as_view(), name='treinamento_delete'),

    # URLs para Turma de Treinamento
    path('turmas/', views.TurmaTreinamentoListView.as_view(), name='turmas_treinamento_list'),
    path('turmas/<int:pk>/', views.TurmaTreinamentoDetailView.as_view(), name='turma_treinamento_detail'),
    path('turmas/adicionar/', views.TurmaTreinamentoCreateView.as_view(), name='turma_treinamento_create'),
    path('turmas/editar/<int:pk>/', views.TurmaTreinamentoUpdateView.as_view(), name='turma_treinamento_update'),
    path('turmas/excluir/<int:pk>/', views.TurmaTreinamentoDeleteView.as_view(), name='turma_treinamento_delete'),

    # URLs para ParticipacaoTurma
    path('participacoes/', views.ParticipacaoTurmaListView.as_view(), name='participacao_turma_list'),
    # URL para criar participação associada a uma turma específica
    path('turmas/<int:turma_pk>/participacoes/novo/', views.ParticipacaoTurmaCreateView.as_view(), name='participacao_turma_create'),
    # NOVO: URL para criar participação sem especificar a turma (será selecionada no formulário)
    path('participacoes/adicionar-geral/', views.ParticipacaoTurmaCreateView.as_view(), name='participacao_turma_create_general'),
    
    path('turmas/<int:turma_pk>/participacoes/<int:pk>/editar/', views.ParticipacaoTurmaUpdateView.as_view(), name='participacao_turma_update'),
    path('turmas/<int:turma_pk>/participacoes/<int:pk>/excluir/', views.ParticipacaoTurmaDeleteView.as_view(), name='participacao_turma_delete'),

    # URLs para Geração de Documentos
    path('turmas/<int:pk>/lista-presenca/', views.TurmaListaPresencaPDFView.as_view(), name='turma_lista_presenca_pdf'),
    path('participacoes/<int:pk>/certificado/', views.ParticipacaoCertificadoPDFView.as_view(), name='participacao_certificado_pdf'),
]
