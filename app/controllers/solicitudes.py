from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.models import Solicitud, Cliente, Servicio
from app.forms import SolicitudForm
from app.decorators import admin_required, admin_or_tecnico_required

solicitudes_bp = Blueprint('solicitudes', __name__)


@solicitudes_bp.route('/')
@login_required
def list():
    page = request.args.get('page', 1, type=int)
    estado = request.args.get('estado', 'todas')

    query = Solicitud.query

    # Filtrar por estado si se especifica
    if estado == 'pendientes':
        query = query.filter_by(estado='pendiente')
    elif estado == 'asignadas':
        query = query.filter_by(estado='asignada')
    elif estado == 'proceso':
        query = query.filter_by(estado='en_proceso')
    elif estado == 'completadas':
        query = query.filter_by(estado='completada')

    solicitudes = query.order_by(Solicitud.fecha_solicitud.desc()).paginate(
        page=page, per_page=10, error_out=False)

    return render_template('solicitudes/list.html', solicitudes=solicitudes, estado_actual=estado)


@solicitudes_bp.route('/nueva', methods=['GET', 'POST'])
@admin_or_tecnico_required
def create():
    form = SolicitudForm()
    form.cliente_id.choices = [(c.id, c.nombre) for c in Cliente.query.all()]
    form.servicio_id.choices = [(s.id, s.nombre) for s in Servicio.query.all()]

    if form.validate_on_submit():
        solicitud = Solicitud(
            cliente_id=form.cliente_id.data,
            servicio_id=form.servicio_id.data,
            descripcion_problema=form.descripcion_problema.data,
            prioridad=form.prioridad.data,
            estado=form.estado.data
        )
        db.session.add(solicitud)
        db.session.commit()
        flash('Solicitud creada exitosamente', 'success')
        return redirect(url_for('solicitudes.list'))

    return render_template('solicitudes/form.html', form=form, title='Nueva Solicitud')


@solicitudes_bp.route('/<int:id>')
@login_required
def detail(id):
    solicitud = Solicitud.query.get_or_404(id)
    return render_template('solicitudes/detail.html', solicitud=solicitud)


@solicitudes_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@admin_or_tecnico_required
def edit(id):
    solicitud = Solicitud.query.get_or_404(id)
    form = SolicitudForm(obj=solicitud)
    form.cliente_id.choices = [(c.id, c.nombre) for c in Cliente.query.all()]
    form.servicio_id.choices = [(s.id, s.nombre) for s in Servicio.query.all()]

    if form.validate_on_submit():
        solicitud.cliente_id = form.cliente_id.data
        solicitud.servicio_id = form.servicio_id.data
        solicitud.descripcion_problema = form.descripcion_problema.data
        solicitud.prioridad = form.prioridad.data
        solicitud.estado = form.estado.data

        db.session.commit()
        flash('Solicitud actualizada exitosamente', 'success')
        return redirect(url_for('solicitudes.list'))

    return render_template('solicitudes/form.html', form=form, title='Editar Solicitud')


@solicitudes_bp.route('/<int:id>/eliminar', methods=['POST'])
@admin_required
def delete(id):
    solicitud = Solicitud.query.get_or_404(id)
    solicitud.estado = 'cancelada'
    db.session.commit()
    flash('Solicitud cancelada exitosamente', 'success')
    return redirect(url_for('solicitudes.list'))
