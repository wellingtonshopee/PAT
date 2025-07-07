# rh/models.py

from django.db import models
from datetime import timedelta
from django.utils.timezone import localdate, now as timezone_now 

from epi.models import ColaboradorEPI 

class TipoContrato(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Contrato")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    class Meta:
        verbose_name = "Tipo de Contrato"
        verbose_name_plural = "Tipos de Contrato" # CORRIGIDO AQUI

    def __str__(self):
        return self.nome

class Lider(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Líder")
    matricula = models.CharField(max_length=50, blank=True, null=True, verbose_name="Matrícula")

    class Meta:
        verbose_name = "Líder"
        verbose_name_plural = "Líderes" # CORRIGIDO AQUI

    def __str__(self):
        return self.nome

class Cargo(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Cargo")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos" # CORRIGIDO AQUI

    def __str__(self):
        return self.nome

# --- Modelos de Absenteísmo ---

class TipoAbsenteismo(models.Model):
    descricao = models.CharField(max_length=100, unique=True, verbose_name="Descrição do Tipo")
    sigla = models.CharField(max_length=10, unique=True, verbose_name="Sigla")
    e_ausencia = models.BooleanField(default=True, verbose_name="Conta como Ausência?") 

    class Meta:
        verbose_name = "Tipo de Absenteísmo"
        verbose_name_plural = "Tipos de Absenteísmo" # CORRIGIDO AQUI
        ordering = ['descricao'] 

    def __str__(self):
        return f"{self.sigla} - {self.descricao}"

class RegistroAbsenteismoDiario(models.Model): 
    colaborador = models.ForeignKey(ColaboradorEPI, on_delete=models.CASCADE, related_name='registros_absenteismo_diario', verbose_name="Colaborador") 
    
    tipo_absenteismo = models.ForeignKey(
        TipoAbsenteismo, 
        on_delete=models.PROTECT, 
        default=16,                
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
        verbose_name_plural = "Registros de Absenteísmo Diários" # CORRIGIDO AQUI
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