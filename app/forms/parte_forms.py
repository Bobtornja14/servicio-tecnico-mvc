from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, FloatField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError
from datetime import datetime

class ParteForm(FlaskForm):
    """Formulario para crear y editar partes/repuestos."""
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    codigo = StringField('Código', validators=[DataRequired(), Length(min=2, max=50)])
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    precio = FloatField('Precio', validators=[
        DataRequired(message='El precio es obligatorio'),
        NumberRange(min=0, message='El precio no puede ser negativo')
    ])
    stock = IntegerField('Stock', validators=[
        DataRequired(message='El stock es obligatorio'),
        NumberRange(min=0, message='El stock no puede ser negativo')
    ])
    stock_minimo = IntegerField('Stock Mínimo', validators=[
        DataRequired(message='El stock mínimo es obligatorio'),
        NumberRange(min=0, message='El stock mínimo no puede ser negativo')
    ])
    proveedor = StringField('Proveedor', validators=[
        Optional(),
        Length(max=100, message='El nombre del proveedor no puede tener más de 100 caracteres')
    ])
    categoria = StringField('Categoría', validators=[
        Optional(),
        Length(max=50, message='La categoría no puede tener más de 50 caracteres')
    ])
    ubicacion = StringField('Ubicación en Almacén', validators=[
        Optional(),
        Length(max=50, message='La ubicación no puede tener más de 50 caracteres')
    ])
    
    def validate_stock_minimo(self, field):
        """Valida que el stock mínimo sea menor o igual al stock actual."""
        if hasattr(self, 'stock') and field.data > self.stock.data:
            raise ValidationError('El stock mínimo no puede ser mayor al stock actual')


class AjusteStockForm(FlaskForm):
    """Formulario para realizar ajustes de inventario de partes."""
    
    TIPO_AJUSTE = [
        ('entrada', 'Entrada de Inventario'),
        ('salida', 'Salida de Inventario'),
        ('ajuste', 'Ajuste de Inventario')
    ]
    
    parte_id = HiddenField('ID de la Parte', validators=[DataRequired()])
    tipo_ajuste = SelectField(
        'Tipo de Ajuste', 
        choices=TIPO_AJUSTE, 
        validators=[DataRequired()]
    )
    cantidad = IntegerField(
        'Cantidad', 
        validators=[
            DataRequired(message='La cantidad es obligatoria'),
            NumberRange(min=1, message='La cantidad debe ser mayor a 0')
        ]
    )
    motivo = SelectField(
        'Motivo',
        choices=[
            ('compra', 'Compra de Inventario'),
            ('devolucion', 'Devolución de Cliente'),
            ('perdida', 'Pérdida o Daño'),
            ('inventario', 'Ajuste de Inventario Físico'),
            ('otro', 'Otro')
        ],
        validators=[DataRequired()]
    )
    notas = TextAreaField(
        'Notas Adicionales', 
        validators=[
            Optional(),
            Length(max=500, message='Las notas no pueden tener más de 500 caracteres')
        ]
    )
    fecha_ajuste = HiddenField(default=datetime.utcnow)
    usuario_id = HiddenField(validators=[DataRequired()])
    
    def validate_cantidad(self, field):
        """Valida que la cantidad sea positiva."""
        if field.data <= 0:
            raise ValidationError('La cantidad debe ser mayor a cero.')


class FiltroPartesForm(FlaskForm):
    """Formulario para filtrar la lista de partes/repuestos."""
    
    buscar = StringField('Buscar', validators=[Optional()])
    
    categoria = SelectField(
        'Categoría',
        choices=[
            ('', 'Todas las categorías'),
            ('electronica', 'Electrónica'),
            ('mecanica', 'Mecánica'),
            ('electricidad', 'Electricidad'),
            ('herramientas', 'Herramientas'),
            ('consumibles', 'Consumibles')
        ],
        validators=[Optional()]
    )
    
    stock_minimo = SelectField(
        'Stock Mínimo',
        choices=[
            ('', 'Todos'),
            ('bajo', 'Por debajo del mínimo'),
            ('normal', 'Sobre el mínimo')
        ],
        validators=[Optional()]
    )
    
    ordenar_por = SelectField(
        'Ordenar por',
        choices=[
            ('nombre', 'Nombre (A-Z)'),
            ('-nombre', 'Nombre (Z-A)'),
            ('stock', 'Stock (menor a mayor)'),
            ('-stock', 'Stock (mayor a menor)'),
            ('precio', 'Precio (menor a mayor)'),
            ('-precio', 'Precio (mayor a menor)')
        ],
        default='nombre'
    )
    
    submit = SubmitField('Filtrar')
