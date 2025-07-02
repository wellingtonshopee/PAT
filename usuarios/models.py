# usuarios/models.py
from django.db import models
from django.conf import settings # Para referenciar o modelo de usuário

class LogAtividade(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário")
    acao = models.CharField(max_length=255, verbose_name="Ação")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora")
    ip_endereco = models.GenericIPAddressField(blank=True, null=True, verbose_name="Endereço IP")

    class Meta:
        verbose_name = "Log de Atividade"
        verbose_name_plural = "Logs de Atividades"
        ordering = ['-data_hora'] # Ordena os logs do mais recente para o mais antigo

    def __str__(self):
        return f"{self.data_hora.strftime('%d/%m/%Y %H:%M')} - {self.acao} por {self.usuario.username if self.usuario else 'Anônimo'}"