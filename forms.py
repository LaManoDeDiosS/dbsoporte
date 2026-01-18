from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, MultipleFileField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    email = StringField('Correo', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Ingresar')


class ClienteForm(FlaskForm):
    nombre = StringField('Nombre del Cliente', validators=[DataRequired()])
    submit = SubmitField('Guardar')


class OrdenForm(FlaskForm):
    cliente = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    persona = StringField('Persona que reporta', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[DataRequired()])
    archivos = MultipleFileField('Adjuntar archivos')
    submit = SubmitField('Guardar Orden')