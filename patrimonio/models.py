# pat/patrimonio/models.py

from django.db import models
from django.utils import timezone
from django.conf import settings # Importar settings para AUTH_USER_MODEL

# --- Modelo para Categoria de Patrimônio ---
class CategoriaPatrimonio(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição da Categoria")

    class Meta:
        verbose_name = "Categoria de Patrimônio"
        verbose_name_plural = "Categorias de Patrimônio"
        ordering = ['nome']

    def __str__(self):
        return self.nome

# --- Modelo para Localização de Patrimônio ---
class LocalizacaoPatrimonio(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Localização")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição da Localização")

    class Meta:
        verbose_name = "Localização de Patrimônio"
        verbose_name_plural = "Localizações de Patrimônio"
        ordering = ['nome']

    def __str__(self):
        return self.nome

# --- Modelo Principal para Item de Patrimônio ---
class ItemPatrimonio(models.Model):
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('BAIXADO', 'Baixado'),
        ('TRANSFERIDO', 'Transferido'),
    ]

    ESTADO_CONSERVACAO_CHOICES = [
        ('NOVO', 'Novo'),
        ('BOM', 'Bom'),
        ('REGULAR', 'Regular'),
        ('RUIM', 'Ruim'),
        ('SUCATA', 'Sucata'),
    ]

    nome = models.CharField(max_length=200, verbose_name="Nome do Bem Patrimonial")
    codigo_patrimonial = models.CharField(max_length=100, unique=True, verbose_name="Código Patrimonial")
    numero_serie = models.CharField(max_length=100, blank=True, null=True, unique=True, verbose_name="Número de Série (Opcional)")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição Detalhada")

    data_aquisicao = models.DateField(verbose_name="Data de Aquisição")
    valor_aquisicao = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor de Aquisição (R$)")

    estado_conservacao = models.CharField(
        max_length=20,
        choices=ESTADO_CONSERVACAO_CHOICES,
        default='BOM',
        verbose_name="Estado de Conservação"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ATIVO',
        verbose_name="Status do Item"
    )
    data_baixa = models.DateField(null=True, blank=True, verbose_name="Data da Baixa")
    motivo_baixa = models.TextField(null=True, blank=True, verbose_name="Motivo da Baixa")

    categoria = models.ForeignKey(
        CategoriaPatrimonio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='itens_patrimonio',
        verbose_name="Categoria"
    )
    localizacao = models.ForeignKey(
        LocalizacaoPatrimonio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='itens_patrimonio',
        verbose_name="Localização Atual"
    )

    responsavel_atual = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bens_patrimonio_responsavel',
        verbose_name="Responsável Atual"
    )

    # NOVO CAMPO: Usuário que registrou o item
    usuario_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='itens_registrados',
        verbose_name="Registrado Por"
    )

    # data_ultima_atualizacao com auto_now=True já é o ideal.
    # Ele será atualizado automaticamente em cada .save() do ItemPatrimonio.
    data_ultima_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro no Sistema")

    class Meta:
        verbose_name = "Item de Patrimônio"
        verbose_name_plural = "Itens de Patrimônio"
        ordering = ['nome', 'codigo_patrimonial']

    def __str__(self):
        return f"{self.nome} ({self.codigo_patrimonial})"


# --- Modelo para Movimentação/Histórico de Patrimônio ---
class MovimentacaoPatrimonio(models.Model):
    # Tipos de movimentação
    TIPO_CHOICES = [
        ('AQUISICAO', 'Aquisição'),
        ('TRANSFERENCIA', 'Transferência'),
        ('BAIXA', 'Baixa'),
        ('MANUTENCAO', 'Manutenção'),
        ('INVENTARIO', 'Inventário'), # Importante para o relatório
    ]

    item = models.ForeignKey(ItemPatrimonio, on_delete=models.CASCADE, related_name='movimentacoes', verbose_name="Item de Patrimônio")
    tipo_movimentacao = models.CharField(max_length=50, choices=TIPO_CHOICES, verbose_name="Tipo de Movimentação")
    data_movimentacao = models.DateTimeField(default=timezone.now, verbose_name="Data da Movimentação")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações da Movimentação")

    localizacao_origem = models.ForeignKey(
        LocalizacaoPatrimonio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_origem',
        verbose_name="Localização de Origem"
    )
    localizacao_destino = models.ForeignKey(
        LocalizacaoPatrimonio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_destino',
        verbose_name="Localização de Destino"
    )

    responsavel_origem = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_resp_origem',
        verbose_name="Responsável de Origem"
    )
    responsavel_destino = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_resp_destino',
        verbose_name="Responsável de Destino" # CORRIGIDO: de verbose_2name para verbose_name
    )

    usuario_registro = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_registradas',
        verbose_name="Usuário do Registro"
    )

    class Meta:
        verbose_name = "Movimentação de Patrimônio"
        verbose_name_plural = "Movimentações de Patrimônio"
        ordering = ['-data_movimentacao']

    # SOBRESCRITA DO MÉTODO save() PARA ATUALIZAR data_ultima_atualizacao DO ITEM
    def save(self, *args, **kwargs):
        # Primeiro, salva a movimentação
        super().save(*args, **kwargs)
        
        # Agora, garante que a data_ultima_atualizacao do ItemPatrimonio associado seja atualizada.
        # Isso é fundamental para o relatório de inventário.
        if self.item:
            # O auto_now=True no campo data_ultima_atualizacao do ItemPatrimonio
            # já garante que ele seja atualizado quando o item é salvo.
            # Basta chamar save() no item.
            self.item.save()

    def __str__(self):
        return f"Movimentação de {self.item.nome} - {self.get_tipo_movimentacao_display()} em {self.data_movimentacao.strftime('%d/%m/%Y %H:%M')}"
    
class ColetaInventario(models.Model):
    """
    Registra cada vez que um item de patrimônio é coletado/escaneado em um inventário.
    """
    item_patrimonio = models.ForeignKey(
        'ItemPatrimonio',
        on_delete=models.CASCADE,
        related_name='coletas_inventario',
        verbose_name="Item de Patrimônio"
    )
    data_coleta = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data e Hora da Coleta"
    )
    localizacao_coleta = models.ForeignKey(
        'LocalizacaoPatrimonio', # Assumindo que você tem este modelo
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Localização da Coleta"
    )
    usuario_coleta = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Referência ao modelo User
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Usuário que Coletou"
    )
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações da Coleta"
    )

    class Meta:
        verbose_name = "Coleta de Inventário"
        verbose_name_plural = "Coletas de Inventário"
        ordering = ['-data_coleta']

    def __str__(self):
        return f"Coleta de {self.item_patrimonio.codigo_patrimonial} em {self.data_coleta.strftime('%d/%m/%Y %H:%M')}"
