# pat/fornecedores/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('fornecedores/', views.listar_fornecedores, name='listar_fornecedores'),
    path('fornecedores/adicionar/', views.adicionar_fornecedor, name='adicionar_fornecedor'),
    path('fornecedores/editar/<int:pk>/', views.editar_fornecedor, name='editar_fornecedor'), # <--- CORRIGIDO AQUI!
    path('fornecedores/excluir/<int:pk>/', views.excluir_fornecedor, name='excluir_fornecedor'),
]