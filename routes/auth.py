from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models import Usuario
from forms import LoginForm
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(
            email=form.email.data
        ).first()

        if usuario and check_password_hash(
            usuario.password,
            form.password.data
        ):
            login_user(usuario)
            return redirect(url_for('ordenes.ordenes'))

        flash('Credenciales inválidas')

    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))