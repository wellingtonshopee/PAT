# C:\Users\SEAOps\Documents\pat\clientes\models.py

from django.db import models
from django.utils import timezone

class Cliente(models.Model):
    razao_social = models.CharField(max_length=255, unique=True, verbose_name="Razão Social / Nome Completo")
    nome_fantasia = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome Fantasia")
    cnpj_cpf = models.CharField(max_length=18, unique=True, blank=True, null=True, verbose_name="CNPJ/CPF")
    data_nascimento = models.DateField(blank=True, null=True, verbose_name="Data de Nascimento") # NOVO CAMPO
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    # Manter 'endereco' para o endereço completo descritivo
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço Completo")
    cep = models.CharField(max_length=9, blank=True, null=True, verbose_name="CEP") # NOVO CAMPO
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade") # NOVO CAMPO
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado (UF)") # NOVO CAMPO
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['razao_social']

    def __str__(self):
        return self.razao_social