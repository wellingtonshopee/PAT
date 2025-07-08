# usuarios/middleware.py

from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve, Resolver404 # Importe Resolver404 para lidar com URLs não encontradas
from .models import LogAtividade
from django.contrib.auth import get_user_model
import json
import logging
from django.http import HttpRequest # Importe HttpRequest para type hinting

logger = logging.getLogger(__name__)
User = get_user_model()

class RequestLogMiddleware(MiddlewareMixin): # <--- NOME DA CLASSE AJUSTADO AQUI!
    """
    Middleware para registrar atividades do usuário (criação, atualização, exclusão, acesso a páginas)
    no sistema.
    """

    def process_view(self, request: HttpRequest, view_func, view_args, view_kwargs):
        """
        Processa a requisição antes da view ser chamada para capturar o nome da view.
        """
        try:
            request._view_name = resolve(request.path_info).view_name
        except Resolver404:
            request._view_name = 'URL_não_encontrada' # Define um nome para URLs que não resolvem
        return None

    def process_response(self, request: HttpRequest, response):
        """
        Processa a resposta para registrar a atividade após a view ser executada.
        """
        # Excluir requisições de arquivos estáticos, favicon, etc.
        if request.path.startswith('/static/') or request.path.endswith(('favicon.ico', '.js', '.css', '.png', '.jpg', '.gif')):
            return response

        # Não logar requisições AJAX GET que não sejam críticas para evitar logs excessivos
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'GET':
             return response

        user = request.user if request.user.is_authenticated else None
        acao = None
        descricao = None
        ip_endereco = self._get_client_ip(request)

        # Captura o nome da view que foi processada
        view_name = getattr(request, '_view_name', 'Desconhecida')

        if request.method in ['POST', 'PUT', 'DELETE']: # Agrupa os métodos que geralmente alteram dados
            url_name = getattr(request.resolver_match, 'url_name', 'Nome_URL_Desconhecido')

            # --- Lógica para POST, PUT, DELETE ---
            if 'login' in url_name:
                acao = "Login de Usuário"
                descricao = f"Tentativa de login para o usuário: {request.POST.get('username', 'N/A')}"
                if user and user.is_authenticated: # Verifica se o usuário autenticou com sucesso
                    descricao = f"Login bem-sucedido para o usuário: {user.username}"
            elif 'logout' in url_name:
                acao = "Logout de Usuário"
                descricao = f"Logout do usuário: {user.username}" if user else "Logout de usuário desconhecido"
            elif 'adicionar' in url_name:
                acao = f"Criação de Registro ({view_name})"
                descricao = f"Usuário {user.username if user else 'anônimo'} criou um registro via view: {view_name}."
                try:
                    # Limita o tamanho da descrição e evita dados sensíveis
                    post_data_str = json.dumps(request.POST.dict())
                    descricao += f" Dados iniciais: {post_data_str[:200]}..." if len(post_data_str) > 200 else f" Dados iniciais: {post_data_str}"
                except Exception as e:
                    logger.warning(f"Não foi possível logar dados do POST para {view_name}: {e}")
            elif 'editar' in url_name:
                acao = f"Atualização de Registro ({view_name})"
                descricao = f"Usuário {user.username if user else 'anônimo'} atualizou um registro via view: {view_name}."
                try:
                    # Limita o tamanho da descrição
                    post_data_str = json.dumps(request.POST.dict())
                    descricao += f" Dados atualizados: {post_data_str[:200]}..." if len(post_data_str) > 200 else f" Dados atualizados: {post_data_str}"
                except Exception as e:
                    logger.warning(f"Não foi possível logar dados do POST para {view_name}: {e}")
            elif 'excluir' in url_name:
                acao = f"Exclusão de Registro ({view_name})"
                descricao = f"Usuário {user.username if user else 'anônimo'} excluiu um registro via view: {view_name}."
            else:
                # Ação padrão para requisições POST/PUT/DELETE não classificadas
                acao = f"Requisição {request.method} ({view_name})"
                descricao = f"Usuário {user.username if user else 'anônimo'} realizou um {request.method} na URL: {request.path}"
            # --- Fim da lógica para POST, PUT, DELETE ---

            if acao: # Garante que só registre se uma ação relevante for identificada
                try:
                    LogAtividade.objects.create(
                        usuario=user,
                        acao=acao,
                        descricao=descricao,
                        ip_endereco=ip_endereco
                    )
                except Exception as e:
                    logger.error(f"Erro ao registrar log de atividade para {request.method} na URL {request.path}: {e}", exc_info=True)

        elif request.method == 'GET':
            # Logar acessos a páginas importantes (e que não são AJAX GETs ou arquivos estáticos, já filtrados)
            # Exclui views do admin se não quiser logar cada acesso ao admin (ajustável)
            if view_name and not view_name.startswith('admin:'):
                # Exemplos de views importantes para logar acesso (adicione ou remova conforme necessidade)
                if view_name in ['home', 'usuarios:log_atividades', 'patrimonio:lista_patrimonios', 'rh:absenteismo_home', 'rh:relatorio_absenteismo_form']:
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
                        logger.error(f"Erro ao registrar log de atividade GET na URL {request.path}: {e}", exc_info=True)

        return response

    def _get_client_ip(self, request: HttpRequest):
        """
        Tenta obter o endereço IP do cliente, considerando proxies como o Nginx ou Render.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip