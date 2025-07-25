from django.db import models
from datetime import timedelta
from django.utils.timezone import localdate, now as timezone_now 
from django.core.validators import MinValueValidator # Adicionado para validação de notas

from epi.models import ColaboradorEPI 

# ==============================================================================
# Modelos de RH (Absenteísmo) - Versão Ajustada pelo Usuário
# ==============================================================================

class TipoContrato(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Contrato")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    class Meta:
        verbose_name = "Tipo de Contrato"
        verbose_name_plural = "Tipos de Contrato"
        ordering = ['nome'] # Adicionado ordenação para consistência

    def __str__(self):
        return self.nome

class Lider(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Líder")
    matricula = models.CharField(max_length=50, blank=True, null=True, verbose_name="Matrícula")

    class Meta:
        verbose_name = "Líder"
        verbose_name_plural = "Líderes"
        ordering = ['nome'] # Adicionado ordenação para consistência

    def __str__(self):
        return self.nome

class Cargo(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Cargo")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ['nome'] # Adicionado ordenação para consistência

    def __str__(self):
        return self.nome

# --- Modelos de Absenteísmo ---

class TipoAbsenteismo(models.Model):
    descricao = models.CharField(max_length=100, unique=True, verbose_name="Descrição do Tipo")
    sigla = models.CharField(max_length=10, unique=True, verbose_name="Sigla")
    e_ausencia = models.BooleanField(default=True, verbose_name="Conta como Ausência?") 

    class Meta:
        verbose_name = "Tipo de Absenteísmo"
        verbose_name_plural = "Tipos de Absenteísmo"
        ordering = ['descricao'] 

    def __str__(self):
        return f"{self.sigla} - {self.descricao}"

class RegistroAbsenteismoDiario(models.Model): 
    colaborador = models.ForeignKey(
        ColaboradorEPI, 
        on_delete=models.CASCADE, 
        related_name='registros_absenteismo_diario', 
        verbose_name="Colaborador"
    ) 
    
    tipo_absenteismo = models.ForeignKey(
        TipoAbsenteismo, 
        on_delete=models.PROTECT, 
        default=16, # Cuidado com valores default fixos, especialmente em produção
        verbose_name="Tipo de Absenteísmo"
    )

    data_inicio = models.DateField(verbose_name="Data Início")
    data_fim = models.DateField(verbose_name="Data Fim")
    
    justificativa = models.TextField(blank=True, null=True, verbose_name="Justificativa")
    atestado_medico = models.BooleanField(default=False, verbose_name="Atestado Médico?")

    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações") 
    
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro") 

    class Meta:
        verbose_name = "Registro de Absenteísmo Diário"
        verbose_name_plural = "Registros de Absenteísmo Diários"
        ordering = ['-data_inicio', 'colaborador__nome_completo']
        constraints = [
            models.UniqueConstraint(
                fields=['colaborador', 'data_inicio', 'data_fim', 'tipo_absenteismo'], 
                name='unique_registro_absenteismo_for_period'
            )
        ]

    def __str__(self):
        return f"{self.colaborador.nome_completo} - {self.tipo_absenteismo.sigla} ({self.data_inicio.strftime('%d/%m/%Y')})"

    @property
    def total_dias(self):
        if self.data_inicio and self.data_fim:
            return (self.data_fim - self.data_inicio).days + 1
        return 0

# ==============================================================================
# NOVOS MODELOS PARA TREINAMENTO (conforme definido anteriormente)
# ==============================================================================

class Treinamento(models.Model):
    """
    Representa um tipo de treinamento genérico (ex: NR-35, Primeiros Socorros).
    """
    nome = models.CharField(max_length=200, unique=True, verbose_name="Nome do Treinamento")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição do Treinamento")
    carga_horaria = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Carga Horária (horas)",
        help_text="Duração total do treinamento em horas."
    )
    ativo = models.BooleanField(default=True, verbose_name="Treinamento Ativo")

    class Meta:
        verbose_name = "Treinamento"
        verbose_name_plural = "Treinamentos"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class TurmaTreinamento(models.Model):
    """
    Representa uma instância específica de um treinamento, uma "turma".
    """
    treinamento = models.ForeignKey(
        Treinamento,
        on_delete=models.CASCADE,
        related_name='turmas',
        verbose_name="Treinamento"
    )
    data_realizacao = models.DateField(verbose_name="Data de Realização")
    horario_inicio = models.TimeField(blank=True, null=True, verbose_name="Horário de Início")
    horario_fim = models.TimeField(blank=True, null=True, verbose_name="Horário de Fim")
    local = models.CharField(max_length=255, blank=True, null=True, verbose_name="Local do Treinamento")
    instrutor = models.CharField(max_length=150, blank=True, null=True, verbose_name="Instrutor")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações da Turma")
    
    # Relação Many-to-Many com ColaboradorEPI através de ParticipacaoTurma
    participantes = models.ManyToManyField(
        ColaboradorEPI,
        through='ParticipacaoTurma',
        related_name='turmas_participadas',
        verbose_name="Participantes da Turma"
    )

    class Meta:
        verbose_name = "Turma de Treinamento"
        verbose_name_plural = "Turmas de Treinamento"
        ordering = ['-data_realizacao', 'treinamento__nome']
        unique_together = ('treinamento', 'data_realizacao', 'local')

    def __str__(self):
        return f"Turma de {self.treinamento.nome} em {self.data_realizacao.strftime('%d/%m/%Y')}"

class ParticipacaoTurma(models.Model):
    """
    Registro da participação de um Colaborador em uma Turma de Treinamento.
    Permite controlar presença, status e emissão de certificado.
    """
    STATUS_PARTICIPACAO_CHOICES = [
        ('P', 'Presente'),
        ('A', 'Ausente'),
        ('C', 'Concluído'),
        ('N', 'Não Concluído'),
        ('X', 'Cancelado')
    ]

    colaborador = models.ForeignKey(
        ColaboradorEPI,
        on_delete=models.CASCADE,
        related_name='participacoes_treinamento',
        verbose_name="Colaborador"
    )
    turma = models.ForeignKey(
        TurmaTreinamento,
        on_delete=models.CASCADE,
        related_name='participacoes',
        verbose_name="Turma de Treinamento"
    )
    status = models.CharField(
        max_length=1,
        choices=STATUS_PARTICIPACAO_CHOICES,
        default='P',
        verbose_name="Status da Participação"
    )
    data_registro_participacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Registro da Participação"
    )
    nota_avaliacao = models.DecimalField(
        max_digits=4, decimal_places=2, blank=True, null=True,
        verbose_name="Nota da Avaliação",
        validators=[MinValueValidator(0)]
    )
    certificado_emitido = models.BooleanField(default=False, verbose_name="Certificado Emitido")
    data_emissao_certificado = models.DateField(blank=True, null=True, verbose_name="Data de Emissão do Certificado")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações da Participação")

    class Meta:
        verbose_name = "Participação em Turma"
        verbose_name_plural = "Participações em Turmas"
        unique_together = ('colaborador', 'turma')
        ordering = ['turma__data_realizacao', 'colaborador__nome_completo']

    def __str__(self):
        return f"{self.colaborador.nome_completo} em {self.turma.treinamento.nome} ({self.turma.data_realizacao.strftime('%d/%m/%Y')}) - {self.get_status_display()}"