# patrimonio/forms.py
from django import forms
from .models import CategoriaPatrimonio, LocalizacaoPatrimonio, ItemPatrimonio, MovimentacaoPatrimonio
from django.contrib.auth import get_user_model
from django.utils import timezone

# Importações para o Crispy Forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column # Adicione Row e Column para um layout mais organizado

User = get_user_model()

# --- Formulário para Adição/Edição de Item de Patrimônio ---
class ItemPatrimonioForm(forms.ModelForm):
    class Meta:
        model = ItemPatrimonio
        fields = [
            'nome', 'codigo_patrimonial', 'numero_serie', 'descricao',
            'data_aquisicao', 'valor_aquisicao', 'estado_conservacao',
            'status',
            'categoria', 'localizacao', 'responsavel_atual',
        ]
        exclude = ['data_ultima_atualizacao', 'data_registro', 'data_baixa', 'motivo_baixa']

        labels = {
            'nome': 'Nome do Bem Patrimonial',
            'codigo_patrimonial': 'Código Patrimonial',
            'data_aquisicao': 'Data de Aquisição',
            'valor_aquisicao': 'Valor de Aquisição (R$)',
            'estado_conservacao': 'Estado de Conservação',
            'status': 'Status do Item',
            'categoria': 'Categoria',
            'localizacao': 'Localização Atual',
            'responsavel_atual': 'Responsável Atual',
            'numero_serie': 'Número de Série',
            'descricao': 'Descrição Detalhada',
        }
        help_texts = {
            'codigo_patrimonial': 'Um código único para identificar o patrimônio.',
            'numero_serie': 'Número de série do fabricante (se aplicável).',
            'data_aquisicao': 'Formato: AAAA-MM-DD (ex: 2023-01-15).',
            'valor_aquisicao': 'Valor de compra do item.',
            'responsavel_atual': 'Usuário responsável por este bem patrimonial.',
        }
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'data_aquisicao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estado_conservacao': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'localizacao': forms.Select(attrs={'class': 'form-select'}),
            'responsavel_atual': forms.Select(attrs={'class': 'form-select'}),
        }


# --- Formulário de Filtro de Patrimônio (Ajustado com Crispy Forms) ---
class PatrimonioFilterForm(forms.Form):
    search_query = forms.CharField(
        max_length=200,
        required=False,
        label='Pesquisar',
        help_text='Nome, Código ou Nº Série',
        widget=forms.TextInput(attrs={'placeholder': 'Pesquisar patrimônio...', 'class': 'form-control'})
    )

    categoria = forms.ModelChoiceField(
        queryset=CategoriaPatrimonio.objects.all().order_by('nome'),
        required=False,
        label='Categoria',
        empty_label="Todas as Categorias",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    localizacao = forms.ModelChoiceField(
        queryset=LocalizacaoPatrimonio.objects.all().order_by('nome'),
        required=False,
        label='Localização',
        empty_label="Todas as Localizações",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    estado_conservacao = forms.ChoiceField(
        choices=[('', 'Todos os Estados')] + list(ItemPatrimonio.ESTADO_CONSERVACAO_CHOICES),
        required=False,
        label='Estado de Conservação',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    status = forms.ChoiceField(
        choices=[('', 'Todos os Status')] + list(ItemPatrimonio.STATUS_CHOICES),
        required=False,
        label='Status do Item',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    data_aquisicao_inicio = forms.DateField(
        required=False,
        label='Adquirido A Partir De',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'],
        help_text='Data inicial de aquisição (AAAA-MM-DD ou DD/MM/AAAA)'
    )
    data_aquisicao_fim = forms.DateField(
        required=False,
        label='Adquirido Até',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'],
        help_text='Data final de aquisição (AAAA-MM-DD ou DD/MM/AAAA)'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get' # O formulário de filtro deve usar GET
        self.helper.layout = Layout(
            Row(
                Column('search_query', css_class='form-group col-md-3 mb-0'),
                Column('categoria', css_class='form-group col-md-2 mb-0'),
                Column('localizacao', css_class='form-group col-md-2 mb-0'),
                Column('estado_conservacao', css_class='form-group col-md-2 mb-0'),
                Column('status', css_class='form-group col-md-2 mb-0'),
                css_class='g-3' # Gutter para espaçamento entre colunas
            ),
            Row(
                Column('data_aquisicao_inicio', css_class='form-group col-md-3 mb-0'),
                Column('data_aquisicao_fim', css_class='form-group col-md-3 mb-0'),
                Column(
                    Submit('submit', 'Aplicar Filtros', css_class='btn btn-primary'),
                    # Você precisará de um botão de limpar separado no template se não usar url como action
                    # 'patrimonio:gerar_relatorio_patrimonio'
                    css_class='form-group col-md-auto d-flex align-items-end mb-0'
                ),
                css_class='g-3'
            )
            # Os botões "Aplicar Filtros" e "Limpar Filtros" você já os tem no template,
            # então este Submit pode ser removido ou você pode decidir renderizar o formulário todo com {{ filter_form|crispy }}
            # Se você usar {{ filter_form|crispy }} no template, este Submit irá gerar os botões automaticamente.
        )
        
        # Se você ainda estiver usando a renderização campo a campo no template ({{ filter_form.field|crispy }}),
        # este Layout interno ainda ajuda a estruturar, mas os botões de submit são melhor gerenciados no template HTML.
        # Por isso, mantive o layout para os campos, mas a parte do Submit pode ser flexível.
        # Vou comentar os botões aqui, pois o template já os tem.
        
        # Removendo os botões daqui para evitar duplicação com o template,
        # assumindo que você ainda usará o layout manual no HTML.
        # Se for usar {{ filter_form|crispy }}, você pode descomentar e ajustar.
        # self.helper.add_input(Submit('submit', 'Aplicar Filtros'))
        # self.helper.add_input(Button('clear', 'Limpar Filtros', css_class='btn btn-outline-secondary', onclick="window.location.href = '{}';".format(reverse('patrimonio:gerar_relatorio_patrimonio'))))


class BaixaPatrimonioForm(forms.Form):
    """
    Formulário para registrar a baixa de um item de patrimônio.
    """
    data_baixa = forms.DateField(
        label="Data da Baixa",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    motivo_baixa = forms.CharField(
        label="Motivo da Baixa",
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        help_text="Descreva o motivo pelo qual o item está sendo baixado (ex: quebra, desuso, venda, doação).",
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'data_baixa' in self.fields and self.fields['data_baixa'].initial is None:
            self.fields['data_baixa'].initial = timezone.localdate()


class TransferenciaPatrimonioForm(forms.Form):
    """
    Formulário para transferir a localização ou o responsável de um item de patrimônio.
    """
    nova_localizacao = forms.ModelChoiceField(
        queryset=LocalizacaoPatrimonio.objects.all().order_by('nome'),
        empty_label="Selecione uma nova localização",
        label="Nova Localização",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    novo_responsavel = forms.ModelChoiceField(
        queryset=User.objects.all().order_by('first_name', 'username'),
        empty_label="Selecione um novo responsável",
        label="Novo Responsável",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    observacoes = forms.CharField(
        label="Observações da Transferência",
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,
        help_text="Adicione qualquer observação relevante sobre esta transferência."
    )

    def clean(self):
        cleaned_data = super().clean()
        nova_localizacao = cleaned_data.get('nova_localizacao')
        novo_responsavel = cleaned_data.get('novo_responsavel')

        if not nova_localizacao and not novo_responsavel:
            raise forms.ValidationError("Você deve selecionar uma nova localização ou um novo responsável para a transferência.")
        return cleaned_data


class MovimentacaoFilterForm(forms.Form):
    q = forms.CharField(
        label='Buscar (Item/Obs)',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Código, Nome ou Observação'})
    )
    tipo_movimentacao = forms.ChoiceField(
        choices=[('', 'Todos')] + list(MovimentacaoPatrimonio.TIPO_CHOICES),
        label='Tipo',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    localizacao_origem = forms.ModelChoiceField(
        queryset=LocalizacaoPatrimonio.objects.all().order_by('nome'),
        label='Origem',
        required=False,
        empty_label='Todas as Origens',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    localizacao_destino = forms.ModelChoiceField(
        queryset=LocalizacaoPatrimonio.objects.all().order_by('nome'),
        label='Destino',
        required=False,
        empty_label='Todos os Destinos',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    data_inicio = forms.DateField(
        label='Data Início',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
    )
    data_fim = forms.DateField(
        label='Data Fim',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
    )