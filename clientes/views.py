# clientes/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cliente
from .forms import ClienteForm
from .filters import ClienteFilter 

@login_required
def listar_clientes(request):
    # Use Cliente.objects.all() para o queryset base antes de aplicar o filtro
    clientes_queryset = Cliente.objects.all().order_by('razao_social')

    # Cria uma instância do filtro com os dados da requisição (GET) e o queryset base
    cliente_filter = ClienteFilter(request.GET, queryset=clientes_queryset)

    # Os clientes filtrados estão disponíveis em cliente_filter.qs
    clientes = cliente_filter.qs

    context = {
        'clientes': clientes,
        'filter': cliente_filter, # <--- PASSE A INSTÂNCIA DO FILTRO PARA O TEMPLATE
        'title': 'Lista de Clientes'
    }
    return render(request, 'clientes/listar_clientes.html', context)

@login_required
def adicionar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente adicionado com sucesso!')
            return redirect('listar_clientes')
    else:
        form = ClienteForm()
    context = {
        'form': form,
        'title': 'Adicionar Cliente'
    }
    return render(request, 'clientes/adicionar_cliente.html', context)

@login_required
def detalhar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    context = {
        'cliente': cliente,
        'title': f'Detalhes do Cliente: {cliente.razao_social}'
    }
    return render(request, 'clientes/detalhar_cliente.html', context)

@login_required
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('detalhar_cliente', pk=cliente.pk)
    else:
        form = ClienteForm(instance=cliente)
    context = {
        'form': form,
        'cliente': cliente,
        'title': f'Editar Cliente: {cliente.razao_social}'
    }
    return render(request, 'clientes/editar_cliente.html', context)

@login_required
def excluir_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.info(request, 'Cliente excluído com sucesso!')
        return redirect('listar_clientes')
    context = {
        'cliente': cliente,
        'title': f'Confirmar Exclusão: {cliente.razao_social}'
    }
    return render(request, 'clientes/excluir_cliente.html', context)