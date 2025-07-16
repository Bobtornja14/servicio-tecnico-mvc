from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired, Optional, NumberRange
from datetime import datetime

class AprobarPedidoForm(FlaskForm):
    cantidad_aprobada = IntegerField(
        'Cantidad Aprobada',
        validators=[DataRequired(), NumberRange(min=1)],
        default=1
    )
    estado = SelectField(
        'Estado',
        choices=[
            ('aprobado', 'Aprobado'),
            ('rechazado', 'Rechazado'),
            ('pendiente', 'Pendiente')
        ],
        validators=[DataRequired()]
    )
    observaciones = TextAreaField('Observaciones', validators=[Optional()])

class EntregarPedidoForm(FlaskForm):
    cantidad_entregada = IntegerField(
        'Cantidad Entregada',
        validators=[DataRequired(), NumberRange(min=1)],
        default=1
    )
    observaciones = TextAreaField('Observaciones', validators=[Optional()])
    fecha_entrega = StringField(
        'Fecha de Entrega',
        default=datetime.now().strftime('%Y-%m-%dT%H:%M'),
        validators=[DataRequired()]
    )

class CrearPedidoForm(FlaskForm):
    parte_id = IntegerField('ID de la Parte', validators=[DataRequired()])
    cantidad_solicitada = IntegerField(
        'Cantidad Solicitada',
        validators=[DataRequired(), NumberRange(min=1)],
        default=1
    )
    motivo = TextAreaField('Motivo del Pedido', validators=[DataRequired()])
    urgencia = SelectField(
        'Nivel de Urgencia',
        choices=[
            ('baja', 'Baja'),
            ('normal', 'Normal'),
            ('alta', 'Alta'),
            ('urgente', 'Urgente')
        ],
        default='normal',
        validators=[DataRequired()]
    )
    asignacion_id = IntegerField('ID de la Asignación', validators=[Optional()])
