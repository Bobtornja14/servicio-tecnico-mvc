from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, IntegerField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Optional, NumberRange
from flask_wtf.file import FileField, FileAllowed
from flask_uploads import UploadSet, IMAGES

# Configuración para manejar la subida de firmas
signatures = UploadSet('signatures', ('png', 'jpg', 'jpeg'))

class ReporteForm(FlaskForm):
    trabajo_realizado = TextAreaField('Trabajo Realizado', validators=[DataRequired()])
    problemas_encontrados = TextAreaField('Problemas Encontrados', validators=[Optional()])
    solucion_aplicada = TextAreaField('Solución Aplicada', validators=[DataRequired()])
    recomendaciones = TextAreaField('Recomendaciones', validators=[Optional()])
    
    # Información del cliente
    cliente_satisfecho = BooleanField('Cliente Satisfecho', default=True)
    observaciones_cliente = TextAreaField('Observaciones del Cliente', validators=[Optional()])
    nombre_firma = StringField('Nombre para la Firma', validators=[DataRequired()])
    
    # Información del servicio
    hora_inicio = DateTimeField('Hora de Inicio', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    hora_fin = DateTimeField('Hora de Finalización', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    
    # Firma digital (se manejará con JavaScript)
    firma_cliente = StringField('Firma del Cliente', validators=[DataRequired()])
    
    # Campos ocultos para el estado
    completado = BooleanField('Completado', default=True)
    aprobado_admin = BooleanField('Aprobado por Administración', default=False)
    
    # Campo para piezas utilizadas (se manejará dinámicamente con JavaScript)
    piezas_utilizadas = TextAreaField('Piezas Utilizadas', validators=[Optional()], render_kw={"rows": 3})


class AprobarReporteForm(FlaskForm):
    aprobado = BooleanField('Aprobar Reporte', default=False)
    observaciones = TextAreaField('Observaciones', validators=[Optional()])
    firma_admin = StringField('Firma del Administrador', validators=[DataRequired()])
    nombre_firma_admin = StringField('Nombre para la Firma', validators=[DataRequired()])
