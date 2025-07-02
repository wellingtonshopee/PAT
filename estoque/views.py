# pat/estoque/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction # Importe para operações atômicas
from django.db.models import Q, F
from .models import ItemEstoque, MovimentacaoEstoque
from .forms import ItemEstoqueFilterForm, ItemEstoqueForm, EntradaEstoqueForm, SaidaEstoqueForm  # Importe EntradaEstoqueForm

# ...

@login_required
def listar_itens_estoque(request):
    # Lógica de filtro existente
    filter_form = ItemEstoqueFilterForm(request.GET)
    itens = ItemEstoque.objects.all()

    if filter_form.is_valid():
        search_query = filter_form.cleaned_data.get('search_query')
        categoria = filter_form.cleaned_data.get('categoria')
        localizacao = filter_form.cleaned_data.get('localizacao')

        if search_query:
            itens = itens.filter(
                Q(nome__icontains=search_query) | # <--- MUDANÇA AQUI: de models.Q para Q
                Q(descricao__icontains=search_query) | # <--- MUDANÇA AQUI: de models.Q para Q
                Q(codigo_interno__icontains=search_query) # <--- MUDANÇA AQUI: de models.Q para Q
            )
        if categoria:
            itens = itens.filter(categoria=categoria)
        if localizacao:
            itens = itens.filter(localizacao=localizacao)

    # Lógica para filtro de status de estoque
    estoque_status = request.GET.get('estoque_status')
    if estoque_status == 'abaixo_minimo':
        # MUDANÇA AQUI: de models.F para F
        itens = itens.filter(quantidade__lte=F('estoque_minimo'), quantidade__gt=0)
        messages.info(request, "Exibindo apenas itens com estoque abaixo do mínimo.")
    elif estoque_status == 'zerado':
        itens = itens.filter(quantidade=0)
        messages.info(request, "Exibindo apenas itens com estoque zerado.")

    itens = itens.order_by('nome') # Garante uma ordenação padrão

    context = {
        'itens': itens,
        'filter_form': filter_form,
        'active_page': 'estoque',
        'estoque_status': estoque_status,
    }
    return render(request, 'estoque/listar_itens_estoque.html', context)

@login_required
def adicionar_item_estoque(request):
    if request.method == 'POST':
        form = ItemEstoqueForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item de estoque adicionado com sucesso!')
            return redirect('listar_itens_estoque') # Redireciona para a lista após o sucesso
        else:
            messages.error(request, 'Erro ao adicionar item de estoque. Verifique os campos.')
    else:
        form = ItemEstoqueForm() # Instancia um formulário vazio para o método GET

    context = {
        'form': form,
        'active_page': 'estoque_add', # Para destacar no menu lateral, se houvesse um link direto
    }
    return render(request, 'estoque/adicionar_item_estoque.html', context)

@login_required
def editar_item_estoque(request, pk): # 'pk' é a chave primária do item
    item = get_object_or_404(ItemEstoque, pk=pk) # Busca o item pelo ID ou retorna 404

    if request.method == 'POST':
        form = ItemEstoqueForm(request.POST, instance=item) # Preenche o formulário com dados da requisição E com a instância do item
        if form.is_valid():
            form.save()
            messages.success(request, f'Item "{item.nome}" atualizado com sucesso!')
            return redirect('listar_itens_estoque')
        else:
            messages.error(request, 'Erro ao atualizar item de estoque. Verifique os campos.')
    else:
        form = ItemEstoqueForm(instance=item) # Preenche o formulário com os dados do item existente

    context = {
        'form': form,
        'item': item, # Passa o item para o template, se precisar de algum dado dele
        'active_page': 'estoque_edit', # Pode ser usado para destacar menu se tiver
    }
    return render(request, 'estoque/editar_item_estoque.html', context) # Novo template

@login_required
def excluir_item_estoque(request, pk):
    item = get_object_or_404(ItemEstoque, pk=pk)
    if request.method == 'POST':
        item_nome = item.nome # Salva o nome antes de deletar para a mensagem
        item.delete()
        messages.success(request, f'Item "{item_nome}" excluído com sucesso!')
        return redirect('listar_itens_estoque')
    # Se for uma requisição GET para esta URL, você pode redirecionar ou mostrar um erro
    # Para exclusão, é sempre melhor esperar um POST para segurança.
    messages.error(request, 'Requisição inválida para exclusão de item.')
    return redirect('listar_itens_estoque')
@login_required
def registrar_entrada_estoque(request):
    if request.method == 'POST':
        form = EntradaEstoqueForm(request.POST)
        if form.is_valid():
            item = form.cleaned_data['item']
            quantidade_movimentada = form.cleaned_data['quantidade_movimentada']
            descricao = form.cleaned_data['descricao']

            try:
                # Usamos uma transação atômica para garantir que ambas as operações 
                # (criar movimentação e atualizar item) ocorram ou nenhuma ocorra.
                with transaction.atomic():
                    # 1. Cria a MovimentacaoEstoque
                    movimentacao = MovimentacaoEstoque.objects.create(
                        item=item,
                        tipo_movimentacao='ENTRADA', # Define o tipo de movimentação como ENTRADA
                        quantidade_movimentada=quantidade_movimentada,
                        descricao=descricao,
                        movimentado_por=request.user # O usuário logado
                    )

                    # 2. Atualiza a quantidade do ItemEstoque
                    item.quantidade += quantidade_movimentada
                    item.save()

                messages.success(request, f'Entrada de {quantidade_movimentada} unidades de "{item.nome}" registrada com sucesso!')
                return redirect('listar_itens_estoque') # Redireciona para a lista após o sucesso
            except Exception as e:
                messages.error(request, f'Erro ao registrar entrada de estoque: {e}')
        else:
            messages.error(request, 'Erro ao registrar entrada de estoque. Verifique os campos.')
    else:
        form = EntradaEstoqueForm() # Instancia um formulário vazio para o método GET

    context = {
        'form': form,
        'active_page': 'estoque_entrada', # Para destacar no menu lateral
    }
    return render(request, 'estoque/registrar_entrada_estoque.html', context) # Novo template

@login_required
def registrar_saida_estoque(request):
    if request.method == 'POST':
        form = SaidaEstoqueForm(request.POST)
        if form.is_valid():
            item = form.cleaned_data['item']
            quantidade_movimentada = form.cleaned_data['quantidade_movimentada']
            descricao = form.cleaned_data['descricao']

            try:
                with transaction.atomic():
                    # 1. Cria a MovimentacaoEstoque
                    movimentacao = MovimentacaoEstoque.objects.create(
                        item=item,
                        tipo_movimentacao='SAIDA', # Define o tipo de movimentação como SAIDA
                        quantidade_movimentada=quantidade_movimentada,
                        descricao=descricao,
                        movimentado_por=request.user # O usuário logado
                    )

                    # 2. Atualiza a quantidade do ItemEstoque (subtrai)
                    item.quantidade -= quantidade_movimentada
                    item.save()

                messages.success(request, f'Saída de {quantidade_movimentada} unidades de "{item.nome}" registrada com sucesso!')
                return redirect('listar_itens_estoque') # Redireciona para a lista após o sucesso
            except Exception as e:
                messages.error(request, f'Erro ao registrar saída de estoque: {e}')
        else:
            messages.error(request, 'Erro ao registrar saída de estoque. Verifique os campos.')
    else:
        form = SaidaEstoqueForm() # Instancia um formulário vazio para o método GET

    context = {
        'form': form,
        'active_page': 'estoque_saida', # Para destacar no menu lateral
    }
    return render(request, 'estoque/registrar_saida_estoque.html', context) # Novo template