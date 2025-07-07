from django.db.models import Q
from .models import RegistroAbsenteismo, TipoAbsenteismo

def listar_registros_absenteismo(request):
    registros = RegistroAbsenteismo.objects.select_related('colaborador', 'tipo_absenteismo').all()
    tipos_absenteismo = TipoAbsenteismo.objects.all()

    colaborador = request.GET.get('colaborador', '').strip()
    tipo = request.GET.get('tipo')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    if colaborador:
        registros = registros.filter(colaborador__nome_completo__icontains=colaborador)

    if tipo:
        registros = registros.filter(tipo_absenteismo_id=tipo)

    if data_inicio:
        registros = registros.filter(data_inicio__gte=data_inicio)

    if data_fim:
        registros = registros.filter(data_fim__lte=data_fim)

    context = {
        'registros': registros,
        'tipos_absenteismo': tipos_absenteismo
    }
    return render(request, 'absenteismo/listar_registros.html', context)
