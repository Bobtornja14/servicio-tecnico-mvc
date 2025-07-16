from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.models import PedidoPieza, Parte, Asignacion, Tecnico, Solicitud, Reporte, Notificacion
from app.forms.pedido_forms import AprobarPedidoForm, EntregarPedidoForm, CrearPedidoForm
from datetime import datetime
from sqlalchemy import and_

pedidos_bp = Blueprint('pedidos_piezas', __name__)

@pedidos_bp.route('/')
@login_required
def list():
    # Solo administradores pueden ver todos los pedidos
    if current_user.is_admin():
        pedidos = PedidoPieza.query.order_by(PedidoPieza.fecha_pedido.desc()).all()
    else:
        # Técnicos solo ven sus propios pedidos
        tecnico = Tecnico.query.filter_by(usuario_id=current_user.id).first_or_404()
        pedidos = PedidoPieza.query.filter_by(tecnico_id=tecnico.id).order_by(PedidoPieza.fecha_pedido.desc()).all()
    
    return render_template('pedidos_piezas/list.html', pedidos=pedidos)

@pedidos_bp.route('/pendientes')
@login_required
def pendientes():
    if not current_user.is_admin():
        flash('No tiene permisos para acceder a esta sección', 'error')
        return redirect(url_for('main.index'))
    
    # Mostrar solo pedidos pendientes de aprobación o entrega
    pedidos = PedidoPieza.query.filter(
        PedidoPieza.estado.in_(['pendiente', 'aprobado'])
    ).order_by(PedidoPieza.urgencia.desc(), PedidoPieza.fecha_pedido).all()
    
    return render_template('pedidos_piezas/pendientes.html', pedidos=pedidos)

@pedidos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def crear():
    # Verificar que el usuario sea un técnico
    tecnico = Tecnico.query.filter_by(usuario_id=current_user.id).first()
    if not tecnico:
        flash('Solo los técnicos pueden realizar pedidos de piezas', 'error')
        return redirect(url_for('main.index'))
    
    form = CrearPedidoForm()
    
    # Obtener asignaciones activas del técnico para el select
    asignaciones = Asignacion.query.filter_by(
        tecnico_id=tecnico.id,
        estado='asignada'
    ).all()
    
    form.asignacion_id.choices = [(0, 'Sin asignar')] + [(a.id, f"{a.solicitud.id} - {a.solicitud.cliente.nombre}") for a in asignaciones]
    
    if form.validate_on_submit():
        # Verificar que la parte existe y tiene stock suficiente
        parte = Parte.query.get(form.parte_id.data)
        if not parte:
            flash('La parte seleccionada no existe', 'error')
            return redirect(url_for('pedidos_piezas.crear'))
            
        # Si el pedido es para una asignación específica, verificar que existe
        asignacion_id = form.asignacion_id.data if form.asignacion_id.data != 0 else None
        if asignacion_id:
            asignacion = Asignacion.query.get_or_404(asignacion_id)
        else:
            asignacion = None
        
        # Crear el pedido
        pedido = PedidoPieza(
            tecnico_id=tecnico.id,
            parte_id=parte.id,
            asignacion_id=asignacion_id,
            cantidad_solicitada=form.cantidad_solicitada.data,
            motivo=form.motivo.data,
            urgencia=form.urgencia.data,
            estado='pendiente',
            fecha_pedido=datetime.utcnow()
        )
        
        db.session.add(pedido)
        db.session.commit()
        
        flash('Pedido de pieza registrado correctamente', 'success')
        return redirect(url_for('pedidos_piezas.list'))
    
    return render_template('pedidos_piezas/crear.html', form=form)

@pedidos_bp.route('/<int:id>/aprobar', methods=['GET', 'POST'])
@login_required
def aprobar(id):
    if not current_user.is_admin():
        flash('No tiene permisos para realizar esta acción', 'error')
        return redirect(url_for('main.index'))
    
    pedido = PedidoPieza.query.get_or_404(id)
    form = AprobarPedidoForm()
    
    if form.validate_on_submit():
        # Actualizar el pedido
        pedido.cantidad_aprobada = form.cantidad_aprobada.data
        pedido.estado = form.estado.data
        pedido.observaciones_admin = form.observaciones.data
        pedido.fecha_aprobacion = datetime.utcnow()
        
        # Si se aprueba, verificar que hay stock suficiente
        if form.estado.data == 'aprobado' and pedido.parte.stock < form.cantidad_aprobada.data:
            flash('No hay suficiente stock para aprobar esta cantidad', 'error')
            return redirect(url_for('pedidos_piezas.aprobar', id=id))
        
        db.session.commit()
        
        # Crear notificación para el técnico
        notificacion = Notificacion(
            usuario_id=pedido.tecnico.usuario_id,
            titulo=f'Pedido de pieza {pedido.parte.nombre}',
            mensaje=f'Su pedido ha sido {form.estado.data}. Cantidad aprobada: {form.cantidad_aprobada.data}',
            tipo=form.estado.data,
            url=url_for('pedidos_piezas.ver', id=pedido.id)
        )
        db.session.add(notificacion)
        db.session.commit()
        
        flash(f'Pedido {form.estado.data} correctamente', 'success')
        return redirect(url_for('pedidos_piezas.pendientes'))
    
    # Configurar valores por defecto
    if request.method == 'GET':
        form.cantidad_aprobada.data = pedido.cantidad_solicitada
        form.estado.data = 'aprobado' if pedido.estado == 'pendiente' else pedido.estado
    
    return render_template('pedidos_piezas/aprobar.html', form=form, pedido=pedido)

@pedidos_bp.route('/<int:id>/entregar', methods=['GET', 'POST'])
@login_required
def entregar(id):
    if not current_user.is_admin():
        flash('No tiene permisos para realizar esta acción', 'error')
        return redirect(url_for('main.index'))
    
    pedido = PedidoPieza.query.get_or_404(id)
    
    # Solo se pueden entregar pedidos aprobados
    if pedido.estado != 'aprobado':
        flash('Solo se pueden entregar pedidos que estén aprobados', 'error')
        return redirect(url_for('pedidos_piezas.pendientes'))
    
    form = EntregarPedidoForm()
    
    if form.validate_on_submit():
        try:
            # Actualizar el stock
            pedido.parte.stock -= form.cantidad_entregada.data
            
            # Actualizar el pedido
            pedido.estado = 'entregado'
            pedido.fecha_entrega = datetime.strptime(form.fecha_entrega.data, '%Y-%m-%dT%H:%M')
            pedido.observaciones_entrega = form.observaciones.data
            
            db.session.commit()
            
            # Crear notificación para el técnico
            notificacion = Notificacion(
                usuario_id=pedido.tecnico.usuario_id,
                titulo=f'Entrega de pieza {pedido.parte.nombre}',
                mensaje=f'Su pedido ha sido entregado. Cantidad: {form.cantidad_entregada.data}',
                tipo='entregado',
                url=url_for('pedidos_piezas.ver', id=pedido.id)
            )
            db.session.add(notificacion)
            db.session.commit()
            
            flash('Pedido entregado correctamente', 'success')
            return redirect(url_for('pedidos_piezas.pendientes'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al procesar la entrega: {str(e)}', 'error')
    
    # Configurar valores por defecto
    if request.method == 'GET':
        form.cantidad_entregada.data = pedido.cantidad_aprobada or pedido.cantidad_solicitada
        form.fecha_entrega.data = datetime.now().strftime('%Y-%m-%dT%H:%M')
    
    return render_template('pedidos_piezas/entregar.html', form=form, pedido=pedido)

@pedidos_bp.route('/<int:id>')
@login_required
def ver(id):
    pedido = PedidoPieza.query.get_or_404(id)
    
    # Verificar permisos (admin o el técnico dueño del pedido)
    if not current_user.is_admin() and pedido.tecnico.usuario_id != current_user.id:
        flash('No tiene permisos para ver este pedido', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('pedidos_piezas/ver.html', pedido=pedido)

# API para buscar partes por nombre o código
@pedidos_bp.route('/api/partes/buscar')
@login_required
def buscar_partes():
    termino = request.args.get('q', '').strip()
    
    if not termino or len(termino) < 2:
        return jsonify([])
    
    # Buscar partes que coincidan con el término de búsqueda
    partes = Parte.query.filter(
        and_(
            Parte.activo == True,
            db.or_(
                Parte.nombre.ilike(f'%{termino}%'),
                Parte.codigo.ilike(f'%{termino}%')
            )
        )
    ).limit(10).all()
    
    # Formatear resultados para Select2
    resultados = [{
        'id': p.id,
        'text': f"{p.nombre} ({p.codigo}) - Stock: {p.stock}",
        'stock': p.stock,
        'precio': p.precio
    } for p in partes]
    
    return jsonify(resultados)
