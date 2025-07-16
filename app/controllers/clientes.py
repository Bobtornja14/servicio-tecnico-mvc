from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.models import Cliente
from app.forms import ClienteForm
from app.decorators import admin_required

clientes_bp = Blueprint('clientes', __name__)


@clientes_bp.route('/')
@login_required
def list():
    page = request.args.get('page', 1, type=int)

    clientes = Cliente.query.order_by(Cliente.fecha_registro.desc()).paginate(
        page=page, per_page=10, error_out=False)

    return render_template('clientes/list.html', clientes=clientes)


@clientes_bp.route('/nuevo', methods=['GET', 'POST'])
@admin_required
def create():
    form = ClienteForm()
    if form.validate_on_submit():
        cliente = Cliente(
            nombre=form.nombre.data,
            email=form.email.data,
            telefono=form.telefono.data,
            direccion=form.direccion.data,
            tipo_cliente=form.tipo_cliente.data
        )
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente creado exitosamente', 'success')
        return redirect(url_for('clientes.list'))

    return render_template('clientes/form.html', form=form, title='Nuevo Cliente')


@clientes_bp.route('/<int:id>')
@login_required
def detail(id):
    cliente = Cliente.query.get_or_404(id)
    return render_template('clientes/detail.html', cliente=cliente)


@clientes_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def edit(id):
    cliente = Cliente.query.get_or_404(id)
    form = ClienteForm(obj=cliente)

    if form.validate_on_submit():
        cliente.nombre = form.nombre.data
        cliente.email = form.email.data
        cliente.telefono = form.telefono.data
        cliente.direccion = form.direccion.data
        cliente.tipo_cliente = form.tipo_cliente.data

        db.session.commit()
        flash('Cliente actualizado exitosamente', 'success')
        return redirect(url_for('clientes.list'))

    return render_template('clientes/form.html', form=form, title='Editar Cliente')


@clientes_bp.route('/<int:id>/eliminar', methods=['POST'])
@admin_required
def delete(id):
    cliente = Cliente.query.get_or_404(id)

    # Verificar si tiene solicitudes asociadas
    if cliente.solicitudes:
        flash('No se puede eliminar el cliente porque tiene solicitudes asociadas', 'error')
        return redirect(url_for('clientes.list'))

    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado permanentemente', 'success')
    return redirect(url_for('clientes.list'))
