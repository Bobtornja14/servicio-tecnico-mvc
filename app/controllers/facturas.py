from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.models import Factura, Cliente, Solicitud
from app.forms import FacturaForm
from app.decorators import admin_required

facturas_bp = Blueprint('facturas', __name__)


@facturas_bp.route('/')
@login_required
def list():
    page = request.args.get('page', 1, type=int)
    estado = request.args.get('estado', '')

    query = Factura.query

    if estado:
        query = query.filter_by(estado=estado)

    facturas = query.order_by(Factura.fecha_emision.desc()).paginate(
        page=page, per_page=10, error_out=False)

    return render_template('facturas/list.html', facturas=facturas, estado_actual=estado)


@facturas_bp.route('/nueva', methods=['GET', 'POST'])
@admin_required
def create():
    form = FacturaForm()

    # Cargar clientes y solicitudes
    clientes = Cliente.query.all()
    solicitudes = Solicitud.query.filter_by(estado='completada').all()

    form.cliente_id.choices = [(c.id, c.nombre) for c in clientes]
    form.solicitud_id.choices = [(0, 'Sin solicitud')] + [(s.id, f"Solicitud #{s.id} - {s.cliente.nombre}") for s in
                                                          solicitudes]

    if form.validate_on_submit():
        factura = Factura(
            numero_factura=form.numero_factura.data,
            cliente_id=form.cliente_id.data,
            solicitud_id=form.solicitud_id.data if form.solicitud_id.data != 0 else None,
            subtotal=form.subtotal.data,
            impuestos=form.impuestos.data,
            total=form.total.data,
            estado=form.estado.data,
            observaciones=form.observaciones.data
        )
        db.session.add(factura)
        db.session.commit()
        flash('Factura creada exitosamente', 'success')
        return redirect(url_for('facturas.list'))

    return render_template('facturas/form.html', form=form, title='Nueva Factura')


@facturas_bp.route('/<int:id>')
@login_required
def detail(id):
    factura = Factura.query.get_or_404(id)
    return render_template('facturas/detail.html', factura=factura)


@facturas_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def edit(id):
    factura = Factura.query.get_or_404(id)
    form = FacturaForm(obj=factura)

    # Cargar clientes y solicitudes
    clientes = Cliente.query.all()
    solicitudes = Solicitud.query.filter_by(estado='completada').all()

    form.cliente_id.choices = [(c.id, c.nombre) for c in clientes]
    form.solicitud_id.choices = [(0, 'Sin solicitud')] + [(s.id, f"Solicitud #{s.id} - {s.cliente.nombre}") for s in
                                                          solicitudes]

    if form.validate_on_submit():
        factura.numero_factura = form.numero_factura.data
        factura.cliente_id = form.cliente_id.data
        factura.solicitud_id = form.solicitud_id.data if form.solicitud_id.data != 0 else None
        factura.subtotal = form.subtotal.data
        factura.impuestos = form.impuestos.data
        factura.total = form.total.data
        factura.estado = form.estado.data
        factura.observaciones = form.observaciones.data

        db.session.commit()
        flash('Factura actualizada exitosamente', 'success')
        return redirect(url_for('facturas.list'))

    return render_template('facturas/form.html', form=form, title='Editar Factura')


@facturas_bp.route('/<int:id>/eliminar', methods=['POST'])
@admin_required
def delete(id):
    factura = Factura.query.get_or_404(id)

    db.session.delete(factura)
    db.session.commit()
    flash('Factura eliminada exitosamente', 'success')
    return redirect(url_for('facturas.list'))
