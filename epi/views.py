# pat/epi/views.py

import io
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
# from django.views.decorators.csrf import csrf_exempt # Remova ou use com CAUTELA, preferindo métodos seguros
from xhtml2pdf import pisa
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta, date # Importe date, é útil para comparação com timezone.now().date()
from django.db import transaction # Importar transaction para atomicidade
from django.core.paginator import Paginator

# --- Importações de Views Genéricas e URLs ---
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy # Necessário para redirecionamento em CBVs

# Importa os modelos do próprio app 'epi'
from .models import (
    EPI, TipoEPI, ColaboradorEPI, EntradaEPI, SaidaEPI,
)

# Importa modelos de absenteísmo e RH do app 'rh'
from rh.models import (
    TipoAbsenteismo, RegistroAbsenteismoDiario, # Ajustado o nome do modelo de registro de absenteísmo
    TipoContrato, Lider, Cargo # Importe os modelos de RH aqui, pois ColaboradorEPI os referencia (via ForeignKey)
)

# Importe os formulários RENOMEADOS (ColaboradorForm -> ColaboradorEPIForm)
from .forms import (
    TipoEPIForm, EPIForm, ColaboradorEPIForm, 
    EntradaEPIForm, SaidaEPIForm,
    EPIFilterForm, ColaboradorEPIFilterForm, EntradaSaidaFilterForm, 
    TipoAbsenteismoForm, RegistroAbsenteismoForm, # Este é o FORM, não o MODELO. Ele usa RegistroAbsenteismoDiario internamente.
    RegistroDiarioAbsenteismoFormSet,
)

from django.core.files.base import ContentFile
import base64


# --- VIEWS PARA EPI ---

@login_required
def listar_epis(request):
    epis = EPI.objects.all()
    filter_form = EPIFilterForm(request.GET)

    if filter_form.is_valid():
        search_query = filter_form.cleaned_data.get('search_query')
        tipo_epi = filter_form.cleaned_data.get('tipo_epi')
        ca_vencido_filter = filter_form.cleaned_data.get('ca_vencido')
        ativo = filter_form.cleaned_data.get('ativo')

        if search_query:
            epis = epis.filter(
                Q(nome__icontains=search_query) |
                Q(ca__icontains=search_query) |
                Q(fabricante__icontains=search_query) |
                Q(modelo__icontains=search_query)
            )
        if tipo_epi:
            epis = epis.filter(tipo_epi=tipo_epi)

        if ca_vencido_filter is not None and ca_vencido_filter != '':
            today = timezone.now().date()
            if ca_vencido_filter == 'True':
                epis = epis.filter(validade_ca__lt=today)
            elif ca_vencido_filter == 'False':
                epis = epis.filter(Q(validade_ca__gte=today) | Q(validade_ca__isnull=True))

        if ativo is not None and ativo != '':
            if ativo == 'True':
                epis = epis.filter(ativo=True)
            elif ativo == 'False':
                epis = epis.filter(ativo=False)

    epis = epis.order_by('nome')

    # Paginação
    paginator = Paginator(epis, 10)  # Ajuste o número de itens por página aqui (ex: 10)
    page_number = request.GET.get('page')
    epis_page = paginator.get_page(page_number)

    context = {
        'epis': epis_page,
        'filter_form': filter_form,
        'active_page': 'epis',
    }
    return render(request, 'epi/listar_epis.html', context)


@login_required
def adicionar_epi(request):
    if request.method == 'POST':
        form = EPIForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'EPI "{form.instance.nome}" (CA: {form.instance.ca}) adicionado com sucesso!')
            return redirect('listar_epis')
        else:
            messages.error(request, 'Erro ao adicionar EPI. Verifique os campos.')
    else:
        form = EPIForm()

    context = {
        'form': form,
        'active_page': 'epis_adicionar',
    }
    return render(request, 'epi/adicionar_epi.html', context)

@login_required
def editar_epi(request, pk):
    epi = get_object_or_404(EPI, pk=pk)
    if request.method == 'POST':
        form = EPIForm(request.POST, instance=epi)
        if form.is_valid():
            form.save()
            messages.success(request, f'EPI "{epi.nome}" (CA: {epi.ca}) atualizado com sucesso!')
            return redirect('listar_epis')
        else:
            messages.error(request, 'Erro ao atualizar EPI. Verifique os campos.')
    else:
        form = EPIForm(instance=epi)

    context = {
        'form': form,
        'epi': epi,
        'active_page': 'epis',
    }
    return render(request, 'epi/editar_epi.html', context)

@login_required
def excluir_epi(request, pk):
    epi = get_object_or_404(EPI, pk=pk)
    if request.method == 'POST':
        nome_epi = epi.nome
        ca_epi = epi.ca
        epi.delete()
        messages.success(request, f'EPI "{nome_epi}" (CA: {ca_epi}) excluído com sucesso.')
    return redirect('listar_epis')


# --- VIEWS PARA TIPO DE EPI ---

@login_required
def listar_tipos_epi(request):
    tipos_epi = TipoEPI.objects.all().order_by('nome')
    context = {
        'tipos_epi': tipos_epi,
        'active_page': 'tipos_epi',
    }
    return render(request, 'epi/listar_tipos_epi.html', context)

@login_required
def adicionar_tipo_epi(request):
    if request.method == 'POST':
        form = TipoEPIForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tipo de EPI "{form.instance.nome}" adicionado com sucesso!')
            return redirect('listar_tipos_epi')
        else:
            messages.error(request, 'Erro ao adicionar Tipo de EPI. Verifique os campos.')
    else:
        form = TipoEPIForm()
    context = {
        'form': form,
        'active_page': 'tipos_epi',
    }
    return render(request, 'epi/adicionar_tipo_epi.html', context)

@login_required
def editar_tipo_epi(request, pk):
    tipo_epi = get_object_or_404(TipoEPI, pk=pk)
    if request.method == 'POST':
        form = TipoEPIForm(request.POST, instance=tipo_epi)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tipo de EPI "{tipo_epi.nome}" atualizado com sucesso!')
            return redirect('listar_tipos_epi')
        else:
            messages.error(request, 'Erro ao atualizar Tipo de EPI. Verifique os campos.')
    else:
        form = TipoEPIForm(instance=tipo_epi)
    context = {
        'form': form,
        'tipo_epi': tipo_epi,
        'active_page': 'tipos_epi',
    }
    return render(request, 'epi/editar_tipo_epi.html', context)

@login_required
def excluir_tipo_epi(request, pk):
    tipo_epi = get_object_or_404(TipoEPI, pk=pk)
    if request.method == 'POST':
        nome_tipo = tipo_epi.nome
        tipo_epi.delete()
        messages.success(request, f'Tipo de EPI "{nome_tipo}" excluído com sucesso.')
    return redirect('listar_tipos_epi')


# --- VIEWS PARA COLABORADOR (AGORA ColaboradorEPI) ---

@login_required
def listar_colaboradores(request): # <--- Nome da função pode ser renomeado para listar_colaboradores_epi
    colaboradores = ColaboradorEPI.objects.all() # <--- RENOMEADO
    filter_form = ColaboradorEPIFilterForm(request.GET) # <--- RENOMEADO

    if filter_form.is_valid():
        search_query = filter_form.cleaned_data.get('search_query')
        ativo = filter_form.cleaned_data.get('ativo')

        if search_query:
            colaboradores = colaboradores.filter(
                Q(nome_completo__icontains=search_query) |
                Q(matricula__icontains=search_query) |
                Q(cpf__icontains=search_query)
            )
        if ativo is not None and ativo != '':
            if ativo == 'True':
                colaboradores = colaboradores.filter(ativo=True)
            elif ativo == 'False':
                colaboradores = colaboradores.filter(ativo=False)

    colaboradores = colaboradores.order_by('nome_completo')
    context = {
        'colaboradores': colaboradores,
        'filter_form': filter_form,
        'active_page': 'colaboradores', # <--- Pode ser 'colaboradores_epi' para clareza
    }
    return render(request, 'epi/listar_colaboradores.html', context) # <--- O template também pode ser renomeado


@login_required
def adicionar_colaborador(request): # <--- Nome da função pode ser renomeado para adicionar_colaborador_epi
    if request.method == 'POST':
        form = ColaboradorEPIForm(request.POST, request.FILES) # <--- RENOMEADO
        if form.is_valid():
            colaborador = form.save()
            messages.success(request, f'Colaborador "{colaborador.nome_completo}" adicionado com sucesso!')
            return redirect('listar_colaboradores') # <--- Mudar para 'listar_colaboradores_epi'
        else:
            messages.error(request, 'Erro ao adicionar colaborador. Verifique os campos.')
    else:
        form = ColaboradorEPIForm() # <--- RENOMEADO
    return render(request, 'epi/adicionar_colaborador.html', {'form': form}) # <--- O template também pode ser renomeado


@login_required
def editar_colaborador(request, pk): # <--- Nome da função pode ser renomeado para editar_colaborador_epi
    colaborador = get_object_or_404(ColaboradorEPI, pk=pk) # <--- RENOMEADO
    if request.method == 'POST':
        form = ColaboradorEPIForm(request.POST, request.FILES, instance=colaborador) # <--- RENOMEADO
        if form.is_valid():
            colaborador = form.save()
            messages.success(request, f'Colaborador "{colaborador.nome_completo}" atualizado com sucesso!')
            return redirect('listar_colaboradores') # <--- Mudar para 'listar_colaboradores_epi'
        else:
            messages.error(request, 'Erro ao atualizar colaborador. Verifique os campos.')
    else:
        form = ColaboradorEPIForm(instance=colaborador) # <--- RENOMEADO
    return render(request, 'epi/editar_colaborador.html', {'form': form}) # <--- O template também pode ser renomeado


@login_required
def excluir_colaborador(request, pk): # <--- Nome da função pode ser renomeado para excluir_colaborador_epi
    colaborador = get_object_or_404(ColaboradorEPI, pk=pk) # <--- RENOMEADO
    if request.method == 'POST':
        nome_completo = colaborador.nome_completo
        colaborador.delete()
        messages.success(request, f'Colaborador "{nome_completo}" excluído com sucesso.')
    return redirect('listar_colaboradores') # <--- Mudar para 'listar_colaboradores_epi'


# --- VIEWS PARA ENTRADA DE EPI ---

@login_required
def listar_entradas_epi(request):
    entradas_epi = EntradaEPI.objects.all()
    filter_form = EntradaSaidaFilterForm(request.GET)

    if filter_form.is_valid():
        epi = filter_form.cleaned_data.get('epi')
        data_inicio = filter_form.cleaned_data.get('data_inicio')
        data_fim = filter_form.cleaned_data.get('data_fim')

        if epi:
            entradas_epi = entradas_epi.filter(epi=epi)
        if data_inicio:
            entradas_epi = entradas_epi.filter(data_entrada__gte=data_inicio)
        if data_fim:
            entradas_epi = entradas_epi.filter(data_entrada__lte=data_fim)

    entradas_epi = entradas_epi.order_by('-data_entrada')
    context = {
        'entradas_epi': entradas_epi,
        'filter_form': filter_form,
        'active_page': 'entradas_epi',
    }
    return render(request, 'epi/listar_entradas_epi.html', context)

@login_required
def adicionar_entrada_epi(request):
    if request.method == 'POST':
        form = EntradaEPIForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Entrada de {form.instance.quantidade}x "{form.instance.epi.nome}" registrada com sucesso!')
            return redirect('listar_entradas_epi')
        else:
            messages.error(request, 'Erro ao registrar entrada de EPI. Verifique os campos.')
    else:
        form = EntradaEPIForm()
    context = {
        'form': form,
        'active_page': 'entradas_epi',
    }
    return render(request, 'epi/adicionar_entrada_epi.html', context)

@login_required
def editar_entrada_epi(request, pk):
    entrada_epi = get_object_or_404(EntradaEPI, pk=pk)
    if request.method == 'POST':
        form = EntradaEPIForm(request.POST, instance=entrada_epi)
        if form.is_valid():
            form.save()
            messages.success(request, f'Entrada de {entrada_epi.quantidade}x "{entrada_epi.epi.nome}" atualizada com sucesso!')
            return redirect('listar_entradas_epi')
        else:
            messages.error(request, 'Erro ao atualizar entrada de EPI. Verifique os campos.')
    else:
        form = EntradaEPIForm(instance=entrada_epi)
    context = {
        'form': form,
        'entrada_epi': entrada_epi,
        'active_page': 'entradas_epi',
    }
    return render(request, 'epi/editar_entrada_epi.html', context)

@login_required
def excluir_entrada_epi(request, pk):
    entrada_epi = get_object_or_404(EntradaEPI, pk=pk)
    if request.method == 'POST':
        info_entrada = f'{entrada_epi.quantidade}x "{entrada_epi.epi.nome}"'
        entrada_epi.delete()
        messages.success(request, f'Entrada de {info_entrada} excluída com sucesso.')
    return redirect('listar_entradas_epi')


# --- VIEWS PARA SAÍDA DE EPI ---

@login_required
def listar_saidas_epi(request):
    saidas_epi = SaidaEPI.objects.all()
    filter_form = EntradaSaidaFilterForm(request.GET)

    if filter_form.is_valid():
        epi = filter_form.cleaned_data.get('epi')
        colaborador = filter_form.cleaned_data.get('colaborador') # Este é um ColaboradorEPI
        data_inicio = filter_form.cleaned_data.get('data_inicio')
        data_fim = filter_form.cleaned_data.get('data_fim')

        if epi:
            saidas_epi = saidas_epi.filter(epi=epi)
        if colaborador:
            saidas_epi = saidas_epi.filter(colaborador=colaborador)
        if data_inicio:
            saidas_epi = saidas_epi.filter(data_saida__gte=data_inicio)
        if data_fim:
            saidas_epi = saidas_epi.filter(data_saida__lte=data_fim)

    saidas_epi = saidas_epi.order_by('-data_saida')
    context = {
        'saidas_epi': saidas_epi,
        'filter_form': filter_form,
        'active_page': 'saidas_epi',
    }
    return render(request, 'epi/listar_saidas_epi.html', context)

@login_required
def adicionar_saida_epi(request):
    if request.method == 'POST':
        form = SaidaEPIForm(request.POST, request.FILES) # Passar request.FILES
        # print(f"DEBUG: Request POST: {request.POST}") # Depuração
        # print(f"DEBUG: Request FILES: {request.FILES}") # Depuração

        if form.is_valid():
            saida = form.save(commit=False)

            # Lida com a assinatura digital se ela for enviada como base64
            assinatura_digital_base64 = request.POST.get('assinatura_digital_base64_hidden') # Campo oculto
            if assinatura_digital_base64 and assinatura_digital_base64.startswith('data:image'):
                format, imgstr = assinatura_digital_base64.split(';base64,')
                ext = format.split('/')[-1]
                # Usa 'temp' no nome do arquivo porque saida.pk ainda não existe
                # O nome final será ajustado pelos signals após o save() principal
                saida.assinatura_digital.save(f'assinatura_temp.{ext}', ContentFile(base64.b64decode(imgstr)), save=False)
                # print(f"DEBUG: Assinatura Base64 processada. Caminho planejado: {saida.assinatura_digital.name}") # Depuração
            # else:
                # print("DEBUG: Assinatura Base64 NÃO encontrada ou inválida.")
                # Validação de estoque antes de salvar
            if saida.quantidade > saida.epi.estoque_atual:
                messages.error(request, f'Estoque insuficiente para {saida.epi.nome}. Disponível: {saida.epi.estoque_atual}, Solicitado: {saida.quantidade}.')
                # print("DEBUG: Estoque insuficiente. Não salvando.") # Depuração
            else:
                saida.save() # Salva a SaidaEPI e as mídias (assinatura e PDF)
                # print(f"DEBUG: SaidaEPI salva com PK: {saida.pk}. Assinatura salva em: {saida.assinatura_digital.url if saida.assinatura_digital else 'N/A'}. PDF salvo em: {saida.pdf_documento.url if saida.pdf_documento else 'N/A'}") # Depuração
                messages.success(request, f'Saída de {saida.quantidade}x "{saida.epi.nome}" para "{saida.colaborador.nome_completo}" registrada com sucesso!')
                return redirect('listar_saidas_epi')
        else:
            # print(f"DEBUG: Form inválido. Erros: {form.errors}") # Depuração
            messages.error(request, 'Erro ao registrar saída de EPI. Verifique os campos.')
    else:
        form = SaidaEPIForm()
    context = {
        'form': form,
        'active_page': 'saidas_epi',
    }
    return render(request, 'epi/adicionar_saida_epi.html', context)

@login_required
def editar_saida_epi(request, pk):
    saida_epi = get_object_or_404(SaidaEPI, pk=pk)
    if request.method == 'POST':
        form = SaidaEPIForm(request.POST, request.FILES, instance=saida_epi)
        if form.is_valid():
            nova_quantidade = form.cleaned_data['quantidade']
            epi_selecionado = form.cleaned_data['epi']

            estoque_sem_esta_saida = epi_selecionado.estoque_atual + saida_epi.quantidade

            if nova_quantidade > estoque_sem_esta_saida:
                messages.error(request, f'Estoque insuficiente para atualizar a saída. Disponível sem esta saída: {estoque_sem_esta_saida}, Nova quantidade solicitada: {nova_quantidade}.')
            else:
                form.save()
                messages.success(request, f'Saída de {saida_epi.quantidade}x "{saida_epi.epi.nome}" atualizada com sucesso!')
                return redirect('listar_saidas_epi')
        else:
            messages.error(request, 'Erro ao atualizar saída de EPI. Verifique os campos.')
    else:
        form = SaidaEPIForm(instance=saida_epi)
    context = {
        'form': form,
        'saida_epi': saida_epi,
        'active_page': 'saidas_epi',
    }
    return render(request, 'epi/editar_saida_epi.html', context)

@login_required
def excluir_saida_epi(request, pk):
    saida_epi = get_object_or_404(SaidaEPI, pk=pk)
    if request.method == 'POST':
        info_saida = f'{saida_epi.quantidade}x "{saida_epi.epi.nome}" para "{saida_epi.colaborador.nome_completo}"'
        saida_epi.delete()
        messages.success(request, f'Saída de {info_saida} excluída com sucesso.')
    return redirect('listar_saidas_epi')


# --- VIEWS PARA GERAÇÃO DE PDF ---

# Removido @csrf_exempt para produção, prefira usar o CSRF token padrão do Django
def gerar_pdf_saida_epi(request):
    if request.method == 'POST':
        # print(f"DEBUG: Gerar PDF - Request POST: {request.POST}") # Depuração

        context = {
            'colaborador_nome_display': request.POST.get('colaborador_nome_display', 'Não informado'),
            'epi_nome_display': request.POST.get('epi_nome_display', 'Não informado'),
            'ca_epi_display': request.POST.get('ca_epi_display', 'Não informado'),
            'quantidade': request.POST.get('quantidade', 'N/A'),
            'data_saida': request.POST.get('data_saida', 'N/A'),
            'observacoes': request.POST.get('observacoes', ''),
            'assinatura_digital_base64': request.POST.get('assinatura_digital_base64', ''),
        }

        colaborador_id = request.POST.get('colaborador')
        if colaborador_id:
            try:
                colaborador_obj = ColaboradorEPI.objects.get(pk=colaborador_id) 
                context['colaborador_nome_display'] = colaborador_obj.nome_completo
                context['colaborador_cpf_display'] = colaborador_obj.cpf
                # print(f"DEBUG: Colaborador encontrado para PDF: {colaborador_obj.nome_completo}") # Depuração
            except ColaboradorEPI.DoesNotExist: 
                # print(f"DEBUG: Colaborador com ID {colaborador_id} não encontrado para PDF.") # Depuração
                pass

        epi_id = request.POST.get('epi')
        if epi_id:
            try:
                epi_obj = EPI.objects.get(pk=epi_id)
                context['epi_nome_display'] = epi_obj.nome
                context['ca_epi_display'] = epi_obj.ca
                # print(f"DEBUG: EPI encontrado para PDF: {epi_obj.nome}") # Depuração
            except EPI.DoesNotExist:
                # print(f"DEBUG: EPI com ID {epi_id} não encontrado para PDF.") # Depuração
                pass

        template_path = 'epi/saida_epi_pdf_template.html'
        template = get_template(template_path)
        html = template.render(context)
        # print(f"DEBUG: HTML para PDF gerado. Tamanho: {len(html)} caracteres.") # Depuração

        result = io.BytesIO()
        pisa_status = pisa.CreatePDF(
            html,
            dest=result
        )

        if pisa_status.err:
            # print(f"ERRO: Erro pisa ao gerar PDF: {pisa_status.err}") # Depuração
            return HttpResponse('Tivemos alguns erros ao gerar o PDF: <pre>%s</pre>' % html, status=500)

        # print("DEBUG: PDF gerado com sucesso pelo Pisa.") # Depuração
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="saida_epi_documento.pdf"'
        return response
    # print("DEBUG: Requisição GET para gerar_pdf_saida_epi.") # Depuração
    return HttpResponse('Método não permitido', status=405)


@login_required
def imprimir_saida_epi_pdf(request, pk):
    saida_epi = get_object_or_404(SaidaEPI, pk=pk)
    # print(f"DEBUG: Imprimir PDF - Buscando SaidaEPI com PK: {pk}") # Depuração

    data_saida_local = timezone.localtime(saida_epi.data_saida)

    context = {
        'colaborador_nome_display': saida_epi.colaborador.nome_completo,
        'colaborador_cpf_display': saida_epi.colaborador.cpf,
        'epi_nome_display': saida_epi.epi.nome,
        'ca_epi_display': saida_epi.epi.ca,
        'quantidade': saida_epi.quantidade,
        'data_saida': data_saida_local.strftime('%d/%m/%Y %H:%M'),
        'observacoes': saida_epi.observacoes or '-',
    }

    if saida_epi.assinatura_digital:
        context['assinatura_digital_base64'] = saida_epi.assinatura_digital.url
        # print(f"DEBUG: URL da assinatura para PDF: {saida_epi.assinatura_digital.url}") # Depuração
    else:
        context['assinatura_digital_base64'] = ''
        # print("DEBUG: Assinatura digital não encontrada para este registro de saída.") # Depuração

    template_path = 'epi/saida_epi_pdf_template.html'
    template = get_template(template_path)
    html = template.render(context)
    # print(f"DEBUG: HTML para imprimir PDF gerado. Tamanho: {len(html)} caracteres.") # Depuração

    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(
        html,
        dest=result
    )

    if pisa_status.err:
        # print(f"ERRO: Erro pisa ao gerar PDF de impressão: {pisa_status.err}") # Depuração
        return HttpResponse('Tivemos alguns erros ao gerar o PDF de impressão: <pre>%s</pre>' % html, status=500)

    # print("DEBUG: PDF de impressão gerado com sucesso pelo Pisa.") # Depuração
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="recibo_saida_epi_{saida_epi.pk}.pdf"'
    return response


# --- VIEWS PARA ABSENTEÍSMO ---

class AbsenteismoHomeView(TemplateView):
    template_name = 'absenteismo/absenteismo_home.html'

class ListaTipoAbsenteismoView(ListView):
    model = TipoAbsenteismo
    template_name = 'absenteismo/lista_tipos_absenteismo.html'
    context_object_name = 'tipos_absenteismo'
    paginate_by = 10

class AdicionarTipoAbsenteismoView(CreateView):
    model = TipoAbsenteismo
    form_class = TipoAbsenteismoForm
    template_name = 'absenteismo/form_tipo_absenteismo.html'
    success_url = reverse_lazy('lista_tipos_absenteismo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Adicionar Tipo de Absenteísmo'
        return context

class EditarTipoAbsenteismoView(UpdateView):
    model = TipoAbsenteismo
    form_class = TipoAbsenteismoForm
    template_name = 'absenteismo/form_tipo_absenteismo.html'
    success_url = reverse_lazy('lista_tipos_absenteismo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Tipo de Absenteísmo'
        return context

class ExcluirTipoAbsenteismoView(DeleteView):
    model = TipoAbsenteismo
    template_name = 'absenteismo/confirm_delete_tipo_absenteismo.html'
    success_url = reverse_lazy('lista_tipos_absenteismo')

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"Não foi possível excluir o tipo de absenteísmo. Pode haver registros de absenteísmo associados a ele. ({e})")
            return redirect('lista_tipos_absenteismo')

class ListaRegistroAbsenteismoView(ListView):
    model = RegistroAbsenteismoDiario # <--- AJUSTADO
    template_name = 'absenteismo/lista_registros_absenteismo.html'
    context_object_name = 'registros'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtros
        colaborador_nome = self.request.GET.get('colaborador')
        tipo_id = self.request.GET.get('tipo')
        data_inicio_filtro = self.request.GET.get('data_inicio')
        data_fim_filtro = self.request.GET.get('data_fim')

        if colaborador_nome:
            queryset = queryset.filter(colaborador__nome_completo__icontains=colaborador_nome)
        if tipo_id:
            queryset = queryset.filter(tipo_absenteismo__id=tipo_id)
        if data_inicio_filtro:
            queryset = queryset.filter(data_inicio__gte=data_inicio_filtro)
        if data_fim_filtro:
            queryset = queryset.filter(data_fim__lte=data_fim_filtro)

        return queryset.select_related('colaborador', 'tipo_absenteismo') # Otimiza o acesso aos FKs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos_absenteismo'] = TipoAbsenteismo.objects.all().order_by('descricao')
        return context

class AdicionarRegistroAbsenteismoView(CreateView):
    model = RegistroAbsenteismoDiario # <--- AJUSTADO
    form_class = RegistroAbsenteismoForm
    template_name = 'absenteismo/form_registro_absenteismo.html'
    success_url = reverse_lazy('lista_registros_absenteismo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Adicionar Registro de Absenteísmo'
        return context

class EditarRegistroAbsenteismoView(UpdateView):
    model = RegistroAbsenteismoDiario # <--- AJUSTADO
    form_class = RegistroAbsenteismoForm
    template_name = 'absenteismo/form_registro_absenteismo.html'
    success_url = reverse_lazy('lista_registros_absenteismo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Registro de Absenteísmo'
        return context

class ExcluirRegistroAbsenteismoView(DeleteView):
    model = RegistroAbsenteismoDiario # <--- AJUSTADO
    template_name = 'absenteismo/confirm_delete_registro_absenteismo.html'
    success_url = reverse_lazy('lista_registros_absenteismo')


# --- NOVA VIEW PARA MARCAÇÃO DIÁRIA ---

@login_required
def marcar_absenteismo_diario(request):
    data_selecionada = request.GET.get('data', timezone.localdate().isoformat()) 

    try:
        data_obj = timezone.datetime.strptime(data_selecionada, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, "Formato de data inválido. Use AAAA-MM-DD.")
        data_obj = timezone.localdate() # Volta para a data atual se for inválido
        data_selecionada = data_obj.isoformat()

    # Buscar o TipoAbsenteismo para "Presente no Hub"
    try:
        tipo_presente = TipoAbsenteismo.objects.get(sigla='P') # Supondo que 'P' seja a sigla para "Presente"
    except TipoAbsenteismo.DoesNotExist:
        messages.error(request, "Tipo de Absenteísmo 'P' (Presente) não encontrado. Por favor, cadastre-o no admin.")
        return redirect('absenteismo_home') # Redireciona ou mostra erro fatal

    # Colaboradores ativos para a marcação
    # Pré-fetch `tipo_contrato`, `lider`, `cargo` para evitar N+1 queries no template se for exibir esses dados
    colaboradores = ColaboradorEPI.objects.filter(ativo=True).order_by('nome_completo').select_related('tipo_contrato', 'lider', 'cargo') 

    # Queryset inicial para o formset:
    # Tenta buscar registros existentes para a data e colaboradores ativos.
    # IMPORTANTE: Consideramos data_inicio e data_fim como sendo o mesmo dia para registros diários
    queryset_registros_existentes = RegistroAbsenteismoDiario.objects.filter( # <--- AJUSTADO
        colaborador__in=colaboradores,
        data_inicio=data_obj,
        data_fim=data_obj
    )
    # Criar um dicionário para busca rápida dos registros existentes
    registros_map = {reg.colaborador_id: reg for reg in queryset_registros_existentes}

    if request.method == 'POST':
        # Instanciar o formset com os dados do POST
        formset = RegistroDiarioAbsenteismoFormSet(request.POST)

        if formset.is_valid():
            with transaction.atomic(): # Garante que todas as operações sejam salvas ou nenhuma seja
                for form in formset:
                    colaborador = form.cleaned_data.get('colaborador')
                    tipo_absenteismo = form.cleaned_data.get('tipo_absenteismo')

                    # Apenas processa formulários que correspondem a um colaborador válido
                    if not colaborador:
                        continue # Pula se não houver um colaborador associado ao form

                    registro_existente = registros_map.get(colaborador.pk)

                    if registro_existente:
                        # Se o tipo mudou, atualiza o registro existente
                        if registro_existente.tipo_absenteismo != tipo_absenteismo:
                            registro_existente.tipo_absenteismo = tipo_absenteismo
                            registro_existente.save()
                    else:
                        # Se não há registro, cria um novo
                        RegistroAbsenteismoDiario.objects.create( # <--- AJUSTADO
                            colaborador=colaborador,
                            tipo_absenteismo=tipo_absenteismo,
                            data_inicio=data_obj,
                            data_fim=data_obj, # Para marcação diária, data_inicio e data_fim são iguais
                            observacoes="" # Ou alguma observação padrão se quiser
                        )
                messages.success(request, f"Registros de absenteísmo para {data_obj.strftime('%d/%m/%Y')} salvos com sucesso!")
                return redirect('marcar_absenteismo_diario') # Redireciona para a mesma página, limpando POST
        else:
            messages.error(request, "Erro ao salvar os registros. Verifique os dados e tente novamente.")
            # Para depuração, você pode printar formset.errors
            # print(formset.errors)
    else: # GET request
        # Preparar dados iniciais para o formset
        initial_data = []
        for colaborador in colaboradores:
            registro_existente = registros_map.get(colaborador.pk)

            initial_item = {
                'colaborador': colaborador.pk, # ID do colaborador para o HiddenInput
                'tipo_absenteismo': tipo_presente.pk # Default para "Presente"
            }

            if registro_existente:
                initial_item['id'] = registro_existente.pk # Passa o ID da instância para o formset (para update)
                initial_item['tipo_absenteismo'] = registro_existente.tipo_absenteismo.pk

            initial_data.append(initial_item)

        # Instanciar o formset com os dados iniciais.
        # Não passamos 'queryset' no GET se queremos que ele crie novos forms para todos os colaboradores.
        # 'initial' já faz isso. Se passarmos queryset, ele só mostra os que já existem.
        # queryset=queryset_registros_existentes # Pode ser útil se você quiser que o formset gerencie UPDATE/DELETE
        formset = RegistroDiarioAbsenteismoFormSet(
            initial=initial_data,
        )

    context = {
        'formset': formset,
        'colaboradores_list': colaboradores, # Passar os colaboradores para o template para exibir nomes e outros dados
        'data_selecionada': data_selecionada, # Para exibir no input de data
        'data_obj': data_obj, # Para exibir a data formatada e usar em comparações
    }
    return render(request, 'absenteismo/marcar_absenteismo_diario.html', context)


## Nova View de API para Colaborador (get_colaborador_data)

@login_required
def get_colaborador_data(request, pk):
    """
    Retorna os dados de um Colaborador, incluindo Tipo de Contrato, Líder e Cargo,
    em formato JSON.
    """
    try:
        colaborador = ColaboradorEPI.objects.select_related('tipo_contrato', 'lider', 'cargo').get(pk=pk) 
        data = {
            'id': colaborador.pk,
            'nome_completo': colaborador.nome_completo,
            'matricula': colaborador.matricula,
            'cpf': colaborador.cpf,
            'station_id': colaborador.station_id, 
            'codigo': colaborador.codigo, 
            'bpo': colaborador.bpo, 
            'turno': colaborador.turno, 
            'data_admissao': colaborador.data_admissao.isoformat() if colaborador.data_admissao else None, 
            'tipo_contrato': colaborador.tipo_contrato.nome if colaborador.tipo_contrato else 'N/A',
            'lider': colaborador.lider.nome if colaborador.lider else 'N/A',
            'cargo': colaborador.cargo.nome if colaborador.cargo else 'N/A',
            # Adicione outros campos do Colaborador que possam ser úteis
        }
        return JsonResponse(data)
    except ColaboradorEPI.DoesNotExist: 
        return JsonResponse({'error': 'Colaborador não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
def relatorio_absenteismo_form(request):
    # Lógica para exibir o formulário de seleção de mês/ano para o relatório
    return render(request, 'epi/absenteismo/relatorio_absenteismo_form.html', {})

@login_required
def exportar_relatorio_absenteismo_csv(request):
    # Lógica para gerar e exportar o CSV
    # Por enquanto, pode ser um HttpResponse simples para teste
    return HttpResponse("Relatório CSV gerado (implementar lógica)", content_type='text/plain')