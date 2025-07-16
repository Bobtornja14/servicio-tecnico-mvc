from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.models import Usuario
from app.forms import LoginForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data

        # Buscar usuario por email
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.check_password(password):
            login_user(usuario, remember=False)
            flash(f'Bienvenido {usuario.nombre}', 'success')

            # Redirigir a la página solicitada o al dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Email o contraseña incorrectos', 'error')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('auth.login'))
