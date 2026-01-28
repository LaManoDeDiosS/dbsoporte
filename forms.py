from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, MultipleFileField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email
from flask_wtf.file import MultipleFileField


class LoginForm(FlaskForm):
    email = StringField(
        'Correo',
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        'Contraseña',
        validators=[DataRequired()]
    )
    submit = SubmitField('Ingresar')


class ClienteForm(FlaskForm):
    nombre = StringField('Nombre del Cliente')
    submit = SubmitField('Guardar')


class OrdenForm(FlaskForm):
    cliente = SelectField('Cliente', coerce=int)
    persona = StringField('Persona que reporta')
    descripcion = TextAreaField('Descripción')

    solucion = TextAreaField('Resultado / Solución')

    estado = SelectField(
        'Estado de la orden',
        choices=[
            ('abierta', 'Abierta'),
            ('en_proceso', 'En proceso'),
            ('cerrada', 'Cerrada')
        ]
    )

    archivos = MultipleFileField('Adjuntar archivos')
    submit = SubmitField('Guardar')



