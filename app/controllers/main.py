from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.models import Cliente, Solicitud, Tecnico, Factura, Asignacion

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    """Dashboard principal que se adapta según el rol del usuario"""

    if current_user.is_admin():
        return admin_dashboard()
    elif current_user.is_tecnico():
        return tecnico_dashboard()
    else:
        return user_dashboard()


def admin_dashboard():
    """Dashboard para administradores"""
    # Estadísticas generales
    total_clientes = Cliente.query.filter_by(activo=True).count()
    solicitudes_pendientes = Solicitud.query.filter_by(estado='pendiente').count()
    solicitudes_en_proceso = Solicitud.query.filter_by(estado='en_proceso').count()
    total_tecnicos = Tecnico.query.filter_by(activo=True).count()
    facturas_pendientes = Factura.query.filter_by(estado='pendiente').count()

    # Últimas solicitudes
    ultimas_solicitudes = Solicitud.query.order_by(Solicitud.fecha_solicitud.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_clientes=total_clientes,
                           solicitudes_pendientes=solicitudes_pendientes,
                           solicitudes_en_proceso=solicitudes_en_proceso,
                           total_tecnicos=total_tecnicos,
                           facturas_pendientes=facturas_pendientes,
                           ultimas_solicitudes=ultimas_solicitudes)


def tecnico_dashboard():
    """Dashboard para técnicos"""
    from app.controllers.tecnico import get_tecnico_for_user

    tecnico = get_tecnico_for_user(current_user)

    if not tecnico:
        return render_template('user/dashboard.html')

    # Estadísticas del técnico
    asignaciones_pendientes = Asignacion.query.filter_by(tecnico_id=tecnico.id, estado='asignada').count()
    asignaciones_proceso = Asignacion.query.filter_by(tecnico_id=tecnico.id, estado='en_proceso').count()
    asignaciones_completadas = Asignacion.query.filter_by(tecnico_id=tecnico.id, estado='completada').count()

    # Últimas asignaciones
    ultimas_asignaciones = Asignacion.query.filter_by(tecnico_id=tecnico.id) \
        .order_by(Asignacion.fecha_asignacion.desc()) \
        .limit(5).all()

    return render_template('tecnico/dashboard.html',
                           asignaciones_pendientes=asignaciones_pendientes,
                           asignaciones_proceso=asignaciones_proceso,
                           asignaciones_completadas=asignaciones_completadas,
                           pedidos_pendientes=0,  # Se puede agregar después
                           ultimas_asignaciones=ultimas_asignaciones,
                           tecnico=tecnico)


def user_dashboard():
    """Dashboard para usuarios normales"""
    # Estadísticas básicas
    total_clientes = Cliente.query.filter_by(activo=True).count()
    solicitudes_recientes = Solicitud.query.order_by(Solicitud.fecha_solicitud.desc()).limit(5).all()

    return render_template('user/dashboard.html',
                           total_clientes=total_clientes,
                           solicitudes_recientes=solicitudes_recientes)
