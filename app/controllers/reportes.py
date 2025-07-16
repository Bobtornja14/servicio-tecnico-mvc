from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import db
from app.models.models import Solicitud, Asignacion
import base64
from datetime import datetime

reportes_bp = Blueprint('reportes', __name__)


@reportes_bp.route('/')
@login_required
def list():
    page = request.args.get('page', 1, type=int)
    estado = request.args.get('estado', 'todos')

    query = Asignacion.query.join(Solicitud)

    if estado == 'completadas':
        query = query.filter(Asignacion.estado == 'completada')
    elif estado == 'en_proceso':
        query = query.filter(Asignacion.estado == 'en_proceso')
    elif estado == 'pendientes':
        query = query.filter(Asignacion.estado == 'asignada')

    asignaciones = query.order_by(Asignacion.fecha_asignacion.desc()).paginate(
        page=page, per_page=10, error_out=False)

    return render_template('reportes/list.html', asignaciones=asignaciones, estado_actual=estado)


@reportes_bp.route('/<int:id>/reporte')
@login_required
def reporte(id):
    asignacion = Asignacion.query.get_or_404(id)
    return render_template('reportes/reporte.html', asignacion=asignacion)


@reportes_bp.route('/<int:id>/firmar', methods=['POST'])
@login_required
def guardar_firma(id):
    asignacion = Asignacion.query.get_or_404(id)

    data = request.get_json()
    firma_data = data.get('firma')
    nombre_cliente = data.get('nombre_cliente', '')

    if firma_data:
        # Remover el prefijo data:image/png;base64,
        if firma_data.startswith('data:image/png;base64,'):
            firma_data = firma_data.replace('data:image/png;base64,', '')

        # Guardar la firma en el campo observaciones (en un proyecto real usarías un campo específico)
        firma_info = f"\n--- FIRMA DIGITAL ---\nCliente: {nombre_cliente}\nFecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\nFirma: {firma_data[:50]}..."

        if asignacion.observaciones:
            asignacion.observaciones += firma_info
        else:
            asignacion.observaciones = firma_info

        # Marcar como completada si no lo está
        if asignacion.estado != 'completada':
            asignacion.estado = 'completada'
            asignacion.fecha_finalizacion = datetime.utcnow()

        db.session.commit()

        return jsonify({'success': True, 'message': 'Firma guardada exitosamente'})

    return jsonify({'success': False, 'message': 'Error al guardar la firma'})
