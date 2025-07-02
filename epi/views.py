# pat/epi/views.py

import io
from django.http import HttpResponse
from django.template.loader import get_template
# Para CSRF, use @csrf_exempt COM CAUTELA ou um decorator mais seguro em produção
from django.views.decorators.csrf import csrf_exempt 
from xhtml2pdf import pisa
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required 
from django.contrib import messages
from django.db.models import Sum, Q 
from django.utils import timezone 

from .forms import (
    TipoEPIForm, EPIForm, ColaboradorForm,
    EntradaEPIForm, SaidaEPIForm,
    EPIFilterForm, ColaboradorFilterForm, EntradaSaidaFilterForm
)
from .models import TipoEPI, EPI, Colaborador, EntradaEPI, SaidaEPI
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

    context = {
        'epis': epis,
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
    messages.error(request, 'A exclusão deve ser feita via POST.')
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
    messages.error(request, 'A exclusão deve ser feita via POST.')
    return redirect('listar_tipos_epi')


# --- VIEWS PARA COLABORADOR ---

@login_required
def listar_colaboradores(request):
    colaboradores = Colaborador.objects.all()
    filter_form = ColaboradorFilterForm(request.GET)

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
        'active_page': 'colaboradores',
    }
    return render(request, 'epi/listar_colaboradores.html', context)

@login_required
def adicionar_colaborador(request):
    if request.method == 'POST':
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Colaborador "{form.instance.nome_completo}" adicionado com sucesso!')
            return redirect('listar_colaboradores')
        else:
            messages.error(request, 'Erro ao adicionar Colaborador. Verifique os campos.')
    else:
        form = ColaboradorForm()
    context = {
        'form': form,
        'active_page': 'colaboradores',
    }
    return render(request, 'epi/adicionar_colaborador.html', context)

@login_required
def editar_colaborador(request, pk):
    colaborador = get_object_or_404(Colaborador, pk=pk)
    if request.method == 'POST':
        form = ColaboradorForm(request.POST, instance=colaborador)
        if form.is_valid():
            form.save()
            messages.success(request, f'Colaborador "{colaborador.nome_completo}" atualizado com sucesso!')
            return redirect('listar_colaboradores')
        else:
            messages.error(request, 'Erro ao atualizar Colaborador. Verifique os campos.')
    else:
        form = ColaboradorForm(instance=colaborador)
    context = {
        'form': form,
        'colaborador': colaborador,
        'active_page': 'colaboradores',
    }
    return render(request, 'epi/editar_colaborador.html', context)

@login_required
def excluir_colaborador(request, pk):
    colaborador = get_object_or_404(Colaborador, pk=pk)
    if request.method == 'POST':
        nome_completo = colaborador.nome_completo
        colaborador.delete()
        messages.success(request, f'Colaborador "{nome_completo}" excluído com sucesso.')
        return redirect('listar_colaboradores')
    messages.error(request, 'A exclusão deve ser feita via POST.')
    return redirect('listar_colaboradores')


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
    messages.error(request, 'A exclusão deve ser feita via POST.')
    return redirect('listar_entradas_epi')


# --- VIEWS PARA SAÍDA DE EPI ---

@login_required
def listar_saidas_epi(request):
    saidas_epi = SaidaEPI.objects.all()
    filter_form = EntradaSaidaFilterForm(request.GET) 

    if filter_form.is_valid():
        epi = filter_form.cleaned_data.get('epi')
        colaborador = filter_form.cleaned_data.get('colaborador')
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
        print(f"DEBUG: Request POST: {request.POST}") # Adicionado para depuração
        print(f"DEBUG: Request FILES: {request.FILES}") # Adicionado para depuração

        if form.is_valid():
            saida = form.save(commit=False)
            
            # Lida com a assinatura digital se ela for enviada como base64
            assinatura_digital_base64 = request.POST.get('assinatura_digital')
            if assinatura_digital_base64 and assinatura_digital_base64.startswith('data:image'):
                format, imgstr = assinatura_digital_base64.split(';base64,')
                ext = format.split('/')[-1]
                # Usa 'temp' no nome do arquivo porque saida.pk ainda não existe
                # O nome final será ajustado pelos signals após o save() principal
                saida.assinatura_digital.save(f'assinatura_temp.{ext}', ContentFile(base64.b64decode(imgstr)), save=False)
                print(f"DEBUG: Assinatura Base64 processada. Caminho planejado: {saida.assinatura_digital.name}") # Adicionado para depuração
            else:
                print("DEBUG: Assinatura Base64 NÃO encontrada ou inválida.")


            # Validação de estoque antes de salvar
            if saida.quantidade > saida.epi.estoque_atual:
                messages.error(request, f'Estoque insuficiente para {saida.epi.nome}. Disponível: {saida.epi.estoque_atual}, Solicitado: {saida.quantidade}.')
                print("DEBUG: Estoque insuficiente. Não salvando.") # Adicionado para depuração
            else:
                saida.save() # Salva a SaidaEPI e as mídias (assinatura e PDF)
                print(f"DEBUG: SaidaEPI salva com PK: {saida.pk}. Assinatura salva em: {saida.assinatura_digital.url if saida.assinatura_digital else 'N/A'}. PDF salvo em: {saida.pdf_documento.url if saida.pdf_documento else 'N/A'}") # Adicionado para depuração
                messages.success(request, f'Saída de {saida.quantidade}x "{saida.epi.nome}" para "{saida.colaborador.nome_completo}" registrada com sucesso!')
                return redirect('listar_saidas_epi')
        else:
            print(f"DEBUG: Form inválido. Erros: {form.errors}") # Adicionado para depuração
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
    messages.error(request, 'A exclusão deve ser feita via POST.')
    return redirect('listar_saidas_epi')


# NOVA VIEW PARA GERAR PDF (usada na página de adicionar)
@csrf_exempt 
def gerar_pdf_saida_epi(request):
    if request.method == 'POST':
        print(f"DEBUG: Gerar PDF - Request POST: {request.POST}") # Depuração
        
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
                colaborador_obj = Colaborador.objects.get(pk=colaborador_id)
                context['colaborador_nome_display'] = colaborador_obj.nome_completo
                context['colaborador_cpf_display'] = colaborador_obj.cpf
                print(f"DEBUG: Colaborador encontrado para PDF: {colaborador_obj.nome_completo}") # Depuração
            except Colaborador.DoesNotExist:
                print(f"DEBUG: Colaborador com ID {colaborador_id} não encontrado para PDF.") # Depuração
                pass 

        epi_id = request.POST.get('epi')
        if epi_id:
            try:
                epi_obj = EPI.objects.get(pk=epi_id)
                context['epi_nome_display'] = epi_obj.nome
                context['ca_epi_display'] = epi_obj.ca
                print(f"DEBUG: EPI encontrado para PDF: {epi_obj.nome}") # Depuração
            except EPI.DoesNotExist:
                print(f"DEBUG: EPI com ID {epi_id} não encontrado para PDF.") # Depuração
                pass

        template_path = 'epi/saida_epi_pdf_template.html'
        template = get_template(template_path)
        html = template.render(context)
        print(f"DEBUG: HTML para PDF gerado. Tamanho: {len(html)} caracteres.") # Depuração

        result = io.BytesIO()
        pisa_status = pisa.CreatePDF(
            html,
            dest=result
        )

        if pisa_status.err:
            print(f"ERRO: Erro pisa ao gerar PDF: {pisa_status.err}") # Depuração
            return HttpResponse('Tivemos alguns erros ao gerar o PDF: <pre>%s</pre>' % html, status=500)
        
        print("DEBUG: PDF gerado com sucesso pelo Pisa.") # Depuração
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="saida_epi_documento.pdf"'
        return response
    print("DEBUG: Requisição GET para gerar_pdf_saida_epi.") # Depuração
    return HttpResponse('Método não permitido', status=405)


# NOVA VIEW: Gerar PDF para um registro de SaidaEPI existente (para o botão de imprimir)
@login_required
def imprimir_saida_epi_pdf(request, pk):
    saida_epi = get_object_or_404(SaidaEPI, pk=pk)
    print(f"DEBUG: Imprimir PDF - Buscando SaidaEPI com PK: {pk}") # Depuração

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
        print(f"DEBUG: URL da assinatura para PDF: {saida_epi.assinatura_digital.url}") # Depuração
    else:
        context['assinatura_digital_base64'] = '' 
        print("DEBUG: Assinatura digital não encontrada para este registro de saída.") # Depuração

    template_path = 'epi/saida_epi_pdf_template.html'
    template = get_template(template_path)
    html = template.render(context)
    print(f"DEBUG: HTML para imprimir PDF gerado. Tamanho: {len(html)} caracteres.") # Depuração

    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(
        html,
        dest=result
    )

    if pisa_status.err:
        print(f"ERRO: Erro pisa ao gerar PDF de impressão: {pisa_status.err}") # Depuração
        return HttpResponse('Tivemos alguns erros ao gerar o PDF de impressão: <pre>%s</pre>' % html, status=500)
    
    print("DEBUG: PDF de impressão gerado com sucesso pelo Pisa.") # Depuração
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="recibo_saida_epi_{saida_epi.pk}.pdf"'
    return response

