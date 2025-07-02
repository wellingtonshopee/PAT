# pat/epi/models.py

from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import os # Importar para a função delete_signature_file_on_delete e delete_old_signature_file_on_update
from uuid import uuid4 # Para gerar nomes de arquivo únicos

# Função para gerar o caminho do arquivo da assinatura
def signature_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    # Gera um nome de arquivo único usando UUID para evitar colisões
    filename = f'{uuid4().hex}.{ext}'
    # O arquivo será salvo em MEDIA_ROOT/signatures/
    return os.path.join('signatures/', filename)

# NOVO: Função para gerar o caminho do arquivo PDF
def pdf_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    # Gera um nome de arquivo único para o PDF
    filename = f'saida_epi_{uuid4().hex}.{ext}'
    # O arquivo será salvo em MEDIA_ROOT/saidas_epi_pdf/
    return os.path.join('saidas_epi_pdf/', filename)

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
        # Calcula o estoque atual baseado nas entradas e saídas
        total_entradas = self.entradas_epi.aggregate(models.Sum('quantidade'))['quantidade__sum'] or 0
        total_saidas = self.saidas_epi.aggregate(models.Sum('quantidade'))['quantidade__sum'] or 0
        return total_entradas - total_saidas

    @property
    def ca_vencido(self):
        if self.validade_ca and self.validade_ca < timezone.now().date():
            return True
        return False

# 3. Modelo para Colaboradores (simplificado para o módulo EPI)
# Se você já tiver um app 'colaboradores' ou 'funcionarios', pode ignorar este e importar o seu.
class Colaborador(models.Model):
    nome_completo = models.CharField(max_length=255, verbose_name="Nome Completo")
    matricula = models.CharField(max_length=50, unique=True, verbose_name="Matrícula")
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF", help_text="Formato: XXX.XXX.XXX-XX")
    data_admissao = models.DateField(verbose_name="Data de Admissão", default=timezone.now)
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Colaborador"
        verbose_name_plural = "Colaboradores"
        ordering = ['nome_completo']

    def __str__(self):
        return f"{self.nome_completo} ({self.matricula})"

# 4. Modelo para Registrar Entradas de EPI no Estoque
class EntradaEPI(models.Model):
    epi = models.ForeignKey(
        EPI,
        on_delete=models.CASCADE, # Se o EPI for deletado, as entradas relacionadas também são
        related_name='entradas_epi',
        verbose_name="EPI"
    )
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade")
    data_entrada = models.DateTimeField(auto_now_add=True, verbose_name="Data de Entrada")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    class Meta:
        verbose_name = "Entrada de EPI"
        verbose_name_plural = "Entradas de EPI"
        ordering = ['-data_entrada'] # Ordena da mais recente para a mais antiga

    def __str__(self):
        return f"Entrada de {self.quantidade}x {self.epi.nome} em {self.data_entrada.strftime('%d/%m/%Y')}"

# 5. Modelo para Registrar Saídas (Entregas) de EPI
class SaidaEPI(models.Model):
    epi = models.ForeignKey(
        EPI,
        on_delete=models.PROTECT, # Protege o EPI de ser deletado se houver saídas associadas
        related_name='saidas_epi',
        verbose_name="EPI"
    )
    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.PROTECT, # Protege o Colaborador de ser deletado se houver saídas associadas
        related_name='epis_recebidos',
        verbose_name="Colaborador"
    )
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade Entregue")
    data_saida = models.DateTimeField(default=timezone.now, verbose_name="Data/Hora da Saída")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações da Entrega")
    assinatura_digital = models.ImageField( # Campo para assinatura digital
        upload_to=signature_upload_to,
        blank=True,
        null=True,
        verbose_name="Assinatura Digital"
    )
    # NOVO CAMPO para armazenar o arquivo PDF gerado
    pdf_documento = models.FileField(
        upload_to=pdf_upload_to,
        blank=True,
        null=True,
        verbose_name="Documento PDF da Saída"
    )

    class Meta:
        verbose_name = "Saída de EPI"
        verbose_name_plural = "Saídas de EPI"
        ordering = ['-data_saida'] # Ordena as saídas por data mais recente

    def __str__(self):
        return f"Saída de {self.quantidade}x {self.epi.nome} para {self.colaborador.nome_completo}"

# Signals para gerenciar arquivos de assinatura
# Opcional: Signal para deletar o arquivo de assinatura quando o objeto SaidaEPI é deletado
@receiver(post_delete, sender=SaidaEPI)
def delete_signature_file_on_delete(sender, instance, **kwargs):
    if instance.assinatura_digital:
        if os.path.isfile(instance.assinatura_digital.path):
            os.remove(instance.assinatura_digital.path)
            
# Opcional: Signal para deletar a assinatura antiga quando uma nova é salva no mesmo objeto
@receiver(post_save, sender=SaidaEPI)
def delete_old_signature_file_on_update(sender, instance, **kwargs):
    if not kwargs['created']: # Se não for uma nova criação (ou seja, é uma atualização)
        try:
            # Pega a instância antiga do banco de dados antes da atualização
            old_instance = sender.objects.get(pk=instance.pk)
            # Se o campo de assinatura mudou e a assinatura antiga existe, remove o arquivo antigo
            if old_instance.assinatura_digital and old_instance.assinatura_digital.path != instance.assinatura_digital.path:
                if os.path.isfile(old_instance.assinatura_digital.path):
                    os.remove(old_instance.assinatura_digital.path)
        except sender.DoesNotExist:
            pass # O objeto não existia antes (cenário raro para atualização)

# Opcional: Signal para deletar o arquivo PDF quando o objeto SaidaEPI é deletado
@receiver(post_delete, sender=SaidaEPI)
def delete_pdf_file_on_delete(sender, instance, **kwargs):
    if instance.pdf_documento:
        if os.path.isfile(instance.pdf_documento.path):
            os.remove(instance.pdf_documento.path)

# Opcional: Signal para deletar o PDF antigo quando um novo é salvo no mesmo objeto
@receiver(post_save, sender=SaidaEPI)
def delete_old_pdf_file_on_update(sender, instance, **kwargs):
    if not kwargs['created']: # Se não for uma nova criação (ou seja, é uma atualização)
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            # Se o campo de PDF mudou e o PDF antigo existe, remove o arquivo antigo
            if old_instance.pdf_documento and old_instance.pdf_documento.path != instance.pdf_documento.path:
                if os.path.isfile(old_instance.pdf_documento.path):
                    os.remove(old_instance.pdf_documento.path)
        except sender.DoesNotExist:
            pass
