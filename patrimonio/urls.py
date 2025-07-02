# pat/patrimonio/urls.py

from django.urls import path
from . import views

app_name = 'patrimonio' 

urlpatterns = [
    path('', views.listar_itens_patrimonio, name='listar_itens_patrimonio'),
    path('adicionar/', views.adicionar_item_patrimonio, name='adicionar_item_patrimonio'),
    path('item/<int:pk>/', views.detalhar_item_patrimonio, name='detalhar_item_patrimonio'),
    path('item/<int:pk>/editar/', views.editar_item_patrimonio, name='editar_item_patrimonio'),
    path('item/<int:pk>/excluir/', views.excluir_item_patrimonio, name='excluir_item_patrimonio'),
    path('item/<int:pk>/baixar/', views.baixar_item_patrimonio, name='baixar_item_patrimonio'),
    path('item/<int:pk>/transferir/', views.transferir_item_patrimonio, name='transferir_item_patrimonio'),
    path('movimentacoes/', views.listar_movimentacoes, name='listar_movimentacoes'),
    path('relatorio/', views.gerar_relatorio_patrimonio, name='gerar_relatorio_patrimonio'),
    path('relatorio/exportar/csv/', views.exportar_patrimonio_csv, name='exportar_patrimonio_csv'),
    path('relatorio/exportar/excel/', views.exportar_patrimonio_excel, name='exportar_patrimonio_excel'),
    
    # URL para Geração do QR Code (apenas uma vez!)
    path('item/<int:item_id>/qrcode/', views.gerar_qrcode_patrimonio, name='gerar_qrcode_patrimonio'),
    
    # MUITO IMPORTANTE: Adicione a URL para a Coleta de Inventário
    path('inventario/coletar/', views.coleta_inventario, name='coleta_inventario'),
    # MUITO IMPORTANTE: Adicione a URL para a Confirmação de Inventário (se você a tem no seu views.py)
    path('inventario/confirmar/', views.confirmar_inventario, name='confirmar_inventario'),
    path('inventario/conferencia/', views.relatorio_inventario_conferencia, name='relatorio_inventario_conferencia'),
    path('inventario/conferencia/exportar-csv/', views.exportar_inventario_conferencia_csv, name='exportar_inventario_conferencia_csv'),
    
]