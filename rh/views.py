# C:\Users\SEAOps\Documents\pat\rh\views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from django.forms import modelformset_factory
from django.utils import timezone
from datetime import date, timedelta, datetime
from django.contrib import messages
import re
from django.db import transaction
from django.urls import reverse
import csv
from django.http import HttpResponse
from usuarios.utils import log_atividade

# Importe seus modelos
from .models import TipoContrato, Lider, Cargo, TipoAbsenteismo, RegistroAbsenteismoDiario
from epi.models import ColaboradorEPI # Certifique-se que este import está correto

# Importe seus formulários, incluindo o novo RelatorioAbsenteismoFilterForm
from .forms import (
    RegistroAbsenteismoForm, TipoContratoForm, TipoAbsenteismoForm,
    LiderForm, CargoForm, RegistroAbsenteismoDiarioForm,
    RelatorioAbsenteismoFilterForm # <--- NOVO IMPORT
)

# --- Views Gerais de RH ---

def rh_home(request):
    """Página inicial do módulo de RH."""
    total_colaboradores = ColaboradorEPI.objects.filter(ativo=True).count()

    # ATENÇÃO: Confirme o 'related_name' no seu modelo ColaboradorEPI em epi/models.py
    # Se o ForeignKey de ColaboradorEPI para TipoContrato tiver um related_name='meus_colaboradores',
    # então a linha abaixo deve ser: num_colabs=Count('meus_colaboradores', distinct=True)
    # Se não houver related_name, o padrão seria 'colaboradorepi_set'.
    tipos_contrato_count = TipoContrato.objects.annotate(
        num_colabs=Count('colaboradorepi', distinct=True) # Mantido como 'colaboradorepi' - VERIFICAR related_name no modelo EPI
    ).order_by('nome')

    context = {
        'modulo': 'Recursos Humanos',
        'total_colaboradores': total_colaboradores,
        'tipos_contrato_count': tipos_contrato_count,
        'active_page': 'rh_home',
    }
    return render(request, 'rh/rh_home.html', context)

# --- Views para TipoContrato ---

def lista_tipos_contrato(request):
    """Exibe uma lista de todos os tipos de contrato."""
    tipos_contrato = TipoContrato.objects.all().order_by('nome')
    context = {
        'tipos_contrato': tipos_contrato,
        'active_page': 'lista_tipos_contrato',
    }
    return render(request, 'rh/lista_tipos_contrato.html', context)

def adicionar_tipo_contrato(request):
    """Página para adicionar um novo tipo de contrato."""
    if request.method == 'POST':
        form = TipoContratoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de contrato adicionado com sucesso!')
            return redirect('lista_tipos_contrato')
    else:
        form = TipoContratoForm()
    context = {
        'form': form,
        'active_page': 'adicionar_tipo_contrato',
    }
    return render(request, 'rh/adicionar_tipo_contrato.html', context)

def editar_tipo_contrato(request, pk):
    """Página para editar um tipo de contrato existente."""
    tipo_contrato = get_object_or_404(TipoContrato, pk=pk)
    if request.method == 'POST':
        form = TipoContratoForm(request.POST, instance=tipo_contrato)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de contrato editado com sucesso!')
            return redirect('lista_tipos_contrato')
    else:
        form = TipoContratoForm(instance=tipo_contrato)
    context = {
        'form': form,
        'tipo_contrato': tipo_contrato,
        'active_page': 'editar_tipo_contrato',
    }
    return render(request, 'rh/editar_tipo_contrato.html', context)

def excluir_tipo_contrato(request, pk):
    """Confirmação e exclusão de um tipo de contrato."""
    tipo_contrato = get_object_or_404(TipoContrato, pk=pk)
    if request.method == 'POST':
        if ColaboradorEPI.objects.filter(tipo_contrato=tipo_contrato).exists():
            messages.error(request, 'Não foi possível excluir o tipo de contrato, pois há colaboradores associados.')
            return redirect('lista_tipos_contrato')
        tipo_contrato.delete()
        messages.success(request, 'Tipo de contrato excluído com sucesso!')
        return redirect('lista_tipos_contrato')
    context = {
        'tipo_contrato': tipo_contrato,
        'active_page': 'excluir_tipo_contrato',
    }
    return render(request, 'rh/confirmar_exclusao_tipo_contrato.html', context)

# --- Views para Absenteísmo ---

def absenteismo_home(request):
    """Página inicial do módulo de Absenteísmo."""
    context = {
        'titulo': 'Gestão de Absenteísmo',
        'active_page': 'absenteismo_home',
    }
    return render(request, 'rh/absenteismo/absenteismo_home.html', context)

def lista_registros_absenteismo(request):
    """Exibe uma lista de todos os registros de absenteísmo, com funcionalidade de filtro manual."""

    registros = RegistroAbsenteismoDiario.objects.all()

    # Obter parâmetros de filtro da requisição GET
    colaborador_nome = request.GET.get('colaborador')
    tipo_absenteismo_id = request.GET.get('tipo')
    data_inicio_filtro_str = request.GET.get('data_inicio')
    data_fim_filtro_str = request.GET.get('data_fim')

    # Aplicar filtros
    if colaborador_nome:
        registros = registros.filter(colaborador__nome_completo__icontains=colaborador_nome)

    if tipo_absenteismo_id:
        registros = registros.filter(tipo_absenteismo__id=tipo_absenteismo_id)

    # Lógica de filtro de datas aprimorada para sobreposição de períodos
    if data_inicio_filtro_str:
        try:
            data_inicio_filtro = datetime.strptime(data_inicio_filtro_str, '%Y-%m-%d').date()
            registros = registros.filter(data_fim__gte=data_inicio_filtro)
        except ValueError:
            messages.error(request, "Formato de 'Data Início' inválido. Utilize AAAA-MM-DD.")

    if data_fim_filtro_str:
        try:
            data_fim_filtro = datetime.strptime(data_fim_filtro_str, '%Y-%m-%d').date()
            registros = registros.filter(data_inicio__lte=data_fim_filtro)
        except ValueError:
            messages.error(request, "Formato de 'Data Fim' inválido. Utilize AAAA-MM-DD.")

    registros = registros.order_by('-data_inicio', 'colaborador__nome_completo')

    tipos_absenteismo = TipoAbsenteismo.objects.all().order_by('descricao')

    context = {
        'registros': registros,
        'tipos_absenteismo': tipos_absenteismo,
        'active_page': 'lista_registros_absenteismo',
        'colaborador_nome': colaborador_nome,
        'tipo_absenteismo_id': tipo_absenteismo_id,
        'data_inicio_filtro': data_inicio_filtro_str,
        'data_fim_filtro': data_fim_filtro_str,
    }
    return render(request, 'rh/absenteismo/lista_registros_absenteismo.html', context)

def adicionar_registro_absenteismo(request):
    """Página para adicionar um novo registro de absenteísmo."""
    if request.method == 'POST':
        form = RegistroAbsenteismoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro de absenteísmo adicionado com sucesso!')
            return redirect('lista_registros_absenteismo')
    else:
        form = RegistroAbsenteismoForm()

    context = {
        'form': form,
        'active_page': 'adicionar_registro_absenteismo',
    }
    return render(request, 'rh/absenteismo/adicionar_registro_absenteismo.html', context)

def editar_registro_absenteismo(request, pk):
    """Página para editar um registro de absenteísmo existente."""
    registro = get_object_or_404(RegistroAbsenteismoDiario, pk=pk)
    if request.method == 'POST':
        form = RegistroAbsenteismoForm(request.POST, instance=registro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro de absenteísmo editado com sucesso!')
            return redirect('lista_registros_absenteismo')
    else:
        form = RegistroAbsenteismoForm(instance=registro)

    context = {
        'form': form,
        'registro': registro,
        'active_page': 'editar_registro_absenteismo',
    }
    return render(request, 'rh/absenteismo/editar_registro_absenteismo.html', context)

def excluir_registro_absenteismo(request, pk):
    """Confirmação e exclusão de um registro de absenteísmo."""
    registro = get_object_or_404(RegistroAbsenteismoDiario, pk=pk)
    if request.method == 'POST':
        registro.delete()
        messages.success(request, 'Registro de absenteísmo excluído com sucesso!')
        return redirect('lista_registros_absenteismo')

    context = {
        'registro': registro,
        'active_page': 'excluir_registro_absenteismo',
    }
    return render(request, 'rh/absenteismo/confirmar_exclusao_absenteismo.html', context)

def lista_tipos_absenteismo(request):
    """Exibe uma lista de todos os tipos de absenteísmo."""
    tipos_absenteismo = TipoAbsenteismo.objects.all().order_by('sigla')
    context = {
        'tipos_absenteismo': tipos_absenteismo,
        'active_page': 'lista_tipos_absenteismo',
    }
    return render(request, 'rh/absenteismo/lista_tipos_absenteismo.html', context)

def adicionar_tipo_absenteismo(request):
    """Página para adicionar um novo tipo de absenteísmo."""
    if request.method == 'POST':
        form = TipoAbsenteismoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de absenteísmo adicionado com sucesso!')
            return redirect('lista_tipos_absenteismo')
    else:
        form = TipoAbsenteismoForm()
    context = {
        'form': form,
        'active_page': 'adicionar_tipo_absenteismo',
    }
    return render(request, 'rh/absenteismo/adicionar_tipo_absenteismo.html', context)

def editar_tipo_absenteismo(request, pk):
    """Página para editar um tipo de absenteísmo existente."""
    tipo_absenteismo = get_object_or_404(TipoAbsenteismo, pk=pk)
    if request.method == 'POST':
        form = TipoAbsenteismoForm(request.POST, instance=tipo_absenteismo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de absenteísmo editado com sucesso!')
            return redirect('lista_tipos_absenteismo')
    else:
        form = TipoAbsenteismoForm(instance=tipo_absenteismo)
    context = {
        'form': form,
        'tipo_absenteismo': tipo_absenteismo,
        'active_page': 'editar_tipo_absenteismo',
    }
    return render(request, 'rh/absenteismo/editar_tipo_absenteismo.html', context)

def excluir_tipo_absenteismo(request, pk):
    """Confirmação e exclusão de um tipo de absenteísmo."""
    tipo_absenteismo = get_object_or_404(TipoAbsenteismo, pk=pk)
    if request.method == 'POST':
        if tipo_absenteismo.registroabsenteismodiario_set.exists():
            messages.error(request, 'Não foi possível excluir o tipo de absenteísmo, pois há registros associados.')
            return redirect('lista_tipos_absenteismo')
        tipo_absenteismo.delete()
        messages.success(request, 'Tipo de absenteísmo excluído com sucesso!')
        return redirect('lista_tipos_absenteismo')
    context = {
        'tipo_absenteismo': tipo_absenteismo,
        'active_page': 'excluir_tipo_absenteismo',
    }
    return render(request, 'rh/absenteismo/confirmar_exclusao_tipo_absenteismo.html', context)


# --- Views para Líderes ---

def lista_lideres(request):
    """Exibe uma lista de todos os líderes."""
    lideres = Lider.objects.all().order_by('nome')
    context = {
        'lideres': lideres,
        'active_page': 'lista_lideres',
    }
    return render(request, 'rh/lista_lideres.html', context)

def adicionar_lider(request):
    """Página para adicionar um novo líder."""
    if request.method == 'POST':
        form = LiderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Líder adicionado com sucesso!')
            return redirect('lista_lideres')
    else:
        form = LiderForm()
    context = {
        'form': form,
        'active_page': 'adicionar_lider',
    }
    return render(request, 'rh/adicionar_lider.html', context)

def editar_lider(request, pk):
    """Página para editar um líder existente."""
    lider = get_object_or_404(Lider, pk=pk)
    if request.method == 'POST':
        form = LiderForm(request.POST, instance=lider)
        if form.is_valid():
            form.save()
            messages.success(request, 'Líder editado com sucesso!')
            return redirect('lista_lideres')
    else:
        form = LiderForm(instance=lider)
    context = {
        'form': form,
        'lider': lider,
        'active_page': 'editar_lider',
    }
    return render(request, 'rh/editar_lider.html', context)

def excluir_lider(request, pk):
    """Confirmação e exclusão de um líder."""
    lider = get_object_or_404(Lider, pk=pk)
    if request.method == 'POST':
        if ColaboradorEPI.objects.filter(lider=lider).exists():
            messages.error(request, 'Não foi possível excluir o líder, pois há colaboradores associados a ele.')
            return redirect('lista_lideres')
        lider.delete()
        messages.success(request, 'Líder excluído com sucesso!')
        return redirect('lista_lideres')
    context = {
        'lider': lider,
        'active_page': 'excluir_lider',
    }
    return render(request, 'rh/confirmar_exclusao_lider.html', context)

# --- Views para Cargos ---

def lista_cargos(request):
    """Exibe uma lista de todos os cargos."""
    cargos = Cargo.objects.all().order_by('nome')
    context = {
        'cargos': cargos,
        'active_page': 'lista_cargos',
    }
    return render(request, 'rh/lista_cargos.html', context)

def adicionar_cargo(request):
    """Página para adicionar um novo cargo."""
    if request.method == 'POST':
        form = CargoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cargo adicionado com sucesso!')
            return redirect('lista_cargos')
    else:
        form = CargoForm()
    context = {
        'form': form,
        'active_page': 'adicionar_cargo',
    }
    return render(request, 'rh/adicionar_cargo.html', context)

def editar_cargo(request, pk):
    """Página para editar um cargo existente."""
    cargo = get_object_or_404(Cargo, pk=pk)
    if request.method == 'POST':
        form = CargoForm(request.POST, instance=cargo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cargo editado com sucesso!')
            return redirect('lista_cargos')
    else:
        form = CargoForm(instance=cargo)
    context = {
        'form': form,
        'cargo': cargo,
        'active_page': 'editar_cargo',
    }
    return render(request, 'rh/editar_cargo.html', context)

def excluir_cargo(request, pk):
    """Confirmação e exclusão de um cargo."""
    cargo = get_object_or_404(Cargo, pk=pk)
    if request.method == 'POST':
        if ColaboradorEPI.objects.filter(cargo=cargo).exists():
            messages.error(request, 'Não foi possível excluir o cargo, pois há colaboradores associados a ele.')
            return redirect('lista_cargos')
        cargo.delete()
        messages.success(request, 'Cargo excluído com sucesso!')
        return redirect('lista_cargos')
    context = {
        'cargo': cargo,
        'active_page': 'excluir_cargo',
    }
    return render(request, 'rh/confirmar_exclusao_cargo.html', context)


# --- Marcar Absenteísmo Diário (Ajustada) ---
def marcar_absenteismo_diario(request):
    """
    Permite marcar o absenteísmo diário para colaboradores,
    com opções de filtro por data e turno, e marcação em massa.
    """
    selected_date_str = request.GET.get('data')
    selected_turno = request.GET.get('turno', '')

    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Formato de data inválido. Usando a data atual. Utilize AAAA-MM-DD.")
            selected_date = timezone.localdate()
            selected_date_str = str(selected_date)
    else:
        selected_date = timezone.localdate()
        selected_date_str = str(selected_date)

    # 1. Obter todos os colaboradores ativos e elegíveis para a data e turno selecionados.
    colaboradores_queryset = ColaboradorEPI.objects.filter(ativo=True) \
                                                    .filter(data_admissao__lte=selected_date) \
                                                    .filter(Q(data_desligamento__isnull=True) | Q(data_desligamento__gte=selected_date))
    if selected_turno:
        colaboradores_queryset = colaboradores_queryset.filter(turno=selected_turno)
    
    colaboradores_queryset = colaboradores_queryset.order_by('nome_completo')

    # 2. Obter os registros de absenteísmo existentes para a data e colaboradores filtrados.
    absenteismos_existentes = RegistroAbsenteismoDiario.objects.filter(
        data_inicio__lte=selected_date,
        data_fim__gte=selected_date,
        colaborador__in=colaboradores_queryset # Passa o queryset diretamente
    ).select_related('colaborador', 'tipo_absenteismo') # Otimiza a busca por related objects
    
    # Criamos um dicionário para fácil acesso aos registros existentes pelo ID do colaborador
    absenteismos_dict = {abs.colaborador_id: abs for abs in absenteismos_existentes}

    # Definir o ModelFormsetFactory
    RegistroAbsenteismoDiarioFormSet = modelformset_factory(
        RegistroAbsenteismoDiario,
        form=RegistroAbsenteismoDiarioForm,
        extra=0, # Não adicionar formulários extras por padrão
        can_delete=True
    )

    if request.method == 'POST':
        # Ao receber um POST, o formset deve ser inicializado com os dados POSTados
        # e com o queryset de registros existentes para que o Django saiba quais instâncias atualizar/deletar.
        formset = RegistroAbsenteismoDiarioFormSet(
            request.POST,
            queryset=absenteismos_existentes # Passa os objetos existentes para o formset
        )

        mass_absenteismo_type_id = request.POST.get('mass_absenteismo_type')
        mass_absenteismo_type = None
        if mass_absenteismo_type_id:
            try:
                if mass_absenteismo_type_id == '': # Nenhuma opção selecionada no "Marcar em Massa"
                    mass_absenteismo_type = None # Indica que é para "desmarcar" em massa
                else:
                    mass_absenteismo_type = TipoAbsenteismo.objects.get(id=mass_absenteismo_type_id)
            except TipoAbsenteismo.DoesNotExist:
                messages.error(request, "Tipo de absenteísmo em massa inválido.")

        if formset.is_valid():
            with transaction.atomic():
                # Conjunto para rastrear colaboradores que tiveram seu absenteísmo modificado individualmente
                colaboradores_processados_individualmente_ids = set()
                
                # Processa os formulários do formset
                for form in formset:
                    colaborador_obj = form.cleaned_data.get('colaborador')
                    
                    if not colaborador_obj:
                        continue

                    colaborador_id = colaborador_obj.id
                    tipo_absenteismo = form.cleaned_data.get('tipo_absenteismo')
                    observacoes = form.cleaned_data.get('observacoes', '')
                    
                    # Marca o colaborador como processado individualmente
                    colaboradores_processados_individualmente_ids.add(colaborador_id)

                    # Se o formulário foi marcado para exclusão OU o tipo_absenteismo foi desmarcado
                    if form.cleaned_data.get('DELETE') or tipo_absenteismo is None:
                        if form.instance.pk: # Se é uma instância existente, delete-a
                            form.instance.delete()
                            messages.info(request, f"Absenteísmo de {colaborador_obj.nome_completo} ({selected_date.strftime('%d/%m/%Y')}) desmarcado/excluído.")
                        continue # Não precisamos fazer mais nada se o formulário foi deletado/desmarcado

                    # Se um tipo de absenteísmo foi selecionado
                    if tipo_absenteismo:
                        # Verifica se já existe um registro para a data e colaborador
                        registro_existente = RegistroAbsenteismoDiario.objects.filter(
                            colaborador=colaborador_obj,
                            data_inicio__lte=selected_date,
                            data_fim__gte=selected_date
                        ).first()

                        if registro_existente:
                            # Se existe e o tipo é o mesmo, não faz nada (evita mensagens de "atualizado" desnecessárias)
                            if registro_existente.tipo_absenteismo == tipo_absenteismo and registro_existente.observacoes == observacoes:
                                pass
                            else: # Atualiza se houve mudança no tipo ou nas observações
                                registro_existente.tipo_absenteismo = tipo_absenteismo
                                registro_existente.observacoes = observacoes
                                registro_existente.save()
                                messages.success(request, f"Absenteísmo de {colaborador_obj.nome_completo} ({selected_date.strftime('%d/%m/%Y')}) atualizado.")
                        else: # Cria um novo registro se não existe
                            RegistroAbsenteismoDiario.objects.create(
                                colaborador=colaborador_obj,
                                data_inicio=selected_date,
                                data_fim=selected_date,
                                tipo_absenteismo=tipo_absenteismo,
                                observacoes=observacoes
                            )
                            messages.success(request, f"Absenteísmo de {colaborador_obj.nome_completo} ({selected_date.strftime('%d/%m/%Y')}) registrado.")
                
                # Aplica o absenteísmo em massa para colaboradores que NÃO foram processados individualmente
                if mass_absenteismo_type: # Se um tipo foi selecionado para massa
                    for colab in colaboradores_queryset:
                        if colab.id not in colaboradores_processados_individualmente_ids:
                            registro, created = RegistroAbsenteismoDiario.objects.update_or_create(
                                colaborador=colab,
                                data_inicio=selected_date,
                                data_fim=selected_date,
                                defaults={
                                    'tipo_absenteismo': mass_absenteismo_type,
                                    'observacoes': f"Marcado em massa em {timezone.now().strftime('%d/%m/%Y %H:%M')}"
                                }
                            )
                            if not created and registro.tipo_absenteismo != mass_absenteismo_type:
                                messages.info(request, f"Absenteísmo de {colab.nome_completo} ({selected_date.strftime('%d/%m/%Y')}) atualizado via massa.")
                            elif created:
                                messages.info(request, f"Absenteísmo de {colab.nome_completo} ({selected_date.strftime('%d/%m/%Y')}) marcado via massa.")
                elif mass_absenteismo_type is None and mass_absenteismo_type_id == '': # Caso tenha sido selecionado '--- Não Ausente ---' para massa
                    for colab in colaboradores_queryset:
                        if colab.id not in colaboradores_processados_individualmente_ids:
                            # Tenta encontrar e deletar qualquer registro existente para o colaborador na data
                            deleted_count, _ = RegistroAbsenteismoDiario.objects.filter(
                                colaborador=colab,
                                data_inicio__lte=selected_date,
                                data_fim__gte=selected_date
                            ).delete()
                            if deleted_count > 0:
                                messages.info(request, f"Absenteísmo de {colab.nome_completo} ({selected_date.strftime('%d/%m/%Y')}) desmarcado via massa.")

            messages.success(request, f"Absenteísmo para {selected_date.strftime('%d/%m/%Y')} processado com sucesso!")
            
            redirect_url = reverse('marcar_absenteismo_diario')
            params = []
            if selected_date_str:
                params.append(f"data={selected_date_str}")
            if selected_turno:
                params.append(f"turno={selected_turno}")
            
            if params:
                redirect_url += '?' + '&'.join(params)
            
            return redirect(redirect_url)

        else: # Formset inválido no POST
            messages.error(request, "Ocorreu um erro ao salvar o absenteísmo. Por favor, verifique os campos destacados.")
            # O formset já contém os dados POSTados e os erros, então basta passá-lo para o contexto.
            # A lista de colaboradores (`colaboradores_queryset`) ainda será usada para iterar no template.

    else: # GET request
        # No GET, criamos um formset que conterá um formulário para CADA colaborador ativo,
        # pré-preenchido com dados existentes se houver, ou vazio se não houver.
        
        # Primeiro, pegamos todos os registros existentes para os colaboradores_queryset na data.
        formset_queryset = RegistroAbsenteismoDiario.objects.filter(
            data_inicio__lte=selected_date,
            data_fim__gte=selected_date,
            colaborador__in=colaboradores_queryset # Passa o queryset diretamente
        )
        
        # Agora, identificamos os colaboradores que NÃO têm um registro existente para a data.
        # Para esses, precisamos criar um dicionário de `initial` data.
        colaboradores_com_absenteismo_existente_ids = {r.colaborador_id for r in formset_queryset}
        
        initial_data_for_new_forms = []
        for colab in colaboradores_queryset:
            if colab.id not in colaboradores_com_absenteismo_existente_ids:
                initial_data_for_new_forms.append({
                    'colaborador': colab.id,
                    'data_inicio': selected_date,
                    'data_fim': selected_date,
                    'tipo_absenteismo': None, # Padrão para "não ausente"
                    'observacoes': '',
                })
        
        formset = RegistroAbsenteismoDiarioFormSet(
            queryset=formset_queryset, # Instâncias existentes
            initial=initial_data_for_new_forms # Dados para novos formulários
        )

    # Contexto para o template
    context = {
        'formset': formset,
        'selected_date': selected_date,
        'selected_turno': selected_turno,
        'tipos_absenteismo': TipoAbsenteismo.objects.all().order_by('descricao'),
        'colaboradores_queryset': colaboradores_queryset, # Alterado para manter consistência com o nome da variável
        'absenteismos_dict': absenteismos_dict, # Ainda útil para lookup rápido no template, mas `formset` é o principal
        'active_page': 'marcar_absenteismo_diario',
    }
    return render(request, 'rh/absenteismo/marcar_absenteismo_diario.html', context)


def relatorio_absenteismo_form(request):
    form = RelatorioAbsenteismoFilterForm(request.GET or None)
    relatorio_data = []

    if form.is_valid():
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        colaborador_filtro = form.cleaned_data.get('colaborador')
        tipo_contrato_filtro = form.cleaned_data.get('tipo_contrato')
        tipo_absenteismo_filtro = form.cleaned_data.get('tipo_absenteismo')
        sigla_absenteismo_filtro = form.cleaned_data.get('sigla_absenteismo') # NOVO FILTRO
        cargo_filtro = form.cleaned_data.get('cargo')
        observacoes_filtro = form.cleaned_data.get('observacoes')

        # Começa com todos os registros de absenteísmo
        queryset = RegistroAbsenteismoDiario.objects.all()

        # Aplica filtros
        if data_inicio:
            queryset = queryset.filter(data_inicio__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data_fim__lte=data_fim)
        if colaborador_filtro:
            queryset = queryset.filter(colaborador=colaborador_filtro)
        if tipo_contrato_filtro:
            # Assumindo que ColaboradorEPI tem um campo tipo_contrato que é ForeignKey para TipoContrato
            queryset = queryset.filter(colaborador__tipo_contrato=tipo_contrato_filtro)
        if tipo_absenteismo_filtro:
            queryset = queryset.filter(tipo_absenteismo=tipo_absenteismo_filtro)
        if sigla_absenteismo_filtro: # Aplica filtro pela sigla
            queryset = queryset.filter(tipo_absenteismo__sigla__icontains=sigla_absenteismo_filtro)
        if cargo_filtro:
            # Assumindo que ColaboradorEPI tem um campo cargo que é ForeignKey para Cargo
            queryset = queryset.filter(colaborador__cargo=cargo_filtro)
        if observacoes_filtro:
            queryset = queryset.filter(observacoes__icontains=observacoes_filtro)

        # Ordenar para garantir consistência
        queryset = queryset.order_by('data_inicio', 'colaborador__nome_completo')

        # Processar os dados para exibição no template
        for registro in queryset:
            # Gerar uma entrada para cada dia do absenteísmo
            current_date = registro.data_inicio
            while current_date <= registro.data_fim:
                relatorio_data.append({
                    'data': current_date.strftime('%d/%m/%Y'),
                    'colaborador': registro.colaborador.nome_completo if registro.colaborador else '',
                    'tipo_contrato': registro.colaborador.tipo_contrato.nome if registro.colaborador and registro.colaborador.tipo_contrato else '',
                    'tipo_absenteismo': registro.tipo_absenteismo.descricao if registro.tipo_absenteismo else '',
                    'sigla_absenteismo': registro.tipo_absenteismo.sigla if registro.tipo_absenteismo else '', # Adicionando a sigla
                    'cargo': registro.colaborador.cargo.nome if registro.colaborador and registro.colaborador.cargo else '',
                    'observacoes': registro.observacoes or '',
                })
                current_date += timedelta(days=1)
    
    # Adicionar o mesmo tratamento de filtro para a função de exportação também
    # def exportar_relatorio_absenteismo_csv(request):
    # (Não incluído aqui para brevidade, mas você deve atualizar essa view também)
    
    context = {
        'form': form,
        'relatorio_data': relatorio_data,
    }
    return render(request, 'rh/absenteismo/relatorio_absenteismo_form.html', context)


# ... (sua função exportar_relatorio_absenteismo_csv também precisará ser atualizada para usar o filtro sigla_absenteismo_filtro) ...
def exportar_relatorio_absenteismo_csv(request):
    """
    Exporta o relatório de absenteísmo para um arquivo CSV,
    aplicando os mesmos filtros da visualização HTML.
    """
    form = RelatorioAbsenteismoFilterForm(request.GET)
    registros = []

    if form.is_valid():
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        colaborador_filtro = form.cleaned_data.get('colaborador')
        tipo_contrato_filtro = form.cleaned_data.get('tipo_contrato')
        tipo_absenteismo_filtro = form.cleaned_data.get('tipo_absenteismo')
        sigla_absenteismo_filtro = form.cleaned_data.get('sigla_absenteismo') # NOVO FILTRO AQUI TAMBÉM
        cargo_filtro = form.cleaned_data.get('cargo')
        observacoes_filtro = form.cleaned_data.get('observacoes')

        queryset = RegistroAbsenteismoDiario.objects.all()

        if data_inicio:
            queryset = queryset.filter(data_inicio__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data_fim__lte=data_fim)
        if colaborador_filtro:
            queryset = queryset.filter(colaborador=colaborador_filtro)
        if tipo_contrato_filtro:
            queryset = queryset.filter(colaborador__tipo_contrato=tipo_contrato_filtro)
        if tipo_absenteismo_filtro:
            queryset = queryset.filter(tipo_absenteismo=tipo_absenteismo_filtro)
        if sigla_absenteismo_filtro: # Aplica filtro pela sigla
            queryset = queryset.filter(tipo_absenteismo__sigla__icontains=sigla_absenteismo_filtro)
        if cargo_filtro:
            queryset = queryset.filter(colaborador__cargo=cargo_filtro)
        if observacoes_filtro:
            queryset = queryset.filter(observacoes__icontains=observacoes_filtro)

        queryset = queryset.order_by('data_inicio', 'colaborador__nome_completo')

        for registro in queryset:
            current_date = registro.data_inicio
            while current_date <= registro.data_fim:
                registros.append({
                    'data': current_date.strftime('%d/%m/%Y'),
                    'colaborador': registro.colaborador.nome_completo if registro.colaborador else '',
                    'tipo_contrato': registro.colaborador.tipo_contrato.nome if registro.colaborador and registro.colaborador.tipo_contrato else '',
                    'tipo_absenteismo': registro.tipo_absenteismo.descricao if registro.tipo_absenteismo else '',
                    'sigla_absenteismo': registro.tipo_absenteismo.sigla if registro.tipo_absenteismo else '', # Adicionando a sigla no export
                    'cargo': registro.colaborador.cargo.nome if registro.colaborador and registro.colaborador.cargo else '',
                    'observacoes': registro.observacoes or '',
                    'justificativa': registro.justificativa or '',
                    'atestado_medico': 'Sim' if registro.atestado_medico else 'Não',
                })
                current_date += timedelta(days=1)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="relatorio_absenteismo.csv"'

    writer = csv.writer(response, delimiter=';')

    headers = [
        'Data', 'Colaborador', 'Tipo Contrato', 'Tipo Absenteísmo', 'Sigla Absenteísmo', # Novo cabeçalho
        'Cargo', 'Observacoes', 'Justificativa', 'Atestado Medico'
    ]
    writer.writerow(headers)

    for item in registros:
        writer.writerow([
            item['data'],
            item['colaborador'],
            item['tipo_contrato'],
            item['tipo_absenteismo'],
            item['sigla_absenteismo'], # Novo item
            item['cargo'],
            item['observacoes'],
            item['justificativa'],
            item['atestado_medico'],
        ])

    return response
