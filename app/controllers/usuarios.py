from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.models import Usuario
from app.forms import UsuarioForm
from app.decorators import admin_required

usuarios_bp = Blueprint('usuarios', __name__)


@usuarios_bp.route('/')
@admin_required
def list():
    page = request.args.get('page', 1, type=int)

    usuarios = Usuario.query.order_by(Usuario.fecha_creacion.desc()).paginate(
        page=page, per_page=10, error_out=False)

    return render_template('usuarios/list.html', usuarios=usuarios)


@usuarios_bp.route('/nuevo', methods=['GET', 'POST'])
@admin_required
def create():
    form = UsuarioForm()
    if form.validate_on_submit():
        usuario = Usuario(
            nombre=form.nombre.data,
            email=form.email.data,
            telefono=form.telefono.data,
            rol=form.rol.data
        )
        if form.password.data:
            usuario.set_password(form.password.data)

        db.session.add(usuario)
        db.session.commit()
        flash('Usuario creado exitosamente', 'success')
        return redirect(url_for('usuarios.list'))

    return render_template('usuarios/form.html', form=form, title='Nuevo Usuario')


@usuarios_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def edit(id):
    usuario = Usuario.query.get_or_404(id)
    form = UsuarioForm(obj=usuario)

    if form.validate_on_submit():
        usuario.nombre = form.nombre.data
        usuario.email = form.email.data
        usuario.telefono = form.telefono.data
        usuario.rol = form.rol.data

        if form.password.data:
            usuario.set_password(form.password.data)

        db.session.commit()
        flash('Usuario actualizado exitosamente', 'success')
        return redirect(url_for('usuarios.list'))

    return render_template('usuarios/form.html', form=form, title='Editar Usuario')


@usuarios_bp.route('/<int:id>/eliminar', methods=['POST'])
@admin_required
def delete(id):
    usuario = Usuario.query.get_or_404(id)

    # No permitir eliminar el usuario actual
    if usuario.id == current_user.id:
        flash('No puedes eliminar tu propio usuario', 'error')
        return redirect(url_for('usuarios.list'))

    # Verificar si es el único administrador
    if usuario.rol == 'administrador':
        admin_count = Usuario.query.filter_by(rol='administrador').count()
        if admin_count <= 1:
            flash('No se puede eliminar el último administrador del sistema', 'error')
            return redirect(url_for('usuarios.list'))

    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado permanentemente', 'success')
    return redirect(url_for('usuarios.list'))
