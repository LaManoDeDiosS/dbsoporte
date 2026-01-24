from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user
from models import Usuario
from forms import LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()

        if usuario and usuario.password == form.password.data:
            login_user(usuario)
            return redirect(url_for('ordenes.ordenes'))

        flash('Correo o contraseña incorrectos')

    return render_template('login.html', form=form)
