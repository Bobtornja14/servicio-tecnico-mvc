from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, IntegerField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])


class UsuarioForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telefono = StringField('Teléfono', validators=[Length(max=20)])
    rol = SelectField('Rol',
                      choices=[('usuario', 'Usuario'), ('tecnico', 'Técnico'), ('administrador', 'Administrador')])
    password = PasswordField('Contraseña', validators=[Optional(), Length(min=6, max=20)])


class ClienteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[Email(), Optional()])
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(max=20)])
    direccion = TextAreaField('Dirección')
    tipo_cliente = SelectField('Tipo de Cliente', choices=[('particular', 'Particular'), ('empresa', 'Empresa')])


class ServicioForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    descripcion = TextAreaField('Descripción')
    precio_base = FloatField('Precio Base', validators=[DataRequired(), NumberRange(min=0)])
    categoria = StringField('Categoría', validators=[Length(max=50)])


class TecnicoForm(FlaskForm):
    usuario_id = SelectField('Usuario Asociado', coerce=int, validators=[Optional()])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[Optional(), Email()], 
                       description='Se usará para iniciar sesión (requerido si crea un nuevo usuario)')
    password = PasswordField('Contraseña', validators=[Optional(), Length(min=6)],
                           description='Dejar en blanco para no cambiar')
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(max=20)])
    especialidad = StringField('Especialidad', validators=[Length(max=100)])
    nivel_experiencia = SelectField('Nivel de Experiencia',
                                   choices=[('junior', 'Junior'), ('senior', 'Senior'), ('experto', 'Experto')])
    
    def validate(self, **kwargs):
        # Run default validation first
        if not super().validate():
            return False
            
        # If creating a new user (usuario_id == 0), email and password are required
        if self.usuario_id.data == 0:
            if not self.email.data:
                self.email.errors.append('El correo electrónico es obligatorio para crear un nuevo usuario')
                return False
            if not self.password.data:
                self.password.errors.append('La contraseña es obligatoria para crear un nuevo usuario')
                return False
                
            # Check if email is already in use
            if Usuario.query.filter_by(email=self.email.data).first():
                self.email.errors.append('Este correo electrónico ya está en uso')
                return False
                
        return True


class SolicitudForm(FlaskForm):
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    servicio_id = SelectField('Servicio', coerce=int, validators=[DataRequired()])
    descripcion_problema = TextAreaField('Descripción del Problema', validators=[DataRequired()])
    prioridad = SelectField('Prioridad',
                            choices=[('baja', 'Baja'), ('media', 'Media'), ('alta', 'Alta'), ('urgente', 'Urgente')])
    estado = SelectField('Estado',
                         choices=[('pendiente', 'Pendiente'), ('asignada', 'Asignada'),
                                  ('en_proceso', 'En Proceso'), ('completada', 'Completada'),
                                  ('cancelada', 'Cancelada')])


class AsignacionForm(FlaskForm):
    solicitud_id = SelectField('Solicitud', coerce=int, validators=[DataRequired()])
    tecnico_id = SelectField('Técnico', coerce=int, validators=[DataRequired()])
    observaciones = TextAreaField('Observaciones')
    tiempo_estimado = IntegerField('Tiempo Estimado (horas)', validators=[Optional(), NumberRange(min=1)])
    estado = SelectField('Estado',
                         choices=[('asignada', 'Asignada'), ('en_proceso', 'En Proceso'), ('completada', 'Completada')])


class ParteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    codigo = StringField('Código', validators=[DataRequired(), Length(min=2, max=50)])
    descripcion = TextAreaField('Descripción')
    precio = FloatField('Precio', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[NumberRange(min=0)])
    stock_minimo = IntegerField('Stock Mínimo', validators=[NumberRange(min=0)])
    proveedor = StringField('Proveedor', validators=[Length(max=100)])


class FacturaForm(FlaskForm):
    numero_factura = StringField('Número de Factura', validators=[DataRequired(), Length(max=20)])
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    solicitud_id = SelectField('Solicitud', coerce=int, validators=[Optional()])
    subtotal = FloatField('Subtotal', validators=[DataRequired(), NumberRange(min=0)])
    impuestos = FloatField('Impuestos', validators=[NumberRange(min=0)])
    total = FloatField('Total', validators=[DataRequired(), NumberRange(min=0)])
    estado = SelectField('Estado',
                         choices=[('pendiente', 'Pendiente'), ('pagada', 'Pagada'), ('vencida', 'Vencida')])
    observaciones = TextAreaField('Observaciones')


class ReporteForm(FlaskForm):
    trabajo_realizado = TextAreaField('Trabajo Realizado', validators=[DataRequired()])
    problemas_encontrados = TextAreaField('Problemas Encontrados')
    solucion_aplicada = TextAreaField('Solución Aplicada')
    recomendaciones = TextAreaField('Recomendaciones')
    piezas_utilizadas = TextAreaField('Piezas Utilizadas')

    estado_inicial = SelectField('Estado Inicial del Equipo',
                                 choices=[('funcionando', 'Funcionando'), ('dañado', 'Dañado'),
                                          ('inoperativo', 'Inoperativo')])
    estado_final = SelectField('Estado Final del Equipo',
                               choices=[('funcionando', 'Funcionando'), ('dañado', 'Dañado'),
                                        ('inoperativo', 'Inoperativo')])

    hora_inicio = StringField('Hora de Inicio (HH:MM)')
    hora_fin = StringField('Hora de Fin (HH:MM)')

    cliente_satisfecho = BooleanField('Cliente Satisfecho', default=True)
    observaciones_cliente = TextAreaField('Observaciones del Cliente')


class PedidoPiezaForm(FlaskForm):
    parte_id = SelectField('Pieza/Repuesto', coerce=int, validators=[DataRequired()])
    cantidad_solicitada = IntegerField('Cantidad Solicitada', validators=[DataRequired(), NumberRange(min=1)])
    motivo = TextAreaField('Motivo del Pedido', validators=[DataRequired()])
    urgencia = SelectField('Urgencia',
                           choices=[('baja', 'Baja'), ('normal', 'Normal'), ('alta', 'Alta'), ('urgente', 'Urgente')])
    asignacion_id = IntegerField('ID Asignación', validators=[Optional()])


class AjusteStockForm(FlaskForm):
    nuevo_stock = IntegerField('Nuevo Stock', validators=[DataRequired(), NumberRange(min=0)])
    motivo = TextAreaField('Motivo del Ajuste', validators=[DataRequired()])
