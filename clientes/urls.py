# clientes/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_clientes, name='listar_clientes'),
    path('adicionar/', views.adicionar_cliente, name='adicionar_cliente'),
    path('<int:pk>/', views.detalhar_cliente, name='detalhar_cliente'),
    path('<int:pk>/editar/', views.editar_cliente, name='editar_cliente'),
    path('<int:pk>/excluir/', views.excluir_cliente, name='excluir_cliente'),
]