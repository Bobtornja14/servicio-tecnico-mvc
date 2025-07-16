from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.models import Asignacion, Solicitud, Tecnico
from app.forms import AsignacionForm
from app.decorators import admin_required, admin_or_tecnico_required

asignaciones_bp = Blueprint('asignaciones', __name__)


@asignaciones_bp.route('/')
@login_required
def list():
    page = request.args.get('page', 1, type=int)
    estado = request.args.get('estado', 'todas')

    query = Asignacion.query

    # Filtrar por estado si se especifica
    if estado == 'pendientes':
        query = query.filter_by(estado='asignada')
    elif estado == 'proceso':
        query = query.filter_by(estado='en_proceso')
    elif estado == 'completadas':
        query = query.filter_by(estado='completada')

    asignaciones = query.order_by(Asignacion.fecha_asignacion.desc()).paginate(
        page=page, per_page=10, error_out=False)

    return render_template('asignaciones/list.html', asignaciones=asignaciones, estado_actual=estado)


@asignaciones_bp.route('/nueva', methods=['GET', 'POST'])
@admin_required
def create():
    form = AsignacionForm()
    form.solicitud_id.choices = [(s.id, f"#{s.id} - {s.cliente.nombre}")
                                 for s in Solicitud.query.filter_by(estado='pendiente').all()]
    form.tecnico_id.choices = [(t.id, t.nombre) for t in Tecnico.query.all()]

    if form.validate_on_submit():
        asignacion = Asignacion(
            solicitud_id=form.solicitud_id.data,
            tecnico_id=form.tecnico_id.data,
            observaciones=form.observaciones.data,
            tiempo_estimado=form.tiempo_estimado.data,
            estado=form.estado.data
        )

        # Actualizar estado de la solicitud
        solicitud = Solicitud.query.get(form.solicitud_id.data)
        solicitud.estado = 'asignada'

        db.session.add(asignacion)
        db.session.commit()
        flash('Asignación creada exitosamente', 'success')
        return redirect(url_for('asignaciones.list'))

    return render_template('asignaciones/form.html', form=form, title='Nueva Asignación')


@asignaciones_bp.route('/<int:id>')
@login_required
def detail(id):
    asignacion = Asignacion.query.get_or_404(id)
    return render_template('asignaciones/detail.html', asignacion=asignacion)


@asignaciones_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@admin_or_tecnico_required
def edit(id):
    asignacion = Asignacion.query.get_or_404(id)

    # Los técnicos solo pueden editar sus propias asignaciones
    if current_user.is_tecnico() and not current_user.is_admin():
        from app.controllers.tecnico import get_tecnico_for_user
        tecnico = get_tecnico_for_user(current_user)
        if not tecnico or asignacion.tecnico_id != tecnico.id:
            flash('Solo puede editar sus propias asignaciones', 'error')
            return redirect(url_for('asignaciones.list'))

    form = AsignacionForm(obj=asignacion)
    form.solicitud_id.choices = [(s.id, f"#{s.id} - {s.cliente.nombre}")
                                 for s in Solicitud.query.all()]
    form.tecnico_id.choices = [(t.id, t.nombre) for t in Tecnico.query.all()]

    if form.validate_on_submit():
        asignacion.solicitud_id = form.solicitud_id.data
        asignacion.tecnico_id = form.tecnico_id.data
        asignacion.observaciones = form.observaciones.data
        asignacion.tiempo_estimado = form.tiempo_estimado.data
        asignacion.estado = form.estado.data

        db.session.commit()
        flash('Asignación actualizada exitosamente', 'success')
        return redirect(url_for('asignaciones.list'))

    return render_template('asignaciones/form.html', form=form, title='Editar Asignación')


@asignaciones_bp.route('/<int:id>/eliminar', methods=['POST'])
@admin_required
def delete(id):
    asignacion = Asignacion.query.get_or_404(id)

    # Restaurar estado de la solicitud
    solicitud = asignacion.solicitud
    solicitud.estado = 'pendiente'

    db.session.delete(asignacion)
    db.session.commit()
    flash('Asignación eliminada exitosamente', 'success')
    return redirect(url_for('asignaciones.list'))
