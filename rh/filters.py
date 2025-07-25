from django.shortcuts import render
from django.db.models import Q
from .models import RegistroAbsenteismo, TipoAbsenteismo

def listar_registros_absenteismo(request):
    """
    View para listar registros de absenteísmo com filtros opcionais por:
    - Nome do colaborador
    - Tipo de absenteísmo
    - Intervalo de datas (início e fim)
    """
    # Filtros recebidos via GET
    colaborador = request.GET.get('colaborador', '').strip()
    tipo = request.GET.get('tipo')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    # Busca inicial com relações otimizadas
    registros = RegistroAbsenteismo.objects.select_related('colaborador', 'tipo_absenteismo').all()

    # Aplica os filtros dinamicamente
    if colaborador:
        registros = registros.filter(colaborador__nome_completo__icontains=colaborador)

    if tipo:
        registros = registros.filter(tipo_absenteismo_id=tipo)

    if data_inicio:
        registros = registros.filter(data_inicio__gte=data_inicio)

    if data_fim:
        registros = registros.filter(data_fim__lte=data_fim)

    # Tipos disponíveis para filtro (combobox, etc)
    tipos_absenteismo = TipoAbsenteismo.objects.all().order_by('descricao')

    context = {
        'registros': registros,
        'tipos_absenteismo': tipos_absenteismo,
        'filtros': {
            'colaborador': colaborador,
            'tipo': tipo,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
        }
    }
    return render(request, 'absenteismo/listar_registros.html', context)
