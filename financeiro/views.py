# financeiro/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy # Para uso em redirecionamentos com sucesso
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum # Importado Sum para as agregações no relatório
from django.utils import timezone
from datetime import timedelta
import csv # Para exportação CSV
from django.http import HttpResponse

# Importe seus modelos financeiros
from .models import CategoriaFinanceira, FormaPagamento, ContaPagar, ContaReceber

# Importe seus formulários
from .forms import (
    ContaPagarForm, BaixaContaPagarForm, ContaReceberForm, BaixaContaReceberForm,
    RelatorioFinanceiroFilterForm # NOVO: Importar o formulário do relatório
)

# Importe seus filtros (django-filter)
from .filters import ContaPagarFilter, ContaReceberFilter

# Importe modelos de outros apps
from clientes.models import Cliente
from fornecedores.models import Fornecedor


# --- FUNÇÃO AUXILIAR PARA DETERMINAR A CLASSE DO BADGE ---
def _get_conta_badge_class(status):
    """
    Retorna a classe CSS do Bootstrap para o badge baseado no status da conta.
    Os status aqui devem corresponder aos do modelo ou aos status de exibição como 'VENCIDA'.
    """
    if status == 'PAGA' or status == 'RECEBIDA':
        return 'text-bg-success'
    elif status == 'VENCIDA': # Status de exibição derivado
        return 'text-bg-danger'
    elif status == 'CANCELADA':
        return 'text-bg-secondary'
    elif status == 'A_PAGAR' or status == 'A_RECEBER': # Status padrão para pendente
        return 'text-bg-warning text-dark'
    return 'text-bg-info' # Default para outros não mapeados


# --- VIEWS PARA CONTAS A PAGAR ---

@login_required
def listar_contas_pagar(request):
    contas_queryset = ContaPagar.objects.select_related(
        'categoria', 'fornecedor', 'forma_pagamento', 'registrado_por'
    ).order_by('-data_vencimento')

    conta_filter = ContaPagarFilter(request.GET, queryset=contas_queryset)
    contas_filtradas = conta_filter.qs.order_by('-data_vencimento', 'status')

    contas_para_exibir = []
    today = timezone.localdate()

    for conta in contas_filtradas:
        display_status = conta.status
        # A lógica para 'VENCIDA' aqui deve usar o status do modelo 'A_PAGAR'
        if display_status == 'A_PAGAR' and conta.data_vencimento and conta.data_vencimento < today:
            display_status = 'VENCIDA' # Altera o status para exibição
        
        conta.badge_class = _get_conta_badge_class(display_status)
        conta.display_status_text = 'Vencida' if display_status == 'VENCIDA' else conta.get_status_display()
        contas_para_exibir.append(conta)

    context = {
        'contas_pagar': contas_para_exibir,
        'filter': conta_filter,
        'title': 'Contas a Pagar',
        'active_page': 'contas_pagar',
        # 'VENCIDA' é um status de exibição, não um status de modelo para edição
        'statuses_nao_editaveis': ['PAGA', 'CANCELADA'], 
    }
    return render(request, 'financeiro/contas_pagar/listar_contas_pagar.html', context)

@login_required
def adicionar_conta_pagar(request):
    if request.method == 'POST':
        form = ContaPagarForm(request.POST)
        if form.is_valid():
            conta = form.save(commit=False)
            conta.registrado_por = request.user
            conta.save()
            messages.success(request, f'Conta a pagar "{conta.descricao}" adicionada com sucesso!')
            return redirect('financeiro:listar_contas_pagar')
        else:
            messages.error(request, 'Erro ao adicionar conta a pagar. Verifique os campos.')
    else:
        form = ContaPagarForm()
        form.fields['data_lancamento'].initial = timezone.localdate()

    context = {
        'form': form,
        'title': 'Adicionar Conta a Pagar',
        'active_page': 'contas_pagar',
    }
    return render(request, 'financeiro/contas_pagar/adicionar_conta_pagar.html', context)


@login_required
def editar_conta_pagar(request, pk):
    conta = get_object_or_404(ContaPagar.objects.select_related('fornecedor', 'categoria'), pk=pk)

    if conta.status in ['PAGA', 'CANCELADA']:
        messages.warning(request, f'Conta "{conta.descricao}" não pode ser editada pois está com status "{conta.get_status_display()}".')
        return redirect('financeiro:detalhar_conta_pagar', pk=pk)

    if request.method == 'POST':
        form = ContaPagarForm(request.POST, instance=conta)
        if form.is_valid():
            form.save()
            messages.success(request, f'Conta a pagar "{conta.descricao}" atualizada com sucesso!')
            return redirect('financeiro:listar_contas_pagar')
        else:
            messages.error(request, 'Erro ao atualizar conta a pagar. Verifique os campos.')
    else:
        form = ContaPagarForm(instance=conta)

    context = {
        'form': form,
        'conta': conta,
        'title': 'Editar Conta a Pagar',
        'active_page': 'contas_pagar',
        'statuses_nao_editaveis': ['PAGA', 'CANCELADA'],
    }
    return render(request, 'financeiro/contas_pagar/editar_conta_pagar.html', context)


@login_required
def detalhar_conta_pagar(request, pk):
    conta = get_object_or_404(ContaPagar.objects.select_related('fornecedor', 'categoria'), pk=pk)

    today = timezone.localdate()
    display_status = conta.status
    if display_status == 'A_PAGAR' and conta.data_vencimento and conta.data_vencimento < today:
        display_status = 'VENCIDA'

    conta.badge_class = _get_conta_badge_class(display_status)
    if display_status == 'VENCIDA':
        conta.display_status_text = 'Vencida'
    else:
        conta.display_status_text = conta.get_status_display()

    context = {
        'conta': conta,
        'title': 'Detalhes da Conta a Pagar',
        'active_page': 'contas_pagar',
        'statuses_nao_editaveis': ['PAGA', 'CANCELADA'],
    }
    return render(request, 'financeiro/contas_pagar/detalhar_conta_pagar.html', context)


@login_required
def baixar_conta_pagar(request, pk):
    conta = get_object_or_404(ContaPagar.objects.select_related('fornecedor', 'categoria'), pk=pk)

    if conta.status == 'PAGA':
        messages.warning(request, f'A conta "{conta.descricao}" já está marcada como paga.')
        return redirect('financeiro:detalhar_conta_pagar', pk=pk)
    if conta.status == 'CANCELADA':
        messages.warning(request, f'A conta "{conta.descricao}" está cancelada e não pode ser baixada.')
        return redirect('financeiro:detalhar_conta_pagar', pk=pk)

    if request.method == 'POST':
        form = BaixaContaPagarForm(request.POST, instance=conta)
        if form.is_valid():
            conta = form.save(commit=False)
            conta.status = 'PAGA' # Altera o status para 'PAGA'
            conta.save()
            messages.success(request, f'Conta "{conta.descricao}" baixada (paga) com sucesso!')
            return redirect('financeiro:listar_contas_pagar')
        else:
            messages.error(request, 'Erro ao baixar conta. Verifique os campos.')
    else:
        form = BaixaContaPagarForm(instance=conta)

    context = {
        'form': form,
        'conta': conta,
        'title': 'Baixar Conta a Pagar',
        'active_page': 'contas_pagar',
        'statuses_nao_editaveis': ['PAGA', 'CANCELADA'],
    }
    return render(request, 'financeiro/contas_pagar/baixar_conta_pagar.html', context)


@login_required
def excluir_conta_pagar(request, pk):
    conta = get_object_or_404(ContaPagar.objects.select_related('fornecedor', 'categoria'), pk=pk)
    if request.method == 'POST':
        conta.delete()
        messages.success(request, f'Conta a pagar "{conta.descricao}" excluída com sucesso.')
        return redirect('financeiro:listar_contas_pagar')
    messages.error(request, 'A exclusão deve ser feita via POST.')
    return redirect('financeiro:listar_contas_pagar')


@login_required
def exportar_contas_pagar_csv(request):
    contas_queryset = ContaPagar.objects.all().select_related('fornecedor', 'categoria')
    conta_filter = ContaPagarFilter(request.GET, queryset=contas_queryset)
    contas_queryset_filtrado = conta_filter.qs

    contas_para_csv = []
    today = timezone.localdate()
    for conta in contas_queryset_filtrado.order_by('-data_vencimento', 'status'):
        display_status = conta.status
        if display_status == 'A_PAGAR' and conta.data_vencimento and conta.data_vencimento < today:
            display_status = 'VENCIDA'

        conta.display_status_text_csv = 'Vencida' if display_status == 'VENCIDA' else conta.get_status_display()
        contas_para_csv.append(conta)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="contas_a_pagar_{timezone.localdate()}.csv"'

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'Descricao', 'Valor', 'Data Lancamento', 'Data Vencimento', 'Data Pagamento',
        'Status', 'Categoria', 'Forma Pagamento', 'Fornecedor', 'Observacoes',
        'Registrado Por', 'Data Registro', 'Ultima Atualizacao'
    ])

    for conta in contas_para_csv:
        fornecedor_nome = ""
        if conta.fornecedor:
            fornecedor_nome = conta.fornecedor.razao_social if hasattr(conta.fornecedor, 'razao_social') else (conta.fornecedor.nome_fantasia if hasattr(conta.fornecedor, 'nome_fantasia') else '')

        registrado_por_nome = ""
        if conta.registrado_por:
            registrado_por_nome = conta.registrado_por.get_full_name() if conta.registrado_por.get_full_name() else conta.registrado_por.username

        writer.writerow([
            conta.descricao,
            f"{conta.valor:.2f}".replace('.', ','),
            conta.data_lancamento.strftime('%Y-%m-%d'),
            conta.data_vencimento.strftime('%Y-%m-%d'),
            conta.data_pagamento.strftime('%Y-%m-%d') if conta.data_pagamento else '',
            conta.display_status_text_csv,
            conta.categoria.nome if conta.categoria else '',
            conta.forma_pagamento.nome if conta.forma_pagamento else '',
            fornecedor_nome,
            conta.observacoes,
            registrado_por_nome,
            conta.data_registro.strftime('%Y-%m-%d %H:%M:%S'),
            conta.data_ultima_atualizacao.strftime('%Y-%m-%d %H:%M:%S')
        ])
    return response

# --- VIEWS PARA CONTAS A RECEBER ---

@login_required
def lista_contas_receber(request):
    contas = ContaReceber.objects.all()

    conta_filter = ContaReceberFilter(request.GET, queryset=contas)
    contas_filtradas = conta_filter.qs.order_by('-data_vencimento', 'status')

    contas_para_exibir = []
    today = timezone.localdate()

    for conta in contas_filtradas:
        display_status = conta.status
        # A lógica para 'VENCIDA' aqui deve usar o status do modelo 'A_RECEBER'
        if display_status == 'A_RECEBER' and conta.data_vencimento and conta.data_vencimento < today:
            display_status = 'VENCIDA'
        
        conta.badge_class = _get_conta_badge_class(display_status)
        conta.display_status_text = 'Vencida' if display_status == 'VENCIDA' else conta.get_status_display()
        contas_para_exibir.append(conta)

    context = {
        'contas_receber': contas_para_exibir,
        'filter': conta_filter,
        'title': 'Contas a Receber',
        'active_page': 'contas_receber',
        # 'VENCIDA' é um status de exibição, não um status de modelo para edição
        'statuses_nao_editaveis': ['RECEBIDA', 'CANCELADA'], 
    }

    return render(request, 'financeiro/contas_receber/lista_contas_receber.html', context)

@login_required
def nova_conta_receber(request):
    if request.method == 'POST':
        form = ContaReceberForm(request.POST)
        if form.is_valid():
            conta = form.save(commit=False)
            conta.registrado_por = request.user # Associa o usuário logado
            conta.save()
            messages.success(request, f'Conta a receber "{conta.descricao}" adicionada com sucesso!')
            return redirect('financeiro:lista_contas_receber')
        else:
            messages.error(request, 'Erro ao adicionar conta a receber. Verifique os campos.')
    else:
        form = ContaReceberForm()
        form.fields['data_lancamento'].initial = timezone.localdate() # Pré-preenche a data de lançamento

    context = {
        'form': form,
        'title': 'Nova Conta a Receber',
        'active_page': 'contas_receber',
    }
    return render(request, 'financeiro/contas_receber/conta_receber_form.html', context)


@login_required
def detalhar_conta_receber(request, pk):
    conta = get_object_or_404(ContaReceber.objects.select_related('cliente', 'categoria', 'forma_pagamento'), pk=pk)

    today = timezone.localdate()
    display_status = conta.status
    if display_status == 'A_RECEBER' and conta.data_vencimento and conta.data_vencimento < today:
        display_status = 'VENCIDA'

    conta.badge_class = _get_conta_badge_class(display_status)
    if display_status == 'VENCIDA':
        conta.display_status_text = 'Vencida'
    else:
        conta.display_status_text = conta.get_status_display()

    context = {
        'conta': conta,
        'title': 'Detalhes da Conta a Receber',
        'active_page': 'contas_receber',
        'statuses_nao_editaveis': ['RECEBIDA', 'CANCELADA'], # Status que não permitem edição/baixa
    }
    return render(request, 'financeiro/contas_receber/detalhar_conta_receber.html', context)


@login_required
def editar_conta_receber(request, pk):
    conta = get_object_or_404(ContaReceber.objects.select_related('cliente', 'categoria', 'forma_pagamento'), pk=pk)

    if conta.status in ['RECEBIDA', 'CANCELADA']:
        messages.warning(request, f'Conta "{conta.descricao}" não pode ser editada pois está com status "{conta.get_status_display()}".')
        return redirect('financeiro:detalhar_conta_receber', pk=pk)

    if request.method == 'POST':
        form = ContaReceberForm(request.POST, instance=conta)
        if form.is_valid():
            form.save()
            messages.success(request, f'Conta a receber "{conta.descricao}" atualizada com sucesso!')
            return redirect('financeiro:lista_contas_receber')
        else:
            messages.error(request, 'Erro ao atualizar conta a receber. Verifique os campos.')
    else:
        form = ContaReceberForm(instance=conta)

    context = {
        'form': form,
        'conta': conta,
        'title': 'Editar Conta a Receber',
        'active_page': 'contas_receber',
        'statuses_nao_editaveis': ['RECEBIDA', 'CANCELADA'],
    }
    return render(request, 'financeiro/contas_receber/conta_receber_form.html', context)


@login_required
def baixar_conta_receber(request, pk):
    conta = get_object_or_404(ContaReceber.objects.select_related('cliente', 'categoria', 'forma_pagamento'), pk=pk)

    if conta.status == 'RECEBIDA':
        messages.warning(request, f'A conta "{conta.descricao}" já está marcada como recebida.')
        return redirect('financeiro:detalhar_conta_receber', pk=pk)
    if conta.status == 'CANCELADA':
        messages.warning(request, f'A conta "{conta.descricao}" está cancelada e não pode ser baixada.')
        return redirect('financeiro:detalhar_conta_receber', pk=pk)

    if request.method == 'POST':
        form = BaixaContaReceberForm(request.POST, instance=conta)
        if form.is_valid():
            conta = form.save(commit=False)
            conta.status = 'RECEBIDA' # Altera o status para 'RECEBIDA'
            conta.save()
            messages.success(request, f'Conta "{conta.descricao}" baixada (recebida) com sucesso!')
            return redirect('financeiro:lista_contas_receber')
        else:
            messages.error(request, 'Erro ao baixar conta. Verifique os campos.')
    else:
        form = BaixaContaReceberForm(instance=conta)
        form.fields['data_recebimento'].initial = timezone.localdate()

    context = {
        'form': form,
        'conta': conta,
        'title': 'Baixar Conta a Receber',
        'active_page': 'contas_receber',
        'statuses_nao_editaveis': ['RECEBIDA', 'CANCELADA'],
    }
    return render(request, 'financeiro/contas_receber/baixar_conta_receber.html', context)


@login_required
def excluir_conta_receber(request, pk):
    conta = get_object_or_404(ContaReceber, pk=pk)
    if request.method == 'POST':
        conta.delete()
        messages.success(request, f'Conta a receber "{conta.descricao}" excluída com sucesso.')
        return redirect('financeiro:lista_contas_receber')
    
    messages.error(request, 'A exclusão deve ser feita via POST.')
    return redirect('financeiro:lista_contas_receber')

# --- Exportação CSV para Contas a Receber (Opcional, similar a Contas a Pagar) ---
@login_required
def exportar_contas_receber_csv(request):
    contas_queryset = ContaReceber.objects.all().select_related('cliente', 'categoria', 'forma_pagamento')
    conta_filter = ContaReceberFilter(request.GET, queryset=contas_queryset)
    contas_queryset_filtrado = conta_filter.qs

    contas_para_csv = []
    today = timezone.localdate()
    for conta in contas_queryset_filtrado.order_by('-data_vencimento', 'status'):
        display_status = conta.status
        if display_status == 'A_RECEBER' and conta.data_vencimento and conta.data_vencimento < today:
            display_status = 'VENCIDA'

        conta.display_status_text_csv = 'Vencida' if display_status == 'VENCIDA' else conta.get_status_display()
        contas_para_csv.append(conta)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="contas_a_receber_{timezone.localdate()}.csv"'

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'Descricao', 'Valor', 'Data Lancamento', 'Data Vencimento', 'Data Recebimento',
        'Status', 'Categoria', 'Forma Recebimento', 'Cliente', 'Observacoes',
        'Registrado Por', 'Data Registro', 'Ultima Atualizacao'
    ])

    for conta in contas_para_csv:
        cliente_nome = ""
        if conta.cliente:
            cliente_nome = conta.cliente.razao_social if hasattr(conta.cliente, 'razao_social') else (conta.cliente.nome_fantasia if hasattr(conta.cliente, 'nome_fantasia') else '')

        registrado_por_nome = ""
        if conta.registrado_por:
            registrado_por_nome = conta.registrado_por.get_full_name() if conta.registrado_por.get_full_name() else conta.registrado_por.username

        writer.writerow([
            conta.descricao,
            f"{conta.valor:.2f}".replace('.', ','),
            conta.data_lancamento.strftime('%Y-%m-%d'),
            conta.data_vencimento.strftime('%Y-%m-%d'),
            conta.data_recebimento.strftime('%Y-%m-%d') if conta.data_recebimento else '',
            conta.display_status_text_csv,
            conta.categoria.nome if conta.categoria else '',
            conta.forma_pagamento.nome if conta.forma_pagamento else '',
            cliente_nome,
            conta.observacoes,
            registrado_por_nome,
            conta.data_registro.strftime('%Y-%m-%d %H:%M:%S'),
            conta.data_ultima_atualizacao.strftime('%Y-%m-%d %H:%M:%S')
        ])
    return response


## Relatório Financeiro (Novo)

@login_required
def relatorio_financeiro(request):
    form = RelatorioFinanceiroFilterForm(request.GET)
    
    # Inicializa querysets vazios para evitar erros se nenhum filtro for aplicado
    contas_pagar_filtradas = [] 
    contas_receber_filtradas = [] 

    # Inicializa os totais
    total_a_pagar_pendente_exibido = 0 # Valor das contas a pagar A_PAGAR (não vencidas) exibidas
    total_a_pagar_vencidas_exibido = 0 # Valor das contas a pagar A_PAGAR (vencidas) exibidas
    total_a_receber_pendente_exibido = 0 # Valor das contas a receber A_RECEBER (não vencidas) exibidas
    total_a_receber_vencidas_exibido = 0 # Valor das contas a receber A_RECEBER (vencidas) exibidas
    
    total_pago_no_periodo = 0
    total_recebido_no_periodo = 0
    
    saldo_projetado_geral = 0 # Saldo geral de todas as contas A_PAGAR e A_RECEBER (não filtrado por data)
    saldo_realizado_geral = 0 # Saldo geral de todas as contas PAGA e RECEBIDA (não filtrado por data)

    # Função auxiliar para badges, passada para o template
    context_badge_class = _get_conta_badge_class 

    if form.is_valid():
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        tipo_conta = form.cleaned_data.get('tipo_conta')
        categoria_filtro = form.cleaned_data.get('categoria') 
        status_geral = form.cleaned_data.get('status_geral')
        fornecedor_filtro = form.cleaned_data.get('fornecedor') 
        cliente_filtro = form.cleaned_data.get('cliente') 
        search_query = form.cleaned_data.get('search_query')

        today = timezone.localdate()

        # --- Lógica de filtragem para Contas a Pagar ---
        if tipo_conta in ('', 'pagar'):
            qs_pagar = ContaPagar.objects.select_related('categoria', 'fornecedor', 'forma_pagamento')

            # Filtros de data de vencimento para a listagem principal
            if data_inicio:
                qs_pagar = qs_pagar.filter(data_vencimento__gte=data_inicio)
            if data_fim:
                qs_pagar = qs_pagar.filter(data_vencimento__lte=data_fim)
            
            # Filtro de categoria
            if categoria_filtro:
                qs_pagar = qs_pagar.filter(categoria=categoria_filtro)
            
            # Filtro de status geral para contas a pagar
            if status_geral:
                if status_geral == 'realizado':
                    qs_pagar = qs_pagar.filter(status='PAGA')
                elif status_geral == 'pendente':
                    qs_pagar = qs_pagar.filter(status='A_PAGAR')
                elif status_geral == 'cancelado':
                    qs_pagar = qs_pagar.filter(status='CANCELADA')
                elif status_geral == 'vencida':
                    qs_pagar = qs_pagar.filter(status='A_PAGAR', data_vencimento__lt=today)
            
            # Filtro de fornecedor
            if fornecedor_filtro:
                qs_pagar = qs_pagar.filter(fornecedor=fornecedor_filtro)

            # Filtro de busca geral
            if search_query:
                qs_pagar = qs_pagar.filter(
                    Q(descricao__icontains=search_query) | Q(observacoes__icontains=search_query)
                )
            
            contas_pagar_filtradas_raw = list(qs_pagar.order_by('data_vencimento')) 

            # Processar o status de exibição e badge_class para cada conta
            contas_pagar_processadas = []
            for conta in contas_pagar_filtradas_raw:
                display_status = conta.status
                if display_status == 'A_PAGAR' and conta.data_vencimento and conta.data_vencimento < today:
                    display_status = 'VENCIDA'
                
                conta.badge_class = _get_conta_badge_class(display_status)
                conta.display_status_text = 'Vencida' if display_status == 'VENCIDA' else conta.get_status_display()
                contas_pagar_processadas.append(conta)
            
            contas_pagar_filtradas = contas_pagar_processadas # Atribui a lista processada

            # Cálculos para Totais de Contas a Pagar exibidas na tabela
            total_a_pagar_pendente_exibido = sum(c.valor for c in contas_pagar_filtradas if c.status == 'A_PAGAR' and c.data_vencimento >= today)
            total_a_pagar_vencidas_exibido = sum(c.valor for c in contas_pagar_filtradas if c.display_status_text == 'Vencida')

            # Total PAGO no período (usa data_pagamento e os filtros aplicados)
            total_pago_qs = ContaPagar.objects.filter(status='PAGA')
            if data_inicio:
                total_pago_qs = total_pago_qs.filter(data_pagamento__gte=data_inicio)
            if data_fim:
                total_pago_qs = total_pago_qs.filter(data_pagamento__lte=data_fim)
            if categoria_filtro:
                total_pago_qs = total_pago_qs.filter(categoria=categoria_filtro)
            if fornecedor_filtro:
                total_pago_qs = total_pago_qs.filter(fornecedor=fornecedor_filtro)
            if search_query:
                total_pago_qs = total_pago_qs.filter(Q(descricao__icontains=search_query) | Q(observacoes__icontains=search_query))
            
            total_pago_no_periodo = total_pago_qs.aggregate(Sum('valor'))['valor__sum'] or 0


        # --- Lógica de filtragem para Contas a Receber ---
        if tipo_conta in ('', 'receber'):
            qs_receber = ContaReceber.objects.select_related('categoria', 'cliente', 'forma_pagamento')

            # Filtros de data de vencimento para a listagem principal
            if data_inicio:
                qs_receber = qs_receber.filter(data_vencimento__gte=data_inicio)
            if data_fim:
                qs_receber = qs_receber.filter(data_vencimento__lte=data_fim)
            
            # Filtro de categoria
            if categoria_filtro:
                qs_receber = qs_receber.filter(categoria=categoria_filtro)
            
            # Filtro de status geral para contas a receber
            if status_geral:
                if status_geral == 'realizado':
                    qs_receber = qs_receber.filter(status='RECEBIDA')
                elif status_geral == 'pendente':
                    qs_receber = qs_receber.filter(status='A_RECEBER')
                elif status_geral == 'cancelado':
                    qs_receber = qs_receber.filter(status='CANCELADA')
                elif status_geral == 'vencida':
                    qs_receber = qs_receber.filter(status='A_RECEBER', data_vencimento__lt=today)
            
            # Filtro de cliente
            if cliente_filtro:
                qs_receber = qs_receber.filter(cliente=cliente_filtro)
            
            # Filtro de busca geral
            if search_query:
                qs_receber = qs_receber.filter(
                    Q(descricao__icontains=search_query) | Q(observacoes__icontains=search_query)
                )

            contas_receber_filtradas_raw = list(qs_receber.order_by('data_vencimento'))

            # Processar o status de exibição e badge_class para cada conta
            contas_receber_processadas = []
            for conta in contas_receber_filtradas_raw:
                display_status = conta.status
                if display_status == 'A_RECEBER' and conta.data_vencimento and conta.data_vencimento < today:
                    display_status = 'VENCIDA'
                
                conta.badge_class = _get_conta_badge_class(display_status)
                conta.display_status_text = 'Vencida' if display_status == 'VENCIDA' else conta.get_status_display()
                contas_receber_processadas.append(conta)
            
            contas_receber_filtradas = contas_receber_processadas # Atribui a lista processada

            # Cálculos para Totais de Contas a Receber exibidas na tabela
            total_a_receber_pendente_exibido = sum(c.valor for c in contas_receber_filtradas if c.status == 'A_RECEBER' and c.data_vencimento >= today)
            total_a_receber_vencidas_exibido = sum(c.valor for c in contas_receber_filtradas if c.display_status_text == 'Vencida')

            # Total RECEBIDO no período (usa data_recebimento e os filtros aplicados)
            total_recebido_qs = ContaReceber.objects.filter(status='RECEBIDA')
            if data_inicio:
                total_recebido_qs = total_recebido_qs.filter(data_recebimento__gte=data_inicio)
            if data_fim:
                total_recebido_qs = total_recebido_qs.filter(data_recebimento__lte=data_fim)
            if categoria_filtro:
                total_recebido_qs = total_recebido_qs.filter(categoria=categoria_filtro)
            if cliente_filtro:
                total_recebido_qs = total_recebido_qs.filter(cliente=cliente_filtro)
            if search_query:
                total_recebido_qs = total_recebido_qs.filter(Q(descricao__icontains=search_query) | Q(observacoes__icontains=search_query))
            
            total_recebido_no_periodo = total_recebido_qs.aggregate(Sum('valor'))['valor__sum'] or 0

    # Cálculos de Saldo Geral (independentes dos filtros de exibição na tabela,
    # mas dependentes dos filtros de tipo de conta e categoria/fornecedor/cliente)
    
    # Saldo Projetado Geral: Soma de todas as contas A_RECEBER menos todas as contas A_PAGAR
    # Considera todos os filtros aplicados, exceto o status_geral para 'realizado' ou 'vencida'
    # pois queremos o total de 'pendentes' e 'a vencer'
    
    # Querysets base para saldo projetado (ignora status 'PAGA', 'RECEBIDA', 'CANCELADA')
    qs_saldo_pagar = ContaPagar.objects.filter(status='A_PAGAR')
    qs_saldo_receber = ContaReceber.objects.filter(status='A_RECEBER')

    # Aplica filtros de categoria, fornecedor/cliente e busca geral aos saldos projetados
    if categoria_filtro:
        qs_saldo_pagar = qs_saldo_pagar.filter(categoria=categoria_filtro)
        qs_saldo_receber = qs_saldo_receber.filter(categoria=categoria_filtro)
    if fornecedor_filtro:
        qs_saldo_pagar = qs_saldo_pagar.filter(fornecedor=fornecedor_filtro)
    if cliente_filtro:
        qs_saldo_receber = qs_saldo_receber.filter(cliente=cliente_filtro)
    if search_query:
        qs_saldo_pagar = qs_saldo_pagar.filter(Q(descricao__icontains=search_query) | Q(observacoes__icontains=search_query))
        qs_saldo_receber = qs_saldo_receber.filter(Q(descricao__icontains=search_query) | Q(observacoes__icontains=search_query))

    total_a_pagar_para_saldo_geral = 0
    total_a_receber_para_saldo_geral = 0

    if tipo_conta in ('', 'pagar'):
        total_a_pagar_para_saldo_geral = qs_saldo_pagar.aggregate(Sum('valor'))['valor__sum'] or 0
    if tipo_conta in ('', 'receber'):
        total_a_receber_para_saldo_geral = qs_saldo_receber.aggregate(Sum('valor'))['valor__sum'] or 0

    saldo_projetado_geral = total_a_receber_para_saldo_geral - total_a_pagar_para_saldo_geral
    
    # Saldo Realizado Geral: Soma de todas as contas RECEBIDA menos todas as contas PAGA
    # Considera todos os filtros aplicados, exceto o status_geral para 'pendente' ou 'vencida'
    
    # Querysets base para saldo realizado (ignora status 'A_PAGAR', 'A_RECEBER', 'CANCELADA')
    qs_saldo_pago = ContaPagar.objects.filter(status='PAGA')
    qs_saldo_recebido = ContaReceber.objects.filter(status='RECEBIDA')

    # Aplica filtros de categoria, fornecedor/cliente e busca geral aos saldos realizados
    if categoria_filtro:
        qs_saldo_pago = qs_saldo_pago.filter(categoria=categoria_filtro)
        qs_saldo_recebido = qs_saldo_recebido.filter(categoria=categoria_filtro)
    if fornecedor_filtro:
        qs_saldo_pago = qs_saldo_pago.filter(fornecedor=fornecedor_filtro)
    if cliente_filtro:
        qs_saldo_recebido = qs_saldo_recebido.filter(cliente=cliente_filtro)
    if search_query:
        qs_saldo_pago = qs_saldo_pago.filter(Q(descricao__icontains=search_query) | Q(observacoes__icontains=search_query))
        qs_saldo_recebido = qs_saldo_recebido.filter(Q(descricao__icontains=search_query) | Q(observacoes__icontains=search_query))

    total_pago_para_saldo_geral = 0
    total_recebido_para_saldo_geral = 0

    if tipo_conta in ('', 'pagar'):
        total_pago_para_saldo_geral = qs_saldo_pago.aggregate(Sum('valor'))['valor__sum'] or 0
    if tipo_conta in ('', 'receber'):
        total_recebido_para_saldo_geral = qs_saldo_recebido.aggregate(Sum('valor'))['valor__sum'] or 0

    saldo_realizado_geral = total_recebido_para_saldo_geral - total_pago_para_saldo_geral


    # Preparar o contexto para o template
    context = {
        'title': 'Relatório Financeiro',
        'form': form,
        'contas_pagar': contas_pagar_filtradas, # Passa as contas já processadas para exibição
        'contas_receber': contas_receber_filtradas, # Passa as contas já processadas para exibição
        
        # Totais para exibição na tabela (baseados nos filtros de data de vencimento)
        'total_a_pagar_pendente_exibido': total_a_pagar_pendente_exibido,
        'total_a_pagar_vencidas_exibido': total_a_pagar_vencidas_exibido,
        'total_a_receber_pendente_exibido': total_a_receber_pendente_exibido,
        'total_a_receber_vencidas_exibido': total_a_receber_vencidas_exibido,
        
        # Totais de Pagos/Recebidos no período (baseados nas datas de pagamento/recebimento)
        'total_pago_no_periodo': total_pago_no_periodo,
        'total_recebido_no_periodo': total_recebido_no_periodo,
        
        # Saldos gerais (consideram todos os dados, filtrados apenas por tipo de conta e categoria/fornecedor/cliente)
        'saldo_projetado_geral': saldo_projetado_geral,
        'saldo_realizado_geral': saldo_realizado_geral,
        
        'active_page': 'financeiro_relatorio', # Para o menu de navegação
        'get_conta_badge_class': context_badge_class, # Função para badges no template
    }
    return render(request, 'financeiro/relatorios/relatorio_financeiro.html', context)