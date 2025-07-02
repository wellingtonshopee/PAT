# pat/fornecedores/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q # Para filtros complexos

from .models import Fornecedor, TipoFornecedor
from .forms import FornecedorForm, FornecedorFilterForm # Importe os formulários

@login_required
def listar_fornecedores(request):
    fornecedores = Fornecedor.objects.all()
    filter_form = FornecedorFilterForm(request.GET)

    if filter_form.is_valid():
        search_query = filter_form.cleaned_data.get('search_query')
        tipo_fornecedor = filter_form.cleaned_data.get('tipo_fornecedor')
        ativo = filter_form.cleaned_data.get('ativo') # Retorna 'True', 'False' ou None

        if search_query:
            fornecedores = fornecedores.filter(
                Q(nome_fantasia__icontains=search_query) |
                Q(razao_social__icontains=search_query) |
                Q(cnpj_cpf__icontains=search_query) |
                Q(contato_principal__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        if tipo_fornecedor:
            fornecedores = fornecedores.filter(tipo_fornecedor=tipo_fornecedor)

        # O campo 'ativo' no formulário retorna string, precisamos converter para booleano
        if ativo is not None and ativo != '': # Verifica se não é nulo e não é string vazia
            if ativo == 'True':
                fornecedores = fornecedores.filter(ativo=True)
            elif ativo == 'False':
                fornecedores = fornecedores.filter(ativo=False)

    fornecedores = fornecedores.order_by('nome_fantasia') # Ordena por nome fantasia por padrão

    context = {
        'fornecedores': fornecedores,
        'filter_form': filter_form,
        'active_page': 'fornecedores', # Para destacar no menu lateral
    }
    return render(request, 'fornecedores/listar_fornecedores.html', context)

@login_required
def adicionar_fornecedor(request):
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Fornecedor "{form.instance.nome_fantasia}" adicionado com sucesso!')
            return redirect('listar_fornecedores') # Redireciona para a lista
        else:
            messages.error(request, 'Erro ao adicionar fornecedor. Verifique os campos.')
    else:
        form = FornecedorForm() # Formulário vazio para GET

    context = {
        'form': form,
        'active_page': 'fornecedores_adicionar', # Pode ser usado para destacar link "Adicionar" no menu
    }
    return render(request, 'fornecedores/adicionar_fornecedor.html', context)

@login_required
def editar_fornecedor(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk) # Busca o fornecedor pelo ID ou retorna 404
    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor) # Preenche o formulário com a instância existente
        if form.is_valid():
            form.save()
            messages.success(request, f'Fornecedor "{fornecedor.nome_fantasia}" atualizado com sucesso!')
            return redirect('listar_fornecedores')
        else:
            messages.error(request, 'Erro ao atualizar fornecedor. Verifique os campos.')
    else:
        form = FornecedorForm(instance=fornecedor) # Formulário pré-preenchido para GET

    context = {
        'form': form,
        'fornecedor': fornecedor, # Passa o objeto fornecedor para o template, se precisar exibir detalhes
        'active_page': 'fornecedores',
    }
    return render(request, 'fornecedores/editar_fornecedor.html', context)

# pat/fornecedores/views.py

# ... (imports e as outras views existentes) ...

@login_required
def excluir_fornecedor(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    if request.method == 'POST':
        nome_fornecedor = fornecedor.nome_fantasia # Guarda o nome antes de excluir
        fornecedor.delete()
        messages.success(request, f'Fornecedor "{nome_fornecedor}" excluído com sucesso.')
        return redirect('listar_fornecedores')
    # Para GET requests, podemos renderizar uma página de confirmação.
    # Por simplicidade, vamos apenas redirecionar com uma mensagem de erro se tentar GET
    messages.error(request, 'A exclusão deve ser feita via POST.')
    return redirect('listar_fornecedores')

