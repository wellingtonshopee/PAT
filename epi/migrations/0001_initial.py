# Generated by Django 5.2.3 on 2025-07-04 18:35

import django.utils.timezone
import epi.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ColaboradorEPI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_completo', models.CharField(max_length=255, verbose_name='Nome Completo')),
                ('matricula', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='Matrícula')),
                ('cpf', models.CharField(blank=True, help_text='Formato: XXX.XXX.XXX-XX', max_length=14, null=True, unique=True, verbose_name='CPF')),
                ('station_id', models.CharField(blank=True, help_text='ID da Estação de Trabalho', max_length=50, null=True, unique=True, verbose_name='Station ID')),
                ('codigo', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='Código do Colaborador')),
                ('bpo', models.CharField(blank=True, max_length=100, null=True, verbose_name='BPO')),
                ('turno', models.CharField(blank=True, choices=[('MANHA', 'Manhã'), ('TARDE', 'Tarde'), ('NOITE', 'Noite'), ('INTEGRAL', 'Integral')], max_length=10, null=True, verbose_name='Turno')),
                ('data_admissao', models.DateField(default=django.utils.timezone.localdate, verbose_name='Data de Admissão')),
                ('data_desligamento', models.DateField(blank=True, null=True, verbose_name='Data de Desligamento')),
                ('foto', models.ImageField(blank=True, null=True, upload_to='colaboradores_fotos/', verbose_name='Foto do Colaborador')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
            ],
            options={
                'verbose_name': 'Colaborador (EPI)',
                'verbose_name_plural': 'Colaboradores (EPI)',
                'ordering': ['nome_completo'],
            },
        ),
        migrations.CreateModel(
            name='EntradaEPI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.PositiveIntegerField(verbose_name='Quantidade Entregue')),
                ('data_entrada', models.DateTimeField(auto_now_add=True, verbose_name='Data de Entrada')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
            ],
            options={
                'verbose_name': 'Entrada de EPI',
                'verbose_name_plural': 'Entradas de EPI',
                'ordering': ['-data_entrada'],
            },
        ),
        migrations.CreateModel(
            name='EPI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200, verbose_name='Nome do EPI')),
                ('ca', models.CharField(help_text='Certificado de Aprovação (obrigatório)', max_length=20, unique=True, verbose_name='CA (Certificado de Aprovação)')),
                ('descricao', models.TextField(blank=True, null=True, verbose_name='Descrição Detalhada')),
                ('validade_ca', models.DateField(blank=True, help_text='Data de vencimento do Certificado de Aprovação', null=True, verbose_name='Validade do CA')),
                ('fabricante', models.CharField(blank=True, max_length=150, null=True, verbose_name='Fabricante')),
                ('modelo', models.CharField(blank=True, max_length=100, null=True, verbose_name='Modelo')),
                ('estoque_minimo', models.PositiveIntegerField(default=0, verbose_name='Estoque Mínimo')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
            ],
            options={
                'verbose_name': 'EPI',
                'verbose_name_plural': 'EPIs',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='SaidaEPI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.PositiveIntegerField(verbose_name='Quantidade Entregue')),
                ('data_saida', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data/Hora da Saída')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações da Entrega')),
                ('assinatura_digital', models.ImageField(blank=True, null=True, upload_to=epi.models.signature_upload_to, verbose_name='Assinatura Digital')),
                ('pdf_documento', models.FileField(blank=True, null=True, upload_to=epi.models.pdf_upload_to, verbose_name='Documento PDF da Saída')),
            ],
            options={
                'verbose_name': 'Saída de EPI',
                'verbose_name_plural': 'Saídas de EPI',
                'ordering': ['-data_saida'],
            },
        ),
        migrations.CreateModel(
            name='TipoEPI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True, verbose_name='Tipo de EPI')),
                ('descricao', models.TextField(blank=True, null=True, verbose_name='Descrição do Tipo')),
            ],
            options={
                'verbose_name': 'Tipo de EPI',
                'verbose_name_plural': 'Tipos de EPI',
                'ordering': ['nome'],
            },
        ),
    ]
