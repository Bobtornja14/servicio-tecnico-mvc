from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.models import PedidoPieza, Reporte, Parte, Cliente, Solicitud, Factura, Tecnico
from app.decorators import admin_required
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Obtener estadísticas para el dashboard
    total_clientes = Cliente.query.filter_by(activo=True).count()
    total_tecnicos = Tecnico.query.filter_by(activo=True).count()
    
    # Obtener recuento de solicitudes por estado
    solicitudes_pendientes = Solicitud.query.filter_by(estado='pendiente').count()
    solicitudes_en_proceso = Solicitud.query.filter_by(estado='en_proceso').count()
    
    # Obtener facturas pendientes de pago
    facturas_pendientes = Factura.query.filter_by(estado='pendiente').count()
    
    # Obtener últimas solicitudes
    ultimas_solicitudes = Solicitud.query.order_by(
        Solicitud.fecha_creacion.desc()
    ).limit(5).all()
    
    # Obtener pedidos de piezas pendientes
    pedidos_pendientes = PedidoPieza.query.filter_by(estado='pendiente').count()
    
    return render_template(
        'admin/dashboard.html',
        total_clientes=total_clientes,
        total_tecnicos=total_tecnicos,
        solicitudes_pendientes=solicitudes_pendientes,
        solicitudes_en_proceso=solicitudes_en_proceso,
        facturas_pendientes=facturas_pendientes,
        ultimas_solicitudes=ultimas_solicitudes,
        pedidos_pendientes=pedidos_pendientes
    )


@admin_bp.route('/pedidos-piezas')
@admin_required
def gestionar_pedidos():
    page = request.args.get('page', 1, type=int)
    estado = request.args.get('estado', 'todos')

    query = PedidoPieza.query

    if estado == 'pendientes':
        query = query.filter_by(estado='pendiente')
    elif estado == 'aprobados':
        query = query.filter_by(estado='aprobado')
    elif estado == 'entregados':
        query = query.filter_by(estado='entregado')
    elif estado == 'rechazados':
        query = query.filter_by(estado='rechazado')

    pedidos = query.order_by(PedidoPieza.fecha_pedido.desc()).paginate(
        page=page, per_page=10, error_out=False)

    return render_template('admin/pedidos_piezas.html', pedidos=pedidos, estado_actual=estado)


@admin_bp.route('/pedido/<int:id>/aprobar', methods=['POST'])
@admin_required
def aprobar_pedido(id):
    pedido = PedidoPieza.query.get_or_404(id)
    cantidad_aprobada = request.form.get('cantidad_aprobada', type=int)
    observaciones = request.form.get('observaciones', '')

    if cantidad_aprobada and cantidad_aprobada > 0:
        # Verificar stock disponible
        if cantidad_aprobada <= pedido.parte.stock:
            pedido.cantidad_aprobada = cantidad_aprobada
            pedido.estado = 'aprobado'
            pedido.fecha_aprobacion = datetime.utcnow()
            pedido.observaciones_admin = observaciones

            # Reducir stock
            pedido.parte.stock -= cantidad_aprobada

            db.session.commit()
            flash(f'Pedido aprobado por {cantidad_aprobada} unidades', 'success')
        else:
            flash(f'Stock insuficiente. Disponible: {pedido.parte.stock}', 'error')
    else:
        flash('Cantidad inválida', 'error')

    return redirect(url_for('admin.gestionar_pedidos'))


@admin_bp.route('/pedido/<int:id>/rechazar', methods=['POST'])
@admin_required
def rechazar_pedido(id):
    pedido = PedidoPieza.query.get_or_404(id)
    observaciones = request.form.get('observaciones', '')

    pedido.estado = 'rechazado'
    pedido.observaciones_admin = observaciones

    db.session.commit()
    flash('Pedido rechazado', 'success')
    return redirect(url_for('admin.gestionar_pedidos'))


@admin_bp.route('/pedido/<int:id>/entregar', methods=['POST'])
@admin_required
def entregar_pedido(id):
    pedido = PedidoPieza.query.get_or_404(id)

    if pedido.estado == 'aprobado':
        pedido.estado = 'entregado'
        pedido.fecha_entrega = datetime.utcnow()

        db.session.commit()
        flash('Pedido marcado como entregado', 'success')

    return redirect(url_for('admin.gestionar_pedidos'))


@admin_bp.route('/reportes')
@admin_required
def ver_reportes():
    page = request.args.get('page', 1, type=int)
    estado = request.args.get('estado', 'todos')

    query = Reporte.query

    if estado == 'pendientes':
        query = query.filter_by(completado=False)
    elif estado == 'completados':
        query = query.filter_by(completado=True, aprobado_admin=False)
    elif estado == 'aprobados':
        query = query.filter_by(aprobado_admin=True)

    reportes = query.order_by(Reporte.fecha_reporte.desc()).paginate(
        page=page, per_page=10, error_out=False)

    return render_template('admin/reportes.html', reportes=reportes, estado_actual=estado)


@admin_bp.route('/reporte/<int:id>/aprobar', methods=['POST'])
@admin_required
def aprobar_reporte(id):
    reporte = Reporte.query.get_or_404(id)
    reporte.aprobado_admin = True

    db.session.commit()
    flash('Reporte aprobado exitosamente', 'success')
    return redirect(url_for('admin.ver_reportes'))


@admin_bp.route('/inventario/ajustar-stock/<int:id>', methods=['POST'])
@admin_required
def ajustar_stock(id):
    parte = Parte.query.get_or_404(id)
    nuevo_stock = request.form.get('nuevo_stock', type=int)
    motivo = request.form.get('motivo', '')

    if nuevo_stock is not None and nuevo_stock >= 0:
        stock_anterior = parte.stock
        parte.stock = nuevo_stock

        db.session.commit()
        flash(f'Stock ajustado de {stock_anterior} a {nuevo_stock}. Motivo: {motivo}', 'success')
    else:
        flash('Stock inválido', 'error')

    return redirect(url_for('partes.list'))
