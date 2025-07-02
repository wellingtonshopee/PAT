#__init__.py

def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Este loop itera sobre todos os campos do formulário de filtro
        for field_name, field in self.form.fields.items():
            # Verifica se o widget é um DateRangeWidget (usado para data_vencimento, data_pagamento, etc.)
            if isinstance(field.widget, django_filters.widgets.DateRangeWidget):
                # Se for um DateRangeWidget, ele possui dois sub-widgets (um para "de" e outro para "até")
                # Iteramos sobre eles e adicionamos a classe 'form-control'
                for subwidget in field.widget.widgets:
                    subwidget.attrs.update({'class': 'form-control'})
            # Para outros tipos comuns de widgets (input de texto, número, select, data)
            elif isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.Select, forms.DateInput)):
                # Verifica se a classe 'form-control' já existe
                current_class = field.widget.attrs.get('class', '')
                if 'form-control' not in current_class:
                    # Se não existir, adiciona 'form-control' à lista de classes
                    field.widget.attrs['class'] = (current_class + ' form-control').strip()