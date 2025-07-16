from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.models import Tecnico, Usuario
from app.forms import TecnicoForm
from app.decorators import admin_required

tecnicos_bp = Blueprint('tecnicos', __name__)


@tecnicos_bp.route('/')
@login_required
def list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    especialidad = request.args.get('especialidad', '')

    query = Tecnico.query

    if search:
        query = query.filter(Tecnico.nombre.contains(search) |
                             Tecnico.email.contains(search))

    if especialidad:
        query = query.filter(Tecnico.especialidad.contains(especialidad))

    tecnicos = query.order_by(Tecnico.nombre).paginate(
        page=page, per_page=10, error_out=False)

    # Obtener especialidades para el filtro
    especialidades = db.session.query(Tecnico.especialidad).distinct().filter(
        Tecnico.especialidad.isnot(None)).all()
    especialidades = [esp[0] for esp in especialidades if esp[0]]

    return render_template('tecnicos/list.html',
                           tecnicos=tecnicos,
                           search=search,
                           especialidad_actual=especialidad,
                           especialidades=especialidades)


@tecnicos_bp.route('/nuevo', methods=['GET', 'POST'])
@admin_required
def create():
    form = TecnicoForm()

    # Cargar usuarios disponibles para asociar
    usuarios_tecnicos = Usuario.query.filter_by(rol='tecnico').all()
    form.usuario_id.choices = [(0, 'Crear nuevo usuario')] + [(u.id, f"{u.nombre} ({u.email})") for u in usuarios_tecnicos]

    if form.validate_on_submit():
        try:
            # Si se seleccionó un usuario existente
            if form.usuario_id.data != 0:
                usuario = Usuario.query.get(form.usuario_id.data)
                if not usuario:
                    flash('Usuario seleccionado no encontrado', 'error')
                    return render_template('tecnicos/form.html', form=form, title='Nuevo Técnico')
                
                # Si se proporcionó contraseña, actualizarla
                if form.password.data:
                    usuario.set_password(form.password.data)
                    db.session.add(usuario)
                
                # Actualizar datos del usuario si es necesario
                if usuario.nombre != form.nombre.data or usuario.telefono != form.telefono.data:
                    usuario.nombre = form.nombre.data
                    usuario.telefono = form.telefono.data
                    db.session.add(usuario)
                
                usuario_id = usuario.id
            else:
                # Crear nuevo usuario si no se seleccionó uno existente
                usuario = Usuario(
                    nombre=form.nombre.data,
                    email=form.email.data,
                    rol='tecnico',
                    telefono=form.telefono.data
                )
                usuario.set_password(form.password.data)
                db.session.add(usuario)
                db.session.flush()  # Para obtener el ID del usuario recién creado
                usuario_id = usuario.id

            # Crear el técnico (sin duplicar el email)
            tecnico = Tecnico(
                usuario_id=usuario_id,
                nombre=form.nombre.data,
                telefono=form.telefono.data,
                especialidad=form.especialidad.data,
                nivel_experiencia=form.nivel_experiencia.data
            )
            
            db.session.add(tecnico)
            db.session.commit()
            flash('Técnico creado exitosamente. El usuario puede iniciar sesión con su email y contraseña.', 'success')
            return redirect(url_for('tecnicos.list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el técnico: {str(e)}', 'error')

    return render_template('tecnicos/form.html', form=form, title='Nuevo Técnico')


@tecnicos_bp.route('/<int:id>')
@login_required
def detail(id):
    tecnico = Tecnico.query.get_or_404(id)
    return render_template('tecnicos/detail.html', tecnico=tecnico)


@tecnicos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def edit(id):
    tecnico = Tecnico.query.get_or_404(id)
    form = TecnicoForm(obj=tecnico)

    # Cargar usuarios disponibles para asociar
    usuarios_tecnicos = Usuario.query.filter_by(rol='tecnico').all()
    form.usuario_id.choices = [(0, 'Sin asociar')] + [(u.id, f"{u.nombre} ({u.email})") for u in usuarios_tecnicos]

    if form.validate_on_submit():
        tecnico.usuario_id = form.usuario_id.data if form.usuario_id.data != 0 else None
        tecnico.nombre = form.nombre.data
        tecnico.email = form.email.data
        tecnico.telefono = form.telefono.data
        tecnico.especialidad = form.especialidad.data
        tecnico.nivel_experiencia = form.nivel_experiencia.data

        db.session.commit()
        flash('Técnico actualizado exitosamente', 'success')
        return redirect(url_for('tecnicos.list'))

    return render_template('tecnicos/form.html', form=form, title='Editar Técnico')


@tecnicos_bp.route('/<int:id>/eliminar', methods=['POST'])
@admin_required
def delete(id):
    tecnico = Tecnico.query.get_or_404(id)

    # Verificar si tiene asignaciones
    if tecnico.asignaciones:
        flash('No se puede eliminar el técnico porque tiene asignaciones asociadas', 'error')
        return redirect(url_for('tecnicos.list'))

    db.session.delete(tecnico)
    db.session.commit()
    flash('Técnico eliminado exitosamente', 'success')
    return redirect(url_for('tecnicos.list'))
