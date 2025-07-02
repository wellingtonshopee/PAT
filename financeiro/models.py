# C:\Users\SEAOps\Documents\pat\financeiro\models.py

from django.db import models
from django.conf import settings # Para referenciar o User model (registrado_por)
from django.utils import timezone # Para campos de data/hora
from decimal import Decimal # Para valores monetários precisos

# Assumindo que seu app 'fornecedores' já existe e tem o modelo Fornecedor.
# Se não tiver, por favor, me avise para ajustarmos esta linha.
from fornecedores.models import Fornecedor
from clientes.models import Cliente # Importa o modelo Cliente do seu app 'clientes'


# --- MÓDULOS FINANCEIROS ---

class CategoriaFinanceira(models.Model):
    """
    Categorias para classificar as contas a pagar e a receber (ex: Aluguel, Vendas, Salários).
    """
    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome da Categoria"
    )
    tipo = models.CharField(
        max_length=10,
        choices=[('RECEITA', 'Receita'), ('DESPESA', 'Despesa')],
        verbose_name="Tipo"
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição"
    )

    class Meta:
        verbose_name = "Categoria Financeira"
        verbose_name_plural = "Categorias Financeiras"
        ordering = ['tipo', 'nome']

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.nome}"

class FormaPagamento(models.Model):
    """
    Formas de pagamento utilizadas (ex: Dinheiro, Cartão de Crédito, Pix, Boleto).
    """
    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome da Forma de Pagamento"
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição"
    )

    class Meta:
        verbose_name = "Forma de Pagamento"
        verbose_name_plural = "Formas de Pagamento"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class ContaPagar(models.Model):
    """
    Representa uma conta a ser paga pela empresa.
    """
    STATUS_CHOICES = [
        ('A_PAGAR', 'A Pagar'),
        ('PAGA', 'Paga'),
        ('VENCIDA', 'Vencida'),
        ('CANCELADA', 'Cancelada'),
    ]

    descricao = models.CharField(
        max_length=255,
        verbose_name="Descrição"
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor"
    )
    data_lancamento = models.DateField(
        default=timezone.now,
        verbose_name="Data de Lançamento"
    )
    data_vencimento = models.DateField(
        verbose_name="Data de Vencimento"
    )
    data_pagamento = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data de Pagamento"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='A_PAGAR',
        verbose_name="Status"
    )
    categoria = models.ForeignKey(
        CategoriaFinanceira,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'tipo': 'DESPESA'}, # Restringe a categorias de despesa
        related_name='contas_pagar',
        verbose_name="Categoria"
    )
    forma_pagamento = models.ForeignKey(
        FormaPagamento,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Forma de Pagamento"
    )
    fornecedor = models.ForeignKey(
        Fornecedor, # Referencia o modelo Fornecedor importado
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='contas_a_pagar',
        verbose_name="Fornecedor"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='contas_pagar_registradas',
        verbose_name="Registrado por"
    )
    data_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Registro"
    )
    data_ultima_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        verbose_name = "Conta a Pagar"
        verbose_name_plural = "Contas a Pagar"
        ordering = ['data_vencimento', 'status']

    def __str__(self):
        return f"Pagar: {self.descricao} - R${self.valor:.2f} (Venc: {self.data_vencimento})"

    def save(self, *args, **kwargs):
        # Atualiza o status se a data de vencimento for ultrapassada e não estiver paga/cancelada
        if self.status not in ['PAGA', 'CANCELADA'] and self.data_vencimento and self.data_vencimento < timezone.localdate():
            self.status = 'VENCIDA'
        super().save(*args, **kwargs)

class ContaReceber(models.Model):
    """
    Representa uma conta a ser recebida pela empresa.
    """
    STATUS_CHOICES = [
        ('A_RECEBER', 'A Receber'),
        ('RECEBIDA', 'Recebida'),
        ('VENCIDA', 'Vencida'),
        ('CANCELADA', 'Cancelada'),
    ]

    descricao = models.CharField(
        max_length=255,
        verbose_name="Descrição"
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor"
    )
    data_lancamento = models.DateField(
        default=timezone.now,
        verbose_name="Data de Lançamento"
    )
    data_vencimento = models.DateField(
        verbose_name="Data de Vencimento"
    )
    data_recebimento = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data de Recebimento"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='A_RECEBER',
        verbose_name="Status"
    )
    categoria = models.ForeignKey(
        CategoriaFinanceira,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'tipo': 'RECEITA'}, # Restringe a categorias de receita
        related_name='contas_receber',
        verbose_name="Categoria"
    )
    forma_pagamento = models.ForeignKey(
        FormaPagamento,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Forma de Recebimento"
    )

    data_pagamento = models.DateField(null=True, blank=True) 
    
    # AJUSTE CRÍTICO: Aponta para o modelo Cliente do seu app 'clientes'
    cliente = models.ForeignKey(
        Cliente, # CORRIGIDO: Aponta para o seu modelo Cliente
        on_delete=models.SET_NULL, # Ou models.PROTECT se desejar impedir exclusão de cliente com CR
        null=True, blank=True,
        related_name='contas_a_receber_cliente', # Renomeado para evitar conflito com 'contas_a_receber' do User
        verbose_name="Cliente"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='contas_receber_registradas',
        verbose_name="Registrado por"
    )
    data_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Registro"
    )
    data_ultima_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        verbose_name = "Conta a Receber"
        verbose_name_plural = "Contas a Receber"
        ordering = ['data_vencimento', 'status']

    def __str__(self):
        return f"Receber: {self.descricao} - R${self.valor:.2f} (Venc: {self.data_vencimento})"

    def save(self, *args, **kwargs):
        # Atualiza o status se a data de vencimento for ultrapassada e não estiver recebida/cancelada
        if self.status not in ['RECEBIDA', 'CANCELADA'] and self.data_vencimento and self.data_vencimento < timezone.localdate():
            self.status = 'VENCIDA'
        super().save(*args, **kwargs)

    # Propriedades como 'saldo_devedor', 'esta_atrasada', 'esta_paga'
    # foram removidas/ajustadas para refletir a nova estrutura de campos
    # (sem valor_original/valor_recebido explícitos para cálculo de saldo).
    # Se precisar delas, o modelo precisará ser reavaliado para incluir campos de valor_recebido.