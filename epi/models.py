# pat/epi/models.py

from django.db import models
from django.utils import timezone 
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import os
from uuid import uuid4

# Importando localdate para usar como default em DateField de forma serializável
from django.utils.timezone import localdate 

# IMPORTANTE: REMOVIDA A IMPORTAÇÃO DIRETA DE Lider, Cargo, TipoContrato
# AGORA USAREMOS REFERÊNCIAS EM STRING PARA EVITAR A CIRCULARIDADE.

# --- Funções Auxiliares para Uploads ---
def signature_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid4().hex}.{ext}'
    return os.path.join('signatures/', filename)

def pdf_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'saida_epi_{uuid4().hex}.{ext}'
    return os.path.join('saidas_epi_pdf/', filename)

# --- Modelos de EPI ---

# 1. Modelo para Categorizar os Tipos de EPI (ex: Luvas, Capacetes)
class TipoEPI(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Tipo de EPI")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição do Tipo")

    class Meta:
        verbose_name = "Tipo de EPI"
        verbose_name_plural = "Tipos de EPI"
        ordering = ['nome']

    def __str__(self):
        return self.nome

# 2. Modelo Principal para o EPI (o item em si)
class EPI(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome do EPI")
    ca = models.CharField(max_length=20, unique=True, verbose_name="CA (Certificado de Aprovação)", help_text="Certificado de Aprovação (obrigatório)")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição Detalhada")
    tipo_epi = models.ForeignKey(
        TipoEPI,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='epis',
        verbose_name="Tipo de EPI"
    )
    validade_ca = models.DateField(blank=True, null=True, verbose_name="Validade do CA", help_text="Data de vencimento do Certificado de Aprovação")
    fabricante = models.CharField(max_length=150, blank=True, null=True, verbose_name="Fabricante")
    modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Modelo")
    estoque_minimo = models.PositiveIntegerField(default=0, verbose_name="Estoque Mínimo")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "EPI"
        verbose_name_plural = "EPIs"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} (CA: {self.ca})"

    @property
    def estoque_atual(self):
        total_entradas = self.entradas_epi.aggregate(models.Sum('quantidade'))['quantidade__sum'] or 0
        total_saidas = self.saidas_epi.aggregate(models.Sum('quantidade'))['quantidade__sum'] or 0
        return total_entradas - total_saidas

    @property
    def ca_vencido(self):
        if self.validade_ca and self.validade_ca < timezone.now().date():
            return True
        return False


# 3. Modelo para Colaboradores (agora ColaboradorEPI, para evitar conflito)
class ColaboradorEPI(models.Model): # <--- RENOMEADO AQUI!
    nome_completo = models.CharField(max_length=255, verbose_name="Nome Completo")
    matricula = models.CharField(max_length=50, unique=True, verbose_name="Matrícula", blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF", help_text="Formato: XXX.XXX.XXX-XX", blank=True, null=True)
    
    # CAMPOS RH (agora usando referências em string para evitar importação circular)
    station_id = models.CharField(max_length=50, unique=True, verbose_name="Station ID", help_text="ID da Estação de Trabalho", blank=True, null=True)
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código do Colaborador", blank=True, null=True)
    bpo = models.CharField(max_length=100, verbose_name="BPO", blank=True, null=True)

    tipo_contrato = models.ForeignKey(
        'rh.TipoContrato', # <--- CORRIGIDO: Referência em string
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        verbose_name="Tipo de Contrato",
    )
    
    lider = models.ForeignKey('rh.Lider', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Líder") # <--- CORRIGIDO: Referência em string
    cargo = models.ForeignKey('rh.Cargo', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cargo") # <--- CORRIGIDO: Referência em string

    TURNO_CHOICES = [
        ('MANHA', 'Manhã'),
        ('TARDE', 'Tarde'),
        ('NOITE', 'Noite'),
        ('INTEGRAL', 'Integral'),
    ]
    turno = models.CharField(
        max_length=10,
        choices=TURNO_CHOICES,
        verbose_name="Turno",
        blank=True,
        null=True
    )

    data_admissao = models.DateField(verbose_name="Data de Admissão", default=localdate) 
    data_desligamento = models.DateField(verbose_name="Data de Desligamento", blank=True, null=True)
    foto = models.ImageField(upload_to='colaboradores_fotos/', blank=True, null=True, verbose_name="Foto do Colaborador")

    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Colaborador (EPI)" 
        verbose_name_plural = "Colaboradores (EPI)"
        ordering = ['nome_completo']

    def __str__(self):
        identifier = self.station_id or self.matricula
        return f"{self.nome_completo} ({identifier})" if identifier else self.nome_completo

# 4. Modelo para Registrar Entradas de EPI no Estoque
class EntradaEPI(models.Model):
    epi = models.ForeignKey(
        EPI,
        on_delete=models.CASCADE,
        related_name='entradas_epi',
        verbose_name="EPI"
    )
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade Entregue")
    data_entrada = models.DateTimeField(auto_now_add=True, verbose_name="Data de Entrada")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    class Meta:
        verbose_name = "Entrada de EPI"
        verbose_name_plural = "Entradas de EPI"
        ordering = ['-data_entrada']

    def __str__(self):
        return f"Entrada de {self.quantidade}x {self.epi.nome} em {self.data_entrada.strftime('%d/%m/%Y')}"

# 5. Modelo para Registrar Saídas (Entregas) de EPI
class SaidaEPI(models.Model):
    epi = models.ForeignKey(
        EPI,
        on_delete=models.PROTECT,
        related_name='saidas_epi',
        verbose_name="EPI"
    )
    colaborador = models.ForeignKey(
        ColaboradorEPI, 
        on_delete=models.PROTECT,
        related_name='epis_recebidos',
        verbose_name="Colaborador"
    )
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade Entregue")
    data_saida = models.DateTimeField(default=timezone.now, verbose_name="Data/Hora da Saída")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações da Entrega")
    assinatura_digital = models.ImageField(
        upload_to=signature_upload_to,
        blank=True,
        null=True,
        verbose_name="Assinatura Digital"
    )
    pdf_documento = models.FileField(
        upload_to=pdf_upload_to,
        blank=True,
        null=True,
        verbose_name="Documento PDF da Saída"
    )

    class Meta:
        verbose_name = "Saída de EPI"
        verbose_name_plural = "Saídas de EPI"
        ordering = ['-data_saida']

    def __str__(self):
        return f"Saída de {self.quantidade}x {self.epi.nome} para {self.colaborador.nome_completo}"


# --- Signals (não alterados, pois já estavam corretos) ---
@receiver(post_delete, sender=SaidaEPI)
def delete_signature_file_on_delete(sender, instance, **kwargs):
    if instance.assinatura_digital:
        if os.path.isfile(instance.assinatura_digital.path):
            os.remove(instance.assinatura_digital.path)

@receiver(post_save, sender=SaidaEPI)
def delete_old_signature_file_on_update(sender, instance, **kwargs):
    if not kwargs['created']:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if old_instance.assinatura_digital and old_instance.assinatura_digital.path != instance.assinatura_digital.path:
                if os.path.isfile(old_instance.assinatura_digital.path):
                    os.remove(old_instance.assinatura_digital.path)
        except sender.DoesNotExist:
            pass

@receiver(post_delete, sender=SaidaEPI)
def delete_pdf_file_on_delete(sender, instance, **kwargs):
    if instance.pdf_documento:
        if os.path.isfile(instance.pdf_documento.path):
            os.remove(instance.pdf_documento.path)

@receiver(post_save, sender=SaidaEPI)
def delete_old_pdf_file_on_update(sender, instance, **kwargs):
    if not kwargs['created']:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if old_instance.pdf_documento and old_instance.pdf_documento.path != instance.pdf_documento.path:
                if os.path.isfile(old_instance.pdf_documento.path):
                    os.remove(old_instance.pdf_documento.path)
        except sender.DoesNotExist:
            pass