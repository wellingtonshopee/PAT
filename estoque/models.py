# pat/estoque/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model # Para pegar o modelo de usuário atual

User = get_user_model() # Obtém o modelo de usuário ativo no projeto

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nome'] # Ordenar por nome por padrão

    def __str__(self):
        return self.nome

class Localizacao(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Localização"
        verbose_name_plural = "Localizações"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class ItemEstoque(models.Model):
    nome = models.CharField(max_length=200, unique=True, verbose_name="Nome do Item") # Adicionado unique=True para nome
    codigo_interno = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Código Interno (Opcional)")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição Detalhada")
    quantidade = models.PositiveIntegerField(default=0, verbose_name="Quantidade Atual")
    unidade_medida = models.CharField(max_length=50, default="un", verbose_name="Unidade de Medida (Ex: un, kg, m)")
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Preço Unitário (R$)")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='itens', verbose_name="Categoria")
    localizacao = models.ForeignKey(Localizacao, on_delete=models.SET_NULL, null=True, blank=True, related_name='itens', verbose_name="Localização no Estoque")
    data_ultima_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    estoque_minimo = models.PositiveIntegerField(default=5, verbose_name="Estoque Mínimo")

    class Meta:
        verbose_name = "Item de Estoque"
        verbose_name_plural = "Itens de Estoque"
        # Ajustei a ordenação para ser apenas por nome, que é mais comum
        # se precisar por categoria depois, pode ser feito na queryset da view.
        ordering = ['nome'] 

    def __str__(self):
        # Representação em string do objeto, útil para o Admin
        return f"{self.nome} ({self.quantidade} {self.unidade_medida})"
    
    # Propriedade para verificar se o item está abaixo do estoque mínimo
    @property
    def is_abaixo_estoque_minimo(self):
        # Retorna True se a quantidade for menor ou igual ao mínimo E não for zero
        return self.quantidade <= self.estoque_minimo and self.quantidade > 0

    # Propriedade para verificar se o item está zerado
    @property
    def is_estoque_zerado(self):
        return self.quantidade == 0
    
class MovimentacaoEstoque(models.Model):
    TIPO_MOVIMENTACAO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
    ]

    item = models.ForeignKey(ItemEstoque, on_delete=models.PROTECT, related_name='movimentacoes', verbose_name="Item")
    tipo_movimentacao = models.CharField(max_length=10, choices=TIPO_MOVIMENTACAO_CHOICES, verbose_name="Tipo de Movimentação")
    quantidade_movimentada = models.PositiveIntegerField(verbose_name="Quantidade Movimentada")
    data_hora_movimentacao = models.DateTimeField(auto_now_add=True, verbose_name="Data e Hora")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição/Motivo")
    movimentado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='movimentacoes_realizadas', verbose_name="Movimentado Por")

    class Meta:
        verbose_name = "Movimentação de Estoque"
        verbose_name_plural = "Movimentações de Estoque"
        ordering = ['-data_hora_movimentacao'] # Ordena do mais novo para o mais antigo

    def __str__(self):
        return f"{self.tipo_movimentacao} de {self.quantidade_movimentada} de {self.item.nome} em {self.data_hora_movimentacao.strftime('%d/%m/%Y %H:%M')}"