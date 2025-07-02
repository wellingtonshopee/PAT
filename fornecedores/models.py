# pat/fornecedores/models.py

from django.db import models
from django.utils import timezone

# --- Modelo para Tipo de Fornecedor ---
class TipoFornecedor(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Tipo de Fornecedor")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição do Tipo")

    class Meta:
        verbose_name = "Tipo de Fornecedor"
        verbose_name_plural = "Tipos de Fornecedor"
        ordering = ['nome']

    def __str__(self):
        return self.nome

# --- Modelo Principal para Fornecedor ---
class Fornecedor(models.Model):
    nome_fantasia = models.CharField(max_length=200, verbose_name="Nome Fantasia")
    razao_social = models.CharField(max_length=255, unique=True, verbose_name="Razão Social")
    cnpj_cpf = models.CharField(max_length=18, unique=True, verbose_name="CNPJ/CPF") # Formato pode ser "XX.XXX.XXX/XXXX-XX" ou "XXX.XXX.XXX-XX"

    contato_principal = models.CharField(max_length=100, blank=True, null=True, verbose_name="Contato Principal")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name="E-mail")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço Completo")

    tipo_fornecedor = models.ForeignKey(
        TipoFornecedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fornecedores',
        verbose_name="Tipo de Fornecedor"
    )

    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_ultima_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ['nome_fantasia']

    def __str__(self):
        return self.nome_fantasia