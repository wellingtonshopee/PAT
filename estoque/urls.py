# pat/estoque/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_itens_estoque, name='listar_itens_estoque'),
    path('adicionar/', views.adicionar_item_estoque, name='adicionar_item_estoque'),
    path('editar/<int:pk>/', views.editar_item_estoque, name='editar_item_estoque'),
    path('excluir/<int:pk>/', views.excluir_item_estoque, name='excluir_item_estoque'),
    path('entrada/', views.registrar_entrada_estoque, name='registrar_entrada_estoque'), # <--- NOVA URL!
    path('saida/', views.registrar_saida_estoque, name='registrar_saida_estoque'), # <--- NOVA URL!
    # Outras URLs do estoque virão aqui
]