# usuarios/admin.py
from django.contrib import admin
from .models import LogAtividade

@admin.register(LogAtividade)
class LogAtividadeAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'usuario', 'acao', 'ip_endereco')
    list_filter = ('acao', 'usuario', 'data_hora')
    search_fields = ('acao', 'descricao', 'usuario__username', 'ip_endereco')
    readonly_fields = ('usuario', 'acao', 'descricao', 'data_hora', 'ip_endereco') # Impede edições acidentais
    date_hierarchy = 'data_hora' # Facilita a navegação por data