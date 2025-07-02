# pat/estoque/forms.py

from django import forms
from .models import Categoria, Localizacao, ItemEstoque, MovimentacaoEstoque

class ItemEstoqueFilterForm(forms.Form):
    # Campo para busca por nome/código
    search_query = forms.CharField(
        label='Buscar',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Nome ou Código'})
    )

    # Campo para filtro por categoria
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        label='Filtrar por Categoria',
        required=False,
        empty_label="Todas as Categorias" # Opção para não filtrar
    )

    # Campo para filtro por localização
    localizacao = forms.ModelChoiceField(
        queryset=Localizacao.objects.all(),
        label='Filtrar por Localização',
        required=False,
        empty_label="Todas as Localizações" # Opção para não filtrar
    )

class ItemEstoqueForm(forms.ModelForm): # <--- NOVO FORMULÁRIO
    class Meta:
        model = ItemEstoque
        # Quais campos do modelo você quer no formulário?
        # '__all__' inclui todos os campos do modelo
        # Ou você pode listar ('nome', 'quantidade', 'categoria', ...)
        fields = '__all__' 
        # Campos que não precisam aparecer no formulário (ex: auto_now_add, auto_now)
        exclude = ['data_criacao', 'data_ultima_atualizacao'] 

        # Adicione rótulos personalizados se desejar (opcional)
        labels = {
            'nome': 'Nome do Item',
            'codigo_interno': 'Código Interno',
            'descricao': 'Descrição Detalhada',
            'quantidade': 'Quantidade Atual',
            'unidade_medida': 'Unidade de Medida',
            'preco_unitario': 'Preço Unitário (R$)',
            'categoria': 'Categoria',
            'localizacao': 'Localização no Estoque',
        }
        # Adicione mensagens de ajuda (opcional)
        help_texts = {
            'codigo_interno': 'Um código único para identificar o item.',
            'quantidade': 'A quantidade atual em estoque.',
            'unidade_medida': 'Ex: un (unidade), kg (quilograma), m (metro), L (litro).',
        }
        # Widgets personalizados para inputs específicos (opcional)
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}), # Aumenta o tamanho da caixa de texto
            # 'preco_unitario': forms.NumberInput(attrs={'step': '0.01'}), # Para garantir 2 casas decimais
        }

    ### Entrada Estoque ---
    
class EntradaEstoqueForm(forms.ModelForm): # <--- NOVO FORMULÁRIO
    class Meta:
        model = MovimentacaoEstoque
        fields = ['item', 'quantidade_movimentada', 'descricao']
        labels = {
            'item': 'Item de Estoque',
            'quantidade_movimentada': 'Quantidade a Adicionar',
            'descricao': 'Motivo da Entrada (Ex: Compra NF-123, Devolução)',
        }
        help_texts = {
            'item': 'Selecione o item ao qual a entrada se refere.',
            'quantidade_movimentada': 'Insira a quantidade de itens que está entrando no estoque.',
        }
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

    # Opcional: Filtra os itens exibidos no campo 'item' se necessário
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].queryset = ItemEstoque.objects.all().order_by('nome')

        #------ Saida de Estoque -------

class SaidaEstoqueForm(forms.ModelForm): # <--- NOVO FORMULÁRIO
    class Meta:
        model = MovimentacaoEstoque
        fields = ['item', 'quantidade_movimentada', 'descricao']
        labels = {
            'item': 'Item de Estoque',
            'quantidade_movimentada': 'Quantidade a Retirar',
            'descricao': 'Motivo da Saída (Ex: Venda, Consumo, Descarte)',
        }
        help_texts = {
            'item': 'Selecione o item do qual a saída se refere.',
            'quantidade_movimentada': 'Insira a quantidade de itens que está saindo do estoque.',
        }
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].queryset = ItemEstoque.objects.all().order_by('nome')

    # Adicionar validação customizada para a quantidade
    def clean_quantidade_movimentada(self):
        quantidade = self.cleaned_data['quantidade_movimentada']
        item = self.cleaned_data['item'] # Já acessamos o item aqui

        if quantidade <= 0:
            raise forms.ValidationError("A quantidade a retirar deve ser maior que zero.")

        if item.quantidade < quantidade:
            # Se a quantidade em estoque for menor que a solicitada para saída
            raise forms.ValidationError(
                f"Quantidade insuficiente em estoque. Disponível: {item.quantidade} unidades."
            )
        return quantidade
