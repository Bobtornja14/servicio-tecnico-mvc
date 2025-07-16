from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)

    return decorated_function


def tecnico_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_tecnico() or current_user.is_admin()):
            flash('Acceso denegado. Se requieren permisos de técnico.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)

    return decorated_function


def admin_or_tecnico_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_admin() or current_user.is_tecnico()):
            flash('Acceso denegado.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)

    return decorated_function


def can_edit_resource(resource_type):
    """Verifica si el usuario puede editar un tipo de recurso"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))

            # Administrador puede editar todo
            if current_user.is_admin():
                return f(*args, **kwargs)

            # Técnico puede editar solo ciertos recursos
            if current_user.is_tecnico():
                allowed_resources = ['reportes', 'asignaciones_propias', 'pedidos_piezas']
                if resource_type in allowed_resources:
                    return f(*args, **kwargs)

            flash('No tiene permisos para realizar esta acción.', 'error')
            return redirect(url_for('main.index'))

        return decorated_function

    return decorator
