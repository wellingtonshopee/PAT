#pat/usuarios/middleware.py
import threading
from .utils import log_atividade # Assumindo que log_atividade está em pat/usuarios/utils

_thread_locals = threading.local()

def get_current_request():
    return getattr(_thread_locals, 'request', None)

class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request # Armazena a requisição no thread local

        # Log de acesso à página (exclua arquivos estáticos/media para não sobrecarregar)
        if not request.path.startswith(('/static/', '/media/', '/admin/js/')): # Filtra URLs que geralmente não precisam de log de acesso
            log_atividade(
                request.user,
                "Acesso à URL",
                f"Acessou: {request.method} {request.path}",
                request=request
            )

        response = self.get_response(request)

        # Limpa o request do thread local
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request

        return response