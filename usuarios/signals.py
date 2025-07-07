from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import LogAtividade
from django.contrib.auth.models import User
from rh.models import ColaboradorEPI, RegistroAbsenteismoDiario # Importe os modelos que deseja logar
# ... importe outros modelos importantes de outros apps ...

# Suponha que get_client_ip esteja em usuarios.utils
from .utils import get_client_ip

# Funções auxiliares (se preferir extrair a lógica)
def create_log(sender, instance, action, description, request=None):
    # Aqui você precisaria de uma forma de obter o usuário da requisição
    # para post_save/post_delete, o que é mais complexo com signals
    # sem middleware. Por enquanto, user e IP podem ser nulos ou requerem
    # uma abordagem diferente para serem preenchidos em signals.
    # Vamos assumir que para signals, o 'request' não está disponível diretamente.

    # Uma forma é usar um thread-local para armazenar o request.user e IP
    # (veja a seção de Middleware abaixo para uma solução mais robusta).
    # Por simplicidade, para signals diretos, user e IP podem ser 'Sistema'.

    # Para demonstração:
    LogAtividade.objects.create(
        usuario=getattr(instance, 'updated_by', None) or getattr(instance, 'created_by', None) or None, # Tente pegar usuário se o modelo tiver campo de quem atualizou/criou
        acao=action,
        descricao=description,
        # ip_endereco=get_client_ip(request) # Não temos request aqui facilmente
    )

# --- Sinais para Modelos Específicos ---

@receiver(post_save, sender=User)
def log_user_save(sender, instance, created, **kwargs):
    action = "Criação de Usuário" if created else "Atualização de Usuário"
    description = f"Usuário '{instance.username}' {'criado' if created else 'atualizado'}."
    # Note: Aqui o 'usuario' do LogAtividade seria 'None' ou você precisaria de um contexto global
    LogAtividade.objects.create(usuario=None, acao=action, descricao=description)

@receiver(post_delete, sender=User)
def log_user_delete(sender, instance, **kwargs):
    LogAtividade.objects.create(
        usuario=None, # Quem deletou é mais difícil de saber aqui
        acao="Exclusão de Usuário",
        descricao=f"Usuário '{instance.username}' excluído."
    )

@receiver(post_save, sender=ColaboradorEPI)
def log_colaborador_save(sender, instance, created, **kwargs):
    action = "Cadastro de Colaborador" if created else "Atualização de Colaborador"
    description = f"Colaborador '{instance.nome_completo}' {'cadastrado' if created else 'atualizado'}."
    LogAtividade.objects.create(usuario=None, acao=action, descricao=description) # User e IP seriam nulos

@receiver(post_delete, sender=ColaboradorEPI)
def log_colaborador_delete(sender, instance, **kwargs):
    LogAtividade.objects.create(
        usuario=None,
        acao="Exclusão de Colaborador",
        descricao=f"Colaborador '{instance.nome_completo}' excluído."
    )

# Adicione sinais para outros modelos importantes como RegistroAbsenteismoDiario
@receiver(post_save, sender=RegistroAbsenteismoDiario)
def log_absenteismo_save(sender, instance, created, **kwargs):
    action = "Registro de Absenteísmo" if created else "Atualização de Absenteísmo"
    description = f"Absenteísmo de '{instance.colaborador.nome_completo}' em '{instance.data_inicio.strftime('%d/%m/%Y')}' {'registrado' if created else 'atualizado'} para '{instance.tipo_absenteismo.descricao if instance.tipo_absenteismo else 'Nenhum'}'. Obs: '{instance.observacoes}'."
    LogAtividade.objects.create(usuario=None, acao=action, descricao=description)

@receiver(post_delete, sender=RegistroAbsenteismoDiario)
def log_absenteismo_delete(sender, instance, **kwargs):
    LogAtividade.objects.create(
        usuario=None,
        acao="Exclusão de Absenteísmo",
        descricao=f"Absenteísmo de '{instance.colaborador.nome_completo}' em '{instance.data_inicio.strftime('%d/%m/%Y')}' excluído."
    )