# usuarios/middleware.py

from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from .models import LogAtividade
from django.contrib.auth import get_user_model
import json
import logging
from django.http import HttpRequest # Importe HttpRequest para type hinting

logger = logging.getLogger(__name__)
User = get_user_model()

class LogAtividadeMiddleware(MiddlewareMixin):
    """
    Middleware para registrar atividades do usuário (criação, atualização, exclusão)
    no sistema.
    """

    def process_view(self, request: HttpRequest, view_func, view_args, view_kwargs):
        """
        Processa a requisição antes da view ser chamada para capturar o nome da view.
        """
        request._view_name = resolve(request.path_info).view_name
        return None

    def process_response(self, request: HttpRequest, response):
        """
        Processa a resposta para registrar a atividade após a view ser executada.
        """
        # Excluir requisições de arquivos estáticos, favicon, etc.
        if request.path.startswith('/static/') or request.path.endswith(('favicon.ico', '.js', '.css', '.png', '.jpg', '.gif')):
            return response

        # Não logar requisições AJAX que não sejam POST/PUT/DELETE
        # if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method not in ['POST', 'PUT', 'DELETE']:
        #     return response

        user = request.user if request.user.is_authenticated else None
        acao = None
        descricao = None
        ip_endereco = self._get_client_ip(request)

        # Captura o nome da view que foi processada
        view_name = getattr(request, '_view_name', 'Desconhecida')

        if request.method == 'POST':
            if request.resolver_match and request.resolver_match.url_name:
                url_name = request.resolver_match.url_name
                
                # Exemplo de ações baseadas no nome da URL ou no path
                if 'login' in url_name:
                    acao = "Login de Usuário"
                    descricao = f"Tentativa de login para o usuário: {request.POST.get('username', 'N/A')}"
                    # Se o login falhar, user será None aqui, mas a ação ainda é registrada.
                    if user:
                        descricao = f"Login bem-sucedido para o usuário: {user.username}"
                elif 'logout' in url_name:
                    acao = "Logout de Usuário"
                    descricao = f"Logout do usuário: {user.username}" if user else "Logout de usuário desconhecido"
                elif 'adicionar' in url_name:
                    acao = f"Criação de Registro ({view_name})"
                    descricao = f"Usuário {user.username if user else 'anônimo'} criou um registro via view: {view_name}."
                    # Tentar adicionar dados do POST para mais detalhes (cuidado com dados sensíveis)
                    try:
                        descricao += f" Dados iniciais: {json.dumps(request.POST.dict(), indent=2)[:200]}..." # Limita o tamanho
                    except Exception:
                        pass
                elif 'editar' in url_name:
                    acao = f"Atualização de Registro ({view_name})"
                    descricao = f"Usuário {user.username if user else 'anônimo'} atualizou um registro via view: {view_name}."
                    try:
                        descricao += f" Dados atualizados: {json.dumps(request.POST.dict(), indent=2)[:200]}..."
                    except Exception:
                        pass
                elif 'excluir' in url_name:
                    acao = f"Exclusão de Registro ({view_name})"
                    descricao = f"Usuário {user.username if user else 'anônimo'} excluiu um registro via view: {view_name}."
                else:
                    # Ação padrão para POSTs não classificados
                    acao = f"Requisição POST ({view_name})"
                    descricao = f"Usuário {user.username if user else 'anônimo'} realizou um POST na URL: {request.path}"
            
            if acao: # Garante que só registre se uma ação relevante for identificada
                try:
                    LogAtividade.objects.create(
                        usuario=user,
                        acao=acao,
                        descricao=descricao,
                        ip_endereco=ip_endereco
                    )
                except Exception as e:
                    logger.error(f"Erro ao registrar log de atividade: {e}")

        elif request.method == 'GET' and not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Logar acessos a páginas importantes (não AJAX GETs)
            if view_name and not view_name.startswith('admin:'): # Exclui views do admin se não quiser logar cada acesso ao admin
                 # Exemplo: logar acesso a Home, lista de logs, etc.
                if view_name in ['home', 'usuarios:log_atividades', 'patrimonio:lista_patrimonios']:
                    acao = f"Acesso à Página ({view_name})"
                    descricao = f"Usuário {user.username if user else 'anônimo'} acessou a página: {request.path} ({view_name})"
                    try:
                        LogAtividade.objects.create(
                            usuario=user,
                            acao=acao,
                            descricao=descricao,
                            ip_endereco=ip_endereco
                        )
                    except Exception as e:
                        logger.error(f"Erro ao registrar log de atividade GET: {e}")

        return response

    def _get_client_ip(self, request: HttpRequest):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
