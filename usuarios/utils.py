# pat/usuarios/utils.py

from .models import LogAtividade # Importe o seu modelo de LogAtividade
from django.utils import timezone # Para usar timezone.now()
from django.contrib.auth import get_user_model # Para obter o modelo de usuário

User = get_user_model() # Obtém o modelo de usuário configurado no settings

def get_client_ip(request):
    """
    Retorna o endereço IP do cliente que fez a requisição.
    Lida com proxies como NGINX ou cloudflared.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_atividade(user, action, description=None, request=None):
    """
    Registra uma atividade no sistema.

    Args:
        user (User): O objeto User que realizou a ação. Pode ser None para ações do sistema.
        action (str): Ação realizada (ex: "Cadastro de Usuário", "Atualização de Perfil").
        description (str, optional): Descrição detalhada da atividade. Defaults to None.
        request (HttpRequest, optional): Objeto da requisição HTTP para extrair o IP. Defaults to None.
    """
    ip_address = get_client_ip(request) if request else None

    # Verifica se o usuário é válido antes de tentar usá-lo
    if user and not user.is_authenticated:
        user = None # Não logar usuário anônimo ou inválido

    LogAtividade.objects.create(
        usuario=user,
        acao=action,
        descricao=description,
        data_hora=timezone.now(), # Usa timezone.now() para garantir compatibilidade com USE_TZ
        ip_endereco=ip_address
    )