from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(20))
    rol = db.Column(db.String(20), nullable=False, default='usuario')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Establece la contraseña hasheada"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.rol == 'administrador'

    def is_tecnico(self):
        """Verifica si el usuario es técnico"""
        return self.rol == 'tecnico'

    def __repr__(self):
        return f'<Usuario {self.nombre}>'


class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    telefono = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.Text)
    tipo_cliente = db.Column(db.String(20), default='particular')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    solicitudes = db.relationship('Solicitud', backref='cliente', lazy=True)
    facturas = db.relationship('Factura', backref='cliente', lazy=True)

    def __repr__(self):
        return f'<Cliente {self.nombre}>'


class Servicio(db.Model):
    __tablename__ = 'servicios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio_base = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50))

    # Relaciones
    solicitudes = db.relationship('Solicitud', backref='servicio', lazy=True)

    def __repr__(self):
        return f'<Servicio {self.nombre}>'


class Tecnico(db.Model):
    __tablename__ = 'tecnicos'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    telefono = db.Column(db.String(20), nullable=False)
    especialidad = db.Column(db.String(100))
    nivel_experiencia = db.Column(db.String(20), default='junior')
    fecha_ingreso = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    usuario = db.relationship('Usuario', backref='tecnico_profile')
    asignaciones = db.relationship('Asignacion', backref='tecnico', lazy=True)
    reportes = db.relationship('Reporte', backref='tecnico', lazy=True)
    pedidos_piezas = db.relationship('PedidoPieza', backref='tecnico', lazy=True)

    def __repr__(self):
        return f'<Tecnico {self.nombre}>'


class Solicitud(db.Model):
    __tablename__ = 'solicitudes'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)
    descripcion_problema = db.Column(db.Text, nullable=False)
    prioridad = db.Column(db.String(20), default='media')
    estado = db.Column(db.String(20), default='pendiente')
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_limite = db.Column(db.DateTime)

    # Relaciones
    asignaciones = db.relationship('Asignacion', backref='solicitud', lazy=True)
    facturas = db.relationship('Factura', backref='solicitud', lazy=True)

    def __repr__(self):
        return f'<Solicitud {self.id}>'


class Asignacion(db.Model):
    __tablename__ = 'asignaciones'

    id = db.Column(db.Integer, primary_key=True)
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitudes.id'), nullable=False)
    tecnico_id = db.Column(db.Integer, db.ForeignKey('tecnicos.id'), nullable=False)
    fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_inicio = db.Column(db.DateTime)
    fecha_finalizacion = db.Column(db.DateTime)
    estado = db.Column(db.String(20), default='asignada')
    observaciones = db.Column(db.Text)
    tiempo_estimado = db.Column(db.Integer)
    tiempo_real = db.Column(db.Integer)

    # Relaciones
    reportes = db.relationship('Reporte', backref='asignacion', lazy=True, cascade='all, delete-orphan', passive_deletes=True)
    pedidos_piezas = db.relationship('PedidoPieza', backref='asignacion', lazy=True, cascade='all, delete-orphan', passive_deletes=True)

    def __repr__(self):
        return f'<Asignacion {self.id}>'


class Reporte(db.Model):
    __tablename__ = 'reportes'

    id = db.Column(db.Integer, primary_key=True)
    asignacion_id = db.Column(db.Integer, db.ForeignKey('asignaciones.id', ondelete='CASCADE'), nullable=False)
    tecnico_id = db.Column(db.Integer, db.ForeignKey('tecnicos.id'), nullable=False)
    fecha_reporte = db.Column(db.DateTime, default=datetime.utcnow)

    trabajo_realizado = db.Column(db.Text, nullable=False)
    problemas_encontrados = db.Column(db.Text)
    solucion_aplicada = db.Column(db.Text)
    recomendaciones = db.Column(db.Text)

    piezas_utilizadas = db.Column(db.Text)

    estado_inicial = db.Column(db.String(50))
    estado_final = db.Column(db.String(50))

    hora_inicio = db.Column(db.DateTime)
    hora_fin = db.Column(db.DateTime)
    tiempo_total = db.Column(db.Integer)

    cliente_satisfecho = db.Column(db.Boolean, default=True)
    observaciones_cliente = db.Column(db.Text)
    firma_cliente = db.Column(db.Text)
    nombre_firma = db.Column(db.String(100))

    completado = db.Column(db.Boolean, default=False)
    aprobado_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Reporte {self.id}>'


class Parte(db.Model):
    __tablename__ = 'partes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=5)
    proveedor = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    pedidos = db.relationship('PedidoPieza', backref='parte', lazy=True)

    @property
    def stock_bajo(self):
        """Indica si el stock está por debajo del mínimo"""
        return self.stock <= self.stock_minimo

    def __repr__(self):
        return f'<Parte {self.nombre}>'


class PedidoPieza(db.Model):
    __tablename__ = 'pedidos_piezas'

    id = db.Column(db.Integer, primary_key=True)
    tecnico_id = db.Column(db.Integer, db.ForeignKey('tecnicos.id'), nullable=False)
    parte_id = db.Column(db.Integer, db.ForeignKey('partes.id'), nullable=False)
    asignacion_id = db.Column(db.Integer, db.ForeignKey('asignaciones.id'), nullable=True)

    cantidad_solicitada = db.Column(db.Integer, nullable=False)
    cantidad_aprobada = db.Column(db.Integer, default=0)

    motivo = db.Column(db.Text, nullable=False)
    urgencia = db.Column(db.String(20), default='normal')

    estado = db.Column(db.String(20), default='pendiente')

    fecha_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_aprobacion = db.Column(db.DateTime)
    fecha_entrega = db.Column(db.DateTime)

    observaciones_admin = db.Column(db.Text)

    def __repr__(self):
        return f'<PedidoPieza {self.id}>'


class Factura(db.Model):
    __tablename__ = 'facturas'

    id = db.Column(db.Integer, primary_key=True)
    numero_factura = db.Column(db.String(20), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitudes.id'), nullable=True)
    fecha_emision = db.Column(db.DateTime, default=datetime.utcnow)
    subtotal = db.Column(db.Float, nullable=False)
    impuestos = db.Column(db.Float, default=0)
    total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')
    fecha_vencimiento = db.Column(db.DateTime)
    observaciones = db.Column(db.Text)

    def __repr__(self):
        return f'<Factura {self.numero_factura}>'
