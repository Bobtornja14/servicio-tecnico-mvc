from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.models import Parte
from app.forms import ParteForm, AjusteStockForm
from app.decorators import admin_required

partes_bp = Blueprint('partes', __name__)


@partes_bp.route('/')
@login_required
def list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    stock_bajo = request.args.get('stock_bajo', False, type=bool)

    query = Parte.query.filter(Parte.activo == True)

    if search:
        query = query.filter(db.or_(
            Parte.nombre.contains(search),
            Parte.codigo.contains(search)
        ))

    if stock_bajo:
        query = query.filter(Parte.stock <= Parte.stock_minimo)

    partes = query.order_by(Parte.nombre).paginate(
        page=page, per_page=10, error_out=False)

    # Contar partes con stock bajo
    stock_bajo_count = Parte.query.filter(
        Parte.stock <= Parte.stock_minimo,
        Parte.activo == True
    ).count()

    return render_template('partes/list.html',
                           partes=partes,
                           search=search,
                           stock_bajo_filtro=stock_bajo,
                           stock_bajo_count=stock_bajo_count)


@partes_bp.route('/nuevo', methods=['GET', 'POST'])
@admin_required
def create():
    form = ParteForm()
    if form.validate_on_submit():
        parte = Parte(
            nombre=form.nombre.data,
            codigo=form.codigo.data,
            descripcion=form.descripcion.data,
            precio=form.precio.data,
            stock=form.stock.data,
            stock_minimo=form.stock_minimo.data,
            proveedor=form.proveedor.data
        )
        db.session.add(parte)
        db.session.commit()
        flash('Parte creada exitosamente', 'success')
        return redirect(url_for('partes.list'))

    return render_template('partes/form.html', form=form, title='Nueva Parte')


@partes_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def edit(id):
    parte = Parte.query.get_or_404(id)
    form = ParteForm(obj=parte)

    if form.validate_on_submit():
        parte.nombre = form.nombre.data
        parte.codigo = form.codigo.data
        parte.descripcion = form.descripcion.data
        parte.precio = form.precio.data
        parte.stock = form.stock.data
        parte.stock_minimo = form.stock_minimo.data
        parte.proveedor = form.proveedor.data

        db.session.commit()
        flash('Parte actualizada exitosamente', 'success')
        return redirect(url_for('partes.list'))

    return render_template('partes/form.html', form=form, title='Editar Parte')


@partes_bp.route('/<int:id>/ajustar-stock', methods=['GET', 'POST'])
@admin_required
def ajustar_stock(id):
    parte = Parte.query.get_or_404(id)
    form = AjusteStockForm()
    form.nuevo_stock.data = parte.stock

    if form.validate_on_submit():
        stock_anterior = parte.stock
        parte.stock = form.nuevo_stock.data

        db.session.commit()

        flash(f'Stock ajustado de {stock_anterior} a {parte.stock} unidades. Motivo: {form.motivo.data}', 'success')
        return redirect(url_for('partes.list'))

    return render_template('partes/ajustar_stock.html', form=form, parte=parte)


@partes_bp.route('/<int:id>/eliminar', methods=['POST'])
@admin_required
def delete(id):
    parte = Parte.query.get_or_404(id)
    if parte.pedidos:
        # En lugar de eliminar, marcamos como inactiva
        parte.activo = False
        db.session.commit()
        flash('La parte ha sido marcada como inactiva debido a pedidos asociados.', 'warning')
    else:
        # Si no hay pedidos, la eliminamos físicamente
        db.session.delete(parte)
        db.session.commit()
        flash('Parte eliminada exitosamente', 'success')
    return redirect(url_for('partes.list'))
